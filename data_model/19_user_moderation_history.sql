-- User Moderation History Table
-- Supports Moderation Component
-- Tracks moderation status and history for each user

CREATE TABLE user_moderation_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    moderation_status VARCHAR(20) NOT NULL DEFAULT 'good_standing' CHECK (moderation_status IN ('good_standing', 'warned', 'suspended', 'banned')),
    warning_count INTEGER NOT NULL DEFAULT 0,
    suspension_count INTEGER NOT NULL DEFAULT 0,
    total_reports_against INTEGER NOT NULL DEFAULT 0,
    total_content_removed INTEGER NOT NULL DEFAULT 0,
    current_suspension_expires DATETIME, -- NULL if not currently suspended
    ban_date DATETIME, -- NULL if not banned
    ban_reason TEXT, -- Reason for ban (if applicable)
    last_moderation_action_id VARCHAR(36), -- Reference to most recent moderation action
    risk_score INTEGER NOT NULL DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100), -- Calculated risk score (0-100)
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (last_moderation_action_id) REFERENCES moderation_actions(id),
    UNIQUE(user_id)
);

-- Comments:
-- id: UUID for moderation history record identification
-- user_id: Foreign key to user this history belongs to (one record per user)
-- moderation_status: Current moderation status of the user
--   - good_standing: No current moderation actions
--   - warned: Has active warnings
--   - suspended: Currently suspended
--   - banned: Permanently banned
-- warning_count: Total number of warnings issued to this user
-- suspension_count: Total number of times user has been suspended
-- total_reports_against: Total number of reports filed against this user
-- total_content_removed: Total pieces of content removed from this user
-- current_suspension_expires: When current suspension ends (NULL if not suspended)
-- ban_date: When user was banned (NULL if not banned)
-- ban_reason: Detailed reason for permanent ban
-- last_moderation_action_id: Reference to most recent moderation action
-- risk_score: Calculated risk score based on user behavior (0=low risk, 100=high risk)
-- created_at: Record creation timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when record was soft deleted
-- UNIQUE constraint: One moderation history record per user
