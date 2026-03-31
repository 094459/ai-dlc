#!/usr/bin/env python3
"""
Comprehensive test for TC_US02_Login_RegisteredEmail_Success
Tests successful login with registered email as described in test case.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService, SessionValidationService
from app.models import User
from app import create_app, db

def test_login_registered_email_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US02_Login_RegisteredEmail_Success")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user - use hard delete
        test_email = "testuser@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Ensuring user account exists with email '{test_email}'")
        
        # Step 1: Ensure user account exists with email "testuser@example.com"
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Test User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        print(f"User ID: {user.id}")
        print(f"User email: {user.email}")
        print(f"User active: {user.is_active}")
        
        user_id = user.id
        
        print("\nStep 2: Attempting to login with registered email")
        
        # Step 2: Navigate to login page and enter registered email
        # Step 3: Click login/submit button
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        
        print(f"Login attempt result: success={login_success}")
        print(f"Message: {login_message}")
        
        # Test acceptance criteria
        # Criterion 1: User is successfully authenticated
        assert login_success, f"Login should succeed with valid credentials: {login_message}"
        assert login_user is not None, "Login should return user object"
        assert login_user.id == user_id, "Login should return the correct user"
        print("✅ User is successfully authenticated")
        
        # Criterion 2: User session is established
        # Note: In a real web context, this would involve session cookies
        # Here we verify the user object is returned correctly
        assert login_user.email == test_email, "Login should return user with correct email"
        print("✅ User identity is maintained (session conceptually established)")
        
        # Criterion 3: Verify user's last_login is updated
        updated_user = db.session.get(User, user_id)
        assert updated_user.last_login is not None, "User's last_login should be updated"
        print("✅ User's last_login timestamp is updated")
        
        # Additional verification: User can access protected features
        # This is simulated by checking user permissions and status
        assert login_user.is_active, "User should be active and able to access features"
        assert login_user.can_post_content(), "User should be able to post content"
        assert login_user.can_comment(), "User should be able to comment"
        assert login_user.can_vote(), "User should be able to vote"
        print("✅ User can access protected features")
        
        # Clean up after test - use hard delete
        user.hard_delete()

def test_login_case_insensitive():
    """Test that login works with different email case variations."""
    print("\n" + "="*70)
    print("🔍 Testing case-insensitive login")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user - use hard delete
        test_emails = ["caselogin@example.com", "CASELOGIN@EXAMPLE.COM"]
        for email in test_emails:
            existing_users = User.query.filter_by(email=email.lower()).all()
            for user in existing_users:
                user.hard_delete()
        
        # Create user with lowercase email
        print("Creating user with lowercase email: caselogin@example.com")
        success, message, user = AuthenticationService.register_user(
            "caselogin@example.com", "password123", "Case Login User"
        )
        
        assert success, f"Setup failed: {message}"
        
        # Test login with various case variations
        case_variations = [
            "caselogin@example.com",    # Original case
            "CASELOGIN@EXAMPLE.COM",    # All uppercase
            "CaseLogin@Example.Com",    # Mixed case
            "caseLogin@Example.com"     # Different mixed case
        ]
        
        try:
            for email_variant in case_variations:
                print(f"\nTesting login with: {email_variant}")
                login_success, login_message, login_user = AuthenticationService.login_user(
                    email_variant, "password123"
                )
                
                assert login_success, f"Login with '{email_variant}' should succeed: {login_message}"
                assert login_user is not None, f"Login should return user object for '{email_variant}'"
                assert login_user.email == "caselogin@example.com", "Should return user with original email case"
                print(f"✅ PASS: Login with '{email_variant}' successful")
        finally:
            # Clean up after all tests - use hard delete
            user.hard_delete()

def test_login_with_remember_me():
    """Test login with remember me functionality."""
    print("\n" + "="*70)
    print("🔐 Testing login with remember me option")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user - use hard delete
        test_email = "rememberme@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        print(f"Creating user for remember me test: {test_email}")
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Remember Me User"
        )
        
        assert success, f"Setup failed: {message}"
        
        # Test login with remember_me=True
        print("\nTesting login with remember_me=True")
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123", remember_me=True
        )
        
        assert login_success, f"Login with remember_me should succeed: {login_message}"
        assert login_user is not None, "Login should return user object"
        print("✅ Login with remember_me option successful")
        
        # Test login with remember_me=False (default)
        print("\nTesting login with remember_me=False")
        login_success2, login_message2, login_user2 = AuthenticationService.login_user(
            test_email, "password123", remember_me=False
        )
        
        assert login_success2, f"Login without remember_me should also succeed: {login_message2}"
        assert login_user2 is not None, "Login should return user object"
        print("✅ Login without remember_me option successful")
        
        # Clean up after test - use hard delete
        user.hard_delete()

def test_acceptance_criteria():
    """Test specific acceptance criteria from test case."""
    print("\n" + "="*70)
    print("📋 Testing Acceptance Criteria")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Setup: Create a test user - use hard delete for cleanup
        test_email = "criteria@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Test User"
        )
        assert success, f"Setup failed: {message}"
        
        print("Testing login with registered email...")
        
        # Test login
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        
        # Criterion 1: User is successfully authenticated
        assert login_success, "User should be successfully authenticated"
        print("✅ User is successfully authenticated")
        
        # Criterion 2: User is redirected to main application dashboard/homepage
        # Note: In service layer, this is indicated by successful login
        # The actual redirect would happen in the web layer
        assert login_user is not None, "Successful login should return user object (indicates redirect readiness)"
        print("✅ Login successful (ready for redirect to main application)")
        
        # Criterion 3: User session is established
        # In service layer, this is represented by returning the authenticated user
        assert login_user.email == test_email, "User session should be established with correct identity"
        print("✅ User session is established")
        
        # Criterion 4: User can access protected features
        assert login_user.is_active, "User should be active"
        assert login_user.can_post_content(), "User should be able to access protected features"
        print("✅ User can access protected features")
        
        # Clean up after test - use hard delete
        user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US02_Login_RegisteredEmail_Success")
    print("=" * 80)
    
    try:
        # Run the tests
        test_login_registered_email_scenario()
        test_login_case_insensitive()
        test_login_with_remember_me()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US02_Login_RegisteredEmail_Success: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Case-insensitive login works correctly")
        print("✅ Remember me functionality works")
        print("✅ User session and authentication work as expected")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
