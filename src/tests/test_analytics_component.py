"""
Unit tests for Analytics Component functionality.
"""

import pytest
from datetime import datetime, date, timedelta
from app.models import db, User
from app.models.system import AnalyticsEvent
from app.models.analytics import MetricsAggregation, DashboardConfiguration, UserEngagementMetrics
from app.components.analytics.services import (
    AnalyticsService,
    MetricsCalculationService,
    DashboardService,
    UserEngagementService
)
from app.components.analytics.tracking import (
    AnalyticsTracker,
    track_login,
    track_logout,
    track_registration,
    track_fact_creation,
    track_comment_creation,
    track_vote
)


class TestAnalyticsService:
    """Test cases for AnalyticsService."""
    
    def test_track_event_success(self, app, sample_user):
        """Test successful event tracking."""
        with app.app_context():
            success, message = AnalyticsService.track_event(
                event_type='test_event',
                event_category='user',
                user_id=sample_user.id,
                resource_type='test',
                resource_id='test123',
                event_data={'key': 'value'},
                duration_ms=1000,
                value=5.0
            )
            
            assert success is True
            assert message == "Event tracked successfully"
            
            # Verify event was created
            event = AnalyticsEvent.query.filter_by(
                event_type='test_event',
                user_id=sample_user.id
            ).first()
            
            assert event is not None
            assert event.event_category == 'user'
            assert event.resource_type == 'test'
            assert event.resource_id == 'test123'
            assert event.event_data == {'key': 'value'}
            assert event.duration_ms == 1000
            assert event.value == 5.0
    
    def test_track_event_anonymous(self, app):
        """Test tracking anonymous events."""
        with app.app_context():
            # Ensure analytics tables exist
            db.create_all()
            
            success, message = AnalyticsService.track_event(
                event_type='page_view',
                event_category='system',
                event_data={'page': 'home'}
            )
            
            assert success is True
            
            # Verify anonymous event was created
            event = AnalyticsEvent.query.filter_by(
                event_type='page_view',
                user_id=None
            ).first()
            
            assert event is not None
            assert event.event_category == 'system'
            assert event.event_data == {'page': 'home'}
    
    def test_get_events_with_filters(self, app, sample_user):
        """Test retrieving events with various filters."""
        with app.app_context():
            # Create test events with unique identifiers
            now = datetime.utcnow()
            yesterday = now - timedelta(days=1)
            
            # Event from yesterday
            AnalyticsService.track_event(
                event_type='test_login_filter',
                event_category='user',
                user_id=sample_user.id
            )
            
            # Update the created_at to yesterday
            old_event = AnalyticsEvent.query.filter_by(event_type='test_login_filter').first()
            old_event.created_at = yesterday
            db.session.commit()
            
            # Event from today
            AnalyticsService.track_event(
                event_type='test_fact_created_filter',
                event_category='content',
                user_id=sample_user.id
            )
            
            # Test date filtering - look for our specific events
            events = AnalyticsService.get_events(
                start_date=now - timedelta(hours=1),
                end_date=now + timedelta(hours=1),
                event_types=['test_fact_created_filter']
            )
            
            assert len(events) == 1
            assert events[0].event_type == 'test_fact_created_filter'
            
            # Test event type filtering
            events = AnalyticsService.get_events(
                event_types=['test_login_filter']
            )
            
            assert len(events) == 1
            assert events[0].event_type == 'test_login_filter'
            
            # Test category filtering
            events = AnalyticsService.get_events(
                event_categories=['content'],
                event_types=['test_fact_created_filter']
            )
            
            assert len(events) == 1
            assert events[0].event_category == 'content'
            
            # Test user filtering
            events = AnalyticsService.get_events(
                user_id=sample_user.id,
                event_types=['test_login_filter', 'test_fact_created_filter']
            )
            
            assert len(events) == 2
    
    def test_get_event_counts(self, app, sample_user):
        """Test getting event counts grouped by field."""
        with app.app_context():
            # Create test events
            AnalyticsService.track_event('login', 'user', sample_user.id)
            AnalyticsService.track_event('login', 'user', sample_user.id)
            AnalyticsService.track_event('logout', 'user', sample_user.id)
            
            # Test grouping by event_type
            counts = AnalyticsService.get_event_counts(group_by='event_type')
            
            assert counts['login'] == 2
            assert counts['logout'] == 1
            
            # Test grouping by event_category
            counts = AnalyticsService.get_event_counts(group_by='event_category')
            
            assert counts['user'] == 3


