# Phase 5: System Administration - Detailed Test Cases

## TC_US17_AdminDashboard_AccessControl_AdminOnly

**Objective**: Verify only administrators can access admin dashboard

**Test Steps**:
1. Login as regular user
2. Attempt to access admin dashboard URL directly
3. Verify access is denied with appropriate error message
4. Login as moderator (non-admin)
5. Attempt to access admin dashboard
6. Verify moderator access is denied or limited
7. Login as designated administrator
8. Navigate to admin dashboard
9. Verify full admin dashboard loads successfully
10. Test with suspended admin account (if applicable)

**Assumptions**:
- Administrator role is distinct from moderator and user roles
- Access control is enforced at multiple levels
- Admin dashboard has dedicated access points

**Success Criteria**:
- Regular users cannot access admin dashboard
- Moderators have limited or no access to admin functions
- Only administrators can access full admin dashboard
- Appropriate error messages for unauthorized access
- Access control is consistently enforced
- Clear role-based permission system

**Sample Data**:
- Regular user: "user@test.com"
- Moderator: "moderator@test.com"
- Administrator: "admin@test.com"

---

## TC_US17_AdminDashboard_SystemMetrics_ProperDisplay

**Objective**: Verify system metrics are displayed correctly

**Test Steps**:
1. Login as administrator
2. Access admin dashboard
3. Verify system metrics section is visible
4. Check display of key metrics:
   - Total registered users
   - Active users (daily/weekly/monthly)
   - Total facts submitted
   - Total comments posted
   - Total votes cast
   - Reports pending/resolved
   - System uptime/performance
5. Verify metrics are current and accurate
6. Test metric refresh/update functionality
7. Verify metrics are properly formatted and readable

**Assumptions**:
- System metrics are calculated and stored
- Metrics provide meaningful insights into system health
- Dashboard displays real-time or near-real-time data

**Success Criteria**:
- All key system metrics are displayed
- Metrics are accurate and up-to-date
- Display format is clear and professional
- Metrics provide actionable insights
- Data refreshes appropriately
- Performance metrics indicate system health

**Sample Data**:
- Expected metrics ranges for validation
- Historical data for trend verification

---

## TC_US17_AdminDashboard_UserManagement_SuspendAccount

**Objective**: Verify admin can suspend user accounts

**Test Steps**:
1. Login as administrator
2. Navigate to user management section
3. Search for specific user account
4. Select user account to suspend
5. Choose "Suspend Account" option
6. Verify confirmation dialog with suspension details
7. Select suspension duration (temporary/permanent)
8. Provide reason for suspension
9. Confirm suspension action
10. Verify user account is suspended
11. Test suspended user cannot login
12. Verify suspended user's content remains visible but marked

**Assumptions**:
- Admin has comprehensive user management capabilities
- Account suspension is reversible action
- Suspension affects login but may preserve content

**Success Criteria**:
- Admins can access user management tools
- User search and selection works correctly
- Suspension requires confirmation and reason
- Suspension duration options are available
- Suspended users cannot login
- Suspension is logged in audit trail
- Content handling follows defined policy
- Suspension can be reversed if needed

**Sample Data**:
- Test user account: "testuser@example.com"
- Suspension reasons: "Policy violation", "Spam activity", "Temporary investigation"
- Suspension durations: "24 hours", "7 days", "30 days", "Indefinite"

---

## TC_US17_AdminDashboard_UserManagement_DeleteAccount

**Objective**: Verify admin can delete user accounts with confirmation

**Test Steps**:
1. Login as administrator
2. Navigate to user management section
3. Search for specific user account
4. Select user account for deletion
5. Choose "Delete Account" option
6. Verify strong confirmation dialog with warnings
7. Verify dialog shows impact (content removal, irreversible action)
8. Provide mandatory reason for deletion
9. Type confirmation phrase (e.g., "DELETE ACCOUNT")
10. Confirm deletion action
11. Verify account is permanently deleted
12. Verify user cannot login
13. Verify content handling (removed or anonymized)

**Assumptions**:
- Account deletion is permanent and irreversible
- Strong confirmation prevents accidental deletions
- Content handling policy is clearly defined

**Success Criteria**:
- Account deletion requires multiple confirmation steps
- Strong warnings about permanent nature of action
- Mandatory reason and confirmation phrase required
- Account is completely removed from system
- User cannot login after deletion
- Content is handled according to policy
- Action is comprehensively logged
- No recovery possible after deletion

