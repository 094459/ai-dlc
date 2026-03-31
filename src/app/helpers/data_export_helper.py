"""
Data Export Helper utilities for generating reports and backups.
"""

import os
import json
import csv
import zipfile
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from io import StringIO, BytesIO
from flask import current_app
from app.models import db, User, Fact, Comment, Report, Notification
from app.models.admin import AdminActivity, SystemHealth
from app.components.analytics.tracking import track_admin_action


class DataExportHelper:
    """Helper class for data export operations."""
    
    @staticmethod
    def export_users_csv(filters: Dict[str, Any] = None, admin_user_id: str = None) -> str:
        """
        Export users data to CSV format.
        
        Args:
            filters: Optional filters to apply
            admin_user_id: ID of admin requesting export
            
        Returns:
            CSV string data
        """
        try:
            # Track export operation
            if admin_user_id:
                track_admin_action(admin_user_id, 'data_export', 'export_users_csv', {
                    'filters': filters or {}
                })
            
            # Build query
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
            
            # Prepare CSV data
            output = StringIO()
            fieldnames = [
                'id', 'username', 'email', 'first_name', 'last_name', 'role',
                'is_active', 'is_suspended', 'is_banned', 'email_verified',
                'created_at', 'last_login', 'fact_count', 'comment_count',
                'reports_made', 'reports_received'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for user in users:
                # Get user statistics
                fact_count = Fact.query.filter_by(author_id=user.id, is_deleted=False).count()
                comment_count = Comment.query.filter_by(author_id=user.id, is_deleted=False).count()
                reports_made = Report.query.filter_by(reporter_id=user.id).count()
                reports_received = Report.query.filter_by(reported_user_id=user.id).count()
                
                writer.writerow({
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
                    'last_login': user.last_login.isoformat() if user.last_login else '',
                    'fact_count': fact_count,
                    'comment_count': comment_count,
                    'reports_made': reports_made,
                    'reports_received': reports_received
                })
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error exporting users: {str(e)}"
    
    @staticmethod
    def export_content_csv(content_type: str = 'facts', filters: Dict[str, Any] = None,
                          admin_user_id: str = None) -> str:
        """
        Export content data (facts or comments) to CSV format.
        
        Args:
            content_type: Type of content to export ('facts' or 'comments')
            filters: Optional filters to apply
            admin_user_id: ID of admin requesting export
            
        Returns:
            CSV string data
        """
        try:
            # Track export operation
            if admin_user_id:
                track_admin_action(admin_user_id, 'data_export', f'export_{content_type}_csv', {
                    'filters': filters or {}
                })
            
            output = StringIO()
            
            if content_type == 'facts':
                # Export facts
                query = Fact.query.filter_by(is_deleted=False)
                
                if filters:
                    if filters.get('is_published') is not None:
                        query = query.filter_by(is_published=filters['is_published'])
                    if filters.get('created_after'):
                        query = query.filter(Fact.created_at >= filters['created_after'])
                    if filters.get('created_before'):
                        query = query.filter(Fact.created_at <= filters['created_before'])
                
                facts = query.order_by(Fact.created_at.desc()).all()
                
                fieldnames = [
                    'id', 'title', 'content', 'author_username', 'is_published',
                    'created_at', 'updated_at', 'vote_count', 'comment_count'
                ]
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for fact in facts:
                    # Get statistics
                    from app.models.community import FactVote
                    vote_count = FactVote.query.filter_by(fact_id=fact.id).count()
                    comment_count = Comment.query.filter_by(fact_id=fact.id, is_deleted=False).count()
                    
                    writer.writerow({
                        'id': fact.id,
                        'title': fact.title,
                        'content': fact.content[:500] + '...' if len(fact.content) > 500 else fact.content,
                        'author_username': fact.author.username if fact.author else 'Unknown',
                        'is_published': fact.is_published,
                        'created_at': fact.created_at.isoformat(),
                        'updated_at': fact.updated_at.isoformat(),
                        'vote_count': vote_count,
                        'comment_count': comment_count
                    })
            
            elif content_type == 'comments':
                # Export comments
                query = Comment.query.filter_by(is_deleted=False)
                
                if filters:
                    if filters.get('created_after'):
                        query = query.filter(Comment.created_at >= filters['created_after'])
                    if filters.get('created_before'):
                        query = query.filter(Comment.created_at <= filters['created_before'])
                
                comments = query.order_by(Comment.created_at.desc()).all()
                
                fieldnames = [
                    'id', 'content', 'author_username', 'fact_title', 'parent_comment_id',
                    'created_at', 'updated_at', 'vote_count'
                ]
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for comment in comments:
                    # Get statistics
                    from app.models.community import CommentVote
                    vote_count = CommentVote.query.filter_by(comment_id=comment.id).count()
                    
                    writer.writerow({
                        'id': comment.id,
                        'content': comment.content[:200] + '...' if len(comment.content) > 200 else comment.content,
                        'author_username': comment.author.username if comment.author else 'Unknown',
                        'fact_title': comment.fact.title if comment.fact else 'Unknown',
                        'parent_comment_id': comment.parent_id,
                        'created_at': comment.created_at.isoformat(),
                        'updated_at': comment.updated_at.isoformat(),
                        'vote_count': vote_count
                    })
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error exporting {content_type}: {str(e)}"
    
    @staticmethod
    def export_moderation_csv(filters: Dict[str, Any] = None, admin_user_id: str = None) -> str:
        """
        Export moderation data to CSV format.
        
        Args:
            filters: Optional filters to apply
            admin_user_id: ID of admin requesting export
            
        Returns:
            CSV string data
        """
        try:
            # Track export operation
            if admin_user_id:
                track_admin_action(admin_user_id, 'data_export', 'export_moderation_csv', {
                    'filters': filters or {}
                })
            
            # Export reports
            query = Report.query
            
            if filters:
                if filters.get('status'):
                    query = query.filter_by(status=filters['status'])
                if filters.get('priority'):
                    query = query.filter_by(priority=filters['priority'])
                if filters.get('created_after'):
                    query = query.filter(Report.created_at >= filters['created_after'])
                if filters.get('created_before'):
                    query = query.filter(Report.created_at <= filters['created_before'])
            
            reports = query.order_by(Report.created_at.desc()).all()
            
            output = StringIO()
            fieldnames = [
                'id', 'content_type', 'content_id', 'reason', 'category',
                'reporter_username', 'reported_user_username', 'status', 'priority',
                'created_at', 'resolved_at', 'assigned_moderator', 'resolution_notes'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for report in reports:
                writer.writerow({
                    'id': report.id,
                    'content_type': report.content_type,
                    'content_id': report.content_id,
                    'reason': report.reason,
                    'category': report.category.name if report.category else 'Unknown',
                    'reporter_username': report.reporter.username if report.reporter else 'Anonymous',
                    'reported_user_username': report.reported_user.username if report.reported_user else 'Unknown',
                    'status': report.status,
                    'priority': report.priority,
                    'created_at': report.created_at.isoformat(),
                    'resolved_at': report.resolved_at.isoformat() if report.resolved_at else '',
                    'assigned_moderator': report.assigned_moderator.username if report.assigned_moderator else '',
                    'resolution_notes': report.resolution_notes or ''
                })
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error exporting moderation data: {str(e)}"
    
    @staticmethod
    def export_analytics_csv(filters: Dict[str, Any] = None, admin_user_id: str = None) -> str:
        """
        Export analytics data to CSV format.
        
        Args:
            filters: Optional filters to apply
            admin_user_id: ID of admin requesting export
            
        Returns:
            CSV string data
        """
        try:
            # Track export operation
            if admin_user_id:
                track_admin_action(admin_user_id, 'data_export', 'export_analytics_csv', {
                    'filters': filters or {}
                })
            
            # Export admin activities as analytics proxy
            query = AdminActivity.query
            
            if filters:
                if filters.get('activity_type'):
                    query = query.filter_by(activity_type=filters['activity_type'])
                if filters.get('severity'):
                    query = query.filter_by(severity=filters['severity'])
                if filters.get('created_after'):
                    query = query.filter(AdminActivity.created_at >= filters['created_after'])
                if filters.get('created_before'):
                    query = query.filter(AdminActivity.created_at <= filters['created_before'])
            
            activities = query.order_by(AdminActivity.created_at.desc()).limit(10000).all()
            
            output = StringIO()
            fieldnames = [
                'id', 'admin_username', 'activity_type', 'action', 'description',
                'target_type', 'target_id', 'severity', 'created_at', 'ip_address'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for activity in activities:
                writer.writerow({
                    'id': activity.id,
                    'admin_username': activity.admin.username if activity.admin else 'System',
                    'activity_type': activity.activity_type,
                    'action': activity.action,
                    'description': activity.description,
                    'target_type': activity.target_type or '',
                    'target_id': activity.target_id or '',
                    'severity': activity.severity,
                    'created_at': activity.created_at.isoformat(),
                    'ip_address': activity.ip_address or ''
                })
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error exporting analytics data: {str(e)}"
    
    @staticmethod
    def create_full_backup(admin_user_id: str) -> bytes:
        """
        Create a full system backup as a ZIP file.
        
        Args:
            admin_user_id: ID of admin creating backup
            
        Returns:
            ZIP file bytes
        """
        try:
            # Track backup operation
            track_admin_action(admin_user_id, 'backup', 'create_full_backup')
            
            # Create temporary directory for backup files
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_files = {}
                
                # Export users
                users_csv = DataExportHelper.export_users_csv(admin_user_id=admin_user_id)
                backup_files['users.csv'] = users_csv
                
                # Export facts
                facts_csv = DataExportHelper.export_content_csv('facts', admin_user_id=admin_user_id)
                backup_files['facts.csv'] = facts_csv
                
                # Export comments
                comments_csv = DataExportHelper.export_content_csv('comments', admin_user_id=admin_user_id)
                backup_files['comments.csv'] = comments_csv
                
                # Export moderation data
                moderation_csv = DataExportHelper.export_moderation_csv(admin_user_id=admin_user_id)
                backup_files['moderation.csv'] = moderation_csv
                
                # Export analytics data
                analytics_csv = DataExportHelper.export_analytics_csv(admin_user_id=admin_user_id)
                backup_files['analytics.csv'] = analytics_csv
                
                # Export system health data
                health_data = DataExportHelper._export_system_health()
                backup_files['system_health.json'] = json.dumps(health_data, indent=2)
                
                # Create backup metadata
                metadata = {
                    'backup_type': 'full_system_backup',
                    'created_at': datetime.utcnow().isoformat(),
                    'created_by': admin_user_id,
                    'files_included': list(backup_files.keys()),
                    'version': '1.0'
                }
                backup_files['backup_metadata.json'] = json.dumps(metadata, indent=2)
                
                # Create ZIP file
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for filename, content in backup_files.items():
                        zip_file.writestr(filename, content)
                
                zip_buffer.seek(0)
                return zip_buffer.getvalue()
                
        except Exception as e:
            # Log backup failure
            from app.helpers.admin_helper import AdminHelper
            AdminHelper.log_admin_activity(
                admin_user_id,
                'backup_error',
                'full_backup_failed',
                f'Full backup creation failed: {str(e)}',
                severity='high'
            )
            raise Exception(f"Backup creation failed: {str(e)}")
    
    @staticmethod
    def _export_system_health() -> List[Dict[str, Any]]:
        """Export system health data."""
        try:
            health_records = SystemHealth.query.order_by(
                SystemHealth.last_check_at.desc()
            ).limit(1000).all()
            
            return [
                {
                    'id': record.id,
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
    
    @staticmethod
    def export_custom_report(report_config: Dict[str, Any], admin_user_id: str) -> str:
        """
        Export custom report based on configuration.
        
        Args:
            report_config: Configuration for the custom report
            admin_user_id: ID of admin requesting export
            
        Returns:
            Report data in specified format
        """
        try:
            # Track custom report export
            track_admin_action(admin_user_id, 'data_export', 'export_custom_report', {
                'report_config': report_config
            })
            
            report_type = report_config.get('type', 'users')
            format_type = report_config.get('format', 'csv')
            filters = report_config.get('filters', {})
            
            if report_type == 'users':
                return DataExportHelper.export_users_csv(filters, admin_user_id)
            elif report_type == 'facts':
                return DataExportHelper.export_content_csv('facts', filters, admin_user_id)
            elif report_type == 'comments':
                return DataExportHelper.export_content_csv('comments', filters, admin_user_id)
            elif report_type == 'moderation':
                return DataExportHelper.export_moderation_csv(filters, admin_user_id)
            elif report_type == 'analytics':
                return DataExportHelper.export_analytics_csv(filters, admin_user_id)
            else:
                return f"Error: Unknown report type '{report_type}'"
                
        except Exception as e:
            return f"Error creating custom report: {str(e)}"
    
    @staticmethod
    def get_export_statistics() -> Dict[str, Any]:
        """
        Get statistics about exportable data.
        
        Returns:
            Dictionary with export statistics
        """
        try:
            return {
                'users': {
                    'total': User.query.filter_by(is_deleted=False).count(),
                    'active': User.query.filter_by(is_active=True, is_deleted=False).count(),
                    'suspended': User.query.filter_by(is_suspended=True).count(),
                    'banned': User.query.filter_by(is_banned=True).count()
                },
                'content': {
                    'facts': Fact.query.filter_by(is_deleted=False).count(),
                    'published_facts': Fact.query.filter_by(is_deleted=False, is_published=True).count(),
                    'comments': Comment.query.filter_by(is_deleted=False).count()
                },
                'moderation': {
                    'total_reports': Report.query.count(),
                    'pending_reports': Report.query.filter_by(status='pending').count(),
                    'resolved_reports': Report.query.filter_by(status='resolved').count()
                },
                'system': {
                    'admin_activities': AdminActivity.query.count(),
                    'health_records': SystemHealth.query.count(),
                    'notifications': Notification.query.count()
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
