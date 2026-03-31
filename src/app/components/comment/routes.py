"""
Comment routes for comment management and display.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from app.components.auth.services import SessionValidationService
from app.components.comment.services import CommentManagementService, CommentRetrievalService, CommentModerationService
from app.components.security.services import AuthorizationService

comment_bp = Blueprint('comment', __name__, url_prefix='/comments')


@comment_bp.route('/create', methods=['POST'])
@SessionValidationService.require_authentication()
def create():
    """Create a new comment via AJAX."""
    user = SessionValidationService.get_current_user()
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication failed'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
        fact_id = data.get('fact_id')
        content = data.get('content', '').strip()
        parent_comment_id = data.get('parent_comment_id')
        
        if not fact_id or not content:
            return jsonify({'success': False, 'message': 'Fact ID and content are required'}), 400
        
        # Create comment
        success, message, comment = CommentManagementService.create_comment(
            user.id, fact_id, content, parent_comment_id
        )
        
        if success:
            # Get comment with author info for response
            comment_data = CommentRetrievalService.get_comment_with_author(comment.id)
            
            return jsonify({
                'success': True,
                'message': message,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                    'author_name': comment_data['author_profile'].name if comment_data else 'Unknown',
                    'author_photo': comment_data['author_profile'].profile_photo_url if comment_data and comment_data['author_profile'].profile_photo_url else None,
                    'depth': comment.nesting_level,
                    'parent_comment_id': comment.parent_comment_id
                }
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to create comment'}), 500


@comment_bp.route('/<comment_id>/edit', methods=['GET', 'POST'])
@SessionValidationService.require_authentication()
def edit(comment_id):
    """Edit a comment."""
    user = SessionValidationService.get_current_user()
    
    # Get comment
    comment_data = CommentRetrievalService.get_comment_with_author(comment_id)
    if not comment_data:
        abort(404)
    
    comment = comment_data['comment']
    
    # Check permissions
    if not AuthorizationService.can_user_access_resource(user, 'comment', comment_id, 'edit'):
        abort(403)
    
    if request.method == 'POST':
        if request.is_json:
            # AJAX request
            data = request.get_json()
            content = data.get('content', '').strip()
            edit_reason = data.get('edit_reason', '').strip()
        else:
            # Form request
            content = request.form.get('content', '').strip()
            edit_reason = request.form.get('edit_reason', '').strip()
        
        if not content:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Content is required'}), 400
            else:
                flash('Content is required', 'error')
                return render_template('comment/edit.html', comment=comment)
        
        # Update comment
        success, message, updated_comment = CommentManagementService.update_comment(
            comment_id, user.id, content, edit_reason
        )
        
        if request.is_json:
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'comment': {
                        'id': updated_comment.id,
                        'content': updated_comment.content,
                        'edit_count': updated_comment.edit_count,
                        'last_edited_at': updated_comment.last_edited_at.isoformat() if updated_comment.last_edited_at else None
                    }
                })
            else:
                return jsonify({'success': False, 'message': message}), 400
        else:
            if success:
                flash(message, 'success')
                return redirect(url_for('fact.view', fact_id=comment.fact_id))
            else:
                flash(message, 'error')
                return render_template('comment/edit.html', comment=comment)
    
    return render_template('comment/edit.html', comment=comment)


@comment_bp.route('/<comment_id>/delete', methods=['POST'])
@SessionValidationService.require_authentication()
def delete(comment_id):
    """Delete a comment."""
    user = SessionValidationService.get_current_user()
    
    # Check permissions
    if not AuthorizationService.can_user_access_resource(user, 'comment', comment_id, 'delete'):
        abort(403)
    
    # Get comment to find fact_id for redirect
    comment_data = CommentRetrievalService.get_comment_with_author(comment_id)
    if not comment_data:
        abort(404)
    
    fact_id = comment_data['comment'].fact_id
    
    # Delete comment
    success, message = CommentManagementService.delete_comment(comment_id, user.id)
    
    if request.is_json:
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
    else:
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('fact.view', fact_id=fact_id))


@comment_bp.route('/<comment_id>/flag', methods=['POST'])
@SessionValidationService.require_authentication()
def flag(comment_id):
    """Flag a comment for moderation."""
    user = SessionValidationService.get_current_user()
    
    try:
        if request.is_json:
            data = request.get_json()
            flag_reason = data.get('reason', '').strip()
        else:
            flag_reason = request.form.get('reason', '').strip()
        
        if not flag_reason:
            message = 'Flag reason is required'
            if request.is_json:
                return jsonify({'success': False, 'message': message}), 400
            else:
                flash(message, 'error')
                return redirect(request.referrer or url_for('main.index'))
        
        # Flag comment
        success, message = CommentModerationService.flag_comment(comment_id, user.id, flag_reason)
        
        if request.is_json:
            if success:
                return jsonify({'success': True, 'message': message})
            else:
                return jsonify({'success': False, 'message': message}), 400
        else:
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
            
            return redirect(request.referrer or url_for('main.index'))
            
    except Exception as e:
        message = 'Failed to flag comment'
        if request.is_json:
            return jsonify({'success': False, 'message': message}), 500
        else:
            flash(message, 'error')
            return redirect(request.referrer or url_for('main.index'))


@comment_bp.route('/<comment_id>/history')
@SessionValidationService.require_authentication()
def history(comment_id):
    """View edit history for a comment."""
    user = SessionValidationService.get_current_user()
    
    # Get comment
    comment_data = CommentRetrievalService.get_comment_with_author(comment_id)
    if not comment_data:
        abort(404)
    
    comment = comment_data['comment']
    
    # Check permissions (only owner and moderators can see edit history)
    if not (comment.user_id == user.id or user.is_admin or user.is_moderator):
        abort(403)
    
    # Get edit history
    edit_history = CommentRetrievalService.get_comment_edit_history(comment_id, user.id)
    
    return render_template('comment/history.html',
                         comment=comment,
                         edit_history=edit_history)


@comment_bp.route('/fact/<fact_id>')
def list_for_fact(fact_id):
    """Get comments for a fact via AJAX."""
    try:
        sort_by = request.args.get('sort', 'oldest')
        
        # Get comments
        comments = CommentRetrievalService.get_fact_comments(fact_id, sort_by)
        
        # Convert to JSON-serializable format
        def serialize_comment(comment):
            try:
                comment_data = CommentRetrievalService.get_comment_with_author(comment.id)
                
                # Safely extract author information
                author_name = 'Unknown'
                author_photo = None
                
                if comment_data and comment_data.get('author_profile'):
                    profile = comment_data['author_profile']
                    author_name = profile.name if hasattr(profile, 'name') and profile.name else 'Unknown'
                    author_photo = profile.profile_photo_url if hasattr(profile, 'profile_photo_url') else None
                elif comment_data and comment_data.get('author'):
                    author = comment_data['author']
                    author_name = author.email if hasattr(author, 'email') else 'Unknown'
                
                return {
                    'id': comment.id,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                    'edit_count': comment.edit_count,
                    'last_edited_at': None,  # Comment model doesn't have this field
                    'depth': getattr(comment, 'nesting_level', 0),  # Use nesting_level instead of depth
                    'parent_comment_id': comment.parent_comment_id,
                    'is_hidden': getattr(comment, 'is_deleted', False),  # Use is_deleted as hidden indicator
                    'author_name': author_name,
                    'author_photo': author_photo,
                    'author_id': comment.user_id,
                    'replies': [serialize_comment(reply) for reply in getattr(comment, 'replies', [])]
                }
            except Exception as e:
                # Fallback for individual comment serialization errors
                return {
                    'id': comment.id,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                    'edit_count': getattr(comment, 'edit_count', 0),
                    'last_edited_at': None,
                    'depth': 0,
                    'parent_comment_id': comment.parent_comment_id,
                    'is_hidden': False,
                    'author_name': 'Unknown',
                    'author_photo': None,
                    'author_id': comment.user_id,
                    'replies': []
                }
        
        serialized_comments = [serialize_comment(comment) for comment in comments]
        
        return jsonify({
            'success': True,
            'comments': serialized_comments,
            'total_count': len(comments)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to load comments'}), 500


# Moderation routes (admin/moderator only)
@comment_bp.route('/moderate/<comment_id>', methods=['POST'])
@SessionValidationService.require_moderator()
def moderate(comment_id):
    """Moderate a comment (admin/moderator only)."""
    user = SessionValidationService.get_current_user()
    
    try:
        if request.is_json:
            data = request.get_json()
            action = data.get('action')
            reason = data.get('reason', '').strip()
        else:
            action = request.form.get('action')
            reason = request.form.get('reason', '').strip()
        
        if action not in ['approve', 'hide', 'delete']:
            message = 'Invalid moderation action'
            if request.is_json:
                return jsonify({'success': False, 'message': message}), 400
            else:
                flash(message, 'error')
                return redirect(request.referrer or url_for('main.index'))
        
        # Moderate comment
        success, message = CommentModerationService.moderate_comment(
            comment_id, user.id, action, reason
        )
        
        if request.is_json:
            if success:
                return jsonify({'success': True, 'message': message})
            else:
                return jsonify({'success': False, 'message': message}), 400
        else:
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
            
            return redirect(request.referrer or url_for('main.index'))
            
    except Exception as e:
        message = 'Failed to moderate comment'
        if request.is_json:
            return jsonify({'success': False, 'message': message}), 500
        else:
            flash(message, 'error')
            return redirect(request.referrer or url_for('main.index'))


@comment_bp.route('/flagged')
@SessionValidationService.require_moderator()
def flagged():
    """View flagged comments (admin/moderator only)."""
    flagged_comments = CommentModerationService.get_flagged_comments(50)
    
    return render_template('comment/flagged.html',
                         flagged_comments=flagged_comments)
