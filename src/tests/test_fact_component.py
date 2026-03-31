"""
Tests for fact component.
"""
import pytest
from app import db
from app.components.fact.services import FactManagementService, FactRetrievalService
from app.models import Fact, FactEditHistory


class TestFactManagementService:
    """Test fact management service functionality."""
    
    def test_create_fact_success(self, db_session, sample_user):
        """Test successful fact creation."""
        content = "This is a test fact about #science and #technology."
        
        success, message, fact = FactManagementService.create_fact(
            sample_user.id, content
        )
        
        assert success is True
        assert 'successful' in message
        assert fact is not None
        assert fact.user_id == sample_user.id
        assert fact.content == content
        assert fact.edit_count == 0
    
    def test_create_fact_invalid_content(self, db_session, sample_user):
        """Test fact creation with invalid content."""
        # Too short
        success, message, fact = FactManagementService.create_fact(
            sample_user.id, "Short"
        )
        
        assert success is False
        assert 'at least 10 characters' in message
        assert fact is None
    
    def test_create_fact_empty_content(self, db_session, sample_user):
        """Test fact creation with empty content."""
        success, message, fact = FactManagementService.create_fact(
            sample_user.id, ""
        )
        
        assert success is False
        assert 'required' in message
        assert fact is None
    
    def test_update_fact_success(self, db_session, sample_fact):
        """Test successful fact update."""
        new_content = "This is updated content for the test fact."
        edit_reason = "Fixed typo"
        
        success, message, updated_fact = FactManagementService.update_fact(
            sample_fact.id, sample_fact.user_id, new_content, edit_reason
        )
        
        assert success is True
        assert 'successful' in message
        assert updated_fact.content == new_content
        assert updated_fact.edit_count == 1
        assert updated_fact.last_edited_at is not None
        
        # Check edit history was created
        history = FactEditHistory.query.filter_by(fact_id=sample_fact.id).first()
        assert history is not None
        assert history.edit_reason == edit_reason
    
    def test_update_fact_not_owner(self, db_session, sample_fact, sample_user):
        """Test fact update by non-owner."""
        # Create another user
        from app.models import User
        other_user = User(
            email='other@example.com',
            password_hash='hash'
        )
        other_user.save()
        
        success, message, fact = FactManagementService.update_fact(
            sample_fact.id, other_user.id, "New content"
        )
        
        assert success is False
        assert 'only edit your own' in message
        assert fact is None
    
    def test_delete_fact_success(self, db_session, sample_fact):
        """Test successful fact deletion."""
        success, message = FactManagementService.delete_fact(
            sample_fact.id, sample_fact.user_id
        )
        
        assert success is True
        assert 'successful' in message
        
        # Check fact is soft deleted
        fact = db.session.get(Fact, sample_fact.id)
        assert fact.is_deleted is True
    
    def test_delete_fact_not_owner(self, db_session, sample_fact):
        """Test fact deletion by non-owner."""
        from app.models import User
        other_user = User(
            email='other@example.com',
            password_hash='hash'
        )
        other_user.save()
        
        success, message = FactManagementService.delete_fact(
            sample_fact.id, other_user.id
        )
        
        assert success is False
        assert 'only delete your own' in message
    
    def test_get_fact_edit_history(self, db_session, sample_fact):
        """Test getting fact edit history."""
        # Update fact to create history
        FactManagementService.update_fact(
            sample_fact.id, sample_fact.user_id, "Updated content", "Test edit"
        )
        
        history = FactManagementService.get_fact_edit_history(
            sample_fact.id, sample_fact.user_id
        )
        
        assert len(history) == 1
        assert history[0].edit_reason == "Test edit"


