"""
Admin dashboard models for system management and monitoring.
"""

from datetime import datetime, timedelta
from app.models import db, BaseModel
from sqlalchemy import Index, CheckConstraint


class AdminActivity(BaseModel):
    """Model for tracking administrative activities and actions."""
    
    __tablename__ = 'admin_activities'
    
    # Activity identification
    admin_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    activity_type = db.Column(db.String(50), nullable=False)  # config_change, user_action, system_action
    action = db.Column(db.String(100), nullable=False)  # specific action taken
    
    # Target information
    target_type = db.Column(db.String(50), nullable=True)  # user, fact, comment, system, etc.
    target_id = db.Column(db.String(36), nullable=True)
    
    # Activity details
    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON, nullable=True)  # Additional structured data
    
    # Context information
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    
    # Impact assessment
    severity = db.Column(db.String(20), nullable=False, default='low')  # low, medium, high, critical
    impact_scope = db.Column(db.String(30), nullable=False, default='single')  # single, multiple, system-wide
    
    # Relationships
    admin = db.relationship('User', backref='admin_activities')
    
    # Indexes
    __table_args__ = (
        Index('idx_admin_activity_admin_created', 'admin_id', 'created_at'),
        Index('idx_admin_activity_type_action', 'activity_type', 'action'),
        Index('idx_admin_activity_target', 'target_type', 'target_id'),
        Index('idx_admin_activity_severity', 'severity'),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name='ck_admin_activity_severity'
        ),
        CheckConstraint(
            "impact_scope IN ('single', 'multiple', 'system-wide')",
            name='ck_admin_activity_impact_scope'
        ),
    )
    
    def __repr__(self):
        return f'<AdminActivity {self.action} by {self.admin_id}>'


class SystemHealth(BaseModel):
    """Model for storing system health metrics and status information."""
    
    __tablename__ = 'system_health'
    
    # Health check identification
    check_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # database, cache, external_api, etc.
    
    # Health status
    status = db.Column(db.String(20), nullable=False)  # healthy, warning, critical, unknown
    response_time_ms = db.Column(db.Integer, nullable=True)
    
    # Health details
    message = db.Column(db.Text, nullable=True)
    details = db.Column(db.JSON, nullable=True)  # Structured health data
    error_message = db.Column(db.Text, nullable=True)
    
    # Metrics
    cpu_usage = db.Column(db.Float, nullable=True)  # Percentage
    memory_usage = db.Column(db.Float, nullable=True)  # Percentage
    disk_usage = db.Column(db.Float, nullable=True)  # Percentage
    
    # Thresholds
    warning_threshold = db.Column(db.Float, nullable=True)
    critical_threshold = db.Column(db.Float, nullable=True)
    
    # Check metadata
    check_interval = db.Column(db.Integer, nullable=False, default=300)  # Seconds
    last_check_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    next_check_at = db.Column(db.DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_system_health_category_status', 'category', 'status'),
        Index('idx_system_health_last_check', 'last_check_at'),
        Index('idx_system_health_next_check', 'next_check_at'),
        CheckConstraint(
            "status IN ('healthy', 'warning', 'critical', 'unknown')",
            name='ck_system_health_status'
        ),
    )
    
    def __repr__(self):
        return f'<SystemHealth {self.check_name}:{self.status}>'
    
    @property
    def is_overdue(self):
        """Check if the health check is overdue."""
        if not self.next_check_at:
            return False
        return datetime.utcnow() > self.next_check_at
    
    def update_next_check(self):
        """Update the next check time based on interval."""
        self.next_check_at = datetime.utcnow() + timedelta(seconds=self.check_interval)


