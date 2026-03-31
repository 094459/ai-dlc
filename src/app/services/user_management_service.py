"""
User Management Service for bulk user operations and advanced account management.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import func, desc, and_, or_
from app.models import (
    db, User, UserProfile, Fact, Comment, Report, ModerationAction,
    UserModerationHistory, AnalyticsEvent
)
from app.models.admin import AdminActivity
from app.components.moderation.services import UserModerationService


class UserManagementService:
    """Service for advanced user management and bulk operations."""
    
    def __init__(self):
        self.moderation_service = UserModerationService()
    
    def search_users(self, query: str = None, filters: Dict[str, Any] = None, 
                    page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Search and filter users with pagination.
        
        Args:
            query: Search query for username or email
            filters: Dictionary of filters (role, status, etc.)
            page: Page number for pagination
            per_page: Number of users per page
            
        Returns:
            Dictionary containing users and pagination info
        """
        try:
            # Start with base query
            user_query = User.query.filter_by(is_deleted=False)
            
            # Apply search query
            if query and len(query.strip()) >= 2:
                search_term = f"%{query.strip()}%"
                user_query = user_query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term)
                    )
                )
            
            # Apply filters
            if filters:
                if filters.get('role'):
                    user_query = user_query.filter_by(role=filters['role'])
                
                if filters.get('is_active') is not None:
                    user_query = user_query.filter_by(is_active=filters['is_active'])
                
                if filters.get('is_suspended') is not None:
                    user_query = user_query.filter_by(is_suspended=filters['is_suspended'])
                
                if filters.get('is_banned') is not None:
                    user_query = user_query.filter_by(is_banned=filters['is_banned'])
                
                if filters.get('created_after'):
                    user_query = user_query.filter(User.created_at >= filters['created_after'])
                
                if filters.get('created_before'):
                    user_query = user_query.filter(User.created_at <= filters['created_before'])
                
                if filters.get('last_login_after'):
                    user_query = user_query.filter(User.last_login >= filters['last_login_after'])
                
                if filters.get('has_reports'):
                    user_query = user_query.join(Report, Report.reported_user_id == User.id)
            
            # Get total count before pagination
            total_count = user_query.count()
            
            # Apply pagination and ordering
            users = user_query.order_by(desc(User.created_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Format user data
            user_list = []
            for user in users.items:
                user_data = self._format_user_data(user)
                user_list.append(user_data)
            
            return {
                'users': user_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': users.pages,
                    'has_prev': users.has_prev,
                    'has_next': users.has_next
                }
            }
            
        except Exception as e:
            return {
                'users': [],
                'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'pages': 0},
                'error': str(e)
            }
    
    def get_user_details(self, user_id: str, admin_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific user.
        
        Args:
            user_id: ID of user to get details for
            admin_user_id: ID of admin requesting details
            
        Returns:
            Dictionary containing detailed user information
        """
        try:
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
            if not user:
                return None
            
            # Log admin access to user details
            self._log_admin_activity(
                admin_user_id,
                'user_management',
                'view_user_details',
                f'Viewed details for user {user.username}',
                target_type='user',
                target_id=user_id
            )
            
            # Get user statistics
            user_stats = self._get_user_statistics(user)
            
            # Get moderation history
            moderation_history = self._get_user_moderation_history(user_id)
            
            # Get recent activity
            recent_activity = self._get_user_recent_activity(user_id)
            
            # Get user's content summary
            content_summary = self._get_user_content_summary(user_id)
            
            return {
                'user': self._format_user_data(user, include_sensitive=True),
                'statistics': user_stats,
                'moderation_history': moderation_history,
                'recent_activity': recent_activity,
                'content_summary': content_summary
            }
            
        except Exception as e:
            self._log_admin_activity(
                admin_user_id,
                'user_management_error',
                'view_details_error',
                f'Error viewing user details for {user_id}: {str(e)}',
                severity='medium'
            )
            return None
    
    def bulk_update_users(self, user_ids: List[str], updates: Dict[str, Any], 
                         admin_user_id: str) -> Dict[str, Any]:
        """
        Perform bulk updates on multiple users.
        
        Args:
            user_ids: List of user IDs to update
            updates: Dictionary of fields to update
            admin_user_id: ID of admin performing updates
            
        Returns:
            Dictionary containing operation results
        """
        try:
            if not user_ids:
                return {'success': False, 'error': 'No users specified'}
            
            # Validate updates
            allowed_updates = {
                'is_active', 'is_suspended', 'is_banned', 'role', 
                'email_verified', 'profile_visibility'
            }
            
            invalid_fields = set(updates.keys()) - allowed_updates
            if invalid_fields:
                return {
                    'success': False, 
                    'error': f'Invalid update fields: {", ".join(invalid_fields)}'
                }
            
            # Get users to update
            users = User.query.filter(
                User.id.in_(user_ids),
                User.is_deleted == False
            ).all()
            
            if not users:
                return {'success': False, 'error': 'No valid users found'}
            
            # Prevent admins from modifying other admins
            admin_users = [u for u in users if u.role == 'admin']
            if admin_users:
                return {
                    'success': False, 
                    'error': 'Cannot bulk modify admin users'
                }
            
            updated_count = 0
            errors = []
            
            for user in users:
                try:
                    # Apply updates
                    for field, value in updates.items():
                        if hasattr(user, field):
                            old_value = getattr(user, field)
                            setattr(user, field, value)
                            
                            # Log individual field changes
                            if old_value != value:
                                self._log_user_field_change(
                                    admin_user_id, user.id, field, old_value, value
                                )
                    
                    user.updated_at = datetime.utcnow()
                    updated_count += 1
                    
                except Exception as e:
                    errors.append(f'Error updating user {user.username}: {str(e)}')
            
            if updated_count > 0:
                db.session.commit()
                
                # Log bulk operation
                self._log_admin_activity(
                    admin_user_id,
                    'user_management',
                    'bulk_update',
                    f'Bulk updated {updated_count} users',
                    severity='medium',
                    details={
                        'updated_count': updated_count,
                        'updates_applied': updates,
                        'user_ids': user_ids
                    }
                )
            
            return {
                'success': True,
                'updated_count': updated_count,
                'errors': errors
            }
            
        except Exception as e:
            db.session.rollback()
            self._log_admin_activity(
                admin_user_id,
                'user_management_error',
                'bulk_update_error',
                f'Error in bulk user update: {str(e)}',
                severity='high'
            )
            return {'success': False, 'error': str(e)}
    
    def suspend_users(self, user_ids: List[str], reason: str, duration_hours: int,
                     admin_user_id: str) -> Dict[str, Any]:
        """
        Suspend multiple users with specified duration and reason.
        
        Args:
            user_ids: List of user IDs to suspend
            reason: Reason for suspension
            duration_hours: Duration of suspension in hours
            admin_user_id: ID of admin performing suspensions
            
        Returns:
            Dictionary containing operation results
        """
        try:
            if not user_ids:
                return {'success': False, 'error': 'No users specified'}
            
            users = User.query.filter(
                User.id.in_(user_ids),
                User.is_deleted == False,
                User.role != 'admin'  # Prevent suspending admins
            ).all()
            
            if not users:
                return {'success': False, 'error': 'No valid users found'}
            
            suspended_count = 0
            errors = []
            
            for user in users:
                try:
                    # Use moderation service for proper suspension
                    result = self.moderation_service.suspend_user(
                        user.id, admin_user_id, reason, duration_hours
                    )
                    
                    if result['success']:
                        suspended_count += 1
                    else:
                        errors.append(f'Error suspending {user.username}: {result.get("error", "Unknown error")}')
                        
                except Exception as e:
                    errors.append(f'Error suspending {user.username}: {str(e)}')
            
            # Log bulk suspension
            if suspended_count > 0:
                self._log_admin_activity(
                    admin_user_id,
                    'user_moderation',
                    'bulk_suspend',
                    f'Bulk suspended {suspended_count} users for {duration_hours} hours',
                    severity='high',
                    details={
                        'suspended_count': suspended_count,
                        'reason': reason,
                        'duration_hours': duration_hours,
                        'user_ids': user_ids
                    }
                )
            
            return {
                'success': True,
                'suspended_count': suspended_count,
                'errors': errors
            }
            
        except Exception as e:
            self._log_admin_activity(
                admin_user_id,
                'user_management_error',
                'bulk_suspend_error',
                f'Error in bulk user suspension: {str(e)}',
                severity='high'
            )
            return {'success': False, 'error': str(e)}
    
    def export_user_data(self, filters: Dict[str, Any] = None, 
                        admin_user_id: str = None) -> List[Dict[str, Any]]:
        """
        Export user data based on filters.
        
        Args:
            filters: Dictionary of filters to apply
            admin_user_id: ID of admin requesting export
            
        Returns:
            List of user data dictionaries
        """
        try:
            # Start with base query
            user_query = User.query.filter_by(is_deleted=False)
            
            # Apply filters
            if filters:
                if filters.get('role'):
                    user_query = user_query.filter_by(role=filters['role'])
                
                if filters.get('is_active') is not None:
                    user_query = user_query.filter_by(is_active=filters['is_active'])
                
                if filters.get('created_after'):
                    user_query = user_query.filter(User.created_at >= filters['created_after'])
                
                if filters.get('created_before'):
                    user_query = user_query.filter(User.created_at <= filters['created_before'])
            
            users = user_query.order_by(User.created_at).all()
            
            # Format export data
            export_data = []
            for user in users:
                user_stats = self._get_user_statistics(user)
                
                export_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'is_suspended': user.is_suspended,
                    'is_banned': user.is_banned,
                    'email_verified': user.email_verified,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'fact_count': user_stats['fact_count'],
                    'comment_count': user_stats['comment_count'],
                    'total_votes_received': user_stats['total_votes_received'],
                    'reports_made': user_stats['reports_made'],
                    'reports_received': user_stats['reports_received']
                })
            
            # Log export operation
            if admin_user_id:
                self._log_admin_activity(
                    admin_user_id,
                    'data_export',
                    'export_users',
                    f'Exported data for {len(export_data)} users',
                    severity='medium',
                    details={'export_count': len(export_data), 'filters': filters}
                )
            
            return export_data
            
        except Exception as e:
            if admin_user_id:
                self._log_admin_activity(
                    admin_user_id,
                    'data_export_error',
                    'export_users_error',
                    f'Error exporting user data: {str(e)}',
                    severity='medium'
                )
            return []
    
    def get_user_activity_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get user activity summary for the specified number of days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing activity summary
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # New user registrations
            new_users = User.query.filter(
                User.created_at >= start_date,
                User.is_deleted == False
            ).count()
            
            # Active users (users who logged in)
            active_users = User.query.filter(
                User.last_login >= start_date,
                User.is_deleted == False
            ).count()
            
            # Users by role
            role_counts = db.session.query(
                User.role, func.count(User.id)
            ).filter(
                User.created_at >= start_date,
                User.is_deleted == False
            ).group_by(User.role).all()
            
            # Daily registration trend
            daily_registrations = db.session.query(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            ).filter(
                User.created_at >= start_date,
                User.is_deleted == False
            ).group_by(func.date(User.created_at)).order_by('date').all()
            
            return {
                'period_days': days,
                'new_users': new_users,
                'active_users': active_users,
                'role_distribution': {role: count for role, count in role_counts},
                'daily_registrations': [
                    {'date': date.isoformat(), 'count': count}
                    for date, count in daily_registrations
                ]
            }
            
        except Exception:
            return {
                'period_days': days,
                'new_users': 0,
                'active_users': 0,
                'role_distribution': {},
                'daily_registrations': []
            }
    
    def _format_user_data(self, user: User, include_sensitive: bool = False) -> Dict[str, Any]:
        """Format user data for API responses."""
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'is_suspended': user.is_suspended,
            'is_banned': user.is_banned,
            'email_verified': user.email_verified,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        if include_sensitive:
            user_data.update({
                'email': user.email,
                'suspension_end': user.suspension_end.isoformat() if user.suspension_end else None,
                'ban_reason': user.ban_reason
            })
        
        return user_data
    
    def _get_user_statistics(self, user: User) -> Dict[str, Any]:
        """Get comprehensive statistics for a user."""
        try:
            # Content statistics
            fact_count = Fact.query.filter_by(author_id=user.id, is_deleted=False).count()
            comment_count = Comment.query.filter_by(author_id=user.id, is_deleted=False).count()
            
            # Vote statistics (votes received on user's content)
            from app.models.community import FactVote, CommentVote
            
            fact_votes = db.session.query(func.count(FactVote.id)).join(Fact).filter(
                Fact.author_id == user.id,
                Fact.is_deleted == False
            ).scalar() or 0
            
            comment_votes = db.session.query(func.count(CommentVote.id)).join(Comment).filter(
                Comment.author_id == user.id,
                Comment.is_deleted == False
            ).scalar() or 0
            
            # Report statistics
            reports_made = Report.query.filter_by(reporter_id=user.id).count()
            reports_received = Report.query.filter_by(reported_user_id=user.id).count()
            
            # Moderation statistics
            moderation_actions = ModerationAction.query.filter_by(target_user_id=user.id).count()
            
            return {
                'fact_count': fact_count,
                'comment_count': comment_count,
                'total_votes_received': fact_votes + comment_votes,
                'reports_made': reports_made,
                'reports_received': reports_received,
                'moderation_actions': moderation_actions
            }
            
        except Exception:
            return {
                'fact_count': 0,
                'comment_count': 0,
                'total_votes_received': 0,
                'reports_made': 0,
                'reports_received': 0,
                'moderation_actions': 0
            }
    
    def _get_user_moderation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's moderation history."""
        try:
            history = UserModerationHistory.query.filter_by(
                user_id=user_id
            ).order_by(desc(UserModerationHistory.created_at)).limit(20).all()
            
            return [
                {
                    'id': record.id,
                    'action_type': record.action_type,
                    'reason': record.reason,
                    'moderator': record.moderator.username if record.moderator else 'System',
                    'created_at': record.created_at.isoformat(),
                    'expires_at': record.expires_at.isoformat() if record.expires_at else None,
                    'is_active': record.is_active
                }
                for record in history
            ]
            
        except Exception:
            return []
    
    def _get_user_recent_activity(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's recent activity."""
        try:
            # Get recent facts and comments
            recent_facts = Fact.query.filter_by(
                author_id=user_id, is_deleted=False
            ).order_by(desc(Fact.created_at)).limit(5).all()
            
            recent_comments = Comment.query.filter_by(
                author_id=user_id, is_deleted=False
            ).order_by(desc(Comment.created_at)).limit(5).all()
            
            activities = []
            
            for fact in recent_facts:
                activities.append({
                    'type': 'fact_created',
                    'title': fact.title,
                    'created_at': fact.created_at.isoformat(),
                    'id': fact.id
                })
            
            for comment in recent_comments:
                activities.append({
                    'type': 'comment_created',
                    'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                    'created_at': comment.created_at.isoformat(),
                    'id': comment.id
                })
            
            # Sort by creation date
            activities.sort(key=lambda x: x['created_at'], reverse=True)
            return activities[:10]
            
        except Exception:
            return []
    
    def _get_user_content_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's content."""
        try:
            # Recent facts
            recent_facts = Fact.query.filter_by(
                author_id=user_id, is_deleted=False
            ).order_by(desc(Fact.created_at)).limit(5).all()
            
            # Recent comments
            recent_comments = Comment.query.filter_by(
                author_id=user_id, is_deleted=False
            ).order_by(desc(Comment.created_at)).limit(5).all()
            
            return {
                'recent_facts': [
                    {
                        'id': fact.id,
                        'title': fact.title,
                        'created_at': fact.created_at.isoformat(),
                        'is_published': fact.is_published
                    }
                    for fact in recent_facts
                ],
                'recent_comments': [
                    {
                        'id': comment.id,
                        'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                        'created_at': comment.created_at.isoformat(),
                        'fact_id': comment.fact_id
                    }
                    for comment in recent_comments
                ]
            }
            
        except Exception:
            return {'recent_facts': [], 'recent_comments': []}
    
    def _log_user_field_change(self, admin_id: str, user_id: str, field: str, 
                              old_value: Any, new_value: Any):
        """Log individual user field changes."""
        try:
            self._log_admin_activity(
                admin_id,
                'user_field_change',
                f'update_{field}',
                f'Changed user {field} from "{old_value}" to "{new_value}"',
                target_type='user',
                target_id=user_id,
                details={
                    'field': field,
                    'old_value': str(old_value),
                    'new_value': str(new_value)
                }
            )
        except Exception:
            pass
    
    def _log_admin_activity(self, admin_id: str, activity_type: str, action: str, 
                           description: str, target_type: str = None, target_id: str = None,
                           severity: str = 'low', details: Dict = None):
        """Log admin activity for audit purposes."""
        try:
            activity = AdminActivity(
                admin_id=admin_id,
                activity_type=activity_type,
                action=action,
                description=description,
                target_type=target_type,
                target_id=target_id,
                severity=severity,
                details=details
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception:
            # Don't let logging errors break the main functionality
            db.session.rollback()
