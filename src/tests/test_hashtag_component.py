"""
Tests for hashtag component.
"""
import pytest
from app.components.hashtag.services import HashtagProcessingService, HashtagDiscoveryService
from app.models import Hashtag, FactHashtag


class TestHashtagProcessingService:
    """Test hashtag processing service functionality."""
    
    def test_process_fact_hashtags(self, db_session, sample_fact, sample_user):
        """Test processing hashtags from fact content."""
        content = "This is about #science and #technology #AI"
        
        hashtags = HashtagProcessingService.process_fact_hashtags(
            sample_fact.id, content, sample_user.id
        )
        
        assert len(hashtags) == 3
        hashtag_tags = [h.tag for h in hashtags]
        assert 'science' in hashtag_tags
        assert 'technology' in hashtag_tags
        assert 'ai' in hashtag_tags
        
        # Check hashtags were created in database
        for hashtag in hashtags:
            assert hashtag.usage_count >= 1
            
        # Check fact-hashtag associations were created
        associations = FactHashtag.query.filter_by(fact_id=sample_fact.id).all()
        assert len(associations) == 3
    
    def test_process_fact_hashtags_no_hashtags(self, db_session, sample_fact, sample_user):
        """Test processing content with no hashtags."""
        content = "This content has no hashtags"
        
        hashtags = HashtagProcessingService.process_fact_hashtags(
            sample_fact.id, content, sample_user.id
        )
        
        assert len(hashtags) == 0
    
    def test_process_fact_hashtags_duplicates(self, db_session, sample_fact, sample_user):
        """Test processing content with duplicate hashtags."""
        content = "This is about #science and #Science #SCIENCE"
        
        hashtags = HashtagProcessingService.process_fact_hashtags(
            sample_fact.id, content, sample_user.id
        )
        
        assert len(hashtags) == 1
        assert hashtags[0].tag == 'science'
    
    def test_update_fact_hashtags(self, db_session, sample_fact, sample_user):
        """Test updating hashtags when fact content changes."""
        old_content = "This is about #science and #technology"
        new_content = "This is about #science and #AI #research"
        
        # First process old hashtags
        HashtagProcessingService.process_fact_hashtags(
            sample_fact.id, old_content, sample_user.id
        )
        
        # Then update with new content
        current_hashtags = HashtagProcessingService.update_fact_hashtags(
            sample_fact.id, old_content, new_content, sample_user.id
        )
        
        hashtag_tags = [h.tag for h in current_hashtags]
        assert 'science' in hashtag_tags  # Kept
        assert 'ai' in hashtag_tags       # Added
        assert 'research' in hashtag_tags # Added
        assert 'technology' not in hashtag_tags  # Removed
    
    def test_remove_fact_hashtags(self, db_session, sample_fact, sample_user):
        """Test removing all hashtags from a fact."""
        content = "This is about #science and #technology"
        
        # First add hashtags
        HashtagProcessingService.process_fact_hashtags(
            sample_fact.id, content, sample_user.id
        )
        
        # Check hashtags exist
        associations_before = FactHashtag.query.filter_by(
            fact_id=sample_fact.id, is_deleted=False
        ).count()
        assert associations_before == 2
        
        # Remove hashtags
        HashtagProcessingService.remove_fact_hashtags(sample_fact.id, sample_user.id)
        
        # Check hashtags are removed
        associations_after = FactHashtag.query.filter_by(
            fact_id=sample_fact.id, is_deleted=False
        ).count()
        assert associations_after == 0
    
    def test_get_fact_hashtags(self, db_session, sample_fact, sample_user):
        """Test getting hashtags for a fact."""
        content = "This is about #science and #technology"
        
        # Add hashtags
        HashtagProcessingService.process_fact_hashtags(
            sample_fact.id, content, sample_user.id
        )
        
        # Get hashtags
        hashtags = HashtagProcessingService.get_fact_hashtags(sample_fact.id)
        
        assert len(hashtags) == 2
        hashtag_tags = [h.tag for h in hashtags]
        assert 'science' in hashtag_tags
        assert 'technology' in hashtag_tags
    
    def test_extract_hashtags_valid(self):
        """Test hashtag extraction with valid hashtags."""
        content = "This is about #science and #technology #AI_research"
        
        hashtags = HashtagProcessingService._extract_hashtags(content)
        
        assert len(hashtags) == 3
        assert 'science' in hashtags
        assert 'technology' in hashtags
        assert 'ai_research' in hashtags
    
    def test_extract_hashtags_invalid_characters(self):
        """Test hashtag extraction with invalid characters."""
        content = "This has #invalid-hashtag and #valid_hashtag"
        
        hashtags = HashtagProcessingService._extract_hashtags(content)
        
        # The regex captures word characters, so it gets 'invalid' and 'valid_hashtag'
        # The validation happens in the cleaning step
        assert len(hashtags) == 2
        assert 'invalid' in hashtags  # Only the word part before the hyphen
        assert 'valid_hashtag' in hashtags
    
    def test_extract_hashtags_too_short(self):
        """Test hashtag extraction with too short hashtags."""
        content = "This has #a and #valid_hashtag"
        
        hashtags = HashtagProcessingService._extract_hashtags(content)
        
        assert len(hashtags) == 1
        assert 'valid_hashtag' in hashtags
        assert 'a' not in hashtags
    
    def test_extract_hashtags_too_long(self):
        """Test hashtag extraction with too long hashtags."""
        long_hashtag = 'a' * 51  # 51 characters
        content = f"This has #{long_hashtag} and #valid"
        
        hashtags = HashtagProcessingService._extract_hashtags(content)
        
        assert len(hashtags) == 1
        assert 'valid' in hashtags
        assert long_hashtag not in hashtags
    
    def test_extract_hashtags_limit(self):
        """Test hashtag extraction limit (max 10)."""
        hashtags_text = ' '.join([f'#tag{i}' for i in range(15)])
        content = f"This has many hashtags: {hashtags_text}"
        
        hashtags = HashtagProcessingService._extract_hashtags(content)
        
        assert len(hashtags) == 10  # Should be limited to 10


