#!/usr/bin/env python3
"""
Comprehensive test for TC_US04_ViewProfile_NoPhoto_DefaultPlaceholder
Tests viewing a profile without a photo and verifying default placeholder is displayed.
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

def test_view_profile_no_photo_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US04_ViewProfile_NoPhoto_DefaultPlaceholder")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "nophoto@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating user account with email '{test_email}'")
        
        # Step 1: Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "No Photo User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        user_id = user.id
        
        print("\nStep 2: Verifying profile has no photo")
        
        # Step 2: Verify profile has no photo initially
        profile = ProfileManagementService.get_user_profile(user_id)
        assert profile is not None, "Profile should exist"
        assert profile.profile_photo_url is None, "Profile should have no photo URL initially"
        print("✅ Profile confirmed to have no photo")
        
        # Verify no photo records exist
        photo_records = ProfilePhoto.query.filter_by(user_id=user_id, is_deleted=False).all()
        assert len(photo_records) == 0, "No photo records should exist"
        print("✅ No photo records in database")
        
        print("\nStep 3: Testing profile page displays default placeholder")
        
        # Step 3: Test profile page rendering
        with app.test_client() as client:
            response = client.get(f'/profile/user/{user_id}')
            assert response.status_code == 200, f"Profile page should be accessible, got {response.status_code}"
            
            profile_html = response.get_data(as_text=True)
            
            # Verify no photo URL is present
            assert '/uploads/profile_photos/' not in profile_html, "No photo URL should be in HTML"
            print("✅ No photo URL found in HTML")
            
            # Verify placeholder is displayed
            assert 'bi-person-fill' in profile_html, "Default placeholder icon should be displayed"
            print("✅ Default placeholder icon (bi-person-fill) is displayed")
            
            # Verify no img tag for profile photo
            import re
            img_pattern = r'<img[^>]*class="profile-photo"[^>]*>'
            img_matches = re.findall(img_pattern, profile_html)
            assert len(img_matches) == 0, "No profile photo img tags should be present"
            print("✅ No profile photo img tags found")
            
            # Verify placeholder div structure
            placeholder_pattern = r'<div[^>]*class="[^"]*profile-photo[^"]*"[^>]*>.*?bi-person-fill.*?</div>'
            placeholder_matches = re.findall(placeholder_pattern, profile_html, re.DOTALL)
            assert len(placeholder_matches) > 0, "Placeholder div with icon should be present"
            print("✅ Placeholder div structure found")
        
        print("\nStep 4: Testing acceptance criteria")
        
        # Test acceptance criteria
        # Criterion 1: Default placeholder is displayed when no photo
        assert 'bi-person-fill' in profile_html, "Default placeholder should be displayed"
        print("✅ Default placeholder is displayed when no photo")
        
        # Criterion 2: No broken image links
        assert '<img' not in profile_html or 'profile-photo' not in profile_html, "No broken profile photo img tags"
        print("✅ No broken image links")
        
        # Criterion 3: Profile page loads successfully without photo
        assert response.status_code == 200, "Profile page should load successfully"
        print("✅ Profile page loads successfully without photo")
        
        # Criterion 4: Placeholder is visually appropriate
        # Check for proper CSS classes and Bootstrap icon
        assert 'bi-person-fill' in profile_html, "Should use Bootstrap person icon"
        assert 'profile-photo' in profile_html, "Should have profile-photo CSS class for styling"
        print("✅ Placeholder is visually appropriate")
        
        # Clean up after test
        user.hard_delete()

def test_profile_no_photo_different_completion_levels():
    """Test profiles without photos at different completion levels."""
    print("\n" + "="*70)
    print("📊 Testing Profiles Without Photos at Different Completion Levels")
    print("="*70)
    
    app = create_app()
    
    completion_scenarios = [
        ("minimal@nophoto.com", "Minimal User", None, 33),  # Name only
        ("partial@nophoto.com", "Partial User", "This is my biography without a photo", 66),  # Name + bio
    ]
    
    for email, name, biography, expected_completion in completion_scenarios:
        print(f"\nTesting {expected_completion}% completion profile without photo...")
        
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
                
                # Verify completion percentage
                completion = ProfileManagementService.get_profile_completion_percentage(user.id)
                assert completion == expected_completion, f"Expected {expected_completion}% completion, got {completion}%"
                
                # Test web interface display
                with app.test_client() as client:
                    response = client.get(f'/profile/user/{user.id}')
                    assert response.status_code == 200, "Profile page should be accessible"
                    
                    profile_html = response.get_data(as_text=True)
                    
                    # Verify name is displayed
                    assert name in profile_html, "Name should be displayed"
                    
                    # Verify biography display if present
                    if biography:
                        assert biography in profile_html, "Biography should be displayed when present"
                    
                    # Verify placeholder is always shown when no photo
                    assert 'bi-person-fill' in profile_html, "Placeholder should be shown when no photo"
                    assert '/uploads/profile_photos/' not in profile_html, "No photo URLs should be present"
                    
                    print(f"✅ {expected_completion}% completion profile without photo displays correctly")
                
            finally:
                # Clean up after test
                user.hard_delete()

def test_profile_no_photo_after_deletion():
    """Test profile displays placeholder after photo deletion."""
    print("\n" + "="*70)
    print("🗑️ Testing Profile Placeholder After Photo Deletion")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "photodeletion@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Photo Deletion User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Step 1: Upload profile photo")
            
            # Step 1: Upload a profile photo first
            test_image = create_test_image(300, 300, 'JPEG', 'red')
            file_storage = create_file_storage(test_image, 'deletion_test.jpg', 'image/jpeg')
            
            upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                user.id, file_storage
            )
            
            assert upload_success, f"Photo upload should succeed: {upload_message}"
            print(f"✅ Photo uploaded: {photo_url}")
            
            # Verify photo is displayed
            with app.test_client() as client:
                response_with_photo = client.get(f'/profile/user/{user.id}')
                html_with_photo = response_with_photo.get_data(as_text=True)
                
                assert photo_url in html_with_photo, "Photo URL should be in HTML"
                assert 'bi-person-fill' not in html_with_photo, "Placeholder should not be shown when photo exists"
                print("✅ Photo is displayed correctly")
            
            print("\nStep 2: Delete profile photo")
            
            # Step 2: Delete the photo
            delete_success, delete_message = ProfilePhotoService.delete_profile_photo(user.id)
            assert delete_success, f"Photo deletion should succeed: {delete_message}"
            print("✅ Photo deleted successfully")
            
            print("\nStep 3: Verify placeholder is restored")
            
            # Step 3: Verify placeholder is now shown
            with app.test_client() as client:
                response_after_delete = client.get(f'/profile/user/{user.id}')
                html_after_delete = response_after_delete.get_data(as_text=True)
                
                # Should not contain photo URL
                assert photo_url not in html_after_delete, "Deleted photo URL should not be in HTML"
                
                # Should show placeholder
                assert 'bi-person-fill' in html_after_delete, "Placeholder should be shown after photo deletion"
                
                # Should not have profile photo img tags
                import re
                img_pattern = r'<img[^>]*class="profile-photo"[^>]*>'
                img_matches = re.findall(img_pattern, html_after_delete)
                assert len(img_matches) == 0, "No profile photo img tags should remain"
                
                print("✅ Placeholder correctly restored after photo deletion")
            
            # Verify profile completion dropped
            completion_after_delete = ProfileManagementService.get_profile_completion_percentage(user.id)
            assert completion_after_delete == 33, f"Completion should be 33% without photo, got {completion_after_delete}%"
            print(f"✅ Profile completion correctly updated: {completion_after_delete}%")
            
        finally:
            # Clean up after test
            user.hard_delete()

def test_placeholder_styling_and_accessibility():
    """Test placeholder styling and accessibility features."""
    print("\n" + "="*70)
    print("🎨 Testing Placeholder Styling and Accessibility")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "placeholderstyling@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Placeholder Styling User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Test placeholder styling
            with app.test_client() as client:
                response = client.get(f'/profile/user/{user.id}')
                assert response.status_code == 200, "Profile page should be accessible"
                
                profile_html = response.get_data(as_text=True)
                
                print("Testing placeholder CSS classes...")
                
                # Check for proper CSS classes
                assert 'profile-photo' in profile_html, "Should have profile-photo CSS class"
                assert 'bi-person-fill' in profile_html, "Should have Bootstrap icon class"
                
                # Check for proper styling classes (background, alignment, etc.)
                styling_indicators = [
                    'bg-secondary',  # Background color
                    'd-flex',        # Flexbox display
                    'align-items-center',  # Vertical alignment
                    'justify-content-center',  # Horizontal alignment
                ]
                
                styling_found = []
                for indicator in styling_indicators:
                    if indicator in profile_html:
                        styling_found.append(indicator)
                
                print(f"Styling classes found: {styling_found}")
                assert len(styling_found) > 0, "Should have some styling classes for placeholder"
                print("✅ Placeholder has proper CSS styling")
                
                print("\nTesting accessibility features...")
                
                # Check for accessibility features
                accessibility_indicators = [
                    'alt=',           # Alt text
                    'aria-',          # ARIA attributes
                    'role=',          # Role attributes
                    'title=',         # Title attributes
                ]
                
                accessibility_found = []
                for indicator in accessibility_indicators:
                    if indicator in profile_html:
                        accessibility_found.append(indicator)
                
                print(f"Accessibility features found: {accessibility_found}")
                
                # At minimum, should have some accessibility consideration
                if len(accessibility_found) > 0:
                    print("✅ Placeholder includes accessibility features")
                else:
                    print("ℹ️  Placeholder may benefit from additional accessibility features")
                
                print("\nTesting visual consistency...")
                
                # Check that placeholder maintains same dimensions/styling as photo would
                import re
                placeholder_pattern = r'<div[^>]*class="[^"]*profile-photo[^"]*"[^>]*>'
                placeholder_matches = re.findall(placeholder_pattern, profile_html)
                
                if len(placeholder_matches) > 0:
                    print("✅ Placeholder uses same CSS class as profile photos")
                    print(f"Placeholder element: {placeholder_matches[0]}")
                else:
                    print("⚠️  Placeholder may not use consistent styling with photos")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_placeholder_edge_cases():
    """Test placeholder display in various edge cases."""
    print("\n" + "="*70)
    print("🔍 Testing Placeholder Edge Cases")
    print("="*70)
    
    app = create_app()
    
    edge_cases = [
        ("newuser@example.com", "New User", None, "Newly created user"),
        ("longname@example.com", "Very Long User Name That Might Affect Layout", None, "User with very long name"),
        ("unicode@example.com", "Unicode User 世界", None, "User with unicode characters"),
        ("empty@example.com", "A", None, "User with minimal name"),
    ]
    
    for email, name, biography, description in edge_cases:
        print(f"\nTesting {description}...")
        
        with app.test_request_context():
            # Clean up any existing test user
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
            
            # Create user
            success, message, user = AuthenticationService.register_user(
                email, "password123", name
            )
            assert success, f"Setup failed for {description}: {message}"
            
            try:
                # Test placeholder display
                with app.test_client() as client:
                    response = client.get(f'/profile/user/{user.id}')
                    assert response.status_code == 200, f"Profile page should be accessible for {description}"
                    
                    profile_html = response.get_data(as_text=True)
                    
                    # Verify placeholder is shown
                    assert 'bi-person-fill' in profile_html, f"Placeholder should be shown for {description}"
                    
                    # Verify no photo URLs
                    assert '/uploads/profile_photos/' not in profile_html, f"No photo URLs should be present for {description}"
                    
                    # Verify name is displayed (may be escaped for HTML)
                    name_found = name in profile_html or name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') in profile_html
                    assert name_found, f"Name should be displayed for {description}"
                    
                    print(f"✅ {description} displays placeholder correctly")
                    
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
        # Setup: Create a test user without photo
        test_email = "criteria@nophoto.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria No Photo User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Testing no photo profile display criteria...")
            
            # Add biography to make profile more complete (but still no photo)
            biography = "I am testing the no photo placeholder display functionality."
            update_success, update_message, updated_profile = ProfileManagementService.update_profile(
                user.id, biography=biography
            )
            assert update_success, f"Profile update should succeed: {update_message}"
            
            with app.test_client() as client:
                response = client.get(f'/profile/user/{user.id}')
                assert response.status_code == 200, "Profile page should be accessible"
                
                profile_html = response.get_data(as_text=True)
                
                print("Testing no photo placeholder criteria...")
                
                # Criterion 1: Default placeholder is displayed when no photo
                assert 'bi-person-fill' in profile_html, "Default placeholder icon should be displayed"
                print("✅ Default placeholder is displayed when no photo")
                
                # Criterion 2: No broken image links or 404 errors
                assert '/uploads/profile_photos/' not in profile_html, "No photo URLs should be present"
                
                # Check for any img tags that might be broken
                import re
                img_tags = re.findall(r'<img[^>]*>', profile_html)
                profile_img_tags = [tag for tag in img_tags if 'profile-photo' in tag]
                assert len(profile_img_tags) == 0, "No profile photo img tags should be present"
                print("✅ No broken image links or 404 errors")
                
                # Criterion 3: Profile page loads successfully without photo
                assert response.status_code == 200, "Profile page should load successfully"
                print("✅ Profile page loads successfully without photo")
                
                # Criterion 4: Placeholder is visually appropriate and styled
                assert 'profile-photo' in profile_html, "Placeholder should use profile-photo CSS class"
                
                # Check for proper Bootstrap icon
                assert 'bi-person-fill' in profile_html, "Should use appropriate Bootstrap person icon"
                print("✅ Placeholder is visually appropriate and styled")
                
                # Criterion 5: Other profile information is still displayed
                assert "Criteria No Photo User" in profile_html, "User name should be displayed"
                assert biography in profile_html, "Biography should be displayed"
                print("✅ Other profile information is still displayed correctly")
                
                # Criterion 6: Profile completion reflects missing photo
                completion = ProfileManagementService.get_profile_completion_percentage(user.id)
                assert completion == 66, f"Profile completion should be 66% without photo, got {completion}%"
                print(f"✅ Profile completion correctly reflects missing photo: {completion}%")
                
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US04_ViewProfile_NoPhoto_DefaultPlaceholder")
    print("=" * 80)
    
    try:
        # Run the tests
        test_view_profile_no_photo_scenario()
        test_profile_no_photo_different_completion_levels()
        test_profile_no_photo_after_deletion()
        test_placeholder_styling_and_accessibility()
        test_placeholder_edge_cases()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US04_ViewProfile_NoPhoto_DefaultPlaceholder: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Default placeholder displayed correctly when no photo")
        print("✅ No broken image links or 404 errors")
        print("✅ Profile page loads successfully without photo")
        print("✅ Placeholder is visually appropriate and styled")
        print("✅ Other profile information displays correctly")
        print("✅ Profile completion reflects missing photo")
        print("✅ Placeholder restored correctly after photo deletion")
        print("✅ Edge cases handled properly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
