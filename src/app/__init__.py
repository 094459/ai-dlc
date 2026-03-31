"""
Flask application factory for the Fact Checker application.
Implements the application factory pattern for better testing and configuration management.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask application
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register blueprints (will be added as components are implemented)
    register_blueprints(app)
    
    # Register error handlers
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Configure logging
    configure_logging(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def register_blueprints(app):
    """
    Register all application blueprints.
    
    Args:
        app (Flask): Flask application instance
    """
    # Import and register main blueprint
    from app.main import main
    app.register_blueprint(main)
    
    # Import and register authentication blueprint
    from app.components.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Import and register profile blueprint
    from app.components.profile import profile_bp
    app.register_blueprint(profile_bp)
    
    # Import and register fact blueprint
    from app.components.fact import fact_bp
    app.register_blueprint(fact_bp)
    
    # Import and register voting blueprint
    from app.components.voting import voting_bp
    app.register_blueprint(voting_bp)
    
    # Import and register comment blueprint
    from app.components.comment import comment_bp
    app.register_blueprint(comment_bp)
    
    # Import and register report blueprint
    from app.components.report import report_bp
    app.register_blueprint(report_bp)
    
    # Import and register moderation blueprint
    from app.components.moderation import moderation_bp
    app.register_blueprint(moderation_bp)
    
    # Import and register notification blueprint
    from app.components.notification import notification_bp
    app.register_blueprint(notification_bp)
    
    # Import and register analytics blueprint
    from app.components.analytics.routes import analytics_bp
    app.register_blueprint(analytics_bp)
    
    # Import and register UI framework blueprint
    from app.components.ui.routes import ui_bp
    app.register_blueprint(ui_bp)
    
    # Import and register admin dashboard blueprints
    from app.routes.admin_routes import admin_bp
    from app.routes.admin_api_routes import admin_api_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_api_bp)
    
    # Additional blueprints will be registered here as components are implemented


def configure_logging(app):
    """
    Configure application logging.
    
    Args:
        app (Flask): Flask application instance
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configure file handler
        file_handler = RotatingFileHandler(
            'logs/fact_checker.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Fact Checker application startup')
