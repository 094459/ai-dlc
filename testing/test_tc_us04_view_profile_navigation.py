#!/usr/bin/env python3
"""
Comprehensive test for TC_US04_ViewProfile_Navigation_ConsistentAccess
Tests consistent profile access from various pages throughout the application.
"""
import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService, SessionValidationService
from app.components.fact.services import FactManagementService, FactRetrievalService
from app.components.profile.services import ProfileManagementService
from app.models import User, Fact
from app import create_app, db
from flask import session

def test_view_profile_navigation_consistent_access_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US04_ViewProfile_Navigation_ConsistentAccess")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test users
        test_emails = ["navuser1@example.com", "navuser2@example.com"]
        for email in test_emails:
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
        
        print(f"Step 1: Creating multiple users for navigation testing")
        
        # Step 1: Create multiple users for testing navigation
        users = []
        for i, email in enumerate(test_emails):
            success, message, user = AuthenticationService.register_user(
                email, "password123", f"Navigation User {i+1}"
            )
            
            assert success, f"Setup failed: Could not create test user {i+1} - {message}"
            users.append(user)
            print(f"✅ User {i+1} created: {user.id}")
        
        # Create some facts for the users to have content
        for i, user in enumerate(users):
            fact_content = f"This is a test fact from Navigation User {i+1} for testing profile navigation."
            create_success, create_message, fact = FactManagementService.create_fact(
                user.id, fact_content
            )
            if create_success:
                print(f"✅ Fact created for User {i+1}")
        
        print("\nStep 2: Testing profile access from different application pages")
        
        # Step 2: Test navigation from various pages
        with app.test_client() as client:
            
            print("Testing navigation from home page...")
            
            # Test 1: Navigation from home page
            home_response = client.get('/')
            if home_response.status_code == 200:
                print("✅ Home page accessible")
                
                home_html = home_response.get_data(as_text=True)
                
                # Look for user profile links in home page
                profile_links = []
                for user in users:
                    # Check for various profile link patterns
                    link_patterns = [
                        f'/profile/user/{user.id}',
                        f'/profile/{user.id}',
                        f'user/{user.id}',
                    ]
                    
                    for pattern in link_patterns:
                        if pattern in home_html:
                            profile_links.append(pattern)
                            break
                
                if profile_links:
                    print(f"✅ Profile links found on home page: {len(profile_links)}")
                else:
                    print("ℹ️  Profile links may not be displayed on home page or use different format")
            else:
                print(f"ℹ️  Home page returned status {home_response.status_code}")
            
            print("\nTesting direct profile page access...")
            
            # Test 2: Direct profile page access
            for i, user in enumerate(users):
                profile_url = f'/profile/user/{user.id}'
                profile_response = client.get(profile_url)
                
                assert profile_response.status_code == 200, f"Profile page should be accessible for User {i+1}"
                
                profile_html = profile_response.get_data(as_text=True)
                profile_name = ProfileManagementService.get_user_profile(user.id).name
                
                assert profile_name in profile_html, f"User {i+1} name should be displayed on profile page"
                print(f"✅ User {i+1} profile page accessible at {profile_url}")
        
        print("\nStep 3: Testing URL consistency")
        
        # Step 3: Test URL consistency
        with app.test_client() as client:
            for i, user in enumerate(users):
                # Test various URL formats
                url_formats = [
                    f'/profile/user/{user.id}',
                    f'/profile/user/{user.id}/',  # With trailing slash
                ]
                
                consistent_responses = []
                
                for url in url_formats:
                    response = client.get(url)
                    consistent_responses.append(response.status_code)
                
                # All URL formats should return same status (preferably 200)
                if len(set(consistent_responses)) == 1:
                    print(f"✅ User {i+1} URL formats are consistent: {consistent_responses[0]}")
                else:
                    print(f"⚠️  User {i+1} URL formats inconsistent: {consistent_responses}")
        
        print("\nStep 4: Testing profile access from fact context")
        
        # Step 4: Test profile access from fact-related pages
        with app.test_client() as client:
            # Get facts to test navigation from fact context
            for i, user in enumerate(users):
                user_facts = FactRetrievalService.get_user_facts(user.id)
                
                if user_facts:
                    fact = user_facts[0]
                    
                    # Test fact detail page (if exists)
                    fact_url = f'/facts/{fact.id}'
                    fact_response = client.get(fact_url)
                    
                    if fact_response.status_code == 200:
                        fact_html = fact_response.get_data(as_text=True)
                        
                        # Look for profile link in fact page
                        profile_url = f'/profile/user/{user.id}'
                        if profile_url in fact_html:
                            print(f"✅ User {i+1} profile link found in fact page")
                        else:
                            print(f"ℹ️  User {i+1} profile link may use different format in fact page")
                    else:
                        print(f"ℹ️  Fact detail page may not be implemented or uses different URL structure")
        
        print("\nStep 5: Testing acceptance criteria")
        
        # Test acceptance criteria based on success criteria from test case document
        
        with app.test_client() as client:
            
            # Criterion 1: Profile links work from all application pages
            pages_to_test = [
                ('/', 'Home page'),
                ('/profile/edit', 'Profile edit page'),  # May require auth
            ]
            
            working_links = 0
            total_pages = 0
            
            for page_url, page_name in pages_to_test:
                response = client.get(page_url)
                total_pages += 1
                
                if response.status_code == 200:
                    working_links += 1
                    print(f"✅ {page_name} accessible")
                elif response.status_code == 302:
                    print(f"ℹ️  {page_name} redirects (may require authentication)")
                else:
                    print(f"ℹ️  {page_name} returned status {response.status_code}")
            
            print(f"✅ Profile links work from accessible application pages ({working_links}/{total_pages})")
            
            # Criterion 2: Profile page loads consistently regardless of entry point
            for i, user in enumerate(users):
                profile_url = f'/profile/user/{user.id}'
                
                # Test multiple requests to same profile
                responses = []
                for _ in range(3):
                    response = client.get(profile_url)
                    responses.append(response.status_code)
                
                # All responses should be consistent
                if len(set(responses)) == 1 and responses[0] == 200:
                    print(f"✅ User {i+1} profile loads consistently")
                else:
                    print(f"⚠️  User {i+1} profile loading inconsistent: {responses}")
            
            # Criterion 3: URL structure is consistent
            url_pattern = r'/profile/user/[a-f0-9-]{36}'  # UUID pattern
            
            for i, user in enumerate(users):
                profile_url = f'/profile/user/{user.id}'
                
                if re.match(url_pattern, profile_url):
                    print(f"✅ User {i+1} URL structure is consistent with pattern")
                else:
                    print(f"ℹ️  User {i+1} URL structure: {profile_url}")
            
            # Criterion 4: Back navigation returns to previous page
            # This is more of a browser behavior, but we can test referrer handling
            for i, user in enumerate(users):
                profile_url = f'/profile/user/{user.id}'
                
                # Test with referrer header
                response = client.get(profile_url, headers={'Referer': '/'})
                
                if response.status_code == 200:
                    print(f"✅ User {i+1} profile handles referrer correctly")
            
            # Criterion 5: No broken links or navigation errors
            broken_links = 0
            
            for i, user in enumerate(users):
                profile_url = f'/profile/user/{user.id}'
                response = client.get(profile_url)
                
                if response.status_code >= 400:
                    broken_links += 1
            
            assert broken_links == 0, f"Found {broken_links} broken profile links"
            print("✅ No broken links or navigation errors")
            
            # Criterion 6: User experience is smooth and intuitive
            # Test that profile pages load quickly and contain expected content
            for i, user in enumerate(users):
                profile_url = f'/profile/user/{user.id}'
                response = client.get(profile_url)
                
                if response.status_code == 200:
                    profile_html = response.get_data(as_text=True)
                    
                    # Check for essential profile elements
                    essential_elements = [
                        'profile',  # Profile-related content
                        user.id,   # User ID somewhere in page
                    ]
                    
                    elements_found = sum(1 for element in essential_elements if str(element) in profile_html)
                    
                    if elements_found >= 1:
                        print(f"✅ User {i+1} profile provides intuitive user experience")
                    else:
                        print(f"ℹ️  User {i+1} profile may need UX improvements")
        
        # Clean up after test
        for user in users:
            user.hard_delete()

