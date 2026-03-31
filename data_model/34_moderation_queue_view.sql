-- Moderation Queue View
-- Comprehensive view for moderator workflow and report management

CREATE VIEW moderation_queue AS
SELECT 
    r.id AS report_id,
    r.status,
    r.priority,
    r.report_category,
    r.report_reason,
    r.created_at AS reported_at,
    r.resolved_at,
    
    -- Reporter information
    reporter.id AS reporter_id,
    reporter_profile.name AS reporter_name,
    
    -- Reported content information
    r.reported_content_type,
    r.reported_content_id,
    
    -- Content details (facts)
    CASE 
        WHEN r.reported_content_type = 'fact' THEN f.content
        ELSE NULL
    END AS fact_content,
    CASE 
        WHEN r.reported_content_type = 'fact' THEN fact_author_profile.name
        ELSE NULL
    END AS fact_author_name,
    
    -- Content details (comments)
    CASE 
        WHEN r.reported_content_type = 'comment' THEN c.content
        ELSE NULL
    END AS comment_content,
    CASE 
        WHEN r.reported_content_type = 'comment' THEN comment_author_profile.name
        ELSE NULL
    END AS comment_author_name,
    
    -- Content author information
    CASE 
        WHEN r.reported_content_type = 'fact' THEN f.user_id
        WHEN r.reported_content_type = 'comment' THEN c.user_id
        ELSE NULL
    END AS content_author_id,
    
    -- Assigned moderator information
    r.assigned_moderator_id,
    moderator_profile.name AS assigned_moderator_name,
    
    -- Content statistics
    CASE 
        WHEN r.reported_content_type = 'fact' THEN COALESCE(fact_votes.total_votes, 0)
        WHEN r.reported_content_type = 'comment' THEN COALESCE(comment_votes.total_votes, 0)
        ELSE 0
    END AS content_total_votes,
    
    -- Author moderation history
    COALESCE(umh.warning_count, 0) AS author_warning_count,
    COALESCE(umh.total_reports_against, 0) AS author_total_reports,
    COALESCE(umh.moderation_status, 'good_standing') AS author_moderation_status,
    COALESCE(umh.risk_score, 0) AS author_risk_score,
    
    -- Report age and priority scoring
    CASE 
        WHEN r.priority = 'urgent' THEN 100
        WHEN r.priority = 'high' THEN 75
        WHEN r.priority = 'normal' THEN 50
        WHEN r.priority = 'low' THEN 25
        ELSE 0
    END + 
    CASE 
        WHEN r.created_at <= datetime('now', '-7 days') THEN 20
        WHEN r.created_at <= datetime('now', '-3 days') THEN 10
        WHEN r.created_at <= datetime('now', '-1 day') THEN 5
        ELSE 0
    END AS priority_score,
    
    -- Workload indicators
    CASE 
        WHEN r.assigned_moderator_id IS NULL THEN 'unassigned'
        WHEN r.status = 'pending' THEN 'assigned_pending'
        WHEN r.status = 'under_review' THEN 'in_progress'
        ELSE r.status
    END AS workflow_status

FROM reports r
JOIN users reporter ON r.reporter_user_id = reporter.id
LEFT JOIN user_profiles reporter_profile ON reporter.id = reporter_profile.user_id AND reporter_profile.is_deleted = 0
LEFT JOIN users moderator ON r.assigned_moderator_id = moderator.id
LEFT JOIN user_profiles moderator_profile ON moderator.id = moderator_profile.user_id AND moderator_profile.is_deleted = 0

-- Join fact information if reported content is a fact
LEFT JOIN facts f ON r.reported_content_type = 'fact' AND r.reported_content_id = f.id
LEFT JOIN users fact_author ON f.user_id = fact_author.id
LEFT JOIN user_profiles fact_author_profile ON fact_author.id = fact_author_profile.user_id AND fact_author_profile.is_deleted = 0
LEFT JOIN vote_statistics fact_votes ON f.id = fact_votes.content_id AND fact_votes.content_type = 'fact' AND fact_votes.is_deleted = 0

-- Join comment information if reported content is a comment
LEFT JOIN comments c ON r.reported_content_type = 'comment' AND r.reported_content_id = c.id
LEFT JOIN users comment_author ON c.user_id = comment_author.id
LEFT JOIN user_profiles comment_author_profile ON comment_author.id = comment_author_profile.user_id AND comment_author_profile.is_deleted = 0
LEFT JOIN vote_statistics comment_votes ON c.id = comment_votes.content_id AND comment_votes.content_type = 'comment' AND comment_votes.is_deleted = 0

-- Join author moderation history
LEFT JOIN user_moderation_history umh ON 
    (r.reported_content_type = 'fact' AND f.user_id = umh.user_id) OR
    (r.reported_content_type = 'comment' AND c.user_id = umh.user_id)
    AND umh.is_deleted = 0

WHERE r.is_deleted = 0 AND reporter.is_deleted = 0;
