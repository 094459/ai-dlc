# API Testing Guide

## Overview

This guide provides comprehensive instructions for testing the Fact Checker Application API, including setup, authentication, endpoint testing, and automated testing strategies.

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd fact-checker-app

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export DATABASE_URL=sqlite:///factchecker.db
export SECRET_KEY=your-secret-key-here

# Initialize database
flask db upgrade

# Run the application
python run.py
```

### 2. Base URL

```
Development: http://localhost:5000
```

## Authentication Testing

### Register a Test User

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "confirm_password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "user_id": "user-uuid"
}
```

### Login and Get Session Cookie

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "user-uuid",
    "email": "test@example.com",
    "is_admin": false,
    "is_moderator": false
  }
}
```

### Use Session Cookie for Authenticated Requests

```bash
curl -X GET http://localhost:5000/auth/session \
  -b cookies.txt
```

## Endpoint Testing Examples

### Facts Management

#### Create a Fact

```bash
curl -X POST http://localhost:5000/facts \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "content": "The Earth orbits around the Sun.",
    "resources": [
      {
        "url": "https://nasa.gov/earth-sun-orbit",
        "title": "NASA: Earth-Sun Orbit"
      }
    ]
  }'
```

#### List Facts

```bash
curl -X GET "http://localhost:5000/facts?page=1&per_page=10&sort=newest"
```

#### Get Specific Fact

```bash
curl -X GET http://localhost:5000/facts/{fact_id}
```

### Voting System

#### Vote on a Fact

```bash
curl -X POST http://localhost:5000/voting/fact/{fact_id} \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "vote_type": "fact"
  }'
```

### Comments

#### Create a Comment

```bash
curl -X POST http://localhost:5000/comments \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "content": "Great fact! Thanks for sharing.",
    "fact_id": "{fact_id}",
    "parent_id": null
  }'
```

#### Get Comments for a Fact

```bash
curl -X GET "http://localhost:5000/comments/fact/{fact_id}?page=1&per_page=20"
```

### Admin Endpoints (Requires Admin Role)

#### Get Admin Dashboard

```bash
curl -X GET http://localhost:5000/admin/dashboard \
  -b cookies.txt
```

#### List Users

```bash
curl -X GET "http://localhost:5000/admin/users?status=active" \
  -b cookies.txt
```

## Postman Collection

### Import Collection

1. Download the Postman collection: `docs/postman_collection.json`
2. Open Postman
3. Click "Import" → "Upload Files"
4. Select the collection file
5. Set the `baseUrl` variable to `http://localhost:5000`

### Environment Variables

Create a Postman environment with these variables:

```json
{
  "baseUrl": "http://localhost:5000",
  "fact_id": "",
  "comment_id": "",
  "user_id": ""
}
```

### Authentication Setup

1. Login using the "Login User" request
2. The session cookie will be automatically stored
3. All subsequent requests will use the session cookie

## Automated Testing with Python

### Test Script Example

```python
import requests
import json

class FactCheckerAPITest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def register_user(self, email, password):
        """Register a new user"""
        response = self.session.post(f"{self.base_url}/auth/register", json={
            "email": email,
            "password": password,
            "confirm_password": password
        })
        return response.json()
    
    def login(self, email, password):
        """Login user and store session"""
        response = self.session.post(f"{self.base_url}/auth/login", json={
            "email": email,
            "password": password
        })
        return response.json()
    
    def create_fact(self, content, resources=None):
        """Create a new fact"""
        data = {"content": content}
        if resources:
            data["resources"] = resources
        
        response = self.session.post(f"{self.base_url}/facts", json=data)
        return response.json()
    
    def vote_on_fact(self, fact_id, vote_type):
        """Vote on a fact"""
        response = self.session.post(
            f"{self.base_url}/voting/fact/{fact_id}",
            json={"vote_type": vote_type}
        )
        return response.json()
    
    def get_facts(self, page=1, per_page=20):
        """Get list of facts"""
        response = self.session.get(
            f"{self.base_url}/facts",
            params={"page": page, "per_page": per_page}
        )
        return response.json()

# Usage example
def run_tests():
    api = FactCheckerAPITest()
    
    # Register and login
    email = "test@example.com"
    password = "testpass123"
    
    print("Registering user...")
    register_result = api.register_user(email, password)
    print(f"Registration: {register_result}")
    
    print("Logging in...")
    login_result = api.login(email, password)
    print(f"Login: {login_result}")
    
    # Create a fact
    print("Creating fact...")
    fact_result = api.create_fact(
        "Python is a programming language.",
        [{"url": "https://python.org", "title": "Python Official Site"}]
    )
    print(f"Fact creation: {fact_result}")
    
    if fact_result.get("success"):
        fact_id = fact_result["fact"]["id"]
        
        # Vote on the fact
        print("Voting on fact...")
        vote_result = api.vote_on_fact(fact_id, "fact")
        print(f"Vote: {vote_result}")
    
    # Get facts list
    print("Getting facts...")
    facts_result = api.get_facts()
    print(f"Facts: {facts_result}")

if __name__ == "__main__":
    run_tests()
```

