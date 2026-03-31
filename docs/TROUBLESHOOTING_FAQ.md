# Troubleshooting Guide and FAQ

## Overview

This guide provides solutions to common issues and frequently asked questions for the Fact Checker Application.

## Table of Contents

1. [Common User Issues](#common-user-issues)
2. [Administrator Troubleshooting](#administrator-troubleshooting)
3. [System Issues](#system-issues)
4. [Performance Problems](#performance-problems)
5. [Security Issues](#security-issues)
6. [Frequently Asked Questions](#frequently-asked-questions)
7. [Getting Help](#getting-help)

## Common User Issues

### Login and Authentication Problems

#### Cannot Log In
**Symptoms**: Login form shows error, user cannot access account
**Possible Causes**:
- Incorrect email or password
- Account suspended or banned
- Browser cache issues
- Session expired

**Solutions**:
1. **Verify Credentials**
   - Double-check email address spelling
   - Ensure password is correct (case-sensitive)
   - Try typing password manually instead of copy/paste

2. **Clear Browser Data**
   ```
   Chrome: Settings → Privacy → Clear browsing data
   Firefox: Settings → Privacy → Clear Data
   Safari: Develop → Empty Caches
   ```

3. **Reset Password**
   - Click "Forgot Password" on login page
   - Check email for reset instructions
   - Check spam/junk folder if email doesn't arrive

4. **Check Account Status**
   - Contact support if you believe account was suspended incorrectly
   - Review community guidelines for potential violations

#### Password Reset Not Working
**Symptoms**: Password reset email not received or link doesn't work
**Solutions**:
1. **Check Email Settings**
   - Verify email address is correct
   - Check spam/junk folders
   - Add noreply@factchecker.com to contacts

2. **Try Different Browser**
   - Use incognito/private browsing mode
   - Disable browser extensions temporarily
   - Clear cookies and cache

3. **Contact Support**
   - Email support@factchecker.com with your account email
   - Include any error messages received

### Content Submission Issues

#### Cannot Submit Facts
**Symptoms**: Submit button doesn't work, error messages appear
**Solutions**:
1. **Check Content Requirements**
   - Minimum 10 characters required
   - Maximum 2000 characters allowed
   - Include at least one credible source

2. **Verify Account Status**
   - Ensure you're logged in
   - Check if account has submission restrictions
   - Verify email address if required

3. **Technical Issues**
   - Refresh the page and try again
   - Check internet connection
   - Try different browser or device

#### Voting Not Working
**Symptoms**: Vote buttons don't respond, votes don't register
**Solutions**:
1. **Check Voting Rules**
   - Cannot vote on your own content
   - Must be logged in to vote
   - Can only vote once per item

2. **Clear Browser Cache**
   - Refresh the page
   - Clear cookies and cache
   - Try incognito/private mode

3. **Account Restrictions**
   - Check if account has voting restrictions
   - Contact support if restrictions seem incorrect

### Notification Issues

#### Not Receiving Notifications
**Symptoms**: Missing email notifications, no in-app alerts
**Solutions**:
1. **Check Notification Settings**
   - Go to Account Settings → Notifications
   - Verify email notifications are enabled
   - Check frequency settings

2. **Email Delivery Issues**
   - Check spam/junk folders
   - Add factchecker.com to email whitelist
   - Verify email address is correct

3. **Browser Notifications**
   - Allow notifications in browser settings
   - Check if notifications are blocked for the site

## Administrator Troubleshooting

### User Management Issues

#### Bulk Operations Failing
**Symptoms**: Bulk user actions don't complete, partial failures
**Solutions**:
1. **Check Selection Criteria**
   - Verify user selection is correct
   - Ensure admin accounts aren't included in bulk operations
   - Review action permissions

2. **Database Issues**
   - Check database connectivity
   - Review error logs for specific failures
   - Verify database constraints aren't violated

3. **System Resources**
   - Monitor server performance during bulk operations
   - Consider processing in smaller batches
   - Check for timeout issues

#### Moderation Queue Problems
**Symptoms**: Reports not appearing, actions not processing
**Solutions**:
1. **Queue Status Check**
   - Verify reports are being created properly
   - Check report assignment and priority
   - Review moderation workflow settings

2. **Permission Issues**
   - Ensure moderator has appropriate permissions
   - Check role assignments and access levels
   - Verify moderation action logging

### System Configuration Issues

#### Email Notifications Not Sending
**Symptoms**: Users not receiving system emails
**Solutions**:
1. **SMTP Configuration**
   ```bash
   # Check SMTP settings
   echo $SMTP_HOST
   echo $SMTP_PORT
   echo $SMTP_USERNAME
   ```

2. **Test Email Delivery**
   ```python
   # Test script
   from app import create_app
   from app.components.notification.services import NotificationService
   
   app = create_app()
   with app.app_context():
       result = NotificationService.send_test_email('test@example.com')
       print(f"Email test result: {result}")
   ```

3. **Check Email Logs**
   - Review application logs for email errors
   - Check SMTP server logs if accessible
   - Verify email queue processing

#### Database Connection Issues
**Symptoms**: Application errors, database timeouts
**Solutions**:
1. **Connection String Verification**
   ```bash
   # Check database URL
   echo $DATABASE_URL
   
   # Test connection
   psql $DATABASE_URL -c "SELECT 1;"
   ```

2. **Connection Pool Settings**
   ```python
   # Adjust pool settings in config
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 20,
       'pool_recycle': 3600,
       'pool_pre_ping': True,
       'pool_timeout': 30
   }
   ```

3. **Database Maintenance**
   ```sql
   -- Check for blocking queries
   SELECT * FROM pg_stat_activity WHERE state = 'active';
   
   -- Vacuum and analyze
   VACUUM ANALYZE;
   ```

## System Issues

### Application Won't Start

#### Flask Application Errors
**Symptoms**: Application fails to start, import errors
**Solutions**:
1. **Check Dependencies**
   ```bash
   # Verify all packages installed
   pip install -r requirements.txt
   
   # Check for version conflicts
   pip check
   ```

2. **Environment Variables**
   ```bash
   # Verify required environment variables
   env | grep FLASK
   env | grep DATABASE_URL
   env | grep SECRET_KEY
   ```

3. **Database Initialization**
   ```bash
   # Initialize database if needed
   flask db upgrade
   
   # Check database status
   flask db current
   ```

#### Import Errors
**Symptoms**: ModuleNotFoundError, ImportError messages
**Solutions**:
1. **Python Path Issues**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"
   
   # Add application directory to path
   export PYTHONPATH=/path/to/factchecker:$PYTHONPATH
   ```

2. **Virtual Environment**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Verify correct Python version
   python --version
   which python
   ```

### Database Issues

#### Migration Failures
**Symptoms**: Database migration errors, schema conflicts
**Solutions**:
1. **Check Migration Status**
   ```bash
   # View current migration
   flask db current
   
   # View migration history
   flask db history
   ```

2. **Resolve Conflicts**
   ```bash
   # Stamp database with current migration
   flask db stamp head
   
   # Create new migration
   flask db migrate -m "Fix migration conflict"
   ```

3. **Manual Schema Fixes**
   ```sql
   -- Check table structure
   \d+ table_name
   
   -- Fix schema manually if needed
   ALTER TABLE table_name ADD COLUMN column_name TYPE;
   ```

#### Data Corruption
**Symptoms**: Inconsistent data, foreign key violations
**Solutions**:
1. **Data Integrity Check**
   ```sql
   -- Check for orphaned records
   SELECT * FROM comments WHERE fact_id NOT IN (SELECT id FROM facts);
   
   -- Check constraint violations
   SELECT conname, conrelid::regclass FROM pg_constraint WHERE NOT convalidated;
   ```

2. **Restore from Backup**
   ```bash
   # Restore database from backup
   pg_restore -d factchecker_prod backup_file.sql
   
   # Verify data integrity after restore
   psql factchecker_prod -c "SELECT COUNT(*) FROM facts;"
   ```

## Performance Problems

### Slow Page Loading

#### Database Performance
**Symptoms**: Slow queries, high database CPU usage
**Solutions**:
1. **Query Analysis**
   ```sql
   -- Enable query logging
   SET log_statement = 'all';
   SET log_min_duration_statement = 1000;
   
   -- Analyze slow queries
   SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC;
   ```

2. **Index Optimization**
   ```sql
   -- Check missing indexes
   SELECT schemaname, tablename, attname, n_distinct, correlation 
   FROM pg_stats WHERE schemaname = 'public';
   
   -- Add indexes for common queries
   CREATE INDEX CONCURRENTLY idx_facts_created_at ON facts(created_at DESC);
   ```

3. **Database Maintenance**
   ```sql
   -- Update statistics
   ANALYZE;
   
   -- Vacuum tables
   VACUUM VERBOSE facts;
   ```

#### Application Performance
**Symptoms**: High CPU usage, memory leaks
**Solutions**:
1. **Profiling**
   ```python
   # Add profiling to identify bottlenecks
   from werkzeug.middleware.profiler import ProfilerMiddleware
   app.wsgi_app = ProfilerMiddleware(app.wsgi_app)
   ```

2. **Caching Implementation**
   ```python
   # Add caching to expensive operations
   from flask_caching import Cache
   
   @cache.cached(timeout=300)
   def expensive_operation():
       # Cached function
       pass
   ```

3. **Resource Monitoring**
   ```bash
   # Monitor system resources
   htop
   iotop
   free -h
   df -h
   ```

### High Memory Usage

#### Memory Leaks
**Symptoms**: Continuously increasing memory usage
**Solutions**:
1. **Memory Profiling**
   ```python
   # Use memory profiler
   from memory_profiler import profile
   
   @profile
   def memory_intensive_function():
       # Function to profile
       pass
   ```

2. **Database Connection Management**
   ```python
   # Ensure connections are properly closed
   try:
       # Database operations
       pass
   finally:
       db.session.close()
   ```

3. **Garbage Collection**
   ```python
   # Force garbage collection
   import gc
   gc.collect()
   
   # Monitor object counts
   print(len(gc.get_objects()))
   ```

## Security Issues

### Suspicious Activity

#### Unusual Login Patterns
**Symptoms**: Multiple failed login attempts, unusual access patterns
**Solutions**:
1. **Review Access Logs**
   ```bash
   # Check authentication logs
   grep "login" /var/log/factchecker/app.log
   
   # Look for suspicious IP addresses
   grep "failed login" /var/log/factchecker/app.log | awk '{print $5}' | sort | uniq -c
   ```

2. **Implement Rate Limiting**
   ```python
   # Add rate limiting to login endpoint
   from flask_limiter import Limiter
   
   @limiter.limit("5 per minute")
   @auth_bp.route('/login', methods=['POST'])
   def login():
       # Login logic
       pass
   ```

3. **Account Security Measures**
   - Force password reset for affected accounts
   - Enable two-factor authentication
   - Monitor account activity closely

#### Content Spam or Abuse
**Symptoms**: Rapid content submission, inappropriate content
**Solutions**:
1. **Content Analysis**
   ```sql
   -- Check for rapid submissions
   SELECT user_id, COUNT(*) as fact_count, 
          MAX(created_at) - MIN(created_at) as time_span
   FROM facts 
   WHERE created_at > NOW() - INTERVAL '1 hour'
   GROUP BY user_id 
   HAVING COUNT(*) > 10;
   ```

2. **Automated Detection**
   ```python
   # Implement spam detection
   def detect_spam_content(content):
       # Check for spam patterns
       spam_keywords = ['buy now', 'click here', 'free money']
       return any(keyword in content.lower() for keyword in spam_keywords)
   ```

3. **User Restrictions**
   - Temporarily suspend suspicious accounts
   - Implement content approval for new users
   - Increase moderation for flagged content

## Frequently Asked Questions

### General Questions

**Q: How do I reset the admin password?**
A: Use the admin creation script:
```bash
python scripts/create_admin.py --email admin@yourdomain.com --password new_password --reset
```

**Q: How do I backup the database?**
A: Use the backup script:
```bash
./scripts/backup_database.sh
```

**Q: How do I check system health?**
A: Visit the health check endpoint:
```bash
curl http://localhost:5000/health/detailed
```

**Q: How do I update the application?**
A: Follow the update procedure:
```bash
./scripts/update_application.sh
```

### Technical Questions

**Q: How do I enable debug mode?**
A: Set the environment variable:
```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
```

**Q: How do I check database migrations?**
A: Use Flask-Migrate commands:
```bash
flask db current
flask db history
```

**Q: How do I clear the cache?**
A: Restart Redis or clear programmatically:
```python
from app import cache
cache.clear()
```

**Q: How do I monitor performance?**
A: Use the built-in monitoring endpoints and system tools:
```bash
# Application metrics
curl http://localhost:5000/admin/api/system/health

# System metrics
htop
iotop
```

### Configuration Questions

**Q: How do I change email settings?**
A: Update environment variables:
```bash
export SMTP_HOST=new-smtp-server.com
export SMTP_USERNAME=new-username
export SMTP_PASSWORD=new-password
```

**Q: How do I enable/disable features?**
A: Use feature flags in environment:
```bash
export ENABLE_REGISTRATION=false
export ENABLE_EMAIL_NOTIFICATIONS=true
```

**Q: How do I change rate limits?**
A: Update the rate limiting configuration in `config.py`:
```python
RATE_LIMITS = {
    'auth.login': '10 per minute',
    'facts.create': '5 per hour'
}
```

## Getting Help

### Self-Service Resources
1. **Documentation**: Review all documentation files
2. **Logs**: Check application and system logs
3. **Health Checks**: Use built-in monitoring endpoints
4. **Community**: Search community forums and discussions

### Support Channels

#### Technical Support
- **Email**: support@factchecker.com
- **Response Time**: 24-48 hours
- **Include**: Error messages, logs, steps to reproduce

#### Emergency Support
- **Critical Issues**: security@factchecker.com
- **System Outages**: admin@factchecker.com
- **Response Time**: 2-4 hours

#### Community Support
- **User Forum**: community.factchecker.com
- **GitHub Issues**: github.com/factchecker/issues
- **Documentation**: docs.factchecker.com

### When Contacting Support

**Include the Following Information**:
1. **Problem Description**: Clear description of the issue
2. **Steps to Reproduce**: Exact steps that cause the problem
3. **Error Messages**: Complete error messages and stack traces
4. **Environment**: Operating system, browser, version information
5. **Screenshots**: Visual evidence of the problem
6. **Logs**: Relevant log entries (remove sensitive information)

**Example Support Request**:
```
Subject: Cannot submit facts - validation error

Description:
Users are unable to submit facts and receive a validation error message.

Steps to Reproduce:
1. Log in as regular user
2. Navigate to "Submit Fact" page
3. Enter fact content (>10 characters)
4. Add source URL
5. Click "Submit Fact"
6. Error appears: "Validation failed"

Environment:
- Browser: Chrome 96.0.4664.110
- OS: Windows 10
- User Role: Regular user
- Time: 2024-01-01 14:30 UTC

Error Logs:
[2024-01-01 14:30:15] ERROR: ValidationError in facts.create: Required field missing

Screenshots: [attached]
```

---

*This troubleshooting guide is updated regularly based on common issues and user feedback.*
*Last updated: 2024-01-01*
