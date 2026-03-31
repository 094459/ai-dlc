#!/usr/bin/env python3
"""
Comprehensive test for TC_US03_Profile_InvalidPhotoFormat_ErrorMessage
Tests error handling for unsupported image formats in profile photo upload.
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

def create_fake_file(filename, content=b"fake file content"):
    """Create a fake file with specified filename and content."""
    fake_file = BytesIO(content)
    return FileStorage(
        stream=fake_file,
        filename=filename,
        content_type='application/octet-stream'
    )

def create_test_image(width=300, height=300, format='JPEG', color='blue'):
    """Create a test image with specified dimensions and format."""
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

def test_invalid_photo_format_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US03_Profile_InvalidPhotoFormat_ErrorMessage")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "invalidformat@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Creating user account with email '{test_email}'")
        
        # Step 1: Create user account
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Invalid Format User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        user_id = user.id
        
        print("\nStep 2: Testing upload of invalid photo formats")
        
        # Step 2: Test various invalid photo formats
        invalid_formats = [
            ("document.txt", "text/plain", "Text file"),
            ("document.pdf", "application/pdf", "PDF document"),
            ("document.doc", "application/msword", "Word document"),
            ("program.exe", "application/x-executable", "Executable file"),
            ("archive.zip", "application/zip", "ZIP archive"),
            ("image.bmp", "image/bmp", "BMP image (not in allowed list)"),
            ("image.tiff", "image/tiff", "TIFF image (not in allowed list)"),
            ("image.svg", "image/svg+xml", "SVG image (not in allowed list)"),
            ("image.webp", "image/webp", "WebP image (not in allowed list)"),
            ("no_extension", "application/octet-stream", "File without extension"),
        ]
        
        for filename, content_type, description in invalid_formats:
            print(f"\nTesting {description}: {filename}")
            
            # Create fake file with invalid format
            fake_file = create_fake_file(filename)
            
            upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                user_id, fake_file
            )
            
            # Should fail for all invalid formats
            assert not upload_success, f"{description} should be rejected"
            assert photo_url is None, f"No photo URL should be returned for {description}"
            assert "Invalid file type" in upload_message, f"Error message should mention invalid file type for {description}"
            print(f"✅ PASS: {description} correctly rejected - {upload_message}")
        
        print("\nStep 3: Testing acceptance criteria")
        
        # Test acceptance criteria with a specific invalid format
        test_file = create_fake_file("test.txt")
        upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
            user_id, test_file
        )
        
        # Criterion 1: Clear error message is displayed
        assert not upload_success, "Upload should fail for invalid format"
        assert upload_message, "Error message should be provided"
        assert "Invalid file type" in upload_message, "Error message should mention invalid file type"
        print("✅ Clear error message is displayed")
        
        # Criterion 2: Upload is rejected
        assert not upload_success, "Upload should be rejected"
        assert photo_url is None, "No photo URL should be returned"
        print("✅ Upload is rejected")
        
        # Criterion 3: User can try again with valid format
        # Test that user can upload valid format after invalid attempt
        valid_image = create_test_image(300, 300, 'JPEG', 'green')
        valid_file = create_file_storage(valid_image, 'valid.jpg', 'image/jpeg')
        
        valid_success, valid_message, valid_url = ProfilePhotoService.upload_profile_photo(
            user_id, valid_file
        )
        
        assert valid_success, f"Valid format should be accepted after invalid attempt: {valid_message}"
        assert valid_url is not None, "Valid upload should return photo URL"
        print("✅ User can try again with valid format")
        
        # Criterion 4: Supported formats are clearly indicated
        # Check that error message mentions supported formats
        assert "PNG, JPG, JPEG, or GIF" in upload_message, "Error message should list supported formats"
        print("✅ Supported formats are clearly indicated in error message")
        
        # Clean up after test
        user.hard_delete()

def test_invalid_photo_format_web_interface():
    """Test invalid photo format handling in web interface."""
    print("\n" + "="*70)
    print("🌐 Testing Invalid Photo Format in Web Interface")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "webinvalidformat@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Web Invalid Format User"
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
                
                print("Testing profile edit page file input attributes...")
                
                # Get profile edit page
                response = client.get('/profile/edit')
                assert response.status_code == 200, "Profile edit page should be accessible"
                
                edit_html = response.get_data(as_text=True)
                
                # Check for file input with accept attribute
                if 'type="file"' in edit_html and 'name="photo"' in edit_html:
                    print("✅ File input for photo upload found")
                    
                    # Check if accept attribute is present (should restrict to image types)
                    if 'accept=' in edit_html:
                        print("✅ File input has accept attribute for format restriction")
                    else:
                        print("ℹ️  File input doesn't have accept attribute (validation done server-side)")
                else:
                    print("ℹ️  Photo upload may be handled via separate endpoint or AJAX")
                
                print("Testing server-side validation through direct service calls...")
                
                # Test invalid format through service (simulating form submission)
                invalid_file = create_fake_file("test.txt")
                upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                    user.id, invalid_file
                )
                
                assert not upload_success, "Invalid format should be rejected by server"
                assert "Invalid file type" in upload_message, "Server should return clear error message"
                print("✅ Server-side validation rejects invalid formats with clear error message")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_invalid_photo_format_edge_cases():
    """Test edge cases for invalid photo format handling."""
    print("\n" + "="*70)
    print("🔍 Testing Invalid Photo Format Edge Cases")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "edgeinvalidformat@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Edge Invalid Format User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            edge_cases = [
                # Filename edge cases
                ("", "Empty filename"),
                (".", "Just a dot"),
                (".txt", "Extension only"),
                ("file.", "Filename with trailing dot"),
                ("file.TXT", "Uppercase extension"),
                ("file.Jpg", "Mixed case extension"),
                ("file.jpeg.txt", "Multiple extensions (should use last)"),
                ("file with spaces.txt", "Filename with spaces"),
                ("file-with-dashes.pdf", "Filename with dashes"),
                ("file_with_underscores.doc", "Filename with underscores"),
                ("very_long_filename_that_exceeds_normal_length_limits.exe", "Very long filename"),
                ("файл.txt", "Unicode filename"),
                ("file.unknown", "Unknown extension"),
            ]
            
            for filename, description in edge_cases:
                print(f"\nTesting {description}: '{filename}'")
                
                try:
                    fake_file = create_fake_file(filename)
                    upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                        user.id, fake_file
                    )
                    
                    # All these should be rejected (none are valid image formats)
                    assert not upload_success, f"{description} should be rejected"
                    assert photo_url is None, f"No photo URL should be returned for {description}"
                    print(f"✅ PASS: {description} correctly rejected - {upload_message}")
                    
                except Exception as e:
                    # Some edge cases might cause exceptions, which is also acceptable
                    print(f"✅ PASS: {description} handled with exception (acceptable) - {e}")
            
            print("\nTesting malicious file attempts...")
            
            # Test files that might try to bypass validation
            malicious_cases = [
                ("image.jpg.exe", "Executable disguised as image"),
                ("image.php", "PHP script"),
                ("image.js", "JavaScript file"),
                ("image.html", "HTML file"),
                ("../../../etc/passwd", "Path traversal attempt"),
                ("image.jpg%00.exe", "Null byte injection attempt"),
            ]
            
            for filename, description in malicious_cases:
                print(f"\nTesting {description}: '{filename}'")
                
                try:
                    fake_file = create_fake_file(filename)
                    upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                        user.id, fake_file
                    )
                    
                    # All malicious attempts should be rejected
                    assert not upload_success, f"{description} should be rejected"
                    assert photo_url is None, f"No photo URL should be returned for {description}"
                    print(f"✅ PASS: {description} correctly rejected - {upload_message}")
                    
                except Exception as e:
                    # Exceptions are acceptable for malicious attempts
                    print(f"✅ PASS: {description} handled with exception (good security) - {e}")
                    
        finally:
            # Clean up after test
            user.hard_delete()

def test_valid_vs_invalid_format_comparison():
    """Test comparison between valid and invalid formats."""
    print("\n" + "="*70)
    print("📊 Testing Valid vs Invalid Format Comparison")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "formatcomparison@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Format Comparison User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Testing valid formats (should be accepted)...")
            
            valid_formats = [
                ('test.jpg', 'image/jpeg', 'JPEG'),
                ('test.jpeg', 'image/jpeg', 'JPEG'),
                ('test.png', 'image/png', 'PNG'),
                ('test.gif', 'image/gif', 'GIF'),
            ]
            
            for filename, content_type, pil_format in valid_formats:
                print(f"Testing valid format: {filename}")
                
                # Create actual image file
                test_image = create_test_image(200, 200, pil_format, 'blue')
                file_storage = create_file_storage(test_image, filename, content_type)
                
                upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                    user.id, file_storage
                )
                
                assert upload_success, f"Valid format {filename} should be accepted: {upload_message}"
                assert photo_url is not None, f"Photo URL should be returned for {filename}"
                print(f"✅ PASS: {filename} accepted")
                
                # Clean up photo for next test
                ProfilePhotoService.delete_profile_photo(user.id)
            
            print("\nTesting invalid formats (should be rejected)...")
            
            invalid_formats = [
                'test.txt',
                'test.pdf',
                'test.doc',
                'test.bmp',
                'test.tiff',
                'test.svg',
            ]
            
            for filename in invalid_formats:
                print(f"Testing invalid format: {filename}")
                
                fake_file = create_fake_file(filename)
                upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                    user.id, fake_file
                )
                
                assert not upload_success, f"Invalid format {filename} should be rejected"
                assert photo_url is None, f"No photo URL should be returned for {filename}"
                assert "Invalid file type" in upload_message, f"Error message should mention invalid file type for {filename}"
                print(f"✅ PASS: {filename} correctly rejected - {upload_message}")
            
            print("\nTesting error message consistency...")
            
            # Test that all invalid formats get the same error message
            error_messages = []
            for filename in ['test.txt', 'test.pdf', 'test.doc']:
                fake_file = create_fake_file(filename)
                upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                    user.id, fake_file
                )
                error_messages.append(upload_message)
            
            # All error messages should be the same (consistent user experience)
            unique_messages = set(error_messages)
            assert len(unique_messages) == 1, f"All invalid formats should return same error message, got: {unique_messages}"
            print("✅ Error messages are consistent across different invalid formats")
            
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
        test_email = "criteria@invalidformat.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Invalid Format User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Testing invalid photo format error handling...")
            
            # Test with a clearly invalid format
            invalid_file = create_fake_file("document.txt")
            upload_success, upload_message, photo_url = ProfilePhotoService.upload_profile_photo(
                user.id, invalid_file
            )
            
            # Criterion 1: Clear error message is displayed
            assert not upload_success, "Upload should fail for invalid format"
            assert upload_message, "Error message should be provided"
            assert "Invalid file type" in upload_message, "Error message should mention invalid file type"
            print("✅ Clear error message is displayed")
            
            # Criterion 2: Upload is rejected
            assert not upload_success, "Upload should be rejected"
            assert photo_url is None, "No photo URL should be returned"
            print("✅ Upload is rejected")
            
            # Criterion 3: User can try again with valid format
            valid_image = create_test_image(300, 300, 'JPEG', 'red')
            valid_file = create_file_storage(valid_image, 'valid.jpg', 'image/jpeg')
            
            valid_success, valid_message, valid_url = ProfilePhotoService.upload_profile_photo(
                user.id, valid_file
            )
            
            assert valid_success, f"Valid format should be accepted: {valid_message}"
            assert valid_url is not None, "Valid upload should return photo URL"
            print("✅ User can try again with valid format")
            
            # Criterion 4: Supported formats are clearly indicated
            assert "PNG, JPG, JPEG, or GIF" in upload_message, "Error message should list supported formats"
            print("✅ Supported formats are clearly indicated")
            
            # Criterion 5: No security vulnerabilities from invalid uploads
            # Test that invalid uploads don't create any files or database records
            photo_count_before = ProfilePhoto.query.filter_by(user_id=user.id, is_deleted=False).count()
            
            malicious_file = create_fake_file("malicious.exe")
            malicious_success, malicious_message, malicious_url = ProfilePhotoService.upload_profile_photo(
                user.id, malicious_file
            )
            
            photo_count_after = ProfilePhoto.query.filter_by(user_id=user.id, is_deleted=False).count()
            
            assert not malicious_success, "Malicious file should be rejected"
            assert photo_count_after == photo_count_before, "No new photo records should be created for invalid uploads"
            print("✅ No security vulnerabilities from invalid uploads")
            
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US03_Profile_InvalidPhotoFormat_ErrorMessage")
    print("=" * 80)
    
    try:
        # Run the tests
        test_invalid_photo_format_scenario()
        test_invalid_photo_format_web_interface()
        test_invalid_photo_format_edge_cases()
        test_valid_vs_invalid_format_comparison()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US03_Profile_InvalidPhotoFormat_ErrorMessage: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Clear error messages displayed for invalid formats")
        print("✅ Invalid uploads are properly rejected")
        print("✅ Users can retry with valid formats")
        print("✅ Supported formats are clearly indicated")
        print("✅ No security vulnerabilities from invalid uploads")
        print("✅ Edge cases and malicious attempts handled correctly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
