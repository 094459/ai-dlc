-- User Activity Summary View
-- Comprehensive view of user activity and engagement metrics

CREATE VIEW user_activity_summary AS
SELECT 
    u.id AS user_id,
    u.email,
    up.name,
    u.created_at AS user_joined_date,
    u.last_login,
    
    -- Content creation activity
    COALESCE(content_stats.total_facts, 0) AS facts_submitted,
    COALESCE(content_stats.total_comments, 0) AS comments_posted,
    COALESCE(content_stats.facts_last_30_days, 0) AS facts_last_30_days,
    COALESCE(content_stats.comments_last_30_days, 0) AS comments_last_30_days,
    
    -- Voting activity
    COALESCE(voting_stats.fact_votes_cast, 0) AS fact_votes_cast,
    COALESCE(voting_stats.comment_votes_cast, 0) AS comment_votes_cast,
    COALESCE(voting_stats.votes_last_30_days, 0) AS votes_last_30_days,
    
    -- Engagement received
    COALESCE(engagement_stats.votes_received_on_facts, 0) AS votes_received_on_facts,
    COALESCE(engagement_stats.votes_received_on_comments, 0) AS votes_received_on_comments,
    COALESCE(engagement_stats.comments_received_on_facts, 0) AS comments_received_on_facts,
    
    -- Recent activity indicators
    CASE 
        WHEN u.last_login >= datetime('now', '-7 days') THEN 1 
        ELSE 0 
    END AS active_last_week,
    CASE 
        WHEN u.last_login >= datetime('now', '-30 days') THEN 1 
        ELSE 0 
    END AS active_last_month,
    
    -- Activity score calculation
    (COALESCE(content_stats.total_facts, 0) * 3 +
     COALESCE(content_stats.total_comments, 0) * 2 +
     COALESCE(voting_stats.fact_votes_cast, 0) * 1 +
     COALESCE(voting_stats.comment_votes_cast, 0) * 1 +
     COALESCE(engagement_stats.votes_received_on_facts, 0) * 2 +
     COALESCE(engagement_stats.votes_received_on_comments, 0) * 1) AS activity_score,
    
    -- User type classification
    CASE 
        WHEN COALESCE(content_stats.total_facts, 0) >= 10 AND COALESCE(content_stats.total_comments, 0) >= 20 THEN 'power_user'
        WHEN COALESCE(content_stats.total_facts, 0) >= 5 OR COALESCE(content_stats.total_comments, 0) >= 10 THEN 'active_user'
        WHEN COALESCE(voting_stats.fact_votes_cast, 0) + COALESCE(voting_stats.comment_votes_cast, 0) >= 10 THEN 'engaged_voter'
        WHEN COALESCE(content_stats.total_facts, 0) + COALESCE(content_stats.total_comments, 0) > 0 THEN 'contributor'
        ELSE 'lurker'
    END AS user_type

FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id AND up.is_deleted = 0
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(CASE WHEN table_name = 'facts' THEN 1 END) as total_facts,
        COUNT(CASE WHEN table_name = 'comments' THEN 1 END) as total_comments,
        COUNT(CASE WHEN table_name = 'facts' AND created_at >= datetime('now', '-30 days') THEN 1 END) as facts_last_30_days,
        COUNT(CASE WHEN table_name = 'comments' AND created_at >= datetime('now', '-30 days') THEN 1 END) as comments_last_30_days
    FROM (
        SELECT user_id, created_at, 'facts' as table_name FROM facts WHERE is_deleted = 0
        UNION ALL
        SELECT user_id, created_at, 'comments' as table_name FROM comments WHERE is_deleted = 0
    ) combined_content
    GROUP BY user_id
) content_stats ON u.id = content_stats.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(CASE WHEN table_name = 'fact_votes' THEN 1 END) as fact_votes_cast,
        COUNT(CASE WHEN table_name = 'comment_votes' THEN 1 END) as comment_votes_cast,
        COUNT(CASE WHEN created_at >= datetime('now', '-30 days') THEN 1 END) as votes_last_30_days
    FROM (
        SELECT user_id, created_at, 'fact_votes' as table_name FROM fact_votes WHERE is_deleted = 0
        UNION ALL
        SELECT user_id, created_at, 'comment_votes' as table_name FROM comment_votes WHERE is_deleted = 0
    ) combined_votes
    GROUP BY user_id
) voting_stats ON u.id = voting_stats.user_id
LEFT JOIN (
    SELECT 
        f.user_id,
        COUNT(DISTINCT fv.id) as votes_received_on_facts,
        COUNT(DISTINCT cv.id) as votes_received_on_comments,
        COUNT(DISTINCT c.id) as comments_received_on_facts
    FROM facts f
    LEFT JOIN fact_votes fv ON f.id = fv.fact_id AND fv.is_deleted = 0
    LEFT JOIN comments c ON f.id = c.fact_id AND c.is_deleted = 0 AND c.user_id != f.user_id
    LEFT JOIN comment_votes cv ON c.id = cv.comment_id AND cv.is_deleted = 0
    WHERE f.is_deleted = 0
    GROUP BY f.user_id
) engagement_stats ON u.id = engagement_stats.user_id
WHERE u.is_deleted = 0;
