"""
Analytics tracking helper functions for easy integration across components.
"""

import logging
from flask import session, request
from typing import Dict, Any, Optional
from .services import AnalyticsService

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Helper class for tracking analytics events across the application."""
    
    @staticmethod
    def track_user_action(event_type: str, resource_type: str = None, 
                         resource_id: str = None, event_data: Dict[str, Any] = None,
                         duration_ms: int = None, value: float = None) -> bool:
        """
        Track a user action event.
        
        Args:
            event_type: Type of event (login, fact_created, vote_cast, etc.)
            resource_type: Type of resource involved (fact, comment, user, etc.)
            resource_id: ID of the resource
            event_data: Additional event-specific data
            duration_ms: Duration in milliseconds for timing events
            value: Numeric value for the event
            
        Returns:
            True if tracking was successful, False otherwise
        """
        try:
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            
            success, message = AnalyticsService.track_event(
                event_type=event_type,
                event_category='user',
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                event_data=event_data or {},
                duration_ms=duration_ms,
                value=value,
                session_id=session_id,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                referrer=request.headers.get('Referer') if request else None,
                page_url=request.url if request else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking user action: {str(e)}")
            return False
    
    @staticmethod
    def track_content_action(event_type: str, resource_type: str, resource_id: str,
                           event_data: Dict[str, Any] = None) -> bool:
        """
        Track a content-related action event.
        
        Args:
            event_type: Type of event (fact_created, comment_created, etc.)
            resource_type: Type of resource (fact, comment)
            resource_id: ID of the resource
            event_data: Additional event-specific data
            
        Returns:
            True if tracking was successful, False otherwise
        """
        try:
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            
            success, message = AnalyticsService.track_event(
                event_type=event_type,
                event_category='content',
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                event_data=event_data or {},
                session_id=session_id,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                page_url=request.url if request else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking content action: {str(e)}")
            return False
    
    @staticmethod
    def track_interaction(event_type: str, resource_type: str, resource_id: str,
                         interaction_value: str = None) -> bool:
        """
        Track an interaction event (votes, likes, etc.).
        
        Args:
            event_type: Type of event (fact_vote, comment_vote, etc.)
            resource_type: Type of resource (fact, comment)
            resource_id: ID of the resource
            interaction_value: Value of the interaction (upvote, downvote, fact, fake)
            
        Returns:
            True if tracking was successful, False otherwise
        """
        try:
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            
            event_data = {}
            if interaction_value:
                event_data['interaction_value'] = interaction_value
            
            success, message = AnalyticsService.track_event(
                event_type=event_type,
                event_category='interaction',
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                event_data=event_data,
                session_id=session_id,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                page_url=request.url if request else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking interaction: {str(e)}")
            return False
    
    @staticmethod
    def track_moderation_action(event_type: str, resource_type: str = None,
                              resource_id: str = None, action_details: Dict[str, Any] = None) -> bool:
        """
        Track a moderation action event.
        
        Args:
            event_type: Type of event (content_removed, user_warned, etc.)
            resource_type: Type of resource (fact, comment, user)
            resource_id: ID of the resource
            action_details: Details about the moderation action
            
        Returns:
            True if tracking was successful, False otherwise
        """
        try:
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            
            success, message = AnalyticsService.track_event(
                event_type=event_type,
                event_category='moderation',
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                event_data=action_details or {},
                session_id=session_id,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                page_url=request.url if request else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking moderation action: {str(e)}")
            return False
    
    @staticmethod
    def track_system_event(event_type: str, event_data: Dict[str, Any] = None) -> bool:
        """
        Track a system event.
        
        Args:
            event_type: Type of event (app_start, error_occurred, etc.)
            event_data: Additional event-specific data
            
        Returns:
            True if tracking was successful, False otherwise
        """
        try:
            success, message = AnalyticsService.track_event(
                event_type=event_type,
                event_category='system',
                event_data=event_data or {},
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                page_url=request.url if request else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking system event: {str(e)}")
            return False
    
    @staticmethod
    def track_page_view(page_name: str, page_category: str = 'general') -> bool:
        """
        Track a page view event.
        
        Args:
            page_name: Name of the page
            page_category: Category of the page
            
        Returns:
            True if tracking was successful, False otherwise
        """
        try:
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            
            success, message = AnalyticsService.track_event(
                event_type='page_view',
                event_category='user',
                user_id=user_id,
                event_data={
                    'page_name': page_name,
                    'page_category': page_category
                },
                session_id=session_id,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                referrer=request.headers.get('Referer') if request else None,
                page_url=request.url if request else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking page view: {str(e)}")
            return False


# Convenience functions for common tracking scenarios

def track_login(user_id: str) -> bool:
    """Track user login event."""
    return AnalyticsTracker.track_user_action('login', 'user', user_id)


def track_logout(user_id: str) -> bool:
    """Track user logout event."""
    return AnalyticsTracker.track_user_action('logout', 'user', user_id)


def track_registration(user_id: str) -> bool:
    """Track user registration event."""
    return AnalyticsTracker.track_user_action('user_registered', 'user', user_id)


def track_fact_creation(fact_id: str, hashtags: list = None) -> bool:
    """Track fact creation event."""
    event_data = {}
    if hashtags:
        event_data['hashtags'] = hashtags
        event_data['hashtag_count'] = len(hashtags)
    
    return AnalyticsTracker.track_content_action('fact_created', 'fact', fact_id, event_data)


def track_comment_creation(comment_id: str, fact_id: str, is_reply: bool = False) -> bool:
    """Track comment creation event."""
    event_data = {
        'fact_id': fact_id,
        'is_reply': is_reply
    }
    
    return AnalyticsTracker.track_content_action('comment_created', 'comment', comment_id, event_data)


def track_vote(resource_type: str, resource_id: str, vote_type: str) -> bool:
    """Track voting event."""
    event_type = f'{resource_type}_vote'
    return AnalyticsTracker.track_interaction(event_type, resource_type, resource_id, vote_type)


def track_report_creation(report_id: str, resource_type: str, resource_id: str, 
                         report_category: str) -> bool:
    """Track report creation event."""
    event_data = {
        'resource_type': resource_type,
        'resource_id': resource_id,
        'report_category': report_category
    }
    
    return AnalyticsTracker.track_user_action('report_created', 'report', report_id, event_data)


def track_moderation_action(action_type: str, resource_type: str, resource_id: str,
                          moderator_id: str, reason: str = None) -> bool:
    """Track moderation action event."""
    event_data = {
        'moderator_id': moderator_id,
        'resource_type': resource_type,
        'resource_id': resource_id
    }
    if reason:
        event_data['reason'] = reason
    
    return AnalyticsTracker.track_moderation_action(action_type, resource_type, resource_id, event_data)


def track_search(query: str, results_count: int, search_type: str = 'general') -> bool:
    """Track search event."""
    event_data = {
        'query': query,
        'results_count': results_count,
        'search_type': search_type
    }
    
    return AnalyticsTracker.track_user_action('search_performed', event_data=event_data)


def track_profile_view(viewed_user_id: str) -> bool:
    """Track profile view event."""
    return AnalyticsTracker.track_user_action('profile_viewed', 'user', viewed_user_id)


def track_error(error_type: str, error_message: str, page_url: str = None) -> bool:
    """Track error event."""
    event_data = {
        'error_type': error_type,
        'error_message': error_message
    }
    if page_url:
        event_data['page_url'] = page_url
    
    return AnalyticsTracker.track_system_event('error_occurred', event_data)


def track_admin_action(admin_user_id: str, action_type: str, action: str, 
                      metadata: dict = None) -> bool:
    """Track admin action event."""
    event_data = {
        'action_type': action_type,
        'action': action,
        'admin_user_id': admin_user_id
    }
    if metadata:
        event_data.update(metadata)
    
    return AnalyticsTracker.track_system_event('admin_action', event_data)
