-- Fact Checker Application - Complete Database Schema
-- Compatible with PostgreSQL (production) and SQLite (development)
-- Generated: 2025-08-19

-- =============================================================================
-- PHASE 1: CORE FOUNDATION TABLES
-- =============================================================================

-- Users Table - Core user account information and authentication
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
    is_moderator INTEGER NOT NULL DEFAULT 0 CHECK (is_moderator IN (0, 1)),
    last_login DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME
);

-- User Sessions Table - Session management and tracking
CREATE TABLE user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- User Profiles Table - User profile information and settings
CREATE TABLE user_profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    biography TEXT,
    profile_photo_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Profile Photos Table - Profile photo metadata and file management
CREATE TABLE profile_photos (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =============================================================================
-- PHASE 2: CONTENT FOUNDATION TABLES
-- =============================================================================

-- Facts Table - Core fact submissions and content
CREATE TABLE facts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    edit_count INTEGER NOT NULL DEFAULT 0,
    last_edited_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Fact Edit History Table - Audit trail for fact modifications
CREATE TABLE fact_edit_history (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    previous_content TEXT NOT NULL,
    edit_reason VARCHAR(500),
    edited_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id)
);

-- Hashtags Table - Hashtag definitions and usage statistics
CREATE TABLE hashtags (
    id VARCHAR(36) PRIMARY KEY,
    tag VARCHAR(100) NOT NULL UNIQUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    first_used_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME
);

-- Fact Hashtags Junction Table - Many-to-many relationship
CREATE TABLE fact_hashtags (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    hashtag_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (hashtag_id) REFERENCES hashtags(id),
    UNIQUE(fact_id, hashtag_id)
);

-- Fact Resources Table - URL and image attachments
CREATE TABLE fact_resources (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    resource_type VARCHAR(10) NOT NULL CHECK (resource_type IN ('url', 'image')),
    resource_value VARCHAR(2000) NOT NULL,
    display_title VARCHAR(200),
    file_size INTEGER,
    mime_type VARCHAR(100),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id)
);

-- Resource Validation Table - Resource health and validation tracking
CREATE TABLE resource_validation (
    id VARCHAR(36) PRIMARY KEY,
    resource_id VARCHAR(36) NOT NULL,
    validation_status VARCHAR(20) NOT NULL CHECK (validation_status IN ('pending', 'valid', 'invalid', 'broken')),
    validation_message TEXT,
    last_checked DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    check_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (resource_id) REFERENCES fact_resources(id)
);

-- =============================================================================
-- PHASE 3: COMMUNITY INTERACTION TABLES
-- =============================================================================

-- Comments Table - Threaded comments with nested reply support
CREATE TABLE comments (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    parent_comment_id VARCHAR(36),
    content TEXT NOT NULL,
    nesting_level INTEGER NOT NULL DEFAULT 0 CHECK (nesting_level >= 0 AND nesting_level <= 2),
    reply_count INTEGER NOT NULL DEFAULT 0,
    edit_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
);

-- Comment Edit History Table - Audit trail for comment modifications
CREATE TABLE comment_edit_history (
    id VARCHAR(36) PRIMARY KEY,
    comment_id VARCHAR(36) NOT NULL,
    previous_content TEXT NOT NULL,
    edit_reason VARCHAR(500),
    edited_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (comment_id) REFERENCES comments(id)
);

-- Comment Threads Table - Thread organization and metadata
CREATE TABLE comment_threads (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    root_comment_id VARCHAR(36) NOT NULL,
    total_comments INTEGER NOT NULL DEFAULT 1,
    last_activity DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (root_comment_id) REFERENCES comments(id),
    UNIQUE(fact_id, root_comment_id)
);

-- Fact Votes Table - Fact/Fake voting system
CREATE TABLE fact_votes (
    id VARCHAR(36) PRIMARY KEY,
    fact_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('fact', 'fake')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (fact_id) REFERENCES facts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(fact_id, user_id)
);

-- Comment Votes Table - Upvote/Downvote voting system
CREATE TABLE comment_votes (
    id VARCHAR(36) PRIMARY KEY,
    comment_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('upvote', 'downvote')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (comment_id) REFERENCES comments(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(comment_id, user_id)
);

-- Vote Statistics Table - Cached voting statistics
CREATE TABLE vote_statistics (
    id VARCHAR(36) PRIMARY KEY,
    content_type VARCHAR(10) NOT NULL CHECK (content_type IN ('fact', 'comment')),
    content_id VARCHAR(36) NOT NULL,
    total_votes INTEGER NOT NULL DEFAULT 0,
    positive_votes INTEGER NOT NULL DEFAULT 0,
    negative_votes INTEGER NOT NULL DEFAULT 0,
    vote_score DECIMAL(10,4) NOT NULL DEFAULT 0.0,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    UNIQUE(content_type, content_id)
);

-- =============================================================================
-- PHASE 4: MODERATION AND SAFETY TABLES
-- =============================================================================

-- Reports Table - Content reporting system
CREATE TABLE reports (
    id VARCHAR(36) PRIMARY KEY,
    reporter_user_id VARCHAR(36) NOT NULL,
    reported_content_type VARCHAR(10) NOT NULL CHECK (reported_content_type IN ('fact', 'comment')),
    reported_content_id VARCHAR(36) NOT NULL,
    report_category VARCHAR(50) NOT NULL CHECK (report_category IN ('spam', 'harassment', 'misinformation', 'inappropriate', 'copyright', 'other')),
    report_reason TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'under_review', 'resolved', 'dismissed')),
    priority VARCHAR(10) NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    assigned_moderator_id VARCHAR(36),
    resolution_notes TEXT,
    resolved_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (reporter_user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_moderator_id) REFERENCES users(id)
);

