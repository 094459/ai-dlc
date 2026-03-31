# Fact Checker Application - API Documentation

## Overview

The Fact Checker Application provides a comprehensive REST API for managing facts, user interactions, moderation, and administrative functions. This documentation covers all available endpoints, authentication requirements, request/response formats, and error handling.

## Base URL

```
Development: http://localhost:5000
Production: https://your-domain.com
```

## Authentication

The API uses session-based authentication with the following requirements:

### Authentication Types

1. **Public Endpoints** - No authentication required
2. **User Endpoints** - Requires valid user session
3. **Moderator Endpoints** - Requires moderator role
4. **Admin Endpoints** - Requires admin role

### Session Management

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "is_admin": false,
    "is_moderator": false
  }
}
```

## Error Handling

All API endpoints return consistent error responses:

### Error Response Format

```json
{
  "success": false,
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `500` - Internal Server Error

## API Endpoints

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "user_id": "user-uuid"
}
```

#### POST /auth/login
Authenticate user and create session.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "is_admin": false,
    "is_moderator": false
  }
}
```

#### POST /auth/logout
End user session.

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

#### GET /auth/session
Get current session information.

**Response:**
```json
{
  "authenticated": true,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "is_admin": false,
    "is_moderator": false
  }
}
```

### Fact Management Endpoints

#### GET /facts
Retrieve facts with optional filtering and pagination.

**Query Parameters:**
- `page` (int) - Page number (default: 1)
- `per_page` (int) - Items per page (default: 20, max: 100)
- `search` (string) - Search term
- `hashtag` (string) - Filter by hashtag
- `user_id` (string) - Filter by user
- `sort` (string) - Sort order: `newest`, `oldest`, `most_voted`

