"""
System models for reporting, moderation, notifications, analytics, and configuration.
"""

from app.models import db, BaseModel
from datetime import datetime, timedelta


class ReportCategory(BaseModel):
    """Report category model for categorizing different types of reports."""
    
    __tablename__ = 'report_categories'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    severity_level = db.Column(db.Integer, nullable=False, default=1)  # 1-5 scale
    auto_escalate = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    reports = db.relationship('Report', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ReportCategory {self.name}>'


class Report(BaseModel):
    """Report model for user-submitted content reports."""
    
    __tablename__ = 'reports'
    
    reporter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    reported_content_type = db.Column(db.String(20), nullable=False)  # 'fact' or 'comment'
    reported_content_id = db.Column(db.String(36), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('report_categories.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, assigned, reviewed, resolved, dismissed
    priority = db.Column(db.String(10), nullable=False, default='medium')  # low, medium, high, urgent
    moderator_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    resolution_notes = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    
    # Additional metadata
    reporter_ip = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.String(500))
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='submitted_reports')
    moderator = db.relationship('User', foreign_keys=[moderator_id], backref='assigned_reports')
    actions = db.relationship('ReportAction', backref='report', cascade='all, delete-orphan')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_report_content', 'reported_content_type', 'reported_content_id'),
        db.Index('idx_report_status', 'status'),
        db.Index('idx_report_priority', 'priority'),
        db.Index('idx_report_moderator', 'moderator_id'),
    )
    
    def __repr__(self):
        return f'<Report {self.reported_content_type}:{self.reported_content_id} by {self.reporter_id}>'
    
    @property
    def is_pending(self):
        """Check if report is still pending."""
        return self.status == 'pending'
    
    @property
    def is_resolved(self):
        """Check if report has been resolved."""
        return self.status in ['resolved', 'dismissed']
    
    @property
    def age_in_hours(self):
        """Get report age in hours."""
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    def get_reported_content(self):
        """Get the actual reported content object."""
        if self.reported_content_type == 'fact':
            from app.models.content import Fact
            return db.session.get(Fact, self.reported_content_id)
        elif self.reported_content_type == 'comment':
            from app.models.community import Comment
            return db.session.get(Comment, self.reported_content_id)
        return None


class ReportAction(BaseModel):
    """Report action model for tracking moderation actions on reports."""
    
    __tablename__ = 'report_actions'
    
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'), nullable=False)
    moderator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # assigned, reviewed, content_removed, user_warned, resolved, dismissed
    notes = db.Column(db.Text)
    previous_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    
    # Additional context
    action_data = db.Column(db.JSON)  # Store additional action-specific data
    
    # Relationships
    moderator = db.relationship('User', backref='report_actions')
    
    def __repr__(self):
        return f'<ReportAction {self.action_type} on {self.report_id} by {self.moderator_id}>'


class ModerationAction(BaseModel):
    """Enhanced moderation action model for tracking all moderation actions."""
    
    __tablename__ = 'moderation_actions'
    
    moderator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(30), nullable=False)
    target_type = db.Column(db.String(10), nullable=False)  # 'fact', 'comment', 'user', 'report'
    target_id = db.Column(db.String(36), nullable=False)
    related_report_id = db.Column(db.String(36), db.ForeignKey('reports.id'))
    reason = db.Column(db.Text, nullable=False)
    duration_hours = db.Column(db.Integer)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Enhanced fields for Phase 5.2
    action_category = db.Column(db.String(20), nullable=False, default='content')  # content, user, system
    severity_level = db.Column(db.Integer, nullable=False, default=1)  # 1-5 scale
    automated = db.Column(db.Boolean, nullable=False, default=False)
    workflow_id = db.Column(db.String(36), db.ForeignKey('moderation_workflows.id'))
    appeal_deadline = db.Column(db.DateTime)
    appealed = db.Column(db.Boolean, nullable=False, default=False)
    appeal_notes = db.Column(db.Text)
    
    # Relationships
    moderator = db.relationship('User', backref='moderation_actions_performed')
    related_report = db.relationship('Report', backref='moderation_actions')
    workflow = db.relationship('ModerationWorkflow', backref='executed_actions')
    
    def __repr__(self):
        return f'<ModerationAction {self.action_type} on {self.target_type}>'
    
    @property
    def is_expired(self):
        """Check if the moderation action has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def time_remaining(self):
        """Get remaining time for temporary actions."""
        if not self.expires_at:
            return None
        remaining = self.expires_at - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else None


class UserModerationHistory(BaseModel):
    """User moderation history model for tracking user violations and actions."""
    
    __tablename__ = 'user_moderation_history'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(30), nullable=False)  # warning, suspension, ban, restriction
    moderator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    severity_level = db.Column(db.Integer, nullable=False, default=1)  # 1-5 scale
    duration_hours = db.Column(db.Integer)  # For temporary actions
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Related content information
    related_content_type = db.Column(db.String(20))  # fact, comment
    related_content_id = db.Column(db.String(36))
    related_report_id = db.Column(db.String(36), db.ForeignKey('reports.id'))
    
    # Appeal information
    appeal_submitted = db.Column(db.Boolean, nullable=False, default=False)
    appeal_reason = db.Column(db.Text)
    appeal_status = db.Column(db.String(20), default='none')  # none, pending, approved, denied
    appeal_reviewed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    appeal_reviewed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='moderation_history')
    moderator = db.relationship('User', foreign_keys=[moderator_id], backref='moderation_actions_taken')
    appeal_reviewer = db.relationship('User', foreign_keys=[appeal_reviewed_by])
    related_report = db.relationship('Report', backref='user_moderation_actions')
    
    def __repr__(self):
        return f'<UserModerationHistory {self.action_type} for {self.user_id}>'
    
    @property
    def is_expired(self):
        """Check if the moderation action has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def can_appeal(self):
        """Check if the user can still appeal this action."""
        if self.appeal_submitted:
            return False
        if not self.is_active:
            return False
        # Allow appeals within 30 days of action
        appeal_deadline = self.created_at + timedelta(days=30)
        return datetime.utcnow() < appeal_deadline


