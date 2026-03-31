# Fact Checker Application - Database Schema Documentation

## Overview
This document provides comprehensive documentation for the Fact Checker application database schema. The schema supports all 15 components identified in the component model and implements a complete fact-checking platform with user management, content creation, community interaction, and moderation capabilities.

## Schema Design Principles

### 1. Cross-Database Compatibility
- **Primary Keys**: UUIDs stored as VARCHAR(36) for PostgreSQL/SQLite compatibility
- **Boolean Fields**: INTEGER(1) with CHECK constraints instead of native BOOLEAN
- **Timestamps**: Standard DATETIME format supported by both databases
- **Enumerations**: VARCHAR with CHECK constraints instead of native ENUMs
- **No Database-Specific Features**: Avoids JSONB, arrays, full-text search extensions

### 2. Data Integrity
- **Soft Deletes**: Consistent `is_deleted` and `deleted_at` pattern across all tables
- **Foreign Key Constraints**: Proper referential integrity enforcement
- **Unique Constraints**: Prevent duplicate data where appropriate
- **Check Constraints**: Validate enumeration values and data ranges

### 3. Performance Optimization
- **Strategic Indexing**: Comprehensive index strategy for common query patterns
- **Composite Indexes**: Multi-column indexes for complex queries
- **Denormalized Statistics**: Cached vote statistics for performance
- **View Optimization**: Pre-calculated views for common data aggregations

## Table Categories

### Core Foundation (Phase 1)
1. **users** - User account information and authentication
2. **user_sessions** - Session management and tracking
3. **user_profiles** - User profile information and settings
4. **profile_photos** - Profile photo metadata and file management

### Content Foundation (Phase 2)
5. **facts** - Core fact submissions and content
6. **fact_edit_history** - Audit trail for fact modifications
7. **hashtags** - Hashtag definitions and usage statistics
8. **fact_hashtags** - Many-to-many relationship between facts and hashtags
9. **fact_resources** - URL and image attachments to facts
10. **resource_validation** - Resource health and validation tracking

### Community Interaction (Phase 3)
11. **comments** - Threaded comments on facts (3-level nesting)
12. **comment_edit_history** - Audit trail for comment modifications
13. **comment_threads** - Thread organization and metadata
14. **fact_votes** - Fact/Fake voting on facts
15. **comment_votes** - Upvote/Downvote voting on comments
16. **vote_statistics** - Cached voting statistics for performance

### Moderation and Safety (Phase 4)
17. **reports** - Content reporting system
18. **moderation_actions** - Moderation decision tracking
19. **user_moderation_history** - User moderation status and history

### System Infrastructure (Phase 5)
20. **notifications** - User notification system
21. **user_notification_preferences** - Notification delivery preferences
22. **analytics_events** - Usage tracking and analytics
23. **audit_logs** - Security and compliance logging
24. **system_configuration** - Application configuration settings

## Key Relationships

### User-Centric Relationships
- **users** → **user_profiles** (1:1)
- **users** → **user_sessions** (1:many)
- **users** → **facts** (1:many)
- **users** → **comments** (1:many)
- **users** → **fact_votes** (1:many)
- **users** → **comment_votes** (1:many)

### Content Relationships
- **facts** → **fact_resources** (1:many)
- **facts** → **comments** (1:many)
- **facts** ↔ **hashtags** (many:many via fact_hashtags)
- **comments** → **comments** (self-referencing for threading)

### Interaction Relationships
- **facts** → **fact_votes** (1:many)
- **comments** → **comment_votes** (1:many)
- **facts/comments** → **vote_statistics** (1:1)
- **facts/comments** → **reports** (1:many)

### Moderation Relationships
- **reports** → **moderation_actions** (1:many)
- **users** → **user_moderation_history** (1:1)
- **moderation_actions** → **users** (many:1 for moderators)

## Data Flow Patterns

### Content Creation Flow
1. User creates fact → **facts** table
2. Resources attached → **fact_resources** table
3. Hashtags processed → **hashtags** and **fact_hashtags** tables
4. Analytics event logged → **analytics_events** table
5. Audit log created → **audit_logs** table