**Response:**
```json
{
  "success": true,
  "facts": [
    {
      "id": "fact-uuid",
      "content": "Fact content here",
      "user_id": "user-uuid",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "vote_counts": {
        "fact": 15,
        "fake": 3
      },
      "hashtags": ["#science", "#health"],
      "comment_count": 5
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### POST /facts
Create a new fact. **Requires authentication.**

**Request:**
```json
{
  "content": "This is a new fact about something important.",
  "resources": [
    {
      "url": "https://example.com/source",
      "title": "Source Title"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Fact created successfully",
  "fact": {
    "id": "fact-uuid",
    "content": "This is a new fact about something important.",
    "user_id": "user-uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "hashtags": ["#important"]
  }
}
```

#### GET /facts/{fact_id}
Retrieve a specific fact by ID.

**Response:**
```json
{
  "success": true,
  "fact": {
    "id": "fact-uuid",
    "content": "Fact content here",
    "user_id": "user-uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "vote_counts": {
      "fact": 15,
      "fake": 3
    },
    "hashtags": ["#science", "#health"],
    "resources": [
      {
        "id": "resource-uuid",
        "url": "https://example.com/source",
        "title": "Source Title"
      }
    ],
    "comments": [
      {
        "id": "comment-uuid",
        "content": "Comment content",
        "user_id": "user-uuid",
        "created_at": "2024-01-01T00:00:00Z",
        "vote_counts": {
          "upvotes": 5,
          "downvotes": 1
        }
      }
    ]
  }
}
```

#### PUT /facts/{fact_id}
Update a fact. **Requires authentication and ownership.**

**Request:**
```json
{
  "content": "Updated fact content"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Fact updated successfully",
  "fact": {
    "id": "fact-uuid",
    "content": "Updated fact content",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### DELETE /facts/{fact_id}
Delete a fact. **Requires authentication and ownership or moderator role.**

**Response:**
```json
{
  "success": true,
  "message": "Fact deleted successfully"
}
```

### Voting Endpoints

#### POST /voting/fact/{fact_id}
Vote on a fact. **Requires authentication.**

**Request:**
```json
{
  "vote_type": "fact"
}
```

**Valid vote types:** `fact`, `fake`

**Response:**
```json
{
  "success": true,
  "message": "Vote recorded successfully",
  "vote_counts": {
    "fact": 16,
    "fake": 3
  }
}
```

#### POST /voting/comment/{comment_id}
Vote on a comment. **Requires authentication.**

**Request:**
```json
{
  "vote_type": "upvote"
}
```

**Valid vote types:** `upvote`, `downvote`

**Response:**
```json
{
  "success": true,
  "message": "Vote recorded successfully",
  "vote_counts": {
    "upvotes": 6,
    "downvotes": 1
  }
}
```

### Comment Endpoints

#### GET /comments/fact/{fact_id}
Get comments for a specific fact.

**Query Parameters:**
- `page` (int) - Page number (default: 1)
- `per_page` (int) - Items per page (default: 20)
- `sort` (string) - Sort order: `newest`, `oldest`, `most_voted`

**Response:**
```json
{
  "success": true,
  "comments": [
    {
      "id": "comment-uuid",
      "content": "This is a comment",
      "user_id": "user-uuid",
      "fact_id": "fact-uuid",
      "parent_id": null,
      "created_at": "2024-01-01T00:00:00Z",
      "vote_counts": {
        "upvotes": 5,
        "downvotes": 1
      },
      "replies": [
        {
          "id": "reply-uuid",
          "content": "This is a reply",
          "user_id": "user-uuid",
          "parent_id": "comment-uuid",
          "created_at": "2024-01-01T00:00:00Z"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "pages": 3
  }
}
```

#### POST /comments
Create a new comment. **Requires authentication.**

**Request:**
```json
{
  "content": "This is my comment on the fact",
  "fact_id": "fact-uuid",
  "parent_id": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "Comment created successfully",
  "comment": {
    "id": "comment-uuid",
    "content": "This is my comment on the fact",
    "user_id": "user-uuid",
    "fact_id": "fact-uuid",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### PUT /comments/{comment_id}
Update a comment. **Requires authentication and ownership.**

**Request:**
```json
{
  "content": "Updated comment content"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Comment updated successfully",
  "comment": {
    "id": "comment-uuid",
    "content": "Updated comment content",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### DELETE /comments/{comment_id}
Delete a comment. **Requires authentication and ownership or moderator role.**

**Response:**
```json
{
  "success": true,
  "message": "Comment deleted successfully"
}
```

### User Profile Endpoints

#### GET /profile/{user_id}
Get user profile information.

**Response:**
```json
{
  "success": true,
  "profile": {
    "user_id": "user-uuid",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "fact_count": 25,
    "comment_count": 150,
    "reputation_score": 85
  }
}
```

#### PUT /profile
Update current user's profile. **Requires authentication.**

**Request:**
```json
{
  "bio": "Updated bio information",
  "preferences": {
    "email_notifications": true,
    "theme": "dark"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

### Notification Endpoints

#### GET /notifications
Get user notifications. **Requires authentication.**

**Query Parameters:**
- `unread_only` (boolean) - Show only unread notifications
- `type` (string) - Filter by notification type
- `page` (int) - Page number

**Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "notification-uuid",
      "type": "comment_reply",
      "title": "New reply to your comment",
      "message": "Someone replied to your comment on a fact",
      "is_read": false,
      "created_at": "2024-01-01T00:00:00Z",
      "data": {
        "fact_id": "fact-uuid",
        "comment_id": "comment-uuid"
      }
    }
  ],
  "unread_count": 5
}
```

#### PUT /notifications/{notification_id}/read
Mark notification as read. **Requires authentication.**

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

#### PUT /notifications/read-all
Mark all notifications as read. **Requires authentication.**

**Response:**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

### Report Endpoints

#### POST /reports
Submit a report. **Requires authentication.**

**Request:**
```json
{
  "target_type": "fact",
  "target_id": "fact-uuid",
  "reason": "misinformation",
  "description": "This fact contains false information"
}
```

**Valid target types:** `fact`, `comment`, `user`
**Valid reasons:** `spam`, `misinformation`, `harassment`, `inappropriate`, `other`

**Response:**
```json
{
  "success": true,
  "message": "Report submitted successfully",
  "report_id": "report-uuid"
}
```

### Analytics Endpoints

#### GET /analytics/dashboard
Get analytics dashboard data. **Requires admin role.**

**Query Parameters:**
- `period` (string) - Time period: `day`, `week`, `month`, `year`
- `start_date` (string) - Start date (ISO format)
- `end_date` (string) - End date (ISO format)

**Response:**
```json
{
  "success": true,
  "analytics": {
    "user_metrics": {
      "total_users": 1000,
      "active_users": 250,
      "new_users": 15
    },
    "content_metrics": {
      "total_facts": 500,
      "total_comments": 2000,
      "total_votes": 5000
    },
    "engagement_metrics": {
      "avg_comments_per_fact": 4.0,
      "avg_votes_per_fact": 10.0,
      "user_retention_rate": 0.75
    }
  }
}
```

### Moderation Endpoints

#### GET /moderation/queue
Get moderation queue. **Requires moderator role.**

**Query Parameters:**
- `status` (string) - Filter by status: `pending`, `resolved`, `dismissed`
- `type` (string) - Filter by type: `fact`, `comment`, `user`
- `priority` (string) - Filter by priority: `low`, `medium`, `high`, `critical`

**Response:**
```json
{
  "success": true,
  "reports": [
    {
      "id": "report-uuid",
      "target_type": "fact",
      "target_id": "fact-uuid",
      "reason": "misinformation",
      "description": "Report description",
      "status": "pending",
      "priority": "high",
      "created_at": "2024-01-01T00:00:00Z",
      "reporter_id": "user-uuid"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50
  }
}
```

#### POST /moderation/action
Take moderation action. **Requires moderator role.**

**Request:**
```json
{
  "report_id": "report-uuid",
  "action": "remove_content",
  "reason": "Content violates community guidelines",
  "notify_user": true
}
```

**Valid actions:** `dismiss`, `warn_user`, `remove_content`, `suspend_user`, `ban_user`

**Response:**
```json
{
  "success": true,
  "message": "Moderation action completed successfully",
  "action_id": "action-uuid"
}
```

### Admin Endpoints

#### GET /admin/dashboard
Get admin dashboard overview. **Requires admin role.**

**Response:**
```json
{
  "success": true,
  "dashboard": {
    "overview": {
      "total_users": 1000,
      "total_facts": 500,
      "total_comments": 2000,
      "active_users_week": 250
    },
    "moderation": {
      "pending_reports": 15,
      "reports_today": 5,
      "moderation_actions_today": 8
    },
    "system_health": {
      "status": "healthy",
      "uptime": "99.9%",
      "response_time": "150ms"
    }
  }
}
```

#### GET /admin/users
Get user management data. **Requires admin role.**

**Query Parameters:**
- `search` (string) - Search users
- `status` (string) - Filter by status: `active`, `suspended`, `banned`
- `role` (string) - Filter by role: `user`, `moderator`, `admin`

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": "user-uuid",
      "email": "user@example.com",
      "is_active": true,
      "is_suspended": false,
      "is_banned": false,
      "is_admin": false,
      "is_moderator": false,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### POST /admin/users/bulk-action
Perform bulk user actions. **Requires admin role.**

**Request:**
```json
{
  "user_ids": ["user-uuid-1", "user-uuid-2"],
  "action": "suspend",
  "reason": "Violation of terms of service",
  "duration_days": 7
}
```

**Valid actions:** `activate`, `suspend`, `ban`, `promote_moderator`, `demote_moderator`

**Response:**
```json
{
  "success": true,
  "message": "Bulk action completed",
  "results": {
    "successful": 2,
    "failed": 0,
    "errors": []
  }
}
```

#### GET /admin/system/health
Get system health status. **Requires admin role.**

**Response:**
```json
{
  "success": true,
  "health": {
    "database": {
      "status": "healthy",
      "response_time": "5ms",
      "connections": 10
    },
    "memory": {
      "status": "healthy",
      "usage": "45%",
      "available": "2.1GB"
    },
    "disk": {
      "status": "warning",
      "usage": "85%",
      "available": "500MB"
    }
  }
}
```

### UI Framework Endpoints

#### GET /ui/components
Get available UI components.

**Response:**
```json
{
  "success": true,
  "components": [
    {
      "name": "button",
      "variants": ["primary", "secondary", "success", "danger"],
      "sizes": ["sm", "md", "lg"],
      "properties": ["disabled", "loading"]
    },
    {
      "name": "card",
      "variants": ["default", "bordered", "elevated"],
      "properties": ["header", "footer", "image"]
    }
  ]
}
```

#### POST /ui/render-component
Render a UI component with specified properties.

**Request:**
```json
{
  "component": "button",
  "variant": "primary",
  "size": "md",
  "properties": {
    "text": "Click Me",
    "disabled": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "html": "<button class=\"btn btn-primary btn-md\">Click Me</button>",
  "css_classes": ["btn", "btn-primary", "btn-md"]
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Public endpoints**: 100 requests per minute per IP
- **Authenticated endpoints**: 1000 requests per minute per user
- **Admin endpoints**: 5000 requests per minute per admin

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Webhooks

The application supports webhooks for real-time notifications:

### Available Events

- `fact.created` - New fact submitted
- `fact.voted` - Fact received a vote
- `comment.created` - New comment posted
- `report.submitted` - New report filed
- `moderation.action` - Moderation action taken
- `user.registered` - New user registered

### Webhook Payload Format

```json
{
  "event": "fact.created",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "fact_id": "fact-uuid",
    "user_id": "user-uuid",
    "content": "Fact content"
  }
}
```

## SDKs and Libraries

### JavaScript SDK

```javascript
import FactCheckerAPI from 'factchecker-js-sdk';

const api = new FactCheckerAPI({
  baseURL: 'https://api.factchecker.com',
  apiKey: 'your-api-key'
});

// Get facts
const facts = await api.facts.list({ page: 1, per_page: 20 });

// Create a fact
const newFact = await api.facts.create({
  content: 'This is a new fact'
});

// Vote on a fact
await api.voting.voteOnFact('fact-uuid', 'fact');
```

### Python SDK

```python
from factchecker_sdk import FactCheckerClient

client = FactCheckerClient(
    base_url='https://api.factchecker.com',
    api_key='your-api-key'
)

# Get facts
facts = client.facts.list(page=1, per_page=20)

# Create a fact
new_fact = client.facts.create(content='This is a new fact')

# Vote on a fact
client.voting.vote_on_fact('fact-uuid', 'fact')
```

## Testing

### Test Environment

```
Base URL: https://api-test.factchecker.com
```

### Test Credentials

```
Admin User:
Email: admin@test.factchecker.com
Password: TestAdmin123!

Moderator User:
Email: moderator@test.factchecker.com
Password: TestMod123!

Regular User:
Email: user@test.factchecker.com
Password: TestUser123!
```

## Support

For API support and questions:

- **Documentation**: https://docs.factchecker.com
- **Support Email**: api-support@factchecker.com
- **GitHub Issues**: https://github.com/factchecker/api/issues
- **Status Page**: https://status.factchecker.com

## Changelog

### Version 1.0.0 (2024-01-01)
- Initial API release
- Authentication and user management
- Fact and comment management
- Voting system
- Moderation tools
- Analytics dashboard
- Admin panel
- UI framework integration

---

*Last updated: 2024-01-01*
*API Version: 1.0.0*
