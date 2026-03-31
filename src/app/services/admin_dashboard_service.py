"""
Admin Dashboard Service for centralized dashboard data management and overview.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import func, desc, and_, or_
from app.models import (
    db, User, Fact, Comment, Report, ModerationAction, 
    AnalyticsEvent, Notification, SystemConfiguration,
    AdminActivity, SystemHealth, AdminDashboardWidget
)
from app.components.analytics.services import AnalyticsService, MetricsCalculationService


class AdminDashboardService:
    """Service for managing admin dashboard data and overview metrics."""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.metrics_service = MetricsCalculationService()
    
    def get_dashboard_overview(self, admin_user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard overview with key metrics and statistics.
        
        Args:
            admin_user_id: ID of the admin user requesting the overview
            
        Returns:
            Dictionary containing dashboard overview data
        """
        try:
            # Log admin dashboard access
            self._log_admin_activity(
                admin_user_id, 
                'dashboard_access', 
                'view_overview',
                'Admin accessed dashboard overview'
            )
            
            # Get current date for calculations
            now = datetime.utcnow()
            today = now.date()
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Core platform statistics
            total_users = User.query.filter_by(is_deleted=False).count()
            total_facts = Fact.query.filter_by(is_deleted=False).count()
            total_comments = Comment.query.filter_by(is_deleted=False).count()
            
            # Recent activity (last 24 hours)
            new_users_today = User.query.filter(
                User.created_at >= datetime.combine(today, datetime.min.time()),
                User.is_deleted == False
            ).count()
            
            new_facts_today = Fact.query.filter(
                Fact.created_at >= datetime.combine(today, datetime.min.time()),
                Fact.is_deleted == False
            ).count()
            
            new_comments_today = Comment.query.filter(
                Comment.created_at >= datetime.combine(today, datetime.min.time()),
                Comment.is_deleted == False
            ).count()
            
            # Moderation statistics
            pending_reports = Report.query.filter_by(status='pending').count()
            reports_today = Report.query.filter(
                Report.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
            
            moderation_actions_today = ModerationAction.query.filter(
                ModerationAction.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
            
            # System health overview
            system_health = self._get_system_health_summary()
            
            # User engagement metrics (last 7 days)
            active_users_week = self._get_active_users_count(week_ago)
            
            # Growth metrics (comparing this week vs last week)
            growth_metrics = self._calculate_growth_metrics(week_ago, today)
            
            # Recent admin activities
            recent_activities = self._get_recent_admin_activities(limit=10)
            
            # System alerts and notifications
            system_alerts = self._get_system_alerts()
            
            return {
                'overview': {
                    'total_users': total_users,
                    'total_facts': total_facts,
                    'total_comments': total_comments,
                    'new_users_today': new_users_today,
                    'new_facts_today': new_facts_today,
                    'new_comments_today': new_comments_today,
                    'active_users_week': active_users_week
                },
                'moderation': {
                    'pending_reports': pending_reports,
                    'reports_today': reports_today,
                    'moderation_actions_today': moderation_actions_today
                },
                'system_health': system_health,
                'growth_metrics': growth_metrics,
                'recent_activities': recent_activities,
                'system_alerts': system_alerts,
                'last_updated': now.isoformat()
            }
            
        except Exception as e:
            # Log error for debugging
            self._log_admin_activity(
                admin_user_id,
                'dashboard_error',
                'overview_error',
                f'Error getting dashboard overview: {str(e)}',
                severity='high'
            )
            raise
    
    def get_user_management_summary(self, admin_user_id: str) -> Dict[str, Any]:
        """
        Get user management summary with user statistics and recent activities.
        
        Args:
            admin_user_id: ID of the admin user
            
        Returns:
            Dictionary containing user management data
        """
        try:
            # User status distribution
            active_users = User.query.filter_by(is_active=True, is_deleted=False).count()
            inactive_users = User.query.filter_by(is_active=False, is_deleted=False).count()
            suspended_users = User.query.filter_by(is_suspended=True, is_deleted=False).count()
            banned_users = User.query.filter_by(is_banned=True, is_deleted=False).count()
            
            # User role distribution
            admin_count = User.query.filter_by(is_admin=True, is_deleted=False).count()
            moderator_count = User.query.filter_by(is_moderator=True, is_deleted=False).count()
            regular_user_count = User.query.filter_by(
                is_admin=False, is_moderator=False, is_deleted=False
            ).count()
            
            role_distribution = [
                ('admin', admin_count),
                ('moderator', moderator_count),
                ('user', regular_user_count)
            ]
            
            # Recent user registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = User.query.filter(
                User.created_at >= thirty_days_ago,
                User.is_deleted == False
            ).order_by(desc(User.created_at)).limit(20).all()
            
            # Users requiring attention (suspended, banned, or with recent reports)
            users_needing_attention = self._get_users_requiring_attention()
            
            # Top contributors (by fact and comment count)
            top_contributors = self._get_top_contributors()
            
            return {
                'user_counts': {
                    'active': active_users,
                    'inactive': inactive_users,
                    'suspended': suspended_users,
                    'banned': banned_users,
                    'total': active_users + inactive_users + suspended_users + banned_users
                },
                'role_distribution': {role: count for role, count in role_distribution},
                'recent_registrations': [
                    {
                        'id': user.id,
                        'email': user.email,
                        'created_at': user.created_at.isoformat(),
                        'is_active': user.is_active,
                        'is_admin': user.is_admin,
                        'is_moderator': user.is_moderator
                    }
                    for user in recent_registrations
                ],
                'users_needing_attention': users_needing_attention,
                'top_contributors': top_contributors
            }
            
        except Exception as e:
            self._log_admin_activity(
                admin_user_id,
                'user_management_error',
                'summary_error',
                f'Error getting user management summary: {str(e)}',
                severity='medium'
            )
            raise
    
    def get_content_management_summary(self, admin_user_id: str) -> Dict[str, Any]:
        """
        Get content management summary with content statistics and moderation data.
        
        Args:
            admin_user_id: ID of the admin user
            
        Returns:
            Dictionary containing content management data
        """
        try:
            # Content statistics
            total_facts = Fact.query.filter_by(is_deleted=False).count()
            total_comments = Comment.query.filter_by(is_deleted=False).count()
            
            # Content by status (all facts are published when created)
            published_facts = Fact.query.filter_by(is_deleted=False).count()
            draft_facts = 0  # No draft concept in current model
            
            # Recent content (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_facts = Fact.query.filter(
                Fact.created_at >= week_ago,
                Fact.is_deleted == False
            ).count()
            
            recent_comments = Comment.query.filter(
                Comment.created_at >= week_ago,
                Comment.is_deleted == False
            ).count()
            
            # Most reported content
            most_reported_content = self._get_most_reported_content()
            
            # Content requiring moderation
            content_needing_moderation = self._get_content_needing_moderation()
            
            return {
                'content_counts': {
                    'total_facts': total_facts,
                    'total_comments': total_comments,
                    'published_facts': published_facts,
                    'draft_facts': draft_facts,
                    'recent_facts': recent_facts,
                    'recent_comments': recent_comments
                },
                'most_reported_content': most_reported_content,
                'content_needing_moderation': content_needing_moderation
            }
            
        except Exception as e:
            self._log_admin_activity(
                admin_user_id,
                'content_management_error',
                'summary_error',
                f'Error getting content management summary: {str(e)}',
                severity='medium'
            )
            raise
    
    def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary from health checks."""
        try:
            # Get latest health checks
            latest_checks = db.session.query(SystemHealth).filter(
                SystemHealth.last_check_at >= datetime.utcnow() - timedelta(hours=1)
            ).all()
            
            if not latest_checks:
                return {
                    'status': 'unknown',
                    'message': 'No recent health checks available',
                    'checks': []
                }
            
            # Categorize health status
            healthy_count = sum(1 for check in latest_checks if check.status == 'healthy')
            warning_count = sum(1 for check in latest_checks if check.status == 'warning')
            critical_count = sum(1 for check in latest_checks if check.status == 'critical')
            
            # Determine overall status
            if critical_count > 0:
                overall_status = 'critical'
            elif warning_count > 0:
                overall_status = 'warning'
            else:
                overall_status = 'healthy'
            
            return {
                'status': overall_status,
                'healthy_checks': healthy_count,
                'warning_checks': warning_count,
                'critical_checks': critical_count,
                'total_checks': len(latest_checks),
                'last_check': max(check.last_check_at for check in latest_checks).isoformat() if latest_checks else None
            }
            
        except Exception:
            return {
                'status': 'unknown',
                'message': 'Error retrieving system health data',
                'checks': []
            }
    
    def _get_active_users_count(self, since_date) -> int:
        """Get count of active users since a specific date."""
        try:
            # Count users who have logged in or performed actions since the date
            active_count = db.session.query(User.id).filter(
                User.last_login >= datetime.combine(since_date, datetime.min.time()),
                User.is_deleted == False
            ).distinct().count()
            
            return active_count
        except Exception:
            return 0
    
    def _calculate_growth_metrics(self, start_date, end_date) -> Dict[str, Any]:
        """Calculate growth metrics comparing periods."""
        try:
            # Current period (last 7 days)
            current_start = datetime.combine(start_date, datetime.min.time())
            current_end = datetime.combine(end_date, datetime.min.time())
            
            # Previous period (7 days before that)
            previous_start = current_start - timedelta(days=7)
            previous_end = current_start
            
            # User growth
            current_users = User.query.filter(
                User.created_at >= current_start,
                User.created_at < current_end,
                User.is_deleted == False
            ).count()
            
            previous_users = User.query.filter(
                User.created_at >= previous_start,
                User.created_at < previous_end,
                User.is_deleted == False
            ).count()
            
            # Content growth
            current_facts = Fact.query.filter(
                Fact.created_at >= current_start,
                Fact.created_at < current_end,
                Fact.is_deleted == False
            ).count()
            
            previous_facts = Fact.query.filter(
                Fact.created_at >= previous_start,
                Fact.created_at < previous_end,
                Fact.is_deleted == False
            ).count()
            
            # Calculate percentage changes
            user_growth = self._calculate_percentage_change(previous_users, current_users)
            fact_growth = self._calculate_percentage_change(previous_facts, current_facts)
            
            return {
                'user_growth': {
                    'current': current_users,
                    'previous': previous_users,
                    'percentage': user_growth
                },
                'fact_growth': {
                    'current': current_facts,
                    'previous': previous_facts,
                    'percentage': fact_growth
                }
            }
            
        except Exception:
            return {
                'user_growth': {'current': 0, 'previous': 0, 'percentage': 0},
                'fact_growth': {'current': 0, 'previous': 0, 'percentage': 0}
            }
    
    def _calculate_percentage_change(self, old_value: int, new_value: int) -> float:
        """Calculate percentage change between two values."""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return round(((new_value - old_value) / old_value) * 100, 1)
    
    def _get_recent_admin_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent admin activities."""
        try:
            activities = AdminActivity.query.order_by(
                desc(AdminActivity.created_at)
            ).limit(limit).all()
            
            return [
                {
                    'id': activity.id,
                    'admin_username': activity.admin.username if activity.admin else 'Unknown',
                    'activity_type': activity.activity_type,
                    'action': activity.action,
                    'description': activity.description,
                    'severity': activity.severity,
                    'created_at': activity.created_at.isoformat()
                }
                for activity in activities
            ]
            
        except Exception:
            return []
    
    def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get current system alerts and notifications."""
        try:
            alerts = []
            
            # Check for critical system health issues
            critical_health = SystemHealth.query.filter_by(status='critical').all()
            for health in critical_health:
                alerts.append({
                    'type': 'system_health',
                    'severity': 'critical',
                    'message': f'Critical health issue: {health.check_name}',
                    'details': health.message
                })
            
            # Check for high number of pending reports
            pending_reports = Report.query.filter_by(status='pending').count()
            if pending_reports > 50:  # Configurable threshold
                alerts.append({
                    'type': 'moderation',
                    'severity': 'warning',
                    'message': f'{pending_reports} pending reports require attention',
                    'details': 'High volume of pending moderation reports'
                })
            
            return alerts
            
        except Exception:
            return []
    
    def _get_users_requiring_attention(self) -> List[Dict[str, Any]]:
        """Get users that require admin attention."""
        try:
            # Users with recent reports or moderation actions
            users_with_issues = db.session.query(User).join(Report).filter(
                Report.created_at >= datetime.utcnow() - timedelta(days=7),
                User.is_deleted == False
            ).distinct().limit(10).all()
            
            return [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_suspended': user.is_suspended,
                    'is_banned': user.is_banned,
                    'created_at': user.created_at.isoformat()
                }
                for user in users_with_issues
            ]
            
        except Exception:
            return []
    
    def _get_top_contributors(self) -> List[Dict[str, Any]]:
        """Get top contributing users by content creation."""
        try:
            # Get users with most facts and comments
            top_users = db.session.query(
                User,
                func.count(Fact.id).label('fact_count'),
                func.count(Comment.id).label('comment_count')
            ).outerjoin(Fact).outerjoin(Comment).filter(
                User.is_deleted == False
            ).group_by(User.id).order_by(
                desc('fact_count'), desc('comment_count')
            ).limit(10).all()
            
            return [
                {
                    'id': user.id,
                    'username': user.username,
                    'fact_count': fact_count or 0,
                    'comment_count': comment_count or 0,
                    'total_contributions': (fact_count or 0) + (comment_count or 0)
                }
                for user, fact_count, comment_count in top_users
            ]
            
        except Exception:
            return []
    
    def _get_most_reported_content(self) -> List[Dict[str, Any]]:
        """Get content with the most reports."""
        try:
            # Get facts and comments with report counts
            reported_facts = db.session.query(
                Fact, func.count(Report.id).label('report_count')
            ).join(Report, Report.content_id == Fact.id).filter(
                Report.content_type == 'fact',
                Fact.is_deleted == False
            ).group_by(Fact.id).order_by(desc('report_count')).limit(5).all()
            
            reported_comments = db.session.query(
                Comment, func.count(Report.id).label('report_count')
            ).join(Report, Report.content_id == Comment.id).filter(
                Report.content_type == 'comment',
                Comment.is_deleted == False
            ).group_by(Comment.id).order_by(desc('report_count')).limit(5).all()
            
            content_list = []
            
            for fact, count in reported_facts:
                content_list.append({
                    'type': 'fact',
                    'id': fact.id,
                    'title': fact.title[:100] + '...' if len(fact.title) > 100 else fact.title,
                    'author': fact.author.username if fact.author else 'Unknown',
                    'report_count': count,
                    'created_at': fact.created_at.isoformat()
                })
            
            for comment, count in reported_comments:
                content_list.append({
                    'type': 'comment',
                    'id': comment.id,
                    'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                    'author': comment.author.username if comment.author else 'Unknown',
                    'report_count': count,
                    'created_at': comment.created_at.isoformat()
                })
            
            # Sort by report count
            content_list.sort(key=lambda x: x['report_count'], reverse=True)
            return content_list[:10]
            
        except Exception:
            return []
    
    def _get_content_needing_moderation(self) -> List[Dict[str, Any]]:
        """Get content that needs immediate moderation attention."""
        try:
            # Get pending reports for facts and comments
            pending_reports = Report.query.filter_by(status='pending').order_by(
                desc(Report.created_at)
            ).limit(20).all()
            
            return [
                {
                    'report_id': report.id,
                    'content_type': report.content_type,
                    'content_id': report.content_id,
                    'reason': report.reason,
                    'category': report.category.name if report.category else 'Unknown',
                    'reporter': report.reporter.username if report.reporter else 'Anonymous',
                    'created_at': report.created_at.isoformat(),
                    'priority': report.priority
                }
                for report in pending_reports
            ]
            
        except Exception:
            return []
    
    def _log_admin_activity(self, admin_id: str, activity_type: str, action: str, 
                           description: str, target_type: str = None, target_id: str = None,
                           severity: str = 'low', details: Dict = None):
        """Log admin activity for audit purposes."""
        try:
            from app.models.admin import AdminActivity
            
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
