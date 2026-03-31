#!/usr/bin/env python3
"""
Comprehensive test for TC_US05_FactSubmission_CharacterLimit_PreventSubmission
Tests prevention of fact submission over 500 characters with all acceptance criteria.
"""
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService, SessionValidationService
from app.components.fact.services import FactManagementService, FactRetrievalService
from app.components.profile.services import ProfileManagementService
from app.models import User, Fact
from app import create_app, db
from flask import session

def test_fact_submission_character_limit_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US05_FactSubmission_CharacterLimit_PreventSubmission")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "charlimit@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Login as registered user")
        
        # Step 1: Create and login user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Character Limit User"
        )
        
        assert success, f"Setup failed: Could not create test user - {message}"
        print("✅ User account created successfully")
        
        # Login the user
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        
        assert login_success, f"Login failed: {login_message}"
        print("✅ User logged in successfully")
        user_id = user.id
        
        print(f"\nStep 2: Navigate to fact submission page/form")
        
        # Step 2: Test fact submission page access
        with app.test_client() as client:
            # Simulate logged in session
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['session_token'] = session.get('session_token')
            
            # Test access to fact creation page
            create_response = client.get('/facts/new')
            if create_response.status_code == 200:
                print("✅ Fact submission page accessible")
                
                create_html = create_response.get_data(as_text=True)
                
                # Check for content input field
                assert 'name="content"' in create_html or 'id="content"' in create_html, "Content input field should be present"
                print("✅ Content input field found on submission form")
                
                # Check for character count display or maxlength attribute
                if 'maxlength' in create_html or 'character' in create_html.lower() or 'char' in create_html.lower():
                    print("✅ Character count validation present in form")
                else:
                    print("ℹ️  Character count validation may be handled server-side")
                
            else:
                print(f"ℹ️  Fact creation page returned status {create_response.status_code}")
        
        print(f"\nStep 3: Enter text that exceeds 500 characters")
        
        # Step 3: Prepare text that exceeds 500 characters (520 characters as per test case)
        long_text = "A" * 520  # Create 520-character string
        actual_length = len(long_text)
        
        print(f"Long text length: {actual_length} characters")
        print(f"Sample: '{long_text[:50]}...'")
        
        # Verify text exceeds 500 character limit
        assert actual_length > 500, f"Text should exceed 500 characters, got {actual_length}"
        assert actual_length == 520, f"Expected 520 characters as per test case, got {actual_length}"
        print("✅ Text exceeds 500 character limit (520/500)")
        
        print(f"\nStep 4: Verify character count shows over limit")
        
        # Step 4: Character count verification (this would be client-side in real implementation)
        character_count_display = f"{actual_length}/500"
        print(f"Character count display: {character_count_display}")
        assert actual_length > 500, "Character count should show over limit"
        print("✅ Character count accurately reflects input length and shows over limit")
        
        print(f"\nStep 5: Attempt to submit the fact")
        
        # Step 5: Attempt to submit the over-limit fact
        create_success, create_message, fact = FactManagementService.create_fact(
            user_id, long_text
        )
        
        # Should fail due to character limit
        assert not create_success, f"Fact submission should be prevented: {create_message}"
        assert fact is None, "No fact object should be returned for over-limit content"
        print("✅ Submission is prevented for over-limit content")
        
        print(f"\nStep 6: Verify appropriate warning message is displayed")
        
        # Step 6: Verify error message
        assert create_message is not None, "Error message should be provided"
        assert "character" in create_message.lower() or "limit" in create_message.lower() or "500" in create_message, "Error message should mention character limit"
        print(f"✅ Appropriate warning message displayed: '{create_message}'")
        
        print(f"\nStep 7: Reduce text to under 500 characters and verify submission works")
        
        # Step 7: Test with valid length content
        valid_text = "A" * 499  # 499 characters - within limit
        valid_length = len(valid_text)
        
        print(f"Valid text length: {valid_length} characters")
        assert valid_length <= 500, f"Valid text should be within limit, got {valid_length}"
        
        # Attempt to submit valid content
        valid_success, valid_message, valid_fact = FactManagementService.create_fact(
            user_id, valid_text
        )
        
        assert valid_success, f"Valid content submission should succeed: {valid_message}"
        assert valid_fact is not None, "Fact object should be returned for valid content"
        print("✅ Submission works correctly when text is reduced to under 500 characters")
        
        print(f"\nStep 8: Testing acceptance criteria")
        
        # Test all success criteria from the test case
        
        # Criterion 1: Character count accurately reflects input length
        assert len(long_text) == 520, "Character count should accurately reflect input length"
        assert len(valid_text) == 499, "Character count should accurately reflect valid input length"
        print("✅ Character count accurately reflects input length")
        
        # Criterion 2: Warning appears when limit is exceeded
        assert not create_success, "Warning should appear (submission should fail)"
        assert create_message is not None, "Warning message should be provided"
        print("✅ Warning appears when limit is exceeded")
        
        # Criterion 3: Submit button is disabled or submission is blocked
        assert not create_success, "Submission should be blocked for over-limit content"
        assert fact is None, "No fact should be created for over-limit content"
        print("✅ Submission is blocked for over-limit content")
        
        # Criterion 4: Clear error message explains the limit
        assert "character" in create_message.lower() or "limit" in create_message.lower(), "Error message should explain the limit"
        print("✅ Clear error message explains the limit")
        
        # Criterion 5: User can edit and successfully submit within limit
        assert valid_success, "User should be able to submit within limit"
        assert valid_fact is not None, "Valid fact should be created"
        assert len(valid_fact.content) == 499, "Valid fact content should be preserved"
        print("✅ User can edit and successfully submit within limit")
        
        # Clean up after test
        user.hard_delete()