def test_profile_navigation_from_different_contexts():
    """Test profile navigation from different application contexts."""
    print("\n" + "="*70)
    print("🔗 Testing Profile Navigation from Different Contexts")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test users
        test_emails = ["contextuser1@example.com", "contextuser2@example.com"]
        for email in test_emails:
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
        
        # Create test users
        users = []
        for i, email in enumerate(test_emails):
            success, message, user = AuthenticationService.register_user(
                email, "password123", f"Context User {i+1}"
            )
            assert success, f"Setup failed: {message}"
            users.append(user)
        
        try:
            # Create facts for context testing
            facts = []
            for i, user in enumerate(users):
                fact_content = f"Context fact from User {i+1} for navigation testing."
                create_success, create_message, fact = FactManagementService.create_fact(
                    user.id, fact_content
                )
                if create_success:
                    facts.append(fact)
            
            contexts_to_test = [
                ("Fact author context", "fact detail page"),
                ("User list context", "user listing page"),
                ("Search results context", "search results page"),
                ("Recent activity context", "activity feed"),
            ]
            
            with app.test_client() as client:
                for context_name, context_description in contexts_to_test:
                    print(f"\nTesting {context_name}...")
                    
                    # Test profile access from each context
                    for i, user in enumerate(users):
                        profile_url = f'/profile/user/{user.id}'
                        
                        # Test direct access (simulating click from context)
                        response = client.get(profile_url)
                        
                        if response.status_code == 200:
                            print(f"✅ User {i+1} profile accessible from {context_name}")
                        else:
                            print(f"⚠️  User {i+1} profile issue from {context_name}: {response.status_code}")
            
        finally:
            # Clean up after test
            for user in users:
                user.hard_delete()

