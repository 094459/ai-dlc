-- Notifications Table
-- Supports Notification Component
-- Stores in-app and email notifications for users

CREATE TABLE notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    notification_type VARCHAR(30) NOT NULL CHECK (notification_type IN ('comment_reply', 'fact_vote', 'comment_vote', 'fact_comment', 'moderation_action', 'system_announcement')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    related_content_type VARCHAR(10) CHECK (related_content_type IN ('fact', 'comment', 'user', 'report')),
    related_content_id VARCHAR(36),
    is_read INTEGER NOT NULL DEFAULT 0 CHECK (is_read IN (0, 1)),
    read_at DATETIME,
    delivery_method VARCHAR(20) NOT NULL DEFAULT 'in_app' CHECK (delivery_method IN ('in_app', 'email', 'both')),
    email_sent INTEGER NOT NULL DEFAULT 0 CHECK (email_sent IN (0, 1)),
    email_sent_at DATETIME,
    priority VARCHAR(10) NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Comments:
-- id: UUID for notification identification
-- user_id: Foreign key to user receiving the notification
-- notification_type: Type of notification being sent
-- title: Short notification title for display
-- message: Full notification message content
-- related_content_type: Type of content this notification relates to (optional)
-- related_content_id: ID of related content (fact, comment, etc.)
-- is_read: Whether user has read the notification
-- read_at: Timestamp when notification was marked as read
-- delivery_method: How notification should be delivered
-- email_sent: Whether email notification was successfully sent
-- email_sent_at: Timestamp when email was sent
-- priority: Priority level for notification delivery
-- created_at: Notification creation timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when notification was soft deleted