class TestHashtagDiscoveryService:
    """Test hashtag discovery service functionality."""
    
    def test_get_popular_hashtags(self, db_session, sample_user):
        """Test getting popular hashtags."""
        # Create some hashtags with different usage counts
        from app.models import Hashtag
        
        hashtag1 = Hashtag(tag='popular', usage_count=10)
        hashtag1.save()
        
        hashtag2 = Hashtag(tag='less_popular', usage_count=5)
        hashtag2.save()
        
        hashtag3 = Hashtag(tag='unused', usage_count=0)
        hashtag3.save()
        
        popular = HashtagDiscoveryService.get_popular_hashtags(limit=10)
        
        # Should only include hashtags with usage > 0
        assert len(popular) == 2
        assert popular[0].tag == 'popular'  # Most popular first
        assert popular[1].tag == 'less_popular'
    
    def test_search_hashtags(self, db_session):
        """Test hashtag search functionality."""
        from app.models import Hashtag
        
        # Create hashtags
        hashtag1 = Hashtag(tag='science_fiction', usage_count=5)
        hashtag1.save()
        
        hashtag2 = Hashtag(tag='computer_science', usage_count=3)
        hashtag2.save()
        
        hashtag3 = Hashtag(tag='technology', usage_count=2)
        hashtag3.save()
        
        results = HashtagDiscoveryService.search_hashtags('science')
        
        assert len(results) == 2
        hashtag_tags = [h.tag for h in results]
        assert 'science_fiction' in hashtag_tags
        assert 'computer_science' in hashtag_tags
        assert 'technology' not in hashtag_tags
    
    def test_search_hashtags_short_query(self, db_session):
        """Test hashtag search with short query."""
        results = HashtagDiscoveryService.search_hashtags('a')
        assert len(results) == 0
    
    def test_get_hashtag_stats(self, db_session, sample_fact, sample_user):
        """Test getting hashtag statistics."""
        # Create hashtag and associate with fact
        content = "This is about #science"
        hashtags = HashtagProcessingService.process_fact_hashtags(
            sample_fact.id, content, sample_user.id
        )
        
        hashtag = hashtags[0]
        stats = HashtagDiscoveryService.get_hashtag_stats(hashtag.id)
        
        assert stats is not None
        assert stats['hashtag'].id == hashtag.id
        assert stats['total_facts'] == 1
        assert stats['usage_count'] == 1
    
    def test_get_hashtag_stats_not_found(self, db_session):
        """Test getting stats for non-existent hashtag."""
        stats = HashtagDiscoveryService.get_hashtag_stats('nonexistent-id')
        assert stats is None