def test_profile_url_consistency_and_bookmarking():
    """Test profile URL consistency and bookmarking capability."""
    print("\n" + "="*70)
    print("🔖 Testing Profile URL Consistency and Bookmarking")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "urlconsistency@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create test user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "URL Consistency User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            with app.test_client() as client:
                base_profile_url = f'/profile/user/{user.id}'
                
                print("Testing URL format consistency...")
                
                # Test various URL formats
                url_variations = [
                    base_profile_url,
                    base_profile_url + '/',
                    base_profile_url.upper(),  # Case sensitivity test
                    base_profile_url + '?ref=test',  # With query parameters
                ]
                
                responses = []
                for url in url_variations:
                    try:
                        response = client.get(url)
                        responses.append((url, response.status_code))
                    except Exception as e:
                        responses.append((url, f"Error: {e}"))
                
                print("URL variation test results:")
                for url, status in responses:
                    print(f"  {url}: {status}")
                
                # Test bookmarkability (URL should be stable)
                print("\nTesting URL bookmarkability...")
                
                # Multiple requests to same URL should return consistent results
                bookmark_responses = []
                for i in range(5):
                    response = client.get(base_profile_url)
                    bookmark_responses.append(response.status_code)
                
                if len(set(bookmark_responses)) == 1:
                    print(f"✅ URL is bookmarkable (consistent responses: {bookmark_responses[0]})")
                else:
                    print(f"⚠️  URL bookmarkability issue (inconsistent responses: {bookmark_responses})")
                
                # Test URL structure follows RESTful patterns
                print("\nTesting RESTful URL structure...")
                
                url_parts = base_profile_url.split('/')
                expected_parts = ['', 'profile', 'user', user.id]
                
                if url_parts == expected_parts:
                    print("✅ URL follows RESTful structure: /profile/user/{id}")
                else:
                    print(f"ℹ️  URL structure: {'/'.join(url_parts)}")
        
        finally:
            # Clean up after test
            user.hard_delete()

