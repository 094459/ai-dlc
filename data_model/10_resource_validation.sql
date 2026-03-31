-- Resource Validation Table
-- Supports Resource Component
-- Tracks validation status and health of attached resources

CREATE TABLE resource_validation (
    id VARCHAR(36) PRIMARY KEY,
    resource_id VARCHAR(36) NOT NULL,
    validation_status VARCHAR(20) NOT NULL CHECK (validation_status IN ('pending', 'valid', 'invalid', 'broken')),
    validation_message TEXT, -- Optional details about validation result
    last_checked DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    check_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (resource_id) REFERENCES fact_resources(id)
);

-- Comments:
-- id: UUID for validation record identification
-- resource_id: Foreign key linking to fact_resources table
-- validation_status: Current validation state of the resource
--   - 'pending': Not yet validated
--   - 'valid': Resource is accessible and valid
--   - 'invalid': Resource format/content is invalid
--   - 'broken': Resource is no longer accessible
-- validation_message: Optional details about validation results or errors
-- last_checked: Timestamp of most recent validation check
-- check_count: Number of times this resource has been validated
-- created_at: Record creation timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag
-- deleted_at: Timestamp when record was soft deleted