### Voting Flow
1. User casts vote → **fact_votes** or **comment_votes** table
2. Statistics updated → **vote_statistics** table
3. Analytics event logged → **analytics_events** table
4. Notification sent → **notifications** table

### Moderation Flow
1. User reports content → **reports** table
2. Moderator takes action → **moderation_actions** table
3. User history updated → **user_moderation_history** table
4. Notification sent → **notifications** table
5. Audit log created → **audit_logs** table

## Performance Considerations

### Indexing Strategy
- **Primary Keys**: Automatic indexes on all UUID primary keys
- **Foreign Keys**: Indexes on all foreign key columns for join performance
- **Unique Constraints**: Automatic indexes on unique columns
- **Query Optimization**: Indexes on commonly filtered columns (created_at, is_deleted, status)
- **Composite Indexes**: Multi-column indexes for complex query patterns

### Caching Strategy
- **Vote Statistics**: Pre-calculated and cached in vote_statistics table
- **User Activity**: Aggregated in user activity views
- **Thread Hierarchy**: Optimized through comment_threads table
- **Notification Preferences**: Cached to avoid repeated lookups

### Scalability Features
- **Soft Deletes**: Preserve referential integrity while allowing content removal
- **Pagination Support**: Indexes optimized for LIMIT/OFFSET queries
- **Batch Operations**: Efficient bulk operations through proper indexing
- **Analytics Separation**: Analytics events can be archived/partitioned

## Security Features

### Data Protection
- **Password Security**: Only hashed passwords stored, never plain text
- **Session Management**: Secure token-based sessions with expiration
- **Input Validation**: Check constraints and application-level validation
- **Audit Trail**: Comprehensive logging of all significant actions

### Access Control
- **Role-Based Access**: Admin and moderator flags in users table
- **Content Ownership**: Foreign key relationships enforce ownership
- **Moderation Tracking**: Complete audit trail of moderation actions
- **Privacy Controls**: Soft deletes preserve privacy while maintaining integrity

## Compliance and Auditing

### Audit Trail
- **User Actions**: All significant user actions logged in audit_logs
- **Content Changes**: Edit history preserved for facts and comments
- **Moderation Actions**: Complete record of all moderation decisions
- **System Events**: Analytics events track system usage patterns

### Data Retention
- **Soft Delete Pattern**: Consistent across all tables for data preservation
- **Edit History**: Permanent record of content modifications
- **Session Cleanup**: Expired sessions can be safely removed
- **Analytics Archival**: Old analytics events can be archived

## Views and Aggregations

### User-Focused Views
- **user_profile_summary**: Complete user information with statistics
- **user_activity_summary**: User engagement and activity metrics

### Content-Focused Views
- **fact_with_statistics**: Facts with voting and engagement statistics
- **comment_thread_hierarchy**: Threaded comment display with voting

### Administrative Views
- **moderation_queue**: Comprehensive moderation workflow view

## Migration and Deployment

### Database Setup
1. Create tables in dependency order (Phase 1-5)
2. Apply indexes for performance (Phase 6)
3. Create views for application use (Phase 7)
4. Validate schema completeness (Phase 8)

### Environment Differences
- **Development (SQLite)**: Single file database, simplified deployment
- **Production (PostgreSQL)**: Full ACID compliance, advanced features
- **Schema Compatibility**: Identical schema works in both environments

## Maintenance Procedures

### Regular Maintenance
- **Session Cleanup**: Remove expired sessions periodically
- **Statistics Refresh**: Update vote statistics as needed
- **Analytics Archival**: Archive old analytics events
- **Index Maintenance**: Monitor and optimize index performance

### Data Integrity Checks
- **Referential Integrity**: Validate foreign key relationships
- **Soft Delete Consistency**: Ensure proper soft delete handling
- **Vote Statistics Accuracy**: Verify cached statistics match actual votes
- **Thread Hierarchy Validation**: Ensure comment threading is correct

This schema provides a robust, scalable foundation for the Fact Checker application while maintaining compatibility across different database systems and supporting all required functionality.
