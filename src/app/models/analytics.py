"""
Analytics models for tracking metrics and dashboard configuration.
"""

from datetime import datetime
from app.models import db, BaseModel
from sqlalchemy import Index


class MetricsAggregation(BaseModel):
    """Model for storing aggregated metrics data."""
    
    __tablename__ = 'metrics_aggregations'
    
    # Aggregation identification
    metric_name = db.Column(db.String(100), nullable=False)  # daily_active_users, fact_creation_rate, etc.
    aggregation_type = db.Column(db.String(20), nullable=False)  # hourly, daily, weekly, monthly
    aggregation_date = db.Column(db.Date, nullable=False)
    
    # Metric values
    count_value = db.Column(db.Integer, nullable=True)
    sum_value = db.Column(db.Float, nullable=True)
    avg_value = db.Column(db.Float, nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    
    # Additional data
    extra_data = db.Column(db.JSON, nullable=True)  # Breakdown by category, etc.
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_name_type_date', 'metric_name', 'aggregation_type', 'aggregation_date'),
        db.UniqueConstraint('metric_name', 'aggregation_type', 'aggregation_date', 
                           name='uq_metrics_aggregation'),
    )
    
    def __repr__(self):
        return f'<MetricsAggregation {self.metric_name}:{self.aggregation_type}>'


class DashboardConfiguration(BaseModel):
    """Model for storing dashboard configuration and widgets."""
    
    __tablename__ = 'dashboard_configurations'
    
    # Configuration identification
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    dashboard_type = db.Column(db.String(30), nullable=False)  # admin, moderator, user
    
    # Configuration data
    widget_config = db.Column(db.JSON, nullable=False)  # Widget layout and settings
    filters = db.Column(db.JSON, nullable=True)  # Default filters
    refresh_interval = db.Column(db.Integer, nullable=False, default=300)  # Seconds
    
    # Access control
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Usage tracking
    view_count = db.Column(db.Integer, nullable=False, default=0)
    last_viewed = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref='dashboard_configurations')
    
    def __repr__(self):
        return f'<DashboardConfiguration {self.name}>'
    
    def increment_view_count(self):
        """Increment view count and update last viewed timestamp."""
        self.view_count += 1
        self.last_viewed = datetime.utcnow()


class UserEngagementMetrics(BaseModel):
    """Model for storing user engagement metrics."""
    
    __tablename__ = 'user_engagement_metrics'
    
    # User identification
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    metric_date = db.Column(db.Date, nullable=False)
    
    # Engagement metrics
    session_count = db.Column(db.Integer, nullable=False, default=0)
    total_session_duration = db.Column(db.Integer, nullable=False, default=0)  # Seconds
    page_views = db.Column(db.Integer, nullable=False, default=0)
    
    # Content interaction
    facts_created = db.Column(db.Integer, nullable=False, default=0)
    comments_created = db.Column(db.Integer, nullable=False, default=0)
    votes_cast = db.Column(db.Integer, nullable=False, default=0)
    
    # Social interaction
    profile_views = db.Column(db.Integer, nullable=False, default=0)
    followers_gained = db.Column(db.Integer, nullable=False, default=0)
    
    # Moderation activity (for moderators)
    reports_handled = db.Column(db.Integer, nullable=False, default=0)
    moderation_actions = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    user = db.relationship('User', backref='engagement_metrics')
    
    # Indexes
    __table_args__ = (
        Index('idx_user_engagement_user_date', 'user_id', 'metric_date'),
        db.UniqueConstraint('user_id', 'metric_date', name='uq_user_engagement_date'),
    )
    
    def __repr__(self):
        return f'<UserEngagementMetrics {self.user_id}:{self.metric_date}>'
    
    @property
    def avg_session_duration(self):
        """Calculate average session duration in seconds."""
        if self.session_count == 0:
            return 0
        return self.total_session_duration / self.session_count
    
    @property
    def engagement_score(self):
        """Calculate a simple engagement score."""
        # Simple scoring algorithm - can be refined
        score = (
            self.facts_created * 10 +
            self.comments_created * 5 +
            self.votes_cast * 2 +
            self.session_count * 3 +
            min(self.total_session_duration / 60, 120)  # Cap at 2 hours
        )
        return round(score, 2)
