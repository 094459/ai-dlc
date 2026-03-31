# Testing Plan: Fact Checking Application

## Objective
Manually test the local fact checking application at http://127.0.0.1:5000 using Playwright to verify user registration, login, homepage navigation, and profile page functionality.

## Test Environment
- Application URL: http://127.0.0.1:5000
- Test User: playwright@test.com
- Test Password: 1Password!

## Testing Steps

### Pre-Testing Setup
- [x] Verify application is running at http://127.0.0.1:5000
- [x] Initialize Playwright browser session
- [x] Create images/ directory for screenshots if it doesn't exist


### User Registration Testing
- [x] Navigate to the application homepage
- [x] Locate and access user registration functionality
- [x] Register new user with email: playwright@test.com and password: 1Password!
- [x] If there are any links on the registration page to supporting resources, validate they work
- [x] Verify successful registration (check for success messages, redirects, or confirmation)
- [x] Take screenshot of successful registration confirmation
- [x] Document any HTTP error codes (4xx/5xx) encountered during registration

### User Login Testing
- [x] Navigate to login page/functionality
- [x] Login using registered credentials (playwright@test.com / 1Password!)
- [x] Verify successful login (check for authentication success indicators)
- [x] Take screenshot of successful login state
- [x] Document any HTTP error codes (4xx/5xx) encountered during login

### Homepage Navigation Testing (Post-Login)
- [x] Verify user is properly authenticated and on homepage
- [x] Test all navigation elements and links on homepage
- [x] Verify page loads completely without errors
- [x] Check for any broken functionality or UI issues
- [x] Take screenshot of homepage in logged-in state
- [x] Document any HTTP error codes (4xx/5xx) encountered on homepage

### Profile Page Testing
- [x] Navigate to user profile page
- [x] Verify profile page loads correctly
- [x] Check that user information is displayed properly
- [x] Test any interactive elements on profile page
- [x] Take screenshot of profile page
- [x] Document any HTTP error codes (4xx/5xx) encountered on profile page

### Reporting and Documentation
- [x] Generate comprehensive playwright_report.md with all findings
- [x] Update issue_log.md with any issues found (append only)
- [x] Organize all screenshots in images/ directory
- [x] Mark all completed steps in this plan

### Homepage links Testing
- [x] Navigate to the application homepage and validate that ALL links work

## Success Criteria
- User registration completes successfully
- User login works with registered credentials
- Homepage loads and functions properly when logged in
- Profile page is accessible and displays correctly
- No HTTP 4xx or 5xx errors encountered
- All screenshots captured for documentation

## Risk Areas Requiring Clarification
- [ ] **CLARIFICATION NEEDED**: Should I test logout functionality as well?
- [ ] **CLARIFICATION NEEDED**: Are there specific homepage features/sections I should focus on testing?
- [ ] **CLARIFICATION NEEDED**: Should I test profile editing functionality or just viewing?
- [ ] **CLARIFICATION NEEDED**: If the user already exists, should I try to delete it first or use a different email?

## Notes
- All issues will be documented in testing/issue_log.md
- Screenshots will be stored in images/ directory
- Report will be generated in testing/playwright_report.md
- Existing files will not be overwritten - append only approach
