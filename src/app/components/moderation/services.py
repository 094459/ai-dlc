"""
Moderation Component Services

Provides comprehensive moderation functionality for content and user management.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import (
    User, Fact, Comment, ModerationAction, UserModerationHistory, 
    ModerationWorkflow, Report, AuditLog
)
from app.components.security.services import AuditService

logger = logging.getLogger(__name__)


class ContentModerationService:
    """Service for content moderation actions (facts and comments)."""
    
    @staticmethod
    def remove_content(content_type: str, content_id: str, moderator_id: str, 
                      reason: str, permanent: bool = False, related_report_id: str = None) -> Tuple[bool, str]:
        """
        Remove content (soft delete with restoration capability).
        
        Args:
            content_type: Type of content ('fact' or 'comment')
            content_id: ID of the content to remove
            moderator_id: ID of the moderator performing the action
            reason: Reason for removal
            permanent: Whether the removal is permanent
            related_report_id: ID of related report if applicable
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate content type
            if content_type not in ['fact', 'comment']:
                return False, "Invalid content type"
            
            # Get content object
            content = ContentModerationService._get_content(content_type, content_id)
            if not content:
                return False, f"{content_type.title()} not found"
            
            # Check if already deleted
            if content.is_deleted:
                return False, f"{content_type.title()} is already removed"
            
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions"
            
            # Perform soft delete
            content.is_deleted = True
            content.deleted_at = datetime.utcnow()
            
            # Create moderation action record
            action = ModerationAction(
                moderator_id=moderator_id,
                action_type='remove_permanent' if permanent else 'remove_temporary',
                target_type=content_type,
                target_id=content_id,
                related_report_id=related_report_id,
                reason=reason,
                action_category='content',
                severity_level=3 if permanent else 2,
                is_active=True
            )
            
            db.session.add(action)
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=moderator_id,
                action_type=f'{content_type}_remove',
                resource_type=content_type,
                resource_id=content_id,
                new_values={'removed': True, 'permanent': permanent, 'reason': reason}
            )
            
            action_word = "permanently removed" if permanent else "removed"
            return True, f"{content_type.title()} {action_word} successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error removing {content_type}: {str(e)}")
            return False, f"Failed to remove {content_type}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing {content_type}: {str(e)}")
            return False, f"Failed to remove {content_type}"
    
    @staticmethod
    def restore_content(content_type: str, content_id: str, moderator_id: str, 
                       reason: str) -> Tuple[bool, str]:
        """
        Restore previously removed content.
        
        Args:
            content_type: Type of content ('fact' or 'comment')
            content_id: ID of the content to restore
            moderator_id: ID of the moderator performing the action
            reason: Reason for restoration
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate content type
            if content_type not in ['fact', 'comment']:
                return False, "Invalid content type"
            
            # Get content object
            content = ContentModerationService._get_content(content_type, content_id)
            if not content:
                return False, f"{content_type.title()} not found"
            
            # Check if actually deleted
            if not content.is_deleted:
                return False, f"{content_type.title()} is not removed"
            
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions"
            
            # Restore content
            content.is_deleted = False
            content.deleted_at = None
            
            # Deactivate previous removal actions
            previous_actions = ModerationAction.query.filter(
                and_(
                    ModerationAction.target_type == content_type,
                    ModerationAction.target_id == content_id,
                    ModerationAction.action_type.in_(['remove_temporary', 'remove_permanent']),
                    ModerationAction.is_active == True
                )
            ).all()
            
            for action in previous_actions:
                action.is_active = False
            
            # Create restoration action record
            restore_action = ModerationAction(
                moderator_id=moderator_id,
                action_type='restore',
                target_type=content_type,
                target_id=content_id,
                reason=reason,
                action_category='content',
                severity_level=1,
                is_active=True
            )
            
            db.session.add(restore_action)
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=moderator_id,
                action_type=f'{content_type}_restore',
                resource_type=content_type,
                resource_id=content_id,
                new_values={'restored': True, 'reason': reason}
            )
            
            return True, f"{content_type.title()} restored successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error restoring {content_type}: {str(e)}")
            return False, f"Failed to restore {content_type}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error restoring {content_type}: {str(e)}")
            return False, f"Failed to restore {content_type}"
    
    @staticmethod
    def hide_content(content_type: str, content_id: str, moderator_id: str, 
                    reason: str, duration_hours: int = None) -> Tuple[bool, str]:
        """
        Hide content temporarily (different from removal - content is hidden but not deleted).
        
        Args:
            content_type: Type of content ('fact' or 'comment')
            content_id: ID of the content to hide
            moderator_id: ID of the moderator performing the action
            reason: Reason for hiding
            duration_hours: Duration to hide content (None for indefinite)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate content type
            if content_type not in ['fact', 'comment']:
                return False, "Invalid content type"
            
            # Get content object
            content = ContentModerationService._get_content(content_type, content_id)
            if not content:
                return False, f"{content_type.title()} not found"
            
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions"
            
            # Calculate expiration if duration provided
            expires_at = None
            if duration_hours:
                expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
            
            # Create hide action record
            action = ModerationAction(
                moderator_id=moderator_id,
                action_type='hide',
                target_type=content_type,
                target_id=content_id,
                reason=reason,
                action_category='content',
                severity_level=1,
                duration_hours=duration_hours,
                expires_at=expires_at,
                is_active=True
            )
            
            db.session.add(action)
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=moderator_id,
                action_type=f'{content_type}_hide',
                resource_type=content_type,
                resource_id=content_id,
                new_values={'hidden': True, 'duration_hours': duration_hours, 'reason': reason}
            )
            
            duration_text = f" for {duration_hours} hours" if duration_hours else " indefinitely"
            return True, f"{content_type.title()} hidden{duration_text} successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error hiding {content_type}: {str(e)}")
            return False, f"Failed to hide {content_type}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error hiding {content_type}: {str(e)}")
            return False, f"Failed to hide {content_type}"
    
    @staticmethod
    def get_moderated_content(moderator_id: str = None, action_type: str = None, 
                            page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get list of moderated content with filtering options.
        
        Args:
            moderator_id: Filter by specific moderator
            action_type: Filter by action type
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Dictionary with moderated content data and pagination info
        """
        try:
            query = ModerationAction.query.filter(
                ModerationAction.action_category == 'content'
            )
            
            if moderator_id:
                query = query.filter(ModerationAction.moderator_id == moderator_id)
            
            if action_type:
                query = query.filter(ModerationAction.action_type == action_type)
            
            # Order by most recent first
            query = query.order_by(desc(ModerationAction.created_at))
            
            # Paginate results
            paginated = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Build response with content details
            actions_data = []
            for action in paginated.items:
                content = ContentModerationService._get_content(action.target_type, action.target_id)
                moderator = db.session.get(User, action.moderator_id)
                
                action_data = {
                    'action': action,
                    'content': content,
                    'moderator': moderator,
                    'content_preview': ContentModerationService._get_content_preview(content) if content else None
                }
                actions_data.append(action_data)
            
            return {
                'actions': actions_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated.total,
                    'pages': paginated.pages,
                    'has_prev': paginated.has_prev,
                    'has_next': paginated.has_next
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting moderated content: {str(e)}")
            return {
                'actions': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0,
                    'has_prev': False,
                    'has_next': False
                }
            }
    
    @staticmethod
    def _get_content(content_type: str, content_id: str):
        """Get content object by type and ID."""
        if content_type == 'fact':
            return db.session.get(Fact, content_id)
        elif content_type == 'comment':
            return db.session.get(Comment, content_id)
        return None
    
    @staticmethod
    def _get_content_preview(content, max_length: int = 100) -> str:
        """Get a preview of content for display."""
        if not content:
            return "Content not found"
        
        text = content.content if hasattr(content, 'content') else str(content)
        if len(text) <= max_length:
            return text

class UserModerationService:
    """Service for user moderation actions (warnings, suspensions, bans)."""
    
    @staticmethod
    def warn_user(user_id: str, moderator_id: str, reason: str, severity_level: int = 1,
                  related_content_type: str = None, related_content_id: str = None,
                  related_report_id: str = None) -> Tuple[bool, str]:
        """
        Issue a warning to a user.
        
        Args:
            user_id: ID of the user to warn
            moderator_id: ID of the moderator issuing the warning
            reason: Reason for the warning
            severity_level: Severity level (1-5)
            related_content_type: Type of related content if applicable
            related_content_id: ID of related content if applicable
            related_report_id: ID of related report if applicable
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate user
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions"
            
            # Cannot moderate other moderators/admins unless you're an admin
            if (user.is_moderator or user.is_admin) and not moderator.is_admin:
                return False, "Cannot moderate other moderators or administrators"
            
            # Create user moderation history record
            history = UserModerationHistory(
                user_id=user_id,
                action_type='warning',
                moderator_id=moderator_id,
                reason=reason,
                severity_level=severity_level,
                related_content_type=related_content_type,
                related_content_id=related_content_id,
                related_report_id=related_report_id,
                is_active=True
            )
            
            # Update user warning count
            user.increment_warning_count()
            
            # Create moderation action record
            action = ModerationAction(
                moderator_id=moderator_id,
                action_type='user_warning',
                target_type='user',
                target_id=user_id,
                related_report_id=related_report_id,
                reason=reason,
                action_category='user',
                severity_level=severity_level,
                is_active=True
            )
            
            db.session.add(history)
            db.session.add(action)
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=moderator_id,
                action_type='user_warning',
                resource_type='user',
                resource_id=user_id,
                new_values={'warning_count': user.warning_count, 'severity': severity_level, 'reason': reason}
            )
            
            return True, f"Warning issued to user successfully (Warning #{user.warning_count})"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error warning user: {str(e)}")
            return False, "Failed to issue warning"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error warning user: {str(e)}")
            return False, "Failed to issue warning"
    
    @staticmethod
    def suspend_user(user_id: str, moderator_id: str, reason: str, duration_hours: int,
                     severity_level: int = 2, related_report_id: str = None) -> Tuple[bool, str]:
        """
        Suspend a user for a specified duration.
        
        Args:
            user_id: ID of the user to suspend
            moderator_id: ID of the moderator performing the suspension
            reason: Reason for suspension
            duration_hours: Duration of suspension in hours
            severity_level: Severity level (1-5)
            related_report_id: ID of related report if applicable
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate user
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions"
            
            # Cannot moderate other moderators/admins unless you're an admin
            if (user.is_moderator or user.is_admin) and not moderator.is_admin:
                return False, "Cannot moderate other moderators or administrators"
            
            # Check if user is already suspended
            if user.is_suspended and user.suspension_expires and datetime.utcnow() < user.suspension_expires:
                return False, "User is already suspended"
            
            # Calculate suspension expiration
            expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
            
            # Update user suspension status
            user.is_suspended = True
            user.suspension_expires = expires_at
            
            # Create user moderation history record
            history = UserModerationHistory(
                user_id=user_id,
                action_type='suspension',
                moderator_id=moderator_id,
                reason=reason,
                severity_level=severity_level,
                duration_hours=duration_hours,
                expires_at=expires_at,
                related_report_id=related_report_id,
                is_active=True
            )
            
            # Create moderation action record
            action = ModerationAction(
                moderator_id=moderator_id,
                action_type='user_suspension',
                target_type='user',
                target_id=user_id,
                related_report_id=related_report_id,
                reason=reason,
                action_category='user',
                severity_level=severity_level,
                duration_hours=duration_hours,
                expires_at=expires_at,
                is_active=True
            )
            
            db.session.add(history)
            db.session.add(action)
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=moderator_id,
                action_type='user_suspension',
                resource_type='user',
                resource_id=user_id,
                new_values={'suspended': True, 'duration_hours': duration_hours, 'expires_at': expires_at.isoformat(), 'reason': reason}
            )
            
            return True, f"User suspended for {duration_hours} hours successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error suspending user: {str(e)}")
            return False, "Failed to suspend user"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error suspending user: {str(e)}")
            return False, "Failed to suspend user"
    
    @staticmethod
    def ban_user(user_id: str, moderator_id: str, reason: str, permanent: bool = False,
                 severity_level: int = 5, related_report_id: str = None) -> Tuple[bool, str]:
        """
        Ban a user permanently or temporarily.
        
        Args:
            user_id: ID of the user to ban
            moderator_id: ID of the moderator performing the ban
            reason: Reason for ban
            permanent: Whether the ban is permanent
            severity_level: Severity level (1-5)
            related_report_id: ID of related report if applicable
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate user
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions"
            
            # Cannot moderate other moderators/admins unless you're an admin
            if (user.is_moderator or user.is_admin) and not moderator.is_admin:
                return False, "Cannot moderate other moderators or administrators"
            
            # Check if user is already banned
            if user.is_banned:
                return False, "User is already banned"
            
            # Update user ban status
            user.is_banned = True
            user.ban_reason = reason
            user.is_active = False  # Deactivate account
            
            # Clear any existing suspension
            user.is_suspended = False
            user.suspension_expires = None
            
            # Create user moderation history record
            history = UserModerationHistory(
                user_id=user_id,
                action_type='ban_permanent' if permanent else 'ban_temporary',
                moderator_id=moderator_id,
                reason=reason,
                severity_level=severity_level,
                related_report_id=related_report_id,
                is_active=True
            )
            
            # Create moderation action record
            action = ModerationAction(
                moderator_id=moderator_id,
                action_type='user_ban_permanent' if permanent else 'user_ban_temporary',
                target_type='user',
                target_id=user_id,
                related_report_id=related_report_id,
                reason=reason,
                action_category='user',
                severity_level=severity_level,
                is_active=True
            )
            
            db.session.add(history)
            db.session.add(action)
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=moderator_id,
                action_type='user_ban',
                resource_type='user',
                resource_id=user_id,
                new_values={'banned': True, 'permanent': permanent, 'reason': reason}
            )
            
            ban_type = "permanently" if permanent else "temporarily"
            return True, f"User banned {ban_type} successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error banning user: {str(e)}")
            return False, "Failed to ban user"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error banning user: {str(e)}")
            return False, "Failed to ban user"
    
    @staticmethod
    def lift_user_restriction(user_id: str, moderator_id: str, reason: str) -> Tuple[bool, str]:
        """
        Lift user restrictions (suspension or ban).
        
        Args:
            user_id: ID of the user to lift restrictions from
            moderator_id: ID of the moderator performing the action
            reason: Reason for lifting restrictions
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate user
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions"
            
            restrictions_lifted = []
            
            # Lift suspension
            if user.is_suspended:
                user.clear_suspension()
                restrictions_lifted.append("suspension")
            
            # Lift ban (requires admin privileges)
            if user.is_banned:
                if not moderator.is_admin:
                    return False, "Only administrators can lift bans"
                user.is_banned = False
                user.ban_reason = None
                user.is_active = True
                restrictions_lifted.append("ban")
            
            # Reset content restrictions
            if user.content_restriction_level > 0:
                user.content_restriction_level = 0
                restrictions_lifted.append("content restrictions")
            
            if not restrictions_lifted:
                return False, "User has no active restrictions to lift"
            
            # Deactivate related moderation actions
            active_actions = ModerationAction.query.filter(
                and_(
                    ModerationAction.target_type == 'user',
                    ModerationAction.target_id == user_id,
                    ModerationAction.is_active == True,
                    ModerationAction.action_type.in_([
                        'user_suspension', 'user_ban_temporary', 'user_ban_permanent'
                    ])
                )
            ).all()
            
            for action in active_actions:
                action.is_active = False
            
            # Create lift restriction action record
            lift_action = ModerationAction(
                moderator_id=moderator_id,
                action_type='user_restriction_lifted',
                target_type='user',
                target_id=user_id,
                reason=reason,
                action_category='user',
                severity_level=1,
                is_active=True
            )
            
            db.session.add(lift_action)
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=moderator_id,
                action_type='user_restriction_lifted',
                resource_type='user',
                resource_id=user_id,
                new_values={'restrictions_lifted': restrictions_lifted, 'reason': reason}
            )
            
            restrictions_text = ", ".join(restrictions_lifted)
            return True, f"User restrictions lifted successfully: {restrictions_text}"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error lifting user restrictions: {str(e)}")
            return False, "Failed to lift user restrictions"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error lifting user restrictions: {str(e)}")
            return False, "Failed to lift user restrictions"
    
    @staticmethod
    def get_user_moderation_history(user_id: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get moderation history for a specific user.
        
        Args:
            user_id: ID of the user
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Dictionary with user moderation history and pagination info
        """
        try:
            query = UserModerationHistory.query.filter(
                UserModerationHistory.user_id == user_id
            ).order_by(desc(UserModerationHistory.created_at))
            
            # Paginate results
            paginated = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Build response with moderator details
            history_data = []
            for history in paginated.items:
                moderator = db.session.get(User, history.moderator_id)
                
                history_item = {
                    'history': history,
                    'moderator': moderator,
                    'is_expired': history.is_expired,
                    'can_appeal': history.can_appeal
                }
                history_data.append(history_item)
            
            return {
                'history': history_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated.total,
                    'pages': paginated.pages,
                    'has_prev': paginated.has_prev,
                    'has_next': paginated.has_next
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user moderation history: {str(e)}")
            return {
                'history': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0,
                    'has_prev': False,
                    'has_next': False
                }
            }
    
    @staticmethod
    def get_users_requiring_attention(threshold: int = 3, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get users who may require moderation attention based on warning count or recent activity.
        
        Args:
            threshold: Warning count threshold for flagging users
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Dictionary with users requiring attention and pagination info
        """
        try:
            # Get users with high warning counts or recent moderation actions
            query = User.query.filter(
                or_(
                    User.warning_count >= threshold,
                    User.is_suspended == True,
                    User.content_restriction_level > 0
                )
            ).filter(
                User.is_banned == False  # Exclude already banned users
            ).order_by(desc(User.warning_count), desc(User.last_warning_date))
            
            # Paginate results
            paginated = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Build response with recent moderation history
            users_data = []
            for user in paginated.items:
                recent_history = UserModerationHistory.query.filter(
                    UserModerationHistory.user_id == user.id
                ).order_by(desc(UserModerationHistory.created_at)).limit(3).all()
                
                user_data = {
                    'user': user,
                    'moderation_status': user.get_moderation_status(),
                    'recent_history': recent_history,
                    'requires_attention': user.warning_count >= threshold
                }
                users_data.append(user_data)
            
            return {
                'users': users_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated.total,
                    'pages': paginated.pages,
                    'has_prev': paginated.has_prev,
                    'has_next': paginated.has_next
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting users requiring attention: {str(e)}")
            return {
                'users': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0,
                    'has_prev': False,
                    'has_next': False
                }
            }


class ModerationWorkflowService:
    """Service for automated moderation workflows and rules."""
    
    @staticmethod
    def create_workflow(name: str, description: str, trigger_type: str, 
                       conditions: Dict[str, Any], actions: List[Dict[str, Any]], 
                       moderator_id: str, priority: int = 1) -> Tuple[bool, str, Optional[ModerationWorkflow]]:
        """Create a new moderation workflow."""
        try:
            # Validate moderator
            moderator = db.session.get(User, moderator_id)
            if not moderator or not (moderator.is_moderator or moderator.is_admin):
                return False, "Invalid moderator or insufficient permissions", None
            
            # Create workflow
            workflow = ModerationWorkflow(
                name=name,
                description=description,
                trigger_type=trigger_type,
                trigger_conditions=conditions,
                actions=actions,
                priority=priority,
                created_by=moderator_id,
                is_active=True
            )
            
            db.session.add(workflow)
            db.session.commit()
            
            return True, "Moderation workflow created successfully", workflow
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating workflow: {str(e)}")
            return False, "Failed to create workflow", None
    
    @staticmethod
    def get_active_workflows(trigger_type: str = None) -> List[ModerationWorkflow]:
        """Get active moderation workflows."""
        try:
            query = ModerationWorkflow.query.filter(ModerationWorkflow.is_active == True)
            
            if trigger_type:
                query = query.filter(ModerationWorkflow.trigger_type == trigger_type)
            
            return query.order_by(desc(ModerationWorkflow.priority)).all()
            
        except Exception as e:
            logger.error(f"Error getting active workflows: {str(e)}")
            return []


class ModerationDashboardService:
    """Service for moderation analytics and dashboard data."""
    
    @staticmethod
    def get_moderation_overview(time_period: int = 7) -> Dict[str, Any]:
        """Get moderation overview statistics."""
        try:
            start_date = datetime.utcnow() - timedelta(days=time_period)
            
            # Content moderation stats
            content_actions = ModerationAction.query.filter(
                and_(
                    ModerationAction.action_category == 'content',
                    ModerationAction.created_at >= start_date
                )
            ).count()
            
            # User moderation stats
            user_actions = ModerationAction.query.filter(
                and_(
                    ModerationAction.action_category == 'user',
                    ModerationAction.created_at >= start_date
                )
            ).count()
            
            return {
                'time_period': time_period,
                'content_actions': content_actions,
                'user_actions': user_actions,
                'total_actions': content_actions + user_actions
            }
            
        except Exception as e:
            logger.error(f"Error getting moderation overview: {str(e)}")
            return {
                'time_period': time_period,
                'content_actions': 0,
                'user_actions': 0,
                'total_actions': 0
            }
