"""
Authentication services for user registration, login, and session management.
"""
import uuid
import bcrypt
from datetime import datetime, timedelta
from flask import current_app, request, session
from app import db
from app.models import User, UserSession, UserProfile
from app.components.security.services import AuditService


class AuthenticationService:
    """Service for user authentication operations."""
    
    @staticmethod
    def register_user(email, password, name):
        """
        Register a new user with email validation.
        
        Args:
            email (str): User email address
            password (str): Plain text password
            name (str): User's display name
            
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        try:
            # Validate email format
            if not AuthenticationService._is_valid_email(email):
                return False, "Invalid email format", None
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email.lower()).first()
            if existing_user:
                return False, "Email already registered", None
            
            # Validate password strength
            if not AuthenticationService._is_valid_password(password):
                return False, "Password must be at least 8 characters long", None
            
            # Hash password
            password_hash = AuthenticationService._hash_password(password)
            
            # Create user
            user = User(
                email=email.lower(),
                password_hash=password_hash,
                is_active=True
            )
            user.save()
            
            # Create user profile
            profile = UserProfile(
                user_id=user.id,
                name=name
            )
            profile.save()
            
            # Log registration
            AuditService.log_action(
                user_id=user.id,
                action_type='user_registration',
                resource_type='user',
                resource_id=user.id,
                success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return True, "User registered successfully", user
            
        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            return False, "Registration failed. Please try again.", None
    
    @staticmethod
    def login_user(email, password, remember_me=False):
        """
        Authenticate user login.
        
        Args:
            email (str): User email address
            password (str): Plain text password
            remember_me (bool): Whether to create long-lived session
            
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        try:
            # Find user by email
            user = User.query.filter_by(email=email.lower()).first()
            
            if not user:
                AuditService.log_action(
                    action_type='login_attempt',
                    resource_type='user',
                    success=False,
                    error_message='User not found',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                return False, "Invalid email or password", None
            
            # Check if user is active
            if not user.is_active:
                AuditService.log_action(
                    user_id=user.id,
                    action_type='login_attempt',
                    resource_type='user',
                    resource_id=user.id,
                    success=False,
                    error_message='User account inactive',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                return False, "Account is inactive", None
            
            # Verify password
            if not AuthenticationService._verify_password(password, user.password_hash):
                AuditService.log_action(
                    user_id=user.id,
                    action_type='login_attempt',
                    resource_type='user',
                    resource_id=user.id,
                    success=False,
                    error_message='Invalid password',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                return False, "Invalid email or password", None
            
            # Update last login
            user.last_login = datetime.utcnow()
            user.save()
            
            # Create session
            session_token = AuthenticationService._create_session(user, remember_me)
            
            # Log successful login
            AuditService.log_action(
                user_id=user.id,
                action_type='login_success',
                resource_type='user',
                resource_id=user.id,
                success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return True, "Login successful", user
            
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return False, "Login failed. Please try again.", None
    
    @staticmethod
    def logout_user(user_id):
        """
        Logout user and invalidate session.
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: Success status
        """
        try:
            # Get session token from Flask session
            session_token = session.get('session_token')
            
            if session_token:
                # Invalidate session in database
                user_session = UserSession.query.filter_by(
                    session_token=session_token,
                    user_id=user_id
                ).first()
                
                if user_session:
                    user_session.delete()
            
            # Clear Flask session
            session.clear()
            
            # Log logout
            AuditService.log_action(
                user_id=user_id,
                action_type='logout',
                resource_type='user',
                resource_id=user_id,
                success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Logout error: {str(e)}")
            return False
    
    @staticmethod
    def _create_session(user, remember_me=False):
        """
        Create user session.
        
        Args:
            user (User): User object
            remember_me (bool): Whether to create long-lived session
            
        Returns:
            str: Session token
        """
        # Generate session token
        session_token = str(uuid.uuid4())
        
        # Set expiration
        if remember_me:
            expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            expires_at = datetime.utcnow() + timedelta(hours=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600) // 3600)
        
        # Create session record
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        user_session.save()
        
        # Store in Flask session
        session['user_id'] = user.id
        session['session_token'] = session_token
        session.permanent = remember_me
        
        return session_token
    
    @staticmethod
    def _hash_password(password):
        """Hash password using bcrypt."""
        rounds = current_app.config.get('BCRYPT_LOG_ROUNDS', 12)
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=rounds)).decode('utf-8')
    
    @staticmethod
    def _verify_password(password, password_hash):
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def _is_valid_email(email):
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def _is_valid_password(password):
        """Basic password validation."""
        return len(password) >= 8


class SessionValidationService:
    """Service for session validation and management."""
    
    @staticmethod
    def get_current_user():
        """
        Get current authenticated user from session.
        
        Returns:
            User or None: Current user if authenticated
        """
        try:
            user_id = session.get('user_id')
            session_token = session.get('session_token')
            
            if not user_id or not session_token:
                return None
            
            # Validate session in database
            user_session = UserSession.query.filter_by(
                user_id=user_id,
                session_token=session_token,
                is_deleted=False
            ).first()
            
            if not user_session:
                session.clear()
                return None
            
            # Check if session is expired
            if user_session.is_expired():
                user_session.delete()
                session.clear()
                return None
            
            # Get user
            user = User.query.filter_by(id=user_id, is_active=True, is_deleted=False).first()
            
            if not user:
                user_session.delete()
                session.clear()
                return None
            
            return user
            
        except Exception as e:
            current_app.logger.error(f"Session validation error: {str(e)}")
            session.clear()
            return None
    
    @staticmethod
    def is_authenticated():
        """Check if current user is authenticated."""
        return SessionValidationService.get_current_user() is not None
    
    @staticmethod
    def require_authentication():
        """Decorator to require authentication for routes."""
        from functools import wraps
        from flask import redirect, url_for, flash, request, jsonify
        
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not SessionValidationService.is_authenticated():
                    # Handle JSON/AJAX requests differently
                    if request.is_json or request.headers.get('Content-Type') == 'application/json':
                        return jsonify({'success': False, 'message': 'Authentication required'}), 401
                    else:
                        flash('Please log in to access this page.', 'warning')
                        return redirect(url_for('auth.login'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def require_admin():
        """Decorator to require admin privileges."""
        from functools import wraps
        from flask import redirect, url_for, flash, abort
        
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = SessionValidationService.get_current_user()
                if not user:
                    flash('Please log in to access this page.', 'warning')
                    return redirect(url_for('auth.login'))
                if not user.is_admin:
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def require_moderator():
        """Decorator to require moderator privileges."""
        from functools import wraps
        from flask import redirect, url_for, flash, abort
        
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = SessionValidationService.get_current_user()
                if not user:
                    flash('Please log in to access this page.', 'warning')
                    return redirect(url_for('auth.login'))
                if not (user.is_admin or user.is_moderator):
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator
