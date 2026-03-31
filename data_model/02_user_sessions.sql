-- User Sessions Table
-- Supports User Authentication Component
-- Manages user login sessions and session tokens

CREATE TABLE user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    ip_address VARCHAR(45), -- Supports both IPv4 and IPv6
    user_agent TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Comments:
-- id: UUID for session identification
-- user_id: Foreign key linking to users table
-- session_token: Unique cryptographically secure token for session validation
-- expires_at: Session expiration timestamp (configurable, default 24 hours)
-- ip_address: Client IP address for security monitoring (VARCHAR(45) for IPv6)
-- user_agent: Browser/client information for security and analytics
-- created_at: Session creation timestamp
-- is_deleted: Soft delete for session invalidation
-- deleted_at: Timestamp when session was invalidated
