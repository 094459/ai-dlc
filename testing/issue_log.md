## Issues log

## Overview

This issue list outlines issues with the application that have been identified by user testing. When reviewing this list:

- ALWAYS run tests after making any code changes - if updates break tests, undo and try again
- AFTER completing each issue, ASK FOR A REVIEW and confirmation of the fix
- DO NOT PROCEED to the next task until the application is in a working state
- Fix ONLY ONE ISSUE at a time
- Do NOT delete/remove the existing planning docs - always APPEND/ADD

## Notes

- Virtual environment: venv
- Application code location: src/ directory
- Data model: data_model/complete_schema.sql
- PyTests location: src/tests/ directory
- End to End Tests with addition tests: testing/

### Issues


[x] - When you open a fact, when you click on the view history link it generates - jinja2.exceptions.TemplateNotFound: fact/history.html - **FIXED**: Created comprehensive fact/history.html template with timeline-based edit history display, showing previous versions, edit reasons, timestamps, and proper navigation. Also fixed UndefinedError by using fact.author instead of fact.user to match the database relationship structure.
[ ] - When you view a fact, the pull down menu (Edit Fact, View History, Delete Fact) is initially hidden behind the Fact Statitistic widget

### Fixed Issues


[x] - When voting on a claim, whilst the voting works successfully, an error message is displayed "An error occurred when submitting your vote" which you can see in the screen shot (images/issue-1.png). I can also see the following in the logs "[2025-08-22 17:22:33,098] ERROR in services: Vote blocking check error: 'AuditLog' object has no attribute 'action_type'"
[x] - Two failing unit tests in src/tests/ directory - **FIXED**: Updated test expectations to match correct authentication behavior (401 for JSON requests instead of 302 redirect)
[x] - When logged in as a user, when trying to comment on a fact, the screen generates a "Failed to create comment" message and I can see that the POST /comments/create generates an HTTP 500 error - **FIXED**: Updated comment creation route to properly handle authentication and fixed attribute references (nesting_level vs depth). Cleaned up all debugging code.
[x] - When you view a fact, there is an error about not be able to display comments - **FIXED**: Updated comment route to handle Comment model attributes correctly
[x] - Trying to edit a fact generates an error jinja2.exceptions.TemplateNotFound: fact/edit.html - **FIXED**: Created missing fact/edit.html template with full editing functionality
[x] - From the "/facts" page, the correct number of votes for fact or fake for a give claim is not correctly displayed. - **FIXED**: Updated facts list template to load actual vote counts via AJAX and enable voting functionality

## Playwright Manual Testing Results (2025-08-23)

### Testing Summary
Manual testing completed using Playwright MCP Server for user registration, login, homepage navigation, and profile page access.

### Issues Found
No critical HTTP 4xx or 5xx errors were encountered during testing. All functionality worked as expected.

### Minor Observations
- User registration attempted with playwright@test.com showed "Email already registered" message, indicating the user already existed in the system
- All network requests returned successful HTTP status codes (200 OK, 302 FOUND for redirects)
- Application navigation and user authentication flows work correctly
- Profile page displays user information and statistics properly

### Screenshots Captured
- homepage_initial.png - Initial homepage view
- registration_form_filled.png - Registration form with test data
- registration_email_exists_error.png - Email already registered error
- login_form_filled.png - Login form with credentials
- homepage_logged_in.png - Homepage after successful login
- profile_page.png - User profile page view

## Current Testing Session (2025-08-23 10:45 UTC)

### Issues Found

[x] - Community Guidelines link on registration page returns HTTP 500 error with "jinja2.exceptions.TemplateNotFound: main/guidelines.html" - missing template file (screenshot: guidelines-error.png) - **FIXED**: Created comprehensive main/guidelines.html template with community guidelines content
[x] - About link in footer returns HTTP 500 error with "jinja2.exceptions.TemplateNotFound: main/about.html" - missing template file (screenshot: about-error.png) - **FIXED**: Created comprehensive main/about.html template with about page content including mission, values, approach, impact, community info, and call-to-action sections  
[x] - Contact link in footer returns HTTP 500 error with "jinja2.exceptions.TemplateNotFound: main/contact.html" - missing template file (screenshot: contact-error.png) - **FIXED**: Created comprehensive main/contact.html template with contact form, FAQ section, response times, and multiple contact methods
[x] - Community Guidelines link in footer returns HTTP 500 error with "jinja2.exceptions.TemplateNotFound: main/guidelines.html" - same missing template affects multiple locations - **FIXED**: Same fix as above resolves this issue
[x] - Password input fields missing autocomplete attributes causing accessibility warnings in browser console - should add autocomplete="current-password" and autocomplete="new-password" attributes - **FIXED**: Added proper autocomplete attributes to all password fields in login.html (current-password) and register.html (new-password for both password and confirm password fields)