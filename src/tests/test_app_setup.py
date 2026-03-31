"""
Tests for basic application setup and configuration.
"""
import pytest
from app import create_app, db
from app.models import User


class TestAppSetup:
    """Test application setup and basic functionality."""
    
    def test_app_creation(self):
        """Test that the application can be created."""
        app = create_app('testing')
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_app_context(self, app_context):
        """Test that application context works."""
        assert app_context is not None
    
    def test_database_connection(self, db_session):
        """Test that database connection works."""
        # Create a test user
        user = User(
            email='test@example.com',
            password_hash='test_hash'
        )
        user.save()
        
        # Verify user was created
        retrieved_user = User.query.filter_by(email='test@example.com').first()
        assert retrieved_user is not None
        assert retrieved_user.email == 'test@example.com'
    
    def test_home_page(self, client):
        """Test that home page loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Fact Checker' in response.data
    
    def test_404_error_page(self, client):
        """Test that 404 error page works."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'Page Not Found' in response.data


class TestConfiguration:
    """Test configuration management."""
    
    def test_development_config(self):
        """Test development configuration."""
        app = create_app('development')
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False
    
    def test_testing_config(self):
        """Test testing configuration."""
        app = create_app('testing')
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is True
        assert 'memory' in app.config['SQLALCHEMY_DATABASE_URI']
    
    def test_production_config(self):
        """Test production configuration."""
        app = create_app('production')
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False


class TestModels:
    """Test basic model functionality."""
    
    def test_base_model_methods(self, db_session):
        """Test BaseModel methods."""
        user = User(
            email='test@example.com',
            password_hash='test_hash'
        )
        
        # Test save method
        user.save()
        assert user.id is not None
        assert user.created_at is not None
        
        # Test to_dict method
        user_dict = user.to_dict()
        assert isinstance(user_dict, dict)
        assert user_dict['email'] == 'test@example.com'
        
        # Test soft delete
        user.delete()
        assert user.is_deleted is True
        assert user.deleted_at is not None
    
    def test_user_model_relationships(self, db_session, sample_user, sample_user_profile):
        """Test User model relationships."""
        assert sample_user.profile is not None
        assert sample_user.profile.name == 'Test User'
        assert sample_user_profile.user == sample_user
