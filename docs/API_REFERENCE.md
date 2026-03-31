# Fact Checker Application - Technical API Reference

## Overview

This document provides detailed technical information about the Fact Checker Application's API endpoints, including actual implementation details, route mappings, and service integrations.

## Application Architecture

### Component Structure
```
app/
├── components/           # Modular components
│   ├── auth/            # Authentication & session management
│   ├── profile/         # User profile management
│   ├── fact/            # Fact content management
│   ├── comment/         # Comment system
│   ├── voting/          # Voting functionality
│   ├── report/          # Content reporting
│   ├── moderation/      # Moderation tools
│   ├── notification/    # Notification system
│   ├── analytics/       # Analytics & metrics
│   └── ui/              # UI framework components
├── routes/              # Main application routes
│   ├── admin_routes.py  # Admin dashboard routes
│   └── admin_api_routes.py # Admin API endpoints
├── services/            # Business logic services
├── models/              # Database models
└── helpers/             # Utility functions
```

### Service Layer Architecture
```
Services:
├── AdminDashboardService     # Dashboard data aggregation
├── AdminIntegrationService   # Cross-component integration
├── SystemConfigurationService # System settings management
├── UserManagementService     # User account operations
├── SystemHealthService       # System monitoring
└── Component Services        # Individual component services
```

## Authentication & Authorization

### Session-Based Authentication
The application uses Flask sessions for authentication with the following decorators:

```python
@login_required          # Requires valid user session
@admin_required         # Requires admin role
@moderator_required     # Requires moderator role
```

### Role Hierarchy
```
Admin > Moderator > User > Anonymous
```

## Detailed Endpoint Documentation

### Authentication Component (`/auth`)

#### Routes Implementation
```python
# app/components/auth/routes.py
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/logout', methods=['POST'])
@auth_bp.route('/session', methods=['GET'])
```

#### Service Integration
- **AuthenticationService**: User login/logout, session management
- **SessionValidationService**: Session validation and security
- **PasswordService**: Password hashing and validation

### Fact Management Component (`/facts`)

#### Routes Implementation
```python
# app/components/fact/routes.py
fact_bp = Blueprint('fact', __name__, url_prefix='/facts')

@fact_bp.route('/', methods=['GET', 'POST'])
@fact_bp.route('/<fact_id>', methods=['GET', 'PUT', 'DELETE'])
@fact_bp.route('/<fact_id>/edit', methods=['GET', 'POST'])
@fact_bp.route('/search', methods=['GET'])
```

#### Service Integration
- **FactService**: CRUD operations, search, validation
- **ResourceService**: URL validation, image processing
- **HashtagService**: Hashtag extraction and management

### Voting Component (`/voting`)

#### Routes Implementation
```python
# app/components/voting/routes.py
voting_bp = Blueprint('voting', __name__, url_prefix='/voting')

@voting_bp.route('/fact/<fact_id>', methods=['POST'])
@voting_bp.route('/comment/<comment_id>', methods=['POST'])
@voting_bp.route('/stats/<target_type>/<target_id>', methods=['GET'])
```

#### Service Integration
- **VotingService**: Vote recording, statistics calculation
- **VoteValidationService**: Duplicate vote prevention

### Comment Component (`/comments`)

#### Routes Implementation
```python
# app/components/comment/routes.py
comment_bp = Blueprint('comment', __name__, url_prefix='/comments')

@comment_bp.route('/', methods=['POST'])
@comment_bp.route('/<comment_id>', methods=['GET', 'PUT', 'DELETE'])
@comment_bp.route('/fact/<fact_id>', methods=['GET'])
@comment_bp.route('/<comment_id>/reply', methods=['POST'])
```

#### Service Integration
- **CommentService**: Comment CRUD, threading, validation
- **ThreadService**: Comment hierarchy management

### User Profile Component (`/profile`)

#### Routes Implementation
```python
# app/components/profile/routes.py
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@profile_bp.route('/<user_id>', methods=['GET'])
@profile_bp.route('/settings', methods=['GET', 'POST'])
@profile_bp.route('/upload-photo', methods=['POST'])
```

#### Service Integration
- **ProfileService**: Profile management, photo upload
- **UserPreferencesService**: User settings and preferences

### Notification Component (`/notifications`)

#### Routes Implementation
```python
# app/components/notification/routes.py
notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')

@notification_bp.route('/', methods=['GET'])
@notification_bp.route('/<notification_id>/read', methods=['PUT'])
@notification_bp.route('/read-all', methods=['PUT'])
@notification_bp.route('/preferences', methods=['GET', 'POST'])
```

