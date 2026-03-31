"""
Tests for profile component.
"""
import pytest
import tempfile
import os
from PIL import Image
from app.components.profile.services import ProfileManagementService, ProfilePhotoService
from app.models import UserProfile, ProfilePhoto


class TestProfileManagementService:
    """Test profile management service functionality."""
    
    def test_get_user_profile(self, db_session, sample_user_profile):
        """Test getting user profile."""
        profile = ProfileManagementService.get_user_profile(sample_user_profile.user_id)
        
        assert profile is not None
        assert profile.id == sample_user_profile.id
        assert profile.name == sample_user_profile.name
    
    def test_get_user_profile_not_found(self, db_session):
        """Test getting non-existent user profile."""
        profile = ProfileManagementService.get_user_profile('nonexistent-id')
        assert profile is None
    
    def test_update_profile_success(self, db_session, sample_user_profile):
        """Test successful profile update."""
        success, message, profile = ProfileManagementService.update_profile(
            sample_user_profile.user_id,
            name='Updated Name',
            biography='Updated biography'
        )
        
        assert success is True
        assert 'successful' in message
        assert profile.name == 'Updated Name'
        assert profile.biography == 'Updated biography'
    
    def test_update_profile_invalid_name(self, db_session, sample_user_profile):
        """Test profile update with invalid name."""
        success, message, profile = ProfileManagementService.update_profile(
            sample_user_profile.user_id,
            name='X'  # Too short
        )
        
        assert success is False
        assert 'at least 2 characters' in message
    
    def test_update_profile_biography_too_long(self, db_session, sample_user_profile):
        """Test profile update with biography too long."""
        long_bio = 'x' * 501  # Exceeds 500 character limit
        
        success, message, profile = ProfileManagementService.update_profile(
            sample_user_profile.user_id,
            biography=long_bio
        )
        
        assert success is False
        assert 'less than 500 characters' in message
    
    def test_get_profile_completion_percentage(self, db_session, sample_user):
        """Test profile completion calculation."""
        # Create a minimal profile with just name
        from app.models import UserProfile
        profile = UserProfile(
            user_id=sample_user.id,
            name='Test User'
        )
        profile.save()
        
        # Initially should have name only (33%)
        completion = ProfileManagementService.get_profile_completion_percentage(
            sample_user.id
        )
        assert completion == 33
        
        # Add biography (66%)
        profile.biography = 'Test biography'
        profile.save()
        
        completion = ProfileManagementService.get_profile_completion_percentage(
            sample_user.id
        )
        assert completion == 66
        
        # Add photo URL (100%)
        profile.profile_photo_url = '/uploads/test.jpg'
        profile.save()
        
        completion = ProfileManagementService.get_profile_completion_percentage(
            sample_user.id
        )
        assert completion == 100
    
    def test_get_user_stats(self, db_session, sample_user):
        """Test getting user statistics."""
        stats = ProfileManagementService.get_user_stats(sample_user.id)
        
        assert isinstance(stats, dict)
        assert 'facts_submitted' in stats
        assert 'comments_posted' in stats
        assert 'fact_votes_cast' in stats
        assert 'comment_votes_cast' in stats
        assert 'profile_completion' in stats
        
        # Initially all should be 0 except profile completion
        assert stats['facts_submitted'] == 0
        assert stats['comments_posted'] == 0
        assert stats['fact_votes_cast'] == 0
        assert stats['comment_votes_cast'] == 0


class TestProfilePhotoService:
    """Test profile photo service functionality."""
    
    def test_allowed_file_valid_extensions(self):
        """Test allowed file extensions."""
        assert ProfilePhotoService._allowed_file('test.jpg') is True
        assert ProfilePhotoService._allowed_file('test.jpeg') is True
        assert ProfilePhotoService._allowed_file('test.png') is True
        assert ProfilePhotoService._allowed_file('test.gif') is True
        assert ProfilePhotoService._allowed_file('TEST.JPG') is True  # Case insensitive
    
    def test_allowed_file_invalid_extensions(self):
        """Test invalid file extensions."""
        assert ProfilePhotoService._allowed_file('test.txt') is False
        assert ProfilePhotoService._allowed_file('test.pdf') is False
        assert ProfilePhotoService._allowed_file('test') is False
        assert ProfilePhotoService._allowed_file('') is False
    
    def test_get_file_extension(self):
        """Test getting file extension."""
        assert ProfilePhotoService._get_file_extension('test.jpg') == 'jpg'
        assert ProfilePhotoService._get_file_extension('test.JPEG') == 'jpeg'
        assert ProfilePhotoService._get_file_extension('image.png') == 'png'
    
    def test_process_image(self, app_context):
        """Test image processing."""
        # Create a temporary test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            # Create a test image
            img = Image.new('RGB', (800, 600), color='red')
            img.save(tmp_file.name, 'JPEG')
            
            # Process the image
            processed_path = ProfilePhotoService._process_image(
                tmp_file.name, 'test.jpg'
            )
            
            # Check that processed image exists and is smaller
            assert os.path.exists(processed_path)
            
            with Image.open(processed_path) as processed_img:
                # Should be resized to fit within 300x300
                assert processed_img.width <= 300
                assert processed_img.height <= 300
            
            # Clean up
            os.unlink(tmp_file.name)
            if os.path.exists(processed_path):
                os.unlink(processed_path)


class TestProfileRoutes:
    """Test profile routes."""
    
    def test_view_profile_page(self, client, sample_user_profile):
        """Test viewing profile page."""
        response = client.get(f'/profile/user/{sample_user_profile.user_id}')
        assert response.status_code == 200
        assert sample_user_profile.name.encode() in response.data
    
    def test_view_profile_not_found(self, client, db_session):
        """Test viewing non-existent profile."""
        response = client.get('/profile/user/nonexistent-id')
        assert response.status_code == 404
    
    def test_edit_profile_requires_auth(self, client):
        """Test that edit profile requires authentication."""
        response = client.get('/profile/edit')
        assert response.status_code == 302  # Redirect to login
    
    def test_my_profile_requires_auth(self, client):
        """Test that my profile requires authentication."""
        response = client.get('/profile/')
        assert response.status_code == 302  # Redirect to login
