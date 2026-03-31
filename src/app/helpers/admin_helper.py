"""
Admin Helper utilities for common administrative operations.
"""

import os
import json
import csv
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from io import StringIO, BytesIO
from flask import current_app
from app.models import db, User, Fact, Comment, Report, Notification
from app.models.admin import AdminActivity, SystemHealth
from app.components.analytics.tracking import track_admin_action


class AdminHelper:
    """Helper class for common administrative operations."""
    
    @staticmethod
    def bulk_user_operation(user_ids: List[str], operation: str, admin_user_id: str, 
                           **kwargs) -> Dict[str, Any]:
        """
        Perform bulk operations on multiple users.
        
        Args:
            user_ids: List of user IDs to operate on
            operation: Operation to perform (activate, deactivate, suspend, ban)
            admin_user_id: ID of admin performing the operation
            **kwargs: Additional operation parameters
            
        Returns:
            Dictionary with operation results
        """
        try:
            if not user_ids:
                return {'success': False, 'error': 'No users specified'}
            
            # Get users (exclude admins from bulk operations)
            users = User.query.filter(
                User.id.in_(user_ids),
                User.is_deleted == False,
                User.role != 'admin'
            ).all()
            
            if not users:
                return {'success': False, 'error': 'No valid users found'}
            
            success_count = 0
            errors = []
            
            for user in users:
                try:
                    if operation == 'activate':
                        user.is_active = True
                        user.is_suspended = False
                        user.suspension_end = None
                    elif operation == 'deactivate':
                        user.is_active = False
                    elif operation == 'suspend':
                        user.is_suspended = True
                        user.is_active = False
                        if 'duration_hours' in kwargs:
                            user.suspension_end = datetime.utcnow() + timedelta(
                                hours=kwargs['duration_hours']
                            )
                    elif operation == 'ban':
                        user.is_banned = True
                        user.is_active = False
                        user.ban_reason = kwargs.get('reason', 'Banned by administrator')
                    
                    success_count += 1
                    
                    # Log individual user operation
                    AdminHelper.log_admin_activity(
                        admin_user_id,
                        'user_management',
                        f'bulk_{operation}',
                        f'{operation.title()} user {user.username}',
                        target_type='user',
                        target_id=user.id
                    )
                    
                except Exception as e:
                    errors.append(f'Error {operation} user {user.username}: {str(e)}')
            
            if success_count > 0:
                db.session.commit()
                
                # Track bulk operation
                track_admin_action(admin_user_id, 'user_management', f'bulk_{operation}', {
                    'user_count': success_count,
                    'operation': operation,
                    'parameters': kwargs
                })
            
            return {
                'success': True,
                'affected_count': success_count,
                'errors': errors
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def generate_user_report(filters: Dict[str, Any] = None, 
                           format_type: str = 'csv') -> Union[str, bytes]:
        """
        Generate comprehensive user report.
        
        Args:
            filters: Optional filters to apply
            format_type: Output format (csv, json, excel)
            
        Returns:
            Report data in specified format
        """
        try:
            # Build query with filters
            query = User.query.filter_by(is_deleted=False)
            
            if filters:
                if filters.get('role'):
                    query = query.filter_by(role=filters['role'])
                if filters.get('is_active') is not None:
                    query = query.filter_by(is_active=filters['is_active'])
                if filters.get('created_after'):
                    query = query.filter(User.created_at >= filters['created_after'])
                if filters.get('created_before'):
                    query = query.filter(User.created_at <= filters['created_before'])
            
            users = query.order_by(User.created_at.desc()).all()
            
            # Prepare report data
            report_data = []
            for user in users:
                # Get user statistics
                fact_count = Fact.query.filter_by(author_id=user.id, is_deleted=False).count()
                comment_count = Comment.query.filter_by(author_id=user.id, is_deleted=False).count()
                reports_made = Report.query.filter_by(reporter_id=user.id).count()
                reports_received = Report.query.filter_by(reported_user_id=user.id).count()
                
                user_data = {
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
                    'fact_count': fact_count,
                    'comment_count': comment_count,
                    'reports_made': reports_made,
                    'reports_received': reports_received,
                    'suspension_end': user.suspension_end.isoformat() if user.suspension_end else None,
                    'ban_reason': user.ban_reason
                }
                report_data.append(user_data)
            
            # Format output
            if format_type == 'json':
                return json.dumps({
                    'report_type': 'user_report',
                    'generated_at': datetime.utcnow().isoformat(),
                    'total_users': len(report_data),
                    'filters_applied': filters or {},
                    'data': report_data
                }, indent=2)
            
            elif format_type == 'csv':
                output = StringIO()
                if report_data:
                    writer = csv.DictWriter(output, fieldnames=report_data[0].keys())
                    writer.writeheader()
                    writer.writerows(report_data)
                return output.getvalue()
            
            else:
                return json.dumps(report_data, indent=2)
                
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    @staticmethod
    def generate_system_report(admin_user_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive system status report.
        
        Args:
            admin_user_id: ID of admin requesting the report
            
        Returns:
            Dictionary containing system report data
        """
        try:
            # Track report generation
            track_admin_action(admin_user_id, 'reporting', 'generate_system_report')
            
            # System statistics
            system_stats = {
                'total_users': User.query.filter_by(is_deleted=False).count(),
                'active_users': User.query.filter_by(is_active=True, is_deleted=False).count(),
                'suspended_users': User.query.filter_by(is_suspended=True).count(),
                'banned_users': User.query.filter_by(is_banned=True).count(),
                'total_facts': Fact.query.filter_by(is_deleted=False).count(),
                'published_facts': Fact.query.filter_by(is_deleted=False, is_published=True).count(),
                'total_comments': Comment.query.filter_by(is_deleted=False).count(),
                'pending_reports': Report.query.filter_by(status='pending').count(),
                'resolved_reports': Report.query.filter_by(status='resolved').count()
            }
            
            # Recent activity (last 24 hours)
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_activity = {
                'new_users': User.query.filter(
                    User.created_at >= last_24h,
                    User.is_deleted == False
                ).count(),
                'new_facts': Fact.query.filter(
                    Fact.created_at >= last_24h,
                    Fact.is_deleted == False
                ).count(),
                'new_comments': Comment.query.filter(
                    Comment.created_at >= last_24h,
                    Comment.is_deleted == False
                ).count(),
                'new_reports': Report.query.filter(Report.created_at >= last_24h).count(),
                'admin_actions': AdminActivity.query.filter(
                    AdminActivity.created_at >= last_24h
                ).count()
            }
            
            # System health summary
            latest_health = SystemHealth.query.order_by(
                SystemHealth.last_check_at.desc()
            ).limit(10).all()
            
            health_summary = {
                'total_checks': len(latest_health),
                'healthy_checks': len([h for h in latest_health if h.status == 'healthy']),
                'warning_checks': len([h for h in latest_health if h.status == 'warning']),
                'critical_checks': len([h for h in latest_health if h.status == 'critical']),
                'last_check': latest_health[0].last_check_at.isoformat() if latest_health else None
            }
            
            # User role distribution
            role_distribution = {}
            roles = db.session.query(User.role, db.func.count(User.id)).filter_by(
                is_deleted=False
            ).group_by(User.role).all()
            
            for role, count in roles:
                role_distribution[role] = count
            
            return {
                'report_type': 'system_report',
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': admin_user_id,
                'system_statistics': system_stats,
                'recent_activity': recent_activity,
                'health_summary': health_summary,
                'role_distribution': role_distribution
            }
            
        except Exception as e:
            AdminHelper.log_admin_activity(
                admin_user_id,
                'reporting_error',
                'system_report_failed',
                f'Failed to generate system report: {str(e)}',
                severity='medium'
            )
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def cleanup_old_data(admin_user_id: str, days_old: int = 90) -> Dict[str, Any]:
        """
        Clean up old system data for maintenance.
        
        Args:
            admin_user_id: ID of admin performing cleanup
            days_old: Age threshold for cleanup (default 90 days)
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Track cleanup operation
            track_admin_action(admin_user_id, 'maintenance', 'data_cleanup', {
                'days_old': days_old,
                'cutoff_date': cutoff_date.isoformat()
            })
            
            cleanup_results = {}
            
            # Clean up old admin activities (keep high/critical severity)
            old_activities = AdminActivity.query.filter(
                AdminActivity.created_at < cutoff_date,
                AdminActivity.severity.in_(['low', 'medium'])
            ).all()
            
            for activity in old_activities:
                db.session.delete(activity)
            
            cleanup_results['admin_activities_cleaned'] = len(old_activities)
            
            # Clean up old system health records (keep latest for each check)
            old_health_records = db.session.query(SystemHealth).filter(
                SystemHealth.last_check_at < cutoff_date
            ).all()
            
            # Keep the most recent record for each check type
            keep_records = {}
            for record in old_health_records:
                key = record.check_name
                if key not in keep_records or record.last_check_at > keep_records[key].last_check_at:
                    if key in keep_records:
                        db.session.delete(keep_records[key])
                    keep_records[key] = record
                else:
                    db.session.delete(record)
            
            cleanup_results['health_records_cleaned'] = len(old_health_records) - len(keep_records)
            
            # Clean up old resolved reports
            old_reports = Report.query.filter(
                Report.resolved_at < cutoff_date,
                Report.status.in_(['resolved', 'dismissed'])
            ).all()
            
            for report in old_reports:
                db.session.delete(report)
            
            cleanup_results['old_reports_cleaned'] = len(old_reports)
            
            # Clean up old notifications (read notifications older than cutoff)
            old_notifications = Notification.query.filter(
                Notification.created_at < cutoff_date,
                Notification.is_read == True
            ).all()
            
            for notification in old_notifications:
                db.session.delete(notification)
            
            cleanup_results['old_notifications_cleaned'] = len(old_notifications)
            
            db.session.commit()
            
            # Log successful cleanup
            AdminHelper.log_admin_activity(
                admin_user_id,
                'maintenance',
                'data_cleanup_completed',
                f'Cleaned up old data: {cleanup_results}',
                severity='low'
            )
            
            return {
                'success': True,
                'cleanup_results': cleanup_results,
                'cutoff_date': cutoff_date.isoformat(),
                'total_records_cleaned': sum(cleanup_results.values())
            }
            
        except Exception as e:
            db.session.rollback()
            AdminHelper.log_admin_activity(
                admin_user_id,
                'maintenance_error',
                'data_cleanup_failed',
                f'Data cleanup failed: {str(e)}',
                severity='high'
            )
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_system_integrity(admin_user_id: str) -> Dict[str, Any]:
        """
        Validate system data integrity and consistency.
        
        Args:
            admin_user_id: ID of admin performing validation
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Track validation operation
            track_admin_action(admin_user_id, 'maintenance', 'system_validation')
            
            validation_results = {
                'issues_found': [],
                'warnings': [],
                'statistics': {}
            }
            
            # Check for orphaned records
            orphaned_facts = Fact.query.filter(
                ~Fact.author_id.in_(db.session.query(User.id))
            ).count()
            
            if orphaned_facts > 0:
                validation_results['issues_found'].append(
                    f'Found {orphaned_facts} facts with missing authors'
                )
            
            orphaned_comments = Comment.query.filter(
                ~Comment.author_id.in_(db.session.query(User.id))
            ).count()
            
            if orphaned_comments > 0:
                validation_results['issues_found'].append(
                    f'Found {orphaned_comments} comments with missing authors'
                )
            
            # Check for inconsistent user states
            inconsistent_users = User.query.filter(
                User.is_banned == True,
                User.is_active == True
            ).count()
            
            if inconsistent_users > 0:
                validation_results['issues_found'].append(
                    f'Found {inconsistent_users} users who are both banned and active'
                )
            
            # Check for expired suspensions
            expired_suspensions = User.query.filter(
                User.is_suspended == True,
                User.suspension_end < datetime.utcnow()
            ).count()
            
            if expired_suspensions > 0:
                validation_results['warnings'].append(
                    f'Found {expired_suspensions} users with expired suspensions'
                )
            
            # Check for old pending reports
            old_pending_reports = Report.query.filter(
                Report.status == 'pending',
                Report.created_at < datetime.utcnow() - timedelta(days=30)
            ).count()
            
            if old_pending_reports > 0:
                validation_results['warnings'].append(
                    f'Found {old_pending_reports} reports pending for over 30 days'
                )
            
            # Collect statistics
            validation_results['statistics'] = {
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(is_active=True).count(),
                'total_facts': Fact.query.count(),
                'total_comments': Comment.query.count(),
                'pending_reports': Report.query.filter_by(status='pending').count(),
                'orphaned_facts': orphaned_facts,
                'orphaned_comments': orphaned_comments,
                'inconsistent_users': inconsistent_users,
                'expired_suspensions': expired_suspensions,
                'old_pending_reports': old_pending_reports
            }
            
            # Log validation results
            severity = 'high' if validation_results['issues_found'] else 'low'
            AdminHelper.log_admin_activity(
                admin_user_id,
                'maintenance',
                'system_validation_completed',
                f'System validation completed. Issues: {len(validation_results["issues_found"])}, Warnings: {len(validation_results["warnings"])}',
                severity=severity
            )
            
            return {
                'success': True,
                'validation_results': validation_results,
                'validated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            AdminHelper.log_admin_activity(
                admin_user_id,
                'maintenance_error',
                'system_validation_failed',
                f'System validation failed: {str(e)}',
                severity='high'
            )
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def log_admin_activity(admin_id: str, activity_type: str, action: str, 
                          description: str, target_type: str = None, target_id: str = None,
                          severity: str = 'low', details: Dict = None):
        """
        Log admin activity for audit purposes.
        
        Args:
            admin_id: ID of admin performing the action
            activity_type: Type of activity
            action: Specific action taken
            description: Description of the action
            target_type: Type of target (optional)
            target_id: ID of target (optional)
            severity: Severity level
            details: Additional details (optional)
        """
        try:
            activity = AdminActivity(
                admin_id=admin_id,
                activity_type=activity_type,
                action=action,
                description=description,
                target_type=target_type,
                target_id=target_id,
                severity=severity,
                details=details or {}
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception:
            # Don't let logging errors break the main functionality
            db.session.rollback()
    
    @staticmethod
    def get_system_statistics() -> Dict[str, Any]:
        """
        Get comprehensive system statistics.
        
        Returns:
            Dictionary containing system statistics
        """
        try:
            stats = {
                'users': {
                    'total': User.query.filter_by(is_deleted=False).count(),
                    'active': User.query.filter_by(is_active=True, is_deleted=False).count(),
                    'suspended': User.query.filter_by(is_suspended=True).count(),
                    'banned': User.query.filter_by(is_banned=True).count(),
                    'admins': User.query.filter_by(role='admin', is_deleted=False).count(),
                    'moderators': User.query.filter_by(role='moderator', is_deleted=False).count()
                },
                'content': {
                    'total_facts': Fact.query.filter_by(is_deleted=False).count(),
                    'published_facts': Fact.query.filter_by(is_deleted=False, is_published=True).count(),
                    'draft_facts': Fact.query.filter_by(is_deleted=False, is_published=False).count(),
                    'total_comments': Comment.query.filter_by(is_deleted=False).count()
                },
                'moderation': {
                    'pending_reports': Report.query.filter_by(status='pending').count(),
                    'resolved_reports': Report.query.filter_by(status='resolved').count(),
                    'dismissed_reports': Report.query.filter_by(status='dismissed').count(),
                    'total_reports': Report.query.count()
                },
                'system': {
                    'total_admin_activities': AdminActivity.query.count(),
                    'recent_admin_activities': AdminActivity.query.filter(
                        AdminActivity.created_at >= datetime.utcnow() - timedelta(hours=24)
                    ).count(),
                    'health_checks': SystemHealth.query.count(),
                    'notifications': Notification.query.count(),
                    'unread_notifications': Notification.query.filter_by(is_read=False).count()
                }
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def calculate_uptime() -> Dict[str, Any]:
        """
        Calculate system uptime based on oldest admin activity.
        
        Returns:
            Dictionary with uptime information
        """
        try:
            # Get the oldest admin activity as a proxy for system start
            oldest_activity = AdminActivity.query.order_by(AdminActivity.created_at.asc()).first()
            
            if not oldest_activity:
                return {'error': 'No admin activities found'}
            
            uptime_delta = datetime.utcnow() - oldest_activity.created_at
            
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return {
                'total_seconds': uptime_delta.total_seconds(),
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'formatted': f"{days}d {hours}h {minutes}m",
                'since': oldest_activity.created_at.isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
