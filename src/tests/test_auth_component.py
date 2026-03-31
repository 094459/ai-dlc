"""
Tests for authentication component.
"""
import pytest
from app.components.auth.services import AuthenticationService, SessionValidationService
from app.components.security.services import ValidationService
from app.models import User, UserProfile, UserSession


class TestAuthenticationService:
    """Test authentication service functionality."""
    
    def test_register_user_success(self, db_session):
        """Test successful user registration."""
        success, message, user = AuthenticationService.register_user(
            'test@example.com', 'password123', 'Test User'
        )
        
        assert success is True
        assert 'successful' in message
        assert user is not None
        assert user.email == 'test@example.com'
        assert user.is_active is True
        
        # Check profile was created
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        assert profile is not None
        assert profile.name == 'Test User'
    
    def test_register_user_duplicate_email(self, db_session, sample_user):
        """Test registration with duplicate email."""
        success, message, user = AuthenticationService.register_user(
            sample_user.email, 'password123', 'Another User'
        )
        
        assert success is False
        assert 'already registered' in message
        assert user is None
    
    def test_register_user_invalid_email(self, db_session):
        """Test registration with invalid email."""
        success, message, user = AuthenticationService.register_user(
            'invalid-email', 'password123', 'Test User'
        )
        
        assert success is False
        assert 'Invalid email' in message
        assert user is None
    
    def test_register_user_weak_password(self, db_session):
        """Test registration with weak password."""
        success, message, user = AuthenticationService.register_user(
            'test@example.com', '123', 'Test User'
        )
        
        assert success is False
        assert 'at least 8 characters' in message
        assert user is None
    
    def test_login_user_success(self, db_session):
        """Test successful user login."""
        # First register a user
        AuthenticationService.register_user(
            'test@example.com', 'password123', 'Test User'
        )
        
        # Then login
        success, message, user = AuthenticationService.login_user(
            'test@example.com', 'password123'
        )
        
        assert success is True
        assert 'successful' in message
        assert user is not None
        assert user.email == 'test@example.com'
        assert user.last_login is not None
    
    def test_login_user_invalid_email(self, db_session):
        """Test login with non-existent email."""
        success, message, user = AuthenticationService.login_user(
            'nonexistent@example.com', 'password123'
        )
        
        assert success is False
        assert 'Invalid email or password' in message
        assert user is None
    
    def test_login_user_wrong_password(self, db_session):
        """Test login with wrong password."""
        # First register a user
        AuthenticationService.register_user(
            'test@example.com', 'password123', 'Test User'
        )
        
        # Then try wrong password
        success, message, user = AuthenticationService.login_user(
            'test@example.com', 'wrongpassword'
        )
        
        assert success is False
        assert 'Invalid email or password' in message
        assert user is None
    
    def test_login_inactive_user(self, db_session):
        """Test login with inactive user."""
        # Register and deactivate user
        success, message, user = AuthenticationService.register_user(
            'test@example.com', 'password123', 'Test User'
        )
        user.is_active = False
        user.save()
        
        # Try to login
        success, message, login_user = AuthenticationService.login_user(
            'test@example.com', 'password123'
        )
        
        assert success is False
        assert 'inactive' in message
        assert login_user is None


class TestSessionValidationService:
    """Test session validation service functionality."""
    
    def test_get_current_user_no_session(self, app_context):
        """Test getting current user with no session."""
        user = SessionValidationService.get_current_user()
        assert user is None
    
    def test_is_authenticated_no_session(self, app_context):
        """Test authentication check with no session."""
        assert SessionValidationService.is_authenticated() is False


class TestValidationService:
    """Test validation service functionality."""
    
    def test_validate_email_valid(self):
        """Test valid email validation."""
        valid, message = ValidationService.validate_email('test@example.com')
        assert valid is True
        assert 'Valid' in message
    
    def test_validate_email_invalid_format(self):
        """Test invalid email format."""
        valid, message = ValidationService.validate_email('invalid-email')
        assert valid is False
        assert 'Invalid email format' in message
    
    def test_validate_email_empty(self):
        """Test empty email validation."""
        valid, message = ValidationService.validate_email('')
        assert valid is False
        assert 'required' in message
    
    def test_validate_password_valid(self):
        """Test valid password validation."""
        valid, message = ValidationService.validate_password('password123')
        assert valid is True
        assert 'Valid' in message
    
    def test_validate_password_too_short(self):
        """Test password too short."""
        valid, message = ValidationService.validate_password('123')
        assert valid is False
        assert 'at least 8 characters' in message
    
    def test_validate_password_no_letter(self):
        """Test password without letters."""
        valid, message = ValidationService.validate_password('12345678')
        assert valid is False
        assert 'at least one letter' in message
    
    def test_validate_password_no_number(self):
        """Test password without numbers."""
        valid, message = ValidationService.validate_password('password')
        assert valid is False
        assert 'at least one number' in message
    
    def test_validate_name_valid(self):
        """Test valid name validation."""
        valid, message = ValidationService.validate_name('John Doe')
        assert valid is True
        assert 'Valid' in message
    
    def test_validate_name_too_short(self):
        """Test name too short."""
        valid, message = ValidationService.validate_name('J')
        assert valid is False
        assert 'at least 2 characters' in message
    
    def test_validate_name_invalid_characters(self):
        """Test name with invalid characters."""
        valid, message = ValidationService.validate_name('John123')
        assert valid is False
        assert 'invalid characters' in message
    
    def test_sanitize_html(self):
        """Test HTML sanitization."""
        dirty_html = '<script>alert("xss")</script><p>Hello</p>'
        clean_html = ValidationService.sanitize_html(dirty_html)
        
        assert '<script>' not in clean_html
        assert 'javascript:' not in clean_html
        # The content is HTML escaped, so we check for escaped content
        assert '&lt;' in clean_html  # < is escaped
        assert '&gt;' in clean_html  # > is escaped
