"""
System Maintenance Helper utilities for cleanup and optimization.
"""

import os
import shutil
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import text, func
from flask import current_app
from app.models import db, User, Fact, Comment, Report, Notification
from app.models.admin import AdminActivity, SystemHealth, SystemMaintenanceWindow
from app.components.analytics.tracking import track_admin_action


class SystemMaintenanceHelper:
    """Helper class for system maintenance operations."""
    
    @staticmethod
    def schedule_maintenance_window(admin_user_id: str, title: str, description: str,
                                  scheduled_start: datetime, scheduled_end: datetime,
                                  maintenance_type: str = 'scheduled',
                                  impact_level: str = 'medium') -> Dict[str, Any]:
        """
        Schedule a system maintenance window.
        
        Args:
            admin_user_id: ID of admin scheduling maintenance
            title: Maintenance window title
            description: Description of maintenance activities
            scheduled_start: Start time for maintenance
            scheduled_end: End time for maintenance
            maintenance_type: Type of maintenance (scheduled, emergency, routine)
            impact_level: Impact level (low, medium, high, critical)
            
        Returns:
            Dictionary with operation results
        """
        try:
            # Validate maintenance window
            if scheduled_start >= scheduled_end:
                return {'success': False, 'error': 'Start time must be before end time'}
            
            if scheduled_start < datetime.utcnow():
                return {'success': False, 'error': 'Cannot schedule maintenance in the past'}
            
            # Check for overlapping maintenance windows
            overlapping = SystemMaintenanceWindow.query.filter(
                SystemMaintenanceWindow.status.in_(['scheduled', 'in_progress']),
                SystemMaintenanceWindow.scheduled_start < scheduled_end,
                SystemMaintenanceWindow.scheduled_end > scheduled_start
            ).first()
            
            if overlapping:
                return {
                    'success': False, 
                    'error': f'Overlaps with existing maintenance window: {overlapping.title}'
                }
            
            # Create maintenance window
            maintenance_window = SystemMaintenanceWindow(
                title=title,
                description=description,
                maintenance_type=maintenance_type,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                impact_level=impact_level,
                created_by=admin_user_id
            )
            
            db.session.add(maintenance_window)
            db.session.commit()
            
            # Track maintenance scheduling
            track_admin_action(admin_user_id, 'maintenance', 'schedule_maintenance_window', {
                'title': title,
                'maintenance_type': maintenance_type,
                'impact_level': impact_level,
                'duration_minutes': maintenance_window.duration_minutes
            })
            
            # Log admin activity
            SystemMaintenanceHelper._log_admin_activity(
                admin_user_id,
                'maintenance',
                'schedule_maintenance',
                f'Scheduled maintenance window: {title}',
                target_type='maintenance_window',
                target_id=maintenance_window.id,
                severity='medium'
            )
            
            return {
                'success': True,
                'maintenance_id': maintenance_window.id,
                'message': 'Maintenance window scheduled successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def perform_database_optimization(admin_user_id: str) -> Dict[str, Any]:
        """
        Perform database optimization tasks.
        
        Args:
            admin_user_id: ID of admin performing optimization
            
        Returns:
            Dictionary with optimization results
        """
        try:
            # Track optimization operation
            track_admin_action(admin_user_id, 'maintenance', 'database_optimization')
            
            optimization_results = {}
            
            # Analyze table sizes before optimization
            table_stats_before = SystemMaintenanceHelper._get_table_statistics()
            optimization_results['table_stats_before'] = table_stats_before
            
            # Clean up soft-deleted records older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Hard delete old soft-deleted users
            old_deleted_users = User.query.filter(
                User.is_deleted == True,
                User.deleted_at < cutoff_date
            ).all()
            
            for user in old_deleted_users:
                db.session.delete(user)
            
            optimization_results['deleted_users_cleaned'] = len(old_deleted_users)
            
            # Hard delete old soft-deleted facts
            old_deleted_facts = Fact.query.filter(
                Fact.is_deleted == True,
                Fact.deleted_at < cutoff_date
            ).all()
            
            for fact in old_deleted_facts:
                db.session.delete(fact)
            
            optimization_results['deleted_facts_cleaned'] = len(old_deleted_facts)
            
            # Hard delete old soft-deleted comments
            old_deleted_comments = Comment.query.filter(
                Comment.is_deleted == True,
                Comment.deleted_at < cutoff_date
            ).all()
            
            for comment in old_deleted_comments:
                db.session.delete(comment)
            
            optimization_results['deleted_comments_cleaned'] = len(old_deleted_comments)
            
            # Clean up old resolved reports (keep for 90 days)
            old_resolved_reports = Report.query.filter(
                Report.status.in_(['resolved', 'dismissed']),
                Report.resolved_at < datetime.utcnow() - timedelta(days=90)
            ).all()
            
            for report in old_resolved_reports:
                db.session.delete(report)
            
            optimization_results['old_reports_cleaned'] = len(old_resolved_reports)
            
            # Clean up old read notifications (keep for 30 days)
            old_notifications = Notification.query.filter(
                Notification.is_read == True,
                Notification.created_at < cutoff_date
            ).all()
            
            for notification in old_notifications:
                db.session.delete(notification)
            
            optimization_results['old_notifications_cleaned'] = len(old_notifications)
            
            # Commit all deletions
            db.session.commit()
            
            # Get table statistics after optimization
            table_stats_after = SystemMaintenanceHelper._get_table_statistics()
            optimization_results['table_stats_after'] = table_stats_after
            
            # Calculate space saved (approximate)
            space_saved = 0
            for table, stats_before in table_stats_before.items():
                stats_after = table_stats_after.get(table, {'count': 0})
                records_removed = stats_before['count'] - stats_after['count']
                space_saved += records_removed
            
            optimization_results['total_records_removed'] = space_saved
            
            # Log successful optimization
            SystemMaintenanceHelper._log_admin_activity(
                admin_user_id,
                'maintenance',
                'database_optimization_completed',
                f'Database optimization completed. Removed {space_saved} old records.',
                severity='low'
            )
            
            return {
                'success': True,
                'optimization_results': optimization_results,
                'optimized_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            SystemMaintenanceHelper._log_admin_activity(
                admin_user_id,
                'maintenance_error',
                'database_optimization_failed',
                f'Database optimization failed: {str(e)}',
                severity='high'
            )
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def cleanup_temporary_files(admin_user_id: str) -> Dict[str, Any]:
        """
        Clean up temporary files and directories.
        
        Args:
            admin_user_id: ID of admin performing cleanup
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            # Track cleanup operation
            track_admin_action(admin_user_id, 'maintenance', 'cleanup_temporary_files')
            
            cleanup_results = {
                'files_removed': 0,
                'directories_removed': 0,
                'space_freed_bytes': 0,
                'errors': []
            }
            
            # Define temporary directories to clean
            temp_dirs = [
                tempfile.gettempdir(),
                '/tmp' if os.path.exists('/tmp') else None,
                os.path.join(current_app.instance_path, 'temp') if current_app else None
            ]
            
            # Remove None values
            temp_dirs = [d for d in temp_dirs if d and os.path.exists(d)]
            
            for temp_dir in temp_dirs:
                try:
                    # Look for old temporary files (older than 24 hours)
                    cutoff_time = datetime.utcnow() - timedelta(hours=24)
                    
                    for root, dirs, files in os.walk(temp_dir):
                        # Skip if not our temporary files
                        if 'fact_checker' not in root.lower() and 'admin' not in root.lower():
                            continue
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                # Check file age
                                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                                if file_mtime < cutoff_time:
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    cleanup_results['files_removed'] += 1
                                    cleanup_results['space_freed_bytes'] += file_size
                            except (OSError, IOError) as e:
                                cleanup_results['errors'].append(f'Error removing file {file_path}: {str(e)}')
                        
                        # Remove empty directories
                        for dir_name in dirs:
                            dir_path = os.path.join(root, dir_name)
                            try:
                                if not os.listdir(dir_path):  # Directory is empty
                                    os.rmdir(dir_path)
                                    cleanup_results['directories_removed'] += 1
                            except (OSError, IOError) as e:
                                cleanup_results['errors'].append(f'Error removing directory {dir_path}: {str(e)}')
                
                except Exception as e:
                    cleanup_results['errors'].append(f'Error processing directory {temp_dir}: {str(e)}')
            
            # Log cleanup results
            SystemMaintenanceHelper._log_admin_activity(
                admin_user_id,
                'maintenance',
                'temp_files_cleanup_completed',
                f'Temporary files cleanup completed. Removed {cleanup_results["files_removed"]} files, freed {cleanup_results["space_freed_bytes"]} bytes.',
                severity='low'
            )
            
            return {
                'success': True,
                'cleanup_results': cleanup_results,
                'cleaned_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            SystemMaintenanceHelper._log_admin_activity(
                admin_user_id,
                'maintenance_error',
                'temp_files_cleanup_failed',
                f'Temporary files cleanup failed: {str(e)}',
                severity='medium'
            )
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def optimize_system_performance(admin_user_id: str) -> Dict[str, Any]:
        """
        Perform system performance optimization tasks.
        
        Args:
            admin_user_id: ID of admin performing optimization
            
        Returns:
            Dictionary with optimization results
        """
        try:
            # Track performance optimization
            track_admin_action(admin_user_id, 'maintenance', 'system_performance_optimization')
            
            optimization_results = {}
            
            # Database optimization
            db_optimization = SystemMaintenanceHelper.perform_database_optimization(admin_user_id)
            optimization_results['database_optimization'] = db_optimization
            
            # Temporary files cleanup
            temp_cleanup = SystemMaintenanceHelper.cleanup_temporary_files(admin_user_id)
            optimization_results['temp_files_cleanup'] = temp_cleanup
            
            # Update system statistics
            system_stats = SystemMaintenanceHelper._get_system_performance_stats()
            optimization_results['system_stats'] = system_stats
            
            # Log performance optimization
            SystemMaintenanceHelper._log_admin_activity(
                admin_user_id,
                'maintenance',
                'performance_optimization_completed',
                'System performance optimization completed successfully.',
                severity='low'
            )
            
            return {
                'success': True,
                'optimization_results': optimization_results,
                'optimized_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            SystemMaintenanceHelper._log_admin_activity(
                admin_user_id,
                'maintenance_error',
                'performance_optimization_failed',
                f'System performance optimization failed: {str(e)}',
                severity='high'
            )
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_maintenance_schedule(days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Get scheduled maintenance windows.
        
        Args:
            days_ahead: Number of days ahead to look for maintenance
            
        Returns:
            List of scheduled maintenance windows
        """
        try:
            end_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            maintenance_windows = SystemMaintenanceWindow.query.filter(
                SystemMaintenanceWindow.scheduled_start <= end_date,
                SystemMaintenanceWindow.status.in_(['scheduled', 'in_progress'])
            ).order_by(SystemMaintenanceWindow.scheduled_start).all()
            
            return [
                {
                    'id': window.id,
                    'title': window.title,
                    'description': window.description,
                    'maintenance_type': window.maintenance_type,
                    'impact_level': window.impact_level,
                    'scheduled_start': window.scheduled_start.isoformat(),
                    'scheduled_end': window.scheduled_end.isoformat(),
                    'duration_minutes': window.duration_minutes,
                    'status': window.status,
                    'created_by': window.creator.username if window.creator else 'Unknown'
                }
                for window in maintenance_windows
            ]
            
        except Exception as e:
            return []
    
    @staticmethod
    def _get_table_statistics() -> Dict[str, Dict[str, int]]:
        """Get database table statistics."""
        try:
            stats = {}
            
            # Get counts for main tables
            tables = {
                'users': User,
                'facts': Fact,
                'comments': Comment,
                'reports': Report,
                'notifications': Notification,
                'admin_activities': AdminActivity,
                'system_health': SystemHealth
            }
            
            for table_name, model in tables.items():
                try:
                    total_count = model.query.count()
                    
                    # Get deleted count if applicable
                    deleted_count = 0
                    if hasattr(model, 'is_deleted'):
                        deleted_count = model.query.filter_by(is_deleted=True).count()
                    
                    stats[table_name] = {
                        'count': total_count,
                        'deleted_count': deleted_count,
                        'active_count': total_count - deleted_count
                    }
                except Exception:
                    stats[table_name] = {'count': 0, 'deleted_count': 0, 'active_count': 0}
            
            return stats
            
        except Exception:
            return {}
    
    @staticmethod
    def _get_system_performance_stats() -> Dict[str, Any]:
        """Get system performance statistics."""
        try:
            # Database statistics
            db_stats = SystemMaintenanceHelper._get_table_statistics()
            
            # Calculate total records
            total_records = sum(stats['count'] for stats in db_stats.values())
            total_deleted = sum(stats['deleted_count'] for stats in db_stats.values())
            
            # Recent activity statistics
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_activities = AdminActivity.query.filter(
                AdminActivity.created_at >= last_24h
            ).count()
            
            # System health statistics
            latest_health = SystemHealth.query.order_by(
                SystemHealth.last_check_at.desc()
            ).limit(10).all()
            
            healthy_checks = len([h for h in latest_health if h.status == 'healthy'])
            total_checks = len(latest_health)
            
            return {
                'database': {
                    'total_records': total_records,
                    'deleted_records': total_deleted,
                    'active_records': total_records - total_deleted,
                    'table_stats': db_stats
                },
                'activity': {
                    'recent_admin_activities': recent_activities
                },
                'health': {
                    'healthy_checks': healthy_checks,
                    'total_checks': total_checks,
                    'health_percentage': (healthy_checks / total_checks * 100) if total_checks > 0 else 0
                }
            }
            
        except Exception:
            return {}
    
    @staticmethod
    def _log_admin_activity(admin_id: str, activity_type: str, action: str, 
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
                details=details or {}
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception:
            # Don't let logging errors break the main functionality
            db.session.rollback()
