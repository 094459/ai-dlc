"""
Report Component Services

Provides business logic for content reporting, moderation queue management,
and report analytics.
"""

from flask import current_app, request
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta, date
from app.models import db, Report, ReportCategory, ReportAction, ReportStatistics
from app.models.user import User
from app.models.content import Fact
from app.models.community import Comment


class ReportManagementService:
    """Service for managing content reports and report lifecycle."""
    
    @staticmethod
    def create_report(reporter_id, content_type, content_id, category_id, reason):
        """
        Create a new content report.
        
        Args:
            reporter_id (str): ID of the user submitting the report
            content_type (str): Type of content being reported ('fact' or 'comment')
            content_id (str): ID of the content being reported
            category_id (str): ID of the report category
            reason (str): Detailed reason for the report
            
        Returns:
            tuple: (success: bool, message: str, report: Report or None)
        """
        try:
            # Validate inputs
            if not all([reporter_id, content_type, content_id, category_id, reason]):
                return False, "All fields are required", None
            
            if content_type not in ['fact', 'comment']:
                return False, "Invalid content type", None
            
            if len(reason.strip()) < 10:
                return False, "Report reason must be at least 10 characters", None
            
            if len(reason.strip()) > 1000:
                return False, "Report reason cannot exceed 1000 characters", None
            
            # Check if content exists
            content = ReportManagementService._get_content(content_type, content_id)
            if not content:
                return False, "Content not found", None
            
            # Check if content is already deleted
            if content.is_deleted:
                return False, "Cannot report deleted content", None
            
            # Validate category
            category = ReportCategory.query.filter_by(
                id=category_id, 
                is_active=True
            ).first()
            if not category:
                return False, "Invalid report category", None
            
            # Check for duplicate reports
            existing_report = Report.query.filter_by(
                reporter_id=reporter_id,
                reported_content_type=content_type,
                reported_content_id=content_id,
                status='pending'
            ).first()
            
            if existing_report:
                return False, "You have already reported this content", None
            
            # Check if user is trying to report their own content
            if ReportManagementService._is_own_content(reporter_id, content_type, content_id):
                return False, "You cannot report your own content", None
            
            # Check rate limiting
            if not ReportManagementService._check_rate_limit(reporter_id):
                return False, "Too many reports submitted recently. Please wait before submitting another report.", None
            
            # Create the report
            report = Report(
                reporter_id=reporter_id,
                reported_content_type=content_type,
                reported_content_id=content_id,
                category_id=category_id,
                reason=reason.strip(),
                status='pending',
                priority=ReportManagementService._calculate_priority(category),
                reporter_ip=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None
            )
            
            report.save()
            
            # Log the report creation
            ReportManagementService._log_report_action(
                report.id, 
                reporter_id, 
                'created', 
                f"Report created for {content_type} {content_id}"
            )
            
            # Auto-escalate if needed
            if category.auto_escalate:
                ReportManagementService._escalate_report(report.id, 'high')
            
            return True, "Report submitted successfully", report
            
        except Exception as e:
            current_app.logger.error(f"Error creating report: {str(e)}")
            return False, "Failed to submit report", None
    
    @staticmethod
    def get_user_reports(user_id, status=None, page=1, per_page=20):
        """
        Get reports submitted by a user.
        
        Args:
            user_id (str): ID of the user
            status (str, optional): Filter by report status
            page (int): Page number for pagination
            per_page (int): Number of reports per page
            
        Returns:
            dict: Paginated reports with metadata
        """
        try:
            query = Report.query.filter_by(reporter_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            query = query.order_by(desc(Report.created_at))
            
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            reports_data = []
            for report in pagination.items:
                content = report.get_reported_content()
                reports_data.append({
                    'report': report,
                    'category': report.category,
                    'content': content,
                    'content_preview': ReportManagementService._get_content_preview(content)
                })
            
            return {
                'reports': reports_data,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting user reports: {str(e)}")
            return {'reports': [], 'pagination': {}}
    
    @staticmethod
    def get_content_reports(content_type, content_id):
        """
        Get all reports for a specific piece of content.
        
        Args:
            content_type (str): Type of content ('fact' or 'comment')
            content_id (str): ID of the content
            
        Returns:
            list: List of reports for the content
        """
        try:
            reports = Report.query.filter_by(
                reported_content_type=content_type,
                reported_content_id=content_id
            ).order_by(desc(Report.created_at)).all()
            
            return reports
            
        except Exception as e:
            current_app.logger.error(f"Error getting content reports: {str(e)}")
            return []
    
    @staticmethod
    def update_report_status(report_id, status, moderator_id, notes=None):
        """
        Update report status and add moderation notes.
        
        Args:
            report_id (str): ID of the report
            status (str): New status for the report
            moderator_id (str): ID of the moderator making the change
            notes (str, optional): Resolution notes
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            report = db.session.get(Report, report_id)
            if not report:
                return False, "Report not found"
            
            if status not in ['pending', 'assigned', 'reviewed', 'resolved', 'dismissed']:
                return False, "Invalid status"
            
            old_status = report.status
            report.status = status
            report.moderator_id = moderator_id
            
            if notes:
                report.resolution_notes = notes
            
            if status in ['resolved', 'dismissed']:
                report.resolved_at = datetime.utcnow()
            
            report.save()
            
            # Log the status change
            ReportManagementService._log_report_action(
                report_id,
                moderator_id,
                'status_changed',
                f"Status changed from {old_status} to {status}",
                old_status,
                status
            )
            
            return True, f"Report status updated to {status}"
            
        except Exception as e:
            current_app.logger.error(f"Error updating report status: {str(e)}")
            return False, "Failed to update report status"
    
    # Helper methods
    @staticmethod
    def _get_content(content_type, content_id):
        """Get content object by type and ID."""
        if content_type == 'fact':
            return db.session.get(Fact, content_id)
        elif content_type == 'comment':
            return db.session.get(Comment, content_id)
        return None
    
    @staticmethod
    def _is_own_content(user_id, content_type, content_id):
        """Check if user is trying to report their own content."""
        content = ReportManagementService._get_content(content_type, content_id)
        return content and content.user_id == user_id
    
    @staticmethod
    def _check_rate_limit(user_id):
        """Check if user has exceeded report rate limit."""
        # Allow max 5 reports per hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_reports = Report.query.filter(
            Report.reporter_id == user_id,
            Report.created_at >= one_hour_ago
        ).count()
        
        return recent_reports < 5
    
    @staticmethod
    def _calculate_priority(category):
        """Calculate report priority based on category severity."""
        if category.severity_level >= 4:
            return 'urgent'
        elif category.severity_level >= 3:
            return 'high'
        elif category.severity_level >= 2:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _escalate_report(report_id, new_priority):
        """Escalate report to higher priority."""
        try:
            report = db.session.get(Report, report_id)
            if report:
                old_priority = report.priority
                report.priority = new_priority
                report.save()
                
                ReportManagementService._log_report_action(
                    report_id,
                    None,
                    'escalated',
                    f"Priority escalated from {old_priority} to {new_priority}"
                )
        except Exception as e:
            current_app.logger.error(f"Error escalating report: {str(e)}")
    
    @staticmethod
    def _log_report_action(report_id, moderator_id, action_type, notes, old_status=None, new_status=None):
        """Log report action for audit trail."""
        try:
            action = ReportAction(
                report_id=report_id,
                moderator_id=moderator_id,
                action_type=action_type,
                notes=notes,
                previous_status=old_status,
                new_status=new_status
            )
            action.save()
        except Exception as e:
            current_app.logger.error(f"Error logging report action: {str(e)}")
    
    @staticmethod
    def _get_content_preview(content):
        """Get a preview of the content for display."""
        if not content:
            return "Content not available"
        
        if hasattr(content, 'content'):
            text = content.content
        else:
            text = str(content)
        
        return text[:100] + "..." if len(text) > 100 else text


class ReportQueueService:
    """Service for managing moderation queue and report assignments."""
    
    @staticmethod
    def get_pending_reports(priority=None, category_id=None, page=1, per_page=20):
        """
        Get pending reports for moderation queue.
        
        Args:
            priority (str, optional): Filter by priority
            category_id (str, optional): Filter by category
            page (int): Page number for pagination
            per_page (int): Number of reports per page
            
        Returns:
            dict: Paginated reports with metadata
        """
        try:
            query = Report.query.filter_by(status='pending')
            
            if priority:
                query = query.filter_by(priority=priority)
            
            if category_id:
                query = query.filter_by(category_id=category_id)
            
            # Order by priority and age (SQLite compatible)
            # Map priority to numeric values for ordering
            priority_map = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
            query = query.order_by(
                db.case(
                    (Report.priority == 'urgent', 1),
                    (Report.priority == 'high', 2),
                    (Report.priority == 'medium', 3),
                    else_=4
                ),
                Report.created_at
            )
            
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            reports_data = []
            for report in pagination.items:
                content = report.get_reported_content()
                reports_data.append({
                    'report': report,
                    'category': report.category,
                    'reporter': report.reporter,
                    'content': content,
                    'content_preview': ReportManagementService._get_content_preview(content),
                    'age_hours': report.age_in_hours
                })
            
            return {
                'reports': reports_data,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting pending reports: {str(e)}")
            return {'reports': [], 'pagination': {}}
    
    @staticmethod
    def assign_report_to_moderator(report_id, moderator_id):
        """
        Assign a report to a specific moderator.
        
        Args:
            report_id (str): ID of the report
            moderator_id (str): ID of the moderator
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            report = db.session.get(Report, report_id)
            if not report:
                return False, "Report not found"
            
            if report.status != 'pending':
                return False, "Report is not available for assignment"
            
            # Verify moderator exists and has proper permissions
            moderator = db.session.get(User, moderator_id)
            if not moderator or not moderator.is_moderator:
                return False, "Invalid moderator"
            
            report.moderator_id = moderator_id
            report.status = 'assigned'
            report.save()
            
            # Log the assignment
            ReportManagementService._log_report_action(
                report_id,
                moderator_id,
                'assigned',
                f"Report assigned to moderator {moderator.email}"
            )
            
            return True, "Report assigned successfully"
            
        except Exception as e:
            current_app.logger.error(f"Error assigning report: {str(e)}")
            return False, "Failed to assign report"
    
    @staticmethod
    def get_moderator_queue(moderator_id, page=1, per_page=20):
        """
        Get reports assigned to a specific moderator.
        
        Args:
            moderator_id (str): ID of the moderator
            page (int): Page number for pagination
            per_page (int): Number of reports per page
            
        Returns:
            dict: Paginated reports assigned to moderator
        """
        try:
            query = Report.query.filter_by(
                moderator_id=moderator_id,
                status='assigned'
            ).order_by(desc(Report.created_at))
            
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            reports_data = []
            for report in pagination.items:
                content = report.get_reported_content()
                reports_data.append({
                    'report': report,
                    'category': report.category,
                    'reporter': report.reporter,
                    'content': content,
                    'content_preview': ReportManagementService._get_content_preview(content),
                    'age_hours': report.age_in_hours
                })
            
            return {
                'reports': reports_data,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting moderator queue: {str(e)}")
            return {'reports': [], 'pagination': {}}
    
    @staticmethod
    def get_queue_statistics():
        """
        Get statistics about the moderation queue.
        
        Returns:
            dict: Queue statistics
        """
        try:
            stats = {
                'pending_reports': Report.query.filter_by(status='pending').count(),
                'assigned_reports': Report.query.filter_by(status='assigned').count(),
                'resolved_today': Report.query.filter(
                    Report.status == 'resolved',
                    Report.resolved_at >= datetime.utcnow().date()
                ).count(),
                'urgent_reports': Report.query.filter_by(
                    status='pending',
                    priority='urgent'
                ).count(),
                'high_priority_reports': Report.query.filter_by(
                    status='pending',
                    priority='high'
                ).count()
            }
            
            # Average resolution time for reports resolved in last 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_resolved = Report.query.filter(
                Report.status == 'resolved',
                Report.resolved_at >= seven_days_ago
            ).all()
            
            if recent_resolved:
                total_time = sum([
                    (report.resolved_at - report.created_at).total_seconds() / 3600
                    for report in recent_resolved
                ])
                stats['avg_resolution_hours'] = round(total_time / len(recent_resolved), 2)
            else:
                stats['avg_resolution_hours'] = 0
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Error getting queue statistics: {str(e)}")
            return {}


class ReportAnalyticsService:
    """Service for report analytics and trend analysis."""
    
    @staticmethod
    def get_report_trends(days=30):
        """
        Get report trends over specified time period.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            dict: Report trends data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Daily report counts
            daily_reports = db.session.query(
                func.date(Report.created_at).label('date'),
                func.count(Report.id).label('count')
            ).filter(
                Report.created_at >= start_date
            ).group_by(
                func.date(Report.created_at)
            ).order_by('date').all()
            
            # Category breakdown
            category_stats = db.session.query(
                ReportCategory.name,
                func.count(Report.id).label('count')
            ).join(Report).filter(
                Report.created_at >= start_date
            ).group_by(ReportCategory.name).all()
            
            # Status breakdown
            status_stats = db.session.query(
                Report.status,
                func.count(Report.id).label('count')
            ).filter(
                Report.created_at >= start_date
            ).group_by(Report.status).all()
            
            return {
                'daily_reports': [{'date': str(r.date), 'count': r.count} for r in daily_reports],
                'category_breakdown': [{'category': r.name, 'count': r.count} for r in category_stats],
                'status_breakdown': [{'status': r.status, 'count': r.count} for r in status_stats],
                'total_reports': sum([r.count for r in daily_reports])
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting report trends: {str(e)}")
            return {}
    
    @staticmethod
    def get_category_statistics():
        """
        Get statistics for each report category.
        
        Returns:
            list: Category statistics
        """
        try:
            categories = ReportCategory.query.filter_by(is_active=True).all()
            stats = []
            
            for category in categories:
                category_reports = Report.query.filter_by(category_id=category.id)
                
                total_reports = category_reports.count()
                resolved_reports = category_reports.filter_by(status='resolved').count()
                dismissed_reports = category_reports.filter_by(status='dismissed').count()
                pending_reports = category_reports.filter_by(status='pending').count()
                
                # Calculate average resolution time
                resolved_with_time = category_reports.filter(
                    Report.status == 'resolved',
                    Report.resolved_at.isnot(None)
                ).all()
                
                avg_resolution_hours = 0
                if resolved_with_time:
                    total_time = sum([
                        (report.resolved_at - report.created_at).total_seconds() / 3600
                        for report in resolved_with_time
                    ])
                    avg_resolution_hours = round(total_time / len(resolved_with_time), 2)
                
                stats.append({
                    'category': category,
                    'total_reports': total_reports,
                    'resolved_reports': resolved_reports,
                    'dismissed_reports': dismissed_reports,
                    'pending_reports': pending_reports,
                    'resolution_rate': round((resolved_reports / total_reports * 100), 2) if total_reports > 0 else 0,
                    'avg_resolution_hours': avg_resolution_hours
                })
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Error getting category statistics: {str(e)}")
            return []
    
    @staticmethod
    def get_moderator_performance(moderator_id, days=30):
        """
        Get performance metrics for a specific moderator.
        
        Args:
            moderator_id (str): ID of the moderator
            days (int): Number of days to analyze
            
        Returns:
            dict: Moderator performance metrics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Reports handled by moderator
            handled_reports = Report.query.filter(
                Report.moderator_id == moderator_id,
                Report.resolved_at >= start_date
            ).all()
            
            if not handled_reports:
                return {
                    'reports_handled': 0,
                    'avg_resolution_hours': 0,
                    'resolution_rate': 0,
                    'categories_handled': []
                }
            
            # Calculate metrics
            total_handled = len(handled_reports)
            resolved_count = len([r for r in handled_reports if r.status == 'resolved'])
            
            total_time = sum([
                (report.resolved_at - report.created_at).total_seconds() / 3600
                for report in handled_reports
            ])
            avg_resolution_hours = round(total_time / total_handled, 2)
            
            # Category breakdown
            category_counts = {}
            for report in handled_reports:
                category_name = report.category.name
                category_counts[category_name] = category_counts.get(category_name, 0) + 1
            
            return {
                'reports_handled': total_handled,
                'resolved_reports': resolved_count,
                'dismissed_reports': total_handled - resolved_count,
                'avg_resolution_hours': avg_resolution_hours,
                'resolution_rate': round((resolved_count / total_handled * 100), 2),
                'categories_handled': [
                    {'category': cat, 'count': count}
                    for cat, count in category_counts.items()
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting moderator performance: {str(e)}")
            return {}
    
    @staticmethod
    def identify_problematic_users(threshold=5):
        """
        Identify users who have been reported multiple times.
        
        Args:
            threshold (int): Minimum number of reports to be considered problematic
            
        Returns:
            list: Users with high report counts
        """
        try:
            # Count reports per content creator
            fact_reports = db.session.query(
                Fact.user_id,
                func.count(Report.id).label('report_count')
            ).join(
                Report, and_(
                    Report.reported_content_type == 'fact',
                    Report.reported_content_id == Fact.id
                )
            ).group_by(Fact.user_id).subquery()
            
            comment_reports = db.session.query(
                Comment.user_id,
                func.count(Report.id).label('report_count')
            ).join(
                Report, and_(
                    Report.reported_content_type == 'comment',
                    Report.reported_content_id == Comment.id
                )
            ).group_by(Comment.user_id).subquery()
            
            # Combine and filter by threshold
            problematic_users = db.session.query(
                User,
                (func.coalesce(fact_reports.c.report_count, 0) + 
                 func.coalesce(comment_reports.c.report_count, 0)).label('total_reports')
            ).outerjoin(
                fact_reports, User.id == fact_reports.c.user_id
            ).outerjoin(
                comment_reports, User.id == comment_reports.c.user_id
            ).having(
                func.coalesce(fact_reports.c.report_count, 0) + 
                func.coalesce(comment_reports.c.report_count, 0) >= threshold
            ).order_by(desc('total_reports')).all()
            
            return [
                {
                    'user': user,
                    'total_reports': total_reports
                }
                for user, total_reports in problematic_users
            ]
            
        except Exception as e:
            current_app.logger.error(f"Error identifying problematic users: {str(e)}")
            return []
