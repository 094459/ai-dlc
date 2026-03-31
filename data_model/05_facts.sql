-- Facts Table
-- Supports Fact Component
-- Stores user-submitted facts with content and metadata

CREATE TABLE facts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL, -- Max 500 characters enforced at application level
    edit_count INTEGER NOT NULL DEFAULT 0,
    last_edited_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Comments:
-- id: UUID for fact identification
-- user_id: Foreign key linking to the user who submitted the fact
-- content: The actual fact content (max 500 characters, enforced at app level)
-- edit_count: Number of times the fact has been edited
-- last_edited_at: Timestamp of the most recent edit (NULL if never edited)
-- created_at: Fact submission timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag to preserve referential integrity
-- deleted_at: Timestamp when fact was soft deleted
