#!/usr/bin/env python3
"""
Comprehensive test for TC_US03_Profile_BiographyLimit_CharacterWarning
Tests biography character limit and warning functionality.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService, SessionValidationService
from app.components.profile.services import ProfileManagementService
from app.models import User, UserProfile
from app import create_app, db
from flask import session

def test_biography_character_limit_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US03_Profile_BiographyLimit_CharacterWarning")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "biographylimit@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating user account with email '{test_email}'")
        
        # Step 1: Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Biography Limit User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        user_id = user.id
        
        print("\nStep 2: Testing biography within character limit")
        
        # Step 2: Test biography within limit (500 characters)
        valid_biography = "I am a passionate fact-checker with over 10 years of experience in journalism and research. I specialize in verifying claims about science, politics, and current events. My goal is to help create a more informed society by promoting accurate information and critical thinking skills. I believe that everyone deserves access to reliable, well-sourced facts to make informed decisions in their daily lives."
        
        print(f"Valid biography length: {len(valid_biography)} characters")
        assert len(valid_biography) <= 500, "Test biography should be within 500 character limit"
        
        update_success, update_message, updated_profile = ProfileManagementService.update_profile(
            user_id, biography=valid_biography
        )
        
        assert update_success, f"Biography within limit should be accepted: {update_message}"
        assert updated_profile is not None, "Updated profile should be returned"
        print("✅ Biography within character limit accepted")
        
        print("\nStep 3: Testing biography at character limit boundary")
        
        # Step 3: Test biography exactly at 500 characters
        boundary_biography = "A" * 500  # Exactly 500 characters
        print(f"Boundary biography length: {len(boundary_biography)} characters")
        
        boundary_success, boundary_message, boundary_profile = ProfileManagementService.update_profile(
            user_id, biography=boundary_biography
        )
        
        assert boundary_success, f"Biography at 500 characters should be accepted: {boundary_message}"
        print("✅ Biography at character limit boundary accepted")
        
        print("\nStep 4: Testing biography exceeding character limit")
        
        # Step 4: Test biography exceeding 500 characters
        long_biography = "A" * 501  # 501 characters - should be rejected
        print(f"Long biography length: {len(long_biography)} characters")
        
        long_success, long_message, long_profile = ProfileManagementService.update_profile(
            user_id, biography=long_biography
        )
        
        assert not long_success, "Biography exceeding 500 characters should be rejected"
        assert long_profile is None, "No profile should be returned for invalid biography"
        assert "500" in long_message, f"Error message should mention character limit: {long_message}"
        print(f"✅ Biography exceeding limit rejected: {long_message}")
        
        print("\nStep 5: Testing acceptance criteria")
        
        # Test acceptance criteria
        # Criterion 1: Character limit is enforced (500 characters)
        assert not long_success, "Character limit should be enforced"
        print("✅ Character limit is enforced")
        
        # Criterion 2: Clear error message is displayed when limit exceeded
        assert "Biography must be less than 500 characters" in long_message, "Clear error message should be displayed"
        print("✅ Clear error message displayed when limit exceeded")
        
        # Criterion 3: User can edit biography to fit within limit
        corrected_biography = long_biography[:499]  # Trim to 499 characters
        corrected_success, corrected_message, corrected_profile = ProfileManagementService.update_profile(
            user_id, biography=corrected_biography
        )
        
        assert corrected_success, f"Corrected biography should be accepted: {corrected_message}"
        print("✅ User can edit biography to fit within limit")
        
        # Criterion 4: Biography is saved when within limit
        final_profile = ProfileManagementService.get_user_profile(user_id)
        assert final_profile.biography == corrected_biography, "Biography should be saved when within limit"
        print("✅ Biography is saved when within limit")
        
        # Clean up after test
        user.hard_delete()

def test_biography_character_limit_web_interface():
    """Test biography character limit in web interface."""
    print("\n" + "="*70)
    print("🌐 Testing Biography Character Limit in Web Interface")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "webbiography@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Web Biography User"
        )
        assert success, f"Setup failed: {message}"
        
        # Login user
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        assert login_success, f"Login failed: {login_message}"
        
        try:
            with app.test_client() as client:
                # Simulate logged in session
                with client.session_transaction() as sess:
                    sess['user_id'] = user.id
                    sess['session_token'] = session.get('session_token')
                
                print("Testing profile edit page HTML attributes...")
                
                # Get profile edit page
                response = client.get('/profile/edit')
                assert response.status_code == 200, "Profile edit page should be accessible"
                
                edit_html = response.get_data(as_text=True)
                
                # Check for maxlength attribute
                assert 'maxlength="500"' in edit_html, "Biography textarea should have maxlength attribute"
                print("✅ Biography textarea has maxlength='500' attribute")
                
                # Check for data-max-length attribute (for JavaScript)
                assert 'data-max-length="500"' in edit_html, "Biography textarea should have data-max-length attribute"
                print("✅ Biography textarea has data-max-length='500' attribute")
                
                # Check for biography field
                assert 'name="biography"' in edit_html, "Biography field should be present"
                assert 'id="biography"' in edit_html, "Biography field should have correct ID"
                print("✅ Biography field properly configured")
                
                print("\nTesting form submission with valid biography...")
                
                # Test form submission with valid biography
                valid_bio = "This is a valid biography within the character limit."
                form_data = {
                    'name': 'Web Biography User',
                    'biography': valid_bio
                }
                
                response = client.post('/profile/edit', data=form_data, follow_redirects=True)
                assert response.status_code == 200, "Form submission should succeed"
                
                # Verify biography was saved
                updated_profile = ProfileManagementService.get_user_profile(user.id)
                assert updated_profile.biography == valid_bio, "Biography should be saved correctly"
                print("✅ Valid biography submitted and saved successfully")
                
                print("\nTesting form submission with biography exceeding limit...")
                
                # Test form submission with biography exceeding limit
                long_bio = "A" * 501  # 501 characters
                form_data_long = {
                    'name': 'Web Biography User',
                    'biography': long_bio
                }
                
                response_long = client.post('/profile/edit', data=form_data_long, follow_redirects=True)
                # The response should either show an error or the biography should be truncated/rejected
                
                # Check if biography was rejected (should not be saved)
                profile_after_long = ProfileManagementService.get_user_profile(user.id)
                assert profile_after_long.biography != long_bio, "Long biography should not be saved"
                print("✅ Biography exceeding limit handled correctly by web interface")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_biography_character_limit_edge_cases():
    """Test edge cases for biography character limits."""
    print("\n" + "="*70)
    print("🔍 Testing Biography Character Limit Edge Cases")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "edgebiography@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Edge Biography User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            edge_cases = [
                ("Empty biography", "", True),
                ("Single character", "A", True),
                ("Whitespace only", "   ", True),  # Should be trimmed to empty
                ("499 characters", "A" * 499, True),
                ("500 characters", "A" * 500, True),
                ("501 characters", "A" * 501, False),
                ("1000 characters", "A" * 1000, False),
                ("Biography with newlines", "Line 1\nLine 2\nLine 3", True),
                ("Biography with special chars", "Hello! @#$%^&*()_+ 123", True),
                ("Unicode characters", "Hello 世界 🌍 café naïve", True),
            ]
            
            for description, biography, should_succeed in edge_cases:
                print(f"\nTesting {description}: {len(biography)} characters")
                
                update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                    user.id, biography=biography
                )
                
                if should_succeed:
                    assert update_success, f"{description} should be accepted: {update_message}"
                    print(f"✅ PASS: {description} accepted")
                else:
                    assert not update_success, f"{description} should be rejected"
                    assert updated_profile is None, f"No profile should be returned for {description}"
                    print(f"✅ PASS: {description} correctly rejected - {update_message}")
                    
        finally:
            # Clean up after test
            user.hard_delete()

def test_biography_character_limit_with_whitespace():
    """Test biography character limit handling with whitespace."""
    print("\n" + "="*70)
    print("🔤 Testing Biography Character Limit with Whitespace")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "whitespacebiography@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Whitespace Biography User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Test biography with leading/trailing whitespace that becomes valid after trimming
            biography_with_spaces = "   " + "A" * 495 + "   "  # 501 total, 495 after trim
            print(f"Biography with spaces: {len(biography_with_spaces)} characters (before trim)")
            
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, biography=biography_with_spaces
            )
            
            assert update_success, f"Biography should be accepted after trimming: {update_message}"
            
            # Verify it was trimmed
            final_profile = ProfileManagementService.get_user_profile(user.id)
            assert len(final_profile.biography) == 495, "Biography should be trimmed to 495 characters"
            assert not final_profile.biography.startswith(" "), "Leading spaces should be trimmed"
            assert not final_profile.biography.endswith(" "), "Trailing spaces should be trimmed"
            print("✅ Biography with whitespace trimmed correctly")
            
            # Test biography that exceeds limit even after trimming
            long_biography_with_spaces = "   " + "A" * 501 + "   "  # 507 total, 501 after trim
            print(f"Long biography with spaces: {len(long_biography_with_spaces)} characters (before trim)")
            
            long_update_success, long_update_message, long_updated_profile = ProfileManagementService.update_profile(
                user.id, biography=long_biography_with_spaces
            )
            
            assert not long_update_success, "Biography should be rejected even after trimming"
            print("✅ Long biography correctly rejected even after trimming")
            
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
        test_email = "criteria@biography.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Biography User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Testing biography character limit and warning functionality...")
            
            # Criterion 1: Character limit is enforced (500 characters)
            long_biography = "A" * 501
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, biography=long_biography
            )
            
            assert not update_success, "Character limit should be enforced"
            assert "500" in update_message, "Error message should mention character limit"
            print("✅ Character limit is enforced (500 characters)")
            
            # Criterion 2: Clear error message is displayed when limit exceeded
            assert "Biography must be less than 500 characters" in update_message, "Clear error message should be displayed"
            print("✅ Clear error message displayed when limit exceeded")
            
            # Criterion 3: User can edit biography to fit within limit
            valid_biography = "A" * 499
            valid_success, valid_message, valid_profile = ProfileManagementService.update_profile(
                user.id, biography=valid_biography
            )
            
            assert valid_success, f"Valid biography should be accepted: {valid_message}"
            print("✅ User can edit biography to fit within limit")
            
            # Criterion 4: Biography is saved when within limit
            final_profile = ProfileManagementService.get_user_profile(user.id)
            assert final_profile.biography == valid_biography, "Biography should be saved when within limit"
            print("✅ Biography is saved when within limit")
            
            # Criterion 5: Character count/warning is provided (HTML attributes)
            with app.test_client() as client:
                # Simulate logged in session
                login_success, login_message, login_user = AuthenticationService.login_user(
                    test_email, "password123"
                )
                assert login_success, f"Login failed: {login_message}"
                
                with client.session_transaction() as sess:
                    sess['user_id'] = user.id
                    sess['session_token'] = session.get('session_token')
                
                response = client.get('/profile/edit')
                assert response.status_code == 200, "Profile edit page should be accessible"
                
                edit_html = response.get_data(as_text=True)
                assert 'maxlength="500"' in edit_html, "HTML should enforce character limit"
                assert 'data-max-length="500"' in edit_html, "HTML should provide character limit data"
                print("✅ Character limit information provided in HTML")
            
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US03_Profile_BiographyLimit_CharacterWarning")
    print("=" * 80)
    
    try:
        # Run the tests
        test_biography_character_limit_scenario()
        test_biography_character_limit_web_interface()
        test_biography_character_limit_edge_cases()
        test_biography_character_limit_with_whitespace()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US03_Profile_BiographyLimit_CharacterWarning: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Character limit (500 characters) enforced correctly")
        print("✅ Clear error messages displayed when limit exceeded")
        print("✅ Biography can be edited to fit within limit")
        print("✅ Valid biographies are saved correctly")
        print("✅ Web interface provides character limit attributes")
        print("✅ Edge cases handled properly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
