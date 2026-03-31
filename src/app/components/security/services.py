"""
Security services for authorization, validation, and audit logging.
"""
import re
import html
from datetime import datetime
from flask import current_app, request
from app import db
from app.models import AuditLog


class AuthorizationService:
    """Service for role-based access control."""
    
    @staticmethod
    def can_user_access_resource(user, resource_type, resource_id, action):
        """
        Check if user can perform action on resource.
        
        Args:
            user (User): User object
            resource_type (str): Type of resource (fact, comment, etc.)
            resource_id (str): Resource ID
            action (str): Action to perform (read, write, delete, etc.)
            
        Returns:
            bool: Whether user has permission
        """
        if not user or not user.is_active:
            return False
        
        # Admin can do everything
        if user.is_admin:
            return True
        
        # Moderators can moderate content
        if user.is_moderator and action in ['moderate', 'delete', 'restore']:
            return True
        
        # Resource-specific permissions
        if resource_type == 'fact':
            return AuthorizationService._can_access_fact(user, resource_id, action)
        elif resource_type == 'comment':
            return AuthorizationService._can_access_comment(user, resource_id, action)
        elif resource_type == 'profile':
            return AuthorizationService._can_access_profile(user, resource_id, action)
        
        return False
    
    @staticmethod
    def _can_access_fact(user, fact_id, action):
        """Check fact-specific permissions."""
        from app.models import Fact
        
        if action == 'read':
            return True  # Anyone can read facts
        
        if action in ['write', 'edit', 'delete']:
            fact = db.session.get(Fact, fact_id)
            return fact and fact.user_id == user.id
        
        if action == 'vote':
            return True  # Anyone can vote
        
        return False
    
    @staticmethod
    def _can_access_comment(user, comment_id, action):
        """Check comment-specific permissions."""
        from app.models import Comment
        
        if action == 'read':
            return True  # Anyone can read comments
        
        if action in ['write', 'edit', 'delete']:
            comment = db.session.get(Comment, comment_id)
            return comment and comment.user_id == user.id
        
        if action == 'vote':
            return True  # Anyone can vote
        
        return False
    
    @staticmethod
    def _can_access_profile(user, profile_user_id, action):
        """Check profile-specific permissions."""
        if action == 'read':
            return True  # Anyone can read profiles
        
        if action in ['write', 'edit']:
            return user.id == profile_user_id
        
        return False


class ValidationService:
    """Service for input validation and sanitization."""
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format.
        
        Args:
            email (str): Email address
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not email:
            return False, "Email is required"
        
        if len(email) > 255:
            return False, "Email is too long"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, "Valid email"
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength.
        
        Args:
            password (str): Password
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password is too long"
        
        # Check for at least one letter and one number
        if not re.search(r'[a-zA-Z]', password):
            return False, "Password must contain at least one letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Valid password"
    
    @staticmethod
    def validate_name(name):
        """
        Validate user name.
        
        Args:
            name (str): User name
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not name:
            return False, "Name is required"
        
        if len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 100:
            return False, "Name is too long"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, "Name contains invalid characters"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_fact_content(content):
        """
        Validate fact content.
        
        Args:
            content (str): Fact content
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not content:
            return False, "Fact content is required"
        
        content = content.strip()
        if len(content) < 10:
            return False, "Fact content must be at least 10 characters long"
        
        max_length = current_app.config.get('MAX_FACT_LENGTH', 500)
        if len(content) > max_length:
            return False, f"Fact content must be less than {max_length} characters"
        
        return True, "Valid fact content"
    
    @staticmethod
    def validate_comment_content(content):
        """
        Validate comment content.
        
        Args:
            content (str): Comment content
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not content:
            return False, "Comment content is required"
        
        content = content.strip()
        if len(content) < 3:
            return False, "Comment must be at least 3 characters long"
        
        max_length = current_app.config.get('MAX_COMMENT_LENGTH', 250)
        if len(content) > max_length:
            return False, f"Comment must be less than {max_length} characters"
        
        return True, "Valid comment content"
    
    @staticmethod
    def sanitize_html(content):
        """
        Sanitize HTML content to prevent XSS.
        
        Args:
            content (str): HTML content
            
        Returns:
            str: Sanitized content
        """
        if not content:
            return ""
        
        # Escape HTML entities
        sanitized = html.escape(content)
        
        # Remove any remaining script tags or javascript
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_url(url):
        """
        Validate URL format.
        
        Args:
            url (str): URL to validate
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not url:
            return False, "URL is required"
        
        if len(url) > 2000:
            return False, "URL is too long"
        
        # Basic URL pattern
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(pattern, url):
            return False, "Invalid URL format"
        
        return True, "Valid URL"


class AuditService:
    """Service for security and compliance logging."""
    
    @staticmethod
    def log_action(user_id=None, action_type=None, resource_type=None, resource_id=None,
                   old_values=None, new_values=None, success=True, error_message=None,
                   severity='info', ip_address=None, user_agent=None):
        """
        Log an action for audit purposes.
        
        Args:
            user_id (str): User ID performing the action
            action_type (str): Type of action performed
            resource_type (str): Type of resource affected
            resource_id (str): ID of resource affected
            old_values (str): Previous values (JSON string)
            new_values (str): New values (JSON string)
            success (bool): Whether action was successful
            error_message (str): Error message if action failed
            severity (str): Log severity level
            ip_address (str): IP address of user
            user_agent (str): User agent string
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action_type or 'unknown',
                resource_type=resource_type or 'unknown',
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address or (request.remote_addr if request else None),
                user_agent=user_agent or (request.headers.get('User-Agent') if request else None)
            )
            audit_log.save()
            
        except Exception as e:
            current_app.logger.error(f"Audit logging error: {str(e)}")
    
    @staticmethod
    def log_security_event(event_type, user_id=None, details=None, severity='warning'):
        """
        Log a security-related event.
        
        Args:
            event_type (str): Type of security event
            user_id (str): User ID if applicable
            details (str): Event details
            severity (str): Event severity
        """
        AuditService.log_action(
            user_id=user_id,
            action_type=f'security_{event_type}',
            resource_type='security',
            success=False,
            error_message=details,
            severity=severity
        )
    
    @staticmethod
    def get_user_audit_trail(user_id, limit=50):
        """
        Get audit trail for a specific user.
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of records
            
        Returns:
            list: List of audit log entries
        """
        return AuditLog.query.filter_by(
            user_id=user_id,
            is_deleted=False
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_resource_audit_trail(resource_type, resource_id, limit=50):
        """
        Get audit trail for a specific resource.
        
        Args:
            resource_type (str): Type of resource
            resource_id (str): Resource ID
            limit (int): Maximum number of records
            
        Returns:
            list: List of audit log entries
        """
        return AuditLog.query.filter_by(
            resource_type=resource_type,
            resource_id=resource_id,
            is_deleted=False
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
