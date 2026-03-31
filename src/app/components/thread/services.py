"""
Thread management services for organizing discussions and managing conversation flow.
"""
from datetime import datetime, timedelta
from sqlalchemy import func, desc, asc, and_, or_
from flask import current_app
from app import db
from app.models import Fact, Comment, User, UserProfile, FactVote, CommentVote
from app.components.security.services import AuditService


class ThreadOrganizationService:
    """Service for organizing and managing discussion threads."""
    
    @staticmethod
    def get_thread_summary(fact_id):
        """
        Get a comprehensive summary of a discussion thread.
        
        Args:
            fact_id (str): Fact ID
            
        Returns:
            dict: Thread summary with statistics and metadata
        """
        try:
            # Get fact
            fact = db.session.get(Fact, fact_id)
            if not fact or fact.is_deleted:
                return None
            
            # Get comment statistics
            comment_stats = ThreadOrganizationService._get_comment_statistics(fact_id)
            
            # Get voting statistics
            vote_stats = ThreadOrganizationService._get_voting_statistics(fact_id)
            
            # Get participant statistics
            participant_stats = ThreadOrganizationService._get_participant_statistics(fact_id)
            
            # Get activity timeline
            activity_timeline = ThreadOrganizationService._get_activity_timeline(fact_id)
            
            # Calculate engagement metrics
            engagement_metrics = ThreadOrganizationService._calculate_engagement_metrics(
                fact_id, comment_stats, vote_stats, participant_stats
            )
            
            return {
                'fact_id': fact_id,
                'fact': fact,
                'comment_stats': comment_stats,
                'vote_stats': vote_stats,
                'participant_stats': participant_stats,
                'activity_timeline': activity_timeline,
                'engagement_metrics': engagement_metrics,
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting thread summary: {str(e)}")
            return None
    
    @staticmethod
    def get_trending_threads(limit=20, time_window_hours=24):
        """
        Get trending discussion threads based on recent activity.
        
        Args:
            limit (int): Maximum number of threads to return
            time_window_hours (int): Time window for trend analysis
            
        Returns:
            list: Trending threads with activity scores
        """
        try:
            since_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Get facts with recent activity (comments or votes)
            recent_activity = db.session.query(
                Fact.id.label('fact_id'),
                func.count(Comment.id).label('recent_comments'),
                func.count(FactVote.id).label('recent_votes')
            ).outerjoin(
                Comment, and_(
                    Comment.fact_id == Fact.id,
                    Comment.created_at >= since_time,
                    Comment.is_deleted == False
                )
            ).outerjoin(
                FactVote, and_(
                    FactVote.fact_id == Fact.id,
                    FactVote.created_at >= since_time,
                    FactVote.is_deleted == False
                )
            ).filter(
                Fact.is_deleted == False
            ).group_by(Fact.id).all()
            
            # Calculate trend scores
            trending_threads = []
            for activity in recent_activity:
                fact = db.session.get(Fact, activity.fact_id)
                if not fact:
                    continue
                
                # Calculate trend score based on recent activity
                comment_weight = 3  # Comments are worth more than votes
                vote_weight = 1
                
                trend_score = (
                    activity.recent_comments * comment_weight +
                    activity.recent_votes * vote_weight
                )
                
                # Boost score for newer facts
                fact_age_hours = (datetime.utcnow() - fact.created_at).total_seconds() / 3600
                if fact_age_hours < 24:
                    trend_score *= 1.5
                elif fact_age_hours < 72:
                    trend_score *= 1.2
                
                if trend_score > 0:
                    trending_threads.append({
                        'fact': fact,
                        'trend_score': trend_score,
                        'recent_comments': activity.recent_comments,
                        'recent_votes': activity.recent_votes,
                        'fact_age_hours': fact_age_hours
                    })
            
            # Sort by trend score and return top results
            trending_threads.sort(key=lambda x: x['trend_score'], reverse=True)
            return trending_threads[:limit]
            
        except Exception as e:
            current_app.logger.error(f"Error getting trending threads: {str(e)}")
            return []
    
    @staticmethod
    def get_active_discussions(limit=50):
        """
        Get currently active discussions with recent activity.
        
        Args:
            limit (int): Maximum number of discussions to return
            
        Returns:
            list: Active discussions with last activity timestamps
        """
        try:
            # Get facts with recent comments or votes
            active_discussions = db.session.query(
                Fact,
                func.max(Comment.created_at).label('last_comment'),
                func.max(FactVote.created_at).label('last_vote'),
                func.count(Comment.id).label('total_comments'),
                func.count(FactVote.id).label('total_votes')
            ).outerjoin(
                Comment, and_(
                    Comment.fact_id == Fact.id,
                    Comment.is_deleted == False
                )
            ).outerjoin(
                FactVote, and_(
                    FactVote.fact_id == Fact.id,
                    FactVote.is_deleted == False
                )
            ).filter(
                Fact.is_deleted == False
            ).group_by(Fact.id).all()
            
            # Process and sort by last activity
            discussions = []
            for discussion in active_discussions:
                fact = discussion[0]
                last_comment = discussion[1]
                last_vote = discussion[2]
                total_comments = discussion[3]
                total_votes = discussion[4]
                
                # Determine last activity time
                last_activity = fact.created_at
                if last_comment and last_comment > last_activity:
                    last_activity = last_comment
                if last_vote and last_vote > last_activity:
                    last_activity = last_vote
                
                discussions.append({
                    'fact': fact,
                    'last_activity': last_activity,
                    'total_comments': total_comments,
                    'total_votes': total_votes,
                    'activity_type': 'comment' if last_comment and last_comment == last_activity else 'vote' if last_vote and last_vote == last_activity else 'creation'
                })
            
            # Sort by last activity (most recent first)
            discussions.sort(key=lambda x: x['last_activity'], reverse=True)
            return discussions[:limit]
            
        except Exception as e:
            current_app.logger.error(f"Error getting active discussions: {str(e)}")
            return []
    
    @staticmethod
    def get_controversial_threads(limit=20):
        """
        Get controversial threads with high disagreement.
        
        Args:
            limit (int): Maximum number of threads to return
            
        Returns:
            list: Controversial threads with controversy scores
        """
        try:
            # Get facts with votes
            controversial_threads = []
            
            facts_with_votes = db.session.query(
                Fact,
                func.count(FactVote.id).label('total_votes'),
                func.sum(func.case([(FactVote.vote_type == 'fact', 1)], else_=0)).label('fact_votes'),
                func.sum(func.case([(FactVote.vote_type == 'fake', 1)], else_=0)).label('fake_votes')
            ).join(
                FactVote, and_(
                    FactVote.fact_id == Fact.id,
                    FactVote.is_deleted == False
                )
            ).filter(
                Fact.is_deleted == False
            ).group_by(Fact.id).having(
                func.count(FactVote.id) >= 10  # Minimum votes for controversy
            ).all()
            
            for fact_data in facts_with_votes:
                fact = fact_data[0]
                total_votes = fact_data[1] or 0
                fact_votes = fact_data[2] or 0
                fake_votes = fact_data[3] or 0
                
                if total_votes > 0:
                    # Calculate controversy score (higher when votes are more evenly split)
                    controversy_score = min(fact_votes, fake_votes) / total_votes * 100
                    
                    if controversy_score > 20:  # At least 20% minority opinion
                        controversial_threads.append({
                            'fact': fact,
                            'controversy_score': controversy_score,
                            'total_votes': total_votes,
                            'fact_votes': fact_votes,
                            'fake_votes': fake_votes,
                            'vote_split': f"{fact_votes}/{fake_votes}"
                        })
            
            # Sort by controversy score
            controversial_threads.sort(key=lambda x: x['controversy_score'], reverse=True)
            return controversial_threads[:limit]
            
        except Exception as e:
            current_app.logger.error(f"Error getting controversial threads: {str(e)}")
            return []
    
    @staticmethod
    def _get_comment_statistics(fact_id):
        """Get comment statistics for a fact."""
        try:
            stats = db.session.query(
                func.count(Comment.id).label('total_comments'),
                func.count(func.distinct(Comment.user_id)).label('unique_commenters'),
                func.max(Comment.depth).label('max_depth'),
                func.avg(func.length(Comment.content)).label('avg_comment_length'),
                func.min(Comment.created_at).label('first_comment'),
                func.max(Comment.created_at).label('last_comment')
            ).filter(
                Comment.fact_id == fact_id,
                Comment.is_deleted == False
            ).first()
            
            return {
                'total_comments': stats.total_comments or 0,
                'unique_commenters': stats.unique_commenters or 0,
                'max_depth': stats.max_depth or 0,
                'avg_comment_length': round(stats.avg_comment_length or 0, 1),
                'first_comment': stats.first_comment,
                'last_comment': stats.last_comment
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting comment statistics: {str(e)}")
            return {'total_comments': 0, 'unique_commenters': 0, 'max_depth': 0, 'avg_comment_length': 0}
    
    @staticmethod
    def _get_voting_statistics(fact_id):
        """Get voting statistics for a fact."""
        try:
            stats = db.session.query(
                func.count(FactVote.id).label('total_votes'),
                func.count(func.distinct(FactVote.user_id)).label('unique_voters'),
                func.sum(func.case([(FactVote.vote_type == 'fact', 1)], else_=0)).label('fact_votes'),
                func.sum(func.case([(FactVote.vote_type == 'fake', 1)], else_=0)).label('fake_votes'),
                func.min(FactVote.created_at).label('first_vote'),
                func.max(FactVote.created_at).label('last_vote')
            ).filter(
                FactVote.fact_id == fact_id,
                FactVote.is_deleted == False
            ).first()
            
            total_votes = stats.total_votes or 0
            fact_votes = stats.fact_votes or 0
            fake_votes = stats.fake_votes or 0
            
            return {
                'total_votes': total_votes,
                'unique_voters': stats.unique_voters or 0,
                'fact_votes': fact_votes,
                'fake_votes': fake_votes,
                'fact_percentage': round((fact_votes / total_votes * 100) if total_votes > 0 else 0, 1),
                'fake_percentage': round((fake_votes / total_votes * 100) if total_votes > 0 else 0, 1),
                'first_vote': stats.first_vote,
                'last_vote': stats.last_vote
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting voting statistics: {str(e)}")
            return {'total_votes': 0, 'unique_voters': 0, 'fact_votes': 0, 'fake_votes': 0}
    
    @staticmethod
    def _get_participant_statistics(fact_id):
        """Get participant statistics for a fact."""
        try:
            # Get all users who participated (commented or voted)
            commenters = db.session.query(Comment.user_id).filter(
                Comment.fact_id == fact_id,
                Comment.is_deleted == False
            ).distinct().subquery()
            
            voters = db.session.query(FactVote.user_id).filter(
                FactVote.fact_id == fact_id,
                FactVote.is_deleted == False
            ).distinct().subquery()
            
            # Count unique participants
            total_participants = db.session.query(
                func.count(func.distinct(
                    func.coalesce(commenters.c.user_id, voters.c.user_id)
                ))
            ).select_from(
                commenters.outerjoin(voters, commenters.c.user_id == voters.c.user_id)
            ).scalar() or 0
            
            return {
                'total_participants': total_participants,
                'commenters_only': db.session.query(commenters).count(),
                'voters_only': db.session.query(voters).count()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting participant statistics: {str(e)}")
            return {'total_participants': 0, 'commenters_only': 0, 'voters_only': 0}
    
    @staticmethod
    def _get_activity_timeline(fact_id, hours_back=168):  # 1 week
        """Get activity timeline for a fact."""
        try:
            since_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Get hourly activity counts
            timeline = []
            
            for hour in range(hours_back):
                hour_start = datetime.utcnow() - timedelta(hours=hour+1)
                hour_end = datetime.utcnow() - timedelta(hours=hour)
                
                comments = Comment.query.filter(
                    Comment.fact_id == fact_id,
                    Comment.created_at >= hour_start,
                    Comment.created_at < hour_end,
                    Comment.is_deleted == False
                ).count()
                
                votes = FactVote.query.filter(
                    FactVote.fact_id == fact_id,
                    FactVote.created_at >= hour_start,
                    FactVote.created_at < hour_end,
                    FactVote.is_deleted == False
                ).count()
                
                if comments > 0 or votes > 0:
                    timeline.append({
                        'hour': hour_start,
                        'comments': comments,
                        'votes': votes,
                        'total_activity': comments + votes
                    })
            
            return timeline
            
        except Exception as e:
            current_app.logger.error(f"Error getting activity timeline: {str(e)}")
            return []
    
    @staticmethod
    def _calculate_engagement_metrics(fact_id, comment_stats, vote_stats, participant_stats):
        """Calculate engagement metrics for a fact."""
        try:
            fact = db.session.get(Fact, fact_id)
            if not fact:
                return {}
            
            # Calculate time since creation
            fact_age_hours = (datetime.utcnow() - fact.created_at).total_seconds() / 3600
            fact_age_days = fact_age_hours / 24
            
            # Calculate engagement rates
            total_interactions = comment_stats['total_comments'] + vote_stats['total_votes']
            
            engagement_metrics = {
                'total_interactions': total_interactions,
                'interactions_per_day': round(total_interactions / max(fact_age_days, 1), 2),
                'comments_per_day': round(comment_stats['total_comments'] / max(fact_age_days, 1), 2),
                'votes_per_day': round(vote_stats['total_votes'] / max(fact_age_days, 1), 2),
                'participant_engagement_ratio': round(
                    total_interactions / max(participant_stats['total_participants'], 1), 2
                ),
                'fact_age_days': round(fact_age_days, 1),
                'discussion_health': ThreadOrganizationService._calculate_discussion_health(
                    comment_stats, vote_stats, participant_stats
                )
            }
            
            return engagement_metrics
            
        except Exception as e:
            current_app.logger.error(f"Error calculating engagement metrics: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_discussion_health(comment_stats, vote_stats, participant_stats):
        """Calculate discussion health score (0-100)."""
        try:
            health_score = 0
            
            # Participation diversity (30 points)
            if participant_stats['total_participants'] > 0:
                participation_score = min(participant_stats['total_participants'] / 10 * 30, 30)
                health_score += participation_score
            
            # Comment engagement (25 points)
            if comment_stats['total_comments'] > 0:
                comment_score = min(comment_stats['total_comments'] / 20 * 25, 25)
                health_score += comment_score
            
            # Voting engagement (25 points)
            if vote_stats['total_votes'] > 0:
                vote_score = min(vote_stats['total_votes'] / 50 * 25, 25)
                health_score += vote_score
            
            # Discussion depth (20 points)
            if comment_stats['max_depth'] > 0:
                depth_score = min(comment_stats['max_depth'] / 3 * 20, 20)
                health_score += depth_score
            
            return round(health_score, 1)
            
        except Exception as e:
            current_app.logger.error(f"Error calculating discussion health: {str(e)}")
            return 0


class ConversationFlowService:
    """Service for managing conversation flow and discussion quality."""
    
    @staticmethod
    def get_conversation_insights(fact_id):
        """
        Get insights about conversation patterns and quality.
        
        Args:
            fact_id (str): Fact ID
            
        Returns:
            dict: Conversation insights and recommendations
        """
        try:
            # Get thread summary
            thread_summary = ThreadOrganizationService.get_thread_summary(fact_id)
            if not thread_summary:
                return None
            
            insights = {
                'fact_id': fact_id,
                'conversation_quality': ConversationFlowService._assess_conversation_quality(thread_summary),
                'participation_patterns': ConversationFlowService._analyze_participation_patterns(fact_id),
                'discussion_recommendations': ConversationFlowService._generate_discussion_recommendations(thread_summary),
                'moderation_alerts': ConversationFlowService._check_moderation_needs(fact_id)
            }
            
            return insights
            
        except Exception as e:
            current_app.logger.error(f"Error getting conversation insights: {str(e)}")
            return None
    
    @staticmethod
    def _assess_conversation_quality(thread_summary):
        """Assess the quality of a conversation."""
        try:
            quality_metrics = {
                'overall_score': 0,
                'participation_diversity': 0,
                'discussion_depth': 0,
                'engagement_level': 0,
                'civility_score': 0
            }
            
            comment_stats = thread_summary['comment_stats']
            vote_stats = thread_summary['vote_stats']
            participant_stats = thread_summary['participant_stats']
            
            # Participation diversity (0-25 points)
            if participant_stats['total_participants'] > 0:
                diversity_score = min(participant_stats['total_participants'] / 15 * 25, 25)
                quality_metrics['participation_diversity'] = round(diversity_score, 1)
            
            # Discussion depth (0-25 points)
            if comment_stats['max_depth'] > 0:
                depth_score = min(comment_stats['max_depth'] / 4 * 25, 25)
                quality_metrics['discussion_depth'] = round(depth_score, 1)
            
            # Engagement level (0-25 points)
            total_interactions = comment_stats['total_comments'] + vote_stats['total_votes']
            if total_interactions > 0:
                engagement_score = min(total_interactions / 100 * 25, 25)
                quality_metrics['engagement_level'] = round(engagement_score, 1)
            
            # Civility score (0-25 points) - placeholder for now
            quality_metrics['civility_score'] = 20  # Assume good civility unless flagged
            
            # Calculate overall score
            quality_metrics['overall_score'] = round(
                quality_metrics['participation_diversity'] +
                quality_metrics['discussion_depth'] +
                quality_metrics['engagement_level'] +
                quality_metrics['civility_score'], 1
            )
            
            return quality_metrics
            
        except Exception as e:
            current_app.logger.error(f"Error assessing conversation quality: {str(e)}")
            return {'overall_score': 0}
    
    @staticmethod
    def _analyze_participation_patterns(fact_id):
        """Analyze participation patterns in a discussion."""
        try:
            # Get top commenters
            top_commenters = db.session.query(
                Comment.user_id,
                func.count(Comment.id).label('comment_count'),
                func.avg(func.length(Comment.content)).label('avg_length')
            ).filter(
                Comment.fact_id == fact_id,
                Comment.is_deleted == False
            ).group_by(Comment.user_id).order_by(
                desc('comment_count')
            ).limit(5).all()
            
            # Get voting patterns
            voting_patterns = db.session.query(
                FactVote.vote_type,
                func.count(FactVote.id).label('count')
            ).filter(
                FactVote.fact_id == fact_id,
                FactVote.is_deleted == False
            ).group_by(FactVote.vote_type).all()
            
            return {
                'top_commenters': [
                    {
                        'user_id': commenter.user_id,
                        'comment_count': commenter.comment_count,
                        'avg_comment_length': round(commenter.avg_length or 0, 1)
                    }
                    for commenter in top_commenters
                ],
                'voting_distribution': {
                    pattern.vote_type: pattern.count
                    for pattern in voting_patterns
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing participation patterns: {str(e)}")
            return {'top_commenters': [], 'voting_distribution': {}}
    
    @staticmethod
    def _generate_discussion_recommendations(thread_summary):
        """Generate recommendations to improve discussion quality."""
        try:
            recommendations = []
            
            comment_stats = thread_summary['comment_stats']
            vote_stats = thread_summary['vote_stats']
            participant_stats = thread_summary['participant_stats']
            engagement_metrics = thread_summary['engagement_metrics']
            
            # Low participation
            if participant_stats['total_participants'] < 5:
                recommendations.append({
                    'type': 'increase_participation',
                    'message': 'This discussion could benefit from more diverse perspectives. Consider sharing it with others.',
                    'priority': 'medium'
                })
            
            # Low engagement
            if engagement_metrics['interactions_per_day'] < 2:
                recommendations.append({
                    'type': 'boost_engagement',
                    'message': 'Discussion activity is low. Try asking thought-provoking questions or sharing additional resources.',
                    'priority': 'low'
                })
            
            # Shallow discussion
            if comment_stats['max_depth'] < 2 and comment_stats['total_comments'] > 5:
                recommendations.append({
                    'type': 'encourage_depth',
                    'message': 'Comments are mostly top-level. Encourage users to respond to each other for deeper discussion.',
                    'priority': 'medium'
                })
            
            # Voting imbalance
            if vote_stats['total_votes'] > 0:
                fact_percentage = vote_stats['fact_percentage']
                if fact_percentage > 90 or fact_percentage < 10:
                    recommendations.append({
                        'type': 'encourage_diverse_opinions',
                        'message': 'Voting is heavily one-sided. Consider presenting alternative viewpoints for balanced discussion.',
                        'priority': 'low'
                    })
            
            return recommendations
            
        except Exception as e:
            current_app.logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    @staticmethod
    def _check_moderation_needs(fact_id):
        """Check if discussion needs moderation attention."""
        try:
            alerts = []
            
            # Check for flagged comments
            flagged_comments = db.session.query(func.count(Comment.id)).filter(
                Comment.fact_id == fact_id,
                Comment.is_hidden == True,
                Comment.is_deleted == False
            ).scalar() or 0
            
            if flagged_comments > 0:
                alerts.append({
                    'type': 'flagged_content',
                    'message': f'{flagged_comments} comment(s) have been flagged and may need review.',
                    'severity': 'medium'
                })
            
            # Check for rapid activity (potential spam)
            recent_comments = Comment.query.filter(
                Comment.fact_id == fact_id,
                Comment.created_at >= datetime.utcnow() - timedelta(hours=1),
                Comment.is_deleted == False
            ).count()
            
            if recent_comments > 20:
                alerts.append({
                    'type': 'high_activity',
                    'message': f'{recent_comments} comments posted in the last hour. Monitor for spam or brigading.',
                    'severity': 'high'
                })
            
            return alerts
            
        except Exception as e:
            current_app.logger.error(f"Error checking moderation needs: {str(e)}")
            return []
