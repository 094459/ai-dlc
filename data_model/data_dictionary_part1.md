# Data Dictionary - Part 1: User Management Tables

## Overview
This document provides detailed field descriptions for all user management tables in the Fact Checker application database schema.

## Table: users
**Purpose**: Core user account information and authentication data

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for user account (UUID format) |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User's email address, used for login and communication |
| password_hash | VARCHAR(255) | NOT NULL | Securely hashed password using bcrypt (never store plain text) |
| is_active | INTEGER | NOT NULL, DEFAULT 1, CHECK (0,1) | Account status: 1=active, 0=deactivated |
| is_admin | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Administrative privileges: 1=admin, 0=regular user |
| is_moderator | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Moderation privileges: 1=moderator, 0=regular user |
| last_login | DATETIME | NULL | Timestamp of user's most recent login session |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last account modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag: 1=deleted, 0=active |
| deleted_at | DATETIME | NULL | Timestamp when account was soft deleted |

**Business Rules**:
- Email must be unique across all users
- Password must be hashed using bcrypt with appropriate salt rounds
- Admin users automatically have moderator privileges
- Soft delete preserves referential integrity

## Table: user_sessions
**Purpose**: User login session management and tracking

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for session (UUID format) |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User who owns this session |
| session_token | VARCHAR(255) | NOT NULL, UNIQUE | Cryptographically secure session token |
| expires_at | DATETIME | NOT NULL | Session expiration timestamp |
| ip_address | VARCHAR(45) | NULL | Client IP address (supports IPv4 and IPv6) |
| user_agent | TEXT | NULL | Browser/client user agent string |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Session creation timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Session invalidation flag |
| deleted_at | DATETIME | NULL | Timestamp when session was invalidated |

**Business Rules**:
- Session tokens must be cryptographically secure and unpredictable
- Default session expiration is 24 hours (configurable)
- Expired sessions should be cleaned up periodically
- IP address and user agent used for security monitoring

## Table: user_profiles
**Purpose**: User profile information and display settings

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for profile (UUID format) |
| user_id | VARCHAR(36) | NOT NULL, UNIQUE, FK to users.id | User who owns this profile (1:1 relationship) |
| name | VARCHAR(100) | NOT NULL | User's display name (required for profile completion) |
| biography | TEXT | NULL | User's biography/description (max 1000 chars at app level) |
| profile_photo_url | VARCHAR(500) | NULL | URL/path to user's current profile photo |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Profile creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last profile modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when profile was soft deleted |

**Business Rules**:
- Each user can have exactly one profile
- Name is required for profile completion
- Biography character limit enforced at application level
- Profile photo URL references file in profile_photos table

## Table: profile_photos
**Purpose**: Profile photo file metadata and management

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for photo record (UUID format) |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User who uploaded this photo |
| filename | VARCHAR(255) | NOT NULL | Original filename of uploaded photo |
| file_path | VARCHAR(500) | NOT NULL | Server file path where photo is stored |
| file_size | INTEGER | NOT NULL | File size in bytes for storage management |
| mime_type | VARCHAR(100) | NOT NULL | MIME type (image/jpeg, image/png, etc.) |
| uploaded_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Photo upload timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when photo was soft deleted |

**Business Rules**:
- Users can upload multiple photos over time
- Only one photo is active at a time (referenced in user_profiles)
- Supported formats: JPG, PNG, GIF, WebP
- Maximum file size: 10MB (configurable)
- Photos automatically resized for web display

## Relationships Summary

### users → user_sessions (1:many)
- One user can have multiple active sessions
- Sessions expire automatically and are cleaned up periodically

### users → user_profiles (1:1)
- Each user has exactly one profile
- Profile is optional but recommended for full functionality

### users → profile_photos (1:many)
- Users can upload multiple photos over time
- Current photo referenced in user_profiles.profile_photo_url

## Indexes for User Management Tables

### Primary Key Indexes (Automatic)
- users(id)
- user_sessions(id)
- user_profiles(id)
- profile_photos(id)

### Foreign Key Indexes
- user_sessions(user_id)
- user_profiles(user_id)
- profile_photos(user_id)

### Unique Constraint Indexes (Automatic)
- users(email)
- user_sessions(session_token)
- user_profiles(user_id)

### Performance Indexes
- users(is_active)
- users(is_deleted)
- users(created_at)
- users(last_login)
- user_sessions(expires_at)
- user_sessions(is_deleted)

## Security Considerations

### Password Security
- Passwords never stored in plain text
- bcrypt hashing with appropriate salt rounds
- Password complexity enforced at application level

### Session Security
- Cryptographically secure session tokens
- Session fixation protection through token regeneration
- IP address and user agent tracking for security monitoring

### Data Protection
- Soft delete pattern preserves data integrity
- Personal information can be anonymized if needed
- Audit trail maintained for all account changes
