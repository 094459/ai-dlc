#!/usr/bin/env python3
"""
Run script for the Fact Checker application.
"""
import os
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Run the application
    app.run(
        debug=debug,
        host=host,
        port=port
    )
