# Entity Relationship Diagram (ERD) - Fact Checker Application

## ERD Overview
This document describes the entity relationships in the Fact Checker application database schema. The ERD illustrates how the 24 tables interact to support the complete application functionality.

## Entity Relationship Structure

### Core User Entities
```
users (1) ──── (1) user_profiles
  │
  ├── (1) ──── (many) user_sessions
  ├── (1) ──── (1) user_moderation_history
  ├── (1) ──── (many) profile_photos
  ├── (1) ──── (many) user_notification_preferences
  └── (1) ──── (many) notifications
```

### Content Creation Entities
```
users (1) ──── (many) facts
                │
                ├── (1) ──── (many) fact_edit_history
                ├── (1) ──── (many) fact_resources
                ├── (1) ──── (many) comments
                ├── (1) ──── (many) fact_votes
                └── (many) ──── (many) hashtags [via fact_hashtags]

fact_resources (1) ──── (1) resource_validation
```

### Comment Threading Entities
```
facts (1) ──── (many) comments
                │
                ├── (1) ──── (many) comments [self-referencing parent_comment_id]
                ├── (1) ──── (many) comment_edit_history
                ├── (1) ──── (many) comment_votes
                └── (1) ──── (1) comment_threads [for root comments]

comments (1) ──── (many) comment_threads [root_comment_id]
```

### Voting and Statistics Entities
```
facts (1) ──── (many) fact_votes ──── (many) users
comments (1) ──── (many) comment_votes ──── (many) users

facts/comments (1) ──── (1) vote_statistics [polymorphic relationship]
```

### Moderation Entities
```
users (1) ──── (many) reports [as reporter]
users (1) ──── (many) reports [as assigned_moderator]
users (1) ──── (many) moderation_actions [as moderator]

reports (1) ──── (many) moderation_actions
facts/comments ──── (many) reports [polymorphic reported_content]
```

### System Infrastructure Entities
```
users (1) ──── (many) analytics_events
user_sessions (1) ──── (many) analytics_events
users (1) ──── (many) audit_logs
users (1) ──── (many) system_configuration [updated_by]
```

## Detailed Relationship Descriptions

### 1. User Management Relationships

#### users → user_profiles (1:1)
- **Relationship**: One user has exactly one profile
- **Foreign Key**: user_profiles.user_id → users.id
- **Constraint**: UNIQUE constraint on user_profiles.user_id
- **Business Rule**: Profile is optional but recommended for full functionality

#### users → user_sessions (1:many)
- **Relationship**: One user can have multiple active sessions
- **Foreign Key**: user_sessions.user_id → users.id
- **Business Rule**: Sessions expire automatically, old sessions cleaned up periodically

#### users → profile_photos (1:many)
- **Relationship**: One user can upload multiple photos over time
- **Foreign Key**: profile_photos.user_id → users.id
- **Business Rule**: Only one photo is active at a time (referenced in user_profiles)

### 2. Content Creation Relationships

#### users → facts (1:many)
- **Relationship**: One user can submit multiple facts
- **Foreign Key**: facts.user_id → users.id
- **Business Rule**: Users own their facts and can edit/delete them

#### facts → fact_edit_history (1:many)
- **Relationship**: One fact can have multiple edit records
- **Foreign Key**: fact_edit_history.fact_id → facts.id
- **Business Rule**: Every edit creates a history record for audit trail

#### facts → fact_resources (1:many)
- **Relationship**: One fact can have multiple attached resources
- **Foreign Key**: fact_resources.fact_id → facts.id
- **Business Rule**: Maximum 5 resources per fact (enforced at application level)

#### fact_resources → resource_validation (1:1)
- **Relationship**: Each resource has validation status
- **Foreign Key**: resource_validation.resource_id → fact_resources.id
- **Business Rule**: Validation occurs asynchronously after resource creation

### 3. Hashtag Relationships

#### facts ↔ hashtags (many:many)
- **Relationship**: Facts can have multiple hashtags, hashtags can be on multiple facts
- **Junction Table**: fact_hashtags
- **Foreign Keys**: 
  - fact_hashtags.fact_id → facts.id
  - fact_hashtags.hashtag_id → hashtags.id
- **Constraint**: UNIQUE(fact_id, hashtag_id) prevents duplicates
- **Business Rule**: Hashtags are extracted from fact content automatically

### 4. Comment Threading Relationships

#### facts → comments (1:many)
- **Relationship**: One fact can have multiple comments
- **Foreign Key**: comments.fact_id → facts.id
- **Business Rule**: Comments are organized in threads up to 3 levels deep

#### comments → comments (self-referencing)
- **Relationship**: Comments can reply to other comments
- **Foreign Key**: comments.parent_comment_id → comments.id
- **Business Rule**: Maximum nesting level of 2 (0=top-level, 1=reply, 2=reply to reply)

#### comments → comment_threads (1:1 for root comments)
- **Relationship**: Root comments (level 0) have thread metadata
- **Foreign Key**: comment_threads.root_comment_id → comments.id
- **Business Rule**: Only created for top-level comments, tracks thread statistics

### 5. Voting Relationships

