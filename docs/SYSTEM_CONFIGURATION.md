# System Configuration Guide

## Overview

This guide covers system configuration, environment setup, and maintenance procedures for the Fact Checker Application.

## Environment Configuration

### Development Environment

```bash
# Environment Variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export DATABASE_URL=sqlite:///factchecker_dev.db
export SECRET_KEY=dev-secret-key-change-in-production
export WTF_CSRF_SECRET_KEY=dev-csrf-key-change-in-production

# Optional Development Settings
export ENABLE_ANALYTICS=true
export ENABLE_EMAIL_NOTIFICATIONS=false
export SMTP_HOST=localhost
export SMTP_PORT=1025
```

### Production Environment

```bash
# Core Settings
export FLASK_ENV=production
export FLASK_DEBUG=0
export DATABASE_URL=postgresql://user:password@localhost/factchecker_prod
export SECRET_KEY=your-secure-secret-key-here
export WTF_CSRF_SECRET_KEY=your-secure-csrf-key-here

# Security Settings
export SSL_REDIRECT=true
export SECURE_COOKIES=true
export SESSION_COOKIE_SECURE=true
export SESSION_COOKIE_HTTPONLY=true

# Email Configuration
export SMTP_HOST=smtp.your-provider.com
export SMTP_PORT=587
export SMTP_USERNAME=notifications@yourdomain.com
export SMTP_PASSWORD=your-smtp-password
export SMTP_USE_TLS=true
export FROM_EMAIL=noreply@yourdomain.com

# Performance Settings
export MAX_CONTENT_LENGTH=16777216  # 16MB
export UPLOAD_FOLDER=/var/uploads/factchecker
export CACHE_TYPE=redis
export CACHE_REDIS_URL=redis://localhost:6379/0
```

### Testing Environment

```bash
# Test Configuration
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///:memory:
export SECRET_KEY=test-secret-key
export WTF_CSRF_SECRET_KEY=test-csrf-key
export TESTING=true
export WTF_CSRF_ENABLED=false
```

## Database Configuration

### SQLite (Development)

```python
# config.py
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'factchecker_dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### PostgreSQL (Production)

```python
# config.py
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/factchecker_prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }
```

### Database Initialization

```bash
# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
python scripts/create_admin.py --email admin@yourdomain.com --password secure_password
```

## Application Configuration

### Feature Flags

```python
# config.py
class Config:
    # Core Features
    ENABLE_REGISTRATION = os.environ.get('ENABLE_REGISTRATION', 'true').lower() == 'true'
    ENABLE_EMAIL_VERIFICATION = os.environ.get('ENABLE_EMAIL_VERIFICATION', 'true').lower() == 'true'
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'true').lower() == 'true'
    
    # Content Settings
    REQUIRE_FACT_SOURCES = os.environ.get('REQUIRE_FACT_SOURCES', 'true').lower() == 'true'
    ENABLE_COMMENT_VOTING = os.environ.get('ENABLE_COMMENT_VOTING', 'true').lower() == 'true'
    MAX_COMMENT_DEPTH = int(os.environ.get('MAX_COMMENT_DEPTH', '2'))
    
    # Moderation Settings
    AUTO_MODERATION = os.environ.get('AUTO_MODERATION', 'false').lower() == 'true'
    REQUIRE_APPROVAL = os.environ.get('REQUIRE_APPROVAL', 'false').lower() == 'true'
```

### Rate Limiting

```python
# Rate limiting configuration
RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

