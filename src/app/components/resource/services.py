"""
Resource services for URL and image attachment management.
"""
import os
import uuid
import requests
from urllib.parse import urlparse
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app
from app import db
from app.models import FactResource, ResourceValidation
from app.components.security.services import ValidationService, AuditService


class ResourceManagementService:
    """Service for managing fact resources (URLs and images)."""
    
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGES_PER_FACT = 5
    MAX_URLS_PER_FACT = 10
    
    @staticmethod
    def add_url_resource(fact_id, user_id, url, display_title=None):
        """
        Add a URL resource to a fact.
        
        Args:
            fact_id (str): Fact ID
            user_id (str): User ID adding the resource
            url (str): URL to add
            display_title (str): Optional display title
            
        Returns:
            tuple: (success: bool, message: str, resource: FactResource or None)
        """
        try:
            # Validate URL
            url_valid, url_msg = ValidationService.validate_url(url)
            if not url_valid:
                return False, url_msg, None
            
            # Check URL limit
            existing_urls = FactResource.query.filter_by(
                fact_id=fact_id,
                resource_type='url',
                is_deleted=False
            ).count()
            
            if existing_urls >= ResourceManagementService.MAX_URLS_PER_FACT:
                return False, f"Maximum {ResourceManagementService.MAX_URLS_PER_FACT} URLs allowed per fact", None
            
            # Create resource
            resource = FactResource(
                fact_id=fact_id,
                resource_type='url',
                resource_value=url,
                display_title=display_title[:200] if display_title else None
            )
            resource.save()
            
            # Create validation record
            validation = ResourceValidation(
                resource_id=resource.id,
                validation_status='pending'
            )
            validation.save()
            
            # Start async validation
            ResourceValidationService.validate_url_async(resource.id, url)
            
            # Log addition
            AuditService.log_action(
                user_id=user_id,
                action_type='resource_add_url',
                resource_type='fact_resource',
                resource_id=resource.id,
                new_values=url,
                success=True
            )
            
            return True, "URL added successfully", resource
            
        except Exception as e:
            current_app.logger.error(f"URL resource addition error: {str(e)}")
            return False, "Failed to add URL", None
    
    @staticmethod
    def add_image_resource(fact_id, user_id, file, display_title=None):
        """
        Add an image resource to a fact.
        
        Args:
            fact_id (str): Fact ID
            user_id (str): User ID adding the resource
            file: Uploaded file object
            display_title (str): Optional display title
            
        Returns:
            tuple: (success: bool, message: str, resource: FactResource or None)
        """
        try:
            # Validate file
            if not file or file.filename == '':
                return False, "No file selected", None
            
            if not ResourceManagementService._allowed_image_file(file.filename):
                return False, "Invalid file type. Please use PNG, JPG, JPEG, GIF, or WebP", None
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > ResourceManagementService.MAX_IMAGE_SIZE:
                return False, "File too large. Maximum size is 10MB", None
            
            # Check image limit
            existing_images = FactResource.query.filter_by(
                fact_id=fact_id,
                resource_type='image',
                is_deleted=False
            ).count()
            
            if existing_images >= ResourceManagementService.MAX_IMAGES_PER_FACT:
                return False, f"Maximum {ResourceManagementService.MAX_IMAGES_PER_FACT} images allowed per fact", None
            
            # Generate unique filename
            file_extension = ResourceManagementService._get_file_extension(file.filename)
            filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Create upload directory
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'fact_images')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Process image
            processed_path = ResourceManagementService._process_image(file_path, filename)
            
            # Remove original if different from processed
            if processed_path != file_path:
                os.remove(file_path)
            
            # Create resource
            resource_url = f"/uploads/fact_images/{os.path.basename(processed_path)}"
            
            resource = FactResource(
                fact_id=fact_id,
                resource_type='image',
                resource_value=resource_url,
                display_title=display_title[:200] if display_title else None,
                file_size=os.path.getsize(processed_path),
                mime_type=f"image/{file_extension}"
            )
            resource.save()
            
            # Create validation record (images are immediately valid)
            validation = ResourceValidation(
                resource_id=resource.id,
                validation_status='valid',
                validation_message='Image uploaded successfully'
            )
            validation.save()
            
            # Log addition
            AuditService.log_action(
                user_id=user_id,
                action_type='resource_add_image',
                resource_type='fact_resource',
                resource_id=resource.id,
                new_values=resource_url,
                success=True
            )
            
            return True, "Image added successfully", resource
            
        except Exception as e:
            current_app.logger.error(f"Image resource addition error: {str(e)}")
            return False, "Failed to add image", None
    
    @staticmethod
    def remove_resource(resource_id, user_id):
        """
        Remove a resource from a fact.
        
        Args:
            resource_id (str): Resource ID
            user_id (str): User ID removing the resource
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Get resource
            resource = FactResource.query.filter_by(
                id=resource_id,
                is_deleted=False
            ).first()
            
            if not resource:
                return False, "Resource not found"
            
            # Check ownership (user must own the fact)
            from app.models import Fact
            fact = Fact.query.filter_by(
                id=resource.fact_id,
                user_id=user_id,
                is_deleted=False
            ).first()
            
            if not fact:
                return False, "You can only remove resources from your own facts"
            
            # Delete file if it's an image
            if resource.resource_type == 'image':
                try:
                    # Extract filename from URL
                    filename = os.path.basename(resource.resource_value)
                    file_path = os.path.join(
                        current_app.config['UPLOAD_FOLDER'], 
                        'fact_images', 
                        filename
                    )
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete image file: {str(e)}")
            
            # Soft delete resource
            resource.delete()
            
            # Log removal
            AuditService.log_action(
                user_id=user_id,
                action_type='resource_remove',
                resource_type='fact_resource',
                resource_id=resource.id,
                old_values=resource.resource_value,
                success=True
            )
            
            return True, "Resource removed successfully"
            
        except Exception as e:
            current_app.logger.error(f"Resource removal error: {str(e)}")
            return False, "Failed to remove resource"
    
    @staticmethod
    def get_fact_resources(fact_id):
        """
        Get all resources for a fact.
        
        Args:
            fact_id (str): Fact ID
            
        Returns:
            dict: Resources grouped by type
        """
        try:
            resources = FactResource.query.filter_by(
                fact_id=fact_id,
                is_deleted=False,
                is_active=True
            ).order_by(FactResource.created_at.asc()).all()
            
            urls = []
            images = []
            
            for resource in resources:
                if resource.resource_type == 'url':
                    urls.append(resource)
                elif resource.resource_type == 'image':
                    images.append(resource)
            
            return {
                'urls': urls,
                'images': images,
                'total_count': len(resources)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting fact resources: {str(e)}")
            return {'urls': [], 'images': [], 'total_count': 0}
    
    @staticmethod
    def _allowed_image_file(filename):
        """Check if image file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ResourceManagementService.ALLOWED_IMAGE_EXTENSIONS
    
    @staticmethod
    def _get_file_extension(filename):
        """Get file extension."""
        return filename.rsplit('.', 1)[1].lower()
    
    @staticmethod
    def _process_image(file_path, filename):
        """
        Process and optimize image.
        
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
                
                # Resize if too large (max 1200px on longest side)
                max_size = 1200
                if max(img.width, img.height) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
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


class ResourceValidationService:
    """Service for validating resource URLs and health checking."""
    
    @staticmethod
    def validate_url_async(resource_id, url):
        """
        Validate a URL asynchronously (simplified synchronous version for now).
        
        Args:
            resource_id (str): Resource ID
            url (str): URL to validate
        """
        try:
            # Get resource
            resource = db.session.get(FactResource, resource_id)
            if not resource:
                return
            
            # Get validation record
            validation = ResourceValidation.query.filter_by(resource_id=resource_id).first()
            if not validation:
                return
            
            # Perform validation
            status, message = ResourceValidationService._check_url_health(url)
            
            # Update validation record
            validation.validation_status = status
            validation.validation_message = message
            validation.check_count += 1
            validation.last_checked = datetime.utcnow()
            validation.save()
            
            # Deactivate resource if invalid
            if status in ['invalid', 'broken']:
                resource.is_active = False
                resource.save()
            
        except Exception as e:
            current_app.logger.error(f"URL validation error: {str(e)}")
    
    @staticmethod
    def _check_url_health(url, timeout=10):
        """
        Check if URL is accessible and valid.
        
        Args:
            url (str): URL to check
            timeout (int): Request timeout in seconds
            
        Returns:
            tuple: (status: str, message: str)
        """
        try:
            # Basic URL format validation
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return 'invalid', 'Invalid URL format'
            
            # Make HEAD request to check if URL is accessible
            headers = {
                'User-Agent': 'FactChecker/1.0 (URL Validator)'
            }
            
            response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                return 'valid', 'URL is accessible'
            elif response.status_code in [301, 302, 303, 307, 308]:
                return 'valid', f'URL redirects (status: {response.status_code})'
            elif response.status_code == 404:
                return 'broken', 'URL not found (404)'
            elif response.status_code == 403:
                return 'broken', 'Access forbidden (403)'
            else:
                return 'broken', f'HTTP error: {response.status_code}'
                
        except requests.exceptions.Timeout:
            return 'broken', 'Request timeout'
        except requests.exceptions.ConnectionError:
            return 'broken', 'Connection error'
        except requests.exceptions.RequestException as e:
            return 'broken', f'Request error: {str(e)}'
        except Exception as e:
            return 'invalid', f'Validation error: {str(e)}'
    
    @staticmethod
    def revalidate_resource(resource_id):
        """
        Manually revalidate a resource.
        
        Args:
            resource_id (str): Resource ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            resource = db.session.get(FactResource, resource_id)
            if not resource or resource.resource_type != 'url':
                return False, "Resource not found or not a URL"
            
            ResourceValidationService.validate_url_async(resource_id, resource.resource_value)
            return True, "Resource revalidated successfully"
            
        except Exception as e:
            current_app.logger.error(f"Resource revalidation error: {str(e)}")
            return False, "Failed to revalidate resource"
