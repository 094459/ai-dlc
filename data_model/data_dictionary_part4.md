# Data Dictionary - Part 4: System and Infrastructure Tables

## Overview
This document provides detailed field descriptions for system infrastructure tables including moderation, notifications, analytics, and configuration.

## Table: reports
**Purpose**: Content reporting system for inappropriate content

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for report (UUID format) |
| reporter_user_id | VARCHAR(36) | NOT NULL, FK to users.id | User who submitted the report |
| reported_content_type | VARCHAR(10) | NOT NULL, CHECK ('fact', 'comment') | Type of content being reported |
| reported_content_id | VARCHAR(36) | NOT NULL | ID of the fact or comment being reported |
| report_category | VARCHAR(50) | NOT NULL, CHECK (see values below) | Predefined category for report type |
| report_reason | TEXT | NULL | Optional detailed explanation from reporter |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending', CHECK (see values) | Current status in moderation workflow |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'normal', CHECK (see values) | Priority level for report triage |
| assigned_moderator_id | VARCHAR(36) | NULL, FK to users.id | Moderator assigned to handle this report |
| resolution_notes | TEXT | NULL | Moderator notes explaining resolution decision |
| resolved_at | DATETIME | NULL | When report was resolved or dismissed |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Report submission timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when report was soft deleted |

**Report Categories**: 'spam', 'harassment', 'misinformation', 'inappropriate', 'copyright', 'other'
**Status Values**: 'pending', 'under_review', 'resolved', 'dismissed'
**Priority Values**: 'low', 'normal', 'high', 'urgent'

## Table: moderation_actions
**Purpose**: Records all moderation actions taken on content and users

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for action (UUID format) |
| moderator_id | VARCHAR(36) | NOT NULL, FK to users.id | User who performed the moderation action |
| action_type | VARCHAR(30) | NOT NULL, CHECK (see values below) | Type of moderation action taken |
| target_type | VARCHAR(10) | NOT NULL, CHECK ('fact', 'comment', 'user', 'report') | Type of entity action was taken on |
| target_id | VARCHAR(36) | NOT NULL | ID of the specific entity |
| related_report_id | VARCHAR(36) | NULL, FK to reports.id | Report that triggered this action (if applicable) |
| reason | TEXT | NOT NULL | Explanation for the moderation action |
| duration_hours | INTEGER | NULL | Duration for temporary actions (suspensions) |
| expires_at | DATETIME | NULL | When temporary actions expire |
| is_active | INTEGER | NOT NULL, DEFAULT 1, CHECK (0,1) | Whether action is currently in effect |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Action timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when action was soft deleted |

**Action Types**: 'content_removal', 'content_restoration', 'user_warning', 'user_suspension', 'user_ban', 'report_dismissal'

## Table: user_moderation_history
**Purpose**: Tracks moderation status and history for each user

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for history record (UUID format) |
| user_id | VARCHAR(36) | NOT NULL, UNIQUE, FK to users.id | User this history belongs to |
| moderation_status | VARCHAR(20) | NOT NULL, DEFAULT 'good_standing', CHECK (see values) | Current moderation status |
| warning_count | INTEGER | NOT NULL, DEFAULT 0 | Total warnings issued to user |
| suspension_count | INTEGER | NOT NULL, DEFAULT 0 | Total times user has been suspended |
| total_reports_against | INTEGER | NOT NULL, DEFAULT 0 | Total reports filed against user |
| total_content_removed | INTEGER | NOT NULL, DEFAULT 0 | Total pieces of content removed |
| current_suspension_expires | DATETIME | NULL | When current suspension ends |
| ban_date | DATETIME | NULL | When user was banned (if applicable) |
| ban_reason | TEXT | NULL | Detailed reason for permanent ban |
| last_moderation_action_id | VARCHAR(36) | NULL, FK to moderation_actions.id | Most recent moderation action |
| risk_score | INTEGER | NOT NULL, DEFAULT 0, CHECK (0-100) | Calculated risk score |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when record was soft deleted |

**Moderation Status Values**: 'good_standing', 'warned', 'suspended', 'banned'

## Table: notifications
**Purpose**: User notification system for in-app and email notifications

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for notification (UUID format) |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User receiving the notification |
| notification_type | VARCHAR(30) | NOT NULL, CHECK (see values below) | Type of notification |
| title | VARCHAR(200) | NOT NULL | Short notification title for display |
| message | TEXT | NOT NULL | Full notification message content |
| related_content_type | VARCHAR(10) | NULL, CHECK ('fact', 'comment', 'user', 'report') | Type of related content |
| related_content_id | VARCHAR(36) | NULL | ID of related content |
| is_read | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Whether user has read notification |
| read_at | DATETIME | NULL | When notification was marked as read |
| delivery_method | VARCHAR(20) | NOT NULL, DEFAULT 'in_app', CHECK (see values) | How notification should be delivered |
| email_sent | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Whether email was successfully sent |
| email_sent_at | DATETIME | NULL | When email notification was sent |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'normal', CHECK (see values) | Priority level |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Notification creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when notification was soft deleted |

