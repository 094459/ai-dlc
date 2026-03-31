# Error Codes Reference

## Overview

This document provides a comprehensive reference for all error codes used in the Fact Checker Application API. Each error code includes the HTTP status code, description, and example response.

## Error Response Format

All API errors follow this consistent format:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional context or validation details"
  }
}
```

## Authentication Errors (AUTH_*)

### AUTH_001 - Invalid Credentials
**HTTP Status:** 401 Unauthorized
**Description:** Login credentials are incorrect

```json
{
  "success": false,
  "error": "Invalid email or password",
  "code": "AUTH_001"
}
```

### AUTH_002 - Session Expired
**HTTP Status:** 401 Unauthorized
**Description:** User session has expired

```json
{
  "success": false,
  "error": "Session has expired. Please log in again",
  "code": "AUTH_002"
}
```

### AUTH_003 - Account Suspended
**HTTP Status:** 403 Forbidden
**Description:** User account is suspended

```json
{
  "success": false,
  "error": "Account is suspended until 2024-02-01",
  "code": "AUTH_003",
  "details": {
    "suspension_end": "2024-02-01T00:00:00Z",
    "reason": "Violation of community guidelines"
  }
}
```

### AUTH_004 - Account Banned
**HTTP Status:** 403 Forbidden
**Description:** User account is permanently banned

```json
{
  "success": false,
  "error": "Account has been permanently banned",
  "code": "AUTH_004",
  "details": {
    "reason": "Repeated violations of terms of service"
  }
}
```

### AUTH_005 - Insufficient Permissions
**HTTP Status:** 403 Forbidden
**Description:** User lacks required permissions

```json
{
  "success": false,
  "error": "Insufficient permissions to access this resource",
  "code": "AUTH_005",
  "details": {
    "required_role": "moderator",
    "user_role": "user"
  }
}
```

### AUTH_006 - Registration Failed
**HTTP Status:** 400 Bad Request
**Description:** User registration failed due to validation errors

```json
{
  "success": false,
  "error": "Registration failed",
  "code": "AUTH_006",
  "details": {
    "email": "Email already exists",
    "password": "Password must be at least 8 characters"
  }
}
```

## Validation Errors (VAL_*)

### VAL_001 - Required Field Missing
**HTTP Status:** 400 Bad Request
**Description:** Required field is missing from request

```json
{
  "success": false,
  "error": "Required field missing",
  "code": "VAL_001",
  "details": {
    "field": "content",
    "message": "Content is required"
  }
}
```

### VAL_002 - Invalid Field Format
**HTTP Status:** 400 Bad Request
**Description:** Field format is invalid

```json
{
  "success": false,
  "error": "Invalid field format",
  "code": "VAL_002",
  "details": {
    "field": "email",
    "message": "Invalid email format",
    "value": "invalid-email"
  }
}
```

### VAL_003 - Field Length Violation
**HTTP Status:** 400 Bad Request
**Description:** Field length exceeds limits

```json
{
  "success": false,
  "error": "Field length violation",
  "code": "VAL_003",
  "details": {
    "field": "content",
    "message": "Content must be between 10 and 2000 characters",
    "current_length": 5,
    "min_length": 10,
    "max_length": 2000
  }
}
```

### VAL_004 - Invalid Enum Value
**HTTP Status:** 400 Bad Request
**Description:** Field value is not in allowed enum values

```json
{
  "success": false,
  "error": "Invalid enum value",
  "code": "VAL_004",
  "details": {
    "field": "vote_type",
    "message": "Vote type must be 'fact' or 'fake'",
    "value": "invalid",
    "allowed_values": ["fact", "fake"]
  }
}
```

### VAL_005 - Invalid URL Format
**HTTP Status:** 400 Bad Request
**Description:** URL format is invalid

```json
{
  "success": false,
  "error": "Invalid URL format",
  "code": "VAL_005",
  "details": {
    "field": "resource_url",
    "message": "URL must be a valid HTTP or HTTPS URL",
    "value": "invalid-url"
  }
}
```

## Resource Errors (RES_*)

### RES_001 - Resource Not Found
**HTTP Status:** 404 Not Found
**Description:** Requested resource does not exist

```json
{
  "success": false,
  "error": "Resource not found",
  "code": "RES_001",
  "details": {
    "resource_type": "fact",
    "resource_id": "non-existent-uuid"
  }
}
```

### RES_002 - Resource Access Denied
**HTTP Status:** 403 Forbidden
**Description:** User cannot access the requested resource

```json
{
  "success": false,
  "error": "Access denied to resource",
  "code": "RES_002",
  "details": {
    "resource_type": "fact",
    "resource_id": "fact-uuid",
    "reason": "Resource is private"
  }
}
```

### RES_003 - Resource Already Exists
**HTTP Status:** 409 Conflict
**Description:** Resource already exists and cannot be created

```json
{
  "success": false,
  "error": "Resource already exists",
  "code": "RES_003",
  "details": {
    "resource_type": "user",
    "field": "email",
    "value": "user@example.com"
  }
}
```

### RES_004 - Resource Deleted
**HTTP Status:** 410 Gone
**Description:** Resource has been deleted

```json
{
  "success": false,
  "error": "Resource has been deleted",
  "code": "RES_004",
  "details": {
    "resource_type": "fact",
    "resource_id": "deleted-fact-uuid",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

## Business Logic Errors (BIZ_*)

### BIZ_001 - Duplicate Vote
**HTTP Status:** 409 Conflict
**Description:** User has already voted on this item

```json
{
  "success": false,
  "error": "You have already voted on this item",
  "code": "BIZ_001",
  "details": {
    "target_type": "fact",
    "target_id": "fact-uuid",
    "existing_vote": "fact"
  }
}
```

### BIZ_002 - Self Action Prohibited
**HTTP Status:** 400 Bad Request
**Description:** User cannot perform action on their own content

```json
{
  "success": false,
  "error": "Cannot vote on your own content",
  "code": "BIZ_002",
  "details": {
    "action": "vote",
    "target_type": "fact",
    "target_id": "fact-uuid"
  }
}
```

### BIZ_003 - Comment Depth Exceeded
**HTTP Status:** 400 Bad Request
**Description:** Comment nesting depth limit exceeded

```json
{
  "success": false,
  "error": "Comment nesting depth limit exceeded",
  "code": "BIZ_003",
  "details": {
    "max_depth": 2,
    "current_depth": 3
  }
}
```

### BIZ_004 - Rate Limit Exceeded
**HTTP Status:** 429 Too Many Requests
**Description:** User has exceeded rate limits

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": "BIZ_004",
  "details": {
    "limit": 100,
    "window": "1 hour",
    "reset_at": "2024-01-01T01:00:00Z"
  }
}
```

### BIZ_005 - Content Moderated
**HTTP Status:** 403 Forbidden
**Description:** Content is under moderation

```json
{
  "success": false,
  "error": "Content is under moderation review",
  "code": "BIZ_005",
  "details": {
    "content_type": "fact",
    "content_id": "fact-uuid",
    "moderation_status": "pending"
  }
}
```

## File Upload Errors (FILE_*)

### FILE_001 - File Too Large
**HTTP Status:** 413 Payload Too Large
**Description:** Uploaded file exceeds size limit

```json
{
  "success": false,
  "error": "File size exceeds limit",
  "code": "FILE_001",
  "details": {
    "file_size": 20971520,
    "max_size": 16777216,
    "max_size_mb": 16
  }
}
```

### FILE_002 - Invalid File Type
**HTTP Status:** 400 Bad Request
**Description:** File type is not allowed

```json
{
  "success": false,
  "error": "Invalid file type",
  "code": "FILE_002",
  "details": {
    "file_type": "application/exe",
    "allowed_types": ["image/jpeg", "image/png", "image/gif"]
  }
}
```

### FILE_003 - File Upload Failed
**HTTP Status:** 500 Internal Server Error
**Description:** File upload failed due to server error

```json
{
  "success": false,
  "error": "File upload failed",
  "code": "FILE_003",
  "details": {
    "reason": "Storage service unavailable"
  }
}
```

## Database Errors (DB_*)

### DB_001 - Database Connection Failed
**HTTP Status:** 500 Internal Server Error
**Description:** Cannot connect to database

```json
{
  "success": false,
  "error": "Database connection failed",
  "code": "DB_001"
}
```

### DB_002 - Database Constraint Violation
**HTTP Status:** 400 Bad Request
**Description:** Database constraint violated

```json
{
  "success": false,
  "error": "Database constraint violation",
  "code": "DB_002",
  "details": {
    "constraint": "unique_email",
    "field": "email",
    "value": "user@example.com"
  }
}
```

### DB_003 - Database Transaction Failed
**HTTP Status:** 500 Internal Server Error
**Description:** Database transaction failed

```json
{
  "success": false,
  "error": "Database transaction failed",
  "code": "DB_003",
  "details": {
    "operation": "bulk_user_update"
  }
}
```

## External Service Errors (EXT_*)

### EXT_001 - Email Service Unavailable
**HTTP Status:** 503 Service Unavailable
**Description:** Email service is temporarily unavailable

```json
{
  "success": false,
  "error": "Email service temporarily unavailable",
  "code": "EXT_001",
  "details": {
    "service": "SMTP",
    "retry_after": 300
  }
}
```

### EXT_002 - URL Validation Failed
**HTTP Status:** 400 Bad Request
**Description:** URL could not be validated or accessed

```json
{
  "success": false,
  "error": "URL validation failed",
  "code": "EXT_002",
  "details": {
    "url": "https://example.com/invalid",
    "reason": "URL not accessible",
    "status_code": 404
  }
}
```

## System Errors (SYS_*)

### SYS_001 - Internal Server Error
**HTTP Status:** 500 Internal Server Error
**Description:** Unexpected server error

```json
{
  "success": false,
  "error": "Internal server error",
  "code": "SYS_001",
  "details": {
    "error_id": "error-uuid-for-tracking"
  }
}
```

### SYS_002 - Service Unavailable
**HTTP Status:** 503 Service Unavailable
**Description:** Service is temporarily unavailable

```json
{
  "success": false,
  "error": "Service temporarily unavailable",
  "code": "SYS_002",
  "details": {
    "maintenance_mode": true,
    "estimated_duration": "30 minutes"
  }
}
```

### SYS_003 - Configuration Error
**HTTP Status:** 500 Internal Server Error
**Description:** System configuration error

```json
{
  "success": false,
  "error": "System configuration error",
  "code": "SYS_003",
  "details": {
    "component": "email_service",
    "missing_config": "SMTP_HOST"
  }
}
```

## Moderation Errors (MOD_*)

### MOD_001 - Report Already Exists
**HTTP Status:** 409 Conflict
**Description:** User has already reported this content

```json
{
  "success": false,
  "error": "You have already reported this content",
  "code": "MOD_001",
  "details": {
    "target_type": "fact",
    "target_id": "fact-uuid",
    "existing_report_id": "report-uuid"
  }
}
```

### MOD_002 - Cannot Report Own Content
**HTTP Status:** 400 Bad Request
**Description:** User cannot report their own content

```json
{
  "success": false,
  "error": "Cannot report your own content",
  "code": "MOD_002",
  "details": {
    "target_type": "comment",
    "target_id": "comment-uuid"
  }
}
```

### MOD_003 - Moderation Action Failed
**HTTP Status:** 500 Internal Server Error
**Description:** Moderation action could not be completed

```json
{
  "success": false,
  "error": "Moderation action failed",
  "code": "MOD_003",
  "details": {
    "action": "suspend_user",
    "target_id": "user-uuid",
    "reason": "Database transaction failed"
  }
}
```

## Admin Errors (ADM_*)

### ADM_001 - Admin Action Prohibited
**HTTP Status:** 403 Forbidden
**Description:** Admin action is not allowed

```json
{
  "success": false,
  "error": "Cannot perform action on admin account",
  "code": "ADM_001",
  "details": {
    "action": "suspend",
    "target_user_role": "admin"
  }
}
```

### ADM_002 - Bulk Action Partial Failure
**HTTP Status:** 207 Multi-Status
**Description:** Bulk action completed with some failures

```json
{
  "success": true,
  "error": "Bulk action completed with errors",
  "code": "ADM_002",
  "details": {
    "total": 10,
    "successful": 8,
    "failed": 2,
    "errors": [
      {
        "user_id": "user-uuid-1",
        "error": "User not found"
      },
      {
        "user_id": "user-uuid-2", 
        "error": "Cannot suspend admin user"
      }
    ]
  }
}
```

### ADM_003 - System Maintenance Required
**HTTP Status:** 503 Service Unavailable
**Description:** System maintenance is required

```json
{
  "success": false,
  "error": "System maintenance required",
  "code": "ADM_003",
  "details": {
    "maintenance_type": "database_cleanup",
    "estimated_duration": "15 minutes"
  }
}
```

## Error Handling Best Practices

### Client-Side Error Handling

```javascript
// Example error handling in JavaScript
async function handleApiCall() {
  try {
    const response = await fetch('/api/facts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: 'New fact' })
    });
    
    const data = await response.json();
    
    if (!data.success) {
      switch (data.code) {
        case 'AUTH_001':
          // Redirect to login
          window.location.href = '/login';
          break;
        case 'VAL_003':
          // Show validation error
          showValidationError(data.details.field, data.details.message);
          break;
        case 'BIZ_004':
          // Show rate limit message
          showRateLimitError(data.details.reset_at);
          break;
        default:
          // Show generic error
          showError(data.error);
      }
    }
  } catch (error) {
    // Handle network errors
    showError('Network error occurred');
  }
}
```

### Server-Side Error Logging

```python
# Example error logging in Python
import logging
from flask import jsonify

def handle_error(error_code, message, details=None, status_code=400):
    """Standard error response handler"""
    
    # Log error for monitoring
    logging.error(f"API Error {error_code}: {message}", extra={
        'error_code': error_code,
        'details': details,
        'status_code': status_code
    })
    
    response = {
        'success': False,
        'error': message,
        'code': error_code
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code
```

## Error Monitoring

### Recommended Monitoring

1. **Error Rate Tracking**: Monitor error rates by endpoint and error code
2. **Alert Thresholds**: Set up alerts for critical errors (5xx codes)
3. **Error Correlation**: Track errors by user, session, and time
4. **Performance Impact**: Monitor how errors affect response times

### Error Metrics

- **Error Rate**: Percentage of requests resulting in errors
- **Error Distribution**: Breakdown of errors by code and endpoint
- **Recovery Time**: Time to resolve system errors
- **User Impact**: Number of users affected by errors

---

*This error codes reference is maintained alongside the API documentation.*
*Last updated: 2024-01-01*
