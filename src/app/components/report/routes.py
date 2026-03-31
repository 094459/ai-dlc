"""
Report Component Routes

Handles HTTP requests for content reporting and moderation functionality.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.components.report.services import ReportManagementService, ReportQueueService, ReportAnalyticsService
from app.models import ReportCategory
from app.components.security.services import AuditService

report_bp = Blueprint('report', __name__, url_prefix='/reports')


# User Reporting Routes
@report_bp.route('/create', methods=['POST'])
@login_required
def create_report():
    """Create a new content report."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        content_type = data.get('content_type')
        content_id = data.get('content_id')
        category_id = data.get('category_id')
        reason = data.get('reason')
        
        success, message, report = ReportManagementService.create_report(
            current_user.id,
            content_type,
            content_id,
            category_id,
            reason
        )
        
        if success:
            # Log the report creation for security audit
            AuditService.log_action(
                user_id=current_user.id,
                action_type='report_created',
                resource_type='report',
                resource_id=report.id,
                new_values=f"Report created for {content_type} {content_id}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'success': True,
                'message': message,
                'report_id': report.id
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to create report'
        }), 500


@report_bp.route('/categories', methods=['GET'])
def get_report_categories():
    """Get available report categories."""
    try:
        categories = ReportCategory.query.filter_by(is_active=True).order_by(ReportCategory.name).all()
        
        return jsonify({
            'success': True,
            'categories': [
                {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'severity_level': category.severity_level
                }
                for category in categories
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get categories'
        }), 500


@report_bp.route('/my-reports')
@login_required
def my_reports():
    """Display user's submitted reports."""
    try:
        page = request.args.get('page', 1, type=int)
        status = request.args.get('status')
        
        reports_data = ReportManagementService.get_user_reports(
            current_user.id,
            status=status,
            page=page,
            per_page=10
        )
        
        return render_template(
            'report/my_reports.html',
            reports_data=reports_data,
            current_status=status
        )
        
    except Exception as e:
        flash('Failed to load your reports', 'error')
        return redirect(url_for('main.index'))


@report_bp.route('/check-duplicate')
@login_required
def check_duplicate():
    """Check if content has already been reported by user."""
    try:
        content_type = request.args.get('content_type')
        content_id = request.args.get('content_id')
        
        if not content_type or not content_id:
            return jsonify({
                'success': False,
                'message': 'Missing parameters'
            }), 400
        
        # Check for existing pending report
        from app.models import Report
        existing_report = Report.query.filter_by(
            reporter_id=current_user.id,
            reported_content_type=content_type,
            reported_content_id=content_id,
            status='pending'
        ).first()
        
        return jsonify({
            'success': True,
            'has_duplicate': existing_report is not None,
            'report_id': existing_report.id if existing_report else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to check for duplicates'
        }), 500


# Moderation Routes (Moderator Only)
@report_bp.route('/moderation/queue')
@login_required
def moderation_queue():
    """Display moderation queue for moderators."""
    if not current_user.is_moderator:
        flash('Access denied. Moderator privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        priority = request.args.get('priority')
        category_id = request.args.get('category_id')
        
        reports_data = ReportQueueService.get_pending_reports(
            priority=priority,
            category_id=category_id,
            page=page,
            per_page=15
        )
        
        # Get categories for filtering
        categories = ReportCategory.query.filter_by(is_active=True).all()
        
        # Get queue statistics
        queue_stats = ReportQueueService.get_queue_statistics()
        
        return render_template(
            'report/moderation_queue.html',
            reports_data=reports_data,
            categories=categories,
            queue_stats=queue_stats,
            current_priority=priority,
            current_category=category_id
        )
        
    except Exception as e:
        flash('Failed to load moderation queue', 'error')
        return redirect(url_for('main.index'))


@report_bp.route('/moderation/my-queue')
@login_required
def my_moderation_queue():
    """Display reports assigned to current moderator."""
    if not current_user.is_moderator:
        flash('Access denied. Moderator privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        
        reports_data = ReportQueueService.get_moderator_queue(
            current_user.id,
            page=page,
            per_page=15
        )
        
        return render_template(
            'report/my_moderation_queue.html',
            reports_data=reports_data
        )
        
    except Exception as e:
        flash('Failed to load your moderation queue', 'error')
        return redirect(url_for('main.index'))


@report_bp.route('/moderation/assign/<report_id>', methods=['POST'])
@login_required
def assign_report(report_id):
    """Assign a report to current moderator."""
    if not current_user.is_moderator:
        return jsonify({
            'success': False,
            'message': 'Access denied'
        }), 403
    
    try:
        success, message = ReportQueueService.assign_report_to_moderator(
            report_id,
            current_user.id
        )
        
        if success:
            # Log the assignment
            AuditService.log_action(
                user_id=current_user.id,
                action_type='report_assigned',
                resource_type='report',
                resource_id=report_id,
                new_values=f"Report {report_id} assigned to moderator",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to assign report'
        }), 500


@report_bp.route('/moderation/resolve/<report_id>', methods=['POST'])
@login_required
def resolve_report(report_id):
    """Resolve a report with moderator action."""
    if not current_user.is_moderator:
        return jsonify({
            'success': False,
            'message': 'Access denied'
        }), 403
    
    try:
        data = request.get_json()
        status = data.get('status')  # 'resolved' or 'dismissed'
        notes = data.get('notes', '')
        
        if status not in ['resolved', 'dismissed']:
            return jsonify({
                'success': False,
                'message': 'Invalid status'
            }), 400
        
        success, message = ReportManagementService.update_report_status(
            report_id,
            status,
            current_user.id,
            notes
        )
        
        if success:
            # Log the resolution
            AuditService.log_action(
                user_id=current_user.id,
                action_type='report_resolved',
                resource_type='report',
                resource_id=report_id,
                new_values=f"Report {report_id} {status} by moderator",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to resolve report'
        }), 500


@report_bp.route('/moderation/statistics')
@login_required
def moderation_statistics():
    """Display moderation statistics and analytics."""
    if not current_user.is_moderator:
        flash('Access denied. Moderator privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get various analytics
        queue_stats = ReportQueueService.get_queue_statistics()
        report_trends = ReportAnalyticsService.get_report_trends(days=30)
        category_stats = ReportAnalyticsService.get_category_statistics()
        
        # Get moderator performance if they have handled reports
        moderator_performance = ReportAnalyticsService.get_moderator_performance(
            current_user.id,
            days=30
        )
        
        return render_template(
            'report/moderation_statistics.html',
            queue_stats=queue_stats,
            report_trends=report_trends,
            category_stats=category_stats,
            moderator_performance=moderator_performance
        )
        
    except Exception as e:
        flash('Failed to load moderation statistics', 'error')
        return redirect(url_for('main.index'))


# API Routes for AJAX calls
@report_bp.route('/api/queue-stats')
@login_required
def api_queue_stats():
    """Get queue statistics via API."""
    if not current_user.is_moderator:
        return jsonify({
            'success': False,
            'message': 'Access denied'
        }), 403
    
    try:
        stats = ReportQueueService.get_queue_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get statistics'
        }), 500


@report_bp.route('/api/content/<content_type>/<content_id>/reports')
@login_required
def api_content_reports(content_type, content_id):
    """Get reports for specific content (moderators only)."""
    if not current_user.is_moderator:
        return jsonify({
            'success': False,
            'message': 'Access denied'
        }), 403
    
    try:
        reports = ReportManagementService.get_content_reports(content_type, content_id)
        
        reports_data = []
        for report in reports:
            reports_data.append({
                'id': report.id,
                'category': report.category.name,
                'reason': report.reason,
                'status': report.status,
                'priority': report.priority,
                'reporter_id': report.reporter_id,
                'created_at': report.created_at.isoformat(),
                'age_hours': report.age_in_hours
            })
        
        return jsonify({
            'success': True,
            'reports': reports_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get content reports'
        }), 500


# Error handlers for the report blueprint
@report_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors in report routes."""
    if request.is_json:
        return jsonify({
            'success': False,
            'message': 'Report not found'
        }), 404
    
    flash('Report not found', 'error')
    return redirect(url_for('main.index'))


@report_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors in report routes."""
    if request.is_json:
        return jsonify({
            'success': False,
            'message': 'Access denied'
        }), 403
    
    flash('Access denied', 'error')
    return redirect(url_for('main.index'))