**Notification Types**: 'comment_reply', 'fact_vote', 'comment_vote', 'fact_comment', 'moderation_action', 'system_announcement'
**Delivery Methods**: 'in_app', 'email', 'both'
**Priority Values**: 'low', 'normal', 'high', 'urgent'

## Table: user_notification_preferences
**Purpose**: User preferences for different types of notifications

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for preference record (UUID format) |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User these preferences belong to |
| notification_type | VARCHAR(30) | NOT NULL, CHECK (same as notifications) | Type of notification this preference applies to |
| in_app_enabled | INTEGER | NOT NULL, DEFAULT 1, CHECK (0,1) | Whether to show in-app notifications |
| email_enabled | INTEGER | NOT NULL, DEFAULT 1, CHECK (0,1) | Whether to send email notifications |
| frequency | VARCHAR(20) | NOT NULL, DEFAULT 'immediate', CHECK (see values) | How often to send notifications |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Preference creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when preference was soft deleted |

**Constraints**: UNIQUE(user_id, notification_type)
**Frequency Values**: 'immediate', 'hourly', 'daily', 'weekly', 'disabled'

## Table: analytics_events
**Purpose**: Usage tracking and analytics for system metrics

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for event (UUID format) |
| user_id | VARCHAR(36) | NULL, FK to users.id | User who triggered event (NULL for anonymous) |
| session_id | VARCHAR(36) | NULL, FK to user_sessions.id | Session where event occurred |
| event_type | VARCHAR(50) | NOT NULL | Specific type of event |
| event_category | VARCHAR(30) | NOT NULL, CHECK (see values below) | Broad category for grouping |
| event_data | TEXT | NULL | Additional event data (JSON-like string) |
| related_content_type | VARCHAR(10) | NULL, CHECK ('fact', 'comment', 'user', 'report') | Type of related content |
| related_content_id | VARCHAR(36) | NULL | ID of related content |
| ip_address | VARCHAR(45) | NULL | Client IP address |
| user_agent | TEXT | NULL | Browser/client information |
| referrer | VARCHAR(500) | NULL | HTTP referrer |
| page_url | VARCHAR(500) | NULL | URL where event occurred |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Event timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when event was soft deleted |

**Event Categories**: 'user_action', 'content_interaction', 'system_event', 'moderation_event'

## Table: audit_logs
**Purpose**: Security and compliance logging for all significant actions

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for log entry (UUID format) |
| user_id | VARCHAR(36) | NULL, FK to users.id | User who performed action (NULL for system) |
| action_type | VARCHAR(50) | NOT NULL | Type of action performed |
| resource_type | VARCHAR(30) | NOT NULL | Type of resource affected |
| resource_id | VARCHAR(36) | NULL | ID of specific resource affected |
| old_values | TEXT | NULL | Previous state (JSON-like string) |
| new_values | TEXT | NULL | New state (JSON-like string) |
| ip_address | VARCHAR(45) | NULL | Client IP address |
| user_agent | TEXT | NULL | Browser/client information |
| success | INTEGER | NOT NULL, CHECK (0,1) | Whether action completed successfully |
| error_message | TEXT | NULL | Error details if success = 0 |
| severity | VARCHAR(10) | NOT NULL, DEFAULT 'info', CHECK (see values) | Log level |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Action timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when log was soft deleted |

**Severity Values**: 'debug', 'info', 'warning', 'error', 'critical'

## Table: system_configuration
**Purpose**: Application-wide configuration settings

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for config record (UUID format) |
| config_key | VARCHAR(100) | NOT NULL, UNIQUE | Unique identifier for setting |
| config_value | TEXT | NOT NULL | The configuration value (stored as text) |
| config_type | VARCHAR(20) | NOT NULL, CHECK (see values below) | Data type for proper parsing |
| description | TEXT | NULL | Human-readable description |
| is_public | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Whether visible to non-admins |
| requires_restart | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Whether change requires app restart |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Setting creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| updated_by | VARCHAR(36) | NULL, FK to users.id | Admin who last updated setting |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when setting was soft deleted |

**Config Types**: 'string', 'integer', 'boolean', 'json'
