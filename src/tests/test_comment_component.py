"""
Tests for comment component.
"""
import pytest
from datetime import datetime, timedelta
from app import db
from app.components.comment.services import CommentManagementService, CommentRetrievalService, CommentModerationService
from app.models import Comment, CommentEditHistory


class TestCommentManagementService:
    """Test comment management service functionality."""
    
    def test_create_comment_success(self, db_session, sample_fact, sample_user):
        """Test successful comment creation."""
        content = "This is a test comment about the fact."
        
        success, message, comment = CommentManagementService.create_comment(
            sample_user.id, sample_fact.id, content
        )
        
        assert success is True
        assert 'Comment posted successfully' == message
        assert comment is not None
        assert comment.user_id == sample_user.id
        assert comment.fact_id == sample_fact.id
        assert comment.content == content
        assert comment.nesting_level == 0
        assert comment.parent_comment_id is None
    
    def test_create_comment_invalid_content(self, db_session, sample_fact, sample_user):
        """Test comment creation with invalid content."""
        # Too short
        success, message, comment = CommentManagementService.create_comment(
            sample_user.id, sample_fact.id, "Hi"
        )
        
        assert success is False
        assert 'at least 3 characters' in message
        assert comment is None
    
    def test_create_comment_empty_content(self, db_session, sample_fact, sample_user):
        """Test comment creation with empty content."""
        success, message, comment = CommentManagementService.create_comment(
            sample_user.id, sample_fact.id, ""
        )
        
        assert success is False
        assert 'required' in message
        assert comment is None
    
    def test_create_reply_comment(self, db_session, sample_comment):
        """Test creating a reply to a comment."""
        from app.models import User
        replier = User(email='replier@example.com', password_hash='hash')
        replier.save()
        
        reply_content = "This is a reply to the comment."
        
        success, message, reply = CommentManagementService.create_comment(
            replier.id, sample_comment.fact_id, reply_content, sample_comment.id
        )
        
        assert success is True
        assert reply.parent_comment_id == sample_comment.id
        assert reply.nesting_level == 1
        assert reply.content == reply_content
    
    def test_create_comment_nonexistent_fact(self, db_session, sample_user):
        """Test creating comment on non-existent fact."""
        success, message, comment = CommentManagementService.create_comment(
            sample_user.id, 'nonexistent-id', 'Test comment'
        )
        
        assert success is False
        assert 'not found' in message
        assert comment is None
    
    def test_update_comment_success(self, db_session, sample_comment):
        """Test successful comment update."""
        new_content = "This is updated comment content."
        edit_reason = "Fixed typo"
        
        success, message, updated_comment = CommentManagementService.update_comment(
            sample_comment.id, sample_comment.user_id, new_content, edit_reason
        )
        
        assert success is True
        assert 'Comment updated successfully' == message
        assert updated_comment.content == new_content
        assert updated_comment.edit_count == 1
        assert updated_comment.updated_at is not None
        
        # Check edit history was created
        history = CommentEditHistory.query.filter_by(comment_id=sample_comment.id).first()
        assert history is not None
        assert history.edit_reason == edit_reason
    
    def test_update_comment_not_owner(self, db_session, sample_comment):
        """Test comment update by non-owner."""
        from app.models import User
        other_user = User(email='other@example.com', password_hash='hash')
        other_user.save()
        
        success, message, comment = CommentManagementService.update_comment(
            sample_comment.id, other_user.id, "New content"
        )
        
        assert success is False
        assert 'only edit your own' in message
        assert comment is None
    
    def test_delete_comment_success(self, db_session, sample_comment):
        """Test successful comment deletion."""
        success, message = CommentManagementService.delete_comment(
            sample_comment.id, sample_comment.user_id
        )
        
        assert success is True
        assert 'successful' in message
        
        # Check comment is soft deleted
        comment = db.session.get(Comment, sample_comment.id)
        assert comment.is_deleted is True
    
    def test_delete_comment_with_replies(self, db_session, sample_comment):
        """Test deleting comment with replies."""
        from app.models import User
        replier = User(email='replier@example.com', password_hash='hash')
        replier.save()
        
        # Create reply
        success, message, reply = CommentManagementService.create_comment(
            replier.id, sample_comment.fact_id, "Reply content", sample_comment.id
        )
        
        # Delete parent comment
        success, message = CommentManagementService.delete_comment(
            sample_comment.id, sample_comment.user_id
        )
        
        assert success is True
        
        # Check both parent and reply are deleted
        parent = db.session.get(Comment, sample_comment.id)
        reply_comment = db.session.get(Comment, reply.id)
        assert parent.is_deleted is True
        assert reply_comment.is_deleted is True


