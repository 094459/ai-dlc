"""
Notification Component Services

Provides comprehensive notification functionality for in-app and email notifications.
"""

import logging
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import (
    User, Notification, NotificationTemplate, NotificationQueue, 
    UserNotificationPreferences
)
from app.components.security.services import AuditService

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification creation and management."""
    
    @staticmethod
    def create_notification(user_id: str, notification_type: str, title: str, 
                          message: str, data: Dict[str, Any] = None, priority: str = 'normal',
                          delivery_method: str = 'in_app', template_name: str = None,
                          related_content_type: str = None, related_content_id: str = None,
                          expires_at: datetime = None) -> Tuple[bool, str, Optional[Notification]]:
        """
        Create a new notification for a user.
        
        Args:
            user_id: ID of the user to notify
            notification_type: Type of notification (system, content, interaction, moderation)
            title: Notification title
            message: Notification message
            data: Additional data for template rendering
            priority: Priority level (low, normal, high, urgent)
            delivery_method: How to deliver (in_app, email, both)
            template_name: Template to use for rendering
            related_content_type: Type of related content
            related_content_id: ID of related content
            expires_at: When notification expires
            
        Returns:
            Tuple of (success: bool, message: str, notification: Notification or None)
        """
        try:
            # Validate user exists
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found", None
            
            # Check user preferences
            if not NotificationPreferenceService.should_send_notification(
                user_id, notification_type, delivery_method
            ):
                return False, "User has disabled this notification type", None
            
            # Get template if specified
            template = None
            template_id = None
            if template_name:
                template = NotificationTemplateService.get_template(template_name)
                if template:
                    template_id = template.id
                    # Render template if data provided
                    if data:
                        title = template.render_subject(data)
                        message = template.render_body(data)
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                type=notification_type,  # For backward compatibility
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                template_id=template_id,
                data=data or {},
                delivery_method=delivery_method,
                related_content_type=related_content_type,
                related_content_id=related_content_id,
                expires_at=expires_at,
                delivery_status='pending'
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Send notification based on delivery method
            if delivery_method in ['in_app', 'both']:
                notification.delivery_status = 'delivered'
                notification.delivered_at = datetime.utcnow()
            
            if delivery_method in ['email', 'both']:
                # Queue email for delivery
                success, email_message = EmailNotificationService.queue_email(
                    notification.id, template_name or 'default', user.email, data or {}
                )
                if not success:
                    logger.warning(f"Failed to queue email for notification {notification.id}: {email_message}")
            
            db.session.commit()
            
            # Log audit trail
            AuditService.log_action(
                user_id=user_id,
                action_type='notification_created',
                resource_type='notification',
                resource_id=notification.id,
                new_values={'type': notification_type, 'title': title, 'delivery_method': delivery_method}
            )
            
            return True, "Notification created successfully", notification
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating notification: {str(e)}")
            return False, "Failed to create notification", None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            return False, "Failed to create notification", None
    
    @staticmethod
    def get_user_notifications(user_id: str, unread_only: bool = False, 
                             notification_type: str = None, page: int = 1, 
                             per_page: int = 20) -> Dict[str, Any]:
        """
        Get notifications for a user with filtering and pagination.
        
        Args:
            user_id: ID of the user
            unread_only: Only return unread notifications
            notification_type: Filter by notification type
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Dictionary with notifications and pagination info
        """
        try:
            query = Notification.query.filter(Notification.user_id == user_id)
            
            # Filter by read status
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            # Filter by type
            if notification_type:
                query = query.filter(Notification.notification_type == notification_type)
            
            # Filter out expired notifications
            query = query.filter(
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
            
            # Order by priority and creation date
            query = query.order_by(
                desc(Notification.priority),
                desc(Notification.created_at)
            )
            
            # Paginate results
            paginated = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'notifications': paginated.items,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated.total,
                    'pages': paginated.pages,
                    'has_prev': paginated.has_prev,
                    'has_next': paginated.has_next
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return {
                'notifications': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0,
                    'has_prev': False,
                    'has_next': False
                }
            }
    
    @staticmethod
    def mark_as_read(notification_id: str, user_id: str) -> Tuple[bool, str]:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of the notification
            user_id: ID of the user (for security)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            notification = db.session.get(Notification, notification_id)
            if not notification:
                return False, "Notification not found"
            
            if notification.user_id != user_id:
                return False, "Unauthorized access to notification"
            
            if not notification.is_read:
                notification.mark_as_read()
                db.session.commit()
            
            return True, "Notification marked as read"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error marking notification as read: {str(e)}")
            return False, "Failed to mark notification as read"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error marking notification as read: {str(e)}")
            return False, "Failed to mark notification as read"
    
    @staticmethod
    def mark_all_as_read(user_id: str) -> Tuple[bool, str]:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            notifications = Notification.query.filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).all()
            
            count = 0
            for notification in notifications:
                notification.mark_as_read()
                count += 1
            
            db.session.commit()
            
            return True, f"Marked {count} notifications as read"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error marking all notifications as read: {str(e)}")
            return False, "Failed to mark notifications as read"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return False, "Failed to mark notifications as read"
    
    @staticmethod
    def delete_notification(notification_id: str, user_id: str) -> Tuple[bool, str]:
        """
        Delete a notification.
        
        Args:
            notification_id: ID of the notification
            user_id: ID of the user (for security)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            notification = db.session.get(Notification, notification_id)
            if not notification:
                return False, "Notification not found"
            
            if notification.user_id != user_id:
                return False, "Unauthorized access to notification"
            
            db.session.delete(notification)
            db.session.commit()
            
            return True, "Notification deleted successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error deleting notification: {str(e)}")
            return False, "Failed to delete notification"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting notification: {str(e)}")
            return False, "Failed to delete notification"
    
    @staticmethod
    def get_notification_counts(user_id: str) -> Dict[str, int]:
        """
        Get notification counts for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with notification counts
        """
        try:
            # Total unread count
            unread_count = Notification.query.filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
            ).count()
            
            # Count by type
            type_counts = db.session.query(
                Notification.notification_type,
                func.count(Notification.id).label('count')
            ).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
            ).group_by(Notification.notification_type).all()
            
            counts = {
                'total_unread': unread_count,
                'by_type': {type_name: count for type_name, count in type_counts}
            }
            
            return counts
            
        except Exception as e:
            logger.error(f"Error getting notification counts: {str(e)}")
            return {
                'total_unread': 0,
                'by_type': {}
            }
    
    @staticmethod
    def cleanup_expired_notifications() -> int:
        """
        Clean up expired notifications.
        
        Returns:
            Number of notifications cleaned up
        """
        try:
            expired_notifications = Notification.query.filter(
                and_(
                    Notification.expires_at.isnot(None),
                    Notification.expires_at <= datetime.utcnow()
                )
            ).all()
            
            count = len(expired_notifications)
            
            for notification in expired_notifications:
                db.session.delete(notification)
            
            db.session.commit()
            
            logger.info(f"Cleaned up {count} expired notifications")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cleaning up expired notifications: {str(e)}")
            return 0


