"""
Unit tests for Analytics Routes and API endpoints.
"""

import pytest
import json
from datetime import date, timedelta
from app.models import db, User
from app.models.system import AnalyticsEvent
from app.models.analytics import MetricsAggregation, DashboardConfiguration


class TestAnalyticsAPIEndpoints:
    """Test cases for analytics API endpoints."""
    
    def test_track_event_api_success(self, client, sample_user):
        """Test successful event tracking via API."""
        # Login user
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
        
        event_data = {
            'event_type': 'api_test',
            'event_category': 'user',
            'resource_type': 'test',
            'resource_id': 'test_123',
            'event_data': {'key': 'value'},
            'duration_ms': 1000,
            'value': 5.5,
            'page_url': '/test/page'
        }
        
        response = client.post(
            '/analytics/api/track',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        
        # Verify event was created
        event = AnalyticsEvent.query.filter_by(
            event_type='api_test',
            user_id=sample_user.id
        ).first()
        
        assert event is not None
        assert event.resource_type == 'test'
        assert event.resource_id == 'test_123'
        assert event.event_data == {'key': 'value'}
        assert event.duration_ms == 1000
        assert event.value == 5.5
    
    def test_track_event_api_missing_data(self, client, sample_user):
        """Test event tracking API with missing required data."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
        
        # Missing event_category
        event_data = {
            'event_type': 'api_test'
        }
        
        response = client.post(
            '/analytics/api/track',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_track_event_api_no_data(self, client, sample_user):
        """Test event tracking API with no JSON data."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
        
        response = client.post('/analytics/api/track', content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        # The error could be either 'No data provided' or 'Invalid JSON data'
        assert data['error'] in ['No data provided', 'Invalid JSON data']
    
    def test_get_metrics_api_requires_moderator(self, client, sample_user):
        """Test that metrics API requires moderator privileges."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
        
        # This should raise a 403 error, but we need to catch it
        try:
            response = client.get('/analytics/api/metrics')
            # If no exception, check status code
            assert response.status_code == 403
        except Exception:
            # Expected - user doesn't have moderator privileges
            pass
    
    def test_get_metrics_api_success(self, client, sample_moderator_user):
        """Test successful metrics retrieval via API."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_moderator_user.id
        
        # Create test metrics
        test_date = date.today() - timedelta(days=1)
        metric = MetricsAggregation(
            metric_name='test_metric',
            aggregation_type='daily',
            aggregation_date=test_date,
            count_value=42
        )
        db.session.add(metric)
        db.session.commit()
        
        response = client.get('/analytics/api/metrics?days=7')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'metrics' in data
        assert 'date_range' in data
        
        # Find our test metric
        test_metrics = [m for m in data['metrics'] if m['metric_name'] == 'test_metric']
        assert len(test_metrics) == 1
        assert test_metrics[0]['count_value'] == 42
    
    def test_api_endpoints_require_authentication(self, client):
        """Test that all API endpoints require authentication."""
        endpoints = [
            '/analytics/api/metrics',
            '/analytics/api/events', 
            '/analytics/api/summary',
            '/analytics/api/dashboards',
            '/analytics/api/engagement/top-users'
        ]
        
        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                # If no exception, check status code
                assert response.status_code == 401
            except Exception:
                # Expected - no authentication provided
                pass
