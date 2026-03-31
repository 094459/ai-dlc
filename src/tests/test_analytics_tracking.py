"""
Unit tests for Analytics Tracking functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import session
from app.models import db
from app.models.system import AnalyticsEvent
from app.components.analytics.services import AnalyticsService
from app.components.analytics.tracking import (
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


class TestAnalyticsTracker:
    """Test cases for AnalyticsTracker class."""
    
    @patch('app.components.analytics.tracking.request')
    @patch('app.components.analytics.tracking.session')
    def test_track_user_action_success(self, mock_session, mock_request, app, sample_user):
        """Test successful user action tracking."""
        with app.app_context():
            # Mock session and request
            mock_session.get = MagicMock(side_effect=lambda key: {
                'user_id': sample_user.id,
                'session_id': 'test_session_123'
            }.get(key))
            
            mock_request.remote_addr = '127.0.0.1'
            mock_request.headers = {'User-Agent': 'Test Browser', 'Referer': 'http://test.com'}
            mock_request.url = 'http://test.com/page'
            
            # Track user action
            success = AnalyticsTracker.track_user_action(
                event_type='test_action',
                resource_type='test_resource',
                resource_id='test_123',
                event_data={'key': 'value'},
                duration_ms=500,
                value=10.5
            )
            
            assert success is True
            
            # Verify event was created
            event = AnalyticsEvent.query.filter_by(
                event_type='test_action',
                user_id=sample_user.id
            ).first()
            
            assert event is not None
            assert event.event_category == 'user'
            assert event.resource_type == 'test_resource'
            assert event.resource_id == 'test_123'
            assert event.event_data == {'key': 'value'}
            assert event.duration_ms == 500
            assert event.value == 10.5
            assert event.session_id == 'test_session_123'
            assert event.ip_address == '127.0.0.1'
    
    @patch('app.components.analytics.tracking.request')
    @patch('app.components.analytics.tracking.session')
    def test_track_content_action(self, mock_session, mock_request, app, sample_user):
        """Test content action tracking."""
        with app.app_context():
            mock_session.get = MagicMock(side_effect=lambda key: {
                'user_id': sample_user.id,
                'session_id': 'test_session_123'
            }.get(key))
            
            mock_request.remote_addr = '127.0.0.1'
            mock_request.headers = {}
            mock_request.url = 'http://test.com/content'
            
            success = AnalyticsTracker.track_content_action(
                event_type='content_created',
                resource_type='fact',
                resource_id='fact_123',
                event_data={'title': 'Test Fact'}
            )
            
            assert success is True
            
            event = AnalyticsEvent.query.filter_by(
                event_type='content_created',
                event_category='content'
            ).first()
            
            assert event is not None
            assert event.resource_type == 'fact'
            assert event.resource_id == 'fact_123'
            assert event.event_data == {'title': 'Test Fact'}
    
    @patch('app.components.analytics.tracking.request')
    @patch('app.components.analytics.tracking.session')
    def test_track_interaction(self, mock_session, mock_request, app, sample_user):
        """Test interaction tracking."""
        with app.app_context():
            mock_session.get = MagicMock(side_effect=lambda key: {
                'user_id': sample_user.id,
                'session_id': 'test_session_123'
            }.get(key))
            
            mock_request.remote_addr = '127.0.0.1'
            mock_request.headers = {}
            mock_request.url = 'http://test.com/vote'
            
            success = AnalyticsTracker.track_interaction(
                event_type='fact_vote',
                resource_type='fact',
                resource_id='fact_123',
                interaction_value='upvote'
            )
            
            assert success is True
            
            event = AnalyticsEvent.query.filter_by(
                event_type='fact_vote',
                event_category='interaction'
            ).first()
            
            assert event is not None
            assert event.resource_type == 'fact'
            assert event.resource_id == 'fact_123'
            assert event.event_data == {'interaction_value': 'upvote'}
    
    @patch('app.components.analytics.tracking.request')
    @patch('app.components.analytics.tracking.session')
    def test_track_moderation_action(self, mock_session, mock_request, app, sample_user):
        """Test moderation action tracking."""
        with app.app_context():
            mock_session.get = MagicMock(side_effect=lambda key: {
                'user_id': sample_user.id,
                'session_id': 'test_session_123'
            }.get(key))
            
            mock_request.remote_addr = '127.0.0.1'
            mock_request.headers = {}
            mock_request.url = 'http://test.com/moderate'
            
            success = AnalyticsTracker.track_moderation_action(
                event_type='content_removed',
                resource_type='fact',
                resource_id='fact_123',
                action_details={'reason': 'spam', 'moderator': sample_user.id}
            )
            
            assert success is True
            
            event = AnalyticsEvent.query.filter_by(
                event_type='content_removed',
                event_category='moderation'
            ).first()
            
            assert event is not None
            assert event.resource_type == 'fact'
            assert event.resource_id == 'fact_123'
            assert event.event_data == {'reason': 'spam', 'moderator': sample_user.id}
    
    @patch('app.components.analytics.tracking.request')
    def test_track_system_event(self, mock_request, app):
        """Test system event tracking."""
        with app.app_context():
            # Ensure analytics tables exist
            db.create_all()
            
            mock_request.remote_addr = '127.0.0.1'
            mock_request.headers = {}
            mock_request.url = 'http://test.com/system'
            
            success = AnalyticsTracker.track_system_event(
                event_type='app_start',
                event_data={'version': '1.0.0'}
            )
            
            assert success is True
            
            event = AnalyticsEvent.query.filter_by(
                event_type='app_start',
                event_category='system'
            ).first()
            
            assert event is not None
            assert event.user_id is None  # System events don't have users
            assert event.event_data == {'version': '1.0.0'}
    
    @patch('app.components.analytics.tracking.request')
    @patch('app.components.analytics.tracking.session')
    def test_track_page_view(self, mock_session, mock_request, app, sample_user):
        """Test page view tracking."""
        with app.app_context():
            mock_session.get = MagicMock(side_effect=lambda key: {
                'user_id': sample_user.id,
                'session_id': 'test_session_123'
            }.get(key))
            
            mock_request.remote_addr = '127.0.0.1'
            mock_request.headers = {'Referer': 'http://test.com/previous'}
            mock_request.url = 'http://test.com/current'
            
            success = AnalyticsTracker.track_page_view(
                page_name='home',
                page_category='main'
            )
            
            assert success is True
            
            event = AnalyticsEvent.query.filter_by(
                event_type='page_view',
                event_category='user'
            ).first()
            
            assert event is not None
            assert event.event_data == {'page_name': 'home', 'page_category': 'main'}
            assert event.referrer == 'http://test.com/previous'
            assert event.page_url == 'http://test.com/current'
    
    def test_track_action_error_handling(self, app):
        """Test error handling in tracking methods."""
        with app.app_context():
            # Test with invalid data that might cause an error
            success = AnalyticsTracker.track_user_action(
                event_type=None,  # Invalid event type
                resource_type='test'
            )
            
            # Should return False but not raise an exception
            assert success is False


class TestConvenienceFunctions:
    """Test cases for convenience tracking functions."""
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_user_action')
    def test_track_login(self, mock_track, app, sample_user):
        """Test login tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_login(sample_user.id)
            
            assert result is True
            mock_track.assert_called_once_with('login', 'user', sample_user.id)
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_user_action')
    def test_track_logout(self, mock_track, app, sample_user):
        """Test logout tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_logout(sample_user.id)
            
            assert result is True
            mock_track.assert_called_once_with('logout', 'user', sample_user.id)
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_user_action')
    def test_track_registration(self, mock_track, app, sample_user):
        """Test registration tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_registration(sample_user.id)
            
            assert result is True
            mock_track.assert_called_once_with('user_registered', 'user', sample_user.id)
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_content_action')
    def test_track_fact_creation(self, mock_track, app):
        """Test fact creation tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_fact_creation('fact_123', ['tag1', 'tag2'])
            
            assert result is True
            mock_track.assert_called_once_with(
                'fact_created', 
                'fact', 
                'fact_123', 
                {'hashtags': ['tag1', 'tag2'], 'hashtag_count': 2}
            )
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_content_action')
    def test_track_fact_creation_no_hashtags(self, mock_track, app):
        """Test fact creation tracking without hashtags."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_fact_creation('fact_123')
            
            assert result is True
            mock_track.assert_called_once_with('fact_created', 'fact', 'fact_123', {})
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_content_action')
    def test_track_comment_creation(self, mock_track, app):
        """Test comment creation tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_comment_creation('comment_123', 'fact_456', is_reply=True)
            
            assert result is True
            mock_track.assert_called_once_with(
                'comment_created', 
                'comment', 
                'comment_123', 
                {'fact_id': 'fact_456', 'is_reply': True}
            )
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_interaction')
    def test_track_vote(self, mock_track, app):
        """Test vote tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_vote('fact', 'fact_123', 'upvote')
            
            assert result is True
            mock_track.assert_called_once_with('fact_vote', 'fact', 'fact_123', 'upvote')
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_user_action')
    def test_track_report_creation(self, mock_track, app):
        """Test report creation tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_report_creation('report_123', 'fact', 'fact_456', 'spam')
            
            assert result is True
            mock_track.assert_called_once_with(
                'report_created', 
                'report', 
                'report_123', 
                {
                    'resource_type': 'fact',
                    'resource_id': 'fact_456',
                    'report_category': 'spam'
                }
            )
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_moderation_action')
    def test_track_moderation_action_func(self, mock_track, app):
        """Test moderation action tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_moderation_action(
                'content_removed', 
                'fact', 
                'fact_123', 
                'mod_456', 
                'spam content'
            )
            
            assert result is True
            mock_track.assert_called_once_with(
                'content_removed', 
                'fact', 
                'fact_123', 
                {
                    'moderator_id': 'mod_456',
                    'resource_type': 'fact',
                    'resource_id': 'fact_123',
                    'reason': 'spam content'
                }
            )
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_user_action')
    def test_track_search(self, mock_track, app):
        """Test search tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_search('test query', 5, 'facts')
            
            assert result is True
            mock_track.assert_called_once_with(
                'search_performed', 
                event_data={
                    'query': 'test query',
                    'results_count': 5,
                    'search_type': 'facts'
                }
            )
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_user_action')
    def test_track_profile_view(self, mock_track, app):
        """Test profile view tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_profile_view('user_123')
            
            assert result is True
            mock_track.assert_called_once_with('profile_viewed', 'user', 'user_123')
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_system_event')
    def test_track_error(self, mock_track, app):
        """Test error tracking convenience function."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_error('database_error', 'Connection failed', '/test/page')
            
            assert result is True
            mock_track.assert_called_once_with(
                'error_occurred', 
                {
                    'error_type': 'database_error',
                    'error_message': 'Connection failed',
                    'page_url': '/test/page'
                }
            )
    
    @patch('app.components.analytics.tracking.AnalyticsTracker.track_system_event')
    def test_track_error_no_page_url(self, mock_track, app):
        """Test error tracking without page URL."""
        with app.app_context():
            mock_track.return_value = True
            
            result = track_error('validation_error', 'Invalid input')
            
            assert result is True
            mock_track.assert_called_once_with(
                'error_occurred', 
                {
                    'error_type': 'validation_error',
                    'error_message': 'Invalid input'
                }
            )


class TestAnalyticsIntegration:
    """Test cases for analytics integration scenarios."""
    
    @patch('app.components.analytics.tracking.request')
    @patch('app.components.analytics.tracking.session')
    def test_full_user_journey_tracking(self, mock_session, mock_request, app, sample_user):
        """Test tracking a complete user journey."""
        with app.app_context():
            # Mock session and request
            mock_session.get = MagicMock(side_effect=lambda key: {
                'user_id': sample_user.id,
                'session_id': 'journey_session_123'
            }.get(key))
            
            mock_request.remote_addr = '192.168.1.1'
            mock_request.headers = {'User-Agent': 'Test Browser'}
            mock_request.url = 'http://test.com'
            
            # Simulate user journey
            # 1. Login
            track_login(sample_user.id)
            
            # 2. Page view
            AnalyticsTracker.track_page_view('home', 'main')
            
            # 3. Create fact
            track_fact_creation('fact_journey_123', ['test', 'journey'])
            
            # 4. Vote on content
            track_vote('fact', 'other_fact_123', 'upvote')
            
            # 5. Search
            track_search('test search', 3)
            
            # 6. Logout
            track_logout(sample_user.id)
            
            # Verify all events were tracked
            events = AnalyticsEvent.query.filter_by(user_id=sample_user.id).all()
            
            assert len(events) == 6
            
            event_types = [event.event_type for event in events]
            expected_types = ['login', 'page_view', 'fact_created', 'fact_vote', 'search_performed', 'logout']
            
            for expected_type in expected_types:
                assert expected_type in event_types
            
            # Verify session consistency
            for event in events:
                if event.session_id:  # Some events might not have session
                    assert event.session_id == 'journey_session_123'
    
    def test_anonymous_user_tracking(self, app):
        """Test tracking events for anonymous users."""
        with app.app_context():
            # Ensure analytics tables exist
            db.create_all()
            
            # Track system event (no user)
            success = AnalyticsTracker.track_system_event(
                'page_view_anonymous',
                {'page': 'home', 'anonymous': True}
            )
            
            assert success is True
            
            # Verify anonymous event
            event = AnalyticsEvent.query.filter_by(
                event_type='page_view_anonymous'
            ).first()
            
            assert event is not None
            assert event.user_id is None
            assert event.event_category == 'system'
            assert event.event_data == {'page': 'home', 'anonymous': True}
    
    def test_bulk_event_tracking_performance(self, app, sample_user):
        """Test performance with multiple events."""
        with app.app_context():
            # Track multiple events quickly
            events_to_track = 50
            
            for i in range(events_to_track):
                AnalyticsService.track_event(
                    event_type='bulk_test',
                    event_category='user',
                    user_id=sample_user.id,
                    event_data={'index': i}
                )
            
            # Verify all events were tracked
            events = AnalyticsEvent.query.filter_by(
                event_type='bulk_test',
                user_id=sample_user.id
            ).all()
            
            assert len(events) == events_to_track
            
            # Verify data integrity
            indices = [event.event_data.get('index') for event in events]
            assert set(indices) == set(range(events_to_track))
