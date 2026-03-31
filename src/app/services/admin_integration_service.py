"""
Admin Integration Service for connecting admin dashboard with existing components.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import session, request
from app.models import db, User, Fact, Comment, Report, Notification
from app.models.admin import AdminActivity
from app.components.analytics.services import AnalyticsService, DashboardService
from app.components.moderation.services import ModerationDashboardService
from app.components.notification.services import NotificationService
from app.components.analytics.tracking import track_admin_action


class AdminIntegrationService:
    """Service for integrating admin dashboard with existing components."""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.dashboard_service = DashboardService()
        self.moderation_service = ModerationDashboardService()
        self.notification_service = NotificationService()
    
    def get_integrated_dashboard_data(self, admin_user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data integrating all components.
        
        Args:
            admin_user_id: ID of the admin user
            
        Returns:
            Dictionary containing integrated dashboard data
        """
        try:
            # Track admin dashboard access
            track_admin_action(admin_user_id, 'dashboard', 'view_integrated_dashboard')
            
            # Get analytics dashboard data
            analytics_data = self._get_analytics_integration_data(admin_user_id)
            
            # Get moderation dashboard data
            moderation_data = self._get_moderation_integration_data(admin_user_id)
            
            # Get notification system data
            notification_data = self._get_notification_integration_data(admin_user_id)
            
            # Get security audit data
            security_data = self._get_security_integration_data(admin_user_id)
            
            # Combine all data
            integrated_data = {
                'analytics': analytics_data,
                'moderation': moderation_data,
                'notifications': notification_data,
                'security': security_data,
                'integration_timestamp': datetime.utcnow().isoformat()
            }
            
            # Log successful integration
            self._log_admin_activity(
                admin_user_id,
                'integration',
                'dashboard_data_integrated',
                'Successfully integrated dashboard data from all components',
                severity='low'
            )
            
            return integrated_data
            
        except Exception as e:
            # Log integration error
            self._log_admin_activity(
                admin_user_id,
                'integration_error',
                'dashboard_integration_failed',
                f'Failed to integrate dashboard data: {str(e)}',
                severity='high'
            )
            
            # Return partial data with error information
            return {
                'analytics': {},
                'moderation': {},
                'notifications': {},
                'security': {},
                'error': str(e),
                'integration_timestamp': datetime.utcnow().isoformat()
            }
    
    def get_analytics_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get analytics data specifically for admin dashboard integration."""
        try:
            # Get admin-specific analytics dashboard
            admin_dashboard = self.dashboard_service.get_dashboard_data(
                'admin_overview', admin_user_id
            )
            
            # Get recent analytics events
            recent_events = self.analytics_service.get_events(
                limit=50,
                event_types=['admin_action', 'user_login', 'content_created', 'moderation_action']
            )
            
            # Get key metrics for admin overview
            now = datetime.utcnow()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            
            metrics = {
                'events_last_24h': self.analytics_service.get_event_counts(
                    start_date=last_24h,
                    end_date=now
                ),
                'events_last_7d': self.analytics_service.get_event_counts(
                    start_date=last_7d,
                    end_date=now
                ),
                'top_events': self._get_top_admin_events(admin_user_id),
                'user_activity_trends': self._get_user_activity_trends()
            }
            
            return {
                'dashboard': admin_dashboard,
                'recent_events': recent_events,
                'metrics': metrics,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def get_moderation_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get moderation data for admin dashboard integration."""
        try:
            # Get moderation overview
            moderation_overview = self.moderation_service.get_moderation_overview(admin_user_id)
            
            # Get pending reports with priority
            pending_reports = Report.query.filter_by(status='pending').order_by(
                Report.priority.desc(), Report.created_at.asc()
            ).limit(20).all()
            
            # Get recent moderation actions
            recent_actions = db.session.query(
                AdminActivity
            ).filter(
                AdminActivity.activity_type.in_(['moderation', 'user_moderation']),
                AdminActivity.created_at >= datetime.utcnow() - timedelta(days=7)
            ).order_by(AdminActivity.created_at.desc()).limit(10).all()
            
            # Calculate moderation metrics
            moderation_metrics = {
                'pending_reports': len(pending_reports),
                'high_priority_reports': len([r for r in pending_reports if r.priority == 'high']),
                'avg_resolution_time': self._calculate_avg_resolution_time(),
                'moderator_activity': self._get_moderator_activity_summary()
            }
            
            return {
                'overview': moderation_overview,
                'pending_reports': [
                    {
                        'id': report.id,
                        'content_type': report.content_type,
                        'reason': report.reason,
                        'priority': report.priority,
                        'created_at': report.created_at.isoformat(),
                        'reporter': report.reporter.username if report.reporter else 'Anonymous'
                    }
                    for report in pending_reports
                ],
                'recent_actions': [
                    {
                        'id': action.id,
                        'action': action.action,
                        'description': action.description,
                        'admin': action.admin.username if action.admin else 'System',
                        'created_at': action.created_at.isoformat(),
                        'severity': action.severity
                    }
                    for action in recent_actions
                ],
                'metrics': moderation_metrics,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def get_notification_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get notification system data for admin dashboard integration."""
        try:
            # Get system-wide notification statistics
            total_notifications = Notification.query.count()
            unread_notifications = Notification.query.filter_by(is_read=False).count()
            
            # Get recent system notifications
            recent_notifications = Notification.query.filter(
                Notification.notification_type.in_(['system', 'admin', 'security'])
            ).order_by(Notification.created_at.desc()).limit(10).all()
            
            # Get notification queue status
            from app.models.system import NotificationQueue
            queued_notifications = NotificationQueue.query.filter_by(
                status='pending'
            ).count()
            
            failed_notifications = NotificationQueue.query.filter_by(
                status='failed'
            ).count()
            
            # Get notification metrics
            notification_metrics = {
                'total_notifications': total_notifications,
                'unread_notifications': unread_notifications,
                'queued_notifications': queued_notifications,
                'failed_notifications': failed_notifications,
                'delivery_rate': self._calculate_notification_delivery_rate()
            }
            
            return {
                'recent_notifications': [
                    {
                        'id': notif.id,
                        'title': notif.title,
                        'message': notif.message[:100] + '...' if len(notif.message) > 100 else notif.message,
                        'type': notif.notification_type,
                        'created_at': notif.created_at.isoformat(),
                        'is_read': notif.is_read
                    }
                    for notif in recent_notifications
                ],
                'metrics': notification_metrics,
                'queue_status': {
                    'pending': queued_notifications,
                    'failed': failed_notifications
                },
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def get_security_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get security audit data for admin dashboard integration."""
        try:
            # Get recent security-related admin activities
            security_activities = AdminActivity.query.filter(
                AdminActivity.activity_type.in_([
                    'security', 'user_moderation', 'configuration_change', 'system_access'
                ]),
                AdminActivity.severity.in_(['medium', 'high', 'critical'])
            ).order_by(AdminActivity.created_at.desc()).limit(20).all()
            
            # Get failed login attempts (would need to be tracked in analytics)
            failed_logins = self.analytics_service.get_events(
                event_types=['login_failed'],
                start_date=datetime.utcnow() - timedelta(hours=24),
                limit=50
            )
            
            # Get suspicious activities
            suspicious_activities = self._get_suspicious_activities()
            
            # Calculate security metrics
            security_metrics = {
                'high_severity_activities': len([a for a in security_activities if a.severity == 'high']),
                'critical_activities': len([a for a in security_activities if a.severity == 'critical']),
                'failed_logins_24h': len(failed_logins),
                'suspicious_activities': len(suspicious_activities),
                'admin_sessions_active': self._get_active_admin_sessions_count()
            }
            
            return {
                'security_activities': [
                    {
                        'id': activity.id,
                        'action': activity.action,
                        'description': activity.description,
                        'admin': activity.admin.username if activity.admin else 'System',
                        'severity': activity.severity,
                        'created_at': activity.created_at.isoformat(),
                        'ip_address': activity.ip_address
                    }
                    for activity in security_activities
                ],
                'failed_logins': [
                    {
                        'timestamp': event.get('timestamp'),
                        'user_id': event.get('user_id'),
                        'ip_address': event.get('ip_address'),
                        'user_agent': event.get('user_agent')
                    }
                    for event in failed_logins
                ],
                'suspicious_activities': suspicious_activities,
                'metrics': security_metrics,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def send_admin_notification(self, admin_user_id: str, title: str, message: str, 
                               notification_type: str = 'admin', priority: str = 'normal') -> bool:
        """
        Send notification to admin users through the notification system.
        
        Args:
            admin_user_id: ID of admin sending the notification
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all admin users
            admin_users = User.query.filter_by(role='admin', is_active=True).all()
            
            success_count = 0
            for admin_user in admin_users:
                result = self.notification_service.create_notification(
                    user_id=admin_user.id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    sender_id=admin_user_id
                )
                
                if result['success']:
                    success_count += 1
            
            # Log notification broadcast
            self._log_admin_activity(
                admin_user_id,
                'notification',
                'admin_broadcast',
                f'Sent notification to {success_count} admin users: {title}',
                severity='low'
            )
            
            return success_count > 0
            
        except Exception as e:
            self._log_admin_activity(
                admin_user_id,
                'notification_error',
                'admin_broadcast_failed',
                f'Failed to send admin notification: {str(e)}',
                severity='medium'
            )
            return False
    
    def trigger_security_alert(self, admin_user_id: str, alert_type: str, 
                              description: str, severity: str = 'high') -> bool:
        """
        Trigger a security alert that integrates with all monitoring systems.
        
        Args:
            admin_user_id: ID of admin triggering the alert
            alert_type: Type of security alert
            description: Alert description
            severity: Alert severity level
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Log security alert
            self._log_admin_activity(
                admin_user_id,
                'security_alert',
                alert_type,
                description,
                severity=severity
            )
            
            # Track in analytics
            track_admin_action(admin_user_id, 'security', alert_type, {
                'description': description,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Send notification to all admins
            self.send_admin_notification(
                admin_user_id,
                f'Security Alert: {alert_type}',
                description,
                'security',
                'high' if severity in ['high', 'critical'] else 'normal'
            )
            
            return True
            
        except Exception as e:
            self._log_admin_activity(
                admin_user_id,
                'security_error',
                'alert_trigger_failed',
                f'Failed to trigger security alert: {str(e)}',
                severity='critical'
            )
            return False
    
    def _get_analytics_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get analytics data for integration."""
        return self.get_analytics_integration_data(admin_user_id)
    
    def _get_moderation_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get moderation data for integration."""
        return self.get_moderation_integration_data(admin_user_id)
    
    def _get_notification_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get notification data for integration."""
        return self.get_notification_integration_data(admin_user_id)
    
    def _get_security_integration_data(self, admin_user_id: str) -> Dict[str, Any]:
        """Get security data for integration."""
        return self.get_security_integration_data(admin_user_id)
    
    def _get_top_admin_events(self, admin_user_id: str) -> List[Dict[str, Any]]:
        """Get top admin events for analytics."""
        try:
            events = self.analytics_service.get_events(
                event_types=['admin_action'],
                limit=10,
                user_id=admin_user_id
            )
            
            return [
                {
                    'event_type': event.get('event_type'),
                    'action': event.get('metadata', {}).get('action'),
                    'timestamp': event.get('timestamp'),
                    'count': 1  # Would aggregate in real implementation
                }
                for event in events
            ]
            
        except Exception:
            return []
    
    def _get_user_activity_trends(self) -> Dict[str, Any]:
        """Get user activity trends for analytics integration."""
        try:
            # Get user activity over last 7 days
            last_7d = datetime.utcnow() - timedelta(days=7)
            
            daily_activity = {}
            for i in range(7):
                date = (datetime.utcnow() - timedelta(days=i)).date()
                daily_activity[date.isoformat()] = {
                    'logins': 0,  # Would get from analytics
                    'content_created': 0,  # Would get from analytics
                    'active_users': 0  # Would get from analytics
                }
            
            return daily_activity
            
        except Exception:
            return {}
    
    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average report resolution time."""
        try:
            resolved_reports = Report.query.filter(
                Report.status.in_(['resolved', 'dismissed']),
                Report.resolved_at.isnot(None)
            ).limit(100).all()
            
            if not resolved_reports:
                return 0.0
            
            total_time = sum(
                (report.resolved_at - report.created_at).total_seconds() / 3600
                for report in resolved_reports
            )
            
            return round(total_time / len(resolved_reports), 2)
            
        except Exception:
            return 0.0
    
    def _get_moderator_activity_summary(self) -> Dict[str, Any]:
        """Get moderator activity summary."""
        try:
            moderators = User.query.filter_by(role='moderator', is_active=True).all()
            
            activity_summary = {}
            for moderator in moderators:
                recent_actions = AdminActivity.query.filter(
                    AdminActivity.admin_id == moderator.id,
                    AdminActivity.activity_type.in_(['moderation', 'user_moderation']),
                    AdminActivity.created_at >= datetime.utcnow() - timedelta(days=7)
                ).count()
                
                activity_summary[moderator.username] = recent_actions
            
            return activity_summary
            
        except Exception:
            return {}
    
    def _calculate_notification_delivery_rate(self) -> float:
        """Calculate notification delivery success rate."""
        try:
            from app.models.system import NotificationQueue
            
            total_notifications = NotificationQueue.query.count()
            if total_notifications == 0:
                return 100.0
            
            successful_notifications = NotificationQueue.query.filter_by(
                status='sent'
            ).count()
            
            return round((successful_notifications / total_notifications) * 100, 2)
            
        except Exception:
            return 0.0
    
    def _get_suspicious_activities(self) -> List[Dict[str, Any]]:
        """Get suspicious activities for security monitoring."""
        try:
            # Look for patterns that might indicate suspicious behavior
            suspicious = []
            
            # Multiple failed logins from same IP
            failed_logins = self.analytics_service.get_events(
                event_types=['login_failed'],
                start_date=datetime.utcnow() - timedelta(hours=1),
                limit=100
            )
            
            # Group by IP address
            ip_failures = {}
            for event in failed_logins:
                ip = event.get('ip_address', 'unknown')
                ip_failures[ip] = ip_failures.get(ip, 0) + 1
            
            # Flag IPs with more than 5 failures
            for ip, count in ip_failures.items():
                if count > 5:
                    suspicious.append({
                        'type': 'multiple_failed_logins',
                        'description': f'Multiple failed logins from IP {ip}',
                        'count': count,
                        'severity': 'high'
                    })
            
            return suspicious
            
        except Exception:
            return []
    
    def _get_active_admin_sessions_count(self) -> int:
        """Get count of active admin sessions."""
        try:
            # This would require session tracking in the database
            # For now, return a placeholder
            return User.query.filter(
                User.role == 'admin',
                User.is_active == True,
                User.last_login >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
        except Exception:
            return 0
    
    def _log_admin_activity(self, admin_id: str, activity_type: str, action: str, 
                           description: str, target_type: str = None, target_id: str = None,
                           severity: str = 'low', details: Dict = None):
        """Log admin activity for audit purposes."""
        try:
            # Add request context information
            if not details:
                details = {}
            
            details.update({
                'ip_address': request.remote_addr if request else None,
                'user_agent': request.headers.get('User-Agent') if request else None,
                'session_id': session.get('session_id') if session else None
            })
            
            activity = AdminActivity(
                admin_id=admin_id,
                activity_type=activity_type,
                action=action,
                description=description,
                target_type=target_type,
                target_id=target_id,
                severity=severity,
                details=details,
                ip_address=details.get('ip_address'),
                user_agent=details.get('user_agent'),
                session_id=details.get('session_id')
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception:
            # Don't let logging errors break the main functionality
            db.session.rollback()
