"""Community interaction models (Comments, Votes, Threads)."""
from datetime import datetime
from app import db
from app.models import BaseModel


class Comment(BaseModel):
    """Comment model for threaded comments."""
    
    __tablename__ = 'comments'
    
    fact_id = db.Column(db.String(36), db.ForeignKey('facts.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    parent_comment_id = db.Column(db.String(36), db.ForeignKey('comments.id'))
    content = db.Column(db.Text, nullable=False)
    nesting_level = db.Column(db.Integer, nullable=False, default=0)
    reply_count = db.Column(db.Integer, nullable=False, default=0)
    edit_count = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side='Comment.id'), cascade='all, delete-orphan')
    edit_history = db.relationship('CommentEditHistory', backref='comment', cascade='all, delete-orphan')
    votes = db.relationship('CommentVote', backref='comment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Comment {self.content[:50]}...>'


class CommentEditHistory(BaseModel):
    """Comment edit history model for audit trail."""
    
    __tablename__ = 'comment_edit_history'
    
    comment_id = db.Column(db.String(36), db.ForeignKey('comments.id'), nullable=False)
    previous_content = db.Column(db.Text, nullable=False)
    edit_reason = db.Column(db.String(500))
    edited_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CommentEditHistory {self.comment_id}>'


class CommentThread(BaseModel):
    """Comment thread model for thread organization."""
    
    __tablename__ = 'comment_threads'
    
    fact_id = db.Column(db.String(36), db.ForeignKey('facts.id'), nullable=False)
    root_comment_id = db.Column(db.String(36), db.ForeignKey('comments.id'), nullable=False)
    total_comments = db.Column(db.Integer, nullable=False, default=1)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('fact_id', 'root_comment_id'),)
    
    def __repr__(self):
        return f'<CommentThread {self.root_comment_id}>'


class FactVote(BaseModel):
    """Fact vote model for Fact/Fake voting."""
    
    __tablename__ = 'fact_votes'
    
    fact_id = db.Column(db.String(36), db.ForeignKey('facts.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'fact' or 'fake'
    
    __table_args__ = (db.UniqueConstraint('fact_id', 'user_id'),)
    
    def __repr__(self):
        return f'<FactVote {self.vote_type}>'


class CommentVote(BaseModel):
    """Comment vote model for Upvote/Downvote voting."""
    
    __tablename__ = 'comment_votes'
    
    comment_id = db.Column(db.String(36), db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    
    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id'),)
    
    def __repr__(self):
        return f'<CommentVote {self.vote_type}>'


class VoteStatistics(BaseModel):
    """Vote statistics model for cached voting statistics."""
    
    __tablename__ = 'vote_statistics'
    
    content_type = db.Column(db.String(10), nullable=False)  # 'fact' or 'comment'
    content_id = db.Column(db.String(36), nullable=False)
    total_votes = db.Column(db.Integer, nullable=False, default=0)
    positive_votes = db.Column(db.Integer, nullable=False, default=0)
    negative_votes = db.Column(db.Integer, nullable=False, default=0)
    vote_score = db.Column(db.Numeric(10, 4), nullable=False, default=0.0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('content_type', 'content_id'),)
    
    def __repr__(self):
        return f'<VoteStatistics {self.content_type}:{self.content_id}>'
