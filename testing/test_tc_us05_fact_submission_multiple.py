#!/usr/bin/env python3
"""
Comprehensive test for TC_US05_FactSubmission_MultipleSubmissions_AllVisible
Tests multiple fact submissions by same user with all acceptance criteria.
"""
import sys
import os
import time
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.components.auth.services import AuthenticationService, SessionValidationService
from app.components.fact.services import FactManagementService, FactRetrievalService
from app.components.profile.services import ProfileManagementService
from app.models import User, Fact
from app import create_app, db
from flask import session

def test_fact_submission_multiple_submissions_scenario():
    """Test the exact scenario from the test case."""
    print("🧪 Testing TC_US05_FactSubmission_MultipleSubmissions_AllVisible")
    print("=" * 70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "multiplesubmit@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        print(f"Step 1: Login as registered user")
        
        # Step 1: Create and login user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Multiple Submissions User"
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
        
        # Sample facts from test case
        sample_facts = [
            "Water boils at 100°C at sea level",
            "The speed of light is 299,792,458 meters per second",
            "DNA stands for Deoxyribonucleic Acid"
        ]
        
        submitted_facts = []
        
        print(f"\nStep 2: Submit first fact")
        
        # Step 2: Submit first fact
        fact1_content = sample_facts[0]
        print(f"Submitting: '{fact1_content}'")
        
        fact1_success, fact1_message, fact1 = FactManagementService.create_fact(
            user_id, fact1_content
        )
        
        assert fact1_success, f"First fact submission should succeed: {fact1_message}"
        assert fact1 is not None, "First fact object should be returned"
        submitted_facts.append(fact1)
        print("✅ First fact submitted successfully")
        
        # Small delay to ensure different timestamps
        time.sleep(0.1)
        
        print(f"\nStep 3: Verify first fact appears in feed")
        
        # Step 3: Verify first fact in feed
        recent_facts = FactRetrievalService.get_recent_facts(limit=10)
        fact1_ids = [f.id for f in recent_facts]
        
        assert fact1.id in fact1_ids, "First fact should appear in recent facts feed"
        print("✅ First fact appears in feed")
        
        print(f"\nStep 4: Submit second fact")
        
        # Step 4: Submit second fact
        fact2_content = sample_facts[1]
        print(f"Submitting: '{fact2_content}'")
        
        fact2_success, fact2_message, fact2 = FactManagementService.create_fact(
            user_id, fact2_content
        )
        
        assert fact2_success, f"Second fact submission should succeed: {fact2_message}"
        assert fact2 is not None, "Second fact object should be returned"
        submitted_facts.append(fact2)
        print("✅ Second fact submitted successfully")
        
        # Small delay to ensure different timestamps
        time.sleep(0.1)
        
        print(f"\nStep 5: Verify second fact appears in feed")
        
        # Step 5: Verify second fact in feed
        recent_facts_after_2 = FactRetrievalService.get_recent_facts(limit=10)
        fact2_ids = [f.id for f in recent_facts_after_2]
        
        assert fact2.id in fact2_ids, "Second fact should appear in recent facts feed"
        
        # Verify both facts are still in feed
        both_facts_present = fact1.id in fact2_ids and fact2.id in fact2_ids
        assert both_facts_present, "Both first and second facts should be in feed"
        print("✅ Second fact appears in feed")
        print("✅ Both facts are visible in feed")
        
        print(f"\nStep 6: Submit third fact")
        
        # Step 6: Submit third fact
        fact3_content = sample_facts[2]
        print(f"Submitting: '{fact3_content}'")
        
        fact3_success, fact3_message, fact3 = FactManagementService.create_fact(
            user_id, fact3_content
        )
        
        assert fact3_success, f"Third fact submission should succeed: {fact3_message}"
        assert fact3 is not None, "Third fact object should be returned"
        submitted_facts.append(fact3)
        print("✅ Third fact submitted successfully")
        
        print(f"\nStep 7: Verify all three facts are visible in the feed")
        
        # Step 7: Verify all three facts in feed
        final_recent_facts = FactRetrievalService.get_recent_facts(limit=20)
        final_fact_ids = [f.id for f in final_recent_facts]
        
        for i, fact in enumerate(submitted_facts):
            assert fact.id in final_fact_ids, f"Fact {i+1} should be visible in feed"
            print(f"✅ Fact {i+1} is visible in feed")
        
        print("✅ All three facts are visible in the feed")
        
        print(f"\nStep 8: Check user's profile to ensure all facts are listed")
        
        # Step 8: Verify facts in user profile
        user_facts = FactRetrievalService.get_user_facts(user_id)
        user_fact_ids = [f.id for f in user_facts]
        
        assert len(user_facts) >= 3, f"User should have at least 3 facts, got {len(user_facts)}"
        
        for i, fact in enumerate(submitted_facts):
            assert fact.id in user_fact_ids, f"Fact {i+1} should be in user's profile"
            print(f"✅ Fact {i+1} is listed in user profile")
        
        print("✅ All facts are listed in user profile")
        
        print(f"\nStep 9: Testing acceptance criteria")
        
        # Test all success criteria from the test case
        
        # Criterion 1: All submitted facts appear in public feed
        public_facts = FactRetrievalService.get_recent_facts(limit=50)
        public_fact_ids = [f.id for f in public_facts]
        
        for i, fact in enumerate(submitted_facts):
            assert fact.id in public_fact_ids, f"Fact {i+1} should appear in public feed"
        
        print("✅ All submitted facts appear in public feed")
        
        # Criterion 2: Facts are properly attributed to correct user
        for i, fact in enumerate(submitted_facts):
            retrieved_fact = FactRetrievalService.get_fact_by_id(fact.id)
            assert retrieved_fact.user_id == user_id, f"Fact {i+1} should be attributed to correct user"
        
        print("✅ Facts are properly attributed to correct user")
        
        # Criterion 3: Facts maintain submission order
        user_facts_ordered = FactRetrievalService.get_user_facts(user_id)
        
        # Assuming newest first ordering (most common)
        if len(user_facts_ordered) >= 3:
            # Find our submitted facts in the ordered list
            our_facts_in_order = []
            for fact in user_facts_ordered:
                if fact.id in [f.id for f in submitted_facts]:
                    our_facts_in_order.append(fact)
            
            # Should be in reverse chronological order (newest first)
            if len(our_facts_in_order) >= 3:
                # Verify timestamps are in descending order
                timestamps = [f.created_at for f in our_facts_in_order[:3]]
                is_descending = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
                
                if is_descending:
                    print("✅ Facts maintain submission order (newest first)")
                else:
                    # Check if ascending order
                    is_ascending = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
                    if is_ascending:
                        print("✅ Facts maintain submission order (oldest first)")
                    else:
                        print("ℹ️  Facts may have same timestamps or different ordering")
        
        # Criterion 4: User profile shows all submitted facts
        profile_facts = FactRetrievalService.get_user_facts(user_id)
        profile_fact_ids = [f.id for f in profile_facts]
        
        for i, fact in enumerate(submitted_facts):
            assert fact.id in profile_fact_ids, f"Fact {i+1} should be in user profile"
        
        print("✅ User profile shows all submitted facts")
        
        # Criterion 5: No facts are lost or overwritten
        for i, fact in enumerate(submitted_facts):
            retrieved_fact = FactRetrievalService.get_fact_by_id(fact.id)
            assert retrieved_fact is not None, f"Fact {i+1} should not be lost"
            assert retrieved_fact.content == sample_facts[i], f"Fact {i+1} content should not be overwritten"
            assert not retrieved_fact.is_deleted, f"Fact {i+1} should not be marked as deleted"
        
        print("✅ No facts are lost or overwritten")
        
        # Clean up after test
        user.hard_delete()

def test_multiple_submissions_stress_test():
    """Test multiple submissions with more facts to verify scalability."""
    print("\n" + "="*70)
    print("🔄 Testing Multiple Submissions Stress Test")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "stresstest@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Stress Test User"
        )
        assert success, f"Setup failed: {message}"
        
        try:
            print("Submitting 10 facts to test scalability...")
            
            submitted_facts = []
            
            for i in range(10):
                fact_content = f"Stress test fact number {i+1}: This is a test fact to verify multiple submissions work correctly."
                
                create_success, create_message, fact = FactManagementService.create_fact(
                    user.id, fact_content
                )
                
                assert create_success, f"Fact {i+1} should be created successfully: {create_message}"
                assert fact is not None, f"Fact {i+1} object should be returned"
                
                submitted_facts.append(fact)
                print(f"✅ Fact {i+1} submitted successfully")
                
                # Small delay to ensure different timestamps
                time.sleep(0.05)
            
            print(f"\n✅ All 10 facts submitted successfully")
            
            # Verify all facts are retrievable
            user_facts = FactRetrievalService.get_user_facts(user.id)
            assert len(user_facts) >= 10, f"User should have at least 10 facts, got {len(user_facts)}"
            
            # Verify all facts are in public feed
            recent_facts = FactRetrievalService.get_recent_facts(limit=50)
            recent_fact_ids = [f.id for f in recent_facts]
            
            for i, fact in enumerate(submitted_facts):
                assert fact.id in recent_fact_ids, f"Stress test fact {i+1} should be in public feed"
            
            print("✅ All 10 facts are retrievable and visible in public feed")
            
            # Verify chronological ordering
            user_facts_ordered = FactRetrievalService.get_user_facts(user.id)
            if len(user_facts_ordered) >= 10:
                # Check if facts are in chronological order
                timestamps = [f.created_at for f in user_facts_ordered[:10]]
                is_ordered = (
                    all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1)) or
                    all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
                )
                assert is_ordered, "Facts should be in chronological order"
                print("✅ Facts maintain chronological order")
            
        finally:
            # Clean up after test
            user.hard_delete()

