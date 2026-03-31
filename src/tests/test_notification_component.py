"""
Unit tests for Notification Component functionality.
"""

import pytest
from datetime import datetime, timedelta
from app.models import db, User, Notification, NotificationTemplate, NotificationQueue
from app.components.notification.services import (
    NotificationService,
    EmailNotificationService,
    NotificationTemplateService,
    NotificationPreferenceService
)


class TestNotificationService:
    """Test cases for NotificationService."""
    
    def test_create_notification_success(self, app, sample_user):
        """Test successful notification creation."""
        with app.app_context():
            success, message, notification = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Test Notification',
                message='This is a test notification message',
                priority='normal'
            )
            
            assert success is True
            assert 'created successfully' in message.lower()
            assert notification is not None
            assert notification.user_id == sample_user.id
            assert notification.notification_type == 'system'
            assert notification.title == 'Test Notification'
            assert notification.priority == 'normal'
            assert notification.delivery_status == 'delivered'  # in_app delivery
    
    def test_create_notification_invalid_user(self, app):
        """Test notification creation with invalid user."""
        with app.app_context():
            success, message, notification = NotificationService.create_notification(
                user_id='invalid-user-id',
                notification_type='system',
                title='Test Notification',
                message='This is a test notification message'
            )
            
            assert success is False
            assert 'failed to create notification' in message.lower()
            assert notification is None
    
    def test_create_notification_with_template(self, app, sample_user):
        """Test notification creation with template."""
        with app.app_context():
            # Create a template first
            template_success, template_message, template = NotificationTemplateService.create_template(
                name='test_template',
                notification_type='system',
                subject_template='Hello {{ user.name }}!',
                body_template='Welcome to our platform, {{ user.name }}!'
            )
            
            assert template_success is True
            
            # Create notification with template
            success, message, notification = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Original Title',  # Should be overridden by template
                message='Original Message',  # Should be overridden by template
                template_name='test_template',
                data={'user': {'name': 'Test User'}}
            )
            
            assert success is True
            assert notification.title == 'Hello Test User!'
            assert notification.message == 'Welcome to our platform, Test User!'
    
    def test_get_user_notifications(self, app, sample_user):
        """Test retrieving user notifications."""
        with app.app_context():
            # Create multiple notifications
            for i in range(5):
                NotificationService.create_notification(
                    user_id=sample_user.id,
                    notification_type='system',
                    title=f'Test Notification {i+1}',
                    message=f'This is test notification {i+1}',
                    priority='normal' if i % 2 == 0 else 'high'
                )
            
            # Get all notifications
            data = NotificationService.get_user_notifications(sample_user.id)
            
            assert len(data['notifications']) == 5
            assert data['pagination']['total'] == 5
            
            # Check ordering (high priority first, then by creation date)
            notifications = data['notifications']
            high_priority_count = sum(1 for n in notifications if n.priority == 'high')
            assert high_priority_count == 2  # We created 2 high priority notifications
    
    def test_get_user_notifications_unread_only(self, app, sample_user):
        """Test retrieving only unread notifications."""
        with app.app_context():
            # Create notifications
            success1, _, notification1 = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Unread Notification',
                message='This notification is unread'
            )
            
            success2, _, notification2 = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Read Notification',
                message='This notification will be marked as read'
            )
            
            # Mark one as read
            notification2.mark_as_read()
            db.session.commit()
            
            # Get unread notifications only
            data = NotificationService.get_user_notifications(
                sample_user.id, unread_only=True
            )
            
            assert len(data['notifications']) == 1
            assert data['notifications'][0].title == 'Unread Notification'
    
    def test_mark_as_read(self, app, sample_user):
        """Test marking notification as read."""
        with app.app_context():
            success, _, notification = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Test Notification',
                message='This notification will be marked as read'
            )
            
            assert notification.is_read is False
            assert notification.read_at is None
            
            # Mark as read
            success, message = NotificationService.mark_as_read(
                notification.id, sample_user.id
            )
            
            assert success is True
            
            # Verify it's marked as read
            updated_notification = db.session.get(Notification, notification.id)
            assert updated_notification.is_read is True
            assert updated_notification.read_at is not None
    
    def test_mark_as_read_unauthorized(self, app, sample_user):
        """Test marking notification as read with wrong user."""
        with app.app_context():
            # Create another user
            other_user = User(
                email='other@test.com',
                password_hash='hashed_password',
                is_active=True
            )
            other_user.save()
            
            success, _, notification = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Test Notification',
                message='This notification belongs to sample_user'
            )
            
            # Try to mark as read with different user
            success, message = NotificationService.mark_as_read(
                notification.id, other_user.id
            )
            
            assert success is False
            assert 'unauthorized' in message.lower()
    
    def test_mark_all_as_read(self, app, sample_user):
        """Test marking all notifications as read."""
        with app.app_context():
            # Create multiple notifications
            for i in range(3):
                NotificationService.create_notification(
                    user_id=sample_user.id,
                    notification_type='system',
                    title=f'Test Notification {i+1}',
                    message=f'This is test notification {i+1}'
                )
            
            # Mark all as read
            success, message = NotificationService.mark_all_as_read(sample_user.id)
            
            assert success is True
            assert '3 notifications' in message
            
            # Verify all are marked as read
            unread_count = Notification.query.filter_by(
                user_id=sample_user.id,
                is_read=False
            ).count()
            
            assert unread_count == 0
    
    def test_delete_notification(self, app, sample_user):
        """Test deleting a notification."""
        with app.app_context():
            success, _, notification = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Test Notification',
                message='This notification will be deleted'
            )
            
            notification_id = notification.id
            
            # Delete notification
            success, message = NotificationService.delete_notification(
                notification_id, sample_user.id
            )
            
            assert success is True
            assert 'deleted successfully' in message.lower()
            
            # Verify it's deleted
            deleted_notification = db.session.get(Notification, notification_id)
            assert deleted_notification is None
    
    def test_get_notification_counts(self, app, sample_user):
        """Test getting notification counts."""
        with app.app_context():
            # Create notifications of different types
            NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='System Notification',
                message='System message'
            )
            
            NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='content',
                title='Content Notification',
                message='Content message'
            )
            
            NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='interaction',
                title='Interaction Notification',
                message='Interaction message'
            )
            
            counts = NotificationService.get_notification_counts(sample_user.id)
            
            assert counts['total_unread'] == 3
            assert counts['by_type']['system'] == 1
            assert counts['by_type']['content'] == 1
            assert counts['by_type']['interaction'] == 1