class TestFactRetrievalService:
    """Test fact retrieval service functionality."""
    
    def test_get_fact_by_id(self, db_session, sample_fact):
        """Test getting fact by ID."""
        fact = FactRetrievalService.get_fact_by_id(sample_fact.id)
        
        assert fact is not None
        assert fact.id == sample_fact.id
        assert fact.content == sample_fact.content
    
    def test_get_fact_by_id_not_found(self, db_session):
        """Test getting non-existent fact."""
        fact = FactRetrievalService.get_fact_by_id('nonexistent-id')
        assert fact is None
    
    def test_get_facts_paginated(self, db_session, multiple_facts):
        """Test paginated fact retrieval."""
        result = FactRetrievalService.get_facts_paginated(page=1, per_page=3)
        
        assert len(result['facts']) <= 3
        assert result['total'] == len(multiple_facts)
        assert result['current_page'] == 1
        assert isinstance(result['has_next'], bool)
        assert isinstance(result['has_prev'], bool)
    
    def test_get_facts_paginated_with_search(self, db_session, sample_user):
        """Test paginated fact retrieval with search."""
        # Create facts with specific content
        FactManagementService.create_fact(sample_user.id, "This fact is about science and research")
        FactManagementService.create_fact(sample_user.id, "This fact is about technology")
        FactManagementService.create_fact(sample_user.id, "This fact is about history")
        
        result = FactRetrievalService.get_facts_paginated(
            page=1, search_query="science"
        )
        
        assert len(result['facts']) == 1
        assert 'science' in result['facts'][0].content
    
    def test_get_recent_facts(self, db_session, multiple_facts):
        """Test getting recent facts."""
        recent_facts = FactRetrievalService.get_recent_facts(limit=3)
        
        assert len(recent_facts) <= 3
        # Should be ordered by creation date (newest first)
        if len(recent_facts) > 1:
            assert recent_facts[0].created_at >= recent_facts[1].created_at
    
    def test_get_user_facts(self, db_session, sample_user, multiple_facts):
        """Test getting facts by user."""
        user_facts = FactRetrievalService.get_user_facts(sample_user.id)
        
        assert len(user_facts) == len(multiple_facts)
        for fact in user_facts:
            assert fact.user_id == sample_user.id
    
    def test_search_facts(self, db_session, sample_user):
        """Test fact search functionality."""
        # Create facts with searchable content
        FactManagementService.create_fact(sample_user.id, "Climate change is a global issue")
        FactManagementService.create_fact(sample_user.id, "Technology advances rapidly")
        FactManagementService.create_fact(sample_user.id, "Climate affects weather patterns")
        
        results = FactRetrievalService.search_facts("climate")
        
        assert len(results) == 2
        for fact in results:
            assert 'climate' in fact.content.lower()
    
    def test_search_facts_short_query(self, db_session):
        """Test search with too short query."""
        results = FactRetrievalService.search_facts("ab")
        assert len(results) == 0
    
    def test_extract_hashtags_from_content(self, db_session):
        """Test hashtag extraction from content."""
        content = "This is about #science and #technology #AI"
        hashtags = FactRetrievalService.extract_hashtags_from_content(content)
        
        assert len(hashtags) == 3
        assert 'science' in hashtags
        assert 'technology' in hashtags
        assert 'ai' in hashtags
    
    def test_extract_hashtags_no_hashtags(self, db_session):
        """Test hashtag extraction with no hashtags."""
        content = "This content has no hashtags"
        hashtags = FactRetrievalService.extract_hashtags_from_content(content)
        
        assert len(hashtags) == 0
    
    def test_extract_hashtags_duplicates(self, db_session):
        """Test hashtag extraction with duplicates."""
        content = "This is about #science and #Science #SCIENCE"
        hashtags = FactRetrievalService.extract_hashtags_from_content(content)
        
        assert len(hashtags) == 1
        assert hashtags[0] == 'science'


class TestFactRoutes:
    """Test fact routes."""
    
    def test_fact_list_page(self, client, db_session):
        """Test fact list page."""
        response = client.get('/facts/')
        assert response.status_code == 200
        assert b'Facts' in response.data
    
    def test_fact_view_page(self, client, db_session, sample_fact):
        """Test fact view page."""
        response = client.get(f'/facts/{sample_fact.id}')
        assert response.status_code == 200
        assert sample_fact.content.encode() in response.data
    
    def test_fact_view_not_found(self, client, db_session):
        """Test viewing non-existent fact."""
        response = client.get('/facts/nonexistent-id')
        assert response.status_code == 404
    
    def test_fact_create_requires_auth(self, client, db_session):
        """Test that fact creation requires authentication."""
        response = client.get('/facts/new')
        assert response.status_code == 302  # Redirect to login
    
    def test_fact_edit_requires_auth(self, client, db_session, sample_fact):
        """Test that fact editing requires authentication."""
        response = client.get(f'/facts/{sample_fact.id}/edit')
        assert response.status_code == 302  # Redirect to login
