"""
Comment services for comment management, moderation, and threading.
"""
from datetime import datetime, timedelta
from sqlalchemy import func, desc, asc
from flask import current_app
from app import db
from app.models import Comment, CommentEditHistory, Fact, User, UserProfile
from app.components.security.services import ValidationService, AuditService, AuthorizationService


class CommentManagementService:
    """Service for comment creation, editing, and deletion."""
    
    @staticmethod
    def create_comment(user_id, fact_id, content, parent_comment_id=None):
        """
        Create a new comment on a fact.
        
        Args:
            user_id (str): User ID creating the comment
            fact_id (str): Fact ID being commented on
            content (str): Comment content
            parent_comment_id (str): Parent comment ID for replies
            
        Returns:
            tuple: (success: bool, message: str, comment: Comment or None)
        """
        try:
            # Validate content
            content_valid, content_msg = ValidationService.validate_comment_content(content)
            if not content_valid:
                return False, content_msg, None
            
            # Sanitize content
            sanitized_content = ValidationService.sanitize_html(content.strip())
            
            # Check if fact exists and is not deleted
            fact = db.session.get(Fact, fact_id)
            if not fact or fact.is_deleted:
                return False, "Fact not found", None
            
            # Check if parent comment exists (for replies)
            if parent_comment_id:
                parent_comment = db.session.get(Comment, parent_comment_id)
                if not parent_comment or parent_comment.is_deleted or parent_comment.fact_id != fact_id:
                    return False, "Parent comment not found", None
                
                # Limit reply depth
                max_depth = current_app.config.get('MAX_COMMENT_DEPTH', 3)
                if parent_comment.nesting_level >= max_depth:
                    return False, f"Maximum reply depth ({max_depth}) exceeded", None
                
                nesting_level = parent_comment.nesting_level + 1
            else:
                nesting_level = 0
            
            # Check rate limiting
            if CommentManagementService._is_rate_limited(user_id):
                return False, "You are commenting too frequently. Please wait before commenting again.", None
            
            # Create comment
            comment = Comment(
                user_id=user_id,
                fact_id=fact_id,
                content=sanitized_content,
                parent_comment_id=parent_comment_id,
                nesting_level=nesting_level
            )
            comment.save()
            
            # Log creation
            AuditService.log_action(
                user_id=user_id,
                action_type='comment_create',
                resource_type='comment',
                resource_id=comment.id,
                new_values=sanitized_content,
                success=True
            )
            
            return True, "Comment posted successfully", comment
            
        except Exception as e:
            current_app.logger.error(f"Comment creation error: {str(e)}")
            return False, "Failed to post comment", None
    
    @staticmethod
    def update_comment(comment_id, user_id, content, edit_reason=None):
        """
        Update an existing comment.
        
        Args:
            comment_id (str): Comment ID
            user_id (str): User ID making the edit
            content (str): New content
            edit_reason (str): Reason for edit
            
        Returns:
            tuple: (success: bool, message: str, comment: Comment or None)
        """
        try:
            # Get comment
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.is_deleted:
                return False, "Comment not found", None
            
            # Check ownership or moderation rights
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found", None
            
            can_edit = (comment.user_id == user_id or 
                       user.is_admin or 
                       user.is_moderator)
            
            if not can_edit:
                return False, "You can only edit your own comments", None
            
            # Validate content
            content_valid, content_msg = ValidationService.validate_comment_content(content)
            if not content_valid:
                return False, content_msg, None
            
            # Sanitize content
            sanitized_content = ValidationService.sanitize_html(content.strip())
            
            # Check edit time limit (users can only edit within 15 minutes, mods anytime)
            if not (user.is_admin or user.is_moderator):
                edit_time_limit = current_app.config.get('COMMENT_EDIT_TIME_LIMIT_MINUTES', 15)
                time_since_creation = datetime.utcnow() - comment.created_at
                if time_since_creation > timedelta(minutes=edit_time_limit):
                    return False, f"Comments can only be edited within {edit_time_limit} minutes of posting", None
            
            # Save edit history
            edit_history = CommentEditHistory(
                comment_id=comment.id,
                previous_content=comment.content,
                edit_reason=edit_reason
            )
            edit_history.save()
            
            # Update comment
            old_content = comment.content
            comment.content = sanitized_content
            comment.edit_count += 1
            comment.save()
            
            # Log update
            AuditService.log_action(
                user_id=user_id,
                action_type='comment_update',
                resource_type='comment',
                resource_id=comment.id,
                old_values=old_content,
                new_values=sanitized_content,
                success=True
            )
            
            return True, "Comment updated successfully", comment
            
        except Exception as e:
            current_app.logger.error(f"Comment update error: {str(e)}")
            return False, "Failed to update comment", None
    
    @staticmethod
    def delete_comment(comment_id, user_id):
        """
        Delete a comment (soft delete).
        
        Args:
            comment_id (str): Comment ID
            user_id (str): User ID requesting deletion
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Get comment
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.is_deleted:
                return False, "Comment not found"
            
            # Check ownership or moderation rights
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            can_delete = (comment.user_id == user_id or 
                         user.is_admin or 
                         user.is_moderator)
            
            if not can_delete:
                return False, "You can only delete your own comments"
            
            # Soft delete comment
            comment.delete()
            
            # Also soft delete all replies
            CommentManagementService._delete_comment_replies(comment_id, user_id)
            
            # Log deletion
            AuditService.log_action(
                user_id=user_id,
                action_type='comment_delete',
                resource_type='comment',
                resource_id=comment.id,
                old_values=comment.content,
                success=True
            )
            
            return True, "Comment deleted successfully"
            
        except Exception as e:
            current_app.logger.error(f"Comment deletion error: {str(e)}")
            return False, "Failed to delete comment"
    
    @staticmethod
    def _delete_comment_replies(parent_comment_id, user_id):
        """
        Recursively delete all replies to a comment.
        
        Args:
            parent_comment_id (str): Parent comment ID
            user_id (str): User ID performing the deletion
        """
        try:
            replies = Comment.query.filter_by(
                parent_comment_id=parent_comment_id,
                is_deleted=False
            ).all()
            
            for reply in replies:
                # Recursively delete sub-replies
                CommentManagementService._delete_comment_replies(reply.id, user_id)
                
                # Delete this reply
                reply.delete()
                
                # Log deletion
                AuditService.log_action(
                    user_id=user_id,
                    action_type='comment_delete_cascade',
                    resource_type='comment',
                    resource_id=reply.id,
                    old_values=reply.content,
                    success=True
                )
                
        except Exception as e:
            current_app.logger.error(f"Error deleting comment replies: {str(e)}")
    
    @staticmethod
    def _is_rate_limited(user_id):
        """
        Check if user is rate limited for commenting.
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: True if rate limited
        """
        try:
            # Check comments in last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_comments = Comment.query.filter(
                Comment.user_id == user_id,
                Comment.created_at >= one_hour_ago,
                Comment.is_deleted == False
            ).count()
            
            max_comments_per_hour = current_app.config.get('MAX_COMMENTS_PER_HOUR', 20)
            return recent_comments >= max_comments_per_hour
            
        except Exception as e:
            current_app.logger.error(f"Rate limit check error: {str(e)}")
            return False


class CommentRetrievalService:
    """Service for comment retrieval and threading."""
    
    @staticmethod
    def get_fact_comments(fact_id, sort_by='oldest', include_deleted=False):
        """
        Get all comments for a fact with proper threading.
        
        Args:
            fact_id (str): Fact ID
            sort_by (str): Sort method ('oldest', 'newest', 'helpful')
            include_deleted (bool): Whether to include deleted comments
            
        Returns:
            list: Threaded comments
        """
        try:
            # Base query
            query = Comment.query.filter_by(fact_id=fact_id)
            
            if not include_deleted:
                query = query.filter_by(is_deleted=False)
            
            # Apply sorting
            if sort_by == 'oldest':
                query = query.order_by(asc(Comment.created_at))
            elif sort_by == 'newest':
                query = query.order_by(desc(Comment.created_at))
            elif sort_by == 'helpful':
                # TODO: Sort by helpfulness score when voting is integrated
                query = query.order_by(desc(Comment.created_at))
            
            comments = query.all()
            
            # Build threaded structure
            threaded_comments = CommentRetrievalService._build_comment_tree(comments)
            
            return threaded_comments
            
        except Exception as e:
            current_app.logger.error(f"Error getting fact comments: {str(e)}")
            return []
    
    @staticmethod
    def get_comment_with_author(comment_id):
        """
        Get comment with author information.
        
        Args:
            comment_id (str): Comment ID
            
        Returns:
            dict or None: Comment with author info
        """
        try:
            comment_data = db.session.query(Comment, User, UserProfile).join(
                User, Comment.user_id == User.id
            ).join(
                UserProfile, User.id == UserProfile.user_id
            ).filter(
                Comment.id == comment_id,
                Comment.is_deleted == False,
                User.is_active == True,
                User.is_deleted == False
            ).first()
            
            if not comment_data:
                return None
            
            return {
                'comment': comment_data[0],
                'author': comment_data[1],
                'author_profile': comment_data[2]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting comment with author: {str(e)}")
            return None
    
    @staticmethod
    def get_user_comments(user_id, limit=50):
        """
        Get comments by a specific user.
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of comments
            
        Returns:
            list: User's comments
        """
        try:
            return Comment.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).order_by(
                desc(Comment.created_at)
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f"Error getting user comments: {str(e)}")
            return []
    
    @staticmethod
    def get_comment_edit_history(comment_id, user_id):
        """
        Get edit history for a comment.
        
        Args:
            comment_id (str): Comment ID
            user_id (str): User ID requesting history
            
        Returns:
            list: Edit history entries or empty list
        """
        try:
            # Get comment and check ownership/moderation rights
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.is_deleted:
                return []
            
            user = db.session.get(User, user_id)
            if not user:
                return []
            
            can_view_history = (comment.user_id == user_id or 
                               user.is_admin or 
                               user.is_moderator)
            
            if not can_view_history:
                return []
            
            return CommentEditHistory.query.filter_by(
                comment_id=comment_id,
                is_deleted=False
            ).order_by(desc(CommentEditHistory.created_at)).all()
            
        except Exception as e:
            current_app.logger.error(f"Error getting comment history: {str(e)}")
            return []
    
    @staticmethod
    def _build_comment_tree(comments):
        """
        Build a threaded comment tree from flat comment list.
        
        Args:
            comments (list): Flat list of comments
            
        Returns:
            list: Threaded comment structure
        """
        # Create lookup dictionaries
        comment_dict = {comment.id: comment for comment in comments}
        children_dict = {}
        
        # Group comments by parent
        for comment in comments:
            parent_id = comment.parent_comment_id
            if parent_id not in children_dict:
                children_dict[parent_id] = []
            children_dict[parent_id].append(comment)
        
        # Add children to each comment
        for comment in comments:
            comment.replies = children_dict.get(comment.id, [])
            # Sort replies by creation time
            comment.replies.sort(key=lambda x: x.created_at)
        
        # Return top-level comments (no parent)
        top_level_comments = children_dict.get(None, [])
        top_level_comments.sort(key=lambda x: x.created_at)
        
        return top_level_comments


class CommentModerationService:
    """Service for comment moderation and content filtering."""
    
    @staticmethod
    def flag_comment(comment_id, user_id, flag_reason):
        """
        Flag a comment for moderation.
        
        Args:
            comment_id (str): Comment ID
            user_id (str): User ID flagging the comment
            flag_reason (str): Reason for flagging
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Check if comment exists
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.is_deleted:
                return False, "Comment not found"
            
            # Check if user already flagged this comment
            existing_flag = AuditService.get_user_audit_trail(user_id, 10)
            recent_flags = [
                log for log in existing_flag 
                if log.action == 'comment_flag' and log.resource_id == comment_id
            ]
            
            if recent_flags:
                return False, "You have already flagged this comment"
            
            # Log the flag
            AuditService.log_action(
                user_id=user_id,
                action_type='comment_flag',
                resource_type='comment',
                resource_id=comment_id,
                new_values=flag_reason,
                success=True
            )
            
            # Check if comment should be auto-hidden based on flag count
            CommentModerationService._check_auto_moderation(comment_id)
            
            return True, "Comment flagged for review"
            
        except Exception as e:
            current_app.logger.error(f"Comment flagging error: {str(e)}")
            return False, "Failed to flag comment"
    
    @staticmethod
    def moderate_comment(comment_id, moderator_id, action, reason=None):
        """
        Moderate a comment (approve, hide, delete).
        
        Args:
            comment_id (str): Comment ID
            moderator_id (str): Moderator user ID
            action (str): Moderation action ('approve', 'hide', 'delete')
            reason (str): Moderation reason
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Check moderator permissions
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_admin or moderator.is_moderator):
                return False, "Insufficient permissions"
            
            # Get comment
            comment = db.session.get(Comment, comment_id)
            if not comment:
                return False, "Comment not found"
            
            # Apply moderation action
            if action == 'approve':
                # For now, just mark as not deleted since we don't have is_hidden field
                pass
            elif action == 'hide':
                # For now, soft delete to hide
                comment.delete()
            elif action == 'delete':
                comment.delete()
            else:
                return False, "Invalid moderation action"
            
            comment.save()
            
            # Log moderation action
            AuditService.log_action(
                user_id=moderator_id,
                action_type=f'comment_moderate_{action}',
                resource_type='comment',
                resource_id=comment_id,
                new_values=reason,
                success=True
            )
            
            action_past = 'hidden' if action == 'hide' else f"{action}d"
            return True, f"Comment {action_past} successfully"
            
        except Exception as e:
            current_app.logger.error(f"Comment moderation error: {str(e)}")
            return False, "Failed to moderate comment"
    
    @staticmethod
    def _check_auto_moderation(comment_id):
        """
        Check if a comment should be auto-moderated based on flags.
        
        Args:
            comment_id (str): Comment ID
        """
        try:
            # Count flags for this comment
            flag_count = len([
                log for log in AuditService.get_resource_audit_trail('comment', comment_id, 100)
                if log.action == 'comment_flag'
            ])
            
            auto_hide_threshold = current_app.config.get('AUTO_HIDE_COMMENT_FLAGS', 5)
            
            if flag_count >= auto_hide_threshold:
                comment = db.session.get(Comment, comment_id)
                if comment and not comment.is_deleted:
                    # For now, just soft delete to hide
                    comment.delete()
                    
                    # Log auto-moderation
                    AuditService.log_action(
                        action_type='comment_auto_moderate',
                        resource_type='comment',
                        resource_id=comment_id,
                        new_values=f'Auto-hidden with {flag_count} flags',
                        success=True
                    )
                    
        except Exception as e:
            current_app.logger.error(f"Auto-moderation check error: {str(e)}")
    
    @staticmethod
    def get_flagged_comments(limit=50):
        """
        Get comments that have been flagged for moderation.
        
        Args:
            limit (int): Maximum number of comments
            
        Returns:
            list: Flagged comments with flag counts
        """
        try:
            # Get all comment flag audit logs
            flag_logs = AuditService.get_resource_audit_trail('comment', None, 1000)
            flag_logs = [log for log in flag_logs if log.action == 'comment_flag']
            
            # Count flags per comment
            flag_counts = {}
            for log in flag_logs:
                comment_id = log.resource_id
                if comment_id not in flag_counts:
                    flag_counts[comment_id] = 0
                flag_counts[comment_id] += 1
            
            # Get comments with flags
            flagged_comments = []
            for comment_id, flag_count in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
                comment = db.session.get(Comment, comment_id)
                if comment and not comment.is_deleted:
                    flagged_comments.append({
                        'comment': comment,
                        'flag_count': flag_count
                    })
            
            return flagged_comments
            
        except Exception as e:
            current_app.logger.error(f"Error getting flagged comments: {str(e)}")
            return []
