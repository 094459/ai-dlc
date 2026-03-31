-- Vote Statistics Table
-- Supports Voting Component
-- Caches calculated voting statistics for performance optimization

CREATE TABLE vote_statistics (
    id VARCHAR(36) PRIMARY KEY,
    content_type VARCHAR(10) NOT NULL CHECK (content_type IN ('fact', 'comment')),
    content_id VARCHAR(36) NOT NULL,
    total_votes INTEGER NOT NULL DEFAULT 0,
    positive_votes INTEGER NOT NULL DEFAULT 0, -- 'fact' votes or 'upvote' votes
    negative_votes INTEGER NOT NULL DEFAULT 0, -- 'fake' votes or 'downvote' votes
    vote_score DECIMAL(10,4) NOT NULL DEFAULT 0.0, -- Calculated score for ranking
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    UNIQUE(content_type, content_id)
);

-- Comments:
-- id: UUID for statistics record identification
-- content_type: Type of content ('fact' or 'comment')
-- content_id: ID of the fact or comment these statistics apply to
-- total_votes: Total number of votes (positive + negative)
-- positive_votes: Number of positive votes ('fact' for facts, 'upvote' for comments)
-- negative_votes: Number of negative votes ('fake' for facts, 'downvote' for comments)
-- vote_score: Calculated score for ranking and display
--   For facts: (positive_votes - negative_votes) / total_votes
--   For comments: positive_votes - negative_votes
-- last_updated: Timestamp when statistics were last recalculated
-- created_at: Record creation timestamp
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when record was soft deleted
-- UNIQUE constraint: One statistics record per content item
