-- Reports Table
-- Supports Report Component
-- Stores user reports of inappropriate content (facts and comments)

CREATE TABLE reports (
    id VARCHAR(36) PRIMARY KEY,
    reporter_user_id VARCHAR(36) NOT NULL,
    reported_content_type VARCHAR(10) NOT NULL CHECK (reported_content_type IN ('fact', 'comment')),
    reported_content_id VARCHAR(36) NOT NULL,
    report_category VARCHAR(50) NOT NULL CHECK (report_category IN ('spam', 'harassment', 'misinformation', 'inappropriate', 'copyright', 'other')),
    report_reason TEXT, -- Optional detailed explanation from reporter
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'under_review', 'resolved', 'dismissed')),
    priority VARCHAR(10) NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    assigned_moderator_id VARCHAR(36), -- NULL if not yet assigned
    resolution_notes TEXT, -- Moderator notes on resolution
    resolved_at DATETIME, -- When report was resolved/dismissed
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (reporter_user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_moderator_id) REFERENCES users(id)
);

-- Comments:
-- id: UUID for report identification
-- reporter_user_id: Foreign key to user who submitted the report
-- reported_content_type: Type of content being reported ('fact' or 'comment')
-- reported_content_id: ID of the fact or comment being reported
-- report_category: Predefined category for the report type
-- report_reason: Optional detailed explanation from the reporter
-- status: Current status of the report in the moderation workflow
-- priority: Priority level assigned to the report (can be auto-assigned or manual)
-- assigned_moderator_id: Foreign key to moderator handling this report (NULL if unassigned)
-- resolution_notes: Moderator's notes explaining the resolution decision
-- resolved_at: Timestamp when report was resolved or dismissed
-- created_at: Report submission timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when report was soft deleted
