"""
Fact services for fact management including creation, editing, deletion, and retrieval.
"""
import re
from datetime import datetime
from flask import current_app
from sqlalchemy import or_, and_
from app import db
from app.models import Fact, FactEditHistory, User, UserProfile
from app.components.security.services import ValidationService, AuditService


class FactManagementService:
    """Service for fact creation, editing, and deletion."""
    
    @staticmethod
    def create_fact(user_id, content):
        """
        Create a new fact.
        
        Args:
            user_id (str): User ID creating the fact
            content (str): Fact content
            
        Returns:
            tuple: (success: bool, message: str, fact: Fact or None)
        """
        try:
            # Validate content
            content_valid, content_msg = ValidationService.validate_fact_content(content)
            if not content_valid:
                return False, content_msg, None
            
            # Sanitize content
            sanitized_content = ValidationService.sanitize_html(content.strip())
            
            # Create fact
            fact = Fact(
                user_id=user_id,
                content=sanitized_content
            )
            fact.save()
            
            # Log creation
            AuditService.log_action(
                user_id=user_id,
                action_type='fact_create',
                resource_type='fact',
                resource_id=fact.id,
                new_values=sanitized_content,
                success=True
            )
            
            return True, "Fact created successfully", fact
            
        except Exception as e:
            current_app.logger.error(f"Fact creation error: {str(e)}")
            return False, "Failed to create fact", None
    
    @staticmethod
    def update_fact(fact_id, user_id, content, edit_reason=None):
        """
        Update an existing fact.
        
        Args:
            fact_id (str): Fact ID
            user_id (str): User ID making the edit
            content (str): New content
            edit_reason (str): Reason for edit
            
        Returns:
            tuple: (success: bool, message: str, fact: Fact or None)
        """
        try:
            # Get fact
            fact = Fact.query.filter_by(
                id=fact_id,
                is_deleted=False
            ).first()
            
            if not fact:
                return False, "Fact not found", None
            
            # Check ownership
            if fact.user_id != user_id:
                return False, "You can only edit your own facts", None
            
            # Validate content
            content_valid, content_msg = ValidationService.validate_fact_content(content)
            if not content_valid:
                return False, content_msg, None
            
            # Sanitize content
            sanitized_content = ValidationService.sanitize_html(content.strip())
            
            # Save edit history
            edit_history = FactEditHistory(
                fact_id=fact.id,
                previous_content=fact.content,
                edit_reason=edit_reason
            )
            edit_history.save()
            
            # Update fact
            old_content = fact.content
            fact.content = sanitized_content
            fact.edit_count += 1
            fact.last_edited_at = datetime.utcnow()
            fact.save()
            
            # Log update
            AuditService.log_action(
                user_id=user_id,
                action_type='fact_update',
                resource_type='fact',
                resource_id=fact.id,
                old_values=old_content,
                new_values=sanitized_content,
                success=True
            )
            
            return True, "Fact updated successfully", fact
            
        except Exception as e:
            current_app.logger.error(f"Fact update error: {str(e)}")
            return False, "Failed to update fact", None
    
    @staticmethod
    def delete_fact(fact_id, user_id):
        """
        Delete a fact (soft delete).
        
        Args:
            fact_id (str): Fact ID
            user_id (str): User ID requesting deletion
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Get fact
            fact = Fact.query.filter_by(
                id=fact_id,
                is_deleted=False
            ).first()
            
            if not fact:
                return False, "Fact not found"
            
            # Check ownership
            if fact.user_id != user_id:
                return False, "You can only delete your own facts"
            
            # Soft delete
            fact.delete()
            
            # Log deletion
            AuditService.log_action(
                user_id=user_id,
                action_type='fact_delete',
                resource_type='fact',
                resource_id=fact.id,
                old_values=fact.content,
                success=True
            )
            
            return True, "Fact deleted successfully"
            
        except Exception as e:
            current_app.logger.error(f"Fact deletion error: {str(e)}")
            return False, "Failed to delete fact"
    
    @staticmethod
    def get_fact_edit_history(fact_id, user_id):
        """
        Get edit history for a fact.
        
        Args:
            fact_id (str): Fact ID
            user_id (str): User ID requesting history
            
        Returns:
            list: Edit history entries or empty list
        """
        try:
            # Get fact and check ownership
            fact = Fact.query.filter_by(
                id=fact_id,
                user_id=user_id,
                is_deleted=False
            ).first()
            
            if not fact:
                return []
            
            return FactEditHistory.query.filter_by(
                fact_id=fact_id,
                is_deleted=False
            ).order_by(FactEditHistory.created_at.desc()).all()
            
        except Exception as e:
            current_app.logger.error(f"Error getting fact history: {str(e)}")
            return []


class FactRetrievalService:
    """Service for fact search, filtering, and retrieval."""
    
    @staticmethod
    def get_fact_by_id(fact_id, include_deleted=False):
        """
        Get a fact by ID.
        
        Args:
            fact_id (str): Fact ID
            include_deleted (bool): Whether to include deleted facts
            
        Returns:
            Fact or None: Fact if found
        """
        query = Fact.query.filter_by(id=fact_id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        
        return query.first()
    
    @staticmethod
    def get_facts_paginated(page=1, per_page=None, user_id=None, search_query=None, 
                           hashtag=None, sort_by='recent'):
        """
        Get paginated facts with filtering and sorting.
        
        Args:
            page (int): Page number
            per_page (int): Items per page
            user_id (str): Filter by user ID
            search_query (str): Search in content
            hashtag (str): Filter by hashtag
            sort_by (str): Sort method ('recent', 'popular', 'controversial')
            
        Returns:
            dict: Pagination object with facts and metadata
        """
        try:
            if per_page is None:
                per_page = current_app.config.get('POSTS_PER_PAGE', 20)
            
            # Base query
            query = db.session.query(Fact).filter_by(is_deleted=False)
            
            # Apply filters
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            if search_query:
                search_term = f"%{search_query}%"
                query = query.filter(Fact.content.ilike(search_term))
            
            if hashtag:
                from app.models import FactHashtag, Hashtag
                query = query.join(FactHashtag).join(Hashtag).filter(
                    Hashtag.tag == hashtag.lower()
                )
            
            # Apply sorting
            if sort_by == 'recent':
                query = query.order_by(Fact.created_at.desc())
            elif sort_by == 'popular':
                # TODO: Sort by vote score when voting is implemented
                query = query.order_by(Fact.created_at.desc())
            elif sort_by == 'controversial':
                # TODO: Sort by controversy score when voting is implemented
                query = query.order_by(Fact.created_at.desc())
            else:
                query = query.order_by(Fact.created_at.desc())
            
            # Paginate
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'facts': pagination.items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            }
            
        except Exception as e:
            current_app.logger.error(f"Error retrieving facts: {str(e)}")
            return {
                'facts': [],
                'total': 0,
                'pages': 0,
                'current_page': 1,
                'per_page': per_page,
                'has_prev': False,
                'has_next': False,
                'prev_num': None,
                'next_num': None
            }
    
    @staticmethod
    def get_recent_facts(limit=10):
        """
        Get recent facts for display.
        
        Args:
            limit (int): Number of facts to retrieve
            
        Returns:
            list: Recent facts
        """
        try:
            return Fact.query.filter_by(
                is_deleted=False
            ).order_by(
                Fact.created_at.desc()
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f"Error getting recent facts: {str(e)}")
            return []
    
    @staticmethod
    def get_user_facts(user_id, limit=None):
        """
        Get facts by a specific user.
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of facts
            
        Returns:
            list: User's facts
        """
        try:
            query = Fact.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).order_by(Fact.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        except Exception as e:
            current_app.logger.error(f"Error getting user facts: {str(e)}")
            return []
    
    @staticmethod
    def search_facts(search_query, limit=50):
        """
        Search facts by content.
        
        Args:
            search_query (str): Search query
            limit (int): Maximum results
            
        Returns:
            list: Matching facts
        """
        try:
            if not search_query or len(search_query.strip()) < 3:
                return []
            
            search_term = f"%{search_query.strip()}%"
            
            return Fact.query.filter(
                and_(
                    Fact.content.ilike(search_term),
                    Fact.is_deleted == False
                )
            ).order_by(
                Fact.created_at.desc()
            ).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f"Error searching facts: {str(e)}")
            return []
    
    @staticmethod
    def get_fact_with_author(fact_id):
        """
        Get fact with author information.
        
        Args:
            fact_id (str): Fact ID
            
        Returns:
            dict or None: Fact with author info
        """
        try:
            fact = db.session.query(Fact, User, UserProfile).join(
                User, Fact.user_id == User.id
            ).join(
                UserProfile, User.id == UserProfile.user_id
            ).filter(
                Fact.id == fact_id,
                Fact.is_deleted == False,
                User.is_active == True,
                User.is_deleted == False
            ).first()
            
            if not fact:
                return None
            
            return {
                'fact': fact[0],
                'author': fact[1],
                'author_profile': fact[2]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting fact with author: {str(e)}")
            return None
    
    @staticmethod
    def extract_hashtags_from_content(content):
        """
        Extract hashtags from fact content.
        
        Args:
            content (str): Fact content
            
        Returns:
            list: List of hashtag strings (without #)
        """
        if not content:
            return []
        
        # Find hashtags using regex
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, content, re.IGNORECASE)
        
        # Clean and deduplicate
        clean_hashtags = []
        seen = set()
        
        for tag in hashtags:
            clean_tag = tag.lower().strip()
            if clean_tag and len(clean_tag) <= 50 and clean_tag not in seen:
                clean_hashtags.append(clean_tag)
                seen.add(clean_tag)
        
        return clean_hashtags[:10]  # Limit to 10 hashtags per fact
