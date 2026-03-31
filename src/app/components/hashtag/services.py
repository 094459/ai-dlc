"""
Hashtag services for processing, storage, and fact categorization.
"""
import re
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from flask import current_app
from app import db
from app.models import Hashtag, FactHashtag, Fact
from app.components.security.services import AuditService


class HashtagProcessingService:
    """Service for hashtag processing and management."""
    
    @staticmethod
    def process_fact_hashtags(fact_id, content, user_id):
        """
        Process hashtags from fact content and create associations.
        
        Args:
            fact_id (str): Fact ID
            content (str): Fact content containing hashtags
            user_id (str): User ID for audit logging
            
        Returns:
            list: List of processed hashtags
        """
        try:
            # Extract hashtags from content
            hashtag_strings = HashtagProcessingService._extract_hashtags(content)
            
            if not hashtag_strings:
                return []
            
            processed_hashtags = []
            
            for tag_string in hashtag_strings:
                # Get or create hashtag
                hashtag = HashtagProcessingService._get_or_create_hashtag(tag_string)
                
                # Create fact-hashtag association if it doesn't exist
                existing_association = FactHashtag.query.filter_by(
                    fact_id=fact_id,
                    hashtag_id=hashtag.id,
                    is_deleted=False
                ).first()
                
                if not existing_association:
                    fact_hashtag = FactHashtag(
                        fact_id=fact_id,
                        hashtag_id=hashtag.id
                    )
                    fact_hashtag.save()
                    
                    # Update hashtag usage count
                    hashtag.usage_count += 1
                    hashtag.last_used_at = datetime.utcnow()
                    hashtag.save()
                
                processed_hashtags.append(hashtag)
            
            # Log hashtag processing
            AuditService.log_action(
                user_id=user_id,
                action_type='hashtag_process',
                resource_type='fact',
                resource_id=fact_id,
                new_values=', '.join(hashtag_strings),
                success=True
            )
            
            return processed_hashtags
            
        except Exception as e:
            current_app.logger.error(f"Hashtag processing error: {str(e)}")
            return []
    
    @staticmethod
    def update_fact_hashtags(fact_id, old_content, new_content, user_id):
        """
        Update hashtags when fact content changes.
        
        Args:
            fact_id (str): Fact ID
            old_content (str): Previous content
            new_content (str): New content
            user_id (str): User ID for audit logging
            
        Returns:
            list: List of current hashtags
        """
        try:
            # Extract hashtags from both contents
            old_hashtags = set(HashtagProcessingService._extract_hashtags(old_content))
            new_hashtags = set(HashtagProcessingService._extract_hashtags(new_content))
            
            # Find hashtags to remove and add
            hashtags_to_remove = old_hashtags - new_hashtags
            hashtags_to_add = new_hashtags - old_hashtags
            
            # Remove old hashtag associations
            for tag_string in hashtags_to_remove:
                HashtagProcessingService._remove_fact_hashtag(fact_id, tag_string)
            
            # Add new hashtag associations
            for tag_string in hashtags_to_add:
                hashtag = HashtagProcessingService._get_or_create_hashtag(tag_string)
                
                fact_hashtag = FactHashtag(
                    fact_id=fact_id,
                    hashtag_id=hashtag.id
                )
                fact_hashtag.save()
                
                # Update usage count
                hashtag.usage_count += 1
                hashtag.last_used_at = datetime.utcnow()
                hashtag.save()
            
            # Get current hashtags
            current_hashtags = HashtagProcessingService.get_fact_hashtags(fact_id)
            
            # Log hashtag update
            AuditService.log_action(
                user_id=user_id,
                action_type='hashtag_update',
                resource_type='fact',
                resource_id=fact_id,
                old_values=', '.join(old_hashtags),
                new_values=', '.join(new_hashtags),
                success=True
            )
            
            return current_hashtags
            
        except Exception as e:
            current_app.logger.error(f"Hashtag update error: {str(e)}")
            return []
    
    @staticmethod
    def remove_fact_hashtags(fact_id, user_id):
        """
        Remove all hashtags from a fact (when fact is deleted).
        
        Args:
            fact_id (str): Fact ID
            user_id (str): User ID for audit logging
        """
        try:
            # Get all fact hashtag associations
            fact_hashtags = FactHashtag.query.filter_by(
                fact_id=fact_id,
                is_deleted=False
            ).all()
            
            hashtag_names = []
            
            for fact_hashtag in fact_hashtags:
                # Get hashtag and decrease usage count
                hashtag = db.session.get(Hashtag, fact_hashtag.hashtag_id)
                if hashtag:
                    hashtag.usage_count = max(0, hashtag.usage_count - 1)
                    hashtag.save()
                    hashtag_names.append(hashtag.tag)
                
                # Soft delete association
                fact_hashtag.delete()
            
            # Log hashtag removal
            AuditService.log_action(
                user_id=user_id,
                action_type='hashtag_remove_all',
                resource_type='fact',
                resource_id=fact_id,
                old_values=', '.join(hashtag_names),
                success=True
            )
            
        except Exception as e:
            current_app.logger.error(f"Hashtag removal error: {str(e)}")
    
    @staticmethod
    def get_fact_hashtags(fact_id):
        """
        Get all hashtags for a fact.
        
        Args:
            fact_id (str): Fact ID
            
        Returns:
            list: List of Hashtag objects
        """
        try:
            return db.session.query(Hashtag).join(FactHashtag).filter(
                FactHashtag.fact_id == fact_id,
                FactHashtag.is_deleted == False,
                Hashtag.is_deleted == False
            ).order_by(Hashtag.tag).all()
            
        except Exception as e:
            current_app.logger.error(f"Error getting fact hashtags: {str(e)}")
            return []
    
    @staticmethod
    def _extract_hashtags(content):
        """
        Extract hashtags from content.
        
        Args:
            content (str): Text content
            
        Returns:
            list: List of hashtag strings (without #)
        """
        if not content:
            return []
        
        # Find hashtags using regex (# followed by word characters)
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, content, re.IGNORECASE)
        
        # Clean and deduplicate
        clean_hashtags = []
        seen = set()
        
        for tag in hashtags:
            clean_tag = tag.lower().strip()
            # Validate hashtag (2-50 characters, alphanumeric + underscore)
            if (clean_tag and 
                len(clean_tag) >= 2 and 
                len(clean_tag) <= 50 and 
                re.match(r'^[a-z0-9_]+$', clean_tag) and
                clean_tag not in seen):
                clean_hashtags.append(clean_tag)
                seen.add(clean_tag)
        
        return clean_hashtags[:10]  # Limit to 10 hashtags per fact
    
    @staticmethod
    def _get_or_create_hashtag(tag_string):
        """
        Get existing hashtag or create new one.
        
        Args:
            tag_string (str): Hashtag string (without #)
            
        Returns:
            Hashtag: Hashtag object
        """
        hashtag = Hashtag.query.filter_by(
            tag=tag_string.lower(),
            is_deleted=False
        ).first()
        
        if not hashtag:
            hashtag = Hashtag(
                tag=tag_string.lower(),
                usage_count=0,
                first_used_at=datetime.utcnow(),
                last_used_at=datetime.utcnow()
            )
            hashtag.save()
        
        return hashtag
    
    @staticmethod
    def _remove_fact_hashtag(fact_id, tag_string):
        """
        Remove a specific hashtag from a fact.
        
        Args:
            fact_id (str): Fact ID
            tag_string (str): Hashtag string to remove
        """
        hashtag = Hashtag.query.filter_by(
            tag=tag_string.lower(),
            is_deleted=False
        ).first()
        
        if hashtag:
            fact_hashtag = FactHashtag.query.filter_by(
                fact_id=fact_id,
                hashtag_id=hashtag.id,
                is_deleted=False
            ).first()
            
            if fact_hashtag:
                # Decrease usage count
                hashtag.usage_count = max(0, hashtag.usage_count - 1)
                hashtag.save()
                
                # Soft delete association
                fact_hashtag.delete()


