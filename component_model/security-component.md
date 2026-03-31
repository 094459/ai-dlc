# Security Component

## Purpose and Responsibilities
The Security Component provides comprehensive security services including authorization, audit logging, input validation, security monitoring, and protection against common web vulnerabilities. It ensures the application maintains security best practices and protects user data.

## Attributes and Data Models

### Permission Entity
```
Permission {
  id: UUID (Primary Key)
  permission_name: String (Unique)
  description: Text
  resource_type: String (e.g., 'fact', 'comment', 'user')
  action: String (e.g., 'create', 'read', 'update', 'delete')
  is_active: Boolean (Default: true)
  created_at: DateTime
}
```

### UserRole Entity
```
UserRole {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to User)
  role_name: Enum ('user', 'moderator', 'admin', 'super_admin')
  granted_by: UUID (Foreign Key to User)
  granted_at: DateTime
  expires_at: DateTime (Optional)
  is_active: Boolean (Default: true)
}
```

### AuditLog Entity
```
AuditLog {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to User, Optional)
  session_id: String (Optional)
  action: String (Required)
  resource_type: String (Optional)
  resource_id: UUID (Optional)
  old_values: JSON (Optional)
  new_values: JSON (Optional)
  ip_address: String (Hashed)
  user_agent: String
  timestamp: DateTime
  severity: Enum ('info', 'warning', 'error', 'critical')
  success: Boolean (Default: true)
}
```

### SecurityEvent Entity
```
SecurityEvent {
  id: UUID (Primary Key)
  event_type: Enum ('failed_login', 'suspicious_activity', 'rate_limit_exceeded', 'unauthorized_access')
  user_id: UUID (Foreign Key to User, Optional)
  ip_address: String (Hashed)
  details: JSON
  risk_score: Integer (1-100)
  is_resolved: Boolean (Default: false)
  created_at: DateTime
  resolved_at: DateTime (Optional)
}
```

## Behaviors and Methods

### Authorization Methods
- **checkPermission(userId, resource, action)**: Verifies user has permission for action
- **getUserRoles(userId)**: Gets all roles assigned to user
- **getUserPermissions(userId)**: Gets all permissions for user (via roles)
- **assignRole(userId, roleName, grantedBy)**: Assigns role to user
- **revokeRole(userId, roleName, revokedBy)**: Removes role from user
- **hasRole(userId, roleName)**: Checks if user has specific role

### Input Validation Methods
- **validateInput(input, validationType)**: Validates user input against rules
- **sanitizeHtml(content)**: Removes dangerous HTML tags and attributes
- **validateEmail(email)**: Validates email format and checks for common attacks
- **validateUrl(url)**: Validates URL format and checks for malicious content
- **escapeOutput(content, context)**: Escapes content for safe output in different contexts

### Audit Logging Methods
- **logUserAction(userId, action, resourceType, resourceId, details)**: Logs user action
- **logSystemEvent(event, severity, details)**: Logs system-level event
- **logSecurityEvent(eventType, userId, ipAddress, details)**: Logs security-related event
- **getAuditTrail(resourceType, resourceId, limit)**: Gets audit history for resource
- **searchAuditLogs(filters, dateRange, limit)**: Searches audit logs with filters

### Security Monitoring Methods
- **detectSuspiciousActivity(userId, ipAddress, actions)**: Analyzes user behavior for anomalies
- **checkRateLimit(userId, action, timeWindow)**: Enforces rate limiting
- **validateSession(sessionToken)**: Validates session token and checks for hijacking
- **monitorFailedLogins(ipAddress, timeWindow)**: Tracks failed login attempts
- **calculateRiskScore(userId, action, context)**: Calculates risk score for action

### Cryptographic Methods
- **hashPassword(password, salt)**: Securely hashes password with salt
- **verifyPassword(password, hash)**: Verifies password against hash
- **generateSecureToken(length)**: Generates cryptographically secure random token
- **encryptSensitiveData(data, key)**: Encrypts sensitive data for storage
- **decryptSensitiveData(encryptedData, key)**: Decrypts sensitive data

