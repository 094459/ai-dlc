-- Fact with Statistics View
-- Comprehensive view combining facts with voting statistics, comments, and author information

CREATE VIEW fact_with_statistics AS
SELECT 
    f.id AS fact_id,
    f.content,
    f.edit_count,
    f.last_edited_at,
    f.created_at,
    f.updated_at,
    
    -- Author information
    u.id AS author_id,
    up.name AS author_name,
    up.profile_photo_url AS author_photo,
    
    -- Voting statistics
    COALESCE(vs.total_votes, 0) AS total_votes,
    COALESCE(vs.positive_votes, 0) AS fact_votes,
    COALESCE(vs.negative_votes, 0) AS fake_votes,
    COALESCE(vs.vote_score, 0.0) AS vote_score,
    
    -- Vote percentages
    CASE 
        WHEN COALESCE(vs.total_votes, 0) > 0 
        THEN ROUND((COALESCE(vs.positive_votes, 0) * 100.0) / vs.total_votes, 1)
        ELSE 0.0 
    END AS fact_percentage,
    CASE 
        WHEN COALESCE(vs.total_votes, 0) > 0 
        THEN ROUND((COALESCE(vs.negative_votes, 0) * 100.0) / vs.total_votes, 1)
        ELSE 0.0 
    END AS fake_percentage,
    
    -- Comment statistics
    COALESCE(comment_stats.total_comments, 0) AS total_comments,
    COALESCE(comment_stats.top_level_comments, 0) AS top_level_comments,
    
    -- Resource statistics
    COALESCE(resource_stats.total_resources, 0) AS total_resources,
    COALESCE(resource_stats.url_resources, 0) AS url_resources,
    COALESCE(resource_stats.image_resources, 0) AS image_resources,
    
    -- Hashtag information
    COALESCE(hashtag_stats.hashtag_count, 0) AS hashtag_count,
    
    -- Engagement metrics
    CASE 
        WHEN COALESCE(vs.total_votes, 0) + COALESCE(comment_stats.total_comments, 0) > 0
        THEN COALESCE(vs.total_votes, 0) + COALESCE(comment_stats.total_comments, 0)
        ELSE 0
    END AS engagement_score

FROM facts f
JOIN users u ON f.user_id = u.id
LEFT JOIN user_profiles up ON u.id = up.user_id AND up.is_deleted = 0
LEFT JOIN vote_statistics vs ON f.id = vs.content_id AND vs.content_type = 'fact' AND vs.is_deleted = 0
LEFT JOIN (
    SELECT fact_id, 
           COUNT(*) as total_comments,
           COUNT(CASE WHEN parent_comment_id IS NULL THEN 1 END) as top_level_comments
    FROM comments 
    WHERE is_deleted = 0 
    GROUP BY fact_id
) comment_stats ON f.id = comment_stats.fact_id
LEFT JOIN (
    SELECT fact_id,
           COUNT(*) as total_resources,
           COUNT(CASE WHEN resource_type = 'url' THEN 1 END) as url_resources,
           COUNT(CASE WHEN resource_type = 'image' THEN 1 END) as image_resources
    FROM fact_resources 
    WHERE is_active = 1 AND is_deleted = 0
    GROUP BY fact_id
) resource_stats ON f.id = resource_stats.fact_id
LEFT JOIN (
    SELECT fh.fact_id, COUNT(*) as hashtag_count
    FROM fact_hashtags fh
    JOIN hashtags h ON fh.hashtag_id = h.id
    WHERE fh.is_deleted = 0 AND h.is_deleted = 0
    GROUP BY fh.fact_id
) hashtag_stats ON f.id = hashtag_stats.fact_id
WHERE f.is_deleted = 0 AND u.is_deleted = 0;
