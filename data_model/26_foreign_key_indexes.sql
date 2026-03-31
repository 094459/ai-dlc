-- Foreign Key Indexes
-- Indexes on foreign key columns for optimal join performance and referential integrity

-- User-related foreign keys
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_profile_photos_user_id ON profile_photos(user_id);

-- Content foreign keys
CREATE INDEX idx_facts_user_id ON facts(user_id);
CREATE INDEX idx_fact_edit_history_fact_id ON fact_edit_history(fact_id);
CREATE INDEX idx_fact_hashtags_fact_id ON fact_hashtags(fact_id);
CREATE INDEX idx_fact_hashtags_hashtag_id ON fact_hashtags(hashtag_id);
CREATE INDEX idx_fact_resources_fact_id ON fact_resources(fact_id);
CREATE INDEX idx_resource_validation_resource_id ON resource_validation(resource_id);

-- Comment foreign keys
CREATE INDEX idx_comments_fact_id ON comments(fact_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_parent_comment_id ON comments(parent_comment_id);
CREATE INDEX idx_comment_edit_history_comment_id ON comment_edit_history(comment_id);
CREATE INDEX idx_comment_threads_fact_id ON comment_threads(fact_id);
CREATE INDEX idx_comment_threads_root_comment_id ON comment_threads(root_comment_id);

-- Voting foreign keys
CREATE INDEX idx_fact_votes_fact_id ON fact_votes(fact_id);
CREATE INDEX idx_fact_votes_user_id ON fact_votes(user_id);
CREATE INDEX idx_comment_votes_comment_id ON comment_votes(comment_id);
CREATE INDEX idx_comment_votes_user_id ON comment_votes(user_id);

-- Moderation foreign keys
CREATE INDEX idx_reports_reporter_user_id ON reports(reporter_user_id);
CREATE INDEX idx_reports_assigned_moderator_id ON reports(assigned_moderator_id);
CREATE INDEX idx_moderation_actions_moderator_id ON moderation_actions(moderator_id);
CREATE INDEX idx_moderation_actions_related_report_id ON moderation_actions(related_report_id);
CREATE INDEX idx_user_moderation_history_user_id ON user_moderation_history(user_id);
CREATE INDEX idx_user_moderation_history_last_action_id ON user_moderation_history(last_moderation_action_id);

-- System foreign keys
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_user_notification_preferences_user_id ON user_notification_preferences(user_id);
CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_session_id ON analytics_events(session_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_system_configuration_updated_by ON system_configuration(updated_by);
