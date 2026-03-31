"""
System Health Service for monitoring application performance and status.
"""

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import func, text
from app.models import db, User, Fact, Comment, Report
from app.models.admin import SystemHealth, AdminActivity


class SystemHealthService:
    """Service for monitoring and managing system health."""
    
    def __init__(self):
        self.health_checks = {
            'database': self._check_database_health,
            'memory': self._check_memory_usage,
            'disk': self._check_disk_usage,
            'cpu': self._check_cpu_usage,
            'application': self._check_application_health,
            'user_activity': self._check_user_activity_health,
            'content_health': self._check_content_health,
            'moderation_queue': self._check_moderation_queue_health
        }
    
    def run_all_health_checks(self, admin_user_id: str = None) -> Dict[str, Any]:
        """
        Run all health checks and return comprehensive status.
        
        Args:
            admin_user_id: Optional admin user ID for logging
            
        Returns:
            Dictionary containing all health check results
        """
        try:
            results = {}
            overall_status = 'healthy'
            critical_issues = []
            warnings = []
            
            for check_name, check_function in self.health_checks.items():
                try:
                    start_time = time.time()
                    result = check_function()
                    response_time = int((time.time() - start_time) * 1000)  # milliseconds
                    
                    result['response_time_ms'] = response_time
                    result['check_name'] = check_name
                    result['timestamp'] = datetime.utcnow().isoformat()
                    
                    # Store result in database
                    self._store_health_check_result(check_name, result)
                    
                    results[check_name] = result
                    
                    # Update overall status
                    if result['status'] == 'critical':
                        overall_status = 'critical'
                        critical_issues.append(f"{check_name}: {result['message']}")
                    elif result['status'] == 'warning' and overall_status != 'critical':
                        overall_status = 'warning'
                        warnings.append(f"{check_name}: {result['message']}")
                        
                except Exception as e:
                    # If a health check fails, mark it as critical
                    error_result = {
                        'status': 'critical',
                        'message': f'Health check failed: {str(e)}',
                        'response_time_ms': 0,
                        'check_name': check_name,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    results[check_name] = error_result
                    overall_status = 'critical'
                    critical_issues.append(f"{check_name}: Health check failed")
            
            # Log health check run
            if admin_user_id:
                self._log_admin_activity(
                    admin_user_id,
                    'system_health',
                    'run_health_checks',
                    f'Ran all health checks - Status: {overall_status}',
                    severity='low' if overall_status == 'healthy' else 'medium'
                )
            
            return {
                'overall_status': overall_status,
                'critical_issues': critical_issues,
                'warnings': warnings,
                'checks': results,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if admin_user_id:
                self._log_admin_activity(
                    admin_user_id,
                    'system_health_error',
                    'health_check_error',
                    f'Error running health checks: {str(e)}',
                    severity='high'
                )
            
            return {
                'overall_status': 'critical',
                'critical_issues': [f'Health check system error: {str(e)}'],
                'warnings': [],
                'checks': {},
                'last_updated': datetime.utcnow().isoformat()
            }
    
    def get_health_history(self, check_name: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get health check history for analysis.
        
        Args:
            check_name: Optional specific check name to filter
            hours: Number of hours of history to retrieve
            
        Returns:
            List of health check results
        """
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = SystemHealth.query.filter(
                SystemHealth.last_check_at >= start_time
            )
            
            if check_name:
                query = query.filter_by(check_name=check_name)
            
            health_records = query.order_by(SystemHealth.last_check_at.desc()).all()
            
            return [
                {
                    'check_name': record.check_name,
                    'category': record.category,
                    'status': record.status,
                    'message': record.message,
                    'response_time_ms': record.response_time_ms,
                    'cpu_usage': record.cpu_usage,
                    'memory_usage': record.memory_usage,
                    'disk_usage': record.disk_usage,
                    'last_check_at': record.last_check_at.isoformat(),
                    'details': record.details
                }
                for record in health_records
            ]
            
        except Exception:
            return []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics and performance data.
        
        Returns:
            Dictionary containing system metrics
        """
        try:
            system_resources = {}
            
            if PSUTIL_AVAILABLE:
                # System resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_resources = {
                    'cpu_usage_percent': cpu_percent,
                    'memory_usage_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'memory_total_gb': round(memory.total / (1024**3), 2),
                    'disk_usage_percent': disk.percent,
                    'disk_free_gb': round(disk.free / (1024**3), 2),
                    'disk_total_gb': round(disk.total / (1024**3), 2)
                }
            else:
                system_resources = {
                    'error': 'System resource monitoring unavailable (psutil not installed)',
                    'cpu_usage_percent': None,
                    'memory_usage_percent': None,
                    'disk_usage_percent': None
                }
            
            # Database metrics
            db_metrics = self._get_database_metrics()
            
            # Application metrics
            app_metrics = self._get_application_metrics()
            
            return {
                'system_resources': system_resources,
                'database_metrics': db_metrics,
                'application_metrics': app_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Error getting system metrics: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            db.session.execute(text('SELECT 1'))
            
            # Test table access
            user_count = User.query.count()
            
            response_time = (time.time() - start_time) * 1000
            
            if response_time > 5000:  # 5 seconds
                return {
                    'status': 'critical',
                    'message': f'Database response time too slow: {response_time:.0f}ms',
                    'details': {'response_time_ms': response_time, 'user_count': user_count}
                }
            elif response_time > 1000:  # 1 second
                return {
                    'status': 'warning',
                    'message': f'Database response time elevated: {response_time:.0f}ms',
                    'details': {'response_time_ms': response_time, 'user_count': user_count}
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Database responsive: {response_time:.0f}ms',
                    'details': {'response_time_ms': response_time, 'user_count': user_count}
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Database connection failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check system memory usage."""
        try:
            if not PSUTIL_AVAILABLE:
                return {
                    'status': 'unknown',
                    'message': 'Memory monitoring unavailable (psutil not installed)',
                    'details': {'error': 'psutil not available'}
                }
            
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 90:
                return {
                    'status': 'critical',
                    'message': f'Memory usage critical: {usage_percent:.1f}%',
                    'details': {
                        'usage_percent': usage_percent,
                        'available_gb': round(memory.available / (1024**3), 2),
                        'total_gb': round(memory.total / (1024**3), 2)
                    }
                }
            elif usage_percent > 80:
                return {
                    'status': 'warning',
                    'message': f'Memory usage high: {usage_percent:.1f}%',
                    'details': {
                        'usage_percent': usage_percent,
                        'available_gb': round(memory.available / (1024**3), 2),
                        'total_gb': round(memory.total / (1024**3), 2)
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Memory usage normal: {usage_percent:.1f}%',
                    'details': {
                        'usage_percent': usage_percent,
                        'available_gb': round(memory.available / (1024**3), 2),
                        'total_gb': round(memory.total / (1024**3), 2)
                    }
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Memory check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_disk_usage(self) -> Dict[str, Any]:
        """Check disk space usage."""
        try:
            if not PSUTIL_AVAILABLE:
                return {
                    'status': 'unknown',
                    'message': 'Disk monitoring unavailable (psutil not installed)',
                    'details': {'error': 'psutil not available'}
                }
            
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            
            if usage_percent > 95:
                return {
                    'status': 'critical',
                    'message': f'Disk usage critical: {usage_percent:.1f}%',
                    'details': {
                        'usage_percent': usage_percent,
                        'free_gb': round(disk.free / (1024**3), 2),
                        'total_gb': round(disk.total / (1024**3), 2)
                    }
                }
            elif usage_percent > 85:
                return {
                    'status': 'warning',
                    'message': f'Disk usage high: {usage_percent:.1f}%',
                    'details': {
                        'usage_percent': usage_percent,
                        'free_gb': round(disk.free / (1024**3), 2),
                        'total_gb': round(disk.total / (1024**3), 2)
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Disk usage normal: {usage_percent:.1f}%',
                    'details': {
                        'usage_percent': usage_percent,
                        'free_gb': round(disk.free / (1024**3), 2),
                        'total_gb': round(disk.total / (1024**3), 2)
                    }
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Disk check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage."""
        try:
            if not PSUTIL_AVAILABLE:
                return {
                    'status': 'unknown',
                    'message': 'CPU monitoring unavailable (psutil not installed)',
                    'details': {'error': 'psutil not available'}
                }
            
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 90:
                return {
                    'status': 'critical',
                    'message': f'CPU usage critical: {cpu_percent:.1f}%',
                    'details': {'cpu_percent': cpu_percent}
                }
            elif cpu_percent > 80:
                return {
                    'status': 'warning',
                    'message': f'CPU usage high: {cpu_percent:.1f}%',
                    'details': {'cpu_percent': cpu_percent}
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'CPU usage normal: {cpu_percent:.1f}%',
                    'details': {'cpu_percent': cpu_percent}
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'CPU check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_application_health(self) -> Dict[str, Any]:
        """Check application-specific health metrics."""
        try:
            # Check recent errors or issues
            recent_time = datetime.utcnow() - timedelta(hours=1)
            
            # Check for recent user activity (sign of healthy app)
            recent_users = User.query.filter(
                User.last_login >= recent_time
            ).count()
            
            # Check for recent content creation
            recent_facts = Fact.query.filter(
                Fact.created_at >= recent_time,
                Fact.is_deleted == False
            ).count()
            
            recent_comments = Comment.query.filter(
                Comment.created_at >= recent_time,
                Comment.is_deleted == False
            ).count()
            
            total_activity = recent_users + recent_facts + recent_comments
            
            if total_activity == 0:
                return {
                    'status': 'warning',
                    'message': 'No recent user activity detected',
                    'details': {
                        'recent_users': recent_users,
                        'recent_facts': recent_facts,
                        'recent_comments': recent_comments
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Application active: {total_activity} recent activities',
                    'details': {
                        'recent_users': recent_users,
                        'recent_facts': recent_facts,
                        'recent_comments': recent_comments,
                        'total_activity': total_activity
                    }
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Application health check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_user_activity_health(self) -> Dict[str, Any]:
        """Check user activity patterns for anomalies."""
        try:
            # Check for unusual user registration patterns
            last_hour = datetime.utcnow() - timedelta(hours=1)
            last_day = datetime.utcnow() - timedelta(days=1)
            
            registrations_last_hour = User.query.filter(
                User.created_at >= last_hour,
                User.is_deleted == False
            ).count()
            
            registrations_last_day = User.query.filter(
                User.created_at >= last_day,
                User.is_deleted == False
            ).count()
            
            # Check for spam-like activity (too many registrations)
            if registrations_last_hour > 50:  # Configurable threshold
                return {
                    'status': 'warning',
                    'message': f'Unusual registration activity: {registrations_last_hour} in last hour',
                    'details': {
                        'registrations_last_hour': registrations_last_hour,
                        'registrations_last_day': registrations_last_day
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Normal user activity: {registrations_last_day} registrations today',
                    'details': {
                        'registrations_last_hour': registrations_last_hour,
                        'registrations_last_day': registrations_last_day
                    }
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'User activity check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_content_health(self) -> Dict[str, Any]:
        """Check content creation and moderation health."""
        try:
            last_day = datetime.utcnow() - timedelta(days=1)
            
            # Check content creation rates
            facts_today = Fact.query.filter(
                Fact.created_at >= last_day,
                Fact.is_deleted == False
            ).count()
            
            comments_today = Comment.query.filter(
                Comment.created_at >= last_day,
                Comment.is_deleted == False
            ).count()
            
            # Check for content quality issues (high deletion rate)
            deleted_facts_today = Fact.query.filter(
                Fact.updated_at >= last_day,
                Fact.is_deleted == True
            ).count()
            
            total_facts_today = facts_today + deleted_facts_today
            deletion_rate = (deleted_facts_today / total_facts_today * 100) if total_facts_today > 0 else 0
            
            if deletion_rate > 50:  # High deletion rate
                return {
                    'status': 'warning',
                    'message': f'High content deletion rate: {deletion_rate:.1f}%',
                    'details': {
                        'facts_created': facts_today,
                        'comments_created': comments_today,
                        'deletion_rate': deletion_rate
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Content creation healthy: {facts_today} facts, {comments_today} comments',
                    'details': {
                        'facts_created': facts_today,
                        'comments_created': comments_today,
                        'deletion_rate': deletion_rate
                    }
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Content health check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _check_moderation_queue_health(self) -> Dict[str, Any]:
        """Check moderation queue status."""
        try:
            # Check pending reports
            pending_reports = Report.query.filter_by(status='pending').count()
            
            # Check old pending reports (over 24 hours)
            old_reports = Report.query.filter(
                Report.status == 'pending',
                Report.created_at < datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            if pending_reports > 100:  # High queue
                return {
                    'status': 'warning',
                    'message': f'High moderation queue: {pending_reports} pending reports',
                    'details': {
                        'pending_reports': pending_reports,
                        'old_reports': old_reports
                    }
                }
            elif old_reports > 10:  # Old reports not addressed
                return {
                    'status': 'warning',
                    'message': f'Old reports in queue: {old_reports} over 24 hours old',
                    'details': {
                        'pending_reports': pending_reports,
                        'old_reports': old_reports
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Moderation queue manageable: {pending_reports} pending',
                    'details': {
                        'pending_reports': pending_reports,
                        'old_reports': old_reports
                    }
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Moderation queue check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database-specific metrics."""
        try:
            # Table counts
            user_count = User.query.filter_by(is_deleted=False).count()
            fact_count = Fact.query.filter_by(is_deleted=False).count()
            comment_count = Comment.query.filter_by(is_deleted=False).count()
            report_count = Report.query.count()
            
            return {
                'table_counts': {
                    'users': user_count,
                    'facts': fact_count,
                    'comments': comment_count,
                    'reports': report_count
                }
            }
            
        except Exception:
            return {'error': 'Unable to retrieve database metrics'}
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics."""
        try:
            # Recent activity metrics
            last_hour = datetime.utcnow() - timedelta(hours=1)
            
            active_users = User.query.filter(
                User.last_login >= last_hour
            ).count()
            
            recent_content = Fact.query.filter(
                Fact.created_at >= last_hour,
                Fact.is_deleted == False
            ).count() + Comment.query.filter(
                Comment.created_at >= last_hour,
                Comment.is_deleted == False
            ).count()
            
            return {
                'recent_activity': {
                    'active_users_last_hour': active_users,
                    'content_created_last_hour': recent_content
                }
            }
            
        except Exception:
            return {'error': 'Unable to retrieve application metrics'}
    
    def _store_health_check_result(self, check_name: str, result: Dict[str, Any]):
        """Store health check result in database."""
        try:
            # Map check names to categories
            category_map = {
                'database': 'database',
                'memory': 'system',
                'disk': 'system',
                'cpu': 'system',
                'application': 'application',
                'user_activity': 'application',
                'content_health': 'application',
                'moderation_queue': 'moderation'
            }
            
            health_record = SystemHealth(
                check_name=check_name,
                category=category_map.get(check_name, 'system'),
                status=result['status'],
                response_time_ms=result.get('response_time_ms'),
                message=result['message'],
                details=result.get('details'),
                cpu_usage=result.get('details', {}).get('cpu_percent'),
                memory_usage=result.get('details', {}).get('usage_percent'),
                disk_usage=result.get('details', {}).get('usage_percent'),
                last_check_at=datetime.utcnow()
            )
            
            db.session.add(health_record)
            db.session.commit()
            
        except Exception:
            # Don't let storage errors break health checks
            db.session.rollback()
    
    def _log_admin_activity(self, admin_id: str, activity_type: str, action: str, 
                           description: str, severity: str = 'low', details: Dict = None):
        """Log admin activity for audit purposes."""
        try:
            activity = AdminActivity(
                admin_id=admin_id,
                activity_type=activity_type,
                action=action,
                description=description,
                severity=severity,
                details=details
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception:
            # Don't let logging errors break the main functionality
            db.session.rollback()
