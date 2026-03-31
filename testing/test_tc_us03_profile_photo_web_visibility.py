#!/usr/bin/env python3
"""
Web interface test to verify profile photo visibility on profile page.
This test ensures that uploaded profile photos are actually visible on the web interface.
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

def test_profile_photo_web_visibility():
    """Test that uploaded profile photo is visible on the profile page."""
    print("🧪 Testing Profile Photo Web Visibility")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "webphoto@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating user account and logging in")
        
        # Step 1: Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Web Photo User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        
        # Login the user to create a session
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        assert login_success, f"Login failed: {login_message}"
        print("✅ User logged in successfully")
        
        try:
            print("\nStep 2: Testing profile page without photo")
            
            # Step 2: Test profile page access with test client
            with app.test_client() as client:
                # Simulate logged in session
                with client.session_transaction() as sess:
                    sess['user_id'] = user.id
                    sess['session_token'] = session.get('session_token')
                
                response = client.get(f'/profile/user/{user.id}')
                assert response.status_code == 200, f"Profile page should be accessible, got {response.status_code}"
                
                # Check that default placeholder is shown (no profile photo URL)
                profile_html = response.get_data(as_text=True)
                assert 'profile-photo' in profile_html, "Profile photo section should exist"
                
                # Should show placeholder icon, not actual image
                profile = ProfileManagementService.get_user_profile(user.id)
                if not profile.profile_photo_url:
                    assert 'bi-person-fill' in profile_html, "Should show default person icon when no photo"
                    print("✅ Default placeholder shown when no photo uploaded")
                
                print("\nStep 3: Uploading profile photo")
                
                # Step 3: Upload profile photo
                test_image = create_test_image(400, 400, 'JPEG', 'green')
                file_storage = create_file_storage(test_image, 'web_test.jpg', 'image/jpeg')
                
                upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                    user.id, file_storage
                )
                
                assert upload_success, f"Photo upload should succeed: {upload_message}"
                assert photo_url is not None, "Photo URL should be returned"
                print(f"✅ Photo uploaded successfully: {photo_url}")
                
                print("\nStep 4: Verifying photo visibility on profile page")
                
                # Step 4: Access profile page with photo
                response_with_photo = client.get(f'/profile/user/{user.id}')
                assert response_with_photo.status_code == 200, f"Profile page should be accessible after photo upload"
                
                profile_html_with_photo = response_with_photo.get_data(as_text=True)
                
                # Verify photo is displayed
                assert photo_url in profile_html_with_photo, f"Photo URL {photo_url} should be in HTML"
                assert '<img src="' + photo_url + '"' in profile_html_with_photo, "Should have img tag with photo URL"
                assert 'alt="Web Photo User"' in profile_html_with_photo, "Should have alt text with user name"
                print("✅ Profile photo is visible in HTML")
                
                # Verify placeholder is NOT shown when photo exists
                assert 'bi-person-fill' not in profile_html_with_photo, "Should not show placeholder icon when photo exists"
                print("✅ Default placeholder hidden when photo exists")
                
                print("\nStep 5: Testing photo accessibility")
                
                # Step 5: Test that the photo URL is actually accessible
                # Note: In a real deployment, this would be served by a web server
                # For testing, we verify the URL format and database record
                
                photo_record = ProfilePhoto.query.filter_by(user_id=user.id, is_deleted=False).first()
                assert photo_record is not None, "Photo record should exist in database"
                assert photo_record.filename in photo_url, "Photo URL should contain filename"
                print("✅ Photo URL format is correct and database record exists")
                
                print("\nStep 6: Testing profile completion integration")
                
                # Step 6: Verify profile completion reflects photo upload
                completion = ProfileManagementService.get_profile_completion_percentage(user.id)
                assert completion >= 66, f"Profile completion should be at least 66% with photo, got {completion}%"
                print(f"✅ Profile completion updated to {completion}%")
                
                print("\nStep 7: Testing photo deletion and page update")
                
                # Step 7: Delete photo and verify page updates
                delete_success, delete_message = ProfilePhotoService.delete_profile_photo(user.id)
                assert delete_success, f"Photo deletion should succeed: {delete_message}"
                print("✅ Photo deleted successfully")
                
                # Check profile page after deletion
                response_after_delete = client.get(f'/profile/user/{user.id}')
                assert response_after_delete.status_code == 200, "Profile page should be accessible after photo deletion"
                
                profile_html_after_delete = response_after_delete.get_data(as_text=True)
                
                # Should show placeholder again
                assert photo_url not in profile_html_after_delete, "Photo URL should not be in HTML after deletion"
                assert 'bi-person-fill' in profile_html_after_delete, "Should show placeholder icon after photo deletion"
                print("✅ Profile page correctly shows placeholder after photo deletion")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_profile_photo_css_styling():
    """Test that profile photo has proper CSS styling."""
    print("\n" + "="*70)
    print("🎨 Testing Profile Photo CSS Styling")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "cssphoto@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user and upload photo
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "CSS Photo User"
        )
        assert success, f"Setup failed: {message}"
        
        # Login user
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        assert login_success, f"Login failed: {login_message}"
        
        try:
            # Upload photo
            test_image = create_test_image(500, 500, 'PNG', 'purple')
            file_storage = create_file_storage(test_image, 'css_test.png', 'image/png')
            
            upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                user.id, file_storage
            )
            assert upload_success, f"Photo upload should succeed: {upload_message}"
            
            # Test with client
            with app.test_client() as client:
                # Simulate logged in session
                with client.session_transaction() as sess:
                    sess['user_id'] = user.id
                    sess['session_token'] = session.get('session_token')
                
                # Get profile page
                response = client.get(f'/profile/user/{user.id}')
                assert response.status_code == 200, "Profile page should be accessible"
                
                profile_html = response.get_data(as_text=True)
                
                # Check for proper CSS classes and styling
                assert 'class="profile-photo"' in profile_html, "Profile photo should have CSS class"
                assert 'alt="CSS Photo User"' in profile_html, "Should have proper alt text"
                print("✅ Profile photo has proper CSS classes")
                
                # Check that the image tag is properly formed
                assert f'<img src="{photo_url}"' in profile_html, "Should have properly formed img tag"
                print("✅ Image tag is properly formed")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_profile_photo_different_formats():
    """Test that different photo formats are displayed correctly."""
    print("\n" + "="*70)
    print("🖼️ Testing Different Photo Formats Display")
    print("="*70)
    
    app = create_app()
    
    formats_to_test = [
        ('format_jpg@example.com', 'test.jpg', 'image/jpeg', 'JPEG', 'red'),
        ('format_png@example.com', 'test.png', 'image/png', 'PNG', 'blue'),
        ('format_gif@example.com', 'test.gif', 'image/gif', 'GIF', 'yellow'),
    ]
    
    for email, filename, content_type, pil_format, color in formats_to_test:
        print(f"\nTesting {pil_format} format display...")
        
        with app.test_request_context():
            # Clean up any existing test user
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
            
            # Create user
            success, message, user = AuthenticationService.register_user(
                email, "password123", f"{pil_format} User"
            )
            assert success, f"Setup failed: {message}"
            
            # Login user
            login_success, login_message, login_user = AuthenticationService.login_user(
                email, "password123"
            )
            assert login_success, f"Login failed: {login_message}"
            
            try:
                # Upload photo in specific format
                test_image = create_test_image(300, 300, pil_format, color)
                file_storage = create_file_storage(test_image, filename, content_type)
                
                upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                    user.id, file_storage
                )
                assert upload_success, f"{pil_format} upload should succeed: {upload_message}"
                
                # Test with client
                with app.test_client() as client:
                    # Simulate logged in session
                    with client.session_transaction() as sess:
                        sess['user_id'] = user.id
                        sess['session_token'] = session.get('session_token')
                    
                    # Check profile page displays the photo
                    response = client.get(f'/profile/user/{user.id}')
                    assert response.status_code == 200, f"Profile page should be accessible for {pil_format}"
                    
                    profile_html = response.get_data(as_text=True)
                    assert photo_url in profile_html, f"{pil_format} photo URL should be in HTML"
                    print(f"✅ {pil_format} format displays correctly")
                    
            finally:
                # Clean up after test
                user.hard_delete()

if __name__ == "__main__":
    print("Web Interface Test for Profile Photo Visibility")
    print("=" * 80)
    
    try:
        # Run the tests
        test_profile_photo_web_visibility()
        test_profile_photo_css_styling()
        test_profile_photo_different_formats()
        
        print("\n" + "="*80)
        print("📋 WEB VISIBILITY TEST SUMMARY")
        print("="*80)
        print("🎉 Profile Photo Web Visibility: PASSED")
        print("✅ Profile photo is visible on profile page")
        print("✅ Default placeholder shown when no photo")
        print("✅ Photo URL correctly embedded in HTML")
        print("✅ CSS styling applied correctly")
        print("✅ Different formats display correctly")
        print("✅ Photo deletion updates page correctly")
        
    except AssertionError as e:
        print(f"\n❌ WEB VISIBILITY TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ WEB VISIBILITY TEST ERROR: {e}")
        sys.exit(1)
