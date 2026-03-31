"""
PyTest configuration and fixtures for the Fact Checker application.
Provides reusable fixtures for testing with ephemeral databases.
"""
import pytest
import tempfile
import os
from app import create_app, db
# Import all models to ensure they are registered with SQLAlchemy
from app.models import *
# Explicitly import analytics models to ensure they're registered
from app.models.analytics import MetricsAggregation, DashboardConfiguration, UserEngagementMetrics
from app.models.system import AnalyticsEvent


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Create app with testing configuration
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Clean up temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def app_context(app):
    """Create application context."""
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db_session(app_context):
    """Create database session for testing."""
    # Create all tables
    db.create_all()
    
    yield db.session
    
    # Clean up after test
    db.session.rollback()
    db.drop_all()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        email='test@example.com',
        password_hash='$2b$12$test_hash',
        is_active=True,
        # Add notification preference fields with defaults
        email_notifications=True,
        notification_frequency='immediate',
        system_notifications=True,
        content_notifications=True,
        interaction_notifications=True,
        moderation_notifications=True
    )
    user.save()
    return user


@pytest.fixture
def sample_admin_user(db_session):
    """Create a sample admin user for testing."""
    user = User(
        email='admin@example.com',
        password_hash='$2b$12$admin_hash',
        is_active=True,
        is_admin=True,
        # Add notification preference fields with defaults
        email_notifications=True,
        notification_frequency='immediate',
        system_notifications=True,
        content_notifications=True,
        interaction_notifications=True,
        moderation_notifications=True
    )
    user.save()
    return user


@pytest.fixture
def sample_moderator_user(db_session):
    """Create a sample moderator user for testing."""
    user = User(
        email='moderator@example.com',
        password_hash='$2b$12$moderator_hash',
        is_active=True,
        is_moderator=True,
        # Add notification preference fields with defaults
        email_notifications=True,
        notification_frequency='immediate',
        system_notifications=True,
        content_notifications=True,
        interaction_notifications=True,
        moderation_notifications=True
    )
    user.save()
    return user


@pytest.fixture
def sample_user_profile(db_session, sample_user):
    """Create a sample user profile for testing."""
    profile = UserProfile(
        user_id=sample_user.id,
        name='Test User',
        biography='This is a test user profile.'
    )
    profile.save()
    return profile


@pytest.fixture
def sample_fact(db_session, sample_user):
    """Create a sample fact for testing."""
    fact = Fact(
        user_id=sample_user.id,
        content='This is a test fact about something important.'
    )
    fact.save()
    return fact


@pytest.fixture
def sample_comment(db_session, sample_user, sample_fact):
    """Create a sample comment for testing."""
    comment = Comment(
        fact_id=sample_fact.id,
        user_id=sample_user.id,
        content='This is a test comment on the fact.',
        nesting_level=0
    )
    comment.save()
    return comment


@pytest.fixture
def sample_hashtag(db_session):
    """Create a sample hashtag for testing."""
    hashtag = Hashtag(
        tag='testhashtag',
        usage_count=1
    )
    hashtag.save()
    return hashtag


@pytest.fixture
def multiple_users(db_session):
    """Create multiple users for testing."""
    users = []
    for i in range(3):
        user = User(
            email=f'user{i}@example.com',
            password_hash=f'$2b$12$hash{i}',
            is_active=True
        )
        user.save()
        users.append(user)
    return users


@pytest.fixture
def multiple_facts(db_session, sample_user):
    """Create multiple facts for testing."""
    facts = []
    for i in range(5):
        fact = Fact(
            user_id=sample_user.id,
            content=f'This is test fact number {i+1}.'
        )
        fact.save()
        facts.append(fact)
    return facts


@pytest.fixture
def authenticated_user_session(client, sample_user):
    """Create an authenticated user session for testing."""
    with client.session_transaction() as sess:
        sess['user_id'] = sample_user.id
        sess['_fresh'] = True
    return sample_user


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_user(email='test@example.com', password_hash='$2b$12$test_hash', **kwargs):
        """Create a user with default or custom attributes."""
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'is_active': True
        }
        user_data.update(kwargs)
        user = User(**user_data)
        user.save()
        return user
    
    @staticmethod
    def create_fact(user_id, content='Test fact content', **kwargs):
        """Create a fact with default or custom attributes."""
        fact_data = {
            'user_id': user_id,
            'content': content
        }
        fact_data.update(kwargs)
        fact = Fact(**fact_data)
        fact.save()
        return fact
    
    @staticmethod
    def create_comment(fact_id, user_id, content='Test comment content', **kwargs):
        """Create a comment with default or custom attributes."""
        comment_data = {
            'fact_id': fact_id,
            'user_id': user_id,
            'content': content,
            'nesting_level': 0
        }
        comment_data.update(kwargs)
        comment = Comment(**comment_data)
        comment.save()
        return comment


@pytest.fixture
def test_data_factory():
    """Provide test data factory for creating test objects."""
    return TestDataFactory
