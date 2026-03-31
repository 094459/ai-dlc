#!/usr/bin/env python3
"""
Debug script to understand registration issues.
"""
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def debug_registration():
    """Debug registration process."""
    print("🔍 Debugging registration process...")
    
    try:
        session = requests.Session()
        reg_url = urljoin(BASE_URL, "/auth/register")
        
        # Get registration page
        print("Getting registration page...")
        reg_response = session.get(reg_url)
        print(f"Registration page status: {reg_response.status_code}")
        
        if reg_response.status_code == 200:
            # Parse HTML to look for CSRF tokens or form structure
            soup = BeautifulSoup(reg_response.text, 'html.parser')
            form = soup.find('form')
            
            if form:
                print("✅ Found registration form")
                
                # Look for CSRF token
                csrf_token = None
                csrf_input = form.find('input', {'name': 'csrf_token'})
                if csrf_input:
                    csrf_token = csrf_input.get('value')
                    print(f"Found CSRF token: {csrf_token[:20]}...")
                else:
                    print("No CSRF token found")
                
                # Prepare form data
                form_data = {
                    'email': 'testuser@example.com',
                    'password': 'password123',
                    'confirm_password': 'password123',
                    'name': 'Test User'
                }
                
                if csrf_token:
                    form_data['csrf_token'] = csrf_token
                
                print("Submitting registration form...")
                post_response = session.post(reg_url, data=form_data, allow_redirects=False)
                
                print(f"Response status: {post_response.status_code}")
                print(f"Response headers: {dict(post_response.headers)}")
                
                if post_response.status_code == 200:
                    # Check for error messages in response
                    response_soup = BeautifulSoup(post_response.text, 'html.parser')
                    
                    # Look for flash messages or error divs
                    flash_messages = response_soup.find_all(class_=['alert', 'flash', 'error', 'message'])
                    if flash_messages:
                        print("Flash messages found:")
                        for msg in flash_messages:
                            print(f"  - {msg.get_text().strip()}")
                    
                    # Look for form validation errors
                    error_elements = response_soup.find_all(class_=['error', 'invalid-feedback', 'field-error'])
                    if error_elements:
                        print("Form errors found:")
                        for error in error_elements:
                            print(f"  - {error.get_text().strip()}")
                    
                    if not flash_messages and not error_elements:
                        print("No obvious error messages found in response")
                        print("Response content preview:")
                        print(post_response.text[:500])
                
            else:
                print("❌ No registration form found on page")
                print("Page content preview:")
                print(reg_response.text[:500])
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_registration()
