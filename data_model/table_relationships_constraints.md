# Table Relationships and Constraints Documentation

## Overview
This document provides a comprehensive reference for all table relationships, foreign key constraints, unique constraints, and check constraints in the Fact Checker application database schema.

## Table Dependency Order
Tables must be created in this order to satisfy foreign key dependencies:

1. **users** (no dependencies)
2. **user_sessions** (depends on users)
3. **user_profiles** (depends on users)
4. **profile_photos** (depends on users)
5. **facts** (depends on users)
6. **fact_edit_history** (depends on facts)
7. **hashtags** (no dependencies)
8. **fact_hashtags** (depends on facts, hashtags)
9. **fact_resources** (depends on facts)
10. **resource_validation** (depends on fact_resources)
11. **comments** (depends on facts, users, comments)
12. **comment_edit_history** (depends on comments)
13. **comment_threads** (depends on facts, comments)
14. **fact_votes** (depends on facts, users)
15. **comment_votes** (depends on comments, users)
16. **vote_statistics** (no foreign key dependencies)
17. **reports** (depends on users)
18. **moderation_actions** (depends on users, reports)
19. **user_moderation_history** (depends on users, moderation_actions)
20. **notifications** (depends on users)
21. **user_notification_preferences** (depends on users)
22. **analytics_events** (depends on users, user_sessions)
23. **audit_logs** (depends on users)
24. **system_configuration** (depends on users)

## Foreign Key Relationships

### User Management Relationships

#### user_sessions
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationship**: Many sessions belong to one user
- **Cascade**: RESTRICT (preserve user if sessions exist)
- **Business Rule**: Sessions are cleaned up periodically

#### user_profiles
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationship**: One profile belongs to one user
- **Cascade**: RESTRICT (preserve user if profile exists)
- **Business Rule**: Profile is optional but recommended

#### profile_photos
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationship**: Many photos belong to one user
- **Cascade**: RESTRICT (preserve user if photos exist)
- **Business Rule**: Only one photo active at a time

### Content Management Relationships

#### facts
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationship**: Many facts belong to one user
- **Cascade**: RESTRICT (preserve user if facts exist)
- **Business Rule**: User owns and can edit their facts

#### fact_edit_history
```sql
FOREIGN KEY (fact_id) REFERENCES facts(id)
```
- **Relationship**: Many edit records belong to one fact
- **Cascade**: RESTRICT (preserve fact if history exists)
- **Business Rule**: Complete audit trail maintained

#### hashtags
- **No foreign key relationships** (independent entity)

#### fact_hashtags
```sql
FOREIGN KEY (fact_id) REFERENCES facts(id)
FOREIGN KEY (hashtag_id) REFERENCES hashtags(id)
```
- **Relationship**: Junction table for many-to-many relationship
- **Cascade**: RESTRICT (preserve both entities if junction exists)
- **Business Rule**: Hashtags automatically extracted from content

#### fact_resources
```sql
FOREIGN KEY (fact_id) REFERENCES facts(id)
```
- **Relationship**: Many resources belong to one fact
- **Cascade**: RESTRICT (preserve fact if resources exist)
- **Business Rule**: Maximum 5 resources per fact

#### resource_validation
```sql
FOREIGN KEY (resource_id) REFERENCES fact_resources(id)
```
- **Relationship**: One validation record per resource
- **Cascade**: RESTRICT (preserve resource if validation exists)
- **Business Rule**: Validation occurs asynchronously

### Comment System Relationships

#### comments
```sql
FOREIGN KEY (fact_id) REFERENCES facts(id)
FOREIGN KEY (user_id) REFERENCES users(id)
FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
```
- **Relationships**: 
  - Many comments belong to one fact
  - Many comments belong to one user
  - Many comments can reply to one parent comment (self-referencing)
- **Cascade**: RESTRICT on all relationships
- **Business Rule**: Maximum 3-level nesting (0, 1, 2)

#### comment_edit_history
```sql
FOREIGN KEY (comment_id) REFERENCES comments(id)
```
- **Relationship**: Many edit records belong to one comment
- **Cascade**: RESTRICT (preserve comment if history exists)
- **Business Rule**: Complete audit trail maintained

#### comment_threads
```sql
FOREIGN KEY (fact_id) REFERENCES facts(id)
FOREIGN KEY (root_comment_id) REFERENCES comments(id)
```
- **Relationships**: 
  - Many threads belong to one fact
  - One thread belongs to one root comment
- **Cascade**: RESTRICT on both relationships
- **Business Rule**: Only created for top-level comments

### Voting System Relationships

