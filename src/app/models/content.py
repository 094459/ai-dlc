"""Content-related database models (Facts, Resources, Hashtags)."""
from datetime import datetime
from app import db
from app.models import BaseModel


class Fact(BaseModel):
    """Fact model for user-submitted facts."""
    
    __tablename__ = 'facts'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    edit_count = db.Column(db.Integer, nullable=False, default=0)
    last_edited_at = db.Column(db.DateTime)
    
    # Relationships
    edit_history = db.relationship('FactEditHistory', backref='fact', cascade='all, delete-orphan')
    resources = db.relationship('FactResource', backref='fact', cascade='all, delete-orphan')
    hashtags = db.relationship('FactHashtag', backref='fact', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='fact', cascade='all, delete-orphan')
    votes = db.relationship('FactVote', backref='fact', cascade='all, delete-orphan')
    threads = db.relationship('CommentThread', backref='fact', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Fact {self.content[:50]}...>'


class FactEditHistory(BaseModel):
    """Fact edit history model for audit trail."""
    
    __tablename__ = 'fact_edit_history'
    
    fact_id = db.Column(db.String(36), db.ForeignKey('facts.id'), nullable=False)
    previous_content = db.Column(db.Text, nullable=False)
    edit_reason = db.Column(db.String(500))
    edited_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FactEditHistory {self.fact_id}>'


class Hashtag(BaseModel):
    """Hashtag model."""
    
    __tablename__ = 'hashtags'
    
    tag = db.Column(db.String(100), nullable=False, unique=True)
    usage_count = db.Column(db.Integer, nullable=False, default=0)
    first_used_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    facts = db.relationship('FactHashtag', backref='hashtag', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Hashtag #{self.tag}>'


class FactHashtag(BaseModel):
    """Junction table for fact-hashtag many-to-many relationship."""
    
    __tablename__ = 'fact_hashtags'
    
    fact_id = db.Column(db.String(36), db.ForeignKey('facts.id'), nullable=False)
    hashtag_id = db.Column(db.String(36), db.ForeignKey('hashtags.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('fact_id', 'hashtag_id'),)
    
    def __repr__(self):
        return f'<FactHashtag {self.fact_id}-{self.hashtag_id}>'


class FactResource(BaseModel):
    """Fact resource model for URLs and images."""
    
    __tablename__ = 'fact_resources'
    
    fact_id = db.Column(db.String(36), db.ForeignKey('facts.id'), nullable=False)
    resource_type = db.Column(db.String(10), nullable=False)  # 'url' or 'image'
    resource_value = db.Column(db.String(2000), nullable=False)
    display_title = db.Column(db.String(200))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    validation = db.relationship('ResourceValidation', backref='resource', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FactResource {self.resource_type}: {self.resource_value[:50]}...>'


class ResourceValidation(BaseModel):
    """Resource validation model for tracking resource health."""
    
    __tablename__ = 'resource_validation'
    
    resource_id = db.Column(db.String(36), db.ForeignKey('fact_resources.id'), nullable=False)
    validation_status = db.Column(db.String(20), nullable=False)  # 'pending', 'valid', 'invalid', 'broken'
    validation_message = db.Column(db.Text)
    last_checked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_count = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<ResourceValidation {self.validation_status}>'
