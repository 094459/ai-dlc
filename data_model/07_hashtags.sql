-- Hashtags Table
-- Supports Hashtag Component
-- Stores unique hashtags and their metadata

CREATE TABLE hashtags (
    id VARCHAR(36) PRIMARY KEY,
    tag VARCHAR(100) NOT NULL UNIQUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    first_used_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME
);

-- Comments:
-- id: UUID for hashtag identification
-- tag: The hashtag text (without # symbol, normalized to lowercase)
-- usage_count: Number of facts using this hashtag (for trending analysis)
-- first_used_at: Timestamp when hashtag was first created/used
-- last_used_at: Timestamp when hashtag was most recently used
-- created_at: Record creation timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag for hashtag removal
-- deleted_at: Timestamp when hashtag was soft deleted
-- Note: Hashtags are normalized (lowercase, no spaces) for consistency