#### Service Integration
- **NotificationService**: Notification CRUD, delivery
- **EmailService**: Email queue management, template processing

### Report Component (`/reports`)

#### Routes Implementation
```python
# app/components/report/routes.py
report_bp = Blueprint('report', __name__, url_prefix='/reports')

@report_bp.route('/', methods=['POST'])
@report_bp.route('/<report_id>', methods=['GET'])
@report_bp.route('/my-reports', methods=['GET'])
```

#### Service Integration
- **ReportService**: Report creation, categorization, priority assignment

### Moderation Component (`/moderation`)

#### Routes Implementation
```python
# app/components/moderation/routes.py
moderation_bp = Blueprint('moderation', __name__, url_prefix='/moderation')

@moderation_bp.route('/dashboard', methods=['GET'])
@moderation_bp.route('/queue', methods=['GET'])
@moderation_bp.route('/action', methods=['POST'])
@moderation_bp.route('/history', methods=['GET'])
```

#### Service Integration
- **ModerationService**: Moderation actions, workflow management
- **ModerationDashboardService**: Queue management, statistics

### Analytics Component (`/analytics`)

#### Routes Implementation
```python
# app/components/analytics/routes.py
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/dashboard/<dashboard_type>', methods=['GET'])
@analytics_bp.route('/events', methods=['GET', 'POST'])
@analytics_bp.route('/metrics', methods=['GET'])
@analytics_bp.route('/export', methods=['POST'])
```

#### Service Integration
- **AnalyticsService**: Event tracking, data collection
- **MetricsCalculationService**: Metrics aggregation, reporting
- **DashboardService**: Dashboard configuration, data visualization
- **UserEngagementService**: User activity analysis

### UI Framework Component (`/ui`)

#### Routes Implementation
```python
# app/components/ui/routes.py
ui_bp = Blueprint('ui', __name__, url_prefix='/ui')

@ui_bp.route('/showcase', methods=['GET'])
@ui_bp.route('/components', methods=['GET'])
@ui_bp.route('/render-component', methods=['POST'])
@ui_bp.route('/theme', methods=['GET', 'POST'])
```

#### Service Integration
- **UIService**: Component rendering, theme management
- **ThemeService**: Theme switching, user preferences

### Admin Dashboard (`/admin`)

#### Main Routes Implementation
```python
# app/routes/admin_routes.py
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@admin_bp.route('/users', methods=['GET'])
@admin_bp.route('/users/<user_id>', methods=['GET', 'POST'])
@admin_bp.route('/configuration', methods=['GET', 'POST'])
@admin_bp.route('/health', methods=['GET'])
@admin_bp.route('/reports', methods=['GET'])
```

#### API Routes Implementation
```python
# app/routes/admin_api_routes.py
admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')

@admin_api_bp.route('/dashboard/widgets', methods=['GET'])
@admin_api_bp.route('/analytics/summary', methods=['GET'])
@admin_api_bp.route('/moderation/queue', methods=['GET'])
@admin_api_bp.route('/users/bulk-action', methods=['POST'])
@admin_api_bp.route('/system/maintenance', methods=['POST'])
```

#### Service Integration
- **AdminDashboardService**: Dashboard data aggregation
- **AdminIntegrationService**: Cross-component integration
- **UserManagementService**: Bulk user operations
- **SystemHealthService**: System monitoring
- **SystemConfigurationService**: Settings management

## Database Models

### Core Models
```python
# User Management
User                    # User accounts and authentication
UserProfile            # Extended user information
UserPreferences        # User settings and preferences

# Content Management
Fact                   # User-submitted facts
Comment                # Comments on facts
FactResource           # URLs and images attached to facts
FactHashtag           # Hashtag associations

# Interaction
FactVote              # Votes on facts (fact/fake)
CommentVote           # Votes on comments (up/down)
CommentThread         # Comment threading structure

# Moderation
Report                # Content and user reports
ModerationAction      # Actions taken by moderators
ModerationQueue       # Report processing queue

# Notifications
Notification          # User notifications
NotificationQueue     # Email delivery queue
NotificationTemplate  # Email templates

# Analytics
AnalyticsEvent        # Event tracking data
MetricsAggregation    # Calculated metrics
DashboardConfiguration # Dashboard settings
UserEngagementMetrics # User activity metrics

# Admin
AdminActivity         # Admin action logging
SystemHealth          # System health monitoring
SystemConfiguration  # Application settings
AdminDashboardWidget  # Dashboard widget configuration
```

