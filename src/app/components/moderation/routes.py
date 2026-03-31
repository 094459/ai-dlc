"""
Moderation Component Routes

Provides API endpoints for moderation functionality including content moderation,
user management, workflow management, and moderation dashboard.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

from app.components.moderation.services import (
    ContentModerationService,
    UserModerationService,
    ModerationWorkflowService,
    ModerationDashboardService
)

# Create blueprint
moderation_bp = Blueprint('moderation', __name__, url_prefix='/moderation')


def moderator_required(f):
    """Decorator to require moderator or admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not (current_user.is_moderator or current_user.is_admin):
            return jsonify({'error': 'Moderator privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.is_admin:
            return jsonify({'error': 'Administrator privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


# Content Moderation Routes
@moderation_bp.route('/content/remove', methods=['POST'])
@login_required
@moderator_required
def remove_content():
    """Remove content (fact or comment)."""
    try:
        data = request.get_json()
        
        content_type = data.get('content_type')
        content_id = data.get('content_id')
        reason = data.get('reason')
        permanent = data.get('permanent', False)
        related_report_id = data.get('related_report_id')
        
        if not all([content_type, content_id, reason]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message = ContentModerationService.remove_content(
            content_type=content_type,
            content_id=content_id,
            moderator_id=current_user.id,
            reason=reason,
            permanent=permanent,
            related_report_id=related_report_id
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to remove content'}), 500


@moderation_bp.route('/content/restore', methods=['POST'])
@login_required
@moderator_required
def restore_content():
    """Restore previously removed content."""
    try:
        data = request.get_json()
        
        content_type = data.get('content_type')
        content_id = data.get('content_id')
        reason = data.get('reason')
        
        if not all([content_type, content_id, reason]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message = ContentModerationService.restore_content(
            content_type=content_type,
            content_id=content_id,
            moderator_id=current_user.id,
            reason=reason
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to restore content'}), 500


@moderation_bp.route('/content/hide', methods=['POST'])
@login_required
@moderator_required
def hide_content():
    """Hide content temporarily."""
    try:
        data = request.get_json()
        
        content_type = data.get('content_type')
        content_id = data.get('content_id')
        reason = data.get('reason')
        duration_hours = data.get('duration_hours')
        
        if not all([content_type, content_id, reason]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message = ContentModerationService.hide_content(
            content_type=content_type,
            content_id=content_id,
            moderator_id=current_user.id,
            reason=reason,
            duration_hours=duration_hours
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to hide content'}), 500


@moderation_bp.route('/content/history')
@login_required
@moderator_required
def get_content_moderation_history():
    """Get content moderation history."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        moderator_id = request.args.get('moderator_id')
        action_type = request.args.get('action_type')
        
        data = ContentModerationService.get_moderated_content(
            moderator_id=moderator_id,
            action_type=action_type,
            page=page,
            per_page=per_page
        )
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get content history'}), 500


# User Moderation Routes
@moderation_bp.route('/users/warn', methods=['POST'])
@login_required
@moderator_required
def warn_user():
    """Issue a warning to a user."""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        reason = data.get('reason')
        severity_level = data.get('severity_level', 1)
        related_content_type = data.get('related_content_type')
        related_content_id = data.get('related_content_id')
        related_report_id = data.get('related_report_id')
        
        if not all([user_id, reason]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message = UserModerationService.warn_user(
            user_id=user_id,
            moderator_id=current_user.id,
            reason=reason,
            severity_level=severity_level,
            related_content_type=related_content_type,
            related_content_id=related_content_id,
            related_report_id=related_report_id
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to warn user'}), 500


@moderation_bp.route('/users/suspend', methods=['POST'])
@login_required
@moderator_required
def suspend_user():
    """Suspend a user."""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        reason = data.get('reason')
        duration_hours = data.get('duration_hours')
        severity_level = data.get('severity_level', 2)
        related_report_id = data.get('related_report_id')
        
        if not all([user_id, reason, duration_hours]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message = UserModerationService.suspend_user(
            user_id=user_id,
            moderator_id=current_user.id,
            reason=reason,
            duration_hours=duration_hours,
            severity_level=severity_level,
            related_report_id=related_report_id
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to suspend user'}), 500


@moderation_bp.route('/users/ban', methods=['POST'])
@login_required
@admin_required  # Only admins can ban users
def ban_user():
    """Ban a user."""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        reason = data.get('reason')
        permanent = data.get('permanent', False)
        severity_level = data.get('severity_level', 5)
        related_report_id = data.get('related_report_id')
        
        if not all([user_id, reason]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message = UserModerationService.ban_user(
            user_id=user_id,
            moderator_id=current_user.id,
            reason=reason,
            permanent=permanent,
            severity_level=severity_level,
            related_report_id=related_report_id
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to ban user'}), 500


@moderation_bp.route('/users/lift-restriction', methods=['POST'])
@login_required
@moderator_required
def lift_user_restriction():
    """Lift user restrictions."""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        reason = data.get('reason')
        
        if not all([user_id, reason]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message = UserModerationService.lift_user_restriction(
            user_id=user_id,
            moderator_id=current_user.id,
            reason=reason
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to lift user restriction'}), 500


@moderation_bp.route('/users/<user_id>/history')
@login_required
@moderator_required
def get_user_moderation_history(user_id):
    """Get moderation history for a specific user."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        data = UserModerationService.get_user_moderation_history(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user history'}), 500


@moderation_bp.route('/users/attention')
@login_required
@moderator_required
def get_users_requiring_attention():
    """Get users who may require moderation attention."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        threshold = request.args.get('threshold', 3, type=int)
        
        data = UserModerationService.get_users_requiring_attention(
            threshold=threshold,
            page=page,
            per_page=per_page
        )
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get users requiring attention'}), 500


# Workflow Management Routes
@moderation_bp.route('/workflows', methods=['GET'])
@login_required
@moderator_required
def get_workflows():
    """Get moderation workflows."""
    try:
        trigger_type = request.args.get('trigger_type')
        workflows = ModerationWorkflowService.get_active_workflows(trigger_type)
        
        workflows_data = []
        for workflow in workflows:
            workflows_data.append({
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'trigger_type': workflow.trigger_type,
                'priority': workflow.priority,
                'execution_count': workflow.execution_count,
                'success_rate': workflow.success_rate,
                'is_active': workflow.is_active,
                'created_at': workflow.created_at.isoformat()
            })
        
        return jsonify({'workflows': workflows_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get workflows'}), 500


@moderation_bp.route('/workflows', methods=['POST'])
@login_required
@admin_required  # Only admins can create workflows
def create_workflow():
    """Create a new moderation workflow."""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        trigger_type = data.get('trigger_type')
        conditions = data.get('conditions', {})
        actions = data.get('actions', [])
        priority = data.get('priority', 1)
        
        if not all([name, trigger_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message, workflow = ModerationWorkflowService.create_workflow(
            name=name,
            description=description,
            trigger_type=trigger_type,
            conditions=conditions,
            actions=actions,
            moderator_id=current_user.id,
            priority=priority
        )
        
        if success:
            return jsonify({
                'message': message,
                'workflow_id': workflow.id
            }), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to create workflow'}), 500


# Dashboard Routes
@moderation_bp.route('/dashboard')
@login_required
@moderator_required
def dashboard():
    """Moderation dashboard."""
    try:
        time_period = request.args.get('time_period', 7, type=int)
        overview = ModerationDashboardService.get_moderation_overview(time_period)
        
        return jsonify(overview), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard data'}), 500


@moderation_bp.route('/')
@login_required
@moderator_required
def dashboard_view():
    """Render moderation dashboard template."""
    return render_template('moderation/dashboard.html')


@moderation_bp.route('/content')
@login_required
@moderator_required
def content_moderation_view():
    """Render content moderation interface."""
    return render_template('moderation/content/index.html')


@moderation_bp.route('/users')
@login_required
@moderator_required
def user_moderation_view():
    """Render user moderation interface."""
    return render_template('moderation/users/index.html')


@moderation_bp.route('/analytics/overview')
@login_required
@moderator_required
def analytics_overview():
    """Get moderation analytics overview."""
    try:
        time_period = request.args.get('time_period', 7, type=int)
        overview = ModerationDashboardService.get_moderation_overview(time_period)
        
        return jsonify(overview), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get analytics overview'}), 500
