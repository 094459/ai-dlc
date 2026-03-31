"""
Authentication routes for user registration, login, and logout.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.components.auth.services import AuthenticationService, SessionValidationService
from app.components.security.services import ValidationService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    # Redirect if already authenticated
    if SessionValidationService.is_authenticated():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        
        # Validate inputs
        email_valid, email_msg = ValidationService.validate_email(email)
        if not email_valid:
            flash(email_msg, 'error')
            return render_template('auth/register.html', 
                                 email=email, name=name)
        
        password_valid, password_msg = ValidationService.validate_password(password)
        if not password_valid:
            flash(password_msg, 'error')
            return render_template('auth/register.html', 
                                 email=email, name=name)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html', 
                                 email=email, name=name)
        
        name_valid, name_msg = ValidationService.validate_name(name)
        if not name_valid:
            flash(name_msg, 'error')
            return render_template('auth/register.html', 
                                 email=email, name=name)
        
        # Register user
        success, message, user = AuthenticationService.register_user(email, password, name)
        
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
            return render_template('auth/register.html', 
                                 email=email, name=name)
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    # Redirect if already authenticated
    if SessionValidationService.is_authenticated():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html', email=email)
        
        # Authenticate user
        success, message, user = AuthenticationService.login_user(email, password, remember_me)
        
        if success:
            flash('Login successful!', 'success')
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash(message, 'error')
            return render_template('auth/login.html', email=email)
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """User logout route."""
    user = SessionValidationService.get_current_user()
    
    if user:
        AuthenticationService.logout_user(user.id)
        flash('You have been logged out successfully.', 'info')
    
    return redirect(url_for('main.index'))


# Context processor to make current_user available in templates
@auth_bp.app_context_processor
def inject_user():
    """Inject current user into template context."""
    return {
        'current_user': SessionValidationService.get_current_user()
    }