#### users + facts → fact_votes (many:many)
- **Relationship**: Users can vote on facts (but not their own)
- **Foreign Keys**: 
  - fact_votes.user_id → users.id
  - fact_votes.fact_id → facts.id
- **Constraint**: UNIQUE(user_id, fact_id) ensures one vote per user per fact
- **Business Rule**: Users cannot vote on their own facts

#### users + comments → comment_votes (many:many)
- **Relationship**: Users can vote on comments (but not their own)
- **Foreign Keys**: 
  - comment_votes.user_id → users.id
  - comment_votes.comment_id → comments.id
- **Constraint**: UNIQUE(user_id, comment_id) ensures one vote per user per comment
- **Business Rule**: Users cannot vote on their own comments

#### facts/comments → vote_statistics (1:1 polymorphic)
- **Relationship**: Each fact or comment has cached vote statistics
- **Polymorphic Keys**: 
  - vote_statistics.content_type ('fact' or 'comment')
  - vote_statistics.content_id (references facts.id or comments.id)
- **Constraint**: UNIQUE(content_type, content_id)
- **Business Rule**: Statistics updated when votes change

### 6. Moderation Relationships

#### users → reports (1:many as reporter)
- **Relationship**: Users can submit multiple reports
- **Foreign Key**: reports.reporter_user_id → users.id
- **Business Rule**: Users can report inappropriate content

#### users → reports (1:many as moderator)
- **Relationship**: Moderators can be assigned multiple reports
- **Foreign Key**: reports.assigned_moderator_id → users.id
- **Business Rule**: Only users with is_moderator=1 can be assigned

#### facts/comments → reports (polymorphic 1:many)
- **Relationship**: Content can be reported multiple times
- **Polymorphic Keys**: 
  - reports.reported_content_type ('fact' or 'comment')
  - reports.reported_content_id (references facts.id or comments.id)
- **Business Rule**: Multiple users can report the same content

#### reports → moderation_actions (1:many)
- **Relationship**: Reports can result in multiple moderation actions
- **Foreign Key**: moderation_actions.related_report_id → reports.id
- **Business Rule**: Actions can be taken without reports (proactive moderation)

#### users → user_moderation_history (1:1)
- **Relationship**: Each user has one moderation history record
- **Foreign Key**: user_moderation_history.user_id → users.id
- **Constraint**: UNIQUE constraint on user_id
- **Business Rule**: Created when user first receives moderation action

### 7. System Infrastructure Relationships

#### users → notifications (1:many)
- **Relationship**: Users receive multiple notifications
- **Foreign Key**: notifications.user_id → users.id
- **Business Rule**: Notifications sent for various user activities

#### users → user_notification_preferences (1:many)
- **Relationship**: Users have preferences for different notification types
- **Foreign Key**: user_notification_preferences.user_id → users.id
- **Constraint**: UNIQUE(user_id, notification_type)
- **Business Rule**: Default preferences created on user registration

#### users → analytics_events (1:many)
- **Relationship**: User actions generate analytics events
- **Foreign Key**: analytics_events.user_id → users.id
- **Business Rule**: Some events can be anonymous (user_id = NULL)

#### user_sessions → analytics_events (1:many)
- **Relationship**: Events can be tied to specific sessions
- **Foreign Key**: analytics_events.session_id → user_sessions.id
- **Business Rule**: Helps track user behavior within sessions

#### users → audit_logs (1:many)
- **Relationship**: User actions generate audit log entries
- **Foreign Key**: audit_logs.user_id → users.id
- **Business Rule**: System actions can have user_id = NULL

## Polymorphic Relationships

### Content Polymorphism
Several tables use polymorphic relationships to handle both facts and comments:

1. **reports**: Can report facts or comments
   - `reported_content_type` + `reported_content_id`

2. **vote_statistics**: Tracks statistics for facts or comments
   - `content_type` + `content_id`

3. **moderation_actions**: Can target facts, comments, users, or reports
   - `target_type` + `target_id`

4. **analytics_events**: Can relate to various content types
   - `related_content_type` + `related_content_id`

5. **notifications**: Can relate to various content types
   - `related_content_type` + `related_content_id`

## Referential Integrity Rules

### Cascade Rules
- **ON DELETE**: Most foreign keys use RESTRICT to prevent accidental data loss
- **Soft Deletes**: Used instead of CASCADE DELETE to preserve referential integrity
- **Session Cleanup**: user_sessions can be CASCADE deleted when users are deleted

### Constraint Enforcement
- **UNIQUE Constraints**: Prevent duplicate relationships (votes, preferences, etc.)
- **CHECK Constraints**: Validate enumeration values and data ranges
- **NOT NULL Constraints**: Ensure required relationships are maintained

## Index Strategy for Relationships

### Foreign Key Indexes
- All foreign key columns have indexes for join performance
- Composite indexes on frequently joined column combinations
- Unique indexes automatically created for unique constraints

### Query Optimization Indexes
- Indexes on commonly filtered columns in relationships
- Composite indexes for complex relationship queries
- Partial indexes for soft-deleted records where appropriate

This ERD structure supports all the component requirements while maintaining data integrity, performance, and scalability for the Fact Checker application.
