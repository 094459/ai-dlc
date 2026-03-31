# Phase 1: Core User Management - Detailed Test Cases

## TC_US01_Registration_ValidEmail_Success

**Objective**: Verify successful user registration with valid email

**Test Steps**:
1. Navigate to the registration page
2. Enter a valid email address (e.g., "testuser@example.com")
3. Click the submit/register button
4. Verify confirmation message is displayed
5. Verify user can access the application

**Assumptions**:
- Registration page is accessible
- Email validation follows standard RFC 5322 format
- No additional fields required beyond email for registration

**Success Criteria**:
- User receives confirmation message
- User is redirected to main application or login page
- User account is created in the system
- User can subsequently log in with the registered email

**Sample Data**:
- Valid emails: "user1@test.com", "jane.doe@company.org", "test+tag@domain.co.uk"

---

## TC_US01_Registration_InvalidEmailFormat_ErrorMessage

**Objective**: Verify error handling for invalid email format

**Test Steps**:
1. Navigate to the registration page
2. Enter an invalid email format
3. Click the submit/register button
4. Verify appropriate error message is displayed
5. Verify registration is not completed

**Assumptions**:
- Client-side validation is implemented
- Error messages are user-friendly and descriptive

**Success Criteria**:
- Clear error message indicating invalid email format
- Registration form remains on screen
- No user account is created
- User can correct the email and retry

**Sample Data**:
- Invalid emails: "plainaddress", "@missingdomain.com", "missing@.com", "spaces in@email.com", "toolong@verylongdomainnamethatexceedsmaximumlengthallowed.com"

---

## TC_US01_Registration_DuplicateEmail_ErrorMessage

**Objective**: Verify error handling for existing email

**Test Steps**:
1. Ensure a user account already exists with email "existing@test.com"
2. Navigate to the registration page
3. Enter the existing email address "existing@test.com"
4. Click the submit/register button
5. Verify error message indicating email already exists
6. Verify registration is not completed

**Assumptions**:
- System maintains unique email constraint
- Existing user data is available for testing

**Success Criteria**:
- Error message clearly states email is already registered
- No duplicate account is created
- User is given option to login instead or use different email

**Sample Data**:
- Pre-existing email: "existing@test.com"

---

## TC_US01_Registration_EmptyEmail_ValidationError

**Objective**: Verify validation for empty email field

**Test Steps**:
1. Navigate to the registration page
2. Leave email field empty
3. Click the submit/register button
4. Verify validation error message is displayed
5. Verify registration is not completed

**Assumptions**:
- Email field is required for registration
- Form validation prevents submission with empty required fields

**Success Criteria**:
- Error message indicates email is required
- Form submission is prevented
- User remains on registration page
- Email field is highlighted or marked as invalid

**Sample Data**:
- Empty string or null value for email field

---

## TC_US02_Login_RegisteredEmail_Success

**Objective**: Verify successful login with registered email

**Test Steps**:
1. Ensure user account exists with email "testuser@example.com"
2. Navigate to the login page
3. Enter the registered email address
4. Click the login/submit button
5. Verify successful login and redirection to main application

**Assumptions**:
- User account exists and is active
- Login page is accessible
- Session management is implemented

**Success Criteria**:
- User is successfully authenticated
- User is redirected to main application dashboard/homepage
- User session is established
- User can access protected features

**Sample Data**:
- Registered email: "testuser@example.com"

---

## TC_US02_Login_UnregisteredEmail_ErrorMessage

**Objective**: Verify error handling for unregistered email

**Test Steps**:
1. Navigate to the login page
2. Enter an email that doesn't exist in the system "nonexistent@test.com"
3. Click the login/submit button
4. Verify error message indicating account doesn't exist
5. Verify login is not successful

**Assumptions**:
- System checks email existence before authentication
- Error messages don't reveal system information

**Success Criteria**:
- Clear error message stating account doesn't exist
- User remains on login page
- No session is created
- Option to register is provided

**Sample Data**:
- Unregistered email: "nonexistent@test.com"

---

## TC_US02_Login_SessionPersistence_MaintainLogin

**Objective**: Verify session persistence across browser sessions

**Test Steps**:
1. Login with valid credentials "testuser@example.com"
2. Verify successful login and access to application
3. Close the browser completely
4. Reopen browser and navigate to the application
5. Verify user is still logged in (within reasonable session duration)