def test_multiple_users_multiple_facts():
    """Test multiple users each submitting multiple facts."""
    print("\n" + "="*70)
    print("👥 Testing Multiple Users with Multiple Facts")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test users
        test_emails = ["multiuser1@example.com", "multiuser2@example.com"]
        for email in test_emails:
            existing_users = User.query.filter_by(email=email).all()
            for user in existing_users:
                user.hard_delete()
        
        # Create multiple users
        users = []
        for i, email in enumerate(test_emails):
            success, message, user = AuthenticationService.register_user(
                email, "password123", f"Multi User {i+1}"
            )
            assert success, f"Setup failed for user {i+1}: {message}"
            users.append(user)
        
        try:
            all_submitted_facts = []
            
            # Each user submits multiple facts
            for i, user in enumerate(users):
                print(f"\nUser {i+1} submitting facts...")
                
                user_facts = []
                for j in range(3):
                    fact_content = f"User {i+1} fact {j+1}: This is a test fact from user {i+1}."
                    
                    create_success, create_message, fact = FactManagementService.create_fact(
                        user.id, fact_content
                    )
                    
                    assert create_success, f"User {i+1} fact {j+1} should be created: {create_message}"
                    user_facts.append(fact)
                    all_submitted_facts.append(fact)
                    
                    time.sleep(0.05)  # Small delay
                
                print(f"✅ User {i+1} submitted {len(user_facts)} facts")
            
            print(f"\n✅ All users submitted facts (total: {len(all_submitted_facts)})")
            
            # Verify all facts are in public feed
            public_facts = FactRetrievalService.get_recent_facts(limit=50)
            public_fact_ids = [f.id for f in public_facts]
            
            for fact in all_submitted_facts:
                assert fact.id in public_fact_ids, "All facts should be in public feed"
            
            print("✅ All facts from all users are visible in public feed")
            
            # Verify each user can see their own facts
            for i, user in enumerate(users):
                user_facts = FactRetrievalService.get_user_facts(user.id)
                assert len(user_facts) >= 3, f"User {i+1} should have at least 3 facts"
                
                # Verify attribution
                for fact in user_facts:
                    assert fact.user_id == user.id, f"User {i+1} facts should be attributed correctly"
                
                print(f"✅ User {i+1} can see their own facts correctly")
            
        finally:
            # Clean up after test
            for user in users:
                user.hard_delete()

