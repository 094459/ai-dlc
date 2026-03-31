"""
Tests for voting component.
"""
import pytest
from app import db
from app.components.voting.services import VotingService, VoteFraudDetectionService
from app.models import FactVote, CommentVote


class TestVotingService:
    """Test voting service functionality."""
    
    def test_vote_on_fact_success(self, db_session, sample_fact, sample_user):
        """Test successful fact voting."""
        # Create another user to vote (can't vote on own fact)
        from app.models import User
        voter = User(email='voter@example.com', password_hash='hash')
        voter.save()
        
        success, message, vote_counts = VotingService.vote_on_fact(
            voter.id, sample_fact.id, 'fact'
        )
        
        assert success is True
        assert 'Vote cast as fact' == message
        assert vote_counts['fact_votes'] == 1
        assert vote_counts['fake_votes'] == 0
        assert vote_counts['total_votes'] == 1
        
        # Check vote was created
        vote = FactVote.query.filter_by(
            user_id=voter.id,
            fact_id=sample_fact.id
        ).first()
        assert vote is not None
        assert vote.vote_type == 'fact'
    
    def test_vote_on_own_fact(self, db_session, sample_fact):
        """Test that users cannot vote on their own facts."""
        success, message, vote_counts = VotingService.vote_on_fact(
            sample_fact.user_id, sample_fact.id, 'fact'
        )
        
        assert success is False
        assert 'cannot vote on your own' in message
        assert vote_counts is None
    
    def test_vote_on_nonexistent_fact(self, db_session, sample_user):
        """Test voting on non-existent fact."""
        success, message, vote_counts = VotingService.vote_on_fact(
            sample_user.id, 'nonexistent-id', 'fact'
        )
        
        assert success is False
        assert 'not found' in message
        assert vote_counts is None
    
    def test_invalid_vote_type(self, db_session, sample_fact, sample_user):
        """Test voting with invalid vote type."""
        from app.models import User
        voter = User(email='voter@example.com', password_hash='hash')
        voter.save()
        
        success, message, vote_counts = VotingService.vote_on_fact(
            voter.id, sample_fact.id, 'invalid'
        )
        
        assert success is False
        assert 'Invalid vote type' in message
        assert vote_counts is None
    
    def test_change_vote(self, db_session, sample_fact):
        """Test changing a vote."""
        from app.models import User
        voter = User(email='voter@example.com', password_hash='hash')
        voter.save()
        
        # First vote
        VotingService.vote_on_fact(voter.id, sample_fact.id, 'fact')
        
        # Change vote
        success, message, vote_counts = VotingService.vote_on_fact(
            voter.id, sample_fact.id, 'fake'
        )
        
        assert success is True
        assert 'changed' in message
        assert vote_counts['fact_votes'] == 0
        assert vote_counts['fake_votes'] == 1
        
        # Check only one vote exists
        votes = FactVote.query.filter_by(
            user_id=voter.id,
            fact_id=sample_fact.id,
            is_deleted=False
        ).all()
        assert len(votes) == 1
        assert votes[0].vote_type == 'fake'
    
    def test_vote_on_comment_success(self, db_session, sample_comment):
        """Test successful comment voting."""
        from app.models import User
        voter = User(email='voter@example.com', password_hash='hash')
        voter.save()
        
        success, message, vote_counts = VotingService.vote_on_comment(
            voter.id, sample_comment.id, 'upvote'
        )
        
        assert success is True
        assert 'Vote cast as upvote' == message
        assert vote_counts['helpful_votes'] == 1
        assert vote_counts['unhelpful_votes'] == 0
        assert vote_counts['helpfulness_score'] == 1
    
    def test_remove_fact_vote(self, db_session, sample_fact):
        """Test removing a fact vote."""
        from app.models import User
        voter = User(email='voter@example.com', password_hash='hash')
        voter.save()
        
        # First vote
        VotingService.vote_on_fact(voter.id, sample_fact.id, 'fact')
        
        # Remove vote
        success, message, vote_counts = VotingService.remove_fact_vote(
            voter.id, sample_fact.id
        )
        
        assert success is True
        assert 'removed' in message
        assert vote_counts['fact_votes'] == 0
        assert vote_counts['fake_votes'] == 0
    
    def test_get_fact_vote_counts(self, db_session, sample_fact):
        """Test getting fact vote counts."""
        from app.models import User
        
        # Create voters
        voter1 = User(email='voter1@example.com', password_hash='hash')
        voter1.save()
        voter2 = User(email='voter2@example.com', password_hash='hash')
        voter2.save()
        voter3 = User(email='voter3@example.com', password_hash='hash')
        voter3.save()
        
        # Cast votes
        VotingService.vote_on_fact(voter1.id, sample_fact.id, 'fact')
        VotingService.vote_on_fact(voter2.id, sample_fact.id, 'fact')
        VotingService.vote_on_fact(voter3.id, sample_fact.id, 'fake')
        
        vote_counts = VotingService.get_fact_vote_counts(sample_fact.id)
        
        assert vote_counts['fact_votes'] == 2
        assert vote_counts['fake_votes'] == 1
        assert vote_counts['total_votes'] == 3
        assert vote_counts['fact_percentage'] == 66.7
        assert vote_counts['fake_percentage'] == 33.3
        assert vote_counts['consensus'] == 'fact'
    
    def test_get_user_vote_on_fact(self, db_session, sample_fact):
        """Test getting user's vote on a fact."""
        from app.models import User
        voter = User(email='voter@example.com', password_hash='hash')
        voter.save()
        
        # No vote initially
        user_vote = VotingService.get_user_vote_on_fact(voter.id, sample_fact.id)
        assert user_vote is None
        
        # After voting
        VotingService.vote_on_fact(voter.id, sample_fact.id, 'fact')
        user_vote = VotingService.get_user_vote_on_fact(voter.id, sample_fact.id)
        assert user_vote == 'fact'