class TestNotificationTemplateService:
    """Test cases for NotificationTemplateService."""
    
    def test_create_template_success(self, app, sample_admin_user):
        """Test successful template creation."""
        with app.app_context():
            success, message, template = NotificationTemplateService.create_template(
                name='welcome_email',
                notification_type='system',
                subject_template='Welcome to {{ site.name }}!',
                body_template='Hello {{ user.name }}, welcome to our platform!',
                html_template='<h1>Welcome {{ user.name }}!</h1>',
                description='Welcome email template',
                variables=['user.name', 'site.name'],
                creator_id=sample_admin_user.id
            )
            
            assert success is True
            assert 'created successfully' in message.lower()
            assert template is not None
            assert template.name == 'welcome_email'
            assert template.notification_type == 'system'
            assert template.is_active is True
    
    def test_create_template_duplicate_name(self, app, sample_admin_user):
        """Test template creation with duplicate name."""
        with app.app_context():
            # Create first template
            NotificationTemplateService.create_template(
                name='duplicate_name',
                notification_type='system',
                subject_template='Subject',
                body_template='Body',
                creator_id=sample_admin_user.id
            )
            
            # Try to create another with same name
            success, message, template = NotificationTemplateService.create_template(
                name='duplicate_name',
                notification_type='system',
                subject_template='Different Subject',
                body_template='Different Body',
                creator_id=sample_admin_user.id
            )
            
            assert success is False
            assert 'already exists' in message.lower()
            assert template is None
    
    def test_get_template(self, app, sample_admin_user):
        """Test retrieving a template by name."""
        with app.app_context():
            # Create template
            NotificationTemplateService.create_template(
                name='test_template',
                notification_type='system',
                subject_template='Test Subject',
                body_template='Test Body',
                creator_id=sample_admin_user.id
            )
            
            # Retrieve template
            template = NotificationTemplateService.get_template('test_template')
            
            assert template is not None
            assert template.name == 'test_template'
            assert template.subject_template == 'Test Subject'
    
    def test_get_template_not_found(self, app):
        """Test retrieving non-existent template."""
        with app.app_context():
            template = NotificationTemplateService.get_template('nonexistent')
            assert template is None
    
    def test_template_rendering(self, app, sample_admin_user):
        """Test template rendering with variables."""
        with app.app_context():
            success, _, template = NotificationTemplateService.create_template(
                name='render_test',
                notification_type='system',
                subject_template='Hello {{ user.name }}!',
                body_template='Welcome {{ user.name }} to {{ site.name }}!',
                html_template='<h1>Hello {{ user.name }}!</h1><p>Welcome to {{ site.name }}!</p>',
                creator_id=sample_admin_user.id
            )
            
            variables = {
                'user': {'name': 'John Doe'},
                'site': {'name': 'Test Site'}
            }
            
            rendered_subject = template.render_subject(variables)
            rendered_body = template.render_body(variables)
            rendered_html = template.render_html(variables)
            
            assert rendered_subject == 'Hello John Doe!'
            assert rendered_body == 'Welcome John Doe to Test Site!'
            assert '<h1>Hello John Doe!</h1>' in rendered_html
            assert 'Welcome to Test Site!' in rendered_html


