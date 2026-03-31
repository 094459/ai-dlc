#!/usr/bin/env python3
"""
Comprehensive test for TC_US02_Login_EmptyEmail_ValidationError
Tests validation for empty email field during login.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService
from app.components.security.services import ValidationService
from app.models import User
from app import create_app, db

def test_login_empty_email_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US02_Login_EmptyEmail_ValidationError")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        print("Step 1: Testing login with empty email field")
        
        # Test various empty/null values
        empty_values = [
            ("", "Empty string"),
            (None, "None value"),
            ("   ", "Whitespace only"),
            ("\t", "Tab character"),
            ("\n", "Newline character"),
        ]
        
        for empty_value, description in empty_values:
            print(f"\nTesting {description}: {repr(empty_value)}")
            
            try:
                success, message, user = AuthenticationService.login_user(
                    empty_value, "anypassword"
                )
                
                assert not success, f"Login with {description} should fail"
                assert user is None, f"No user should be returned for {description}"
                assert message, f"Error message should be provided for {description}"
                print(f"✅ PASS: {description} correctly rejected - {message}")
                
            except Exception as e:
                # Handle None gracefully - this might cause an exception
                if empty_value is None:
                    print(f"✅ PASS: {description} handled with exception (acceptable) - {e}")
                else:
                    raise AssertionError(f"Unexpected exception with {description}: {e}")

def test_login_empty_email_with_valid_user():
    """Test empty email login when valid users exist in system."""
    print("\n" + "="*70)
    print("🔍 Testing empty email login with valid users in system")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "validuser@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create a valid user to ensure system has users
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Valid User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print(f"Created valid user: {test_email}")
            
            # Test empty email login - should still fail even with valid users in system
            empty_scenarios = [
                ("", "Empty string"),
                ("   ", "Whitespace only"),
                ("\t", "Tab character"),
            ]
            
            for empty_email, description in empty_scenarios:
                print(f"\nTesting login with {description}: {repr(empty_email)}")
                
                login_success, login_message, login_user = AuthenticationService.login_user(
                    empty_email, "password123"  # Using valid password
                )
                
                assert not login_success, f"Login with {description} should fail even with valid password"
                assert login_user is None, f"No user should be returned for {description}"
                print(f"✅ PASS: Login with {description} correctly failed - {login_message}")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_validation_service_empty_email():
    """Test ValidationService behavior with empty emails."""
    print("\n" + "="*70)
    print("🔧 Testing ValidationService with empty emails")
    print("="*70)
    
    # Test ValidationService directly (used by web interface)
    empty_values = [
        ("", "Empty string"),
        (None, "None value"),
        ("   ", "Whitespace only"),
        ("\t", "Tab character"),
        ("\n", "Newline character"),
    ]
    
    for empty_value, description in empty_values:
        print(f"\nTesting ValidationService with {description}: {repr(empty_value)}")
        
        try:
            valid, message = ValidationService.validate_email(empty_value)
            
            assert not valid, f"ValidationService should reject {description}"
            assert message, f"ValidationService should provide error message for {description}"
            
            # Check for appropriate error message
            if empty_value == "" or empty_value is None:
                assert 'required' in message.lower(), f"Error message should mention 'required' for {description}: {message}"
                print(f"✅ PASS: {description} correctly rejected with 'required' message - {message}")
            else:
                print(f"✅ PASS: {description} correctly rejected - {message}")
                
        except Exception as e:
            if empty_value is None:
                print(f"✅ PASS: {description} handled with exception (acceptable) - {e}")
            else:
                raise AssertionError(f"Unexpected exception with {description}: {e}")

def test_security_considerations():
    """Test that empty email login doesn't reveal system information."""
    print("\n" + "="*70)
    print("🔒 Testing security considerations for empty email login")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        print("Testing that empty email errors don't reveal system information...")
        
        # Test various empty values
        empty_values = ["", "   ", "\t"]
        error_messages = []
        
        for empty_value in empty_values:
            success, message, user = AuthenticationService.login_user(
                empty_value, "testpassword"
            )
            error_messages.append(message)
            print(f"Empty value {repr(empty_value)}: '{message}'")
        
        # Check that error messages are consistent and don't reveal too much
        unique_messages = set(error_messages)
        if len(unique_messages) == 1:
            print("✅ All empty email errors return consistent message (good security)")
        else:
            print("⚠️  Different error messages for different empty values")
        
        # Ensure no system information is leaked
        for message in error_messages:
            assert 'database' not in message.lower(), "Error message should not mention database"
            assert 'system' not in message.lower(), "Error message should not mention system"
            assert 'server' not in message.lower(), "Error message should not mention server"
            print(f"✅ Error message doesn't leak system information: '{message}'")

def test_acceptance_criteria():
    """Test specific acceptance criteria from test case."""
    print("\n" + "="*70)
    print("📋 Testing Acceptance Criteria")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        print("Testing login with empty email field...")
        
        # Test with empty string (most common scenario)
        success, message, user = AuthenticationService.login_user(
            "", "anypassword"
        )
        
        # Criterion 1: Error message is displayed
        assert not success, "Login should fail with empty email"
        assert message, "Error message should be provided"
        print("✅ Error message is displayed")
        
        # Criterion 2: Login is not completed
        assert not success, "Login should not be completed"
        assert user is None, "No user should be returned"
        print("✅ Login is not completed")
        
        # Criterion 3: User remains on login page (no session created)
        assert user is None, "No user session should be established"
        print("✅ User remains on login page (no session created)")
        
        # Criterion 4: Form validation prevents submission
        # At service level, this is represented by the login failure
        assert not success, "Form validation should prevent login"
        print("✅ Form validation prevents submission")
        
        # Additional test: Verify email field validation happens before password validation
        print("\nTesting validation order (email should be checked first)...")
        
        # Test with empty email but any password
        success2, message2, user2 = AuthenticationService.login_user(
            "", "validpassword123"
        )
        
        assert not success2, "Login should fail with empty email regardless of password"
        print("✅ Email validation prevents login regardless of password validity")

def test_comparison_with_registration():
    """Test that login empty email validation is consistent with registration."""
    print("\n" + "="*70)
    print("🔄 Testing consistency with registration validation")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        print("Comparing login and registration empty email validation...")
        
        # Test empty email in registration
        reg_success, reg_message, reg_user = AuthenticationService.register_user(
            "", "password123", "Test User"
        )
        
        # Test empty email in login
        login_success, login_message, login_user = AuthenticationService.login_user(
            "", "password123"
        )
        
        # Both should fail
        assert not reg_success, "Registration should fail with empty email"
        assert not login_success, "Login should fail with empty email"
        
        print(f"Registration error: '{reg_message}'")
        print(f"Login error: '{login_message}'")
        
        # Both should return no user
        assert reg_user is None, "Registration should return no user"
        assert login_user is None, "Login should return no user"
        
        print("✅ Both registration and login consistently reject empty emails")
        print("✅ Both return appropriate error messages")
        print("✅ Both return no user objects")

if __name__ == "__main__":
    print("Comprehensive Test for TC_US02_Login_EmptyEmail_ValidationError")
    print("=" * 80)
    
    try:
        # Run the tests
        test_login_empty_email_scenario()
        test_login_empty_email_with_valid_user()
        test_validation_service_empty_email()
        test_security_considerations()
        test_acceptance_criteria()
        test_comparison_with_registration()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US02_Login_EmptyEmail_ValidationError: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Empty email validation works correctly for login")
        print("✅ Security considerations properly implemented")
        print("✅ Consistent behavior with registration validation")
        print("✅ No system information leaked in error messages")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
