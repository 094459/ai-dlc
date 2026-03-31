"""
Error handlers for the Fact Checker application.
Provides custom error pages and logging for different HTTP errors.
"""
from flask import render_template, request, current_app
from app import db


def register_error_handlers(app):
    """Register error handlers with the Flask application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        current_app.logger.warning(f'Bad request: {request.url} - {error}')
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        current_app.logger.warning(f'Unauthorized access: {request.url} - {error}')
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        current_app.logger.warning(f'Forbidden access: {request.url} - {error}')
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        current_app.logger.info(f'Page not found: {request.url}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        current_app.logger.warning(f'Method not allowed: {request.method} {request.url}')
        return render_template('errors/405.html'), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors."""
        current_app.logger.warning(f'File too large: {request.url}')
        return render_template('errors/413.html'), 413
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle 429 Too Many Requests errors."""
        current_app.logger.warning(f'Rate limit exceeded: {request.url}')
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        current_app.logger.error(f'Internal server error: {request.url} - {error}')
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Handle 502 Bad Gateway errors."""
        current_app.logger.error(f'Bad gateway: {request.url} - {error}')
        return render_template('errors/502.html'), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        current_app.logger.error(f'Service unavailable: {request.url} - {error}')
        return render_template('errors/503.html'), 503