-- Moderation Actions Table - Records all moderation actions
CREATE TABLE moderation_actions (
    id VARCHAR(36) PRIMARY KEY,
    moderator_id VARCHAR(36) NOT NULL,
    action_type VARCHAR(30) NOT NULL CHECK (action_type IN ('content_removal', 'content_restoration', 'user_warning', 'user_suspension', 'user_ban', 'report_dismissal')),
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('fact', 'comment', 'user', 'report')),
    target_id VARCHAR(36) NOT NULL,
    related_report_id VARCHAR(36),
    reason TEXT NOT NULL,
    duration_hours INTEGER,
    expires_at DATETIME,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (moderator_id) REFERENCES users(id),
    FOREIGN KEY (related_report_id) REFERENCES reports(id)
);

-- User Moderation History Table - User moderation status and history
CREATE TABLE user_moderation_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    moderation_status VARCHAR(20) NOT NULL DEFAULT 'good_standing' CHECK (moderation_status IN ('good_standing', 'warned', 'suspended', 'banned')),
    warning_count INTEGER NOT NULL DEFAULT 0,
    suspension_count INTEGER NOT NULL DEFAULT 0,
    total_reports_against INTEGER NOT NULL DEFAULT 0,
    total_content_removed INTEGER NOT NULL DEFAULT 0,
    current_suspension_expires DATETIME,
    ban_date DATETIME,
    ban_reason TEXT,
    last_moderation_action_id VARCHAR(36),
    risk_score INTEGER NOT NULL DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (last_moderation_action_id) REFERENCES moderation_actions(id)
);

-- =============================================================================
-- PHASE 5: SYSTEM AND INFRASTRUCTURE TABLES
-- =============================================================================

-- Notifications Table - User notification system
CREATE TABLE notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    notification_type VARCHAR(30) NOT NULL CHECK (notification_type IN ('comment_reply', 'fact_vote', 'comment_vote', 'fact_comment', 'moderation_action', 'system_announcement')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    related_content_type VARCHAR(10) CHECK (related_content_type IN ('fact', 'comment', 'user', 'report')),
    related_content_id VARCHAR(36),
    is_read INTEGER NOT NULL DEFAULT 0 CHECK (is_read IN (0, 1)),
    read_at DATETIME,
    delivery_method VARCHAR(20) NOT NULL DEFAULT 'in_app' CHECK (delivery_method IN ('in_app', 'email', 'both')),
    email_sent INTEGER NOT NULL DEFAULT 0 CHECK (email_sent IN (0, 1)),
    email_sent_at DATETIME,
    priority VARCHAR(10) NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- User Notification Preferences Table - Notification delivery preferences
CREATE TABLE user_notification_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    notification_type VARCHAR(30) NOT NULL CHECK (notification_type IN ('comment_reply', 'fact_vote', 'comment_vote', 'fact_comment', 'moderation_action', 'system_announcement')),
    in_app_enabled INTEGER NOT NULL DEFAULT 1 CHECK (in_app_enabled IN (0, 1)),
    email_enabled INTEGER NOT NULL DEFAULT 1 CHECK (email_enabled IN (0, 1)),
    frequency VARCHAR(20) NOT NULL DEFAULT 'immediate' CHECK (frequency IN ('immediate', 'hourly', 'daily', 'weekly', 'disabled')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, notification_type)
);

-- Analytics Events Table - Usage tracking and metrics
CREATE TABLE analytics_events (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(30) NOT NULL CHECK (event_category IN ('user_action', 'content_interaction', 'system_event', 'moderation_event')),
    event_data TEXT,
    related_content_type VARCHAR(10) CHECK (related_content_type IN ('fact', 'comment', 'user', 'report')),
    related_content_id VARCHAR(36),
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer VARCHAR(500),
    page_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES user_sessions(id)
);

-- Audit Logs Table - Security and compliance logging
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    action_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(30) NOT NULL,
    resource_id VARCHAR(36),
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success INTEGER NOT NULL CHECK (success IN (0, 1)),
    error_message TEXT,
    severity VARCHAR(10) NOT NULL DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- System Configuration Table - Application settings
CREATE TABLE system_configuration (
    id VARCHAR(36) PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) NOT NULL CHECK (config_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    is_public INTEGER NOT NULL DEFAULT 0 CHECK (is_public IN (0, 1)),
    requires_restart INTEGER NOT NULL DEFAULT 0 CHECK (requires_restart IN (0, 1)),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(36),
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at DATETIME,
    
    FOREIGN KEY (updated_by) REFERENCES users(id)
);
