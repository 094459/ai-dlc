"""
Database models for the Fact Checker application.
Contains all SQLAlchemy models based on the complete schema.
"""
import uuid
from datetime import datetime
from app import db


class BaseModel(db.Model):
    """Base model class with common fields and methods."""
    
    __abstract__ = True
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime)
    
    def save(self):
        """Save the model to the database."""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Soft delete the model."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def hard_delete(self):
        """Hard delete the model from the database."""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserSession, UserProfile, ProfilePhoto
from .content import Fact, FactEditHistory, Hashtag, FactHashtag, FactResource, ResourceValidation
from .community import Comment, CommentEditHistory, CommentThread, FactVote, CommentVote, VoteStatistics
from .system import (
    ReportCategory, Report, ReportAction, ReportStatistics, 
    ModerationAction, UserModerationHistory, ModerationWorkflow,
    Notification, NotificationTemplate, NotificationQueue, UserNotificationPreferences, 
    AnalyticsEvent, AuditLog, SystemConfiguration
)
from .analytics import (
    MetricsAggregation, DashboardConfiguration, UserEngagementMetrics
)
from .admin import (
    AdminActivity, SystemHealth, AdminDashboardWidget, SystemMaintenanceWindow
)

__all__ = [
    'BaseModel',
    'User', 'UserSession', 'UserProfile', 'ProfilePhoto',
    'Fact', 'FactEditHistory', 'Hashtag', 'FactHashtag', 'FactResource', 'ResourceValidation',
    'Comment', 'CommentEditHistory', 'CommentThread', 'FactVote', 'CommentVote', 'VoteStatistics',
    'ReportCategory', 'Report', 'ReportAction', 'ReportStatistics', 
    'ModerationAction', 'UserModerationHistory', 'ModerationWorkflow',
    'Notification', 'NotificationTemplate', 'NotificationQueue', 'UserNotificationPreferences', 
    'AnalyticsEvent', 'AuditLog', 'SystemConfiguration',
    'MetricsAggregation', 'DashboardConfiguration', 'UserEngagementMetrics',
    'AdminActivity', 'SystemHealth', 'AdminDashboardWidget', 'SystemMaintenanceWindow'
]
