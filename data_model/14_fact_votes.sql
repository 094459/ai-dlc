-- Fact Votes Table
-- Supports Voting Component
-- Stores user votes on facts (Fact/Fake voting)

CREATE TABLE fact_votes (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('fact', 'fake')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(fact_id, user_id)
);

-- Comments:
-- id: UUID for vote identification
-- fact_id: Foreign key linking to the fact being voted on
-- user_id: Foreign key linking to the user casting the vote
-- vote_type: Type of vote ('fact' = believes it's true, 'fake' = believes it's false)
-- created_at: Vote creation timestamp
-- updated_at: Last modification timestamp (when vote is changed)
-- is_deleted: Soft delete flag for vote removal
-- deleted_at: Timestamp when vote was soft deleted
-- UNIQUE constraint: Ensures one vote per user per fact (can be updated, not duplicated)
-- Note: Users cannot vote on their own facts (enforced at application level)