## Interfaces Provided
- **AuthorizationService**: Interface for permission and role management
- **ValidationService**: Interface for input validation and sanitization
- **AuditService**: Interface for audit logging and trail retrieval
- **SecurityMonitoringService**: Interface for security event detection and monitoring

## Interfaces Required
- **DatabaseService**: For security data persistence
- **UserRetrievalService**: For user information in security checks
- **SessionService**: For session validation and management
- **NotificationService**: For security alert notifications

## Dependencies and Relationships
- **Depends on**: User Authentication Component, Database Service
- **Used by**: All components requiring security services
- **Integrates with**: Admin Dashboard Component, Notification Component

## Business Rules and Constraints
- All user actions must be authorized before execution
- All security events must be logged and monitored
- User input must be validated and sanitized
- Security policies are configurable by administrators

## Error Handling
- **UnauthorizedAccess**: When user lacks permission for action
- **InvalidInput**: When input fails validation rules
- **SecurityViolation**: When suspicious activity is detected
- **AuditLogFailure**: When audit logging fails
- **EncryptionError**: When cryptographic operations fail
- **RateLimitExceeded**: When user exceeds allowed action rate

## Permission System

### Resource Types
- **fact**: User-submitted facts
- **comment**: Comments on facts
- **user**: User accounts and profiles
- **report**: Content reports
- **system**: System configuration and settings

### Actions
- **create**: Create new resources
- **read**: View resources
- **update**: Modify existing resources
- **delete**: Remove resources
- **moderate**: Perform moderation actions
- **admin**: Administrative actions

### Role Hierarchy
```
Super Admin: All permissions
├── Admin: User management, system configuration
├── Moderator: Content moderation, user warnings
└── User: Basic content creation and interaction
```

## Input Validation Rules

### Content Validation
- **Length Limits**: Enforce character limits for all text inputs
- **HTML Sanitization**: Remove dangerous HTML tags and attributes
- **XSS Prevention**: Escape output based on context (HTML, JavaScript, CSS)
- **SQL Injection Prevention**: Use parameterized queries
- **File Upload Validation**: Validate file types, sizes, and content

### Data Format Validation
- **Email**: RFC-compliant email format validation
- **URL**: Valid URL format with protocol validation
- **Phone**: International phone number format validation
- **Date**: Valid date format and range validation
- **Numeric**: Range and format validation for numbers

## Audit Logging

### Logged Events
- **Authentication**: Login, logout, password changes
- **Authorization**: Permission checks, role changes
- **Content Operations**: Create, update, delete facts/comments
- **Moderation Actions**: Content removal, user warnings/bans
- **Administrative Actions**: System configuration changes
- **Security Events**: Failed logins, suspicious activity

### Log Format
```json
{
  "timestamp": "2025-08-18T11:00:00Z",
  "user_id": "uuid",
  "action": "fact_created",
  "resource_type": "fact",
  "resource_id": "uuid",
  "ip_address": "hashed_ip",
  "user_agent": "browser_info",
  "success": true,
  "details": {}
}
```

## Integration Points
- **User Authentication Component**: Validates sessions and manages user roles
- **All Content Components**: Validates permissions before operations
- **Admin Dashboard Component**: Provides security monitoring and audit interfaces
- **Notification Component**: Sends security alerts and notifications
- **Analytics Component**: Provides security metrics and trends

## Security Best Practices
- **Defense in Depth**: Multiple layers of security controls
- **Principle of Least Privilege**: Users get minimum required permissions
- **Secure by Default**: Secure configurations as default settings
- **Input Validation**: Validate all input at multiple layers
- **Output Encoding**: Encode output based on context
- **Session Security**: Secure session management practices
- **Error Handling**: Don't leak sensitive information in errors

