-- Audit Logs Table
-- Supports Security Component
-- Records all significant system actions for security and compliance

CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36), -- NULL for system-initiated actions
    action_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(30) NOT NULL,
    resource_id VARCHAR(36),
    old_values TEXT, -- Previous state (JSON-like string format)
    new_values TEXT, -- New state (JSON-like string format)
    ip_address VARCHAR(45),
    user_agent TEXT,
    success INTEGER NOT NULL CHECK (success IN (0, 1)),
    error_message TEXT, -- Error details if success = 0
    severity VARCHAR(10) NOT NULL DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Comments:
-- id: UUID for audit log identification
-- user_id: Foreign key to user who performed the action (NULL for system actions)
-- action_type: Type of action performed (e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN')
-- resource_type: Type of resource affected (e.g., 'user', 'fact', 'comment')
-- resource_id: ID of the specific resource affected
-- old_values: Previous state of the resource (before change)
-- new_values: New state of the resource (after change)
-- ip_address: Client IP address for security tracking
-- user_agent: Browser/client information
-- success: Whether the action completed successfully
-- error_message: Error details if the action failed
-- severity: Log level for filtering and alerting
-- created_at: Action timestamp
-- is_deleted: Soft delete flag (rarely used, for compliance)
-- deleted_at: Timestamp when log was soft deleted