### Model Relationships
```python
# User relationships
User -> UserProfile (1:1)
User -> Fact (1:many)
User -> Comment (1:many)
User -> Report (1:many)

# Content relationships
Fact -> Comment (1:many)
Fact -> FactVote (1:many)
Fact -> FactResource (1:many)
Fact -> FactHashtag (1:many)

# Comment relationships
Comment -> CommentVote (1:many)
Comment -> Comment (parent-child)

# Moderation relationships
Report -> ModerationAction (1:many)
User -> ModerationAction (moderator)
```

## Service Layer Details

### AdminDashboardService
```python
class AdminDashboardService:
    def get_dashboard_overview(admin_user_id: str) -> Dict
    def get_user_management_summary(admin_user_id: str) -> Dict
    def get_content_management_summary(admin_user_id: str) -> Dict
    def get_system_health_summary() -> Dict
    def _calculate_percentage_change(old_value: int, new_value: int) -> float
    def _get_recent_admin_activities(limit: int = 10) -> List
    def _get_system_alerts() -> List
```

### AdminIntegrationService
```python
class AdminIntegrationService:
    def get_integrated_dashboard_data(admin_user_id: str) -> Dict
    def get_analytics_integration_data(admin_user_id: str) -> Dict
    def get_moderation_integration_data(admin_user_id: str) -> Dict
    def get_notification_integration_data(admin_user_id: str) -> Dict
    def get_security_integration_data(admin_user_id: str) -> Dict
    def send_admin_notification(admin_user_id: str, title: str, message: str) -> bool
    def trigger_security_alert(admin_user_id: str, alert_type: str) -> bool
```

### Component Services
Each component includes specialized services:

```python
# Authentication
AuthenticationService, SessionValidationService, PasswordService

# Content Management
FactService, CommentService, ResourceService, HashtagService

# Interaction
VotingService, ThreadService

# Moderation
ModerationService, ModerationDashboardService, ReportService

# Notifications
NotificationService, EmailService

# Analytics
AnalyticsService, MetricsCalculationService, DashboardService, UserEngagementService

# UI Framework
UIService, ThemeService
```

## Error Handling

### Global Error Handlers
```python
@app.errorhandler(400)  # Bad Request
@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # Not Found
@app.errorhandler(422)  # Unprocessable Entity
@app.errorhandler(500)  # Internal Server Error
```

### Service-Level Error Handling
All services implement consistent error handling:

```python
try:
    # Service operation
    result = perform_operation()
    return {'success': True, 'data': result}
except ValidationError as e:
    return {'success': False, 'error': str(e), 'code': 'VALIDATION_ERROR'}
except PermissionError as e:
    return {'success': False, 'error': str(e), 'code': 'PERMISSION_DENIED'}
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return {'success': False, 'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}
```

## Security Implementation

### Input Validation
- **Flask-WTF**: Form validation and CSRF protection
- **Custom validators**: Content sanitization, URL validation
- **SQL injection prevention**: SQLAlchemy ORM usage

### Authentication Security
- **Password hashing**: bcrypt with salt
- **Session management**: Secure session cookies
- **Role-based access**: Decorator-based authorization

### Content Security
- **XSS prevention**: Content sanitization
- **File upload security**: Type validation, size limits
- **Rate limiting**: Per-endpoint request limits

## Performance Considerations

### Database Optimization
- **Indexes**: Strategic indexing on frequently queried fields
- **Query optimization**: Efficient joins and filtering
- **Connection pooling**: SQLAlchemy connection management

### Caching Strategy
- **Session caching**: User session data
- **Query result caching**: Frequently accessed data
- **Template caching**: Rendered template fragments

### Monitoring
- **System health checks**: Database, memory, disk usage
- **Performance metrics**: Response times, error rates
- **Analytics tracking**: User behavior, system usage

## Testing Strategy

### Test Coverage
- **Unit tests**: 259 comprehensive test cases
- **Integration tests**: Cross-component functionality
- **API tests**: Endpoint validation and error handling

### Test Infrastructure
- **PyTest framework**: Test runner and fixtures
- **Mock objects**: External dependency simulation
- **Test database**: Isolated test environment

## Deployment Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///factchecker.db
DATABASE_URL_TEST=sqlite:///:memory:

# Security
SECRET_KEY=your-secret-key-here
WTF_CSRF_SECRET_KEY=your-csrf-key-here

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password

# Features
ENABLE_ANALYTICS=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_FILE_UPLOADS=true

# Performance
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads/
```

### Production Considerations
- **WSGI server**: Gunicorn or uWSGI
- **Reverse proxy**: Nginx for static files and load balancing
- **Database**: PostgreSQL for production
- **Monitoring**: Application performance monitoring
- **Logging**: Structured logging with log rotation

---

*This technical reference is automatically generated from the application codebase.*
*Last updated: 2024-01-01*
