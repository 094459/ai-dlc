-- Comments Table
-- Supports Comment Component
-- Stores comments on facts with support for nested threading (up to 3 levels)

CREATE TABLE comments (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    parent_comment_id VARCHAR(36), -- NULL for top-level comments
    content TEXT NOT NULL, -- Max 250 characters enforced at application level
    nesting_level INTEGER NOT NULL DEFAULT 0 CHECK (nesting_level >= 0 AND nesting_level <= 2),
    reply_count INTEGER NOT NULL DEFAULT 0,
    edit_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
);

-- Comments:
-- id: UUID for comment identification
-- fact_id: Foreign key linking to the fact being commented on
-- user_id: Foreign key linking to the user who wrote the comment
-- parent_comment_id: Foreign key to parent comment (NULL for top-level comments)
-- content: The comment text (max 250 characters, enforced at app level)
-- nesting_level: Depth of nesting (0=top-level, 1=reply, 2=reply to reply, max=2)
-- reply_count: Number of direct replies to this comment (for UI optimization)
-- edit_count: Number of times the comment has been edited
-- created_at: Comment creation timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag (shows as "[deleted]" but preserves thread structure)
-- deleted_at: Timestamp when comment was soft deleted