class TestMetricsCalculationService:
    """Test cases for MetricsCalculationService."""
    
    def test_calculate_daily_metrics(self, app, sample_user):
        """Test daily metrics calculation."""
        with app.app_context():
            target_date = date.today() - timedelta(days=1)
            
            # Create some test data for yesterday
            yesterday_start = datetime.combine(target_date, datetime.min.time())
            
            # Create a user registration from yesterday
            test_user = User(
                email='metrics_test@example.com',
                password_hash='test_hash',
                is_active=True
            )
            test_user.created_at = yesterday_start + timedelta(hours=10)
            test_user.save()
            
            # Calculate metrics
            success, message = MetricsCalculationService.calculate_daily_metrics(target_date)
            
            assert success is True
            assert "Daily metrics calculated" in message
            
            # Verify metrics were stored
            metrics = MetricsAggregation.query.filter_by(
                aggregation_date=target_date,
                aggregation_type='daily'
            ).all()
            
            assert len(metrics) > 0
            
            # Check user registration metric
            user_reg_metric = MetricsAggregation.query.filter_by(
                metric_name='user_registration_count',
                aggregation_date=target_date
            ).first()
            
            assert user_reg_metric is not None
            assert user_reg_metric.count_value >= 1
    
    def test_get_metrics_with_filters(self, app):
        """Test retrieving metrics with filters."""
        with app.app_context():
            # Ensure analytics tables exist
            db.create_all()
            
            # Create test metrics
            test_date = date.today() - timedelta(days=5)
            
            metric1 = MetricsAggregation(
                metric_name='test_metric_1',
                aggregation_type='daily',
                aggregation_date=test_date,
                count_value=10
            )
            
            metric2 = MetricsAggregation(
                metric_name='test_metric_2',
                aggregation_type='daily',
                aggregation_date=test_date,
                count_value=20
            )
            
            db.session.add(metric1)
            db.session.add(metric2)
            db.session.commit()
            
            # Test filtering by metric names
            metrics = MetricsCalculationService.get_metrics(
                metric_names=['test_metric_1'],
                start_date=test_date,
                end_date=test_date
            )
            
            assert len(metrics) == 1
            assert metrics[0].metric_name == 'test_metric_1'
            assert metrics[0].count_value == 10
            
            # Test date range filtering
            metrics = MetricsCalculationService.get_metrics(
                start_date=test_date - timedelta(days=1),
                end_date=test_date + timedelta(days=1)
            )
            
            assert len(metrics) == 2
    
    def test_store_metric_update_existing(self, app):
        """Test updating existing metrics."""
        with app.app_context():
            # Ensure analytics tables exist
            db.create_all()
            
            test_date = date.today()
            
            # Create initial metric
            MetricsCalculationService._store_metric(
                'test_metric', 'daily', test_date, 10, {'initial': True}
            )
            
            # Update the same metric
            MetricsCalculationService._store_metric(
                'test_metric', 'daily', test_date, 20, {'updated': True}
            )
            
            # Verify only one metric exists with updated value
            metrics = MetricsAggregation.query.filter_by(
                metric_name='test_metric',
                aggregation_date=test_date
            ).all()
            
            assert len(metrics) == 1
            assert metrics[0].count_value == 20
            assert metrics[0].extra_data == {'updated': True}


class TestDashboardService:
    """Test cases for DashboardService."""
    
    def test_create_dashboard_success(self, app, sample_user):
        """Test successful dashboard creation."""
        with app.app_context():
            widget_config = {
                'widget1': {
                    'type': 'metric',
                    'metrics': ['daily_active_users']
                }
            }
            
            success, message, dashboard = DashboardService.create_dashboard(
                name='Test Dashboard',
                dashboard_type='admin',
                widget_config=widget_config,
                description='Test dashboard',
                creator_id=sample_user.id
            )
            
            assert success is True
            assert message == "Dashboard created successfully"
            assert dashboard is not None
            assert dashboard.name == 'Test Dashboard'
            assert dashboard.dashboard_type == 'admin'
            assert dashboard.widget_config == widget_config
            assert dashboard.created_by == sample_user.id
    
    def test_create_dashboard_duplicate_name(self, app, sample_user):
        """Test creating dashboard with duplicate name."""
        with app.app_context():
            # Create first dashboard
            DashboardService.create_dashboard(
                name='Duplicate Test',
                dashboard_type='admin',
                widget_config={},
                creator_id=sample_user.id
            )
            
            # Try to create another with same name
            success, message, dashboard = DashboardService.create_dashboard(
                name='Duplicate Test',
                dashboard_type='admin',
                widget_config={},
                creator_id=sample_user.id
            )
            
            assert success is False
            assert message == "Dashboard name already exists"
            assert dashboard is None
    
    def test_get_dashboards_with_access_control(self, app, sample_user):
        """Test dashboard retrieval with access control."""
        with app.app_context():
            # Create public dashboard
            DashboardService.create_dashboard(
                name='Public Dashboard',
                dashboard_type='admin',
                widget_config={},
                is_public=True,
                creator_id=sample_user.id
            )
            
            # Create private dashboard
            DashboardService.create_dashboard(
                name='Private Dashboard',
                dashboard_type='admin',
                widget_config={},
                is_public=False,
                creator_id=sample_user.id
            )
            
            # Test getting dashboards for the creator
            dashboards = DashboardService.get_dashboards(
                dashboard_type='admin',
                user_id=sample_user.id,
                include_public=True
            )
            
            assert len(dashboards) == 2
            
            # Test getting only public dashboards
            dashboards = DashboardService.get_dashboards(
                dashboard_type='admin',
                user_id=None,
                include_public=True
            )
            
            assert len(dashboards) == 1
            assert dashboards[0].name == 'Public Dashboard'
    
    def test_get_dashboard_data(self, app, sample_user):
        """Test retrieving dashboard data."""
        with app.app_context():
            # Create dashboard with widget config
            widget_config = {
                'metrics_widget': {
                    'type': 'metric',
                    'metrics': ['daily_active_users']
                }
            }
            
            success, message, dashboard = DashboardService.create_dashboard(
                name='Data Test Dashboard',
                dashboard_type='admin',
                widget_config=widget_config,
                creator_id=sample_user.id
            )
            
            # Create some test metrics
            test_date = date.today() - timedelta(days=1)
            metric = MetricsAggregation(
                metric_name='daily_active_users',
                aggregation_type='daily',
                aggregation_date=test_date,
                count_value=50
            )
            db.session.add(metric)
            db.session.commit()
            
            # Get dashboard data
            data = DashboardService.get_dashboard_data(dashboard.id, date_range=7)
            
            assert 'dashboard' in data
            assert 'data' in data
            assert 'date_range' in data
            assert data['dashboard']['name'] == 'Data Test Dashboard'
            
            # Verify view count was incremented
            updated_dashboard = db.session.get(DashboardConfiguration, dashboard.id)
            assert updated_dashboard.view_count == 1
            assert updated_dashboard.last_viewed is not None


