-- System Configuration Table
-- Supports Admin Dashboard Component
-- Stores application-wide configuration settings

CREATE TABLE system_configuration (
    id VARCHAR(36) PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) NOT NULL CHECK (config_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    is_public INTEGER NOT NULL DEFAULT 0 CHECK (is_public IN (0, 1)), -- Whether setting is visible to non-admins
    requires_restart INTEGER NOT NULL DEFAULT 0 CHECK (requires_restart IN (0, 1)), -- Whether change requires app restart
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(36), -- Admin user who last updated this setting
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Comments:
-- id: UUID for configuration record identification
-- config_key: Unique identifier for the configuration setting
-- config_value: The actual configuration value (stored as text)
-- config_type: Data type of the configuration value for proper parsing
-- description: Human-readable description of what this setting controls
-- is_public: Whether this setting can be viewed by non-admin users
-- requires_restart: Whether changing this setting requires application restart
-- created_at: Setting creation timestamp
-- updated_at: Last modification timestamp
-- updated_by: Foreign key to admin user who last modified this setting
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when setting was soft deleted
-- UNIQUE constraint: Ensures one record per configuration key
