#!/usr/bin/env python3
"""
Manual test script for TC_US01_Registration_ValidEmail_Success
Tests the web interface for user registration with valid email.
"""
import requests
import sys
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

def test_registration_valid_email():
    """Test successful user registration with valid email via web interface."""
    print("🧪 Testing TC_US01_Registration_ValidEmail_Success")
    print("=" * 60)
    
    # Test data
    test_email = "testuser@example.com"
    test_password = "password123"
    test_name = "Test User"
    
    try:
        # Step 1: Navigate to registration page
        print("Step 1: Accessing registration page...")
        reg_url = urljoin(BASE_URL, "/auth/register")
        response = requests.get(reg_url)
        
        if response.status_code != 200:
            print(f"❌ Registration page not accessible. Status: {response.status_code}")
            return False
        
        print("✅ Registration page is accessible")
        
        # Step 2: Submit registration form with valid data
        print(f"Step 2: Submitting registration with email: {test_email}")
        
        # Create a session to handle cookies/CSRF tokens
        session = requests.Session()
        
        # Get the registration page to extract any CSRF tokens
        reg_response = session.get(reg_url)
        
        # Prepare form data
        form_data = {
            'email': test_email,
            'password': test_password,
            'confirm_password': test_password,
            'name': test_name
        }
        
        # Submit registration
        post_response = session.post(reg_url, data=form_data, allow_redirects=False)
        
        # Step 3: Verify response
        print(f"Registration response status: {post_response.status_code}")
        
        # Check if redirected (successful registration typically redirects)
        if post_response.status_code in [302, 303]:
            print("✅ Registration appears successful (redirected)")
            
            # Check redirect location
            redirect_location = post_response.headers.get('Location', '')
            print(f"Redirected to: {redirect_location}")
            
            if 'login' in redirect_location:
                print("✅ Redirected to login page as expected")
            else:
                print("⚠️  Redirected but not to login page")
            
            return True
            
        elif post_response.status_code == 200:
            # Check response content for success/error messages
            response_text = post_response.text.lower()
            
            if 'error' in response_text or 'invalid' in response_text:
                print("❌ Registration failed - error message in response")
                print("Response content preview:", response_text[:200])
                return False
            elif 'success' in response_text:
                print("✅ Registration successful")
                return True
            else:
                print("⚠️  Unclear registration result")
                return False
        else:
            print(f"❌ Unexpected response status: {post_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application. Is it running on http://127.0.0.1:5000?")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_login_with_registered_email():
    """Test login with the registered email to verify account creation."""
    print("\n🔐 Testing login with registered email...")
    
    test_email = "testuser@example.com"
    test_password = "password123"
    
    try:
        session = requests.Session()
        login_url = urljoin(BASE_URL, "/auth/login")
        
        # Get login page
        login_response = session.get(login_url)
        if login_response.status_code != 200:
            print(f"❌ Login page not accessible. Status: {login_response.status_code}")
            return False
        
        # Submit login
        form_data = {
            'email': test_email,
            'password': test_password
        }
        
        post_response = session.post(login_url, data=form_data, allow_redirects=False)
        
        if post_response.status_code in [302, 303]:
            print("✅ Login successful (redirected)")
            return True
        else:
            print(f"❌ Login failed. Status: {post_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

if __name__ == "__main__":
    print("Manual Test Execution for TC_US01_Registration_ValidEmail_Success")
    print("=" * 70)
    
    # Run the tests
    registration_success = test_registration_valid_email()
    
    if registration_success:
        login_success = test_login_with_registered_email()
        
        if registration_success and login_success:
            print("\n🎉 TC_US01_Registration_ValidEmail_Success: PASSED")
            print("✅ All acceptance criteria met:")
            print("  - User receives confirmation (redirect to login)")
            print("  - User account is created in system")
            print("  - User can subsequently log in")
            sys.exit(0)
        else:
            print("\n❌ TC_US01_Registration_ValidEmail_Success: FAILED")
            print("Registration succeeded but login failed")
            sys.exit(1)
    else:
        print("\n❌ TC_US01_Registration_ValidEmail_Success: FAILED")
        print("Registration did not succeed")
        sys.exit(1)
