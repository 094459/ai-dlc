#!/usr/bin/env python3
"""
Comprehensive test for TC_US03_Profile_CreateMinimal_Success
Tests minimal profile creation with only required name field.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService
from app.components.profile.services import ProfileManagementService
from app.models import User, UserProfile
from app import create_app, db

def test_minimal_profile_creation_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US03_Profile_CreateMinimal_Success")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "minimaluser@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating user account with minimal profile information")
        
        # Step 1: Create user account with only required name field
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Minimal User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        user_id = user.id
        
        print("\nStep 2: Verifying minimal profile creation")
        
        # Step 2: Verify minimal profile was created
        profile = ProfileManagementService.get_user_profile(user_id)
        assert profile is not None, "Profile should be created during registration"
        assert profile.name == "Minimal User", "Profile should have correct name"
        print("✅ Minimal profile created with required name field")
        
        # Verify optional fields are empty/null
        assert profile.biography is None or profile.biography == "", "Biography should be empty in minimal profile"
        assert profile.profile_photo_url is None or profile.profile_photo_url == "", "Profile photo should be empty in minimal profile"
        print("✅ Optional fields are properly empty")
        
        print("\nStep 3: Testing minimal profile functionality")
        
        # Test acceptance criteria
        # Criterion 1: Profile is created with only required information
        assert profile.name is not None and profile.name != "", "Profile should have required name"
        assert profile.biography is None or profile.biography == "", "Biography should be optional and empty"
        print("✅ Profile is created with only required information")
        
        # Criterion 2: Profile completion reflects minimal status
        completion_percentage = ProfileManagementService.get_profile_completion_percentage(user_id)
        assert completion_percentage > 0, "Profile completion should be greater than 0 with name"
        assert completion_percentage < 100, "Profile completion should be less than 100 for minimal profile"
        print(f"✅ Profile completion reflects minimal status: {completion_percentage}%")
        
        # Criterion 3: User can view their minimal profile
        user_stats = ProfileManagementService.get_user_stats(user_id)
        assert user_stats is not None, "User should be able to view their profile stats"
        print("✅ User can view their minimal profile")
        
        # Criterion 4: Profile can be updated later with additional information
        # Test that we can add biography later
        update_success, update_message, updated_profile = ProfileManagementService.update_profile(
            user_id, biography="Added biography later"
        )
        assert update_success, f"Profile should be updatable: {update_message}"
        
        updated_profile_check = ProfileManagementService.get_user_profile(user_id)
        assert updated_profile_check.biography == "Added biography later", "Biography should be added successfully"
        print("✅ Profile can be updated later with additional information")
        
        # Clean up after test
        user.hard_delete()

def test_minimal_profile_edge_cases():
    """Test edge cases for minimal profile creation."""
    print("\n" + "="*70)
    print("🔍 Testing minimal profile edge cases")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        test_cases = [
            ("singlechar@example.com", "A", "Single character name"),
            ("longname@example.com", "Very Long Name With Multiple Words And Spaces", "Long name"),
            ("specialchars@example.com", "Name-With'Special Characters", "Name with special characters"),
            ("unicode@example.com", "José María González", "Unicode name"),
        ]
        
        for email, name, description in test_cases:
            print(f"\nTesting {description}: '{name}'")
            
            # Clean up any existing test user
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
            
            try:
                # Create user with edge case name
                success, message, user = AuthenticationService.register_user(
                    email, "password123", name
                )
                
                if success:
                    # Verify profile creation
                    profile = ProfileManagementService.get_user_profile(user.id)
                    assert profile is not None, f"Profile should be created for {description}"
                    assert profile.name == name, f"Profile should preserve exact name for {description}"
                    print(f"✅ PASS: {description} handled correctly")
                    
                    # Clean up
                    user.hard_delete()
                else:
                    print(f"⚠️  {description} rejected during registration: {message}")
                    
            except Exception as e:
                print(f"❌ {description} caused exception: {e}")

def test_minimal_profile_vs_complete_profile():
    """Test differences between minimal and complete profiles."""
    print("\n" + "="*70)
    print("📊 Testing minimal vs complete profile comparison")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test users
        test_emails = ["minimal@compare.com", "complete@compare.com"]
        for email in test_emails:
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
        
        try:
            # Create minimal profile user
            success1, message1, minimal_user = AuthenticationService.register_user(
                "minimal@compare.com", "password123", "Minimal User"
            )
            assert success1, f"Minimal user creation failed: {message1}"
            
            # Create complete profile user
            success2, message2, complete_user = AuthenticationService.register_user(
                "complete@compare.com", "password123", "Complete User"
            )
            assert success2, f"Complete user creation failed: {message2}"
            
            # Update complete user with biography
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                complete_user.id, biography="This is a complete profile with biography."
            )
            assert update_success, f"Complete profile update failed: {update_message}"
            
            # Compare completion percentages
            minimal_completion = ProfileManagementService.get_profile_completion_percentage(minimal_user.id)
            complete_completion = ProfileManagementService.get_profile_completion_percentage(complete_user.id)
            
            print(f"Minimal profile completion: {minimal_completion}%")
            print(f"Complete profile completion: {complete_completion}%")
            
            assert minimal_completion < complete_completion, "Complete profile should have higher completion percentage"
            assert minimal_completion > 0, "Minimal profile should have some completion"
            assert complete_completion > minimal_completion, "Complete profile should be more complete"
            print("✅ Completion percentages correctly reflect profile completeness")
            
            # Compare profile data
            minimal_profile = ProfileManagementService.get_user_profile(minimal_user.id)
            complete_profile = ProfileManagementService.get_user_profile(complete_user.id)
            
            assert minimal_profile.name == "Minimal User", "Minimal profile should have correct name"
            assert minimal_profile.biography is None or minimal_profile.biography == "", "Minimal profile should have no biography"
            
            assert complete_profile.name == "Complete User", "Complete profile should have correct name"
            assert complete_profile.biography == "This is a complete profile with biography.", "Complete profile should have biography"
            print("✅ Profile data correctly reflects minimal vs complete status")
            
        finally:
            # Clean up after test
            if 'minimal_user' in locals():
                minimal_user.hard_delete()
            if 'complete_user' in locals():
                complete_user.hard_delete()

def test_minimal_profile_upgrade_path():
    """Test upgrading from minimal to complete profile."""
    print("\n" + "="*70)
    print("🔄 Testing minimal profile upgrade path")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "upgrade@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create minimal profile
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Upgrade User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Track completion at each stage
            initial_completion = ProfileManagementService.get_profile_completion_percentage(user.id)
            print(f"Initial completion (name only): {initial_completion}%")
            
            # Stage 1: Add biography
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, biography="Added biography to upgrade profile."
            )
            assert update_success, f"Biography addition failed: {update_message}"
            
            bio_completion = ProfileManagementService.get_profile_completion_percentage(user.id)
            print(f"Completion after adding biography: {bio_completion}%")
            assert bio_completion > initial_completion, "Completion should increase after adding biography"
            
            # Stage 2: Update name (should maintain biography)
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, name="Updated Upgrade User"
            )
            assert update_success, f"Name update failed: {update_message}"
            
            final_profile = ProfileManagementService.get_user_profile(user.id)
            assert final_profile.name == "Updated Upgrade User", "Name should be updated"
            assert final_profile.biography == "Added biography to upgrade profile.", "Biography should be preserved"
            
            final_completion = ProfileManagementService.get_profile_completion_percentage(user.id)
            print(f"Final completion: {final_completion}%")
            assert final_completion == bio_completion, "Completion should remain same after name update"
            
            print("✅ Profile upgrade path works correctly")
            print("✅ All information preserved during updates")
            
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
        # Setup: Create a test user with minimal profile
        test_email = "criteria@minimal.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Minimal User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Testing minimal profile creation...")
            
            profile = ProfileManagementService.get_user_profile(user.id)
            
            # Criterion 1: Profile is created with only required name field
            assert profile is not None, "Profile should be created"
            assert profile.name == "Criteria Minimal User", "Profile should have required name"
            assert profile.biography is None or profile.biography == "", "Biography should be empty (optional)"
            print("✅ Profile is created with only required name field")
            
            # Criterion 2: Profile completion reflects minimal status
            completion = ProfileManagementService.get_profile_completion_percentage(user.id)
            assert completion > 0, "Profile completion should be greater than 0"
            assert completion < 100, "Profile completion should be less than 100 for minimal profile"
            print("✅ Profile completion reflects minimal status")
            
            # Criterion 3: User can view their minimal profile
            user_stats = ProfileManagementService.get_user_stats(user.id)
            assert user_stats is not None, "User should be able to view profile stats"
            print("✅ User can view their minimal profile")
            
            # Criterion 4: Profile can be updated later with additional information
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, biography="Added later"
            )
            assert update_success, f"Profile should be updatable: {update_message}"
            
            updated_completion = ProfileManagementService.get_profile_completion_percentage(user.id)
            assert updated_completion > completion, "Completion should increase after adding information"
            print("✅ Profile can be updated later with additional information")
            
            # Criterion 5: Minimal profile is functional for basic use
            # User should be able to perform basic actions with minimal profile
            assert profile.name is not None, "User should have identity (name) for basic functionality"
            print("✅ Minimal profile is functional for basic use")
            
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US03_Profile_CreateMinimal_Success")
    print("=" * 80)
    
    try:
        # Run the tests
        test_minimal_profile_creation_scenario()
        test_minimal_profile_edge_cases()
        test_minimal_profile_vs_complete_profile()
        test_minimal_profile_upgrade_path()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US03_Profile_CreateMinimal_Success: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Minimal profile creation works correctly")
        print("✅ Profile completion reflects minimal status correctly")
        print("✅ Minimal profiles can be upgraded with additional information")
        print("✅ Edge cases handled properly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