**Assumptions**:
- Session management uses cookies or similar persistence mechanism
- Session timeout is configured for reasonable duration (e.g., 24 hours)
- Browser supports session persistence

**Success Criteria**:
- User remains logged in after browser restart
- User can access protected features without re-login
- Session persists for configured duration
- User identity is maintained

**Sample Data**:
- Valid user email: "testuser@example.com"

---

## TC_US02_Login_EmptyEmail_ValidationError

**Objective**: Verify validation for empty login field

**Test Steps**:
1. Navigate to the login page
2. Leave email field empty
3. Click the login/submit button
4. Verify validation error message is displayed
5. Verify login is not attempted

**Assumptions**:
- Email field is required for login
- Client-side validation prevents empty submissions

**Success Criteria**:
- Error message indicates email is required
- Login attempt is prevented
- User remains on login page
- Email field is highlighted as invalid

**Sample Data**:
- Empty email field

---

## TC_US03_Profile_CreateComplete_Success

**Objective**: Verify complete profile creation with name, bio, and photo

**Test Steps**:
1. Login as registered user
2. Navigate to profile setup/creation page
3. Enter name: "John Doe"
4. Enter biography: "Software developer with 5 years experience in web development"
5. Upload a valid profile photo (JPG/PNG format, reasonable size)
6. Click save/submit button
7. Verify profile is saved successfully
8. Navigate to profile view and verify all information is displayed

**Assumptions**:
- User is logged in and can access profile creation
- Image upload functionality is implemented
- Profile data is stored persistently

**Success Criteria**:
- Profile is saved with all provided information
- Success confirmation is displayed
- Profile photo is properly sized and displayed
- All profile information is visible to other users
- Profile is accessible from user navigation

**Sample Data**:
- Name: "John Doe"
- Biography: "Software developer with 5 years experience in web development"
- Profile photo: Valid image file (test-profile.jpg, 200KB, 300x300px)

---

## TC_US03_Profile_CreateMinimal_Success

**Objective**: Verify profile creation with only required name field

**Test Steps**:
1. Login as registered user
2. Navigate to profile setup/creation page
3. Enter name: "Jane Smith"
4. Leave biography field empty
5. Do not upload profile photo
6. Click save/submit button
7. Verify profile is saved successfully
8. Navigate to profile view and verify name is displayed

**Assumptions**:
- Name is the only required field for profile creation
- Biography and photo are optional fields
- Default values are used for optional fields

**Success Criteria**:
- Profile is created with name only
- Success confirmation is displayed
- Default placeholder is shown for missing photo
- Biography section is empty or shows default text
- Profile is functional and accessible

**Sample Data**:
- Name: "Jane Smith"
- Biography: (empty)
- Profile photo: (none)

---

## TC_US03_Profile_PhotoUpload_ProperSizing

**Objective**: Verify profile photo upload and proper sizing

**Test Steps**:
1. Login as registered user
2. Navigate to profile setup/creation page
3. Enter required name field
4. Upload a large profile photo (e.g., 2MB, 2000x2000px)
5. Click save/submit button
6. Verify photo is uploaded and automatically resized
7. Check that photo displays properly in profile view
8. Verify photo maintains aspect ratio

**Assumptions**:
- System automatically resizes uploaded images
- Supported formats include JPG, PNG, GIF
- Maximum display size is defined (e.g., 200x200px)

**Success Criteria**:
- Large image is accepted and processed
- Image is resized to appropriate dimensions
- Aspect ratio is maintained or cropped appropriately
- Image quality is acceptable after resizing
- Image loads quickly in profile view

**Sample Data**:
- Large image file: test-large-photo.jpg (2MB, 2000x2000px)
- Expected output: Resized to 200x200px or similar

---

## TC_US03_Profile_BiographyLimit_CharacterWarning

**Objective**: Verify character limit warning for biography

**Test Steps**:
1. Login as registered user
2. Navigate to profile setup/creation page
3. Enter required name field
4. Begin typing in biography field
5. Type text approaching character limit
6. Verify character count is displayed
7. Attempt to exceed character limit
8. Verify warning message or prevention of additional characters

**Assumptions**:
- Biography has defined character limit (assume 500 characters based on user story pattern)
- Real-time character counting is implemented
- User is warned before reaching limit

**Success Criteria**:
- Character count is displayed in real-time
- Warning appears when approaching limit
- User cannot exceed character limit
- Clear indication of remaining characters
- Graceful handling of limit enforcement

