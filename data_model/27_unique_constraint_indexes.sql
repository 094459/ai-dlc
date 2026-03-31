-- Unique Constraint Indexes
-- Indexes for unique constraints (many are automatically created with UNIQUE constraints)

-- User uniqueness
-- CREATE UNIQUE INDEX idx_users_email_unique ON users(email); -- Auto-created with UNIQUE constraint
-- CREATE UNIQUE INDEX idx_user_profiles_user_id_unique ON user_profiles(user_id); -- Auto-created
-- CREATE UNIQUE INDEX idx_user_sessions_session_token_unique ON user_sessions(session_token); -- Auto-created

-- Content uniqueness
-- CREATE UNIQUE INDEX idx_hashtags_tag_unique ON hashtags(tag); -- Auto-created
-- CREATE UNIQUE INDEX idx_fact_hashtags_fact_hashtag_unique ON fact_hashtags(fact_id, hashtag_id); -- Auto-created
-- CREATE UNIQUE INDEX idx_comment_threads_fact_root_unique ON comment_threads(fact_id, root_comment_id); -- Auto-created

-- Voting uniqueness (one vote per user per content)
-- CREATE UNIQUE INDEX idx_fact_votes_fact_user_unique ON fact_votes(fact_id, user_id); -- Auto-created
-- CREATE UNIQUE INDEX idx_comment_votes_comment_user_unique ON comment_votes(comment_id, user_id); -- Auto-created

-- Statistics uniqueness
-- CREATE UNIQUE INDEX idx_vote_statistics_content_unique ON vote_statistics(content_type, content_id); -- Auto-created

-- User preferences uniqueness
-- CREATE UNIQUE INDEX idx_user_notification_prefs_unique ON user_notification_preferences(user_id, notification_type); -- Auto-created

-- System configuration uniqueness
-- CREATE UNIQUE INDEX idx_system_configuration_key_unique ON system_configuration(config_key); -- Auto-created

-- User moderation history uniqueness
-- CREATE UNIQUE INDEX idx_user_moderation_history_user_unique ON user_moderation_history(user_id); -- Auto-created

-- Note: Most unique indexes are automatically created when UNIQUE constraints are defined
-- This file serves as documentation of the unique constraints in the system
