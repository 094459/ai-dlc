"""
Analytics Component

Provides comprehensive analytics and metrics tracking for the fact checker application.
Includes event tracking, metrics calculation, dashboard management, and user engagement analysis.
"""

from .services import (
    AnalyticsService,
    MetricsCalculationService, 
    DashboardService,
    UserEngagementService
)

from .tracking import (
    AnalyticsTracker,
    track_login,
    track_logout,
    track_registration,
    track_fact_creation,
    track_comment_creation,
    track_vote,
    track_report_creation,
    track_moderation_action,
    track_search,
    track_profile_view,
    track_error
)

__all__ = [
    'AnalyticsService',
    'MetricsCalculationService',
    'DashboardService', 
    'UserEngagementService',
    'AnalyticsTracker',
    'track_login',
    'track_logout',
    'track_registration',
    'track_fact_creation',
    'track_comment_creation',
    'track_vote',
    'track_report_creation',
    'track_moderation_action',
    'track_search',
    'track_profile_view',
    'track_error'
]
