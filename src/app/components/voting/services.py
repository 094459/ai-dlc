"""
Voting services for fact and comment voting with fraud detection.
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from flask import current_app, request
from app import db
from app.models import FactVote, CommentVote, Fact, Comment, User
from app.components.security.services import AuditService


class VotingService:
    """Service for managing votes on facts and comments."""
    
    @staticmethod
    def vote_on_fact(user_id, fact_id, vote_type):
        """
        Cast or update a vote on a fact.
        
        Args:
            user_id (str): User ID casting the vote
            fact_id (str): Fact ID being voted on
            vote_type (str): 'fact' or 'fake'
            
        Returns:
            tuple: (success: bool, message: str, vote_counts: dict or None)
        """
        try:
            # Validate vote type
            if vote_type not in ['fact', 'fake']:
                return False, "Invalid vote type", None
            
            # Check if fact exists and is not deleted
            fact = db.session.get(Fact, fact_id)
            if not fact or fact.is_deleted:
                return False, "Fact not found", None
            
            # Check if user is trying to vote on their own fact
            if fact.user_id == user_id:
                return False, "You cannot vote on your own fact", None
            
            # Check for existing vote
            existing_vote = FactVote.query.filter_by(
                user_id=user_id,
                fact_id=fact_id,
                is_deleted=False
            ).first()
            
            if existing_vote:
                # Update existing vote if different
                if existing_vote.vote_type != vote_type:
                    old_vote_type = existing_vote.vote_type
                    existing_vote.vote_type = vote_type
                    existing_vote.updated_at = datetime.utcnow()
                    existing_vote.save()
                    
                    # Log vote change
                    AuditService.log_action(
                        user_id=user_id,
                        action_type='fact_vote_change',
                        resource_type='fact',
                        resource_id=fact_id,
                        old_values=old_vote_type,
                        new_values=vote_type,
                        success=True
                    )
                    
                    message = f"Vote changed to {vote_type}"
                else:
                    message = f"Vote already cast as {vote_type}"
            else:
                # Create new vote
                new_vote = FactVote(
                    user_id=user_id,
                    fact_id=fact_id,
                    vote_type=vote_type
                )
                new_vote.save()
                
                # Log new vote
                AuditService.log_action(
                    user_id=user_id,
                    action_type='fact_vote_cast',
                    resource_type='fact',
                    resource_id=fact_id,
                    new_values=vote_type,
                    success=True
                )
                
                message = f"Vote cast as {vote_type}"
            
            # Get updated vote counts
            vote_counts = VotingService.get_fact_vote_counts(fact_id)
            
            return True, message, vote_counts
            
        except Exception as e:
            current_app.logger.error(f"Fact voting error: {str(e)}")
            return False, "Failed to cast vote", None
    
    @staticmethod
    def vote_on_comment(user_id, comment_id, vote_type):
        """
        Cast or update a vote on a comment.
        
        Args:
            user_id (str): User ID casting the vote
            comment_id (str): Comment ID being voted on
            vote_type (str): 'helpful' or 'unhelpful'
            
        Returns:
            tuple: (success: bool, message: str, vote_counts: dict or None)
        """
        try:
            # Validate vote type
            if vote_type not in ['upvote', 'downvote']:
                return False, "Invalid vote type", None
            
            # Check if comment exists and is not deleted
            comment = db.session.get(Comment, comment_id)
            if not comment or comment.is_deleted:
                return False, "Comment not found", None
            
            # Check if user is trying to vote on their own comment
            if comment.user_id == user_id:
                return False, "You cannot vote on your own comment", None
            
            # Check for existing vote
            existing_vote = CommentVote.query.filter_by(
                user_id=user_id,
                comment_id=comment_id,
                is_deleted=False
            ).first()
            
            if existing_vote:
                # Update existing vote if different
                if existing_vote.vote_type != vote_type:
                    old_vote_type = existing_vote.vote_type
                    existing_vote.vote_type = vote_type
                    existing_vote.updated_at = datetime.utcnow()
                    existing_vote.save()
                    
                    # Log vote change
                    AuditService.log_action(
                        user_id=user_id,
                        action_type='comment_vote_change',
                        resource_type='comment',
                        resource_id=comment_id,
                        old_values=old_vote_type,
                        new_values=vote_type,
                        success=True
                    )
                    
                    message = f"Vote changed to {vote_type}"
                else:
                    message = f"Vote already cast as {vote_type}"
            else:
                # Create new vote
                new_vote = CommentVote(
                    user_id=user_id,
                    comment_id=comment_id,
                    vote_type=vote_type
                )
                new_vote.save()
                
                # Log new vote
                AuditService.log_action(
                    user_id=user_id,
                    action_type='comment_vote_cast',
                    resource_type='comment',
                    resource_id=comment_id,
                    new_values=vote_type,
                    success=True
                )
                
                message = f"Vote cast as {vote_type}"
            
            # Get updated vote counts
            vote_counts = VotingService.get_comment_vote_counts(comment_id)
            
            return True, message, vote_counts
            
        except Exception as e:
            current_app.logger.error(f"Comment voting error: {str(e)}")
            return False, "Failed to cast vote", None
    
    @staticmethod
    def remove_fact_vote(user_id, fact_id):
        """
        Remove a user's vote from a fact.
        
        Args:
            user_id (str): User ID
            fact_id (str): Fact ID
            
        Returns:
            tuple: (success: bool, message: str, vote_counts: dict or None)
        """
        try:
            # Find existing vote
            existing_vote = FactVote.query.filter_by(
                user_id=user_id,
                fact_id=fact_id,
                is_deleted=False
            ).first()
            
            if not existing_vote:
                return False, "No vote found to remove", None
            
            # Soft delete the vote
            old_vote_type = existing_vote.vote_type
            existing_vote.delete()
            
            # Log vote removal
            AuditService.log_action(
                user_id=user_id,
                action_type='fact_vote_remove',
                resource_type='fact',
                resource_id=fact_id,
                old_values=old_vote_type,
                success=True
            )
            
            # Get updated vote counts
            vote_counts = VotingService.get_fact_vote_counts(fact_id)
            
            return True, "Vote removed", vote_counts
            
        except Exception as e:
            current_app.logger.error(f"Vote removal error: {str(e)}")
            return False, "Failed to remove vote", None
    
    @staticmethod
    def remove_comment_vote(user_id, comment_id):
        """
        Remove a user's vote from a comment.
        
        Args:
            user_id (str): User ID
            comment_id (str): Comment ID
            
        Returns:
            tuple: (success: bool, message: str, vote_counts: dict or None)
        """
        try:
            # Find existing vote
            existing_vote = CommentVote.query.filter_by(
                user_id=user_id,
                comment_id=comment_id,
                is_deleted=False
            ).first()
            
            if not existing_vote:
                return False, "No vote found to remove", None
            
            # Soft delete the vote
            old_vote_type = existing_vote.vote_type
            existing_vote.delete()
            
            # Log vote removal
            AuditService.log_action(
                user_id=user_id,
                action_type='comment_vote_remove',
                resource_type='comment',
                resource_id=comment_id,
                old_values=old_vote_type,
                success=True
            )
            
            # Get updated vote counts
            vote_counts = VotingService.get_comment_vote_counts(comment_id)
            
            return True, "Vote removed", vote_counts
            
        except Exception as e:
            current_app.logger.error(f"Vote removal error: {str(e)}")
            return False, "Failed to remove vote", None
    
    @staticmethod
    def get_fact_vote_counts(fact_id):
        """
        Get vote counts for a fact.
        
        Args:
            fact_id (str): Fact ID
            
        Returns:
            dict: Vote counts and statistics
        """
        try:
            # Get vote counts by type
            fact_votes = db.session.query(
                FactVote.vote_type,
                func.count(FactVote.id).label('count')
            ).filter_by(
                fact_id=fact_id,
                is_deleted=False
            ).group_by(FactVote.vote_type).all()
            
            counts = {'fact': 0, 'fake': 0}
            for vote_type, count in fact_votes:
                counts[vote_type] = count
            
            # Calculate statistics
            total_votes = counts['fact'] + counts['fake']
            fact_percentage = (counts['fact'] / total_votes * 100) if total_votes > 0 else 0
            fake_percentage = (counts['fake'] / total_votes * 100) if total_votes > 0 else 0
            
            # Calculate controversy score (higher when votes are more evenly split)
            if total_votes > 0:
                controversy_score = min(counts['fact'], counts['fake']) / total_votes * 100
            else:
                controversy_score = 0
            
            return {
                'fact_votes': counts['fact'],
                'fake_votes': counts['fake'],
                'total_votes': total_votes,
                'fact_percentage': round(fact_percentage, 1),
                'fake_percentage': round(fake_percentage, 1),
                'controversy_score': round(controversy_score, 1),
                'consensus': 'fact' if counts['fact'] > counts['fake'] else 'fake' if counts['fake'] > counts['fact'] else 'disputed'
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting fact vote counts: {str(e)}")
            return {'fact_votes': 0, 'fake_votes': 0, 'total_votes': 0, 'fact_percentage': 0, 'fake_percentage': 0, 'controversy_score': 0, 'consensus': 'unknown'}
    
    @staticmethod
    def get_comment_vote_counts(comment_id):
        """
        Get vote counts for a comment.
        
        Args:
            comment_id (str): Comment ID
            
        Returns:
            dict: Vote counts and statistics
        """
        try:
            # Get vote counts by type
            comment_votes = db.session.query(
                CommentVote.vote_type,
                func.count(CommentVote.id).label('count')
            ).filter_by(
                comment_id=comment_id,
                is_deleted=False
            ).group_by(CommentVote.vote_type).all()
            
            counts = {'upvote': 0, 'downvote': 0}
            for vote_type, count in comment_votes:
                counts[vote_type] = count
            
            # Calculate statistics
            total_votes = counts['upvote'] + counts['downvote']
            upvote_percentage = (counts['upvote'] / total_votes * 100) if total_votes > 0 else 0
            downvote_percentage = (counts['downvote'] / total_votes * 100) if total_votes > 0 else 0
            
            # Calculate helpfulness score
            helpfulness_score = counts['upvote'] - counts['downvote']
            
            return {
                'helpful_votes': counts['upvote'],
                'unhelpful_votes': counts['downvote'],
                'total_votes': total_votes,
                'helpful_percentage': round(upvote_percentage, 1),
                'unhelpful_percentage': round(downvote_percentage, 1),
                'helpfulness_score': helpfulness_score,
                'rating': 'helpful' if helpfulness_score > 0 else 'unhelpful' if helpfulness_score < 0 else 'neutral'
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting comment vote counts: {str(e)}")
            return {'helpful_votes': 0, 'unhelpful_votes': 0, 'total_votes': 0, 'helpful_percentage': 0, 'unhelpful_percentage': 0, 'helpfulness_score': 0, 'rating': 'neutral'}
    
    @staticmethod
    def get_user_vote_on_fact(user_id, fact_id):
        """
        Get a user's current vote on a fact.
        
        Args:
            user_id (str): User ID
            fact_id (str): Fact ID
            
        Returns:
            str or None: Vote type or None if no vote
        """
        try:
            vote = FactVote.query.filter_by(
                user_id=user_id,
                fact_id=fact_id,
                is_deleted=False
            ).first()
            
            return vote.vote_type if vote else None
            
        except Exception as e:
            current_app.logger.error(f"Error getting user fact vote: {str(e)}")
            return None
    
    @staticmethod
    def get_user_vote_on_comment(user_id, comment_id):
        """
        Get a user's current vote on a comment.
        
        Args:
            user_id (str): User ID
            comment_id (str): Comment ID
            
        Returns:
            str or None: Vote type or None if no vote
        """
        try:
            vote = CommentVote.query.filter_by(
                user_id=user_id,
                comment_id=comment_id,
                is_deleted=False
            ).first()
            
            return vote.vote_type if vote else None
            
        except Exception as e:
            current_app.logger.error(f"Error getting user comment vote: {str(e)}")
            return None


class VoteFraudDetectionService:
    """Service for detecting and preventing vote fraud."""
    
    @staticmethod
    def detect_suspicious_voting_patterns(user_id, time_window_hours=24):
        """
        Detect suspicious voting patterns for a user.
        
        Args:
            user_id (str): User ID to check
            time_window_hours (int): Time window to analyze
            
        Returns:
            dict: Fraud detection results
        """
        try:
            since_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Count votes in time window
            fact_votes = FactVote.query.filter(
                FactVote.user_id == user_id,
                FactVote.created_at >= since_time,
                FactVote.is_deleted == False
            ).count()
            
            comment_votes = CommentVote.query.filter(
                CommentVote.user_id == user_id,
                CommentVote.created_at >= since_time,
                CommentVote.is_deleted == False
            ).count()
            
            total_votes = fact_votes + comment_votes
            
            # Define thresholds
            max_votes_per_hour = current_app.config.get('MAX_VOTES_PER_HOUR', 50)
            max_votes_per_day = current_app.config.get('MAX_VOTES_PER_DAY', 500)
            
            # Check for suspicious patterns
            suspicious_patterns = []
            risk_score = 0
            
            # Too many votes in short time
            if total_votes > max_votes_per_day:
                suspicious_patterns.append('excessive_voting_volume')
                risk_score += 30
            
            # Check for rapid voting (more than max per hour in any hour)
            hourly_votes = VoteFraudDetectionService._get_hourly_vote_counts(user_id, 24)
            max_hourly = max(hourly_votes) if hourly_votes else 0
            
            if max_hourly > max_votes_per_hour:
                suspicious_patterns.append('rapid_voting_burst')
                risk_score += 25
            
            # Check for voting only on one type (always fact or always fake)
            fact_vote_types = db.session.query(FactVote.vote_type).filter(
                FactVote.user_id == user_id,
                FactVote.created_at >= since_time,
                FactVote.is_deleted == False
            ).distinct().all()
            
            if len(fact_vote_types) == 1 and fact_votes > 10:
                suspicious_patterns.append('monotonic_voting_pattern')
                risk_score += 20
            
            # Check for voting from multiple IPs in short time (skip for now since no IP field)
            # ip_addresses = db.session.query(FactVote.ip_address).filter(
            #     FactVote.user_id == user_id,
            #     FactVote.created_at >= since_time,
            #     FactVote.is_deleted == False,
            #     FactVote.ip_address.isnot(None)
            # ).distinct().count()
            # 
            # if ip_addresses > 3:
            #     suspicious_patterns.append('multiple_ip_addresses')
            #     risk_score += 15
            
            # Determine risk level
            if risk_score >= 50:
                risk_level = 'high'
            elif risk_score >= 25:
                risk_level = 'medium'
            elif risk_score >= 10:
                risk_level = 'low'
            else:
                risk_level = 'none'
            
            return {
                'user_id': user_id,
                'time_window_hours': time_window_hours,
                'total_votes': total_votes,
                'fact_votes': fact_votes,
                'comment_votes': comment_votes,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'suspicious_patterns': suspicious_patterns,
                'max_hourly_votes': max_hourly,
                'unique_ip_addresses': 0  # Not tracking IPs currently
            }
            
        except Exception as e:
            current_app.logger.error(f"Fraud detection error: {str(e)}")
            return {
                'user_id': user_id,
                'risk_level': 'unknown',
                'error': str(e)
            }
    
    @staticmethod
    def _get_hourly_vote_counts(user_id, hours_back=24):
        """
        Get vote counts per hour for the specified time period.
        
        Args:
            user_id (str): User ID
            hours_back (int): Hours to look back
            
        Returns:
            list: Vote counts per hour
        """
        try:
            since_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Get votes grouped by hour
            hourly_counts = []
            
            for hour in range(hours_back):
                hour_start = datetime.utcnow() - timedelta(hours=hour+1)
                hour_end = datetime.utcnow() - timedelta(hours=hour)
                
                fact_votes = FactVote.query.filter(
                    FactVote.user_id == user_id,
                    FactVote.created_at >= hour_start,
                    FactVote.created_at < hour_end,
                    FactVote.is_deleted == False
                ).count()
                
                comment_votes = CommentVote.query.filter(
                    CommentVote.user_id == user_id,
                    CommentVote.created_at >= hour_start,
                    CommentVote.created_at < hour_end,
                    CommentVote.is_deleted == False
                ).count()
                
                hourly_counts.append(fact_votes + comment_votes)
            
            return hourly_counts
            
        except Exception as e:
            current_app.logger.error(f"Error getting hourly vote counts: {str(e)}")
            return []
    
    @staticmethod
    def should_block_vote(user_id):
        """
        Determine if a user's vote should be blocked due to suspicious activity.
        
        Args:
            user_id (str): User ID
            
        Returns:
            tuple: (should_block: bool, reason: str)
        """
        try:
            # Check recent fraud detection results
            fraud_results = VoteFraudDetectionService.detect_suspicious_voting_patterns(user_id, 1)  # Last hour
            
            if fraud_results['risk_level'] == 'high':
                return True, "Suspicious voting activity detected"
            
            # Check if user has been flagged recently
            recent_flags = AuditService.get_user_audit_trail(user_id, 10)
            fraud_flags = [log for log in recent_flags if 'fraud' in log.action.lower()]
            
            if len(fraud_flags) > 2:
                return True, "Multiple fraud flags detected"
            
            return False, "No suspicious activity"
            
        except Exception as e:
            current_app.logger.error(f"Vote blocking check error: {str(e)}")
            return False, "Error checking vote eligibility"