class ModerationWorkflow(BaseModel):
    """Moderation workflow model for automated moderation rules."""
    
    __tablename__ = 'moderation_workflows'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    trigger_type = db.Column(db.String(30), nullable=False)  # report_count, flag_threshold, user_history
    trigger_conditions = db.Column(db.JSON, nullable=False)  # Conditions for activation
    actions = db.Column(db.JSON, nullable=False)  # Actions to take when triggered
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.Integer, nullable=False, default=1)  # Higher number = higher priority
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Execution statistics
    execution_count = db.Column(db.Integer, nullable=False, default=0)
    last_executed = db.Column(db.DateTime)
    success_rate = db.Column(db.Float, default=0.0)  # Percentage of successful executions
    
    # Relationships
    creator = db.relationship('User', backref='created_workflows')
    
    def __repr__(self):
        return f'<ModerationWorkflow {self.name}>'
    
    def increment_execution(self, success=True):
        """Increment execution count and update success rate."""
        self.execution_count += 1
        self.last_executed = datetime.utcnow()
        
        if success:
            # Calculate new success rate
            if self.execution_count == 1:
                self.success_rate = 100.0
            else:
                current_successes = (self.success_rate / 100.0) * (self.execution_count - 1)
                new_successes = current_successes + 1
                self.success_rate = (new_successes / self.execution_count) * 100.0
        else:
            # Recalculate success rate with failure
            if self.execution_count == 1:
                self.success_rate = 0.0
            else:
                current_successes = (self.success_rate / 100.0) * (self.execution_count - 1)
                self.success_rate = (current_successes / self.execution_count) * 100.0


class Notification(BaseModel):
    """Enhanced notification model for user notifications."""
    
    __tablename__ = 'notifications'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Keeping for backward compatibility
    notification_type = db.Column(db.String(50), nullable=False, default='system')  # system, content, interaction, moderation
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime)
    
    # Enhanced fields for Phase 6.1
    priority = db.Column(db.String(20), nullable=False, default='normal')  # low, normal, high, urgent
    template_id = db.Column(db.String(36), db.ForeignKey('notification_templates.id'))
    data = db.Column(db.JSON)  # Template variables and additional data
    delivery_method = db.Column(db.String(20), nullable=False, default='in_app')  # in_app, email, both
    scheduled_for = db.Column(db.DateTime)  # For scheduled notifications
    delivered_at = db.Column(db.DateTime)
    delivery_status = db.Column(db.String(20), default='pending')  # pending, delivered, failed, cancelled
    retry_count = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime)
    
    # Optional related content
    related_content_type = db.Column(db.String(20))
    related_content_id = db.Column(db.String(36))
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    template = db.relationship('NotificationTemplate', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.notification_type} for {self.user_id}>'
    
    @property
    def is_expired(self):
        """Check if the notification has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_scheduled(self):
        """Check if the notification is scheduled for future delivery."""
        if not self.scheduled_for:
            return False
        return datetime.utcnow() < self.scheduled_for
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def get_priority_level(self):
        """Get numeric priority level for sorting."""
        priority_levels = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
        return priority_levels.get(self.priority, 2)


class NotificationTemplate(BaseModel):
    """Notification template model for customizable notification templates."""
    
    __tablename__ = 'notification_templates'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    notification_type = db.Column(db.String(50), nullable=False)
    subject_template = db.Column(db.String(200), nullable=False)
    body_template = db.Column(db.Text, nullable=False)
    html_template = db.Column(db.Text)  # For rich HTML emails
    variables = db.Column(db.JSON)  # Available template variables
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Usage statistics
    usage_count = db.Column(db.Integer, nullable=False, default=0)
    last_used = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', backref='created_templates')
    
    def __repr__(self):
        return f'<NotificationTemplate {self.name}>'
    
    def render_subject(self, variables):
        """Render subject template with variables."""
        from jinja2 import Template
        template = Template(self.subject_template)
        return template.render(**variables)
    
    def render_body(self, variables):
        """Render body template with variables."""
        from jinja2 import Template
        template = Template(self.body_template)
        return template.render(**variables)
    
    def render_html(self, variables):
        """Render HTML template with variables."""
        if not self.html_template:
            return None
        from jinja2 import Template
        template = Template(self.html_template)
        return template.render(**variables)
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()


class NotificationQueue(BaseModel):
    """Notification queue model for email delivery management."""
    
    __tablename__ = 'notification_queue'
    
    notification_id = db.Column(db.String(36), db.ForeignKey('notifications.id'), nullable=False)
    email_address = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body_text = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)
    priority = db.Column(db.Integer, nullable=False, default=1)  # 1=low, 2=normal, 3=high, 4=urgent
    scheduled_for = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    max_attempts = db.Column(db.Integer, nullable=False, default=3)
    status = db.Column(db.String(20), nullable=False, default='queued')  # queued, sending, sent, failed
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Relationships
    notification = db.relationship('Notification', backref='email_queue')
    
    def __repr__(self):
        return f'<NotificationQueue {self.email_address} - {self.status}>'
    
    @property
    def can_retry(self):
        """Check if email can be retried."""
        return self.status == 'failed' and self.attempts < self.max_attempts
    
    @property
    def is_ready_to_send(self):
        """Check if email is ready to be sent."""
        return (self.status == 'queued' and 
                datetime.utcnow() >= self.scheduled_for and
                self.attempts < self.max_attempts)
    
    def mark_as_sent(self):
        """Mark email as successfully sent."""
        self.status = 'sent'
        self.sent_at = datetime.utcnow()
    
    def mark_as_failed(self, error_message):
        """Mark email as failed with error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.attempts += 1
    
    def increment_attempt(self):
        """Increment attempt count."""
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.status = 'failed'


