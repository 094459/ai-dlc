-- Performance Indexes
-- Indexes optimized for common query patterns and application performance

-- User activity and status queries
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_is_deleted ON users(is_deleted);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login);

-- Session management queries
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_is_deleted ON user_sessions(is_deleted);

-- Content discovery and filtering
CREATE INDEX idx_facts_created_at ON facts(created_at);
CREATE INDEX idx_facts_is_deleted ON facts(is_deleted);
CREATE INDEX idx_facts_user_created ON facts(user_id, created_at);
CREATE INDEX idx_hashtags_usage_count ON hashtags(usage_count DESC);
CREATE INDEX idx_hashtags_last_used_at ON hashtags(last_used_at DESC);

-- Comment threading and display
CREATE INDEX idx_comments_fact_created ON comments(fact_id, created_at);
CREATE INDEX idx_comments_parent_created ON comments(parent_comment_id, created_at);
CREATE INDEX idx_comments_nesting_level ON comments(nesting_level);
CREATE INDEX idx_comments_is_deleted ON comments(is_deleted);

-- Voting and engagement queries
CREATE INDEX idx_fact_votes_created_at ON fact_votes(created_at);
CREATE INDEX idx_comment_votes_created_at ON comment_votes(created_at);
CREATE INDEX idx_vote_statistics_vote_score ON vote_statistics(vote_score DESC);
CREATE INDEX idx_vote_statistics_total_votes ON vote_statistics(total_votes DESC);

-- Moderation workflow queries
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_priority ON reports(priority);
CREATE INDEX idx_reports_created_at ON reports(created_at);
CREATE INDEX idx_reports_status_priority ON reports(status, priority);
CREATE INDEX idx_moderation_actions_created_at ON moderation_actions(created_at);
CREATE INDEX idx_moderation_actions_is_active ON moderation_actions(is_active);
CREATE INDEX idx_user_moderation_history_status ON user_moderation_history(moderation_status);
CREATE INDEX idx_user_moderation_history_risk_score ON user_moderation_history(risk_score DESC);

-- Notification queries
CREATE INDEX idx_notifications_user_is_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_priority ON notifications(priority);

-- Analytics and reporting queries
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at);
CREATE INDEX idx_analytics_events_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_event_category ON analytics_events(event_category);
CREATE INDEX idx_analytics_events_user_created ON analytics_events(user_id, created_at);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_severity ON audit_logs(severity);

-- Resource management queries
CREATE INDEX idx_fact_resources_resource_type ON fact_resources(resource_type);
CREATE INDEX idx_fact_resources_is_active ON fact_resources(is_active);
CREATE INDEX idx_resource_validation_status ON resource_validation(validation_status);
CREATE INDEX idx_resource_validation_last_checked ON resource_validation(last_checked);
