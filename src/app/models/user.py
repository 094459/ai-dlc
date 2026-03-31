"""User-related database models."""
from datetime import datetime
from app import db
from app.models import BaseModel


class User(BaseModel):
    """User account model."""
    
    __tablename__ = 'users'
    
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_moderator = db.Column(db.Boolean, nullable=False, default=False)
    last_login = db.Column(db.DateTime)
    
    # Moderation-related fields
    is_suspended = db.Column(db.Boolean, nullable=False, default=False)
    suspension_expires = db.Column(db.DateTime)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    ban_reason = db.Column(db.Text)
    warning_count = db.Column(db.Integer, nullable=False, default=0)
    last_warning_date = db.Column(db.DateTime)
    content_restriction_level = db.Column(db.Integer, nullable=False, default=0)  # 0=none, 1=limited, 2=restricted
    
    # Notification preference fields
    email_notifications = db.Column(db.Boolean, nullable=False, default=True)
    notification_frequency = db.Column(db.String(20), nullable=False, default='immediate')  # immediate, hourly, daily, weekly
    system_notifications = db.Column(db.Boolean, nullable=False, default=True)
    content_notifications = db.Column(db.Boolean, nullable=False, default=True)
    interaction_notifications = db.Column(db.Boolean, nullable=False, default=True)
    moderation_notifications = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', cascade='all, delete-orphan')
    facts = db.relationship('Fact', backref='author', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', cascade='all, delete-orphan')
    fact_votes = db.relationship('FactVote', backref='user', cascade='all, delete-orphan')
    comment_votes = db.relationship('CommentVote', backref='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def is_authenticated(self):
        """Check if user is authenticated."""
        return True
    
    def is_anonymous(self):
        """Check if user is anonymous."""
        return False
    
    def get_id(self):
        """Get user ID for Flask-Login."""
        return str(self.id)
    
    # Moderation helper methods
    def can_post_content(self):
        """Check if user can post new content."""
        if self.is_banned or not self.is_active:
            return False
        if self.is_suspended and self.suspension_expires and datetime.utcnow() < self.suspension_expires:
            return False
        return self.content_restriction_level < 2
    
    def can_comment(self):
        """Check if user can post comments."""
        if self.is_banned or not self.is_active:
            return False
        if self.is_suspended and self.suspension_expires and datetime.utcnow() < self.suspension_expires:
            return False
        return self.content_restriction_level < 1
    
    def can_vote(self):
        """Check if user can vote on content."""
        if self.is_banned or not self.is_active:
            return False
        if self.is_suspended and self.suspension_expires and datetime.utcnow() < self.suspension_expires:
            return False
        return True
    
    def get_moderation_status(self):
        """Get current moderation status."""
        if self.is_banned:
            return 'banned'
        if self.is_suspended and self.suspension_expires and datetime.utcnow() < self.suspension_expires:
            return 'suspended'
        if self.content_restriction_level > 0:
            return 'restricted'
        return 'active'
    
    def clear_suspension(self):
        """Clear user suspension."""
        self.is_suspended = False
        self.suspension_expires = None
    
    def increment_warning_count(self):
        """Increment warning count and update last warning date."""
        self.warning_count += 1
        self.last_warning_date = datetime.utcnow()
    
    @property
    def role(self):
        """Get user role based on admin and moderator flags."""
        if self.is_admin:
            return 'admin'
        elif self.is_moderator:
            return 'moderator'
        else:
            return 'user'


class UserSession(BaseModel):
    """User session model for session management."""
    
    __tablename__ = 'user_sessions'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    def __repr__(self):
        return f'<UserSession {self.session_token[:8]}...>'
    
    def is_expired(self):
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at


class UserProfile(BaseModel):
    """User profile model."""
    
    __tablename__ = 'user_profiles'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.Text)
    profile_photo_url = db.Column(db.String(500))
    
    # Relationships
    photos = db.relationship('ProfilePhoto', backref='user_profile', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UserProfile {self.name}>'


class ProfilePhoto(BaseModel):
    """Profile photo model."""
    
    __tablename__ = 'profile_photos'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    profile_id = db.Column(db.String(36), db.ForeignKey('user_profiles.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProfilePhoto {self.filename}>'