class TestCommentRetrievalService:
    """Test comment retrieval service functionality."""
    
    def test_get_fact_comments(self, db_session, sample_fact, sample_user):
        """Test getting comments for a fact."""
        # Create some comments
        for i in range(3):
            CommentManagementService.create_comment(
                sample_user.id, sample_fact.id, f"Comment {i}"
            )
        
        comments = CommentRetrievalService.get_fact_comments(sample_fact.id)
        
        assert len(comments) == 3
        # Should be ordered by creation time (oldest first)
        assert comments[0].content == "Comment 0"
        assert comments[2].content == "Comment 2"
    
    def test_get_fact_comments_with_replies(self, db_session, sample_fact, sample_user):
        """Test getting comments with threaded replies."""
        from app.models import User
        replier = User(email='replier@example.com', password_hash='hash')
        replier.save()
        
        # Create parent comment
        success, message, parent = CommentManagementService.create_comment(
            sample_user.id, sample_fact.id, "Parent comment"
        )
        
        # Create reply
        CommentManagementService.create_comment(
            replier.id, sample_fact.id, "Reply comment", parent.id
        )
        
        comments = CommentRetrievalService.get_fact_comments(sample_fact.id)
        
        assert len(comments) == 1  # Only top-level comment
        assert hasattr(comments[0], 'replies')
        assert len(comments[0].replies) == 1
        assert comments[0].replies[0].content == "Reply comment"
    
    def test_get_comment_with_author(self, db_session, sample_comment):
        """Test getting comment with author information."""
        # Create user profile for the comment author
        from app.models import UserProfile
        profile = UserProfile(
            user_id=sample_comment.user_id,
            name='Test User',
            biography='Test biography'
        )
        profile.save()
        
        comment_data = CommentRetrievalService.get_comment_with_author(sample_comment.id)
        
        assert comment_data is not None
        assert comment_data['comment'].id == sample_comment.id
        assert comment_data['author'] is not None
        assert comment_data['author_profile'] is not None
    
    def test_get_user_comments(self, db_session, sample_user, sample_fact):
        """Test getting comments by user."""
        # Create comments
        for i in range(3):
            CommentManagementService.create_comment(
                sample_user.id, sample_fact.id, f"User comment {i}"
            )
        
        user_comments = CommentRetrievalService.get_user_comments(sample_user.id)
        
        assert len(user_comments) == 3
        for comment in user_comments:
            assert comment.user_id == sample_user.id
    
    def test_get_comment_edit_history(self, db_session, sample_comment):
        """Test getting comment edit history."""
        # Update comment to create history
        CommentManagementService.update_comment(
            sample_comment.id, sample_comment.user_id, "Updated content", "Test edit"
        )
        
        history = CommentRetrievalService.get_comment_edit_history(
            sample_comment.id, sample_comment.user_id
        )
        
        assert len(history) == 1
        assert history[0].edit_reason == "Test edit"


class TestCommentModerationService:
    """Test comment moderation service functionality."""
    
    def test_flag_comment_success(self, db_session, sample_comment):
        """Test successful comment flagging."""
        from app.models import User
        flagger = User(email='flagger@example.com', password_hash='hash')
        flagger.save()
        
        success, message = CommentModerationService.flag_comment(
            sample_comment.id, flagger.id, "Inappropriate content"
        )
        
        assert success is True
        assert 'flagged' in message
    
    def test_flag_comment_twice(self, db_session, sample_comment):
        """Test flagging the same comment twice."""
        from app.models import User
        flagger = User(email='flagger@example.com', password_hash='hash')
        flagger.save()
        
        # First flag
        CommentModerationService.flag_comment(
            sample_comment.id, flagger.id, "Inappropriate content"
        )
        
        # Second flag by same user
        success, message = CommentModerationService.flag_comment(
            sample_comment.id, flagger.id, "Still inappropriate"
        )
        
        assert success is False
        assert 'already flagged' in message
    
    def test_moderate_comment_success(self, db_session, sample_comment):
        """Test successful comment moderation."""
        from app.models import User
        moderator = User(email='mod@example.com', password_hash='hash', is_moderator=True)
        moderator.save()
        
        success, message = CommentModerationService.moderate_comment(
            sample_comment.id, moderator.id, 'hide', 'Violates guidelines'
        )
        
        assert success is True
        assert 'hidden' in message
        
        # Check comment is hidden (soft deleted)
        comment = db.session.get(Comment, sample_comment.id)
        assert comment.is_deleted is True
    
    def test_moderate_comment_insufficient_permissions(self, db_session, sample_comment):
        """Test moderation by non-moderator."""
        from app.models import User
        regular_user = User(email='user@example.com', password_hash='hash')
        regular_user.save()
        
        success, message = CommentModerationService.moderate_comment(
            sample_comment.id, regular_user.id, 'hide', 'Reason'
        )
        
        assert success is False
        assert 'Insufficient permissions' in message


class TestCommentRoutes:
    """Test comment routes."""
    
    def test_create_comment_requires_auth(self, client, db_session, sample_fact):
        """Test that creating comments requires authentication."""
        response = client.post('/comments/create',
                              json={'fact_id': sample_fact.id, 'content': 'Test comment'})
        assert response.status_code == 401  # JSON request returns 401
        
        data = response.get_json()
        assert data['success'] is False
        assert 'Authentication required' in data['message']
    
    def test_get_fact_comments_public(self, client, db_session, sample_fact):
        """Test that getting comments is public."""
        response = client.get(f'/comments/fact/{sample_fact.id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'comments' in data
    
    def test_edit_comment_requires_auth(self, client, db_session, sample_comment):
        """Test that editing comments requires authentication."""
        response = client.get(f'/comments/{sample_comment.id}/edit')
        assert response.status_code == 302  # Redirect to login