## Load Testing

### Using Apache Bench (ab)

```bash
# Test fact listing endpoint
ab -n 1000 -c 10 http://localhost:5000/facts

# Test with authentication (requires session setup)
ab -n 100 -c 5 -C "session=your-session-cookie" http://localhost:5000/admin/dashboard
```

### Using Python locust

```python
from locust import HttpUser, task, between

class FactCheckerUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login when user starts"""
        self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
    
    @task(3)
    def view_facts(self):
        """View facts list"""
        self.client.get("/facts")
    
    @task(1)
    def create_fact(self):
        """Create a new fact"""
        self.client.post("/facts", json={
            "content": "This is a test fact for load testing."
        })
    
    @task(2)
    def vote_on_fact(self):
        """Vote on a random fact"""
        # This would need to get a real fact ID
        self.client.post("/voting/fact/some-fact-id", json={
            "vote_type": "fact"
        })
```

Run load test:
```bash
locust -f load_test.py --host=http://localhost:5000
```

## Error Testing

### Test Invalid Authentication

```bash
# Test with invalid credentials
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid@example.com",
    "password": "wrongpassword"
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "error": "Invalid email or password",
  "code": "AUTH_001"
}
```

### Test Validation Errors

```bash
# Test with missing required field
curl -X POST http://localhost:5000/facts \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "content": ""
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "error": "Required field missing",
  "code": "VAL_001",
  "details": {
    "field": "content",
    "message": "Content is required"
  }
}
```

### Test Permission Errors

```bash
# Test admin endpoint without admin role
curl -X GET http://localhost:5000/admin/dashboard \
  -b cookies.txt
```

**Expected Response:**
```json
{
  "success": false,
  "error": "Insufficient permissions to access this resource",
  "code": "AUTH_005",
  "details": {
    "required_role": "admin",
    "user_role": "user"
  }
}
```

## Database Testing

### Test Data Setup

```python
# Create test data for comprehensive testing
def setup_test_data():
    """Create test users, facts, and comments"""
    
    # Create admin user
    admin = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        is_admin=True
    )
    
    # Create regular users
    users = []
    for i in range(5):
        user = User(
            email=f"user{i}@test.com",
            password_hash=hash_password("password123")
        )
        users.append(user)
    
    # Create facts
    facts = []
    for i, user in enumerate(users):
        fact = Fact(
            content=f"Test fact {i} content",
            user_id=user.id
        )
        facts.append(fact)
    
    # Create comments
    for fact in facts:
        for user in users[:3]:  # First 3 users comment
            comment = Comment(
                content=f"Comment on {fact.content[:20]}",
                user_id=user.id,
                fact_id=fact.id
            )
    
    # Save all to database
    db.session.add_all([admin] + users + facts)
    db.session.commit()
```

## Performance Testing

### Response Time Benchmarks

| Endpoint | Expected Response Time | Load Capacity |
|----------|----------------------|---------------|
| GET /facts | < 200ms | 1000 req/min |
| POST /facts | < 500ms | 100 req/min |
| GET /auth/session | < 50ms | 5000 req/min |
| POST /voting/* | < 300ms | 500 req/min |
| GET /admin/dashboard | < 1000ms | 50 req/min |

### Memory Usage Testing

```bash
# Monitor memory usage during testing
ps aux | grep python
top -p $(pgrep -f "python run.py")

# Use memory profiler
pip install memory-profiler
python -m memory_profiler run.py
```

## Security Testing

### SQL Injection Testing

```bash
# Test for SQL injection vulnerabilities
curl -X GET "http://localhost:5000/facts?search='; DROP TABLE facts; --"
```

### XSS Testing

```bash
# Test for XSS vulnerabilities
curl -X POST http://localhost:5000/facts \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "content": "<script>alert(\"XSS\")</script>"
  }'
```

### CSRF Testing

```bash
# Test CSRF protection
curl -X POST http://localhost:5000/facts \
  -H "Content-Type: application/json" \
  -H "Origin: http://malicious-site.com" \
  -d '{
    "content": "Test fact"
  }'
```

## Continuous Integration Testing

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest requests
    
    - name: Run API tests
      run: |
        python run.py &
        sleep 5
        python test_api.py
        pkill -f "python run.py"
```

## Troubleshooting

### Common Issues

1. **Session Cookie Not Persisting**
   - Ensure you're using `-c cookies.txt` and `-b cookies.txt` with curl
   - Check that the application is setting secure cookies correctly

2. **Database Connection Errors**
   - Verify DATABASE_URL environment variable
   - Ensure database is initialized with `flask db upgrade`

3. **Permission Denied Errors**
   - Check user roles in database
   - Verify authentication is working correctly

4. **Rate Limiting Issues**
   - Implement proper delays between requests
   - Check rate limiting configuration

### Debug Mode

```bash
# Run application in debug mode
export FLASK_DEBUG=1
python run.py
```

### Logging

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

*This testing guide covers comprehensive API testing strategies for the Fact Checker Application.*
*Last updated: 2024-01-01*