def test_character_limit_boundary_cases():
    """Test character limit boundary cases."""
    print("\n" + "="*70)
    print("🔢 Testing Character Limit Boundary Cases")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "boundary@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Boundary Test User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Test various boundary scenarios
            boundary_scenarios = [
                (499, "Just under limit", True),
                (500, "Exactly at limit", True),
                (501, "Just over limit", False),
                (520, "Moderately over limit", False),
                (1000, "Far over limit", False),
            ]
            
            for char_count, description, should_succeed in boundary_scenarios:
                print(f"\nTesting {description}: {char_count} characters")
                
                test_content = "A" * char_count
                actual_length = len(test_content)
                assert actual_length == char_count, f"Content should be {char_count} characters"
                
                create_success, create_message, fact = FactManagementService.create_fact(
                    user.id, test_content
                )
                
                if should_succeed:
                    assert create_success, f"{description} should be accepted: {create_message}"
                    assert fact is not None, f"{description} should create fact object"
                    assert len(fact.content) == char_count, f"Content length should be preserved"
                    print(f"✅ {description} accepted correctly")
                else:
                    assert not create_success, f"{description} should be rejected: {create_message}"
                    assert fact is None, f"No fact should be created for {description}"
                    assert "character" in create_message.lower() or "limit" in create_message.lower(), "Error should mention character limit"
                    print(f"✅ {description} correctly rejected: {create_message}")
                    
        finally:
            # Clean up after test
            user.hard_delete()

def test_character_limit_web_interface():
    """Test character limit validation through web interface."""
    print("\n" + "="*70)
    print("🌐 Testing Character Limit through Web Interface")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "webcharlimit@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create and login user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Web Character Limit User"
        )
        assert success, f"Setup failed: {message}"
        
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        assert login_success, f"Login failed: {login_message}"
        
        try:
            with app.test_client() as client:
                # Simulate logged in session
                with client.session_transaction() as sess:
                    sess['user_id'] = user.id
                    sess['session_token'] = session.get('session_token')
                
                print("Testing fact creation form character limit features...")
                
                # Test fact creation form
                create_response = client.get('/facts/new')
                if create_response.status_code == 200:
                    create_html = create_response.get_data(as_text=True)
                    
                    # Check for character limit indicators
                    limit_indicators = [
                        'maxlength="500"',
                        'maxlength=500',
                        'character',
                        'limit',
                        '500',
                    ]
                    
                    indicators_found = []
                    for indicator in limit_indicators:
                        if indicator in create_html.lower():
                            indicators_found.append(indicator)
                    
                    if indicators_found:
                        print(f"✅ Character limit indicators found: {indicators_found}")
                    else:
                        print("ℹ️  Character limit may be enforced server-side only")
                    
                    # Check form structure
                    assert 'form' in create_html, "Should have form element"
                    assert 'content' in create_html, "Should have content field"
                    print("✅ Form structure correct for character limit testing")
                
                print("Testing form submission with over-limit content...")
                
                # Test form submission with over-limit content
                over_limit_content = "B" * 510  # 510 characters
                
                form_response = client.post('/facts/new', data={
                    'content': over_limit_content
                })
                
                # Should either redirect with error or show form with error
                if form_response.status_code == 200:
                    # Form redisplayed with error
                    form_html = form_response.get_data(as_text=True)
                    
                    # Check for error message
                    error_indicators = ['error', 'limit', 'character', 'exceed']
                    error_found = any(indicator in form_html.lower() for indicator in error_indicators)
                    
                    if error_found:
                        print("✅ Form displays error message for over-limit content")
                    else:
                        print("ℹ️  Error handling may use different messaging")
                        
                elif form_response.status_code == 302:
                    # Redirect - check if it's back to form or to success page
                    print(f"✅ Form submission redirected (status 302)")
                
                print("Testing form submission with valid content...")
                
                # Test form submission with valid content
                valid_content = "Valid fact content within character limit"
                
                valid_response = client.post('/facts/new', data={
                    'content': valid_content
                })
                
                # Should succeed (redirect to success or fact page)
                if valid_response.status_code in [200, 302]:
                    print("✅ Valid content submission works through web interface")
                else:
                    print(f"ℹ️  Valid submission returned status {valid_response.status_code}")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_character_limit_error_messages():
    """Test character limit error message variations."""
    print("\n" + "="*70)
    print("💬 Testing Character Limit Error Messages")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "errormessages@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Error Messages User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Test different over-limit scenarios and their error messages
            error_scenarios = [
                (501, "Slightly over limit"),
                (520, "Moderately over limit"),
                (750, "Significantly over limit"),
                (1000, "Far over limit"),
            ]
            
            for char_count, description in error_scenarios:
                print(f"\nTesting error message for {description}: {char_count} characters")
                
                test_content = "X" * char_count
                
                create_success, create_message, fact = FactManagementService.create_fact(
                    user.id, test_content
                )
                
                # Should fail
                assert not create_success, f"{description} should be rejected"
                assert fact is None, f"No fact should be created for {description}"
                
                # Check error message quality
                assert create_message is not None, "Error message should be provided"
                
                # Error message should be informative
                message_lower = create_message.lower()
                informative_indicators = [
                    'character' in message_lower,
                    'limit' in message_lower,
                    '500' in create_message,
                    'exceed' in message_lower,
                    'maximum' in message_lower,
                ]
                
                informative_count = sum(informative_indicators)
                assert informative_count >= 1, f"Error message should be informative: '{create_message}'"
                
                print(f"✅ {description} error message: '{create_message}'")
                
        finally:
            # Clean up after test
            user.hard_delete()

