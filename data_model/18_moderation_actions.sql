-- Moderation Actions Table
-- Supports Moderation Component
-- Records all moderation actions taken on content and users

CREATE TABLE moderation_actions (
    id VARCHAR(36) PRIMARY KEY,
    moderator_id VARCHAR(36) NOT NULL,
    action_type VARCHAR(30) NOT NULL CHECK (action_type IN ('content_removal', 'content_restoration', 'user_warning', 'user_suspension', 'user_ban', 'report_dismissal')),
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('fact', 'comment', 'user', 'report')),
    target_id VARCHAR(36) NOT NULL,
    related_report_id VARCHAR(36), -- NULL if action not related to a specific report
    reason TEXT NOT NULL, -- Explanation for the moderation action
    duration_hours INTEGER, -- For suspensions, duration in hours (NULL for permanent actions)
    expires_at DATETIME, -- When suspension expires (NULL for permanent actions)
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)), -- Whether action is currently in effect
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (moderator_id) REFERENCES users(id),
    FOREIGN KEY (related_report_id) REFERENCES reports(id)
);

-- Comments:
-- id: UUID for moderation action identification
-- moderator_id: Foreign key to user who performed the moderation action
-- action_type: Type of moderation action taken
--   - content_removal: Hide/remove fact or comment
--   - content_restoration: Restore previously removed content
--   - user_warning: Issue warning to user
--   - user_suspension: Temporarily suspend user account
--   - user_ban: Permanently ban user account
--   - report_dismissal: Dismiss report as invalid
-- target_type: Type of entity the action was taken on
-- target_id: ID of the specific entity (fact, comment, user, or report)
-- related_report_id: Foreign key to report that triggered this action (if applicable)
-- reason: Detailed explanation for why the action was taken
-- duration_hours: Duration for temporary actions like suspensions
-- expires_at: When temporary actions expire (calculated from duration_hours)
-- is_active: Whether the action is currently in effect (can be deactivated)
-- created_at: Action timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when action was soft deleted
