#!/usr/bin/env python3
"""
Comprehensive test for TC_US01_Registration_DuplicateEmail_ErrorMessage
Tests the specific scenario with existing@test.com as described in test case.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService
from app.models import User
from app import create_app, db

def test_duplicate_email_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US01_Registration_DuplicateEmail_ErrorMessage")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test data - use hard delete
        test_email = "existing@test.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating existing user account with email '{test_email}'")
        
        # Step 1: Ensure a user account already exists with email "existing@test.com"
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Existing User"
        )
        
        assert success, f"Setup failed: Could not create existing user - {message}"
        print("✅ Existing user account created successfully")
        existing_user_id = user.id
        
        print(f"\nStep 2: Attempting to register with the same email '{test_email}'")
        
        # Step 2: Submit registration with duplicate email
        success, message, duplicate_user = AuthenticationService.register_user(
            test_email, "differentpassword", "Different User"
        )
        
        print(f"Registration attempt result: success={success}")
        print(f"Message: {message}")
        
        # Test acceptance criteria
        # Criterion 1: Error message clearly states email is already registered
        assert not success, "Registration should fail with duplicate email"
        assert ('already' in message.lower() and ('registered' in message.lower() or 'exists' in message.lower())), \
            f"Error message should clearly state email is already registered: '{message}'"
        print("✅ Error message clearly states email is already registered")
        
        # Criterion 2: No duplicate account is created
        assert duplicate_user is None, "No duplicate account should be created"
        print("✅ No duplicate account is created")
        
        # Criterion 3: Verify only one account exists with this email
        all_users_with_email = User.query.filter_by(email=test_email).all()
        assert len(all_users_with_email) == 1, f"Expected 1 account, found {len(all_users_with_email)}"
        print("✅ Only one account exists with this email")
        
        # Criterion 4: Original user account remains unchanged
        original_user = db.session.get(User, existing_user_id)
        assert original_user is not None, "Original user should still exist"
        assert original_user.profile.name == "Existing User", "Original user profile should be unchanged"
        print("✅ Original user account remains unchanged")
        
        # Additional test: Verify user can still login with original account
        print("\nStep 3: Verifying original user can still login")
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        
        assert login_success, f"Original user should be able to login: {login_message}"
        assert login_user.id == existing_user_id, "Login should return the original user"
        print("✅ Original user can still login successfully")
        
        # Clean up after test - use hard delete
        user.hard_delete()

def test_case_insensitive_duplicate_detection():
    """Test that duplicate detection works with different case variations."""
    print("\n" + "="*70)
    print("🔍 Testing case-insensitive duplicate detection")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test data - use hard delete
        test_emails = ["casetest@example.com", "CASETEST@EXAMPLE.COM", "CaseTest@Example.Com"]
        for email in test_emails:
            existing_users = User.query.filter_by(email=email.lower()).all()
            for user in existing_users:
                user.hard_delete()
        
        # Create user with lowercase email
        print("Creating user with lowercase email: casetest@example.com")
        success, message, user = AuthenticationService.register_user(
            "casetest@example.com", "password123", "Case Test User"
        )
        
        assert success, f"Setup failed: {message}"
        
        # Test various case variations
        case_variations = [
            "CASETEST@EXAMPLE.COM",
            "CaseTest@Example.Com", 
            "caseTest@Example.com"
        ]
        
        try:
            for email_variant in case_variations:
                print(f"\nTesting duplicate registration with: {email_variant}")
                success, message, duplicate_user = AuthenticationService.register_user(
                    email_variant, "password123", "Duplicate User"
                )
                
                assert not success, f"Registration with '{email_variant}' should fail due to case-insensitive duplicate detection: {message}"
                assert duplicate_user is None, f"No duplicate user should be created for '{email_variant}'"
                print(f"✅ PASS: Registration with '{email_variant}' correctly rejected")
        finally:
            # Clean up after test - use hard delete
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US01_Registration_DuplicateEmail_ErrorMessage")
    print("=" * 80)
    
    try:
        # Run the tests
        test_duplicate_email_scenario()
        test_case_insensitive_duplicate_detection()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US01_Registration_DuplicateEmail_ErrorMessage: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Case-insensitive duplicate detection works correctly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