**Sample Data**:
- Test account for deletion: "deletetest@example.com"
- Deletion reasons: "Legal request", "Severe policy violation", "User request"
- Confirmation phrase: "DELETE ACCOUNT"

---

## TC_US17_AdminDashboard_ActivityLogs_ComprehensiveView

**Objective**: Verify admin can view system activity logs

**Test Steps**:
1. Login as administrator
2. Navigate to activity logs section
3. Verify comprehensive log display showing:
   - User registrations and logins
   - Content creation (facts, comments)
   - Voting activities
   - Moderation actions
   - Administrative actions
   - System events
4. Test log filtering by:
   - Date range
   - Activity type
   - User ID
   - Severity level
5. Test log search functionality
6. Verify log export capabilities
7. Test log pagination for large datasets

**Assumptions**:
- Comprehensive activity logging is implemented
- Logs provide detailed audit trail
- Log viewing tools are efficient and user-friendly

**Success Criteria**:
- All system activities are logged and visible
- Logs include sufficient detail for audit purposes
- Filtering and search work effectively
- Log display is organized and readable
- Export functionality works for compliance
- Performance is acceptable with large log volumes
- Logs provide accountability and transparency

**Sample Data**:
- Various system activities across different time periods
- Different user types and activity levels
- Mix of normal and exceptional events

---

## TC_US17_AdminDashboard_AdditionalAuth_SecurityLayer

**Objective**: Verify additional authentication for admin access

**Test Steps**:
1. Login with admin credentials
2. Attempt to access sensitive admin functions
3. Verify additional authentication prompt appears
4. Test various additional auth methods:
   - Password re-entry
   - Two-factor authentication (if implemented)
   - Security questions
   - Time-based restrictions
5. Test with correct additional authentication
6. Verify access is granted to sensitive functions
7. Test with incorrect additional authentication
8. Verify access is denied appropriately
9. Test session timeout for additional auth

**Assumptions**:
- Additional authentication layer is implemented for admin functions
- Security measures are appropriate for admin privilege level
- Authentication methods are secure and user-friendly

**Success Criteria**:
- Additional authentication is required for sensitive admin functions
- Authentication methods work correctly
- Failed authentication blocks access appropriately
- Successful authentication grants appropriate access
- Session management handles additional auth properly
- Security measures are proportionate to risk level
- User experience remains manageable despite security

**Sample Data**:
- Admin credentials for testing
- Additional authentication factors (passwords, codes, etc.)
- Various sensitive admin functions for testing

---

## Integration Test Cases for Administration

### TC_US17_INT_AdminWorkflow_CompleteUserManagement

**Objective**: Verify complete admin workflow for user management

**Test Steps**:
1. Login as administrator with additional authentication
2. Review system metrics to identify issues
3. Access activity logs to investigate user behavior
4. Search for problematic user account
5. Review user's content and activity history
6. Suspend user account with appropriate reason
7. Monitor user's attempts to access system
8. Review impact on system metrics
9. If necessary, escalate to account deletion
10. Verify all actions are properly logged

**Assumptions**:
- Complete admin workflow integrates all components
- Admin tools work together seamlessly
- Audit trail captures entire process

**Success Criteria**:
- All admin tools integrate smoothly
- Workflow is efficient and logical
- All actions are properly logged and traceable
- System metrics reflect admin actions
- User management actions are effective
- Audit trail provides complete picture

---

### TC_US17_INT_AdminSecurity_AccessControlValidation

**Objective**: Verify comprehensive admin security measures

**Test Steps**:
1. Test admin access from different IP addresses
2. Verify session timeout enforcement
3. Test concurrent admin sessions
4. Verify admin action logging includes security context
5. Test admin privilege escalation prevention
6. Verify admin account lockout after failed attempts
7. Test admin password requirements and changes
8. Verify admin activity monitoring and alerts

**Assumptions**:
- Comprehensive security measures protect admin functions
- Security monitoring is active and effective
- Admin accounts have enhanced protection

**Success Criteria**:
- Admin access is properly secured and monitored
- Security measures prevent unauthorized access
- Admin activities are comprehensively logged
- Security alerts work for suspicious admin activity
- Admin accounts cannot be compromised easily
- Security measures don't impede legitimate admin work
