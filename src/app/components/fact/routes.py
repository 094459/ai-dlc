"""
Fact routes for fact creation, editing, viewing, and listing.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from app.components.auth.services import SessionValidationService
from app.components.fact.services import FactManagementService, FactRetrievalService
from app.components.security.services import AuthorizationService

fact_bp = Blueprint('fact', __name__, url_prefix='/facts')


@fact_bp.route('/')
def list():
    """List facts with pagination and filtering."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    hashtag = request.args.get('hashtag', '').strip()
    user_id = request.args.get('user', '').strip()
    sort_by = request.args.get('sort', 'recent')
    
    # Get paginated facts
    result = FactRetrievalService.get_facts_paginated(
        page=page,
        search_query=search_query if search_query else None,
        hashtag=hashtag if hashtag else None,
        user_id=user_id if user_id else None,
        sort_by=sort_by
    )
    
    # Get current user for permissions
    current_user = SessionValidationService.get_current_user()
    
    return render_template('fact/list.html',
                         facts=result['facts'],
                         pagination=result,
                         search_query=search_query,
                         hashtag=hashtag,
                         user_filter=user_id,
                         sort_by=sort_by,
                         current_user=current_user)


@fact_bp.route('/<fact_id>')
def view(fact_id):
    """View a single fact with details."""
    # Get fact with author information
    fact_data = FactRetrievalService.get_fact_with_author(fact_id)
    
    if not fact_data:
        # Try to get just the fact if author info fails
        fact = FactRetrievalService.get_fact_by_id(fact_id)
        if not fact:
            abort(404)
        
        # Create minimal fact data structure
        fact_data = {
            'fact': fact,
            'author': None,
            'author_profile': None
        }
    
    fact = fact_data['fact']
    author = fact_data['author']
    author_profile = fact_data['author_profile']
    
    # Get current user for permissions
    current_user = SessionValidationService.get_current_user()
    
    # Check if user can edit this fact
    can_edit = current_user and AuthorizationService.can_user_access_resource(
        current_user, 'fact', fact_id, 'edit'
    )
    
    return render_template('fact/view.html',
                         fact=fact,
                         author=author,
                         author_profile=author_profile,
                         can_edit=can_edit,
                         current_user=current_user)


@fact_bp.route('/new', methods=['GET', 'POST'])
@SessionValidationService.require_authentication()
def create():
    """Create a new fact."""
    user = SessionValidationService.get_current_user()
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        
        if not content:
            flash('Fact content is required', 'error')
            return render_template('fact/create.html', content=content)
        
        # Create fact
        success, message, fact = FactManagementService.create_fact(user.id, content)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('fact.view', fact_id=fact.id))
        else:
            flash(message, 'error')
            return render_template('fact/create.html', content=content)
    
    return render_template('fact/create.html')


@fact_bp.route('/<fact_id>/edit', methods=['GET', 'POST'])
@SessionValidationService.require_authentication()
def edit(fact_id):
    """Edit an existing fact."""
    user = SessionValidationService.get_current_user()
    
    # Get fact
    fact = FactRetrievalService.get_fact_by_id(fact_id)
    if not fact:
        abort(404)
    
    # Check permissions
    if not AuthorizationService.can_user_access_resource(user, 'fact', fact_id, 'edit'):
        abort(403)
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        edit_reason = request.form.get('edit_reason', '').strip()
        
        if not content:
            flash('Fact content is required', 'error')
            return render_template('fact/edit.html', fact=fact, content=content, edit_reason=edit_reason)
        
        # Update fact
        success, message, updated_fact = FactManagementService.update_fact(
            fact_id, user.id, content, edit_reason
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('fact.view', fact_id=fact_id))
        else:
            flash(message, 'error')
            return render_template('fact/edit.html', fact=fact, content=content, edit_reason=edit_reason)
    
    return render_template('fact/edit.html', fact=fact)


@fact_bp.route('/<fact_id>/delete', methods=['POST'])
@SessionValidationService.require_authentication()
def delete(fact_id):
    """Delete a fact."""
    user = SessionValidationService.get_current_user()
    
    # Check permissions
    if not AuthorizationService.can_user_access_resource(user, 'fact', fact_id, 'delete'):
        abort(403)
    
    # Delete fact
    success, message = FactManagementService.delete_fact(fact_id, user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('fact.list'))


@fact_bp.route('/<fact_id>/history')
@SessionValidationService.require_authentication()
def history(fact_id):
    """View edit history for a fact."""
    user = SessionValidationService.get_current_user()
    
    # Get fact
    fact = FactRetrievalService.get_fact_by_id(fact_id)
    if not fact:
        abort(404)
    
    # Check permissions (only owner can see edit history)
    if not AuthorizationService.can_user_access_resource(user, 'fact', fact_id, 'edit'):
        abort(403)
    
    # Get edit history
    edit_history = FactManagementService.get_fact_edit_history(fact_id, user.id)
    
    return render_template('fact/history.html',
                         fact=fact,
                         edit_history=edit_history)


@fact_bp.route('/search')
def search():
    """Search facts via AJAX."""
    query = request.args.get('q', '').strip()
    
    if len(query) < 3:
        return jsonify({'results': []})
    
    facts = FactRetrievalService.search_facts(query, limit=10)
    
    results = []
    for fact in facts:
        results.append({
            'id': fact.id,
            'content': fact.content[:100] + '...' if len(fact.content) > 100 else fact.content,
            'created_at': fact.created_at.strftime('%Y-%m-%d %H:%M'),
            'url': url_for('fact.view', fact_id=fact.id)
        })
    
    return jsonify({'results': results})
