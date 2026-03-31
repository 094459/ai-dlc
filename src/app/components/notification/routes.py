"""
Notification Component Routes

Provides API endpoints for notification functionality including notification management,
user preferences, template management, and email queue administration.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from functools import wraps

from app.components.notification.services import (
    NotificationService,
    EmailNotificationService,
    NotificationTemplateService,
    NotificationPreferenceService
)

# Create blueprint
notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')


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


# Notification Management Routes
@notification_bp.route('/', methods=['GET'])
@login_required
def get_notifications():
    """Get user notifications."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notification_type = request.args.get('type')
        
        data = NotificationService.get_user_notifications(
            user_id=current_user.id,
            unread_only=unread_only,
            notification_type=notification_type,
            page=page,
            per_page=per_page
        )
        
        # Convert notifications to JSON-serializable format
        notifications_data = []
        for notification in data['notifications']:
            notifications_data.append({
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'related_content_type': notification.related_content_type,
                'related_content_id': notification.related_content_id,
                'expires_at': notification.expires_at.isoformat() if notification.expires_at else None
            })
        
        return jsonify({
            'notifications': notifications_data,
            'pagination': data['pagination']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get notifications'}), 500


@notification_bp.route('/count', methods=['GET'])
@login_required
def get_notification_count():
    """Get notification counts."""
    try:
        counts = NotificationService.get_notification_counts(current_user.id)
        return jsonify(counts), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get notification counts'}), 500


@notification_bp.route('/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Mark notifications as read."""
    try:
        data = request.get_json()
        
        if 'notification_id' in data:
            # Mark single notification as read
            success, message = NotificationService.mark_as_read(
                data['notification_id'], current_user.id
            )
        elif data.get('mark_all', False):
            # Mark all notifications as read
            success, message = NotificationService.mark_all_as_read(current_user.id)
        else:
            return jsonify({'error': 'Invalid request data'}), 400
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to mark notifications as read'}), 500


@notification_bp.route('/<notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """Delete a notification."""
    try:
        success, message = NotificationService.delete_notification(
            notification_id, current_user.id
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to delete notification'}), 500


# Notification Preferences Routes
@notification_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get user notification preferences."""
    try:
        preferences = NotificationPreferenceService.get_user_preferences(current_user.id)
        return jsonify(preferences), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get preferences'}), 500


@notification_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """Update user notification preferences."""
    try:
        data = request.get_json()
        
        success, message = NotificationPreferenceService.update_preferences(
            current_user.id, data
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to update preferences'}), 500


@notification_bp.route('/preferences/reset', methods=['POST'])
@login_required
def reset_preferences():
    """Reset preferences to defaults."""
    try:
        success, message = NotificationPreferenceService.reset_to_defaults(current_user.id)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to reset preferences'}), 500


# Admin Template Management Routes
@notification_bp.route('/admin/templates', methods=['GET'])
@login_required
@admin_required
def get_templates():
    """Get notification templates (admin only)."""
    try:
        notification_type = request.args.get('type')
        
        if notification_type:
            templates = NotificationTemplateService.get_templates_by_type(notification_type)
        else:
            from app.models import NotificationTemplate
            templates = NotificationTemplate.query.filter_by(is_active=True).all()
        
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'notification_type': template.notification_type,
                'subject_template': template.subject_template,
                'body_template': template.body_template,
                'html_template': template.html_template,
                'variables': template.variables,
                'usage_count': template.usage_count,
                'last_used': template.last_used.isoformat() if template.last_used else None,
                'created_at': template.created_at.isoformat()
            })
        
        return jsonify({'templates': templates_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get templates'}), 500


@notification_bp.route('/admin/templates', methods=['POST'])
@login_required
@admin_required
def create_template():
    """Create notification template (admin only)."""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'notification_type', 'subject_template', 'body_template']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        success, message, template = NotificationTemplateService.create_template(
            name=data['name'],
            notification_type=data['notification_type'],
            subject_template=data['subject_template'],
            body_template=data['body_template'],
            html_template=data.get('html_template'),
            description=data.get('description'),
            variables=data.get('variables', []),
            creator_id=current_user.id
        )
        
        if success:
            return jsonify({
                'message': message,
                'template_id': template.id
            }), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to create template'}), 500


@notification_bp.route('/admin/templates/<template_id>', methods=['PUT'])
@login_required
@admin_required
def update_template(template_id):
    """Update notification template (admin only)."""
    try:
        data = request.get_json()
        
        success, message = NotificationTemplateService.update_template(
            template_id, **data
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to update template'}), 500


@notification_bp.route('/admin/templates/defaults', methods=['POST'])
@login_required
@admin_required
def create_default_templates():
    """Create default notification templates (admin only)."""
    try:
        defaults = NotificationTemplateService.get_default_templates()
        created_count = 0
        
        for template_name, template_data in defaults.items():
            success, message, template = NotificationTemplateService.create_template(
                name=template_name,
                creator_id=current_user.id,
                **template_data
            )
            if success:
                created_count += 1
        
        return jsonify({
            'message': f'Created {created_count} default templates'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to create default templates'}), 500


# Admin Email Queue Management Routes
@notification_bp.route('/admin/email-queue', methods=['GET'])
@login_required
@admin_required
def get_email_queue():
    """Get email queue status (admin only)."""
    try:
        from app.models import NotificationQueue
        
        # Get queue statistics
        total_queued = NotificationQueue.query.filter_by(status='queued').count()
        total_sending = NotificationQueue.query.filter_by(status='sending').count()
        total_sent = NotificationQueue.query.filter_by(status='sent').count()
        total_failed = NotificationQueue.query.filter_by(status='failed').count()
        
        # Get recent queue items
        recent_items = NotificationQueue.query.order_by(
            NotificationQueue.created_at.desc()
        ).limit(20).all()
        
        queue_items = []
        for item in recent_items:
            queue_items.append({
                'id': item.id,
                'email_address': item.email_address,
                'subject': item.subject,
                'status': item.status,
                'priority': item.priority,
                'attempts': item.attempts,
                'max_attempts': item.max_attempts,
                'scheduled_for': item.scheduled_for.isoformat(),
                'sent_at': item.sent_at.isoformat() if item.sent_at else None,
                'error_message': item.error_message,
                'created_at': item.created_at.isoformat()
            })
        
        return jsonify({
            'statistics': {
                'queued': total_queued,
                'sending': total_sending,
                'sent': total_sent,
                'failed': total_failed
            },
            'recent_items': queue_items
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get email queue'}), 500


@notification_bp.route('/admin/email-queue/process', methods=['POST'])
@login_required
@admin_required
def process_email_queue():
    """Process email queue manually (admin only)."""
    try:
        batch_size = request.json.get('batch_size', 10) if request.json else 10
        
        sent_count, failed_count = EmailNotificationService.send_queued_emails(batch_size)
        
        return jsonify({
            'message': f'Processed {sent_count + failed_count} emails',
            'sent': sent_count,
            'failed': failed_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process email queue'}), 500


@notification_bp.route('/admin/email-queue/retry', methods=['POST'])
@login_required
@admin_required
def retry_failed_emails():
    """Retry failed emails (admin only)."""
    try:
        retry_count = EmailNotificationService.retry_failed_emails()
        
        return jsonify({
            'message': f'Queued {retry_count} failed emails for retry'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retry failed emails'}), 500


# Utility Routes
@notification_bp.route('/test', methods=['POST'])
@login_required
@admin_required
def send_test_notification():
    """Send test notification (admin only)."""
    try:
        data = request.get_json()
        
        success, message, notification = NotificationService.create_notification(
            user_id=current_user.id,
            notification_type='system',
            title=data.get('title', 'Test Notification'),
            message=data.get('message', 'This is a test notification.'),
            priority=data.get('priority', 'normal'),
            delivery_method=data.get('delivery_method', 'in_app')
        )
        
        if success:
            return jsonify({
                'message': 'Test notification sent',
                'notification_id': notification.id
            }), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to send test notification'}), 500
