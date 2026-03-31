-- Fact Resources Table
-- Supports Resource Component
-- Stores URLs and images attached to facts as supporting evidence

CREATE TABLE fact_resources (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    resource_type VARCHAR(10) NOT NULL CHECK (resource_type IN ('url', 'image')),
    resource_value VARCHAR(2000) NOT NULL, -- URL or file path
    display_title VARCHAR(200), -- Optional display title for the resource
    file_size INTEGER, -- For images, file size in bytes
    mime_type VARCHAR(100), -- For images, MIME type
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id)
);

-- Comments:
-- id: UUID for resource identification
-- fact_id: Foreign key linking to the fact this resource supports
-- resource_type: Type of resource ('url' or 'image')
-- resource_value: The actual URL or file path to the resource
-- display_title: Optional user-provided or extracted title for display
-- file_size: File size in bytes (for images only)
-- mime_type: MIME type for file validation (for images only)
-- is_active: Flag to enable/disable resources without deletion
-- created_at: Resource creation timestamp
-- updated_at: Last modification timestamp
-- is_deleted: Soft delete flag for resource removal
-- deleted_at: Timestamp when resource was soft deleted
