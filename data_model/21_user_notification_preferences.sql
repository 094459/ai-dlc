-- User Notification Preferences Table
-- Supports Notification Component
-- Stores user preferences for different types of notifications

CREATE TABLE user_notification_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    notification_type VARCHAR(30) NOT NULL CHECK (notification_type IN ('comment_reply', 'fact_vote', 'comment_vote', 'fact_comment', 'moderation_action', 'system_announcement')),
    in_app_enabled INTEGER NOT NULL DEFAULT 1 CHECK (in_app_enabled IN (0, 1)),
    email_enabled INTEGER NOT NULL DEFAULT 1 CHECK (email_enabled IN (0, 1)),
    frequency VARCHAR(20) NOT NULL DEFAULT 'immediate' CHECK (frequency IN ('immediate', 'hourly', 'daily', 'weekly', 'disabled')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, notification_type)
);

-- Comments:
-- id: UUID for preference record identification
-- user_id: Foreign key to user these preferences belong to
-- notification_type: Type of notification this preference applies to
-- in_app_enabled: Whether to show in-app notifications for this type
-- email_enabled: Whether to send email notifications for this type
-- frequency: How often to send notifications (immediate, batched, or disabled)
-- created_at: Preference creation timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when preference was soft deleted
-- UNIQUE constraint: One preference record per user per notification type
