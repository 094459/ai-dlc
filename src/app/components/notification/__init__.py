"""
Notification Component

This component provides comprehensive notification functionality including:
- In-app notification creation and delivery
- Email notification sending and queuing
- Notification template management
- User notification preferences
- Integration with all application components
"""

from .services import (
    NotificationService,
    EmailNotificationService,
    NotificationTemplateService,
    NotificationPreferenceService
)
from .routes import notification_bp

__all__ = [
    'NotificationService',
    'EmailNotificationService',
    'NotificationTemplateService',
    'NotificationPreferenceService',
    'notification_bp'
]