**Sample Data**:
- Long biography text: 500+ character string for testing limit

---

## TC_US03_Profile_InvalidPhotoFormat_ErrorMessage

**Objective**: Verify error handling for unsupported image formats

**Test Steps**:
1. Login as registered user
2. Navigate to profile setup/creation page
3. Enter required name field
4. Attempt to upload unsupported file format (e.g., .txt, .pdf, .exe)
5. Verify error message is displayed
6. Verify file is not uploaded
7. Try with supported format to confirm functionality works

**Assumptions**:
- Only specific image formats are supported (JPG, PNG, GIF)
- File type validation is implemented
- Clear error messages are provided

**Success Criteria**:
- Error message clearly states unsupported format
- File upload is rejected
- List of supported formats is provided
- User can retry with correct format
- No system errors occur

**Sample Data**:
- Invalid files: document.txt, presentation.pdf, program.exe
- Valid files: image.jpg, photo.png, animation.gif

---

## TC_US04_ViewProfile_CompleteProfile_DisplayAll

**Objective**: Verify viewing complete user profile with all elements

**Test Steps**:
1. Ensure a user profile exists with complete information (name, bio, photo, submitted facts)
2. Login as different user or browse as guest
3. Navigate to the complete user's profile
4. Verify all profile elements are displayed correctly
5. Check profile photo, name, biography, and facts list
6. Verify layout and formatting are proper

**Assumptions**:
- User profiles are publicly viewable
- Profile page layout is implemented
- Facts are linked to user profiles

**Success Criteria**:
- All profile information is visible and properly formatted
- Profile photo displays correctly
- Name and biography are readable
- List of submitted facts is shown
- Navigation to profile works from various entry points
- Page loads without errors

**Sample Data**:
- Complete user profile: "John Doe" with photo, bio, and 3 submitted facts

---

## TC_US04_ViewProfile_NoPhoto_DefaultPlaceholder

**Objective**: Verify default placeholder when no profile photo

**Test Steps**:
1. Ensure a user profile exists without uploaded photo
2. Navigate to that user's profile page
3. Verify default placeholder image is displayed
4. Check that placeholder is appropriate and professional
5. Verify other profile elements display correctly

**Assumptions**:
- Default placeholder image is configured
- Placeholder maintains consistent sizing with uploaded photos
- Profile functionality works without photo

**Success Criteria**:
- Default placeholder image is displayed
- Placeholder is visually appropriate
- Profile layout remains consistent
- No broken image links or errors
- Other profile information displays normally

**Sample Data**:
- User profile without photo: "Jane Smith" with name and bio only

---

## TC_US04_ViewProfile_FactsList_ChronologicalOrder

**Objective**: Verify user's facts displayed in chronological order

**Test Steps**:
1. Ensure a user has submitted multiple facts at different times
2. Navigate to that user's profile page
3. Locate the facts section
4. Verify facts are listed in chronological order (newest first or oldest first)
5. Check timestamps or submission dates if displayed

**Assumptions**:
- Facts are timestamped when submitted
- Profile page includes facts section
- Chronological ordering is implemented

**Success Criteria**:
- Facts are displayed in consistent chronological order
- Most recent facts appear first (or clearly defined order)
- All user's facts are included in the list
- Facts display correctly with proper formatting
- Timestamps are accurate if shown

**Sample Data**:
- User with multiple facts: 5 facts submitted over different days/times

---

## TC_US04_ViewProfile_Navigation_ConsistentAccess

**Objective**: Verify consistent profile access from various pages

**Test Steps**:
1. Navigate to different pages in the application (home, fact details, comments)
2. From each page, click on a user's name or profile link
3. Verify profile page opens correctly each time
4. Check that profile URL is consistent
5. Verify back navigation works properly
6. Test profile access from different contexts (fact author, commenter, etc.)

**Assumptions**:
- User names/avatars are clickable links throughout the application
- Profile URLs are consistent and bookmarkable
- Navigation is implemented across all pages

**Success Criteria**:
- Profile links work from all application pages
- Profile page loads consistently regardless of entry point
- URL structure is consistent
- Back navigation returns to previous page
- No broken links or navigation errors
- User experience is smooth and intuitive

**Sample Data**:
- Multiple users with profiles accessible from various contexts
- Test navigation from: home page, fact details, comment sections, search results
