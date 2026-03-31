# Phase 2: Fact Management - Detailed Test Cases

## TC_US05_FactSubmission_ValidContent_Success

**Objective**: Verify successful fact submission within character limit

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page/form
3. Enter valid fact content (e.g., "The Earth orbits around the Sun once every 365.25 days")
4. Verify character count shows within 500 character limit
5. Click submit button
6. Verify success confirmation message
7. Navigate to main facts feed and verify fact appears
8. Verify fact shows correct author and timestamp

**Assumptions**:
- User is authenticated and can access fact submission
- Fact submission form is accessible
- Facts are immediately visible after submission

**Success Criteria**:
- Fact is successfully submitted and saved
- Success confirmation is displayed
- Fact appears in public feed immediately
- Fact shows correct author attribution
- Timestamp is accurate
- Character count validation works correctly

**Sample Data**:
- Valid fact: "The Earth orbits around the Sun once every 365.25 days"
- Character count: 62 characters (well within 500 limit)

---

## TC_US05_FactSubmission_CharacterLimit_PreventSubmission

**Objective**: Verify prevention of submission over 500 characters

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page/form
3. Enter text that exceeds 500 characters
4. Verify character count shows over limit (e.g., 520/500)
5. Attempt to click submit button
6. Verify submission is prevented
7. Verify appropriate warning message is displayed
8. Reduce text to under 500 characters and verify submission works

**Assumptions**:
- Character limit is enforced at 500 characters
- Real-time character counting is implemented
- Client-side validation prevents over-limit submissions

**Success Criteria**:
- Character count accurately reflects input length
- Warning appears when limit is exceeded
- Submit button is disabled or submission is blocked
- Clear error message explains the limit
- User can edit and successfully submit within limit

**Sample Data**:
- Long text: 520-character string that exceeds limit
- Valid text: Edited version under 500 characters

---

## TC_US05_FactSubmission_EmptyContent_ValidationError

**Objective**: Verify validation for empty fact content

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page/form
3. Leave fact content field empty
4. Attempt to click submit button
5. Verify validation error message appears
6. Verify submission is prevented
7. Enter valid content and verify submission works

**Assumptions**:
- Fact content is required field
- Client-side validation prevents empty submissions
- Error messages are user-friendly

**Success Criteria**:
- Error message indicates fact content is required
- Submission is prevented when field is empty
- Error message is clear and helpful
- Field is highlighted as invalid
- User can correct and successfully submit

**Sample Data**:
- Empty content field
- Valid content for successful submission test

---

## TC_US05_FactSubmission_CharacterCount_RealTimeDisplay

**Objective**: Verify real-time character count display

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page/form
3. Begin typing in fact content field
4. Verify character count updates in real-time as user types
5. Test with various lengths: short (50 chars), medium (250 chars), near limit (490 chars)
6. Verify count accuracy at different lengths
7. Test backspace/delete operations update count correctly

**Assumptions**:
- Character counter is visible and updates dynamically
- Counter includes all characters including spaces and punctuation
- Counter updates immediately on input changes

**Success Criteria**:
- Character count displays and updates in real-time
- Count is accurate for all input lengths
- Counter updates on both typing and deletion
- Counter is clearly visible to user
- Counter shows format like "250/500" or similar

**Sample Data**:
- Short text: "Climate change is real" (21 characters)
- Medium text: 250-character fact about science
- Long text: 490-character fact approaching limit

---

## TC_US05_FactSubmission_MultipleSubmissions_AllVisible

**Objective**: Verify multiple facts can be submitted by same user

**Test Steps**:
1. Login as registered user
2. Submit first fact: "Water boils at 100°C at sea level"
3. Verify first fact appears in feed
4. Submit second fact: "The speed of light is 299,792,458 meters per second"
5. Verify second fact appears in feed
6. Submit third fact: "DNA stands for Deoxyribonucleic Acid"
7. Verify all three facts are visible in the feed
8. Check user's profile to ensure all facts are listed