#### fact_votes
```sql
FOREIGN KEY (fact_id) REFERENCES facts(id)
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationships**: 
  - Many votes belong to one fact
  - Many votes belong to one user
- **Cascade**: RESTRICT on both relationships
- **Business Rule**: Users cannot vote on their own facts

#### comment_votes
```sql
FOREIGN KEY (comment_id) REFERENCES comments(id)
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationships**: 
  - Many votes belong to one comment
  - Many votes belong to one user
- **Cascade**: RESTRICT on both relationships
- **Business Rule**: Users cannot vote on their own comments

#### vote_statistics
- **No foreign key relationships** (polymorphic references via content_type + content_id)

### Moderation System Relationships

#### reports
```sql
FOREIGN KEY (reporter_user_id) REFERENCES users(id)
FOREIGN KEY (assigned_moderator_id) REFERENCES users(id)
```
- **Relationships**: 
  - Many reports belong to one reporter
  - Many reports can be assigned to one moderator
- **Cascade**: RESTRICT on both relationships
- **Business Rule**: Only moderators can be assigned reports

#### moderation_actions
```sql
FOREIGN KEY (moderator_id) REFERENCES users(id)
FOREIGN KEY (related_report_id) REFERENCES reports(id)
```
- **Relationships**: 
  - Many actions belong to one moderator
  - Many actions can relate to one report
- **Cascade**: RESTRICT on both relationships
- **Business Rule**: Actions can be taken without reports

#### user_moderation_history
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
FOREIGN KEY (last_moderation_action_id) REFERENCES moderation_actions(id)
```
- **Relationships**: 
  - One history record belongs to one user
  - One history record references one last action
- **Cascade**: RESTRICT on both relationships
- **Business Rule**: Created when user first receives moderation action

### System Infrastructure Relationships

#### notifications
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationship**: Many notifications belong to one user
- **Cascade**: RESTRICT (preserve user if notifications exist)
- **Business Rule**: Notifications sent for various activities

#### user_notification_preferences
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationship**: Many preferences belong to one user
- **Cascade**: RESTRICT (preserve user if preferences exist)
- **Business Rule**: Default preferences created on registration

#### analytics_events
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
FOREIGN KEY (session_id) REFERENCES user_sessions(id)
```
- **Relationships**: 
  - Many events belong to one user (nullable)
  - Many events belong to one session (nullable)
- **Cascade**: RESTRICT on both relationships
- **Business Rule**: Anonymous events allowed (user_id = NULL)

#### audit_logs
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
```
- **Relationship**: Many log entries belong to one user (nullable)
- **Cascade**: RESTRICT (preserve user if logs exist)
- **Business Rule**: System actions allowed (user_id = NULL)

#### system_configuration
```sql
FOREIGN KEY (updated_by) REFERENCES users(id)
```
- **Relationship**: Many config changes belong to one admin user (nullable)
- **Cascade**: RESTRICT (preserve user if config exists)
- **Business Rule**: Tracks who made configuration changes

## Unique Constraints

### Single Column Unique Constraints
```sql
-- User uniqueness
users.email UNIQUE

-- Session uniqueness
user_sessions.session_token UNIQUE

-- Hashtag uniqueness
hashtags.tag UNIQUE

-- Configuration uniqueness
system_configuration.config_key UNIQUE
```

### Multi-Column Unique Constraints
```sql
-- Profile uniqueness (one profile per user)
user_profiles(user_id) UNIQUE

-- Voting uniqueness (one vote per user per content)
fact_votes(fact_id, user_id) UNIQUE
comment_votes(comment_id, user_id) UNIQUE

-- Junction table uniqueness
fact_hashtags(fact_id, hashtag_id) UNIQUE

-- Thread uniqueness (one thread per root comment per fact)
comment_threads(fact_id, root_comment_id) UNIQUE

-- Statistics uniqueness (one record per content item)
vote_statistics(content_type, content_id) UNIQUE

-- Preference uniqueness (one preference per user per type)
user_notification_preferences(user_id, notification_type) UNIQUE

-- Moderation history uniqueness (one record per user)
user_moderation_history(user_id) UNIQUE
```

## Check Constraints

### Boolean Field Constraints
All boolean fields use INTEGER(1) with CHECK constraints for cross-database compatibility:
```sql
-- Standard boolean pattern
is_active INTEGER CHECK (is_active IN (0, 1))
is_deleted INTEGER CHECK (is_deleted IN (0, 1))
is_admin INTEGER CHECK (is_admin IN (0, 1))
is_moderator INTEGER CHECK (is_moderator IN (0, 1))
-- ... and many more
```

### Enumeration Constraints

#### Vote Types
```sql
-- Fact voting
fact_votes.vote_type CHECK (vote_type IN ('fact', 'fake'))

