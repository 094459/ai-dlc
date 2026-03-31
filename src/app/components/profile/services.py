"""
Profile services for user profile management and photo handling.
"""
import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app, request
from app import db
from app.models import User, UserProfile, ProfilePhoto
from app.components.security.services import ValidationService, AuditService


class ProfileManagementService:
    """Service for user profile management."""
    
    @staticmethod
    def get_user_profile(user_id):
        """
        Get user profile by user ID.
        
        Args:
            user_id (str): User ID
            
        Returns:
            UserProfile or None: User profile if found
        """
        return UserProfile.query.filter_by(
            user_id=user_id,
            is_deleted=False
        ).first()
    
    @staticmethod
    def update_profile(user_id, name=None, biography=None):
        """
        Update user profile information.
        
        Args:
            user_id (str): User ID
            name (str): New name
            biography (str): New biography
            
        Returns:
            tuple: (success: bool, message: str, profile: UserProfile or None)
        """
        try:
            profile = ProfileManagementService.get_user_profile(user_id)
            if not profile:
                return False, "Profile not found", None
            
            old_values = {
                'name': profile.name,
                'biography': profile.biography
            }
            
            # Validate and update name
            if name is not None:
                name_valid, name_msg = ValidationService.validate_name(name)
                if not name_valid:
                    return False, name_msg, None
                profile.name = name.strip()
            
            # Validate and update biography
            if biography is not None:
                biography = biography.strip()
                if len(biography) > 500:
                    return False, "Biography must be less than 500 characters", None
                profile.biography = biography if biography else None
            
            profile.save()
            
            # Log the update
            new_values = {
                'name': profile.name,
                'biography': profile.biography
            }
            
            AuditService.log_action(
                user_id=user_id,
                action_type='profile_update',
                resource_type='profile',
                resource_id=profile.id,
                old_values=str(old_values),
                new_values=str(new_values),
                success=True
            )
            
            return True, "Profile updated successfully", profile
            
        except Exception as e:
            current_app.logger.error(f"Profile update error: {str(e)}")
            return False, "Failed to update profile", None
    
    @staticmethod
    def get_profile_completion_percentage(user_id):
        """
        Calculate profile completion percentage.
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: Completion percentage (0-100)
        """
        profile = ProfileManagementService.get_user_profile(user_id)
        if not profile:
            return 0
        
        completion_score = 0
        total_fields = 3
        
        # Name is required, so it's always filled
        completion_score += 1
        
        # Biography
        if profile.biography and profile.biography.strip():
            completion_score += 1
        
        # Profile photo
        if profile.profile_photo_url:
            completion_score += 1
        
        return int((completion_score / total_fields) * 100)
    
    @staticmethod
    def get_user_recent_activity(user_id, limit=10):
        """
        Get recent activity for a user.
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of activities to return
            
        Returns:
            list: List of recent activities
        """
        from app.models import Fact, Comment, FactVote, CommentVote
        from datetime import datetime
        
        activities = []
        
        try:
            # Get recent facts
            recent_facts = Fact.query.filter_by(
                user_id=user_id, 
                is_deleted=False
            ).order_by(Fact.created_at.desc()).limit(5).all()
            
            for fact in recent_facts:
                activities.append({
                    'type': 'fact_created',
                    'timestamp': fact.created_at,
                    'description': f'Posted a new fact',
                    'content': fact.content[:100] + '...' if len(fact.content) > 100 else fact.content,
                    'url': f'/facts/{fact.id}',
                    'icon': 'bi-file-text'
                })
            
            # Get recent comments
            recent_comments = Comment.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).order_by(Comment.created_at.desc()).limit(5).all()
            
            for comment in recent_comments:
                activities.append({
                    'type': 'comment_created',
                    'timestamp': comment.created_at,
                    'description': f'Commented on a fact',
                    'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                    'url': f'/facts/{comment.fact_id}#comment-{comment.id}',
                    'icon': 'bi-chat-dots'
                })
            
            # Get recent fact votes
            recent_fact_votes = FactVote.query.filter_by(
                user_id=user_id
            ).order_by(FactVote.created_at.desc()).limit(3).all()
            
            for vote in recent_fact_votes:
                activities.append({
                    'type': 'fact_voted',
                    'timestamp': vote.created_at,
                    'description': f'Voted "{vote.vote_type}" on a fact',
                    'content': None,
                    'url': f'/facts/{vote.fact_id}',
                    'icon': 'bi-hand-thumbs-up' if vote.vote_type == 'fact' else 'bi-hand-thumbs-down'
                })
            
            # Sort all activities by timestamp (most recent first)
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Return limited number of activities
            return activities[:limit]
            
        except Exception as e:
            print(f"Error getting user recent activity: {e}")
            return []
    
    @staticmethod
    def get_user_recent_facts(user_id, limit=5):
        """
        Get user's recent facts for profile display.
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of facts to return
            
        Returns:
            list: List of recent facts with metadata
        """
        from app.models import Fact, FactVote
        
        try:
            # Get recent facts by user
            facts = Fact.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).order_by(Fact.created_at.desc()).limit(limit).all()
            
            facts_data = []
            for fact in facts:
                # Get vote counts for each fact
                vote_counts = FactVote.query.filter_by(fact_id=fact.id).all()
                fact_votes = len([v for v in vote_counts if v.vote_type == 'fact'])
                fake_votes = len([v for v in vote_counts if v.vote_type == 'fake'])
                
                facts_data.append({
                    'id': fact.id,
                    'content': fact.content,
                    'created_at': fact.created_at,
                    'edit_count': fact.edit_count,
                    'fact_votes': fact_votes,
                    'fake_votes': fake_votes,
                    'total_votes': fact_votes + fake_votes,
                    'hashtags': getattr(fact, 'hashtags', [])
                })
            
            return facts_data
            
        except Exception as e:
            print(f"Error getting user recent facts: {e}")
            return []
    
    @staticmethod
    def get_user_stats(user_id):
        """
        Get user statistics for profile display.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User statistics
        """
        from app.models import Fact, Comment, FactVote, CommentVote
        
        stats = {
            'facts_submitted': 0,
            'comments_posted': 0,
            'fact_votes_cast': 0,
            'comment_votes_cast': 0,
            'profile_completion': 0
        }
        
        try:
            # Count facts submitted
            stats['facts_submitted'] = Fact.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).count()
            
            # Count comments posted
            stats['comments_posted'] = Comment.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).count()
            
            # Count votes cast
            stats['fact_votes_cast'] = FactVote.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).count()
            
            stats['comment_votes_cast'] = CommentVote.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).count()
            
            # Profile completion
            stats['profile_completion'] = ProfileManagementService.get_profile_completion_percentage(user_id)
            
        except Exception as e:
            current_app.logger.error(f"Error getting user stats: {str(e)}")
        
        return stats


