-- Profile Photos Table
-- Supports User Profile Component
-- Manages profile photo uploads and file metadata

CREATE TABLE profile_photos (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Comments:
-- id: UUID for photo record identification
-- user_id: Foreign key linking to users table
-- filename: Original filename of uploaded photo
-- file_path: Server file path where photo is stored
-- file_size: File size in bytes for storage management
-- mime_type: MIME type (image/jpeg, image/png, etc.) for validation
-- uploaded_at: Photo upload timestamp
-- is_deleted: Soft delete flag for photo removal
-- deleted_at: Timestamp when photo was soft deleted
-- Note: Users can have multiple photos over time, but only one active profile photo