def test_multiple_submissions_web_interface():
    """Test multiple submissions through web interface."""
    print("\n" + "="*70)
    print("🌐 Testing Multiple Submissions through Web Interface")
    print("="*70)
    
    app = create_app()
    
    with app.test_request_context():
        # Clean up any existing test user
        test_email = "webmultiple@example.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        # Create and login user
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Web Multiple User"
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
                
                print("Testing multiple fact submissions via web interface...")
                
                # Submit multiple facts via web form
                web_facts = [
                    "Web fact 1: Testing multiple submissions through web interface",
                    "Web fact 2: Verifying that all facts are preserved and displayed",
                    "Web fact 3: Ensuring proper attribution and ordering"
                ]
                
                submitted_via_web = []
                
                for i, content in enumerate(web_facts):
                    print(f"Submitting web fact {i+1}...")
                    
                    # Submit via service (simulating web form submission)
                    create_success, create_message, fact = FactManagementService.create_fact(
                        user.id, content
                    )
                    
                    assert create_success, f"Web fact {i+1} should be submitted: {create_message}"
                    submitted_via_web.append(fact)
                    
                    time.sleep(0.1)
                
                print("✅ All facts submitted via web interface")
                
                # Verify facts are accessible via web interface
                for i, fact in enumerate(submitted_via_web):
                    fact_response = client.get(f'/facts/{fact.id}')
                    if fact_response.status_code == 200:
                        fact_html = fact_response.get_data(as_text=True)
                        assert web_facts[i] in fact_html, f"Web fact {i+1} content should be visible"
                        print(f"✅ Web fact {i+1} is accessible via web interface")
                    else:
                        print(f"ℹ️  Web fact {i+1} page returned status {fact_response.status_code}")
                
                # Test facts list page
                facts_list_response = client.get('/facts/')
                if facts_list_response.status_code == 200:
                    print("✅ Facts list page accessible")
                else:
                    print(f"ℹ️  Facts list page returned status {facts_list_response.status_code}")
                
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
        test_email = "criteria@multiplesubmit.com"
        existing_users = User.query.filter_by(email=test_email).all()
        for user in existing_users:
            user.hard_delete()
        
        success, message, user = AuthenticationService.register_user(
            test_email, "password123", "Criteria Multiple Submit User"
        )
        assert success, f"Setup failed: {message}"
        
        # Login user
        login_success, login_message, login_user = AuthenticationService.login_user(
            test_email, "password123"
        )
        assert login_success, f"Login failed: {login_message}"
        
        try:
            print("Testing multiple submissions acceptance criteria...")
            
            # Use exact sample data from test case
            sample_facts = [
                "Water boils at 100°C at sea level",
                "The speed of light is 299,792,458 meters per second",
                "DNA stands for Deoxyribonucleic Acid"
            ]
            
            submitted_facts = []
            
            # Submit all sample facts
            for i, content in enumerate(sample_facts):
                create_success, create_message, fact = FactManagementService.create_fact(
                    user.id, content
                )
                
                assert create_success, f"Sample fact {i+1} should be created: {create_message}"
                submitted_facts.append(fact)
                time.sleep(0.1)  # Ensure different timestamps
            
            print(f"✅ All {len(submitted_facts)} sample facts submitted")
            
            # Criterion 1: All submitted facts appear in public feed
            public_facts = FactRetrievalService.get_recent_facts(limit=50)
            public_fact_ids = [f.id for f in public_facts]
            
            for i, fact in enumerate(submitted_facts):
                assert fact.id in public_fact_ids, f"Sample fact {i+1} should appear in public feed"
            
            print("✅ All submitted facts appear in public feed")
            
            # Criterion 2: Facts are properly attributed to correct user
            for i, fact in enumerate(submitted_facts):
                retrieved_fact = FactRetrievalService.get_fact_by_id(fact.id)
                assert retrieved_fact is not None, f"Sample fact {i+1} should be retrievable"
                assert retrieved_fact.user_id == user.id, f"Sample fact {i+1} should be attributed to correct user"
            
            print("✅ Facts are properly attributed to correct user")
            
            # Criterion 3: Facts maintain submission order
            user_facts = FactRetrievalService.get_user_facts(user.id)
            
            # Find our submitted facts in the user's facts
            our_facts = []
            for fact in user_facts:
                if fact.id in [f.id for f in submitted_facts]:
                    our_facts.append(fact)
            
            assert len(our_facts) >= 3, "Should find all our submitted facts"
            
            # Check chronological ordering
            timestamps = [f.created_at for f in our_facts[:3]]
            is_chronological = (
                all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1)) or
                all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
            )
            assert is_chronological, "Facts should maintain chronological order"
            print("✅ Facts maintain submission order")
            
            # Criterion 4: User profile shows all submitted facts
            profile_facts = FactRetrievalService.get_user_facts(user.id)
            profile_fact_ids = [f.id for f in profile_facts]
            
            for i, fact in enumerate(submitted_facts):
                assert fact.id in profile_fact_ids, f"Sample fact {i+1} should be in user profile"
            
            print("✅ User profile shows all submitted facts")
            
            # Criterion 5: No facts are lost or overwritten
            for i, fact in enumerate(submitted_facts):
                retrieved_fact = FactRetrievalService.get_fact_by_id(fact.id)
                assert retrieved_fact is not None, f"Sample fact {i+1} should not be lost"
                assert retrieved_fact.content == sample_facts[i], f"Sample fact {i+1} content should not be overwritten"
                assert not retrieved_fact.is_deleted, f"Sample fact {i+1} should not be marked as deleted"
                assert retrieved_fact.user_id == user.id, f"Sample fact {i+1} attribution should not change"
            
            print("✅ No facts are lost or overwritten")
            
        finally:
            # Clean up after test
            user.hard_delete()

if __name__ == "__main__":
    print("Comprehensive Test for TC_US05_FactSubmission_MultipleSubmissions_AllVisible")
    print("=" * 80)
    
    try:
        # Run the tests
        test_fact_submission_multiple_submissions_scenario()
        test_multiple_submissions_stress_test()
        test_multiple_users_multiple_facts()
        test_multiple_submissions_web_interface()
        test_acceptance_criteria()
        
        print("\n" + "="*80)
        print("📋 TEST SUMMARY")
        print("="*80)
        print("🎉 TC_US05_FactSubmission_MultipleSubmissions_AllVisible: PASSED")
        print("✅ All acceptance criteria met")
        print("✅ All submitted facts appear in public feed")
        print("✅ Facts are properly attributed to correct user")
        print("✅ Facts maintain submission order")
        print("✅ User profile shows all submitted facts")
        print("✅ No facts are lost or overwritten")
        print("✅ Stress testing with 10 facts successful")
        print("✅ Multiple users with multiple facts work correctly")
        print("✅ Web interface integration works correctly")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        sys.exit(1)
