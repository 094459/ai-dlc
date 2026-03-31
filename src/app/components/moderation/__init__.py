"""
Moderation Component

This component provides comprehensive moderation functionality including:
- Content moderation (removal, restoration, hiding)
- User moderation (warnings, suspensions, bans)
- Automated moderation workflows
- Moderation analytics and dashboard
"""

from .services import (
    ContentModerationService,
    UserModerationService, 
    ModerationWorkflowService,
    ModerationDashboardService
)
from .routes import moderation_bp

__all__ = [
    'ContentModerationService',
    'UserModerationService',
    'ModerationWorkflowService', 
    'ModerationDashboardService',
    'moderation_bp'
]
