#!/usr/bin/env python3
"""
Test cleanup utilities for database management during testing.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.models import User
from app import db

def cleanup_test_users(emails):
    """
    Thoroughly clean up test users by hard deleting them.
    
    Args:
        emails (list): List of email addresses to clean up
    """
    for email in emails:
        # Find all users with this email (both active and soft-deleted)
        users_to_delete = User.query.filter_by(email=email).all()
        
        for user in users_to_delete:
            try:
                # Use hard_delete to completely remove from database
                user.hard_delete()
                print(f"Hard deleted user: {email}")
            except Exception as e:
                print(f"Error deleting user {email}: {e}")
                # Fallback to SQLAlchemy delete
                try:
                    db.session.delete(user)
                    db.session.commit()
                    print(f"Fallback deleted user: {email}")
                except Exception as e2:
                    print(f"Fallback delete also failed for {email}: {e2}")

def verify_cleanup(emails):
    """
    Verify that test users have been completely removed.
    
    Args:
        emails (list): List of email addresses to verify
        
    Returns:
        bool: True if all emails are completely removed
    """
    remaining_users = User.query.filter(User.email.in_(emails)).all()
    if remaining_users:
        print(f"Warning: {len(remaining_users)} users still exist:")
        for user in remaining_users:
            print(f"  - {user.email} (deleted: {user.is_deleted})")
        return False
    return True

if __name__ == "__main__":
    # Test the cleanup utilities
    from app import create_app
    
    app = create_app()
    with app.app_context():
        test_emails = [
            'testuser@example.com',
            'caselogin@example.com', 
            'rememberme@example.com',
            'criteria@example.com',
            'security1@test.com',
            'security2@test.com',
            'nonexistent@test.com',
            'criteria@nonexistent.com',
            'existing@test.com',
            'casetest@example.com',
            'sessionuser@example.com',
            'shortsession@example.com',
            'expireduser@example.com',
            'logoutuser@example.com',
            'criteria@session.com',
            'validuser@example.com',
            'profileuser@example.com',
            'minimalprofile@example.com',
            'updateprofile@example.com',
            'validationprofile@example.com',
            'completionprofile@example.com',
            'criteria@profile.com',
            'minimaluser@example.com',
            'singlechar@example.com',
            'longname@example.com',
            'specialchars@example.com',
            'unicode@example.com',
            'minimal@compare.com',
            'complete@compare.com',
            'upgrade@example.com',
            'criteria@minimal.com',
            'photoupload@example.com',
            'photovalidation@example.com',
            'photosize@example.com',
            'photoreplace@example.com',
            'photodelete@example.com',
            'criteria@photo.com',
            'webphoto@example.com',
            'cssphoto@example.com',
            'format_jpg@example.com',
            'format_png@example.com',
            'format_gif@example.com',
            'biographylimit@example.com',
            'webbiography@example.com',
            'edgebiography@example.com',
            'whitespacebiography@example.com',
            'criteria@biography.com',
            'invalidformat@example.com',
            'webinvalidformat@example.com',
            'edgeinvalidformat@example.com',
            'formatcomparison@example.com',
            'criteria@invalidformat.com',
            'completeprofile@example.com',
            'minimal@profile.com',
            'partial@profile.com',
            'complete@profile.com',
            'publicprivate@example.com',
            'unicode@profile.com',
            'special@profile.com',
            'long@profile.com',
            'minimal@profile.com',
            'criteria@completeprofile.com',
            'nophoto@example.com',
            'minimal@nophoto.com',
            'partial@nophoto.com',
            'photodeletion@example.com',
            'placeholderstyling@example.com',
            'newuser@example.com',
            'longname@example.com',
            'unicode@example.com',
            'empty@example.com',
            'criteria@nophoto.com',
            'factschrono@example.com',
            'singlefact@example.com',
            'manyfacts@example.com',
            'nofacts@example.com',
            'timestampfacts@example.com',
            'criteria@factschrono.com',
            'navuser1@example.com',
            'navuser2@example.com',
            'contextuser1@example.com',
            'contextuser2@example.com',
            'urlconsistency@example.com',
            'criteria1@navigation.com',
            'criteria2@navigation.com',
            'factsubmission@example.com',
            'webfactsubmit@example.com',
            'charcount@example.com',
            'criteria@factsubmit.com',
            'charlimit@example.com',
            'boundary@example.com',
            'webcharlimit@example.com',
            'errormessages@example.com',
            'criteria@charlimit.com',
            'emptycontent@example.com',
            'webempty@example.com',
            'edgeempty@example.com',
            'errormsgempty@example.com',
            'criteria@emptycontent.com',
            'charcount@example.com',
            'webcharcount@example.com',
            'criteria@charcount.com',
            'multiplesubmit@example.com',
            'stresstest@example.com',
            'multiuser1@example.com',
            'multiuser2@example.com',
            'webmultiple@example.com',
            'criteria@multiplesubmit.com',
            'editownfact@example.com',
            'webeditfact@example.com',
            'editvalidation@example.com',
            'owner@example.com',
            'other@example.com',
            'criteria@editfact.com',
            'usera@example.com',
            'userb@example.com',
            'owner@multi.com',
            'user1@multi.com',
            'user2@multi.com',
            'webowner@example.com',
            'webother@example.com',
            'criteria_owner@example.com',
            'criteria_other@example.com',
            'edithistory@example.com',
            'publicview@example.com',
            'author1@example.com',
            'author2@example.com',
            'combined@example.com',
            'deleteconfirm@example.com',
            'deletepermanent@example.com',
            'editvalidation@example.com',
            'webvalidation@example.com',
            'finalcombined@example.com',
            'usera@voting.com',
            'userb@voting.com',
            'webowner@voting.com',
            'webvoter@voting.com',
            'edgeowner@voting.com',
            'edgevoter@voting.com',
            'criteria_owner@voting.com',
            'criteria_voter@voting.com',
            'ownfact@voting.com',
            'webself@voting.com',
            'security@voting.com',
            'other@voting.com',
            'criteria@ownvoting.com',
            'changevoter@voting.com',
            'factowner@voting.com',
            'realtime1@voting.com',
            'realtime2@voting.com',
            'realtimeowner@voting.com',
            'rapid0@voting.com',
            'rapid1@voting.com',
            'rapid2@voting.com',
            'display_owner@voting.com',
            'combined_owner@voting.com',
            'combined_voter@voting.com'
        ]
        
        # Add dynamic voter emails
        for i in range(35):
            test_emails.append(f'display_voter{i}@voting.com')
        
        # Add moderation test emails
        moderation_emails = [
            'user@test.com',
            'moderator@test.com', 
            'admin@test.com',
            'suspended@test.com',
            'suspended@mod.com',
            'inactive@mod.com',
            'dashboard@mod.com',
            'roletest@example.com'
        ]
        test_emails.extend(moderation_emails)
        
        # Add report test emails (with timestamp patterns)
        import time
        current_time = int(time.time())
        for i in range(5):  # Clean up recent timestamps
            timestamp = current_time - i
            report_emails = [
                f'content_owner_{timestamp}@test.com',
                f'reporter_{timestamp}@test.com',
                f'moderator_{timestamp}@test.com',
                f'second_reporter_{timestamp}@test.com'
            ]
            test_emails.extend(report_emails)
        
        # Add content removal test emails (with timestamp patterns)
        for i in range(5):  # Clean up recent timestamps
            timestamp = current_time - i
            removal_emails = [
                f'content_author_{timestamp}@test.com',
                f'edge_author_{timestamp}@test.com',
                f'edge_moderator_{timestamp}@test.com'
            ]
            test_emails.extend(removal_emails)
        
        # Add audit logging test emails (with timestamp patterns)
        for i in range(5):  # Clean up recent timestamps
            timestamp = current_time - i
            audit_emails = [
                f'audit_author_{timestamp}@test.com',
                f'audit_reporter_{timestamp}@test.com',
                f'audit_moderator1_{timestamp}@test.com',
                f'audit_moderator2_{timestamp}@test.com',
                f'coverage_author_{timestamp}@test.com',
                f'coverage_moderator_{timestamp}@test.com'
            ]
            test_emails.extend(audit_emails)
        
        # Add account removal test emails (with timestamp patterns)
        for i in range(5):  # Clean up recent timestamps
            timestamp = current_time - i
            account_emails = [
                f'remove_moderator_{timestamp}@test.com',
                f'target_user_{timestamp}@test.com',
                f'edge_moderator_{timestamp}@test.com',
                f'edge_user_{timestamp}@test.com',
                f'admin_moderator_{timestamp}@test.com',
                f'mgmt_user_{timestamp}@test.com'
            ]
            test_emails.extend(account_emails)
        
        # Add fact reporting test emails (with timestamp patterns)
        for i in range(5):  # Clean up recent timestamps
            timestamp = current_time - i
            reporting_emails = [
                f'fact_author_{timestamp}@test.com',
                f'reporting_user_{timestamp}@test.com',
                f'validation_author_{timestamp}@test.com',
                f'validation_reporter_{timestamp}@test.com',
                f'queue_author_{timestamp}@test.com',
                f'queue_reporter_{timestamp}@test.com',
                f'queue_moderator_{timestamp}@test.com'
            ]
            test_emails.extend(reporting_emails)
        
        print("Cleaning up test users...")
        cleanup_test_users(test_emails)
        
        print("\nVerifying cleanup...")
        if verify_cleanup(test_emails):
            print("✅ All test users successfully removed")
        else:
            print("❌ Some test users still exist")
