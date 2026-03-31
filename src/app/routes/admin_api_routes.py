"""
Admin API Routes for advanced administrative functionality and data management.
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime, timedelta
import json
from app.services.admin_dashboard_service import AdminDashboardService
from app.services.system_configuration_service import SystemConfigurationService
from app.services.user_management_service import UserManagementService
from app.services.system_health_service import SystemHealthService
from app.components.auth.services import SessionValidationService
from app.components.analytics.tracking import track_admin_action
from app.models import db, User, Fact, Comment, Report
from app.models.admin import AdminActivity, SystemHealth, AdminDashboardWidget


# Create API blueprint
admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

# Initialize services
admin_dashboard_service = AdminDashboardService()
config_service = SystemConfigurationService()
user_management_service = UserManagementService()
health_service = SystemHealthService()
session_service = SessionValidationService()


def admin_api_required(f):
    """Decorator to require admin authentication for API routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        current_user = session_service.get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has admin role
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        
        # Check if user is active
        if not current_user.is_active:
            return jsonify({'error': 'Account inactive'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


@admin_api_bp.route('/dashboard/widgets', methods=['GET'])
@admin_api_required
def get_dashboard_widgets():
    """Get admin dashboard widget configurations."""
    try:
        widgets = AdminDashboardWidget.query.filter_by(
            is_enabled=True,
            is_visible=True
        ).order_by(AdminDashboardWidget.position_y, AdminDashboardWidget.position_x).all()
        
        widget_data = []
        for widget in widgets:
            widget_data.append({
                'id': widget.id,
                'widget_id': widget.widget_id,
                'widget_type': widget.widget_type,
                'title': widget.title,
                'config': widget.config,
                'data_source': widget.data_source,
                'position': {
                    'x': widget.position_x,
                    'y': widget.position_y,
                    'width': widget.width,
                    'height': widget.height
                },
                'refresh_interval': widget.refresh_interval,
                'requires_permission': widget.requires_permission
            })
        
        return jsonify({'widgets': widget_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/dashboard/widgets', methods=['POST'])
@admin_api_required
def create_dashboard_widget():
    """Create a new dashboard widget."""
    try:
        current_user = session_service.get_current_user()
        data = request.get_json()
        
        if not data or 'widget_id' not in data or 'widget_type' not in data:
            return jsonify({'error': 'Missing required widget data'}), 400
        
        # Track widget creation
        track_admin_action(current_user.id, 'dashboard', 'create_widget',
                          metadata={'widget_id': data['widget_id']})
        
        widget = AdminDashboardWidget(
            widget_id=data['widget_id'],
            widget_type=data['widget_type'],
            title=data.get('title', 'New Widget'),
            config=data.get('config', {}),
            data_source=data.get('data_source', 'default'),
            position_x=data.get('position_x', 0),
            position_y=data.get('position_y', 0),
            width=data.get('width', 4),
            height=data.get('height', 3),
            refresh_interval=data.get('refresh_interval', 300),
            requires_permission=data.get('requires_permission'),
            created_by=current_user.id,
            is_system_widget=False
        )
        
        db.session.add(widget)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'widget_id': widget.id,
            'message': 'Widget created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/dashboard/widgets/<widget_id>', methods=['PUT'])
@admin_api_required
def update_dashboard_widget(widget_id):
    """Update dashboard widget configuration."""
    try:
        current_user = session_service.get_current_user()
        data = request.get_json()
        
        widget = AdminDashboardWidget.query.get(widget_id)
        if not widget:
            return jsonify({'error': 'Widget not found'}), 404
        
        # Track widget update
        track_admin_action(current_user.id, 'dashboard', 'update_widget',
                          metadata={'widget_id': widget.widget_id})
        
        # Update widget properties
        if 'title' in data:
            widget.title = data['title']
        if 'config' in data:
            widget.config = data['config']
        if 'position_x' in data:
            widget.position_x = data['position_x']
        if 'position_y' in data:
            widget.position_y = data['position_y']
        if 'width' in data:
            widget.width = data['width']
        if 'height' in data:
            widget.height = data['height']
        if 'refresh_interval' in data:
            widget.refresh_interval = data['refresh_interval']
        if 'is_enabled' in data:
            widget.is_enabled = data['is_enabled']
        if 'is_visible' in data:
            widget.is_visible = data['is_visible']
        
        widget.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Widget updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/dashboard/widgets/<widget_id>', methods=['DELETE'])
@admin_api_required
def delete_dashboard_widget(widget_id):
    """Delete dashboard widget."""
    try:
        current_user = session_service.get_current_user()
        
        widget = AdminDashboardWidget.query.get(widget_id)
        if not widget:
            return jsonify({'error': 'Widget not found'}), 404
        
        # Prevent deletion of system widgets
        if widget.is_system_widget:
            return jsonify({'error': 'Cannot delete system widgets'}), 400
        
        # Track widget deletion
        track_admin_action(current_user.id, 'dashboard', 'delete_widget',
                          metadata={'widget_id': widget.widget_id})
        
        db.session.delete(widget)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Widget deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/analytics/summary')
@admin_api_required
def get_analytics_summary():
    """Get comprehensive analytics summary for admin dashboard."""
    try:
        current_user = session_service.get_current_user()
        
        # Get date range from query parameters
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Track analytics access
        track_admin_action(current_user.id, 'analytics', 'view_summary',
                          metadata={'days': days})
        
        # Get user activity summary
        user_activity = user_management_service.get_user_activity_summary(days)
        
        # Get content summary
        content_summary = admin_dashboard_service.get_content_management_summary(current_user.id)
        
        # Get system health trends
        health_history = health_service.get_health_history(hours=days * 24)
        
        # Calculate health trends
        health_trends = {}
        for record in health_history:
            check_name = record['check_name']
            if check_name not in health_trends:
                health_trends[check_name] = {'healthy': 0, 'warning': 0, 'critical': 0}
            health_trends[check_name][record['status']] += 1
        
        return jsonify({
            'user_activity': user_activity,
            'content_summary': content_summary,
            'health_trends': health_trends,
            'period_days': days,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/users/search')
@admin_api_required
def search_users_api():
    """Advanced user search API with multiple filters."""
    try:
        current_user = session_service.get_current_user()
        
        # Get search parameters
        query = request.args.get('q', '').strip()
        role = request.args.get('role')
        status = request.args.get('status')
        created_after = request.args.get('created_after')
        created_before = request.args.get('created_before')
        has_reports = request.args.get('has_reports', '').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Limit to 100
        
        # Build filters
        filters = {}
        if role:
            filters['role'] = role
        if status == 'active':
            filters['is_active'] = True
        elif status == 'inactive':
            filters['is_active'] = False
        elif status == 'suspended':
            filters['is_suspended'] = True
        elif status == 'banned':
            filters['is_banned'] = True
        
        if created_after:
            filters['created_after'] = datetime.fromisoformat(created_after)
        if created_before:
            filters['created_before'] = datetime.fromisoformat(created_before)
        if has_reports:
            filters['has_reports'] = True
        
        # Track search
        track_admin_action(current_user.id, 'user_management', 'search_users',
                          metadata={'query': query, 'filters': filters})
        
        # Perform search
        result = user_management_service.search_users(
            query=query if query else None,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/content/summary')
@admin_api_required
def get_content_summary():
    """Get detailed content management summary."""
    try:
        current_user = session_service.get_current_user()
        
        # Track content summary access
        track_admin_action(current_user.id, 'content_management', 'view_summary')
        
        # Get content summary
        content_summary = admin_dashboard_service.get_content_management_summary(current_user.id)
        
        # Get additional content metrics
        days = int(request.args.get('days', 7))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily content creation trends
        daily_facts = db.session.query(
            db.func.date(Fact.created_at).label('date'),
            db.func.count(Fact.id).label('count')
        ).filter(
            Fact.created_at >= start_date,
            Fact.is_deleted == False
        ).group_by(db.func.date(Fact.created_at)).order_by('date').all()
        
        daily_comments = db.session.query(
            db.func.date(Comment.created_at).label('date'),
            db.func.count(Comment.id).label('count')
        ).filter(
            Comment.created_at >= start_date,
            Comment.is_deleted == False
        ).group_by(db.func.date(Comment.created_at)).order_by('date').all()
        
        # Format trends data
        content_trends = {
            'daily_facts': [
                {'date': date.isoformat(), 'count': count}
                for date, count in daily_facts
            ],
            'daily_comments': [
                {'date': date.isoformat(), 'count': count}
                for date, count in daily_comments
            ]
        }
        
        return jsonify({
            'content_summary': content_summary,
            'content_trends': content_trends,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/moderation/queue')
@admin_api_required
def get_moderation_queue():
    """Get moderation queue status and pending items."""
    try:
        current_user = session_service.get_current_user()
        
        # Track moderation queue access
        track_admin_action(current_user.id, 'moderation', 'view_queue')
        
        # Get pending reports with details
        pending_reports = db.session.query(Report).filter_by(
            status='pending'
        ).order_by(Report.created_at.desc()).limit(50).all()
        
        # Format report data
        reports_data = []
        for report in pending_reports:
            reports_data.append({
                'id': report.id,
                'content_type': report.content_type,
                'content_id': report.content_id,
                'reason': report.reason,
                'category': report.category.name if report.category else 'Unknown',
                'reporter': {
                    'id': report.reporter.id if report.reporter else None,
                    'username': report.reporter.username if report.reporter else 'Anonymous'
                },
                'reported_user': {
                    'id': report.reported_user.id if report.reported_user else None,
                    'username': report.reported_user.username if report.reported_user else 'Unknown'
                },
                'priority': report.priority,
                'created_at': report.created_at.isoformat(),
                'age_hours': (datetime.utcnow() - report.created_at).total_seconds() / 3600
            })
        
        # Get queue statistics
        total_pending = Report.query.filter_by(status='pending').count()
        old_reports = Report.query.filter(
            Report.status == 'pending',
            Report.created_at < datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        high_priority = Report.query.filter(
            Report.status == 'pending',
            Report.priority == 'high'
        ).count()
        
        return jsonify({
            'reports': reports_data,
            'statistics': {
                'total_pending': total_pending,
                'old_reports': old_reports,
                'high_priority': high_priority,
                'average_age_hours': sum(r['age_hours'] for r in reports_data) / len(reports_data) if reports_data else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/system/maintenance', methods=['GET', 'POST'])
@admin_api_required
def system_maintenance():
    """Manage system maintenance windows."""
    try:
        current_user = session_service.get_current_user()
        
        if request.method == 'GET':
            # Get maintenance windows
            from app.models.admin import SystemMaintenanceWindow
            
            maintenance_windows = SystemMaintenanceWindow.query.filter(
                SystemMaintenanceWindow.scheduled_start >= datetime.utcnow() - timedelta(days=30)
            ).order_by(SystemMaintenanceWindow.scheduled_start.desc()).all()
            
            windows_data = []
            for window in maintenance_windows:
                windows_data.append({
                    'id': window.id,
                    'title': window.title,
                    'description': window.description,
                    'maintenance_type': window.maintenance_type,
                    'status': window.status,
                    'impact_level': window.impact_level,
                    'scheduled_start': window.scheduled_start.isoformat(),
                    'scheduled_end': window.scheduled_end.isoformat(),
                    'actual_start': window.actual_start.isoformat() if window.actual_start else None,
                    'actual_end': window.actual_end.isoformat() if window.actual_end else None,
                    'duration_minutes': window.duration_minutes,
                    'is_active': window.is_active,
                    'creator': window.creator.username if window.creator else 'Unknown',
                    'created_at': window.created_at.isoformat()
                })
            
            return jsonify({'maintenance_windows': windows_data})
        
        elif request.method == 'POST':
            # Create new maintenance window
            data = request.get_json()
            
            if not data or 'title' not in data or 'scheduled_start' not in data:
                return jsonify({'error': 'Missing required maintenance data'}), 400
            
            # Track maintenance window creation
            track_admin_action(current_user.id, 'system_maintenance', 'create_window',
                              metadata={'title': data['title']})
            
            from app.models.admin import SystemMaintenanceWindow
            
            window = SystemMaintenanceWindow(
                title=data['title'],
                description=data.get('description'),
                maintenance_type=data.get('maintenance_type', 'scheduled'),
                scheduled_start=datetime.fromisoformat(data['scheduled_start']),
                scheduled_end=datetime.fromisoformat(data['scheduled_end']),
                impact_level=data.get('impact_level', 'medium'),
                affected_services=data.get('affected_services', []),
                notify_users=data.get('notify_users', True),
                created_by=current_user.id
            )
            
            db.session.add(window)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'maintenance_id': window.id,
                'message': 'Maintenance window created successfully'
            })
        
    except Exception as e:
        if request.method == 'POST':
            db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/logs/admin-activities')
@admin_api_required
def get_admin_activities():
    """Get admin activity logs."""
    try:
        current_user = session_service.get_current_user()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        activity_type = request.args.get('activity_type')
        severity = request.args.get('severity')
        admin_id = request.args.get('admin_id')
        days = int(request.args.get('days', 7))
        
        # Track log access
        track_admin_action(current_user.id, 'audit', 'view_admin_logs')
        
        # Build query
        query = AdminActivity.query
        
        # Apply filters
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        if severity:
            query = query.filter_by(severity=severity)
        if admin_id:
            query = query.filter_by(admin_id=admin_id)
        
        # Date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AdminActivity.created_at >= start_date)
        
        # Paginate
        activities = query.order_by(AdminActivity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format activity data
        activities_data = []
        for activity in activities.items:
            activities_data.append({
                'id': activity.id,
                'admin': {
                    'id': activity.admin.id if activity.admin else None,
                    'username': activity.admin.username if activity.admin else 'Unknown'
                },
                'activity_type': activity.activity_type,
                'action': activity.action,
                'description': activity.description,
                'target_type': activity.target_type,
                'target_id': activity.target_id,
                'severity': activity.severity,
                'impact_scope': activity.impact_scope,
                'details': activity.details,
                'ip_address': activity.ip_address,
                'created_at': activity.created_at.isoformat()
            })
        
        return jsonify({
            'activities': activities_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': activities.total,
                'pages': activities.pages,
                'has_prev': activities.has_prev,
                'has_next': activities.has_next
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api_bp.route('/stats/overview')
@admin_api_required
def get_stats_overview():
    """Get comprehensive statistics overview."""
    try:
        current_user = session_service.get_current_user()
        
        # Track stats access
        track_admin_action(current_user.id, 'statistics', 'view_overview')
        
        # Get comprehensive overview
        overview = admin_dashboard_service.get_dashboard_overview(current_user.id)
        
        # Add additional statistics
        now = datetime.utcnow()
        
        # Database size statistics (approximate)
        db_stats = {
            'total_users': User.query.count(),
            'total_facts': Fact.query.count(),
            'total_comments': Comment.query.count(),
            'total_reports': Report.query.count(),
            'deleted_users': User.query.filter_by(is_deleted=True).count(),
            'deleted_facts': Fact.query.filter_by(is_deleted=True).count(),
            'deleted_comments': Comment.query.filter_by(is_deleted=True).count()
        }
        
        # Recent activity (last 24 hours)
        yesterday = now - timedelta(days=1)
        recent_activity = {
            'new_users': User.query.filter(User.created_at >= yesterday).count(),
            'new_facts': Fact.query.filter(Fact.created_at >= yesterday).count(),
            'new_comments': Comment.query.filter(Comment.created_at >= yesterday).count(),
            'new_reports': Report.query.filter(Report.created_at >= yesterday).count()
        }
        
        return jsonify({
            'overview': overview,
            'database_stats': db_stats,
            'recent_activity': recent_activity,
            'generated_at': now.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Error handlers for admin API
@admin_api_bp.errorhandler(401)
def api_unauthorized(error):
    """Handle 401 errors in admin API."""
    return jsonify({'error': 'Authentication required'}), 401


@admin_api_bp.errorhandler(403)
def api_forbidden(error):
    """Handle 403 errors in admin API."""
    return jsonify({'error': 'Admin privileges required'}), 403


@admin_api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors in admin API."""
    return jsonify({'error': 'API endpoint not found'}), 404


@admin_api_bp.errorhandler(500)
def api_server_error(error):
    """Handle 500 errors in admin API."""
    return jsonify({'error': 'Internal server error'}), 500
