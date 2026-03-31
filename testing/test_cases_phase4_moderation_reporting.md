# Phase 4: Content Moderation & Reporting - Detailed Test Cases

## TC_US15_Moderation_AccessDashboard_ModeratorOnly

**Objective**: Verify only moderators can access moderation dashboard

**Test Steps**:
1. Login as regular user (non-moderator)
2. Attempt to access moderation dashboard URL directly
3. Verify access is denied with appropriate error message
4. Logout and login as designated moderator account
5. Navigate to moderation dashboard
6. Verify dashboard loads successfully with moderation tools
7. Test with admin account to verify access levels
8. Test with suspended moderator account (if applicable)

**Assumptions**:
- Moderator role is distinct from regular user role
- Access control is enforced at both UI and backend levels
- Moderation dashboard has dedicated URL/navigation

**Success Criteria**:
- Regular users cannot access moderation dashboard
- Appropriate error message for unauthorized access
- Moderators can successfully access dashboard
- Dashboard displays moderation tools and reported content
- Access control is consistently enforced
- Clear distinction between user roles

**Sample Data**:
- Regular user account: "user@test.com"
- Moderator account: "moderator@test.com"
- Admin account: "admin@test.com"

---

## TC_US15_Moderation_ReviewContent_ReportedItems

**Objective**: Verify moderators can see reported content

**Test Steps**:
1. As regular user, report a fact and comment for inappropriate content
2. Login as moderator
3. Access moderation dashboard
4. Verify reported items appear in moderation queue
5. Verify report details include: content, reporter info, reason, timestamp
6. Test filtering/sorting of reported items
7. Verify both fact and comment reports are visible
8. Test with multiple reports on same content

**Assumptions**:
- Reported content appears in moderation dashboard
- Report details provide sufficient context for moderation decisions
- Moderation queue is organized and searchable

**Success Criteria**:
- All reported content appears in moderation dashboard
- Report details are complete and accurate
- Reports are organized chronologically or by priority
- Moderators can easily review and assess reports
- Queue shows both facts and comments
- Multiple reports on same content are handled appropriately

**Sample Data**:
- Reported fact: "Controversial statement for testing"
- Reported comment: "Inappropriate comment for testing"
- Report reasons: "Spam", "Harassment", "Misinformation"

---

## TC_US15_Moderation_RemoveContent_UserNotification

**Objective**: Verify content removal and user notification

**Test Steps**:
1. Login as moderator
2. Review reported content in moderation dashboard
3. Select content for removal
4. Choose removal reason from predefined options
5. Confirm content removal
6. Verify content is immediately removed from public view
7. Verify content author receives notification of removal
8. Check notification includes removal reason and policy reference

**Assumptions**:
- Moderators can remove content with reason selection
- Content removal is immediate and comprehensive
- User notification system is implemented

**Success Criteria**:
- Content is immediately removed from all public views
- Content author receives timely notification
- Notification includes clear reason for removal
- Removal is logged for audit purposes
- Removed content is not accessible to regular users
- Notification provides policy guidance or appeal process

**Sample Data**:
- Content to remove: Reported inappropriate fact/comment
- Removal reasons: "Violates community guidelines", "Spam", "Harassment"

---

## TC_US15_Moderation_ActionLogging_AuditTrail

**Objective**: Verify all moderation actions are logged

**Test Steps**:
1. Login as moderator
2. Perform various moderation actions:
   - Remove a fact
   - Remove a comment
   - Dismiss a report as invalid
   - Suspend a user account
3. Access moderation audit log
4. Verify each action is logged with: timestamp, moderator ID, action type, target content/user, reason
5. Test log filtering and search functionality
6. Verify log entries are immutable and complete

**Assumptions**:
- Comprehensive audit logging is implemented
- Logs capture all relevant moderation activities
- Audit trail is accessible to moderators/admins

**Success Criteria**:
- All moderation actions are automatically logged
- Log entries include complete details (who, what, when, why)
- Logs are searchable and filterable
- Audit trail provides accountability and transparency
- Log entries cannot be modified or deleted
- Logs are accessible for review and compliance

**Sample Data**:
- Various moderation actions for logging
- Different moderators performing actions
- Different types of content and violations

---

## TC_US15_Moderation_RemoveAccount_ProperProcess

**Objective**: Verify moderator can remove user accounts

**Test Steps**:
1. Login as moderator
2. Navigate to user management section
3. Search for specific user account
4. Select account removal option
5. Verify confirmation dialog with account details
6. Provide reason for account removal
7. Confirm account removal
8. Verify user account is deactivated/removed
9. Verify user's content handling (removed/preserved)
10. Test removed user cannot login

**Assumptions**:
- Moderators have user account management capabilities
- Account removal requires confirmation and reason
- Account removal process is comprehensive

**Success Criteria**:
- Moderators can access user management tools
- Account removal requires confirmation with clear warnings
- Removal reason is required and logged
- User account is properly deactivated
- User cannot login after account removal
- Content handling follows defined policy (remove or preserve)
- Action is logged in audit trail