class ProfilePhotoService:
    """Service for profile photo management."""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    PHOTO_SIZES = {
        'thumbnail': (100, 100),
        'medium': (300, 300),
        'large': (600, 600)
    }
    
    @staticmethod
    def upload_profile_photo(user_id, file):
        """
        Upload and process profile photo.
        
        Args:
            user_id (str): User ID
            file: Uploaded file object
            
        Returns:
            tuple: (success: bool, message: str, photo_url: str or None)
        """
        try:
            # Validate file
            if not file or file.filename == '':
                return False, "No file selected", None
            
            if not ProfilePhotoService._allowed_file(file.filename):
                return False, "Invalid file type. Please use PNG, JPG, JPEG, or GIF", None
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > ProfilePhotoService.MAX_FILE_SIZE:
                return False, "File too large. Maximum size is 5MB", None
            
            # Get user profile
            profile = ProfileManagementService.get_user_profile(user_id)
            if not profile:
                return False, "Profile not found", None
            
            # Generate unique filename
            file_extension = ProfilePhotoService._get_file_extension(file.filename)
            filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Create upload directory
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_photos')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save original file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Process and resize image
            processed_path = ProfilePhotoService._process_image(file_path, filename)
            
            # Remove original if different from processed
            if processed_path != file_path:
                os.remove(file_path)
            
            # Save photo record
            photo = ProfilePhoto(
                user_id=user_id,
                profile_id=profile.id,
                filename=os.path.basename(processed_path),
                file_path=processed_path,
                file_size=os.path.getsize(processed_path),
                mime_type=f"image/{file_extension}"
            )
            photo.save()
            
            # Update profile photo URL
            photo_url = f"/uploads/profile_photos/{photo.filename}"
            profile.profile_photo_url = photo_url
            profile.save()
            
            # Log the upload
            AuditService.log_action(
                user_id=user_id,
                action_type='profile_photo_upload',
                resource_type='profile_photo',
                resource_id=photo.id,
                success=True
            )
            
            return True, "Photo uploaded successfully", photo_url
            
        except Exception as e:
            current_app.logger.error(f"Photo upload error: {str(e)}")
            return False, "Failed to upload photo", None
    
    @staticmethod
    def delete_profile_photo(user_id):
        """
        Delete user's profile photo.
        
        Args:
            user_id (str): User ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            profile = ProfileManagementService.get_user_profile(user_id)
            if not profile:
                return False, "Profile not found"
            
            # Get current photo
            photo = ProfilePhoto.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).first()
            
            if photo:
                # Delete file from filesystem
                try:
                    if os.path.exists(photo.file_path):
                        os.remove(photo.file_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete photo file: {str(e)}")
                
                # Soft delete photo record
                photo.delete()
            
            # Clear profile photo URL
            profile.profile_photo_url = None
            profile.save()
            
            # Log the deletion
            AuditService.log_action(
                user_id=user_id,
                action_type='profile_photo_delete',
                resource_type='profile_photo',
                resource_id=photo.id if photo else None,
                success=True
            )
            
            return True, "Photo deleted successfully"
            
        except Exception as e:
            current_app.logger.error(f"Photo deletion error: {str(e)}")
            return False, "Failed to delete photo"
    
    @staticmethod
    def _allowed_file(filename):
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ProfilePhotoService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def _get_file_extension(filename):
        """Get file extension."""
        return filename.rsplit('.', 1)[1].lower()
    
    @staticmethod
    def _process_image(file_path, filename):
        """
        Process and resize image.
        
        Args:
            file_path (str): Path to original image
            filename (str): Original filename
            
        Returns:
            str: Path to processed image
        """
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize to medium size for profile photos
                target_size = ProfilePhotoService.PHOTO_SIZES['medium']
                
                # Calculate resize dimensions maintaining aspect ratio
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # Create new filename for processed image
                name, ext = os.path.splitext(filename)
                processed_filename = f"{name}_processed{ext}"
                processed_path = os.path.join(os.path.dirname(file_path), processed_filename)
                
                # Save processed image
                img.save(processed_path, optimize=True, quality=85)
                
                return processed_path
                
        except Exception as e:
            current_app.logger.error(f"Image processing error: {str(e)}")
            return file_path  # Return original if processing fails
