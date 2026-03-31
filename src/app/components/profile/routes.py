"""
Profile routes for user profile management and display.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import User
from app.components.auth.services import SessionValidationService
from app.components.profile.services import ProfileManagementService, ProfilePhotoService
from app.components.security.services import AuthorizationService

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@SessionValidationService.require_authentication()
def my_profile():
    """Current user's profile page."""
    user = SessionValidationService.get_current_user()
    return redirect(url_for('profile.view', user_id=user.id))


@profile_bp.route('/user/<user_id>')
def view(user_id):
    """View user profile page."""
    # Get user and profile
    user = User.query.filter_by(id=user_id, is_active=True, is_deleted=False).first()
    if not user:
        abort(404)
    
    profile = ProfileManagementService.get_user_profile(user_id)
    if not profile:
        abort(404)
    
    # Get user statistics
    stats = ProfileManagementService.get_user_stats(user_id)
    
    # Get recent activity
    recent_activity = ProfileManagementService.get_user_recent_activity(user_id, limit=10)
    
    # Get recent facts
    recent_facts = ProfileManagementService.get_user_recent_facts(user_id, limit=5)
    
    # Check if current user can edit this profile
    current_user = SessionValidationService.get_current_user()
    can_edit = current_user and AuthorizationService.can_user_access_resource(
        current_user, 'profile', user_id, 'edit'
    )
    
    return render_template('profile/view.html',
                         user=user,
                         profile=profile,
                         stats=stats,
                         recent_activity=recent_activity,
                         recent_facts=recent_facts,
                         can_edit=can_edit)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@SessionValidationService.require_authentication()
def edit():
    """Edit current user's profile."""
    user = SessionValidationService.get_current_user()
    profile = ProfileManagementService.get_user_profile(user.id)
    
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        biography = request.form.get('biography', '').strip()
        
        # Update profile
        success, message, updated_profile = ProfileManagementService.update_profile(
            user.id, name=name, biography=biography
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('profile.view', user_id=user.id))
        else:
            flash(message, 'error')
    
    return render_template('profile/edit.html',
                         user=user,
                         profile=profile)


@profile_bp.route('/upload-photo', methods=['POST'])
@SessionValidationService.require_authentication()
def upload_photo():
    """Upload profile photo."""
    user = SessionValidationService.get_current_user()
    
    if 'photo' not in request.files:
        flash('No photo selected', 'error')
        return redirect(url_for('profile.edit'))
    
    file = request.files['photo']
    
    # Upload photo
    success, message, photo_url = ProfilePhotoService.upload_profile_photo(user.id, file)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('profile.edit'))


@profile_bp.route('/delete-photo', methods=['POST'])
@SessionValidationService.require_authentication()
def delete_photo():
    """Delete profile photo."""
    user = SessionValidationService.get_current_user()
    
    # Delete photo
    success, message = ProfilePhotoService.delete_profile_photo(user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('profile.edit'))


@profile_bp.route('/settings')
@SessionValidationService.require_authentication()
def settings():
    """User settings page."""
    user = SessionValidationService.get_current_user()
    profile = ProfileManagementService.get_user_profile(user.id)
    
    return render_template('profile/settings.html',
                         user=user,
                         profile=profile)