class HashtagDiscoveryService:
    """Service for hashtag discovery and trending analysis."""
    
    @staticmethod
    def get_trending_hashtags(limit=20, days=7):
        """
        Get trending hashtags based on recent usage.
        
        Args:
            limit (int): Maximum number of hashtags to return
            days (int): Number of days to look back
            
        Returns:
            list: List of trending hashtags with usage stats
        """
        try:
            # Calculate date threshold
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Query for hashtags used in recent facts
            trending = db.session.query(
                Hashtag,
                func.count(FactHashtag.id).label('recent_usage')
            ).join(FactHashtag).join(Fact).filter(
                Fact.created_at >= since_date,
                Fact.is_deleted == False,
                FactHashtag.is_deleted == False,
                Hashtag.is_deleted == False
            ).group_by(Hashtag.id).order_by(
                desc('recent_usage'),
                desc(Hashtag.usage_count)
            ).limit(limit).all()
            
            result = []
            for hashtag, recent_usage in trending:
                result.append({
                    'hashtag': hashtag,
                    'recent_usage': recent_usage,
                    'total_usage': hashtag.usage_count,
                    'trend_score': recent_usage / max(1, hashtag.usage_count) * 100
                })
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error getting trending hashtags: {str(e)}")
            return []
    
    @staticmethod
    def get_popular_hashtags(limit=50):
        """
        Get most popular hashtags by total usage.
        
        Args:
            limit (int): Maximum number of hashtags to return
            
        Returns:
            list: List of popular hashtags
        """
        try:
            return Hashtag.query.filter(
                Hashtag.usage_count > 0,
                Hashtag.is_deleted == False
            ).order_by(
                desc(Hashtag.usage_count),
                Hashtag.tag
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f"Error getting popular hashtags: {str(e)}")
            return []
    
    @staticmethod
    def search_hashtags(query, limit=20):
        """
        Search hashtags by name.
        
        Args:
            query (str): Search query
            limit (int): Maximum results
            
        Returns:
            list: Matching hashtags
        """
        try:
            if not query or len(query.strip()) < 2:
                return []
            
            search_term = f"%{query.strip().lower()}%"
            
            return Hashtag.query.filter(
                Hashtag.tag.ilike(search_term),
                Hashtag.usage_count > 0,
                Hashtag.is_deleted == False
            ).order_by(
                desc(Hashtag.usage_count),
                Hashtag.tag
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f"Error searching hashtags: {str(e)}")
            return []
    
    @staticmethod
    def get_hashtag_stats(hashtag_id):
        """
        Get detailed statistics for a hashtag.
        
        Args:
            hashtag_id (str): Hashtag ID
            
        Returns:
            dict: Hashtag statistics
        """
        try:
            hashtag = db.session.get(Hashtag, hashtag_id)
            if not hashtag:
                return None
            
            # Get facts using this hashtag
            fact_count = db.session.query(func.count(FactHashtag.id)).filter(
                FactHashtag.hashtag_id == hashtag_id,
                FactHashtag.is_deleted == False
            ).scalar()
            
            # Get recent usage (last 30 days)
            since_date = datetime.utcnow() - timedelta(days=30)
            recent_usage = db.session.query(func.count(FactHashtag.id)).join(Fact).filter(
                FactHashtag.hashtag_id == hashtag_id,
                FactHashtag.is_deleted == False,
                Fact.created_at >= since_date,
                Fact.is_deleted == False
            ).scalar()
            
            return {
                'hashtag': hashtag,
                'total_facts': fact_count,
                'recent_usage_30d': recent_usage,
                'first_used': hashtag.first_used_at,
                'last_used': hashtag.last_used_at,
                'usage_count': hashtag.usage_count
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting hashtag stats: {str(e)}")
            return None
    
    @staticmethod
    def get_related_hashtags(hashtag_id, limit=10):
        """
        Get hashtags that are commonly used together with the given hashtag.
        
        Args:
            hashtag_id (str): Hashtag ID
            limit (int): Maximum results
            
        Returns:
            list: Related hashtags with co-occurrence count
        """
        try:
            # Find facts that use this hashtag
            fact_ids_subquery = db.session.query(FactHashtag.fact_id).filter(
                FactHashtag.hashtag_id == hashtag_id,
                FactHashtag.is_deleted == False
            ).subquery()
            
            # Find other hashtags used in those facts
            related = db.session.query(
                Hashtag,
                func.count(FactHashtag.fact_id).label('co_occurrence')
            ).join(FactHashtag).filter(
                FactHashtag.fact_id.in_(fact_ids_subquery),
                FactHashtag.hashtag_id != hashtag_id,
                FactHashtag.is_deleted == False,
                Hashtag.is_deleted == False
            ).group_by(Hashtag.id).order_by(
                desc('co_occurrence'),
                desc(Hashtag.usage_count)
            ).limit(limit).all()
            
            result = []
            for hashtag, co_occurrence in related:
                result.append({
                    'hashtag': hashtag,
                    'co_occurrence': co_occurrence,
                    'relatedness_score': co_occurrence / max(1, hashtag.usage_count) * 100
                })
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error getting related hashtags: {str(e)}")
            return []
