-- Users Table
-- Supports User Authentication Component
-- Stores core user account information for registration, login, and authentication

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
    is_moderator INTEGER NOT NULL DEFAULT 0 CHECK (is_moderator IN (0, 1)),
    last_login DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME
);

-- Comments:
-- id: UUID stored as VARCHAR(36) for cross-database compatibility
-- email: Unique identifier for user login, enforced at database level
-- password_hash: Securely hashed password using bcrypt (never store plain text)
-- is_active: Boolean flag to enable/disable user accounts
-- is_admin: Boolean flag for administrative privileges
-- is_moderator: Boolean flag for moderation privileges
-- last_login: Tracks user's most recent login for analytics and security
-- created_at: Account creation timestamp
-- updated_at: Last modification timestamp for account changes
-- is_deleted: Soft delete flag to preserve referential integrity
-- deleted_at: Timestamp when account was soft deleted