class TestVoteFraudDetectionService:
    """Test vote fraud detection service functionality."""
    
    def test_detect_suspicious_voting_patterns_normal(self, db_session, sample_user):
        """Test fraud detection with normal voting patterns."""
        fraud_results = VoteFraudDetectionService.detect_suspicious_voting_patterns(
            sample_user.id, 24
        )
        
        assert fraud_results['risk_level'] == 'none'
        assert fraud_results['total_votes'] == 0
        assert fraud_results['suspicious_patterns'] == []
    
    def test_detect_excessive_voting(self, db_session, sample_user):
        """Test detection of excessive voting."""
        from app.models import User, Fact
        
        # Create many facts and votes
        for i in range(60):  # Create 60 different facts
            fact_owner = User(email=f'owner{i}@example.com', password_hash='hash')
            fact_owner.save()
            
            fact = Fact(user_id=fact_owner.id, content=f'Test fact {i}')
            fact.save()
            
            # Vote on each fact once (one user, many facts)
            vote = FactVote(
                user_id=sample_user.id,
                fact_id=fact.id,
                vote_type='fact'
            )
            vote.save()
        
        fraud_results = VoteFraudDetectionService.detect_suspicious_voting_patterns(
            sample_user.id, 24
        )
        
        assert fraud_results['risk_level'] in ['medium', 'high']
        assert fraud_results['total_votes'] == 60
        assert 'rapid_voting_burst' in fraud_results['suspicious_patterns']
        assert 'monotonic_voting_pattern' in fraud_results['suspicious_patterns']
    
    def test_should_block_vote_normal_user(self, db_session, sample_user):
        """Test vote blocking for normal user."""
        should_block, reason = VoteFraudDetectionService.should_block_vote(sample_user.id)
        
        assert should_block is False
        assert 'No suspicious activity' in reason


class TestVotingRoutes:
    """Test voting routes."""
    
    def test_vote_fact_requires_auth(self, client, db_session, sample_fact):
        """Test that voting requires authentication."""
        response = client.post(f'/api/voting/fact/{sample_fact.id}',
                              json={'vote_type': 'fact'})
        assert response.status_code == 401  # JSON request returns 401
        
        data = response.get_json()
        assert data['success'] is False
        assert 'Authentication required' in data['message']
    
    def test_get_fact_vote_counts_public(self, client, db_session, sample_fact):
        """Test that getting vote counts is public."""
        response = client.get(f'/api/voting/fact/{sample_fact.id}/counts')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'vote_counts' in data
