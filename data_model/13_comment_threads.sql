-- Comment Threads Table
-- Supports Thread Management Component
-- Manages comment thread organization and user-specific thread states

CREATE TABLE comment_threads (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    root_comment_id VARCHAR(36) NOT NULL,
    total_comments INTEGER NOT NULL DEFAULT 1,
    last_activity DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (root_comment_id) REFERENCES comments(id),
    UNIQUE(fact_id, root_comment_id)
);

-- Comments:
-- id: UUID for thread identification
-- fact_id: Foreign key linking to the fact this thread belongs to
-- root_comment_id: Foreign key to the top-level comment that started this thread
-- total_comments: Total number of comments in this thread (including root)
-- last_activity: Timestamp of most recent activity in this thread
-- created_at: Thread creation timestamp (when root comment was created)
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag for thread removal
-- deleted_at: Timestamp when thread was soft deleted
-- UNIQUE constraint: Ensures one thread record per root comment per fact