**Assumptions**:
- Users can submit unlimited facts (or reasonable limit)
- All facts from same user are preserved and displayed
- Facts maintain chronological order

**Success Criteria**:
- All submitted facts appear in public feed
- Facts are properly attributed to correct user
- Facts maintain submission order
- User profile shows all submitted facts
- No facts are lost or overwritten

**Sample Data**:
- Fact 1: "Water boils at 100°C at sea level"
- Fact 2: "The speed of light is 299,792,458 meters per second"
- Fact 3: "DNA stands for Deoxyribonucleic Acid"

---

## TC_US06_Resources_ValidURL_Success

**Objective**: Verify adding valid URL resource to fact

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page
3. Enter fact content: "NASA has confirmed water on Mars"
4. Add URL resource: "https://www.nasa.gov/news/mars-water-discovery"
5. Verify URL format validation passes
6. Submit the fact with resource
7. Verify fact displays with clickable URL link
8. Click the URL link and verify it opens correctly

**Assumptions**:
- URL resource field is available during fact creation
- URL validation follows standard format (http/https)
- URLs are displayed as clickable links

**Success Criteria**:
- Valid URL is accepted and saved with fact
- URL displays as clickable link in fact view
- Link opens in new tab/window when clicked
- URL is properly formatted and accessible
- Fact submission succeeds with resource attached

**Sample Data**:
- Valid URLs: "https://www.nasa.gov/news", "http://example.com/article", "https://subdomain.site.org/path"

---

## TC_US06_Resources_InvalidURL_ErrorMessage

**Objective**: Verify error handling for invalid URL format

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page
3. Enter fact content
4. Attempt to add invalid URL formats
5. Verify error messages for each invalid format
6. Verify fact submission is prevented or URL is rejected
7. Test with valid URL to confirm functionality works

**Assumptions**:
- URL validation is implemented
- Error messages are specific and helpful
- Invalid URLs don't break the submission process

**Success Criteria**:
- Invalid URLs are rejected with clear error messages
- Error messages explain what constitutes valid URL
- Fact submission continues to work with valid URLs
- User can correct URL and successfully submit
- No system errors occur with invalid input

**Sample Data**:
- Invalid URLs: "not-a-url", "ftp://oldprotocol.com", "javascript:alert('xss')", "www.missing-protocol.com"
- Valid URL for verification: "https://www.example.com"

---

## TC_US06_Resources_ImageUpload_ProperStorage

**Objective**: Verify image resource upload and storage

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page
3. Enter fact content: "This chart shows climate data trends"
4. Upload image resource (JPG/PNG file, reasonable size)
5. Verify image upload progress/confirmation
6. Submit fact with image resource
7. Verify fact displays with embedded or linked image
8. Verify image loads correctly and is properly sized

**Assumptions**:
- Image upload functionality is implemented
- Supported formats include JPG, PNG, GIF
- Images are resized/optimized for web display

**Success Criteria**:
- Image uploads successfully without errors
- Image is properly stored and associated with fact
- Image displays correctly in fact view
- Image maintains reasonable quality and size
- Image loading doesn't significantly impact page performance

**Sample Data**:
- Test images: chart.jpg (500KB), diagram.png (200KB), infographic.gif (1MB)

---

## TC_US06_Resources_MultipleResources_AllDisplayed

**Objective**: Verify multiple resources can be added to single fact

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page
3. Enter fact content: "Climate change evidence from multiple sources"
4. Add first resource: URL "https://climate.nasa.gov/evidence"
5. Add second resource: Upload image file "temperature-chart.jpg"
6. Add third resource: URL "https://ipcc.ch/reports"
7. Submit fact with all resources
8. Verify all resources are displayed with the fact
9. Test that all resources are accessible/functional

**Assumptions**:
- Multiple resources can be attached to single fact
- System supports mix of URLs and images
- All resources are preserved and displayed