class TestUserEngagementService:
    """Test cases for UserEngagementService."""
    
    def test_get_user_engagement_summary(self, app, sample_user):
        """Test getting user engagement summary."""
        with app.app_context():
            # Create test engagement metrics
            test_date = date.today() - timedelta(days=5)
            
            engagement = UserEngagementMetrics(
                user_id=sample_user.id,
                metric_date=test_date,
                session_count=3,
                total_session_duration=1800,  # 30 minutes
                page_views=15,
                facts_created=2,
                comments_created=5,
                votes_cast=10
            )
            db.session.add(engagement)
            db.session.commit()
            
            # Get engagement summary
            summary = UserEngagementService.get_user_engagement_summary(
                sample_user.id, days=30
            )
            
            assert summary['user_id'] == sample_user.id
            assert summary['total_sessions'] == 3
            assert summary['total_duration'] == 1800
            assert summary['avg_session_duration'] == 600  # 10 minutes
            assert summary['total_page_views'] == 15
            assert summary['content_created'] == 7  # 2 facts + 5 comments
            assert summary['interactions'] == 10
            assert len(summary['daily_metrics']) == 1
    
    def test_get_user_engagement_summary_no_data(self, app, sample_user):
        """Test getting engagement summary for user with no data."""
        with app.app_context():
            summary = UserEngagementService.get_user_engagement_summary(
                sample_user.id, days=30
            )
            
            assert summary['user_id'] == sample_user.id
            assert summary['total_sessions'] == 0
            assert summary['total_duration'] == 0
            assert summary['avg_session_duration'] == 0
            assert summary['engagement_score'] == 0
            assert summary['daily_metrics'] == []
    
    def test_get_top_engaged_users(self, app, sample_user):
        """Test getting top engaged users."""
        with app.app_context():
            # Create another user for comparison
            user2 = User(
                email='user2@example.com',
                password_hash='test_hash',
                is_active=True
            )
            user2.save()
            
            # Create engagement metrics for both users
            test_date = date.today() - timedelta(days=1)
            
            # High engagement user
            engagement1 = UserEngagementMetrics(
                user_id=sample_user.id,
                metric_date=test_date,
                session_count=5,
                facts_created=3,
                comments_created=8,
                votes_cast=15
            )
            
            # Low engagement user
            engagement2 = UserEngagementMetrics(
                user_id=user2.id,
                metric_date=test_date,
                session_count=1,
                facts_created=0,
                comments_created=1,
                votes_cast=2
            )
            
            db.session.add(engagement1)
            db.session.add(engagement2)
            db.session.commit()
            
            # Get top engaged users
            top_users = UserEngagementService.get_top_engaged_users(days=7, limit=5)
            
            assert len(top_users) == 2
            # First user should have higher engagement
            assert top_users[0]['user_id'] == sample_user.id
            assert top_users[0]['content_created'] == 11  # 3 facts + 8 comments
            assert top_users[1]['user_id'] == user2.id
            assert top_users[1]['content_created'] == 1  # 0 facts + 1 comment
