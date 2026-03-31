#!/usr/bin/env python3
"""
Comprehensive test for TC_US02_Login_SessionPersistence_MaintainLogin
Tests session persistence and login maintenance functionality.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime, timedelta
from app.components.auth.services import AuthenticationService, SessionValidationService
from app.models import User, UserSession
from app import create_app, db
from flask import session

def test_session_persistence_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US02_Login_SessionPersistence_MaintainLogin")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "sessionuser@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating user account with email '{test_email}'")
        
        # Step 1: Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Session Test User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        user_id = user.id
        
        print("\nStep 2: User logs in with 'Remember Me' option")
        
        # Step 2: Login with remember_me=True
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123", remember_me=True
        )
        
        assert login_success, f"Login should succeed: {login_message}"
        assert login_user is not None, "Login should return user object"
        print("✅ User logged in successfully with 'Remember Me' option")
        
        # Verify session was created
        session_token = session.get('session_token')
        user_session_id = session.get('user_id')
        
        assert session_token is not None, "Session token should be created"
        assert user_session_id == user_id, "Session should contain correct user ID"
        assert session.permanent is True, "Session should be marked as permanent"
        print("✅ Session created and marked as permanent")
        
        # Verify session in database
        user_session = UserSession.query.filter_by(
            user_id=user_id,
            session_token=session_token
        ).first()
        
        assert user_session is not None, "Session should be stored in database"
        assert not user_session.is_expired(), "Session should not be expired"
        print("✅ Session stored in database and not expired")
        
        print("\nStep 3: Testing session persistence across requests")
        
        # Step 3: Simulate new request - session should persist
        current_user = SessionValidationService.get_current_user()
        
        assert current_user is not None, "Session should persist across requests"
        assert current_user.id == user_id, "Session should return correct user"
        assert current_user.email == test_email, "Session should return correct user data"
        print("✅ Session persists across requests")
        
        # Test authentication check
        is_authenticated = SessionValidationService.is_authenticated()
        assert is_authenticated, "User should be authenticated"
        print("✅ User authentication status maintained")
        
        print("\nStep 4: Testing long-term session expiration")
        
        # Verify session has long expiration (30 days for remember_me)
        expected_min_expiry = datetime.utcnow() + timedelta(days=29)
        assert user_session.expires_at > expected_min_expiry, "Session should have long expiration (30 days)"
        print("✅ Session has long-term expiration (30+ days)")
        
        # Clean up after test
        user.hard_delete()

def test_session_without_remember_me():
    """Test session behavior without 'Remember Me' option."""
    print("\n" + "="*70)
    print("🔍 Testing session without 'Remember Me' option")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "shortsession@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Short Session User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Login without remember_me (default is False)
            login_success, login_message, login_user = AuthenticationService.login_user(
                test_email, "password123", remember_me=False
            )
            
            assert login_success, f"Login should succeed: {login_message}"
            print("✅ User logged in without 'Remember Me' option")
            
            # Verify session properties
            session_token = session.get('session_token')
            assert session_token is not None, "Session token should be created"
            assert session.permanent is False, "Session should not be marked as permanent"
            print("✅ Session created but not marked as permanent")
            
            # Verify shorter expiration in database
            user_session = UserSession.query.filter_by(
                user_id=user.id,
                session_token=session_token
            ).first()
            
            assert user_session is not None, "Session should be stored in database"
            
            # Session should expire in hours, not days
            max_expected_expiry = datetime.utcnow() + timedelta(days=1)
            assert user_session.expires_at < max_expected_expiry, "Session should have short expiration (hours)"
            print("✅ Session has short-term expiration (hours)")
            
        finally:
            # Clean up after test
            user.hard_delete()

def test_session_expiration_handling():
    """Test handling of expired sessions."""
    print("\n" + "="*70)
    print("⏰ Testing expired session handling")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "expireduser@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Expired Session User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Login to create session
            login_success, login_message, login_user = AuthenticationService.login_user(
                test_email, "password123", remember_me=False
            )
            assert login_success, f"Login should succeed: {login_message}"
            
            session_token = session.get('session_token')
            
            # Manually expire the session in database
            user_session = UserSession.query.filter_by(
                user_id=user.id,
                session_token=session_token
            ).first()
            
            assert user_session is not None, "Session should exist"
            
            # Set expiration to past
            user_session.expires_at = datetime.utcnow() - timedelta(hours=1)
            user_session.save()
            print("✅ Session manually expired")
            
            # Try to get current user - should return None and clean up session
            current_user = SessionValidationService.get_current_user()
            
            assert current_user is None, "Expired session should return no user"
            print("✅ Expired session correctly returns no user")
            
            # Verify session was cleaned up
            remaining_session = UserSession.query.filter_by(
                user_id=user.id,
                session_token=session_token,
                is_deleted=False
            ).first()
            
            assert remaining_session is None, "Expired session should be cleaned up from database"
            print("✅ Expired session cleaned up from database")
            
            # Verify Flask session was cleared
            assert session.get('user_id') is None, "Flask session should be cleared"
            assert session.get('session_token') is None, "Session token should be cleared"
            print("✅ Flask session cleared")
            
        finally:
            # Clean up after test
            user.hard_delete()

def test_session_logout():
    """Test session cleanup during logout."""
    print("\n" + "="*70)
    print("🚪 Testing session cleanup during logout")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "logoutuser@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Logout Test User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Login to create session
            login_success, login_message, login_user = AuthenticationService.login_user(
                test_email, "password123", remember_me=True
            )
            assert login_success, f"Login should succeed: {login_message}"
            
            session_token = session.get('session_token')
            user_id = user.id
            
            # Verify session exists
            user_session = UserSession.query.filter_by(
                user_id=user_id,
                session_token=session_token
            ).first()
            assert user_session is not None, "Session should exist before logout"
            print("✅ Session exists before logout")
            
            # Logout
            logout_success = AuthenticationService.logout_user(user_id)
            assert logout_success, "Logout should succeed"
            print("✅ Logout successful")
            
            # Verify session was cleaned up from database
            remaining_session = UserSession.query.filter_by(
                user_id=user_id,
                session_token=session_token,
                is_deleted=False
            ).first()
            assert remaining_session is None, "Session should be removed from database"
            print("✅ Session removed from database")
            
            # Verify Flask session was cleared
            assert session.get('user_id') is None, "Flask session should be cleared"
            assert session.get('session_token') is None, "Session token should be cleared"
            print("✅ Flask session cleared")
            
            # Verify user is no longer authenticated
            current_user = SessionValidationService.get_current_user()
            assert current_user is None, "User should not be authenticated after logout"
            
            is_authenticated = SessionValidationService.is_authenticated()
            assert not is_authenticated, "User should not be authenticated after logout"
            print("✅ User no longer authenticated")
            
        finally:
            # Clean up after test
            user.hard_delete()

def test_acceptance_criteria():
    """Test specific acceptance criteria from test case."""
    print("\n" + "="*70)
    print("📋 Testing Acceptance Criteria")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Setup: Create a test user
        test_email = "criteria@session.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Test User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Testing login with 'Remember Me' option...")
            
            # Test login with remember_me
            login_success, login_message, login_user = AuthenticationService.login_user(
                test_email, "password123", remember_me=True
            )
            
            # Criterion 1: User session is maintained across browser sessions
            assert login_success, "Login with remember_me should succeed"
            assert session.permanent is True, "Session should be marked as permanent"
            print("✅ User session is maintained across browser sessions")
            
            # Criterion 2: User remains logged in when returning to the application
            current_user = SessionValidationService.get_current_user()
            assert current_user is not None, "User should remain logged in"
            assert current_user.id == user.id, "Correct user should be returned"
            print("✅ User remains logged in when returning to the application")
            
            # Criterion 3: Session persists for extended period (30 days for remember_me)
            session_token = session.get('session_token')
            user_session = UserSession.query.filter_by(
                user_id=user.id,
                session_token=session_token
            ).first()
            
            expected_min_expiry = datetime.utcnow() + timedelta(days=29)
            assert user_session.expires_at > expected_min_expiry, "Session should persist for extended period"
            print("✅ Session persists for extended period (30+ days)")
            
            # Criterion 4: User can access protected features without re-authentication
            is_authenticated = SessionValidationService.is_authenticated()
            assert is_authenticated, "User should be able to access protected features"
            assert current_user.can_post_content(), "User should have access to protected features"
            print("✅ User can access protected features without re-authentication")
            
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US02_Login_SessionPersistence_MaintainLogin")
    print("=" * 80)
    
    try:
        # Run the tests
        test_session_persistence_scenario()
        test_session_without_remember_me()
        test_session_expiration_handling()
        test_session_logout()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US02_Login_SessionPersistence_MaintainLogin: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Session persistence works correctly with 'Remember Me'")
        print("✅ Short-term sessions work correctly without 'Remember Me'")
        print("✅ Expired session handling works correctly")
        print("✅ Session cleanup during logout works correctly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