**Success Criteria**:
- All added resources are saved with the fact
- Resources display in organized, readable format
- URLs are clickable and images are viewable
- Resources don't interfere with each other
- Fact remains readable with multiple resources

**Sample Data**:
- URL 1: "https://climate.nasa.gov/evidence"
- Image: temperature-chart.jpg
- URL 2: "https://ipcc.ch/reports"

---

## TC_US06_Resources_ImageSizeLimit_ValidationError

**Objective**: Verify image size limit validation

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page
3. Enter fact content
4. Attempt to upload very large image file (e.g., 10MB+)
5. Verify size limit error message appears
6. Verify upload is rejected
7. Try with acceptable size image to confirm functionality
8. Test edge cases around the size limit

**Assumptions**:
- Image size limits are defined and enforced
- Error messages clearly state size limits
- Size validation occurs before upload completion

**Success Criteria**:
- Large images are rejected with clear error message
- Error message states maximum allowed file size
- Upload process handles rejection gracefully
- Acceptable size images upload successfully
- No system crashes or errors with large files

**Sample Data**:
- Large image: huge-file.jpg (15MB)
- Acceptable image: normal-chart.png (500KB)
- Edge case: file at exact size limit

---

## TC_US07_Hashtags_ValidFormat_ClickableDisplay

**Objective**: Verify hashtags are properly formatted and clickable