class UserNotificationPreferences(BaseModel):
    """User notification preferences model."""
    
    __tablename__ = 'user_notification_preferences'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    email_notifications = db.Column(db.Boolean, nullable=False, default=True)
    comment_notifications = db.Column(db.Boolean, nullable=False, default=True)
    vote_notifications = db.Column(db.Boolean, nullable=False, default=False)
    moderation_notifications = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    user = db.relationship('User', backref='notification_preferences', uselist=False)
    
    def __repr__(self):
        return f'<NotificationPreferences for {self.user_id}>'


class AnalyticsEvent(BaseModel):
    """Analytics event model for tracking user interactions."""
    
    __tablename__ = 'analytics_events'
    
    # Event identification
    event_type = db.Column(db.String(50), nullable=False)  # login, logout, fact_created, vote_cast, etc.
    event_category = db.Column(db.String(30), nullable=False)  # user, content, interaction, system
    
    # User and session info
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # Null for anonymous events
    session_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    
    # Event data
    resource_type = db.Column(db.String(50), nullable=True)  # fact, comment, user, etc.
    resource_id = db.Column(db.String(36), nullable=True)
    event_data = db.Column(db.JSON, nullable=True)  # Additional event-specific data
    
    # Metrics
    duration_ms = db.Column(db.Integer, nullable=True)  # For timing events
    value = db.Column(db.Float, nullable=True)  # For numeric metrics
    
    # Context
    referrer = db.Column(db.String(500), nullable=True)
    page_url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='analytics_events')
    
    def __repr__(self):
        return f'<AnalyticsEvent {self.event_type}:{self.event_category}>'


class AuditLog(BaseModel):
    """Audit log model for security and compliance tracking."""
    
    __tablename__ = 'audit_logs'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(36))
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.resource_type}>'


class SystemConfiguration(BaseModel):
    """System configuration model for application settings."""
    
    __tablename__ = 'system_configurations'
    
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)
    data_type = db.Column(db.String(20), nullable=False, default='string')  # string, integer, boolean, json
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f'<SystemConfiguration {self.key}>'
    
    def get_typed_value(self):
        """Get the value converted to its proper type."""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class ReportStatistics(BaseModel):
    """Report statistics model for tracking reporting trends and metrics."""
    
    __tablename__ = 'report_statistics'
    
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('report_categories.id'), nullable=False)
    total_reports = db.Column(db.Integer, nullable=False, default=0)
    resolved_reports = db.Column(db.Integer, nullable=False, default=0)
    dismissed_reports = db.Column(db.Integer, nullable=False, default=0)
    average_resolution_time = db.Column(db.Float)  # in hours
    
    # Relationships
    category = db.relationship('ReportCategory', backref='daily_statistics')
    
    # Unique constraint to prevent duplicate entries
    __table_args__ = (
        db.UniqueConstraint('date', 'category_id', name='unique_daily_category_stats'),
    )
    
    def __repr__(self):
        return f'<ReportStatistics {self.date} {self.category.name if self.category else "Unknown"}>'
