-- User Profile Summary View
-- Comprehensive view combining user account, profile, and activity statistics

CREATE VIEW user_profile_summary AS
SELECT 
    u.id AS user_id,
    u.email,
    u.is_active,
    u.is_admin,
    u.is_moderator,
    u.last_login,
    u.created_at AS user_created_at,
    
    -- Profile information
    up.name,
    up.biography,
    up.profile_photo_url,
    up.created_at AS profile_created_at,
    
    -- Activity statistics
    COALESCE(fact_stats.total_facts, 0) AS total_facts_submitted,
    COALESCE(comment_stats.total_comments, 0) AS total_comments_posted,
    COALESCE(vote_stats.total_votes_cast, 0) AS total_votes_cast,
    
    -- Engagement statistics
    COALESCE(engagement_stats.facts_voted_on, 0) AS facts_received_votes,
    COALESCE(engagement_stats.comments_voted_on, 0) AS comments_received_votes,
    
    -- Moderation status
    COALESCE(umh.moderation_status, 'good_standing') AS moderation_status,
    COALESCE(umh.warning_count, 0) AS warning_count,
    COALESCE(umh.total_reports_against, 0) AS reports_against_user,
    
    -- Calculated fields
    CASE 
        WHEN up.name IS NOT NULL THEN 1 
        ELSE 0 
    END AS profile_completed

FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id AND up.is_deleted = 0
LEFT JOIN (
    SELECT user_id, COUNT(*) as total_facts
    FROM facts 
    WHERE is_deleted = 0 
    GROUP BY user_id
) fact_stats ON u.id = fact_stats.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as total_comments
    FROM comments 
    WHERE is_deleted = 0 
    GROUP BY user_id
) comment_stats ON u.id = comment_stats.user_id
LEFT JOIN (
    SELECT user_id, 
           (SELECT COUNT(*) FROM fact_votes fv WHERE fv.user_id = votes.user_id AND fv.is_deleted = 0) +
           (SELECT COUNT(*) FROM comment_votes cv WHERE cv.user_id = votes.user_id AND cv.is_deleted = 0) as total_votes_cast
    FROM (SELECT DISTINCT user_id FROM fact_votes UNION SELECT DISTINCT user_id FROM comment_votes) votes
) vote_stats ON u.id = vote_stats.user_id
LEFT JOIN (
    SELECT f.user_id,
           COUNT(DISTINCT fv.id) as facts_voted_on,
           COUNT(DISTINCT cv.id) as comments_voted_on
    FROM facts f
    LEFT JOIN fact_votes fv ON f.id = fv.fact_id AND fv.is_deleted = 0
    LEFT JOIN comments c ON f.id = c.fact_id AND c.is_deleted = 0
    LEFT JOIN comment_votes cv ON c.id = cv.comment_id AND cv.is_deleted = 0
    WHERE f.is_deleted = 0
    GROUP BY f.user_id
) engagement_stats ON u.id = engagement_stats.user_id
LEFT JOIN user_moderation_history umh ON u.id = umh.user_id AND umh.is_deleted = 0
WHERE u.is_deleted = 0;
