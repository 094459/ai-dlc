"""
Admin Dashboard Routes for system administration and management.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from functools import wraps
from datetime import datetime, timedelta
from app.services.admin_dashboard_service import AdminDashboardService
from app.services.system_configuration_service import SystemConfigurationService
from app.services.user_management_service import UserManagementService
from app.services.system_health_service import SystemHealthService
from app.services.admin_integration_service import AdminIntegrationService
from app.components.auth.services import SessionValidationService
from app.components.analytics.tracking import AnalyticsTracker, track_admin_action


# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize services
admin_dashboard_service = AdminDashboardService()
config_service = SystemConfigurationService()
user_management_service = UserManagementService()
health_service = SystemHealthService()
integration_service = AdminIntegrationService()
session_service = SessionValidationService()


def admin_required(f):
    """Decorator to require admin authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        current_user = session_service.get_current_user()
        if not current_user:
            flash('Please log in to access the admin dashboard.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user has admin role
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        
        # Check if user is active
        if not current_user.is_active:
            flash('Your account is inactive. Please contact support.', 'error')
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Main admin dashboard with comprehensive overview."""
    try:
        current_user = session_service.get_current_user()
        
        # Track admin dashboard access
        AnalyticsTracker.track_page_view('admin_dashboard', 'admin')
        track_admin_action(current_user.id, 'dashboard_access', 'view_main_dashboard')
        
        # Get integrated dashboard data from all components
        integrated_data = integration_service.get_integrated_dashboard_data(current_user.id)
        
        # Get dashboard overview data (fallback to original if integration fails)
        if integrated_data.get('error'):
            overview_data = admin_dashboard_service.get_dashboard_overview(current_user.id)
        else:
            overview_data = integrated_data
        
        # Get system health status
        health_data = health_service.run_all_health_checks(current_user.id)
        
        # Add integration status to template context
        template_context = {
            'overview': overview_data,
            'health': health_data,
            'current_user': current_user,
            'integrated_data': integrated_data,
            'integration_status': 'success' if not integrated_data.get('error') else 'partial'
        }
        
        return render_template('admin/dashboard.html', **template_context)
        
    except Exception as e:
        # Log error and provide fallback
        track_admin_action(current_user.id, 'dashboard_error', 'dashboard_load_error', 
                          metadata={'error': str(e)})
        
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html',
                             overview={},
                             health={'overall_status': 'unknown'},
                             current_user=current_user,
                             integrated_data={},
                             integration_status='error')


@admin_bp.route('/api/overview')
@admin_required
def api_overview():
    """API endpoint for dashboard overview data (for AJAX updates)."""
    try:
        current_user = session_service.get_current_user()
        overview_data = admin_dashboard_service.get_dashboard_overview(current_user.id)
        return jsonify(overview_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/integrated-data')
@admin_required
def api_integrated_data():
    """API endpoint for integrated dashboard data from all components."""
    try:
        current_user = session_service.get_current_user()
        integrated_data = integration_service.get_integrated_dashboard_data(current_user.id)
        return jsonify(integrated_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/analytics-integration')
@admin_required
def api_analytics_integration():
    """API endpoint for analytics integration data."""
    try:
        current_user = session_service.get_current_user()
        analytics_data = integration_service.get_analytics_integration_data(current_user.id)
        return jsonify(analytics_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/moderation-integration')
@admin_required
def api_moderation_integration():
    """API endpoint for moderation integration data."""
    try:
        current_user = session_service.get_current_user()
        moderation_data = integration_service.get_moderation_integration_data(current_user.id)
        return jsonify(moderation_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/notifications-integration')
@admin_required
def api_notifications_integration():
    """API endpoint for notifications integration data."""
    try:
        current_user = session_service.get_current_user()
        notification_data = integration_service.get_notification_integration_data(current_user.id)
        return jsonify(notification_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/security-integration')
@admin_required
def api_security_integration():
    """API endpoint for security integration data."""
    try:
        current_user = session_service.get_current_user()
        security_data = integration_service.get_security_integration_data(current_user.id)
        return jsonify(security_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/health')
@admin_required
def api_health():
    """API endpoint for system health data (for real-time updates)."""
    try:
        current_user = session_service.get_current_user()
        health_data = health_service.run_all_health_checks(current_user.id)
        return jsonify(health_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/health/history')
@admin_required
def api_health_history():
    """API endpoint for health check history."""
    try:
        check_name = request.args.get('check_name')
        hours = int(request.args.get('hours', 24))
        
        history_data = health_service.get_health_history(check_name, hours)
        return jsonify({'history': history_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/metrics')
@admin_required
def api_system_metrics():
    """API endpoint for system metrics."""
    try:
        metrics_data = health_service.get_system_metrics()
        return jsonify(metrics_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users')
@admin_required
def users():
    """User management interface."""
    try:
        current_user = session_service.get_current_user()
        
        # Track user management access
        AnalyticsTracker.track_page_view('admin_users', 'admin')
        track_admin_action(current_user.id, 'user_management', 'view_users_page')
        
        # Get search and filter parameters
        query = request.args.get('q', '').strip()
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build filters
        filters = {}
        if role_filter:
            filters['role'] = role_filter
        if status_filter == 'active':
            filters['is_active'] = True
        elif status_filter == 'inactive':
            filters['is_active'] = False
        elif status_filter == 'suspended':
            filters['is_suspended'] = True
        elif status_filter == 'banned':
            filters['is_banned'] = True
        
        # Get user data
        user_data = user_management_service.search_users(
            query=query if query else None,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        # Get user management summary
        summary_data = admin_dashboard_service.get_user_management_summary(current_user.id)
        
        return render_template('admin/users.html',
                             users=user_data['users'],
                             pagination=user_data['pagination'],
                             summary=summary_data,
                             query=query,
                             role_filter=role_filter,
                             status_filter=status_filter,
                             current_user=current_user)
        
    except Exception as e:
        flash(f'Error loading user management: {str(e)}', 'error')
        return render_template('admin/users.html',
                             users=[],
                             pagination={'page': 1, 'pages': 0, 'total': 0},
                             summary={},
                             current_user=current_user)


@admin_bp.route('/users/<user_id>')
@admin_required
def user_details(user_id):
    """Detailed user information page."""
    try:
        current_user = session_service.get_current_user()
        
        # Track user details access
        track_admin_action(current_user.id, 'user_management', 'view_user_details', 
                          metadata={'target_user_id': user_id})
        
        # Get detailed user information
        user_data = user_management_service.get_user_details(user_id, current_user.id)
        
        if not user_data:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))
        
        return render_template('admin/user_details.html',
                             user_data=user_data,
                             current_user=current_user)
        
    except Exception as e:
        flash(f'Error loading user details: {str(e)}', 'error')
        return redirect(url_for('admin.users'))


@admin_bp.route('/api/users/bulk-update', methods=['POST'])
@admin_required
def api_bulk_update_users():
    """API endpoint for bulk user updates."""
    try:
        current_user = session_service.get_current_user()
        data = request.get_json()
        
        if not data or 'user_ids' not in data or 'updates' not in data:
            return jsonify({'error': 'Missing required data'}), 400
        
        # Track bulk update action
        track_admin_action(current_user.id, 'user_management', 'bulk_update_users',
                          metadata={
                              'user_count': len(data['user_ids']),
                              'updates': data['updates']
                          })
        
        # Perform bulk update
        result = user_management_service.bulk_update_users(
            data['user_ids'],
            data['updates'],
            current_user.id
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/bulk-suspend', methods=['POST'])
@admin_required
def api_bulk_suspend_users():
    """API endpoint for bulk user suspension."""
    try:
        current_user = session_service.get_current_user()
        data = request.get_json()
        
        if not data or 'user_ids' not in data or 'reason' not in data:
            return jsonify({'error': 'Missing required data'}), 400
        
        duration_hours = data.get('duration_hours', 24)
        
        # Track bulk suspension action
        track_admin_action(current_user.id, 'user_moderation', 'bulk_suspend_users',
                          metadata={
                              'user_count': len(data['user_ids']),
                              'duration_hours': duration_hours,
                              'reason': data['reason']
                          })
        
        # Perform bulk suspension
        result = user_management_service.suspend_users(
            data['user_ids'],
            data['reason'],
            duration_hours,
            current_user.id
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/export')
@admin_required
def api_export_users():
    """API endpoint for user data export."""
    try:
        current_user = session_service.get_current_user()
        
        # Get export filters
        filters = {}
        if request.args.get('role'):
            filters['role'] = request.args.get('role')
        if request.args.get('is_active'):
            filters['is_active'] = request.args.get('is_active').lower() == 'true'
        if request.args.get('created_after'):
            filters['created_after'] = datetime.fromisoformat(request.args.get('created_after'))
        if request.args.get('created_before'):
            filters['created_before'] = datetime.fromisoformat(request.args.get('created_before'))
        
        # Track export action
        track_admin_action(current_user.id, 'data_export', 'export_users',
                          metadata={'filters': filters})
        
        # Export user data
        export_data = user_management_service.export_user_data(filters, current_user.id)
        
        return jsonify({
            'data': export_data,
            'exported_at': datetime.utcnow().isoformat(),
            'exported_by': current_user.username,
            'total_records': len(export_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/configuration')
@admin_required
def configuration():
    """System configuration management interface."""
    try:
        current_user = session_service.get_current_user()
        
        # Track configuration access
        AnalyticsTracker.track_page_view('admin_configuration', 'admin')
        track_admin_action(current_user.id, 'configuration', 'view_config_page')
        
        # Get all configurations
        configs = config_service.get_all_configurations(include_private=True)
        
        # Group configurations by category (based on key prefixes)
        config_categories = {}
        for key, config in configs.items():
            # Determine category from key prefix or use 'general'
            if '_' in key:
                category = key.split('_')[0]
            else:
                category = 'general'
            
            if category not in config_categories:
                config_categories[category] = {}
            config_categories[category][key] = config
        
        return render_template('admin/configuration.html',
                             config_categories=config_categories,
                             current_user=current_user)
        
    except Exception as e:
        flash(f'Error loading configuration: {str(e)}', 'error')
        return render_template('admin/configuration.html',
                             config_categories={},
                             current_user=current_user)


@admin_bp.route('/api/configuration/<config_key>', methods=['GET', 'PUT'])
@admin_required
def api_configuration(config_key):
    """API endpoint for individual configuration management."""
    try:
        current_user = session_service.get_current_user()
        
        if request.method == 'GET':
            # Get configuration value
            value = config_service.get_configuration(config_key)
            return jsonify({'key': config_key, 'value': value})
        
        elif request.method == 'PUT':
            # Update configuration value
            data = request.get_json()
            if not data or 'value' not in data:
                return jsonify({'error': 'Missing value'}), 400
            
            # Validate configuration
            validation = config_service.validate_configuration(config_key, data['value'])
            if not validation['valid']:
                return jsonify({
                    'error': 'Validation failed',
                    'validation_errors': validation['errors']
                }), 400
            
            # Track configuration change
            track_admin_action(current_user.id, 'configuration', 'update_config',
                              metadata={
                                  'config_key': config_key,
                                  'new_value': str(data['value'])
                              })
            
            # Update configuration
            success = config_service.set_configuration(
                config_key,
                data['value'],
                current_user.id,
                data.get('description')
            )
            
            if success:
                return jsonify({'success': True, 'warnings': validation.get('warnings', [])})
            else:
                return jsonify({'error': 'Failed to update configuration'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/configuration/validate', methods=['POST'])
@admin_required
def api_validate_configuration():
    """API endpoint for configuration validation."""
    try:
        data = request.get_json()
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({'error': 'Missing key or value'}), 400
        
        validation = config_service.validate_configuration(data['key'], data['value'])
        return jsonify(validation)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/configuration/backup', methods=['POST'])
@admin_required
def api_backup_configuration():
    """API endpoint for configuration backup."""
    try:
        current_user = session_service.get_current_user()
        
        # Track backup action
        track_admin_action(current_user.id, 'configuration', 'create_backup')
        
        backup_data = config_service.backup_configurations(current_user.id)
        
        if backup_data:
            return jsonify({
                'success': True,
                'backup_data': backup_data,
                'created_at': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to create backup'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/configuration/restore', methods=['POST'])
@admin_required
def api_restore_configuration():
    """API endpoint for configuration restore."""
    try:
        current_user = session_service.get_current_user()
        data = request.get_json()
        
        if not data or 'backup_data' not in data:
            return jsonify({'error': 'Missing backup data'}), 400
        
        # Track restore action
        track_admin_action(current_user.id, 'configuration', 'restore_backup',
                          metadata={'severity': 'high'})
        
        success = config_service.restore_configurations(data['backup_data'], current_user.id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to restore configuration'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/configuration/initialize', methods=['POST'])
@admin_required
def api_initialize_configuration():
    """API endpoint for initializing default configurations."""
    try:
        current_user = session_service.get_current_user()
        
        # Track initialization action
        track_admin_action(current_user.id, 'configuration', 'initialize_defaults')
        
        success = config_service.initialize_default_configurations(current_user.id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to initialize configurations'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/health')
@admin_required
def health():
    """System health monitoring interface."""
    try:
        current_user = session_service.get_current_user()
        
        # Track health monitoring access
        AnalyticsTracker.track_page_view('admin_health', 'admin')
        track_admin_action(current_user.id, 'system_health', 'view_health_page')
        
        # Get comprehensive health data
        health_data = health_service.run_all_health_checks(current_user.id)
        
        # Get system metrics
        metrics_data = health_service.get_system_metrics()
        
        # Get recent health history (last 24 hours)
        history_data = health_service.get_health_history(hours=24)
        
        return render_template('admin/health.html',
                             health=health_data,
                             metrics=metrics_data,
                             history=history_data,
                             current_user=current_user)
        
    except Exception as e:
        flash(f'Error loading health monitoring: {str(e)}', 'error')
        return render_template('admin/health.html',
                             health={'overall_status': 'unknown'},
                             metrics={},
                             history=[],
                             current_user=current_user)


@admin_bp.route('/api/health/run-checks', methods=['POST'])
@admin_required
def api_run_health_checks():
    """API endpoint to manually trigger health checks."""
    try:
        current_user = session_service.get_current_user()
        
        # Track manual health check
        track_admin_action(current_user.id, 'system_health', 'manual_health_check')
        
        health_data = health_service.run_all_health_checks(current_user.id)
        return jsonify(health_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/send-notification', methods=['POST'])
@admin_required
def api_send_admin_notification():
    """API endpoint for sending notifications to admin users."""
    try:
        current_user = session_service.get_current_user()
        data = request.get_json()
        
        if not data or 'title' not in data or 'message' not in data:
            return jsonify({'error': 'Missing title or message'}), 400
        
        # Track notification sending
        track_admin_action(current_user.id, 'notification', 'send_admin_notification',
                          metadata={
                              'title': data['title'],
                              'type': data.get('type', 'admin')
                          })
        
        # Send notification through integration service
        success = integration_service.send_admin_notification(
            current_user.id,
            data['title'],
            data['message'],
            data.get('type', 'admin'),
            data.get('priority', 'normal')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Notification sent successfully'})
        else:
            return jsonify({'error': 'Failed to send notification'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/security-alert', methods=['POST'])
@admin_required
def api_trigger_security_alert():
    """API endpoint for triggering security alerts."""
    try:
        current_user = session_service.get_current_user()
        data = request.get_json()
        
        if not data or 'alert_type' not in data or 'description' not in data:
            return jsonify({'error': 'Missing alert_type or description'}), 400
        
        # Trigger security alert through integration service
        success = integration_service.trigger_security_alert(
            current_user.id,
            data['alert_type'],
            data['description'],
            data.get('severity', 'high')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Security alert triggered successfully'})
        else:
            return jsonify({'error': 'Failed to trigger security alert'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/reports')
@admin_required
def reports():
    """Admin reports and analytics interface with integrated data."""
    try:
        current_user = session_service.get_current_user()
        
        # Track reports access
        AnalyticsTracker.track_page_view('admin_reports', 'admin')
        track_admin_action(current_user.id, 'reports', 'view_reports_page')
        
        # Get integrated analytics data
        analytics_data = integration_service.get_analytics_integration_data(current_user.id)
        
        # Get user activity summary (fallback to original service)
        user_activity = user_management_service.get_user_activity_summary(days=30)
        
        # Get content management summary with integration
        content_summary = admin_dashboard_service.get_content_management_summary(current_user.id)
        
        # Add integrated analytics if available
        if analytics_data.get('status') == 'success':
            user_activity.update({
                'analytics_metrics': analytics_data.get('metrics', {}),
                'recent_events': analytics_data.get('recent_events', [])
            })
        
        return render_template('admin/reports.html',
                             user_activity=user_activity,
                             content_summary=content_summary,
                             analytics_data=analytics_data,
                             current_user=current_user)
        
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'error')
        return render_template('admin/reports.html',
                             user_activity={},
                             content_summary={},
                             analytics_data={},
                             current_user=current_user)
    """Admin reports and analytics interface."""
    try:
        current_user = session_service.get_current_user()
        
        # Track reports access
        AnalyticsTracker.track_page_view('admin_reports', 'admin')
        track_admin_action(current_user.id, 'reports', 'view_reports_page')
        
        # Get user activity summary
        user_activity = user_management_service.get_user_activity_summary(days=30)
        
        # Get content management summary
        content_summary = admin_dashboard_service.get_content_management_summary(current_user.id)
        
        return render_template('admin/reports.html',
                             user_activity=user_activity,
                             content_summary=content_summary,
                             current_user=current_user)
        
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'error')
        return render_template('admin/reports.html',
                             user_activity={},
                             content_summary={},
                             current_user=current_user)


# Error handlers for admin blueprint
@admin_bp.errorhandler(403)
def admin_forbidden(error):
    """Handle 403 errors in admin area."""
    flash('Access denied. Admin privileges required.', 'error')
    return redirect(url_for('main.index'))


@admin_bp.errorhandler(404)
def admin_not_found(error):
    """Handle 404 errors in admin area."""
    flash('Admin page not found.', 'error')
    return redirect(url_for('admin.dashboard'))


@admin_bp.errorhandler(500)
def admin_server_error(error):
    """Handle 500 errors in admin area."""
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('admin.dashboard'))
