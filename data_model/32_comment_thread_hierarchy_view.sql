-- Comment Thread Hierarchy View
-- Hierarchical view of comments with threading information and statistics

CREATE VIEW comment_thread_hierarchy AS
SELECT 
    c.id AS comment_id,
    c.fact_id,
    c.user_id,
    c.parent_comment_id,
    c.content,
    c.nesting_level,
    c.reply_count,
    c.edit_count,
    c.created_at,
    c.updated_at,
    
    -- Author information
    up.name AS author_name,
    up.profile_photo_url AS author_photo,
    
    -- Thread information
    CASE 
        WHEN c.parent_comment_id IS NULL THEN c.id
        ELSE (
            SELECT CASE 
                WHEN c2.parent_comment_id IS NULL THEN c2.id
                ELSE (
                    SELECT CASE 
                        WHEN c3.parent_comment_id IS NULL THEN c3.id
                        ELSE c3.parent_comment_id
                    END
                    FROM comments c3 
                    WHERE c3.id = c2.parent_comment_id AND c3.is_deleted = 0
                )
            END
            FROM comments c2 
            WHERE c2.id = c.parent_comment_id AND c2.is_deleted = 0
        )
    END AS root_comment_id,
    
    -- Voting statistics
    COALESCE(vs.total_votes, 0) AS total_votes,
    COALESCE(vs.positive_votes, 0) AS upvotes,
    COALESCE(vs.negative_votes, 0) AS downvotes,
    COALESCE(vs.vote_score, 0.0) AS vote_score,
    
    -- Thread path for ordering (simplified for generic SQL)
    CASE 
        WHEN c.nesting_level = 0 THEN LPAD(c.created_at, 20, '0')
        WHEN c.nesting_level = 1 THEN 
            (SELECT LPAD(p.created_at, 20, '0') FROM comments p WHERE p.id = c.parent_comment_id) || 
            '.' || LPAD(c.created_at, 20, '0')
        WHEN c.nesting_level = 2 THEN
            (SELECT 
                CASE 
                    WHEN p.nesting_level = 0 THEN LPAD(p.created_at, 20, '0')
                    ELSE (SELECT LPAD(pp.created_at, 20, '0') FROM comments pp WHERE pp.id = p.parent_comment_id) || 
                         '.' || LPAD(p.created_at, 20, '0')
                END
             FROM comments p WHERE p.id = c.parent_comment_id) || 
            '.' || LPAD(c.created_at, 20, '0')
    END AS thread_path,
    
    -- Display indicators
    CASE 
        WHEN c.is_deleted = 1 THEN '[deleted]'
        ELSE c.content
    END AS display_content,
    
    -- Reply indicators
    CASE 
        WHEN c.reply_count > 0 THEN 1
        ELSE 0
    END AS has_replies,
    
    -- Edit indicators
    CASE 
        WHEN c.edit_count > 0 THEN 1
        ELSE 0
    END AS is_edited

FROM comments c
JOIN users u ON c.user_id = u.id
LEFT JOIN user_profiles up ON u.id = up.user_id AND up.is_deleted = 0
LEFT JOIN vote_statistics vs ON c.id = vs.content_id AND vs.content_type = 'comment' AND vs.is_deleted = 0
WHERE u.is_deleted = 0;