**Sample Data**:
- Test user account for removal
- Removal reasons: "Repeated violations", "Spam account", "Terms of service violation"

---

## TC_US16_Reporting_FactContent_SubmitReport

**Objective**: Verify reporting fact content with reason selection

**Test Steps**:
1. Login as regular user
2. Navigate to a fact posted by another user
3. Locate and click "Report" option
4. Verify report form appears with reason selection
5. Select report reason: "Misinformation"
6. Add optional additional details
7. Submit report
8. Verify confirmation message appears
9. Verify fact shows "reported" indicator for reporting user
10. Test reporting different facts with various reasons

**Assumptions**:
- Report functionality is available on all facts
- Predefined report reasons are provided
- Report submission is straightforward and user-friendly

**Success Criteria**:
- Report option is easily accessible on facts
- Report form provides clear reason categories
- Optional details field allows additional context
- Report submission provides confirmation
- Reported content is marked for reporting user
- Report is successfully queued for moderation review

**Sample Data**:
- Facts to report with different violation types
- Report reasons: "Misinformation", "Spam", "Harassment", "Inappropriate content"
- Additional details: Optional context for reports

---

## TC_US16_Reporting_CommentContent_SubmitReport

**Objective**: Verify reporting comment content

**Test Steps**:
1. Login as regular user
2. Navigate to comments section of any fact
3. Locate comment by another user
4. Click "Report" option on comment
5. Select appropriate report reason: "Harassment"
6. Add optional details about the violation
7. Submit comment report
8. Verify confirmation and visual indicator
9. Test reporting nested comments (replies)
10. Verify comment reports appear in moderation queue

**Assumptions**:
- Comment reporting follows same process as fact reporting
- Nested comments can also be reported
- Comment reports are handled by moderation system

**Success Criteria**:
- Report option available on all comments
- Comment reporting process matches fact reporting
- Nested comments can be reported independently
- Comment reports are properly queued for review
- Visual feedback confirms successful report submission
- Reports include sufficient context for moderation

**Sample Data**:
- Comments with various types of violations
- Nested comment threads for testing
- Report reasons specific to comment violations

---

## TC_US16_Reporting_Confirmation_UserFeedback

**Objective**: Verify user receives confirmation after reporting

**Test Steps**:
1. Login as regular user
2. Report a fact with reason "Spam"
3. Verify immediate confirmation message appears
4. Check confirmation message content and clarity
5. Report a comment with different reason
6. Verify consistent confirmation behavior
7. Test confirmation message dismissal
8. Verify no duplicate confirmations for same action

**Assumptions**:
- User feedback is provided immediately after reporting
- Confirmation messages are clear and informative
- Feedback system is consistent across content types

**Success Criteria**:
- Immediate confirmation appears after report submission
- Confirmation message is clear and reassuring
- Message explains next steps or expected timeline
- Confirmation behavior is consistent for facts and comments
- User understands their report was successfully submitted
- No technical errors in feedback system

**Sample Data**:
- Various content types for reporting
- Different report reasons to test consistency

---

## TC_US16_Reporting_DuplicateReport_PreventMultiple

**Objective**: Verify cannot report same content multiple times

**Test Steps**:
1. Login as regular user
2. Report a specific fact with reason "Misinformation"
3. Verify report is submitted successfully
4. Attempt to report the same fact again
5. Verify system prevents duplicate report
6. Check for appropriate message explaining limitation
7. Test with different report reasons on same content
8. Verify behavior is consistent for comments as well

**Assumptions**:
- System tracks which users have reported which content
- Duplicate reporting is prevented to avoid spam
- Clear messaging explains why duplicate reports are blocked

**Success Criteria**:
- Users cannot submit multiple reports for same content
- System provides clear message about existing report
- Prevention works for both facts and comments
- Different report reasons don't bypass duplicate prevention
- User understands why they cannot report again
- System maintains integrity of reporting process

**Sample Data**:
- Same fact/comment for multiple report attempts
- Different report reasons for testing

---

## TC_US16_Reporting_AnonymousToCreator_PrivacyProtection

**Objective**: Verify reports are anonymous to content creator

**Test Steps**:
1. Login as User A and create fact: "Test fact for reporting"
2. Login as User B and report User A's fact
3. Login back as User A (content creator)
4. Check if there's any indication of who reported the content
5. Verify no reporter identity is revealed in any UI
6. Test with moderator view to confirm reporter info is available to moderators only
7. Verify anonymity is maintained in all user-facing interfaces

**Assumptions**:
- Reporter identity is hidden from content creators
- Moderators can see reporter information for investigation
- Privacy protection is consistently enforced

**Success Criteria**:
- Content creators cannot see who reported their content
- No UI elements reveal reporter identity to creators
- Moderators can access reporter information when needed
- Anonymity encourages honest reporting without fear of retaliation
- Privacy protection is comprehensive and consistent
- System maintains trust in reporting process

**Sample Data**:
- User A (content creator): "creator@test.com"
- User B (reporter): "reporter@test.com"
- Moderator account for verification: "moderator@test.com"