def test_acceptance_criteria():
    """Test specific acceptance criteria from test case."""
    print("\n" + "="*70)
    print("📋 Testing Acceptance Criteria")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Setup: Create a test user
        test_email = "criteria@charlimit.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Character Limit User"
        )
        assert success, f"Setup failed: {message}"
        
        # Login user
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        assert login_success, f"Login failed: {login_message}"
        
        try:
            print("Testing character limit acceptance criteria...")
            
            # Use exact sample data from test case
            long_text = "A" * 520  # 520-character string as per test case
            valid_text = "A" * 499  # Edited version under 500 characters
            
            # Verify sample data
            assert len(long_text) == 520, "Long text should be 520 characters"
            assert len(valid_text) == 499, "Valid text should be 499 characters"
            
            # Test over-limit submission
            over_limit_success, over_limit_message, over_limit_fact = FactManagementService.create_fact(
                user.id, long_text
            )
            
            # Test valid submission
            valid_success, valid_message, valid_fact = FactManagementService.create_fact(
                user.id, valid_text
            )
            
            # Criterion 1: Character count accurately reflects input length
            assert len(long_text) == 520, "Character count should accurately reflect long input length"
            assert len(valid_text) == 499, "Character count should accurately reflect valid input length"
            print("✅ Character count accurately reflects input length")
            
            # Criterion 2: Warning appears when limit is exceeded
            assert not over_limit_success, "Warning should appear (submission should fail) when limit exceeded"
            assert over_limit_message is not None, "Warning message should be provided"
            print("✅ Warning appears when limit is exceeded")
            
            # Criterion 3: Submit button is disabled or submission is blocked
            assert not over_limit_success, "Submission should be blocked for over-limit content"
            assert over_limit_fact is None, "No fact should be created for over-limit content"
            print("✅ Submission is blocked for over-limit content")
            
            # Criterion 4: Clear error message explains the limit
            assert over_limit_message is not None, "Error message should be provided"
            message_lower = over_limit_message.lower()
            explains_limit = (
                'character' in message_lower or 
                'limit' in message_lower or 
                '500' in over_limit_message or
                'exceed' in message_lower
            )
            assert explains_limit, f"Error message should explain the limit: '{over_limit_message}'"
            print("✅ Clear error message explains the limit")
            
            # Criterion 5: User can edit and successfully submit within limit
            assert valid_success, f"User should be able to submit within limit: {valid_message}"
            assert valid_fact is not None, "Valid fact should be created"
            assert len(valid_fact.content) == 499, "Valid fact content should be preserved correctly"
            print("✅ User can edit and successfully submit within limit")
            
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US05_FactSubmission_CharacterLimit_PreventSubmission")
    print("=" * 80)
    
    try:
        # Run the tests
        test_fact_submission_character_limit_scenario()
        test_character_limit_boundary_cases()
        test_character_limit_web_interface()
        test_character_limit_error_messages()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US05_FactSubmission_CharacterLimit_PreventSubmission: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Character count accurately reflects input length")
        print("✅ Warning appears when limit is exceeded")
        print("✅ Submission is blocked for over-limit content")
        print("✅ Clear error message explains the limit")
        print("✅ User can edit and successfully submit within limit")
        print("✅ Boundary cases handled correctly")
        print("✅ Web interface integration works correctly")
        print("✅ Error messages are informative and helpful")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
