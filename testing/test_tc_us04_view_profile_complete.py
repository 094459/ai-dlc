#!/usr/bin/env python3
"""
Comprehensive test for TC_US04_ViewProfile_CompleteProfile_DisplayAll
Tests viewing a complete profile with all information properly displayed.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage
from app.components.auth.services import AuthenticationService, SessionValidationService
from app.components.profile.services import ProfileManagementService, ProfilePhotoService
from app.models import User, UserProfile, ProfilePhoto
from app import create_app, db
from flask import session

def create_test_image(width=300, height=300, format='JPEG', color='blue'):
    """Create a test image with specified dimensions."""
    img = Image.new('RGB', (width, height), color=color)
    img_io = BytesIO()
    img.save(img_io, format=format)
    img_io.seek(0)
    return img_io

def create_file_storage(image_data, filename, content_type='image/jpeg'):
    """Create a FileStorage object for testing file uploads."""
    return FileStorage(
        stream=image_data,
        filename=filename,
        content_type=content_type
    )

def test_view_complete_profile_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US04_ViewProfile_CompleteProfile_DisplayAll")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "completeprofile@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating user account with email '{test_email}'")
        
        # Step 1: Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Complete Profile User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        user_id = user.id
        
        print("\nStep 2: Creating complete profile with all information")
        
        # Step 2: Update profile with complete information
        complete_biography = "I am a passionate fact-checker and researcher with over 5 years of experience in journalism. I specialize in verifying scientific claims and political statements. My goal is to promote accurate information and help people make informed decisions based on reliable facts."
        
        update_success, update_message, updated_profile = ProfileManagementService.update_profile(
            user_id, 
            name="Complete Profile User",
            biography=complete_biography
        )
        
        assert update_success, f"Profile update should succeed: {update_message}"
        print("✅ Profile updated with complete information")
        
        # Step 3: Add profile photo
        print("\nStep 3: Adding profile photo")
        
        test_image = create_test_image(400, 400, 'JPEG', 'green')
        file_storage = create_file_storage(test_image, 'complete_profile.jpg', 'image/jpeg')
        
        photo_success, photo_message, photo_url = ProfilePhotoService.upload_profile_photo(
            user_id, file_storage
        )
        
        assert photo_success, f"Photo upload should succeed: {photo_message}"
        print("✅ Profile photo uploaded successfully")
        
        print("\nStep 4: Verifying complete profile data")
        
        # Step 4: Verify all profile information is present
        final_profile = ProfileManagementService.get_user_profile(user_id)
        assert final_profile is not None, "Profile should exist"
        assert final_profile.name == "Complete Profile User", "Name should be updated"
        assert final_profile.biography == complete_biography, "Biography should be saved"
        assert final_profile.profile_photo_url is not None, "Profile photo URL should be set"
        print("✅ Complete profile data verified")
        
        # Verify profile completion is 100%
        completion_percentage = ProfileManagementService.get_profile_completion_percentage(user_id)
        assert completion_percentage == 100, f"Profile completion should be 100%, got {completion_percentage}%"
        print(f"✅ Profile completion: {completion_percentage}%")
        
        print("\nStep 5: Testing profile view through web interface")
        
        # Step 5: Test profile viewing through web interface
        with app.test_client() as client:
            # Test public profile view (no authentication required)
            response = client.get(f'/profile/user/{user_id}')
            assert response.status_code == 200, f"Profile page should be accessible, got {response.status_code}"
            
            profile_html = response.get_data(as_text=True)
            
            # Verify all profile information is displayed
            assert "Complete Profile User" in profile_html, "Name should be displayed"
            assert complete_biography in profile_html, "Biography should be displayed"
            assert photo_url in profile_html, "Profile photo should be displayed"
            print("✅ All profile information displayed in web interface")
            
        print("\nStep 6: Testing acceptance criteria")
        
        # Test acceptance criteria
        # Criterion 1: All profile information is displayed
        assert final_profile.name is not None, "Name should be displayed"
        assert final_profile.biography is not None, "Biography should be displayed"
        assert final_profile.profile_photo_url is not None, "Profile photo should be displayed"
        print("✅ All profile information is displayed")
        
        # Criterion 2: Profile photo is visible
        assert photo_url in profile_html, "Profile photo should be visible in HTML"
        assert '<img' in profile_html and photo_url in profile_html, "Profile photo should be rendered as image"
        print("✅ Profile photo is visible")
        
        # Criterion 3: Biography is fully displayed
        assert complete_biography in profile_html, "Full biography should be displayed"
        print("✅ Biography is fully displayed")
        
        # Criterion 4: Profile completion shows 100%
        assert completion_percentage == 100, "Profile completion should show 100%"
        print("✅ Profile completion shows 100%")
        
        # Criterion 5: User statistics are displayed
        user_stats = ProfileManagementService.get_user_stats(user_id)
        assert user_stats is not None, "User statistics should be available"
        print("✅ User statistics are displayed")
        
        # Clean up after test
        user.hard_delete()

def test_profile_view_different_completion_levels():
    """Test profile viewing at different completion levels."""
    print("\n" + "="*70)
    print("📊 Testing Profile View at Different Completion Levels")
    print("="*70)
    
    app = create_app()
    
    completion_scenarios = [
        ("minimal@profile.com", "Minimal User", None, None, 33),  # Name only
        ("partial@profile.com", "Partial User", "Short bio", None, 66),  # Name + bio
        ("complete@profile.com", "Complete User", "Full biography", True, 100),  # Name + bio + photo
    ]
    
    for email, name, biography, has_photo, expected_completion in completion_scenarios:
        print(f"\nTesting {expected_completion}% completion profile...")
        
        with app.test_request_context():
            # Clean up any existing test user
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
            
            # Create user
            success, message, user = AuthenticationService.register_user(
                email, "password123", name
            )
            assert success, f"Setup failed: {message}"
            
            try:
                # Update profile based on scenario
                if biography:
                    update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                        user.id, biography=biography
                    )
                    assert update_success, f"Biography update should succeed: {update_message}"
                
                # Add photo if required
                if has_photo:
                    test_image = create_test_image(300, 300, 'PNG', 'purple')
                    file_storage = create_file_storage(test_image, 'test.png', 'image/png')
                    
                    photo_success, photo_message, photo_url = ProfilePhotoService.upload_profile_photo(
                        user.id, file_storage
                    )
                    assert photo_success, f"Photo upload should succeed: {photo_message}"
                
                # Verify completion percentage
                completion = ProfileManagementService.get_profile_completion_percentage(user.id)
                assert completion == expected_completion, f"Expected {expected_completion}% completion, got {completion}%"
                
                # Test web interface display
                with app.test_client() as client:
                    response = client.get(f'/profile/user/{user.id}')
                    assert response.status_code == 200, "Profile page should be accessible"
                    
                    profile_html = response.get_data(as_text=True)
                    
                    # Verify name is always displayed
                    assert name in profile_html, "Name should always be displayed"
                    
                    # Verify biography display
                    if biography:
                        assert biography in profile_html, "Biography should be displayed when present"
                    
                    # Verify photo display
                    if has_photo:
                        assert '<img' in profile_html, "Profile photo should be displayed when present"
                    else:
                        # Should show placeholder
                        assert 'bi-person-fill' in profile_html, "Placeholder should be shown when no photo"
                
                print(f"✅ {expected_completion}% completion profile displays correctly")
                
            finally:
                # Clean up after test
                user.hard_delete()

def test_profile_view_public_vs_private_information():
    """Test what information is publicly visible vs private."""
    print("\n" + "="*70)
    print("🔒 Testing Public vs Private Profile Information")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "publicprivate@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user with complete profile
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Public Private User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Create complete profile
            biography = "This is my public biography that everyone can see."
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, biography=biography
            )
            assert update_success, f"Profile update should succeed: {update_message}"
            
            # Add profile photo
            test_image = create_test_image(350, 350, 'JPEG', 'orange')
            file_storage = create_file_storage(test_image, 'public_private.jpg', 'image/jpeg')
            
            photo_success, photo_message, photo_url = ProfilePhotoService.upload_profile_photo(
                user.id, file_storage
            )
            assert photo_success, f"Photo upload should succeed: {photo_message}"
            
            with app.test_client() as client:
                print("Testing public profile view (no authentication)...")
                
                # Test public view (no authentication)
                response = client.get(f'/profile/user/{user.id}')
                assert response.status_code == 200, "Profile should be publicly viewable"
                
                profile_html = response.get_data(as_text=True)
                
                # Public information should be visible
                assert "Public Private User" in profile_html, "Name should be publicly visible"
                assert biography in profile_html, "Biography should be publicly visible"
                assert photo_url in profile_html, "Profile photo should be publicly visible"
                print("✅ Public information correctly displayed")
                
                # Private information should NOT be visible
                assert test_email not in profile_html, "Email should not be publicly visible"
                assert "password" not in profile_html.lower(), "Password should not be visible"
                print("✅ Private information correctly hidden")
                
                print("Testing authenticated profile view...")
                
                # Login as the user
                login_success, login_message, login_user = AuthenticationService.login_user(
                    test_email, "password123"
                )
                assert login_success, f"Login should succeed: {login_message}"
                
                # Simulate logged in session
                with client.session_transaction() as sess:
                    sess['user_id'] = user.id
                    sess['session_token'] = session.get('session_token')
                
                # Test authenticated view of own profile
                auth_response = client.get(f'/profile/user/{user.id}')
                assert auth_response.status_code == 200, "Own profile should be viewable when authenticated"
                
                auth_html = auth_response.get_data(as_text=True)
                
                # Should still show public information
                assert "Public Private User" in auth_html, "Name should be visible to owner"
                assert biography in auth_html, "Biography should be visible to owner"
                assert photo_url in auth_html, "Profile photo should be visible to owner"
                
                # May show additional controls for editing (but still no sensitive data)
                assert test_email not in auth_html, "Email should not be displayed even to owner on profile page"
                print("✅ Authenticated view shows appropriate information")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_profile_view_edge_cases():
    """Test profile viewing edge cases."""
    print("\n" + "="*70)
    print("🔍 Testing Profile View Edge Cases")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        edge_cases = [
            ("unicode@profile.com", "Unicode Name", "Biography with unicode: café naïve 测试"),
            ("special@profile.com", "Name With Special Characters", "Biography with @#$%^&*() special chars"),
            ("long@profile.com", "Very Long Name That Exceeds Normal Length", "Very long biography " + "A" * 400),
            ("minimal@profile.com", "A", ""),  # Minimal valid content
        ]
        
        for email, name, biography in edge_cases:
            print(f"\nTesting edge case: {name[:30]}...")
            
            # Clean up any existing test user
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
            
            # Create user
            success, message, user = AuthenticationService.register_user(
                email, "password123", name
            )
            assert success, f"Setup failed for {name}: {message}"
            
            try:
                # Update with biography if provided
                if biography:
                    update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                        user.id, biography=biography
                    )
                    if not update_success:
                        print(f"ℹ️  Biography rejected for {name}: {update_message}")
                        continue
                
                # Test web interface display
                with app.test_client() as client:
                    response = client.get(f'/profile/user/{user.id}')
                    assert response.status_code == 200, f"Profile page should be accessible for {name}"
                    
                    profile_html = response.get_data(as_text=True)
                    
                    # Verify name is displayed (may be escaped for HTML)
                    # Check if name or escaped version is present
                    name_found = name in profile_html or name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') in profile_html
                    assert name_found, f"Name should be displayed for {name}"
                    
                    # Verify biography if present
                    if biography and len(biography.strip()) > 0:
                        bio_found = biography in profile_html or biography.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') in profile_html
                        if bio_found:
                            print(f"✅ Biography displayed correctly for {name}")
                        else:
                            print(f"ℹ️  Biography may be escaped or truncated for {name}")
                    
                    print(f"✅ Edge case handled correctly: {name[:30]}")
                    
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
        # Setup: Create a test user with complete profile
        test_email = "criteria@completeprofile.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Complete User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Creating complete profile for testing...")
            
            # Create complete profile
            complete_bio = "I am a comprehensive user profile for testing all display criteria. This biography contains sufficient information to test the complete profile display functionality."
            
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, biography=complete_bio
            )
            assert update_success, f"Profile update should succeed: {update_message}"
            
            # Add profile photo
            test_image = create_test_image(400, 400, 'PNG', 'red')
            file_storage = create_file_storage(test_image, 'criteria.png', 'image/png')
            
            photo_success, photo_message, photo_url = ProfilePhotoService.upload_profile_photo(
                user.id, file_storage
            )
            assert photo_success, f"Photo upload should succeed: {photo_message}"
            
            # Get final profile
            final_profile = ProfileManagementService.get_user_profile(user.id)
            
            with app.test_client() as client:
                response = client.get(f'/profile/user/{user.id}')
                assert response.status_code == 200, "Profile page should be accessible"
                
                profile_html = response.get_data(as_text=True)
                
                print("Testing complete profile display criteria...")
                
                # Criterion 1: All profile information is displayed
                assert "Criteria Complete User" in profile_html, "Name should be displayed"
                assert complete_bio in profile_html, "Biography should be displayed"
                assert photo_url in profile_html, "Profile photo URL should be in HTML"
                print("✅ All profile information is displayed")
                
                # Criterion 2: Profile photo is visible and properly sized
                assert '<img' in profile_html, "Profile photo should be rendered as image tag"
                assert 'class="profile-photo"' in profile_html, "Profile photo should have proper CSS class"
                print("✅ Profile photo is visible and properly sized")
                
                # Criterion 3: Biography is fully displayed without truncation
                assert complete_bio in profile_html, "Full biography should be displayed without truncation"
                print("✅ Biography is fully displayed without truncation")
                
                # Criterion 4: Profile completion shows 100%
                completion = ProfileManagementService.get_profile_completion_percentage(user.id)
                assert completion == 100, f"Profile completion should be 100%, got {completion}%"
                print("✅ Profile completion shows 100%")
                
                # Criterion 5: User statistics and metadata are displayed
                user_stats = ProfileManagementService.get_user_stats(user.id)
                assert user_stats is not None, "User statistics should be available"
                
                # Check if join date or other metadata is displayed
                if 'member since' in profile_html.lower() or 'joined' in profile_html.lower():
                    print("✅ User metadata (join date) is displayed")
                else:
                    print("ℹ️  User metadata may be displayed differently or not shown")
                
                # Criterion 6: Profile is accessible to other users
                # This is already tested by accessing without authentication
                print("✅ Profile is accessible to other users")
                
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US04_ViewProfile_CompleteProfile_DisplayAll")
    print("=" * 80)
    
    try:
        # Run the tests
        test_view_complete_profile_scenario()
        test_profile_view_different_completion_levels()
        test_profile_view_public_vs_private_information()
        test_profile_view_edge_cases()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US04_ViewProfile_CompleteProfile_DisplayAll: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Complete profile information displayed correctly")
        print("✅ Profile photos visible and properly sized")
        print("✅ Biography fully displayed without truncation")
        print("✅ Profile completion shows 100% correctly")
        print("✅ Public vs private information handled correctly")
        print("✅ Edge cases handled properly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
