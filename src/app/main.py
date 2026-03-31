"""
Main blueprint for the Fact Checker application.
Contains basic routes like home, about, etc.
"""
import os
from flask import Blueprint, render_template, send_from_directory, current_app, abort

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page route."""
    return render_template('main/index.html')


@main.route('/about')
def about():
    """About page route."""
    return render_template('main/about.html')


@main.route('/guidelines')
def guidelines():
    """Community guidelines page route."""
    return render_template('main/guidelines.html')


@main.route('/contact')
def contact():
    """Contact page route."""
    return render_template('main/contact.html')


@main.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files (profile photos, fact images, etc.)."""
    try:
        # The uploads directory is in the project root, not in the app directory
        uploads_dir = os.path.join(os.path.dirname(current_app.root_path), 'uploads')
        return send_from_directory(uploads_dir, filename)
    except FileNotFoundError:
        abort(404)