-- Comment voting
comment_votes.vote_type CHECK (vote_type IN ('upvote', 'downvote'))
```

#### Content Types
```sql
-- Resource types
fact_resources.resource_type CHECK (resource_type IN ('url', 'image'))

-- Report content types
reports.reported_content_type CHECK (reported_content_type IN ('fact', 'comment'))

-- Vote statistics content types
vote_statistics.content_type CHECK (content_type IN ('fact', 'comment'))

-- Analytics event categories
analytics_events.event_category CHECK (event_category IN ('user_action', 'content_interaction', 'system_event', 'moderation_event'))

-- Notification types
notifications.notification_type CHECK (notification_type IN ('comment_reply', 'fact_vote', 'comment_vote', 'fact_comment', 'moderation_action', 'system_announcement'))
user_notification_preferences.notification_type CHECK (notification_type IN ('comment_reply', 'fact_vote', 'comment_vote', 'fact_comment', 'moderation_action', 'system_announcement'))
```

#### Status and Priority Fields
```sql
-- Report status
reports.status CHECK (status IN ('pending', 'under_review', 'resolved', 'dismissed'))

-- Report priority
reports.priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))

-- Report categories
reports.report_category CHECK (report_category IN ('spam', 'harassment', 'misinformation', 'inappropriate', 'copyright', 'other'))

-- Moderation action types
moderation_actions.action_type CHECK (action_type IN ('content_removal', 'content_restoration', 'user_warning', 'user_suspension', 'user_ban', 'report_dismissal'))

-- Moderation target types
moderation_actions.target_type CHECK (target_type IN ('fact', 'comment', 'user', 'report'))

-- User moderation status
user_moderation_history.moderation_status CHECK (moderation_status IN ('good_standing', 'warned', 'suspended', 'banned'))

-- Resource validation status
resource_validation.validation_status CHECK (validation_status IN ('pending', 'valid', 'invalid', 'broken'))

-- Notification delivery methods
notifications.delivery_method CHECK (delivery_method IN ('in_app', 'email', 'both'))

-- Notification priorities
notifications.priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))

-- Notification frequencies
user_notification_preferences.frequency CHECK (frequency IN ('immediate', 'hourly', 'daily', 'weekly', 'disabled'))

-- Audit log severity
audit_logs.severity CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical'))

-- System configuration types
system_configuration.config_type CHECK (config_type IN ('string', 'integer', 'boolean', 'json'))
```

#### Range Constraints
```sql
-- Comment nesting level (0, 1, 2 maximum)
comments.nesting_level CHECK (nesting_level >= 0 AND nesting_level <= 2)

-- User risk score (0-100 range)
user_moderation_history.risk_score CHECK (risk_score >= 0 AND risk_score <= 100)
```

## Constraint Naming Conventions

### Foreign Key Constraints
- Pattern: `fk_{table}_{referenced_table}_{column}`
- Example: `fk_user_sessions_users_user_id`

### Unique Constraints
- Pattern: `uk_{table}_{column(s)}`
- Example: `uk_users_email`, `uk_fact_votes_fact_user`

### Check Constraints
- Pattern: `ck_{table}_{column}_{constraint_type}`
- Example: `ck_users_is_active_boolean`, `ck_reports_status_enum`

## Referential Integrity Rules

### Delete Rules
- **RESTRICT**: Default for all foreign keys to prevent accidental data loss
- **Soft Delete Pattern**: Used instead of CASCADE DELETE to preserve data integrity
- **Manual Cleanup**: Application handles cleanup of related records when needed

### Update Rules
- **CASCADE**: Primary key updates cascade to foreign keys (rare with UUIDs)
- **RESTRICT**: Most foreign key updates restricted to maintain integrity

### Null Handling
- **Required Relationships**: NOT NULL on essential foreign keys
- **Optional Relationships**: NULL allowed for optional associations
- **Polymorphic References**: Special handling for content_type + content_id patterns

## Performance Implications

### Index Creation
- All foreign key columns automatically get indexes
- Unique constraints automatically create unique indexes
- Additional performance indexes created for common query patterns

### Query Optimization
- Foreign key indexes optimize JOIN operations
- Unique indexes optimize uniqueness checks and lookups
- Check constraints provide query optimization hints to database engine

### Maintenance Considerations
- Regular constraint validation recommended
- Index maintenance for optimal performance
- Statistics updates for query planner optimization

This comprehensive constraint system ensures data integrity, enforces business rules, and provides optimal performance for the Fact Checker application.
