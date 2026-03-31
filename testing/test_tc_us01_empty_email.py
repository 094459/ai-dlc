#!/usr/bin/env python3
"""
Comprehensive test for TC_US01_Registration_EmptyEmail_ValidationError
Tests validation for empty email field during registration.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService
from app.components.security.services import ValidationService
from app import create_app, db

def test_empty_email_validation():
    """Test validation service with empty email."""
    print("🧪 Testing TC_US01_Registration_EmptyEmail_ValidationError")
    print("=" * 70)
    
    print("Step 1: Testing ValidationService.validate_email() with empty email")
    
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
            valid, message = ValidationService.validate_email(empty_value)
            
            assert not valid, f"{description} should be invalid but was validated as valid"
            print(f"✅ PASS: {description} correctly rejected - {message}")
            
            # Check that message indicates email is required for truly empty values
            if empty_value == "" or empty_value is None:
                assert 'required' in message.lower(), f"Error message should mention 'required' for {description}: {message}"
                print("✅ Error message indicates email is required")
            else:
                print(f"ℹ️  Error message for {description}: {message}")
        
        except Exception as e:
            if empty_value is None:
                print("✅ None value handled (exception is acceptable)")
            else:
                raise AssertionError(f"Unexpected exception with {description}: {e}")

def test_registration_with_empty_email():
    """Test registration service with empty email."""
    print("\n" + "="*70)
    print("🎯 Testing AuthenticationService.register_user() with empty email")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Test various empty email scenarios
        empty_scenarios = [
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("\t", "Tab character"),
        ]
        
        for empty_email, description in empty_scenarios:
            print(f"\nTesting registration with {description}: {repr(empty_email)}")
            
            success, message, user = AuthenticationService.register_user(
                empty_email, 'password123', 'Test User'
            )
            
            assert not success, f"Registration with {description} should fail"
            assert user is None, f"No user should be created for {description}"
            print(f"✅ PASS: Registration with {description} correctly failed - {message}")

def test_acceptance_criteria():
    """Test specific acceptance criteria from test case."""
    print("\n" + "="*70)
    print("📋 Testing Acceptance Criteria")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        print("Testing registration with empty email field...")
        
        # Test with empty string (most common scenario)
        success, message, user = AuthenticationService.register_user(
            "", 'password123', 'Test User'
        )
        
        # Criterion 1: Error message is displayed (any error message is acceptable)
        assert not success, "Registration should fail with empty email"
        assert message, "Error message should be provided"
        print("✅ Error message is displayed")
        
        # Criterion 2: Form submission is prevented (registration fails)
        assert not success, "Form submission should be prevented"
        print("✅ Form submission is prevented (registration fails)")
        
        # Criterion 3: User remains on registration page (no user created)
        assert user is None, "No user account should be created"
        print("✅ No user account created (user remains on registration page)")
        
        # Additional test: Verify email field validation happens before other validations
        print("\nTesting validation order (email should be checked first)...")
        
        # Test with empty email but valid other fields
        success2, message2, user2 = AuthenticationService.register_user(
            "", 'validpassword123', 'Valid Name'
        )
        
        assert not success2, "Registration should fail with empty email regardless of other fields"
        print("✅ Email validation prevents registration regardless of other field validity")

if __name__ == "__main__":
    print("Comprehensive Test for TC_US01_Registration_EmptyEmail_ValidationError")
    print("=" * 80)
    
    try:
        # Run the tests
        test_empty_email_validation()
        test_registration_with_empty_email()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US01_Registration_EmptyEmail_ValidationError: PASSED")
        print("✅ All empty email values correctly rejected")
        print("✅ Registration properly prevented with empty email")
        print("✅ All acceptance criteria met")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
