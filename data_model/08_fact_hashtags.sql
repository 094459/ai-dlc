-- Fact Hashtags Junction Table
-- Supports Hashtag Component
-- Links facts to hashtags (many-to-many relationship)

CREATE TABLE fact_hashtags (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    hashtag_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (hashtag_id) REFERENCES hashtags(id),
    UNIQUE(fact_id, hashtag_id)
);

-- Comments:
-- id: UUID for junction record identification
-- fact_id: Foreign key linking to facts table
-- hashtag_id: Foreign key linking to hashtags table
-- created_at: Timestamp when hashtag was associated with fact
-- is_deleted: Soft delete flag for removing hashtag associations
-- deleted_at: Timestamp when association was soft deleted
-- UNIQUE constraint: Prevents duplicate hashtag associations per fact
-- Note: This enables many-to-many relationship between facts and hashtags