class EmailNotificationService:
    """Service for email notification sending and queue management."""
    
    # SMTP configuration (would typically come from environment variables)
    SMTP_HOST = 'localhost'
    SMTP_PORT = 587
    SMTP_USERNAME = None
    SMTP_PASSWORD = None
    SMTP_USE_TLS = True
    FROM_EMAIL = 'noreply@factcheck.com'
    
    @staticmethod
    def configure_smtp(host: str, port: int, username: str = None, 
                      password: str = None, use_tls: bool = True, from_email: str = None):
        """Configure SMTP settings."""
        EmailNotificationService.SMTP_HOST = host
        EmailNotificationService.SMTP_PORT = port
        EmailNotificationService.SMTP_USERNAME = username
        EmailNotificationService.SMTP_PASSWORD = password
        EmailNotificationService.SMTP_USE_TLS = use_tls
        if from_email:
            EmailNotificationService.FROM_EMAIL = from_email
    
    @staticmethod
    def queue_email(notification_id: str, template_name: str, recipient_email: str, 
                   template_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Queue an email for delivery.
        
        Args:
            notification_id: ID of the notification
            template_name: Name of the email template
            recipient_email: Recipient email address
            template_data: Data for template rendering
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get notification for priority
            notification = db.session.get(Notification, notification_id)
            if not notification:
                return False, "Notification not found"
            
            # Get template
            template = NotificationTemplateService.get_template(template_name)
            if not template:
                # Use default template
                subject = notification.title
                body_text = notification.message
                body_html = None
            else:
                subject = template.render_subject(template_data)
                body_text = template.render_body(template_data)
                body_html = template.render_html(template_data)
                template.increment_usage()
            
            # Create queue entry
            priority_map = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
            priority = priority_map.get(notification.priority, 2)
            
            queue_entry = NotificationQueue(
                notification_id=notification_id,
                email_address=recipient_email,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                priority=priority,
                scheduled_for=notification.scheduled_for or datetime.utcnow()
            )
            
            db.session.add(queue_entry)
            db.session.commit()
            
            return True, "Email queued for delivery"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error queuing email: {str(e)}")
            return False, "Failed to queue email"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error queuing email: {str(e)}")
            return False, "Failed to queue email"
    
    @staticmethod
    def send_queued_emails(batch_size: int = 10) -> Tuple[int, int]:
        """
        Send queued emails in batches.
        
        Args:
            batch_size: Number of emails to send in one batch
            
        Returns:
            Tuple of (sent_count: int, failed_count: int)
        """
        try:
            # Get ready emails ordered by priority and scheduled time
            ready_emails = NotificationQueue.query.filter(
                NotificationQueue.status == 'queued'
            ).filter(
                NotificationQueue.scheduled_for <= datetime.utcnow()
            ).filter(
                NotificationQueue.attempts < NotificationQueue.max_attempts
            ).order_by(
                desc(NotificationQueue.priority),
                NotificationQueue.scheduled_for
            ).limit(batch_size).all()
            
            if not ready_emails:
                return 0, 0
            
            sent_count = 0
            failed_count = 0
            
            # Initialize SMTP connection
            smtp_server = None
            try:
                smtp_server = smtplib.SMTP(
                    EmailNotificationService.SMTP_HOST, 
                    EmailNotificationService.SMTP_PORT
                )
                
                if EmailNotificationService.SMTP_USE_TLS:
                    smtp_server.starttls()
                
                if EmailNotificationService.SMTP_USERNAME:
                    smtp_server.login(
                        EmailNotificationService.SMTP_USERNAME,
                        EmailNotificationService.SMTP_PASSWORD
                    )
                
                # Send emails
                for email in ready_emails:
                    try:
                        email.status = 'sending'
                        db.session.commit()
                        
                        # Create email message
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = email.subject
                        msg['From'] = EmailNotificationService.FROM_EMAIL
                        msg['To'] = email.email_address
                        
                        # Add text part
                        text_part = MIMEText(email.body_text, 'plain')
                        msg.attach(text_part)
                        
                        # Add HTML part if available
                        if email.body_html:
                            html_part = MIMEText(email.body_html, 'html')
                            msg.attach(html_part)
                        
                        # Send email
                        smtp_server.send_message(msg)
                        
                        # Mark as sent
                        email.mark_as_sent()
                        sent_count += 1
                        
                    except Exception as e:
                        error_message = str(e)
                        logger.error(f"Failed to send email {email.id}: {error_message}")
                        email.mark_as_failed(error_message)
                        failed_count += 1
                    
                    db.session.commit()
                
            finally:
                if smtp_server:
                    smtp_server.quit()
            
            return sent_count, failed_count
            
        except Exception as e:
            logger.error(f"Error sending queued emails: {str(e)}")
            return 0, 0
    
    @staticmethod
    def retry_failed_emails() -> int:
        """
        Retry failed emails that can be retried.
        
        Returns:
            Number of emails queued for retry
        """
        try:
            failed_emails = NotificationQueue.query.filter(
                and_(
                    NotificationQueue.status == 'failed',
                    NotificationQueue.attempts < NotificationQueue.max_attempts
                )
            ).all()
            
            retry_count = 0
            for email in failed_emails:
                email.status = 'queued'
                email.scheduled_for = datetime.utcnow() + timedelta(minutes=30)  # Retry in 30 minutes
                retry_count += 1
            
            db.session.commit()
            
            logger.info(f"Queued {retry_count} failed emails for retry")
            return retry_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error retrying failed emails: {str(e)}")
            return 0

class NotificationTemplateService:
    """Service for notification template management."""
    
    @staticmethod
    def create_template(name: str, notification_type: str, subject_template: str,
                       body_template: str, html_template: str = None, 
                       description: str = None, variables: List[str] = None,
                       creator_id: str = None) -> Tuple[bool, str, Optional[NotificationTemplate]]:
        """
        Create a new notification template.
        
        Args:
            name: Unique template name
            notification_type: Type of notification this template is for
            subject_template: Subject line template
            body_template: Body text template
            html_template: HTML body template (optional)
            description: Template description
            variables: List of available variables
            creator_id: ID of the user creating the template
            
        Returns:
            Tuple of (success: bool, message: str, template: NotificationTemplate or None)
        """
        try:
            # Check if template name already exists
            existing = NotificationTemplate.query.filter_by(name=name).first()
            if existing:
                return False, "Template name already exists", None
            
            # Create template
            template = NotificationTemplate(
                name=name,
                description=description,
                notification_type=notification_type,
                subject_template=subject_template,
                body_template=body_template,
                html_template=html_template,
                variables=variables or [],
                created_by=creator_id,
                is_active=True
            )
            
            db.session.add(template)
            db.session.commit()
            
            return True, "Template created successfully", template
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating template: {str(e)}")
            return False, "Failed to create template", None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating template: {str(e)}")
            return False, "Failed to create template", None
    
    @staticmethod
    def get_template(name: str) -> Optional[NotificationTemplate]:
        """
        Get a template by name.
        
        Args:
            name: Template name
            
        Returns:
            NotificationTemplate or None
        """
        try:
            return NotificationTemplate.query.filter(
                and_(
                    NotificationTemplate.name == name,
                    NotificationTemplate.is_active == True
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return None
    
    @staticmethod
    def get_templates_by_type(notification_type: str) -> List[NotificationTemplate]:
        """
        Get all active templates for a notification type.
        
        Args:
            notification_type: Type of notification
            
        Returns:
            List of NotificationTemplate objects
        """
        try:
            return NotificationTemplate.query.filter(
                and_(
                    NotificationTemplate.notification_type == notification_type,
                    NotificationTemplate.is_active == True
                )
            ).order_by(NotificationTemplate.name).all()
            
        except Exception as e:
            logger.error(f"Error getting templates by type: {str(e)}")
            return []
    
    @staticmethod
    def update_template(template_id: str, **kwargs) -> Tuple[bool, str]:
        """
        Update a template.
        
        Args:
            template_id: ID of the template to update
            **kwargs: Fields to update
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            template = db.session.get(NotificationTemplate, template_id)
            if not template:
                return False, "Template not found"
            
            # Update allowed fields
            allowed_fields = [
                'description', 'subject_template', 'body_template', 
                'html_template', 'variables', 'is_active'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(template, field, value)
            
            db.session.commit()
            
            return True, "Template updated successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error updating template: {str(e)}")
            return False, "Failed to update template"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating template: {str(e)}")
            return False, "Failed to update template"
    
    @staticmethod
    def get_default_templates() -> Dict[str, Dict[str, str]]:
        """
        Get default template definitions.
        
        Returns:
            Dictionary of default templates
        """
        return {
            'welcome': {
                'notification_type': 'system',
                'subject_template': 'Welcome to {{ site.name }}!',
                'body_template': 'Hello {{ user.name }},\n\nWelcome to {{ site.name }}! We\'re excited to have you join our fact-checking community.',
                'html_template': '<h2>Welcome to {{ site.name }}!</h2><p>Hello {{ user.name }},</p><p>Welcome to {{ site.name }}! We\'re excited to have you join our fact-checking community.</p>',
                'variables': ['user.name', 'site.name', 'site.url']
            },
            'comment_notification': {
                'notification_type': 'interaction',
                'subject_template': 'New comment on your fact: {{ content.title }}',
                'body_template': 'Hello {{ user.name }},\n\n{{ commenter.name }} commented on your fact "{{ content.title }}":\n\n"{{ comment.text }}"\n\nView the comment: {{ content.url }}',
                'html_template': '<p>Hello {{ user.name }},</p><p>{{ commenter.name }} commented on your fact "{{ content.title }}":</p><blockquote>{{ comment.text }}</blockquote><p><a href="{{ content.url }}">View the comment</a></p>',
                'variables': ['user.name', 'commenter.name', 'content.title', 'content.url', 'comment.text']
            },
            'moderation_warning': {
                'notification_type': 'moderation',
                'subject_template': 'Warning issued for your account',
                'body_template': 'Hello {{ user.name }},\n\nA warning has been issued for your account.\n\nReason: {{ action.reason }}\n\nPlease review our community guidelines to avoid future issues.',
                'html_template': '<p>Hello {{ user.name }},</p><p>A warning has been issued for your account.</p><p><strong>Reason:</strong> {{ action.reason }}</p><p>Please review our community guidelines to avoid future issues.</p>',
                'variables': ['user.name', 'action.reason', 'action.type']
            }
        }


class NotificationPreferenceService:
    """Service for managing user notification preferences."""
    
    @staticmethod
    def get_user_preferences(user_id: str) -> Dict[str, Any]:
        """
        Get notification preferences for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with user preferences
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return NotificationPreferenceService.get_default_preferences()
            
            return {
                'email_notifications': user.email_notifications,
                'notification_frequency': user.notification_frequency,
                'system_notifications': user.system_notifications,
                'content_notifications': user.content_notifications,
                'interaction_notifications': user.interaction_notifications,
                'moderation_notifications': user.moderation_notifications
            }
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return NotificationPreferenceService.get_default_preferences()
    
    @staticmethod
    def update_preferences(user_id: str, preferences: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update user notification preferences.
        
        Args:
            user_id: ID of the user
            preferences: Dictionary of preferences to update
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            # Update allowed preference fields
            allowed_fields = [
                'email_notifications', 'notification_frequency',
                'system_notifications', 'content_notifications',
                'interaction_notifications', 'moderation_notifications'
            ]
            
            updated_count = 0
            for field, value in preferences.items():
                if field in allowed_fields:
                    setattr(user, field, value)
                    updated_count += 1
            
            db.session.commit()
            
            return True, f"Updated {updated_count} preferences"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error updating preferences: {str(e)}")
            return False, "Failed to update preferences"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating preferences: {str(e)}")
            return False, "Failed to update preferences"
    
    @staticmethod
    def get_default_preferences() -> Dict[str, Any]:
        """
        Get default notification preferences.
        
        Returns:
            Dictionary with default preferences
        """
        return {
            'email_notifications': True,
            'notification_frequency': 'immediate',
            'system_notifications': True,
            'content_notifications': True,
            'interaction_notifications': True,
            'moderation_notifications': True
        }
    
    @staticmethod
    def should_send_notification(user_id: str, notification_type: str, 
                               delivery_method: str) -> bool:
        """
        Check if a notification should be sent based on user preferences.
        
        Args:
            user_id: ID of the user
            notification_type: Type of notification
            delivery_method: Delivery method (in_app, email, both)
            
        Returns:
            True if notification should be sent, False otherwise
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return True  # Default to sending if user not found
            
            # Check if user has disabled email notifications for email/both delivery
            # Handle case where user model doesn't have notification preference fields (for tests)
            email_notifications = getattr(user, 'email_notifications', True)
            if delivery_method == 'email' and not email_notifications:
                return False
            elif delivery_method == 'both' and not email_notifications:
                # If it's both and email is disabled, we can still send in-app
                # So we continue to check type-specific preferences
                pass
            
            # Check type-specific preferences (with defaults for missing fields)
            type_preference_map = {
                'system': getattr(user, 'system_notifications', True),
                'content': getattr(user, 'content_notifications', True),
                'interaction': getattr(user, 'interaction_notifications', True),
                'moderation': getattr(user, 'moderation_notifications', True)
            }
            
            return type_preference_map.get(notification_type, True)
            
        except Exception as e:
            logger.error(f"Error checking notification preferences: {str(e)}")
            return True  # Default to sending on error
    
    @staticmethod
    def reset_to_defaults(user_id: str) -> Tuple[bool, str]:
        """
        Reset user preferences to defaults.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            defaults = NotificationPreferenceService.get_default_preferences()
            return NotificationPreferenceService.update_preferences(user_id, defaults)
            
        except Exception as e:
            logger.error(f"Error resetting preferences to defaults: {str(e)}")
            return False, "Failed to reset preferences"