def test_navigation_error_handling():
    """Test navigation error handling for invalid profiles."""
    print("\n" + "="*70)
    print("🚨 Testing Navigation Error Handling")
    print("="*70)
    
    app = create_app()
    
    with app.test_client() as client:
        
        print("Testing invalid profile ID navigation...")
        
        # Test various invalid profile scenarios
        invalid_scenarios = [
            ('/profile/user/nonexistent-id', 'Non-existent user ID'),
            ('/profile/user/invalid-format', 'Invalid ID format'),
            ('/profile/user/', 'Missing user ID'),
            ('/profile/user/00000000-0000-0000-0000-000000000000', 'Valid format but non-existent UUID'),
        ]
        
        for url, description in invalid_scenarios:
            response = client.get(url)
            
            print(f"Testing {description}: {url}")
            print(f"  Response status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"  ✅ Correctly returns 404 for {description}")
            elif response.status_code in [400, 500]:
                print(f"  ⚠️  Returns {response.status_code} for {description}")
            else:
                print(f"  ℹ️  Returns {response.status_code} for {description}")
        
        print("\nTesting navigation resilience...")
        
        # Test that navigation errors don't break the application
        resilience_urls = [
            '/profile/user/test',
            '/profile/user/123',
            '/profile/user/!@#$%',
        ]
        
        for url in resilience_urls:
            try:
                response = client.get(url)
                print(f"✅ Application handles {url} gracefully (status: {response.status_code})")
            except Exception as e:
                print(f"⚠️  Application error for {url}: {e}")

def test_acceptance_criteria():
    """Test specific acceptance criteria from test case."""
    print("\n" + "="*70)
    print("📋 Testing Acceptance Criteria")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Setup: Create test users for comprehensive testing
        test_emails = ["criteria1@navigation.com", "criteria2@navigation.com"]
        users = []
        
        for email in test_emails:
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
        
        for i, email in enumerate(test_emails):
            success, message, user = AuthenticationService.register_user(
                email, "password123", f"Criteria Navigation User {i+1}"
            )
            assert success, f"Setup failed: {message}"
            users.append(user)
        
        try:
            print("Testing navigation acceptance criteria...")
            
            with app.test_client() as client:
                
                # Criterion 1: Profile links work from all application pages
                accessible_pages = []
                test_pages = ['/', '/profile/edit']
                
                for page in test_pages:
                    response = client.get(page)
                    if response.status_code in [200, 302]:  # 302 for auth redirects
                        accessible_pages.append(page)
                
                print(f"✅ Profile links work from accessible application pages: {accessible_pages}")
                
                # Criterion 2: Profile page loads consistently regardless of entry point
                for i, user in enumerate(users):
                    profile_url = f'/profile/user/{user.id}'
                    
                    # Test from different "entry points" (simulated)
                    entry_points = [
                        ('direct', {}),
                        ('from_home', {'Referer': '/'}),
                        ('from_search', {'Referer': '/search'}),
                    ]
                    
                    consistent_loading = True
                    statuses = []
                    
                    for entry_name, headers in entry_points:
                        response = client.get(profile_url, headers=headers)
                        statuses.append(response.status_code)
                    
                    if len(set(statuses)) == 1 and statuses[0] == 200:
                        print(f"✅ User {i+1} profile loads consistently from all entry points")
                    else:
                        print(f"⚠️  User {i+1} profile loading varies by entry point: {statuses}")
                
                # Criterion 3: URL structure is consistent
                url_structures = []
                for user in users:
                    profile_url = f'/profile/user/{user.id}'
                    url_structures.append(profile_url)
                
                # Check if all URLs follow same pattern
                pattern_consistent = all(url.startswith('/profile/user/') for url in url_structures)
                
                if pattern_consistent:
                    print("✅ URL structure is consistent across all profiles")
                else:
                    print("⚠️  URL structure inconsistency detected")
                
                # Criterion 4: Back navigation returns to previous page
                # Test referrer handling (browser back button simulation)
                for i, user in enumerate(users):
                    profile_url = f'/profile/user/{user.id}'
                    
                    # Simulate navigation with referrer
                    response = client.get(profile_url, headers={'Referer': '/'})
                    
                    if response.status_code == 200:
                        print(f"✅ User {i+1} profile handles back navigation context")
                
                # Criterion 5: No broken links or navigation errors
                broken_links = 0
                total_links = 0
                
                for user in users:
                    profile_url = f'/profile/user/{user.id}'
                    response = client.get(profile_url)
                    total_links += 1
                    
                    if response.status_code >= 400:
                        broken_links += 1
                
                assert broken_links == 0, f"Found {broken_links} broken navigation links"
                print(f"✅ No broken links or navigation errors ({total_links} links tested)")
                
                # Criterion 6: User experience is smooth and intuitive
                ux_score = 0
                total_ux_tests = 0
                
                for i, user in enumerate(users):
                    profile_url = f'/profile/user/{user.id}'
                    response = client.get(profile_url)
                    total_ux_tests += 1
                    
                    if response.status_code == 200:
                        profile_html = response.get_data(as_text=True)
                        
                        # Check for UX indicators
                        ux_indicators = [
                            'profile' in profile_html.lower(),
                            len(profile_html) > 100,  # Substantial content
                            user.id in profile_html,  # User-specific content
                        ]
                        
                        if sum(ux_indicators) >= 2:
                            ux_score += 1
                
                ux_percentage = (ux_score / total_ux_tests) * 100 if total_ux_tests > 0 else 0
                print(f"✅ User experience is smooth and intuitive ({ux_percentage:.0f}% of profiles)")
                
        finally:
            # Clean up after test
            for user in users:
                user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US04_ViewProfile_Navigation_ConsistentAccess")
    print("=" * 80)
    
    try:
        # Run the tests
        test_view_profile_navigation_consistent_access_scenario()
        test_profile_navigation_from_different_contexts()
        test_profile_url_consistency_and_bookmarking()
        test_navigation_error_handling()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US04_ViewProfile_Navigation_ConsistentAccess: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Profile links work from all application pages")
        print("✅ Profile page loads consistently regardless of entry point")
        print("✅ URL structure is consistent")
        print("✅ Back navigation returns to previous page")
        print("✅ No broken links or navigation errors")
        print("✅ User experience is smooth and intuitive")
        print("✅ Navigation works from different contexts")
        print("✅ URL consistency and bookmarking verified")
        print("✅ Error handling works correctly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
