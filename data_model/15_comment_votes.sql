-- Comment Votes Table
-- Supports Voting Component
-- Stores user votes on comments (Upvote/Downvote voting)

CREATE TABLE comment_votes (
    id VARCHAR(36) PRIMARY KEY,
    comment_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('upvote', 'downvote')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (comment_id) REFERENCES comments(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(comment_id, user_id)
);

-- Comments:
-- id: UUID for vote identification
-- comment_id: Foreign key linking to the comment being voted on
-- user_id: Foreign key linking to the user casting the vote
-- vote_type: Type of vote ('upvote' = helpful/valuable, 'downvote' = unhelpful/inappropriate)
-- created_at: Vote creation timestamp
-- updated_at: Last modification timestamp (when vote is changed)
-- is_deleted: Soft delete flag for vote removal
-- deleted_at: Timestamp when vote was soft deleted
-- UNIQUE constraint: Ensures one vote per user per comment (can be updated, not duplicated)
-- Note: Users cannot vote on their own comments (enforced at application level)