**Test Steps**:
1. Login as registered user
2. Navigate to fact submission page
3. Enter fact with hashtags: "Climate change affects weather patterns #climate #science #environment"
4. Submit the fact
5. Verify hashtags are visually distinct (colored, styled)
6. Verify hashtags are clickable links
7. Click each hashtag to verify navigation works
8. Verify hashtag format follows standard (#word)

**Assumptions**:
- Hashtags are automatically detected and formatted
- Hashtags use # symbol followed by word/phrase
- Hashtags are styled differently from regular text

**Success Criteria**:
- Hashtags are automatically detected in fact text
- Hashtags display with distinct visual styling
- Hashtags are clickable and navigate to filtered views
- Hashtag format is consistent and recognizable
- Multiple hashtags in single fact all work correctly

**Sample Data**:
- Fact with hashtags: "Climate change affects weather patterns #climate #science #environment"
- Expected hashtags: #climate, #science, #environment

---

## TC_US07_Hashtags_ClickNavigation_FilteredView

**Objective**: Verify clicking hashtag shows filtered fact view

**Test Steps**:
1. Ensure multiple facts exist with same hashtag #science
2. Navigate to main facts feed
3. Click on #science hashtag from any fact
4. Verify navigation to filtered view showing only #science facts
5. Verify page title/header indicates filtered view
6. Verify all displayed facts contain #science hashtag
7. Test navigation back to main feed
8. Test with different hashtags to verify filtering works

**Assumptions**:
- Hashtag filtering functionality is implemented
- Filtered views show only relevant facts
- Navigation between views is smooth

**Success Criteria**:
- Clicking hashtag navigates to filtered view
- Filtered view shows only facts with that hashtag
- Page clearly indicates current filter
- All facts in filtered view contain the hashtag
- User can navigate back to main feed
- Filter works for all hashtags

**Sample Data**:
- Multiple facts with #science hashtag
- Facts with other hashtags (#climate, #technology)
- Mixed facts for comprehensive testing

---

## TC_US07_Hashtags_MultipleHashtags_AllProcessed

**Objective**: Verify multiple hashtags in single fact

**Test Steps**:
1. Login as registered user
2. Submit fact with multiple hashtags: "Renewable energy reduces carbon emissions #energy #climate #sustainability #green"
3. Verify all hashtags are detected and formatted
4. Click each hashtag individually
5. Verify each leads to appropriate filtered view
6. Verify fact appears in all relevant hashtag filters
7. Test hashtags at different positions (beginning, middle, end)

**Assumptions**:
- Multiple hashtags per fact are supported
- Each hashtag functions independently
- Hashtags can appear anywhere in fact text

**Success Criteria**:
- All hashtags in fact are detected and formatted
- Each hashtag is individually clickable
- Fact appears in filtered views for all its hashtags
- Hashtag processing works regardless of position
- No limit on reasonable number of hashtags

**Sample Data**:
- Multi-hashtag fact: "Renewable energy reduces carbon emissions #energy #climate #sustainability #green"
- Expected hashtags: #energy, #climate, #sustainability, #green

---

## TC_US07_Hashtags_CaseInsensitive_SearchFunctionality

**Objective**: Verify case-insensitive hashtag searching

**Test Steps**:
1. Submit facts with hashtags in different cases: "#Science", "#SCIENCE", "#science"
2. Click on any version of the science hashtag
3. Verify filtered view shows facts with all case variations
4. Test search functionality (if available) with different cases
5. Verify hashtag normalization treats all cases as same hashtag
6. Test with mixed case hashtags like "#ClimateChange"

**Assumptions**:
- Hashtag matching is case-insensitive
- Different cases of same hashtag are treated as identical
- Search and filtering respect case-insensitivity

**Success Criteria**:
- All case variations of hashtag are treated as same tag
- Filtered views include facts with any case variation
- Hashtag display may normalize to consistent case
- Search functionality is case-insensitive
- User experience is consistent regardless of case used

**Sample Data**:
- Facts with: "#Science", "#SCIENCE", "#science", "#ClimateChange", "#climatechange"

---

## TC_US07_Hashtags_SpecialCharacters_ValidationHandling

**Objective**: Verify handling of special characters in hashtags

**Test Steps**:
1. Test hashtags with various special characters: "#climate-change", "#AI/ML", "#covid19", "#2023data"
2. Verify which characters are accepted in hashtags
3. Test hashtags with spaces: "#climate change" (should not work)
4. Test hashtags with numbers: "#covid19", "#2023trends"
5. Verify error handling for invalid hashtag formats
6. Test edge cases like "#", "##double", "#-start-dash"

**Assumptions**:
- Hashtag format rules are defined and enforced
- Some special characters may be allowed, others rejected
- Clear validation rules exist for hashtag format

**Success Criteria**:
- Valid special characters in hashtags work correctly
- Invalid characters are handled gracefully
- Hashtags with spaces are not recognized as single hashtag
- Numbers in hashtags are supported
- Error handling doesn't break fact submission
- Validation rules are consistent and predictable

**Sample Data**:
- Valid: "#covid19", "#AI_ML", "#climate2023"
- Invalid: "#climate change", "#special@char", "#"
- Edge cases: "##double", "#-dash", "#123"

---

## TC_US08_EditFact_OwnFact_SuccessfulModification

**Objective**: Verify editing own fact content and resources

**Test Steps**:
1. Login as user and submit a fact with resources
2. Navigate to the submitted fact
3. Verify edit option is available and visible
4. Click edit option
5. Modify fact content: change text, add/remove hashtags
6. Modify resources: add new URL, remove existing image
7. Save changes
8. Verify fact displays with updated content
9. Verify all changes are preserved correctly

**Assumptions**:
- Edit functionality is available for fact authors
- Edit form pre-populates with existing content
- All fact elements (text, resources, hashtags) can be edited

**Success Criteria**:
- Edit option is visible for own facts
- Edit form loads with current fact content
- All modifications are saved correctly
- Updated fact displays immediately
- Resources are properly updated (added/removed)
- Hashtags are reprocessed after edit

**Sample Data**:
- Original fact: "Water freezes at 0°C #science"
- Edited fact: "Water freezes at 0°C (32°F) at standard pressure #science #physics"
- Resource changes: Add NASA URL, remove old image

---

## TC_US08_EditFact_OtherUserFact_NoEditOption

**Objective**: Verify edit option not available for other users' facts

**Test Steps**:
1. Login as User A and submit a fact
2. Logout and login as User B
3. Navigate to User A's fact
4. Verify no edit option is visible or accessible
5. Attempt direct URL access to edit function (if applicable)
6. Verify unauthorized access is prevented
7. Test with multiple different users to confirm consistency

**Assumptions**:
- Edit permissions are restricted to fact authors
- UI properly hides edit options for non-authors
- Backend enforces edit permissions

**Success Criteria**:
- Edit option is not visible for other users' facts
- No edit buttons, links, or menus appear
- Direct access attempts are blocked
- Appropriate error messages for unauthorized access
- Consistent behavior across all users and facts

**Sample Data**:
- User A fact: "The Earth is round #geography"
- User B (different user) attempting to edit User A's fact

---

## TC_US08_DeleteFact_OwnFact_ConfirmationDialog

**Objective**: Verify delete confirmation dialog for own facts

**Test Steps**:
1. Login as user and submit a fact
2. Navigate to the submitted fact
3. Locate and click delete option
4. Verify confirmation dialog appears
5. Verify dialog clearly explains deletion is permanent
6. Test "Cancel" option - verify fact is not deleted
7. Test "Confirm/Delete" option - proceed to next test case
8. Verify dialog prevents accidental deletion

**Assumptions**:
- Delete functionality includes confirmation step
- Confirmation dialog is clear and informative
- User can cancel deletion process

**Success Criteria**:
- Delete option is available for own facts
- Confirmation dialog appears when delete is clicked
- Dialog clearly warns about permanent deletion
- Cancel option preserves the fact
- Dialog is modal and requires user action
- Warning message is clear and appropriate

**Sample Data**:
- Test fact for deletion: "Test fact for deletion purposes #test"

---

## TC_US08_DeleteFact_Confirmation_PermanentRemoval

**Objective**: Verify fact is permanently removed after confirmation

**Test Steps**:
1. Continue from previous test case with confirmation dialog open
2. Click "Confirm" or "Delete" button in dialog
3. Verify fact is immediately removed from view
4. Navigate to main facts feed - verify fact is not listed
5. Check user's profile - verify fact is not in their facts list
6. Attempt to access fact by direct URL (if applicable)
7. Verify fact is completely removed from system

**Assumptions**:
- Deletion is immediate and permanent
- Fact is removed from all views and listings
- No recovery mechanism exists (for MVP)

**Success Criteria**:
- Fact disappears immediately after confirmation
- Fact is removed from all public listings
- Fact is removed from user's profile
- Direct access returns appropriate error (404/not found)
- Deletion is complete and irreversible
- No broken links or references remain

**Sample Data**:
- Previously created test fact that will be permanently deleted

---

## TC_US08_EditFact_ValidationRules_SameAsCreation

**Objective**: Verify edit validation follows same rules as creation

**Test Steps**:
1. Login and create a fact to edit
2. Edit the fact and test all validation rules:
   - Character limit (500 characters)
   - Empty content validation
   - URL format validation for resources
   - Image size limits for uploads
   - Hashtag format validation
3. Verify each validation rule works during edit
4. Compare validation behavior to fact creation
5. Verify error messages are consistent

**Assumptions**:
- Edit validation uses same rules as creation
- All validation rules apply during edit process
- Error messages are consistent between create and edit

**Success Criteria**:
- Character limit enforced during edit (500 chars)
- Empty content prevents saving edited fact
- Invalid URLs are rejected during edit
- Image size limits apply to new uploads during edit
- Hashtag validation works during edit
- Error messages match those shown during creation
- Validation is consistent and predictable

**Sample Data**:
- Test fact for editing with various validation scenarios
- 600-character text (over limit)
- Invalid URL: "not-a-valid-url"
- Large image file for size limit testing
- Invalid hashtag formats
