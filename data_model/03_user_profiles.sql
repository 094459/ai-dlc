-- User Profiles Table
-- Supports User Profile Component
-- Stores user profile information including name, biography, and profile settings

CREATE TABLE user_profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    biography TEXT, -- Max 1000 characters enforced at application level
    profile_photo_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Comments:
-- id: UUID for profile identification
-- user_id: Foreign key linking to users table (one-to-one relationship)
-- name: Required display name for the user (1-100 characters)
-- biography: Optional user biography (max 1000 characters, enforced at app level)
-- profile_photo_url: URL/path to user's profile photo (optional)
-- created_at: Profile creation timestamp
-- updated_at: Last profile modification timestamp
-- is_deleted: Soft delete flag for profile removal
-- deleted_at: Timestamp when profile was soft deleted
