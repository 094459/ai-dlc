-- Analytics Events Table
-- Supports Analytics Component
-- Tracks user actions and system events for analytics and metrics

CREATE TABLE analytics_events (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36), -- NULL for anonymous events
    session_id VARCHAR(36), -- Links to user session if available
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(30) NOT NULL CHECK (event_category IN ('user_action', 'content_interaction', 'system_event', 'moderation_event')),
    event_data TEXT, -- JSON-like string data (since no JSONB allowed)
    related_content_type VARCHAR(10) CHECK (related_content_type IN ('fact', 'comment', 'user', 'report')),
    related_content_id VARCHAR(36),
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer VARCHAR(500),
    page_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES user_sessions(id)
);

-- Comments:
-- id: UUID for event identification
-- user_id: Foreign key to user who triggered the event (NULL for anonymous)
-- session_id: Foreign key to user session (for session-based analytics)
-- event_type: Specific type of event (e.g., 'fact_created', 'vote_cast', 'login')
-- event_category: Broad category for event grouping and filtering
-- event_data: Additional event data stored as text (JSON-like format)
-- related_content_type: Type of content this event relates to (optional)
-- related_content_id: ID of related content
-- ip_address: Client IP address for geographic analytics
-- user_agent: Browser/client information for device analytics
-- referrer: HTTP referrer for traffic source analysis
-- page_url: URL where event occurred
-- created_at: Event timestamp
-- is_deleted: Soft delete flag (for data cleanup)
-- deleted_at: Timestamp when event was soft deleted