class AdminDashboardWidget(BaseModel):
    """Model for storing admin dashboard widget configurations."""
    
    __tablename__ = 'admin_dashboard_widgets'
    
    # Widget identification
    widget_id = db.Column(db.String(50), nullable=False)  # Unique widget identifier
    widget_type = db.Column(db.String(30), nullable=False)  # metric, chart, table, alert, etc.
    title = db.Column(db.String(100), nullable=False)
    
    # Widget configuration
    config = db.Column(db.JSON, nullable=False)  # Widget-specific configuration
    data_source = db.Column(db.String(100), nullable=False)  # Data source identifier
    refresh_interval = db.Column(db.Integer, nullable=False, default=300)  # Seconds
    
    # Layout and display
    position_x = db.Column(db.Integer, nullable=False, default=0)
    position_y = db.Column(db.Integer, nullable=False, default=0)
    width = db.Column(db.Integer, nullable=False, default=4)  # Grid columns
    height = db.Column(db.Integer, nullable=False, default=3)  # Grid rows
    
    # Widget properties
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    requires_permission = db.Column(db.String(50), nullable=True)  # Required permission to view
    
    # Customization
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    is_system_widget = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_widgets')
    
    # Indexes
    __table_args__ = (
        Index('idx_admin_widget_type_enabled', 'widget_type', 'is_enabled'),
        Index('idx_admin_widget_position', 'position_x', 'position_y'),
        db.UniqueConstraint('widget_id', name='uq_admin_widget_id'),
    )
    
    def __repr__(self):
        return f'<AdminDashboardWidget {self.widget_id}:{self.title}>'


class SystemMaintenanceWindow(BaseModel):
    """Model for scheduling and tracking system maintenance windows."""
    
    __tablename__ = 'system_maintenance_windows'
    
    # Maintenance identification
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    maintenance_type = db.Column(db.String(30), nullable=False)  # scheduled, emergency, routine
    
    # Scheduling
    scheduled_start = db.Column(db.DateTime, nullable=False)
    scheduled_end = db.Column(db.DateTime, nullable=False)
    actual_start = db.Column(db.DateTime, nullable=True)
    actual_end = db.Column(db.DateTime, nullable=True)
    
    # Status and impact
    status = db.Column(db.String(20), nullable=False, default='scheduled')  # scheduled, in_progress, completed, cancelled
    impact_level = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    affected_services = db.Column(db.JSON, nullable=True)  # List of affected services
    
    # Notifications
    notify_users = db.Column(db.Boolean, nullable=False, default=True)
    notification_sent = db.Column(db.Boolean, nullable=False, default=False)
    notification_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Management
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Completion details
    completion_notes = db.Column(db.Text, nullable=True)
    success = db.Column(db.Boolean, nullable=True)  # Null until completed
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_maintenance_windows')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_maintenance_windows')
    
    # Indexes
    __table_args__ = (
        Index('idx_maintenance_status_start', 'status', 'scheduled_start'),
        Index('idx_maintenance_impact_type', 'impact_level', 'maintenance_type'),
        CheckConstraint(
            "status IN ('scheduled', 'in_progress', 'completed', 'cancelled')",
            name='ck_maintenance_status'
        ),
        CheckConstraint(
            "impact_level IN ('low', 'medium', 'high', 'critical')",
            name='ck_maintenance_impact_level'
        ),
        CheckConstraint(
            "maintenance_type IN ('scheduled', 'emergency', 'routine')",
            name='ck_maintenance_type'
        ),
        CheckConstraint(
            'scheduled_end > scheduled_start',
            name='ck_maintenance_schedule_valid'
        ),
    )
    
    def __repr__(self):
        return f'<SystemMaintenanceWindow {self.title}:{self.status}>'
    
    @property
    def is_active(self):
        """Check if maintenance window is currently active."""
        now = datetime.utcnow()
        return (self.status == 'in_progress' or 
                (self.status == 'scheduled' and 
                 self.scheduled_start <= now <= self.scheduled_end))
    
    @property
    def duration_minutes(self):
        """Get scheduled duration in minutes."""
        if self.scheduled_start and self.scheduled_end:
            delta = self.scheduled_end - self.scheduled_start
            return int(delta.total_seconds() / 60)
        return 0
    
    @property
    def actual_duration_minutes(self):
        """Get actual duration in minutes if completed."""
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return None
