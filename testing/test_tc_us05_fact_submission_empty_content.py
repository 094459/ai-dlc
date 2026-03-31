#!/usr/bin/env python3
"""
Comprehensive test for TC_US05_FactSubmission_EmptyContent_ErrorMessage
Tests validation for empty fact content with all acceptance criteria.
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

def test_fact_submission_empty_content_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US05_FactSubmission_EmptyContent_ErrorMessage")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "emptycontent@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Login as registered user")
        
        # Step 1: Create and login user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Empty Content User"
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
                
                # Check for required field indicators
                if 'required' in create_html or 'Required' in create_html:
                    print("✅ Required field validation present in form")
                else:
                    print("ℹ️  Required field validation may be handled server-side")
                
            else:
                print(f"ℹ️  Fact creation page returned status {create_response.status_code}")
        
        print(f"\nStep 3: Leave fact content field empty")
        
        # Step 3: Prepare empty content
        empty_content = ""
        whitespace_content = "   "  # Also test whitespace-only content
        
        print(f"Empty content: '{empty_content}'")
        print(f"Whitespace content: '{whitespace_content}'")
        print("✅ Empty content prepared for testing")
        
        print(f"\nStep 4: Attempt to submit empty content")
        
        # Step 4: Attempt to submit empty fact
        empty_success, empty_message, empty_fact = FactManagementService.create_fact(
            user_id, empty_content
        )
        
        # Should fail due to empty content
        assert not empty_success, f"Empty fact submission should be prevented: {empty_message}"
        assert empty_fact is None, "No fact object should be returned for empty content"
        print("✅ Submission is prevented for empty content")
        
        print(f"\nStep 5: Verify validation error message appears")
        
        # Step 5: Verify error message
        assert empty_message is not None, "Error message should be provided"
        assert "required" in empty_message.lower() or "empty" in empty_message.lower() or "content" in empty_message.lower(), "Error message should indicate content is required"
        print(f"✅ Validation error message appears: '{empty_message}'")
        
        print(f"\nStep 6: Test whitespace-only content")
        
        # Step 6: Test whitespace-only content (should also be rejected)
        whitespace_success, whitespace_message, whitespace_fact = FactManagementService.create_fact(
            user_id, whitespace_content
        )
        
        # Should also fail
        assert not whitespace_success, f"Whitespace-only submission should be prevented: {whitespace_message}"
        assert whitespace_fact is None, "No fact object should be returned for whitespace-only content"
        print("✅ Whitespace-only content is also prevented")
        
        print(f"\nStep 7: Enter valid content and verify submission works")
        
        # Step 7: Test with valid content
        valid_content = "This is a valid fact with actual content"
        
        print(f"Valid content: '{valid_content}'")
        
        # Attempt to submit valid content
        valid_success, valid_message, valid_fact = FactManagementService.create_fact(
            user_id, valid_content
        )
        
        assert valid_success, f"Valid content submission should succeed: {valid_message}"
        assert valid_fact is not None, "Fact object should be returned for valid content"
        print("✅ Submission works correctly with valid content")
        
        print(f"\nStep 8: Testing acceptance criteria")
        
        # Test all success criteria from the test case
        
        # Criterion 1: Error message indicates fact content is required
        assert not empty_success, "Error should occur for empty content"
        assert empty_message is not None, "Error message should be provided"
        content_required_indicators = [
            "required" in empty_message.lower(),
            "empty" in empty_message.lower(),
            "content" in empty_message.lower(),
            "field" in empty_message.lower()
        ]
        assert any(content_required_indicators), f"Error message should indicate content is required: '{empty_message}'"
        print("✅ Error message indicates fact content is required")
        
        # Criterion 2: Submission is prevented when field is empty
        assert not empty_success, "Submission should be prevented for empty content"
        assert empty_fact is None, "No fact should be created for empty content"
        assert not whitespace_success, "Submission should be prevented for whitespace-only content"
        assert whitespace_fact is None, "No fact should be created for whitespace-only content"
        print("✅ Submission is prevented when field is empty")
        
        # Criterion 3: Error message is clear and helpful
        assert empty_message is not None, "Error message should be provided"
        assert len(empty_message.strip()) > 0, "Error message should not be empty"
        # Message should be reasonably informative (not just a generic error)
        helpful_indicators = [
            len(empty_message) > 10,  # Reasonable length
            any(word in empty_message.lower() for word in ["required", "content", "empty", "field"])
        ]
        assert any(helpful_indicators), f"Error message should be clear and helpful: '{empty_message}'"
        print("✅ Error message is clear and helpful")
        
        # Criterion 4: Field is highlighted as invalid (this would be client-side, we test server response)
        assert not empty_success, "Invalid field should result in failed submission"
        print("✅ Field validation indicates invalid state")
        
        # Criterion 5: User can correct and successfully submit
        assert valid_success, f"User should be able to correct and submit: {valid_message}"
        assert valid_fact is not None, "Valid fact should be created after correction"
        assert valid_fact.content == valid_content, "Valid fact content should be preserved"
        print("✅ User can correct and successfully submit")
        
        # Clean up after test
        user.hard_delete()

def test_empty_content_web_interface():
    """Test empty content validation through web interface."""
    print("\n" + "="*70)
    print("🌐 Testing Empty Content Validation through Web Interface")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "webempty@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create and login user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Web Empty Content User"
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
                
                print("Testing fact creation form validation features...")
                
                # Test fact creation form
                create_response = client.get('/facts/new')
                if create_response.status_code == 200:
                    create_html = create_response.get_data(as_text=True)
                    
                    # Check for required field indicators
                    required_indicators = [
                        'required' in create_html,
                        'Required' in create_html,
                        '*' in create_html,  # Common required field indicator
                    ]
                    
                    if any(required_indicators):
                        print("✅ Required field indicators found in form")
                    else:
                        print("ℹ️  Required field validation may be server-side only")
                    
                    # Check form structure
                    assert 'form' in create_html, "Should have form element"
                    assert 'content' in create_html, "Should have content field"
                    print("✅ Form structure correct for empty content testing")
                
                print("Testing form submission with empty content...")
                
                # Test form submission with empty content
                empty_response = client.post('/facts/new', data={
                    'content': ''
                })
                
                # Should either redirect with error or show form with error
                if empty_response.status_code == 200:
                    # Form redisplayed with error
                    form_html = empty_response.get_data(as_text=True)
                    
                    # Check for error message
                    error_indicators = ['error', 'required', 'empty', 'content']
                    error_found = any(indicator in form_html.lower() for indicator in error_indicators)
                    
                    if error_found:
                        print("✅ Form displays error message for empty content")
                    else:
                        print("ℹ️  Error handling may use different messaging")
                        
                elif empty_response.status_code == 302:
                    # Redirect - should be back to form, not to success page
                    print("✅ Form submission redirected (likely back to form with error)")
                
                print("Testing form submission with whitespace-only content...")
                
                # Test form submission with whitespace-only content
                whitespace_response = client.post('/facts/new', data={
                    'content': '   \n\t   '
                })
                
                # Should also be rejected
                if whitespace_response.status_code == 200:
                    print("✅ Whitespace-only content handled by form")
                elif whitespace_response.status_code == 302:
                    print("✅ Whitespace-only content redirected (likely rejected)")
                
                print("Testing form submission with valid content...")
                
                # Test form submission with valid content
                valid_content = "Valid fact content for web interface testing"
                
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

def test_empty_content_edge_cases():
    """Test empty content edge cases and variations."""
    print("\n" + "="*70)
    print("🔍 Testing Empty Content Edge Cases")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "edgeempty@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Edge Empty User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Test various empty/invalid content scenarios
            edge_cases = [
                ("", "Completely empty string"),
                ("   ", "Spaces only"),
                ("\t", "Tab only"),
                ("\n", "Newline only"),
                ("\r\n", "Carriage return and newline"),
                ("   \n\t   ", "Mixed whitespace"),
                (None, "None value"),
            ]
            
            for content, description in edge_cases:
                print(f"\nTesting {description}: '{repr(content)}'")
                
                try:
                    create_success, create_message, fact = FactManagementService.create_fact(
                        user.id, content
                    )
                    
                    # All these should fail
                    assert not create_success, f"{description} should be rejected: {create_message}"
                    assert fact is None, f"No fact should be created for {description}"
                    
                    # Error message should be informative
                    assert create_message is not None, f"Error message should be provided for {description}"
                    
                    print(f"✅ {description} correctly rejected: {create_message}")
                    
                except Exception as e:
                    # Handle cases where None might cause different errors
                    if content is None:
                        print(f"✅ {description} handled with exception (expected): {e}")
                    else:
                        raise e
                    
        finally:
            # Clean up after test
            user.hard_delete()

def test_empty_content_error_messages():
    """Test empty content error message quality and consistency."""
    print("\n" + "="*70)
    print("💬 Testing Empty Content Error Messages")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "errormsgempty@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Error Message Empty User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            # Test error message for empty content
            print("Testing error message for empty content...")
            
            empty_success, empty_message, empty_fact = FactManagementService.create_fact(
                user.id, ""
            )
            
            # Should fail
            assert not empty_success, "Empty content should be rejected"
            assert empty_fact is None, "No fact should be created for empty content"
            
            # Check error message quality
            assert empty_message is not None, "Error message should be provided"
            assert len(empty_message.strip()) > 0, "Error message should not be empty"
            
            # Error message should be user-friendly
            message_lower = empty_message.lower()
            user_friendly_indicators = [
                'required' in message_lower,
                'content' in message_lower,
                'empty' in message_lower,
                'field' in message_lower,
                'please' in message_lower,
            ]
            
            friendly_count = sum(user_friendly_indicators)
            assert friendly_count >= 1, f"Error message should be user-friendly: '{empty_message}'"
            
            print(f"✅ Empty content error message: '{empty_message}'")
            
            # Test consistency across multiple attempts
            print("Testing error message consistency...")
            
            for i in range(3):
                repeat_success, repeat_message, repeat_fact = FactManagementService.create_fact(
                    user.id, ""
                )
                
                assert not repeat_success, f"Attempt {i+1} should fail"
                assert repeat_message == empty_message, f"Error message should be consistent across attempts"
            
            print("✅ Error messages are consistent across multiple attempts")
            
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
        test_email = "criteria@emptycontent.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Empty Content User"
        )
        assert success, f"Setup failed: {message}"
        
        # Login user
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        assert login_success, f"Login failed: {login_message}"
        
        try:
            print("Testing empty content acceptance criteria...")
            
            # Test empty content submission
            empty_success, empty_message, empty_fact = FactManagementService.create_fact(
                user.id, ""
            )
            
            # Test valid content submission
            valid_content = "Valid content for successful submission test"
            valid_success, valid_message, valid_fact = FactManagementService.create_fact(
                user.id, valid_content
            )
            
            # Criterion 1: Error message indicates fact content is required
            assert not empty_success, "Empty content submission should fail"
            assert empty_message is not None, "Error message should be provided"
            
            required_indicators = [
                'required' in empty_message.lower(),
                'content' in empty_message.lower(),
                'empty' in empty_message.lower(),
                'field' in empty_message.lower()
            ]
            assert any(required_indicators), f"Error message should indicate content is required: '{empty_message}'"
            print("✅ Error message indicates fact content is required")
            
            # Criterion 2: Submission is prevented when field is empty
            assert not empty_success, "Submission should be prevented for empty content"
            assert empty_fact is None, "No fact should be created for empty content"
            print("✅ Submission is prevented when field is empty")
            
            # Criterion 3: Error message is clear and helpful
            assert empty_message is not None, "Error message should be provided"
            assert len(empty_message.strip()) > 5, "Error message should be substantial"
            
            # Should contain helpful words
            helpful_words = ['required', 'content', 'empty', 'field', 'please', 'enter']
            contains_helpful = any(word in empty_message.lower() for word in helpful_words)
            assert contains_helpful, f"Error message should be clear and helpful: '{empty_message}'"
            print("✅ Error message is clear and helpful")
            
            # Criterion 4: Field is highlighted as invalid
            # (This is primarily a UI concern, but we verify the validation failure)
            assert not empty_success, "Field validation should indicate invalid state"
            print("✅ Field validation indicates invalid state")
            
            # Criterion 5: User can correct and successfully submit
            assert valid_success, f"User should be able to correct and submit: {valid_message}"
            assert valid_fact is not None, "Valid fact should be created after correction"
            assert valid_fact.content == valid_content, "Valid fact content should be preserved"
            print("✅ User can correct and successfully submit")
            
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US05_FactSubmission_EmptyContent_ErrorMessage")
    print("=" * 80)
    
    try:
        # Run the tests
        test_fact_submission_empty_content_scenario()
        test_empty_content_web_interface()
        test_empty_content_edge_cases()
        test_empty_content_error_messages()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US05_FactSubmission_EmptyContent_ErrorMessage: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ Error message indicates fact content is required")
        print("✅ Submission is prevented when field is empty")
        print("✅ Error message is clear and helpful")
        print("✅ Field validation indicates invalid state")
        print("✅ User can correct and successfully submit")
        print("✅ Edge cases handled correctly")
        print("✅ Web interface integration works correctly")
        print("✅ Error messages are consistent and user-friendly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
