-- Comment Edit History Table
-- Supports Comment Component
-- Maintains audit trail of all comment modifications

CREATE TABLE comment_edit_history (
    id VARCHAR(36) PRIMARY KEY,
    comment_id VARCHAR(36) NOT NULL,
    previous_content TEXT NOT NULL,
    edit_reason VARCHAR(500), -- Optional reason for the edit
    edited_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (comment_id) REFERENCES comments(id)
);

-- Comments:
-- id: UUID for edit history record identification
-- comment_id: Foreign key linking to the comment that was edited
-- previous_content: The content before the edit (for audit purposes)
-- edit_reason: Optional user-provided reason for making the edit
-- edited_at: Timestamp when the edit occurred
-- is_deleted: Soft delete flag (rarely used, for data cleanup)
-- deleted_at: Timestamp when record was soft deleted
-- Note: This table preserves all comment edit history for transparency and moderation