# Rate limits by endpoint
RATE_LIMITS = {
    'auth.register': '5 per minute',
    'auth.login': '10 per minute',
    'facts.create': '10 per hour',
    'comments.create': '30 per hour',
    'voting.vote': '100 per hour',
    'reports.create': '5 per hour'
}
```

## Security Configuration

### Authentication Settings

```python
# Security configuration
class Config:
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_PASSWORD_UPPERCASE = True
    REQUIRE_PASSWORD_LOWERCASE = True
    REQUIRE_PASSWORD_NUMBERS = True
    REQUIRE_PASSWORD_SPECIAL = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('SECURE_COOKIES', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF protection
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SSL_STRICT = os.environ.get('SSL_REDIRECT', 'false').lower() == 'true'
```

### Content Security Policy

```python
# CSP configuration
CSP_POLICY = {
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline' cdn.jsdelivr.net",
    'style-src': "'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com",
    'font-src': "'self' fonts.gstatic.com",
    'img-src': "'self' data: https:",
    'connect-src': "'self'",
    'frame-ancestors': "'none'",
    'base-uri': "'self'",
    'form-action': "'self'"
}
```

## Monitoring and Logging

### Logging Configuration

```python
# logging.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug and not app.testing:
        # File logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/factchecker.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Fact Checker startup')
```

### Health Check Endpoints

```python
# health.py
from flask import Blueprint, jsonify
import psutil
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })

@health_bp.route('/health/detailed')
def detailed_health():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'system': {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        },
        'database': check_database_health(),
        'cache': check_cache_health()
    })
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/factchecker"
DB_NAME="factchecker_prod"

# Create backup directory
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump $DB_NAME > $BACKUP_DIR/factchecker_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/factchecker_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Database backup completed: factchecker_$DATE.sql.gz"
```

### File System Backup

```bash
#!/bin/bash
# backup_files.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/factchecker"
APP_DIR="/var/www/factchecker"

# Backup uploaded files
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz $APP_DIR/uploads/

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz $APP_DIR/config/

# Remove old file backups
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +30 -delete

echo "File backup completed"
```

## Performance Optimization

### Caching Configuration

```python
# cache.py
from flask_caching import Cache

cache = Cache()

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'factchecker:'
}

# Cache decorators
@cache.cached(timeout=300, key_prefix='facts_list')
def get_facts_list():
    # Cached fact listing
    pass

@cache.cached(timeout=600, key_prefix='user_stats')
def get_user_statistics():
    # Cached user statistics
    pass
```

### Database Optimization

```sql
-- Recommended indexes for performance
CREATE INDEX idx_facts_created_at ON facts(created_at DESC);
CREATE INDEX idx_facts_user_id ON facts(user_id);
CREATE INDEX idx_comments_fact_id ON comments(fact_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);
CREATE INDEX idx_votes_target ON fact_votes(fact_id, user_id);
CREATE INDEX idx_reports_status ON reports(status, created_at);
CREATE INDEX idx_users_active ON users(is_active, created_at);
```

## Deployment Configuration

### WSGI Configuration

```python
# wsgi.py
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'production')

if __name__ == "__main__":
    app.run()
```

### Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/factchecker
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Static files
    location /static {
        alias /var/www/factchecker/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploads
    location /uploads {
        alias /var/www/factchecker/uploads;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Maintenance Procedures

### Regular Maintenance Tasks

```bash
#!/bin/bash
# maintenance.sh - Daily maintenance script

# Update system packages (weekly)
if [ $(date +%u) -eq 1 ]; then
    apt update && apt upgrade -y
fi

# Database maintenance
psql factchecker_prod -c "VACUUM ANALYZE;"

# Clean up old log files
find /var/log/factchecker -name "*.log" -mtime +30 -delete

# Clean up temporary files
find /tmp -name "factchecker_*" -mtime +1 -delete

# Restart services if needed
systemctl reload nginx
systemctl restart factchecker

echo "Maintenance completed: $(date)"
```

### System Updates

```bash
#!/bin/bash
# update_application.sh

# Backup before update
./backup_database.sh
./backup_files.sh

# Pull latest code
cd /var/www/factchecker
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Restart application
systemctl restart factchecker
systemctl reload nginx

echo "Application updated successfully"
```

---

*This configuration guide should be customized for your specific deployment environment.*
*Last updated: 2024-01-01*