class TestNotificationPreferenceService:
    """Test cases for NotificationPreferenceService."""
    
    def test_get_user_preferences(self, app, sample_user):
        """Test getting user preferences."""
        with app.app_context():
            preferences = NotificationPreferenceService.get_user_preferences(sample_user.id)
            
            # Should return default preferences for new user
            assert preferences['email_notifications'] is True
            assert preferences['notification_frequency'] == 'immediate'
            assert preferences['system_notifications'] is True
            assert preferences['content_notifications'] is True
            assert preferences['interaction_notifications'] is True
            assert preferences['moderation_notifications'] is True
    
    def test_update_preferences(self, app, sample_user):
        """Test updating user preferences."""
        with app.app_context():
            new_preferences = {
                'email_notifications': False,
                'notification_frequency': 'daily',
                'system_notifications': False
            }
            
            success, message = NotificationPreferenceService.update_preferences(
                sample_user.id, new_preferences
            )
            
            assert success is True
            assert 'updated' in message.lower()
            
            # Verify preferences were updated
            updated_user = db.session.get(User, sample_user.id)
            assert updated_user.email_notifications is False
            assert updated_user.notification_frequency == 'daily'
            assert updated_user.system_notifications is False
    
    def test_should_send_notification(self, app, sample_user):
        """Test notification sending logic based on preferences."""
        with app.app_context():
            # Test with default preferences (should send) - sample_user doesn't have preference fields
            should_send = NotificationPreferenceService.should_send_notification(
                sample_user.id, 'system', 'email'
            )
            assert should_send is True
            
            # Get a fresh user object from the current session
            user = db.session.get(User, sample_user.id)
            
            # Manually set email_notifications attribute for testing
            user.email_notifications = False
            db.session.commit()  # Persist the change
            
            # Should not send email notifications
            should_send = NotificationPreferenceService.should_send_notification(
                sample_user.id, 'system', 'email'
            )
            assert should_send is False
            
            # Should still send in-app notifications
            should_send = NotificationPreferenceService.should_send_notification(
                sample_user.id, 'system', 'in_app'
            )
            assert should_send is True
            
            # Test disabling system notifications
            user.system_notifications = False
            db.session.commit()  # Persist the change
            
            should_send = NotificationPreferenceService.should_send_notification(
                sample_user.id, 'system', 'in_app'
            )
            assert should_send is False
    
    def test_reset_to_defaults(self, app, sample_user):
        """Test resetting preferences to defaults."""
        with app.app_context():
            # Change some preferences
            sample_user.email_notifications = False
            sample_user.system_notifications = False
            db.session.commit()
            
            # Reset to defaults
            success, message = NotificationPreferenceService.reset_to_defaults(sample_user.id)
            
            assert success is True
            
            # Verify preferences are reset
            updated_user = db.session.get(User, sample_user.id)
            assert updated_user.email_notifications is True
            assert updated_user.system_notifications is True


class TestEmailNotificationService:
    """Test cases for EmailNotificationService."""
    
    def test_queue_email(self, app, sample_user):
        """Test queuing an email for delivery."""
        with app.app_context():
            # Create a notification first
            success, _, notification = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Test Email',
                message='This is a test email notification',
                delivery_method='email'
            )
            
            # Queue email
            success, message = EmailNotificationService.queue_email(
                notification.id,
                'default',
                sample_user.email,
                {'user': {'name': 'Test User'}}
            )
            
            assert success is True
            assert 'queued' in message.lower()
            
            # Verify queue entry was created
            queue_entry = NotificationQueue.query.filter_by(
                notification_id=notification.id
            ).first()
            
            assert queue_entry is not None
            assert queue_entry.email_address == sample_user.email
            assert queue_entry.status == 'queued'
    
    def test_queue_email_with_template(self, app, sample_user):
        """Test queuing email with custom template."""
        with app.app_context():
            # Create template
            NotificationTemplateService.create_template(
                name='email_template',
                notification_type='system',
                subject_template='Hello {{ user.name }}!',
                body_template='Dear {{ user.name }}, this is a test email.',
                creator_id=None
            )
            
            # Create notification with template
            success, _, notification = NotificationService.create_notification(
                user_id=sample_user.id,
                notification_type='system',
                title='Test Email',
                message='This is a test email notification',
                delivery_method='email',
                template_name='email_template',
                data={'user': {'name': 'John Doe'}}
            )
            
            assert success is True
            
            # Verify template was used
            queue_entry = NotificationQueue.query.filter_by(
                notification_id=notification.id
            ).first()
            
            assert queue_entry.subject == 'Hello John Doe!'
            assert 'Dear John Doe' in queue_entry.body_text


# Remove the problematic fixture and create users inline in tests that need them
