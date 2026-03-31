# Data Dictionary - Part 2: Content Management Tables

## Overview
This document provides detailed field descriptions for all content management tables in the Fact Checker application database schema.

## Table: facts
**Purpose**: Core fact submissions and content management

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for fact (UUID format) |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User who submitted this fact |
| content | TEXT | NOT NULL | The actual fact content (max 500 chars at app level) |
| edit_count | INTEGER | NOT NULL, DEFAULT 0 | Number of times this fact has been edited |
| last_edited_at | DATETIME | NULL | Timestamp of most recent edit (NULL if never edited) |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Fact submission timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when fact was soft deleted |

**Business Rules**:
- Content length limited to 500 characters (enforced at application level)
- Only fact owners can edit or delete their facts
- Edit count incremented with each modification
- Soft delete preserves referential integrity for votes and comments

## Table: fact_edit_history
**Purpose**: Audit trail for all fact modifications

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for edit record (UUID format) |
| fact_id | VARCHAR(36) | NOT NULL, FK to facts.id | Fact that was edited |
| previous_content | TEXT | NOT NULL | Content before the edit (for audit purposes) |
| edit_reason | VARCHAR(500) | NULL | Optional user-provided reason for the edit |
| edited_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp when edit occurred |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag (rarely used) |
| deleted_at | DATETIME | NULL | Timestamp when record was soft deleted |

**Business Rules**:
- Every fact edit creates a history record
- Previous content preserved for transparency and moderation
- Edit reason is optional but encouraged
- History records are permanent for audit trail

## Table: hashtags
**Purpose**: Hashtag definitions and usage statistics

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for hashtag (UUID format) |
| tag | VARCHAR(100) | NOT NULL, UNIQUE | Hashtag text (normalized, without # symbol) |
| usage_count | INTEGER | NOT NULL, DEFAULT 0 | Number of facts using this hashtag |
| first_used_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When hashtag was first created |
| last_used_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When hashtag was most recently used |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when hashtag was soft deleted |

**Business Rules**:
- Hashtags normalized to lowercase for consistency
- Usage count updated when facts are created/deleted
- Trending analysis based on usage_count and last_used_at
- Hashtags extracted automatically from fact content

## Table: fact_hashtags
**Purpose**: Many-to-many relationship between facts and hashtags

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for association (UUID format) |
| fact_id | VARCHAR(36) | NOT NULL, FK to facts.id | Fact in the association |
| hashtag_id | VARCHAR(36) | NOT NULL, FK to hashtags.id | Hashtag in the association |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When association was created |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when association was soft deleted |

**Constraints**:
- UNIQUE(fact_id, hashtag_id) - Prevents duplicate associations

**Business Rules**:
- Junction table enabling many-to-many relationship
- Created automatically when hashtags found in fact content
- Soft delete allows removing hashtag associations

## Table: fact_resources
**Purpose**: URL and image attachments to facts

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for resource (UUID format) |
| fact_id | VARCHAR(36) | NOT NULL, FK to facts.id | Fact this resource is attached to |
| resource_type | VARCHAR(10) | NOT NULL, CHECK ('url', 'image') | Type of resource |
| resource_value | VARCHAR(2000) | NOT NULL | URL or file path to the resource |
| display_title | VARCHAR(200) | NULL | Optional display title for the resource |
| file_size | INTEGER | NULL | File size in bytes (for images only) |
| mime_type | VARCHAR(100) | NULL | MIME type (for images only) |
| is_active | INTEGER | NOT NULL, DEFAULT 1, CHECK (0,1) | Resource active status |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Resource creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when resource was soft deleted |

**Business Rules**:
- Maximum 5 resources per fact (enforced at application level)
- URLs must be valid HTTP/HTTPS format
- Images must be valid format (JPG, PNG, GIF, WebP)
- Maximum image size: 10MB (configurable)
- Display title extracted from URL metadata or user-provided

## Table: resource_validation
**Purpose**: Resource health and validation tracking

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for validation record (UUID format) |
| resource_id | VARCHAR(36) | NOT NULL, FK to fact_resources.id | Resource being validated |
| validation_status | VARCHAR(20) | NOT NULL, CHECK ('pending', 'valid', 'invalid', 'broken') | Current validation state |
| validation_message | TEXT | NULL | Details about validation results or errors |
| last_checked | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Most recent validation check |
| check_count | INTEGER | NOT NULL, DEFAULT 0 | Number of times resource has been validated |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when record was soft deleted |

**Validation Status Values**:
- **pending**: Not yet validated
- **valid**: Resource is accessible and valid
- **invalid**: Resource format/content is invalid
- **broken**: Resource is no longer accessible

**Business Rules**:
- Validation occurs asynchronously after resource creation
- Periodic re-validation to check for broken links
- Check count tracks validation frequency
- Validation message provides error details

## Relationships Summary

### facts → fact_edit_history (1:many)
- Every fact edit creates a history record
- Complete audit trail for transparency

### facts ↔ hashtags (many:many via fact_hashtags)
- Facts can have multiple hashtags
- Hashtags can be used by multiple facts
- Junction table manages the relationship

### facts → fact_resources (1:many)
- Facts can have multiple attached resources
- Maximum 5 resources per fact

### fact_resources → resource_validation (1:1)
- Each resource has validation status
- Validation occurs asynchronously

## Indexes for Content Management Tables

### Primary Key Indexes (Automatic)
- facts(id), fact_edit_history(id), hashtags(id)
- fact_hashtags(id), fact_resources(id), resource_validation(id)

### Foreign Key Indexes
- facts(user_id), fact_edit_history(fact_id)
- fact_hashtags(fact_id, hashtag_id)
- fact_resources(fact_id), resource_validation(resource_id)

### Unique Constraint Indexes (Automatic)
- hashtags(tag)
- fact_hashtags(fact_id, hashtag_id)

### Performance Indexes
- facts(created_at), facts(is_deleted)
- hashtags(usage_count DESC), hashtags(last_used_at DESC)
- fact_resources(resource_type), fact_resources(is_active)
- resource_validation(validation_status)
