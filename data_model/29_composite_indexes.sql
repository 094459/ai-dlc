-- Composite Indexes
-- Multi-column indexes for complex query patterns and optimal performance

-- User authentication and session queries
CREATE INDEX idx_users_email_is_active ON users(email, is_active);
CREATE INDEX idx_user_sessions_user_expires ON user_sessions(user_id, expires_at);

-- Content listing with filters
CREATE INDEX idx_facts_deleted_created ON facts(is_deleted, created_at DESC);
CREATE INDEX idx_facts_user_deleted_created ON facts(user_id, is_deleted, created_at DESC);
CREATE INDEX idx_comments_fact_deleted_created ON comments(fact_id, is_deleted, created_at);
CREATE INDEX idx_comments_parent_deleted_created ON comments(parent_comment_id, is_deleted, created_at);

-- Voting queries with content filtering
CREATE INDEX idx_fact_votes_fact_deleted_created ON fact_votes(fact_id, is_deleted, created_at);
CREATE INDEX idx_comment_votes_comment_deleted_created ON comment_votes(comment_id, is_deleted, created_at);
CREATE INDEX idx_vote_statistics_type_score ON vote_statistics(content_type, vote_score DESC);

-- Moderation workflow optimization
CREATE INDEX idx_reports_status_priority_created ON reports(status, priority, created_at);
CREATE INDEX idx_reports_assigned_status ON reports(assigned_moderator_id, status);
CREATE INDEX idx_moderation_actions_target_type_id ON moderation_actions(target_type, target_id);
CREATE INDEX idx_moderation_actions_moderator_created ON moderation_actions(moderator_id, created_at DESC);

-- Notification management
CREATE INDEX idx_notifications_user_read_created ON notifications(user_id, is_read, created_at DESC);
CREATE INDEX idx_notifications_type_priority_created ON notifications(notification_type, priority, created_at DESC);
CREATE INDEX idx_user_notification_prefs_user_type ON user_notification_preferences(user_id, notification_type);

-- Analytics and reporting optimization
CREATE INDEX idx_analytics_events_user_type_created ON analytics_events(user_id, event_type, created_at);
CREATE INDEX idx_analytics_events_category_type_created ON analytics_events(event_category, event_type, created_at);
CREATE INDEX idx_audit_logs_user_action_created ON audit_logs(user_id, action_type, created_at);
CREATE INDEX idx_audit_logs_resource_type_id ON audit_logs(resource_type, resource_id);

-- Content engagement queries
CREATE INDEX idx_fact_hashtags_hashtag_fact ON fact_hashtags(hashtag_id, fact_id);
CREATE INDEX idx_fact_resources_fact_type_active ON fact_resources(fact_id, resource_type, is_active);
CREATE INDEX idx_resource_validation_resource_status ON resource_validation(resource_id, validation_status);

-- Thread management optimization
CREATE INDEX idx_comment_threads_fact_activity ON comment_threads(fact_id, last_activity DESC);
CREATE INDEX idx_comments_thread_level_created ON comments(parent_comment_id, nesting_level, created_at);

-- User activity tracking
CREATE INDEX idx_facts_user_created_deleted ON facts(user_id, created_at DESC, is_deleted);
CREATE INDEX idx_comments_user_created_deleted ON comments(user_id, created_at DESC, is_deleted);
CREATE INDEX idx_fact_votes_user_created ON fact_votes(user_id, created_at DESC);
CREATE INDEX idx_comment_votes_user_created ON comment_votes(user_id, created_at DESC);
