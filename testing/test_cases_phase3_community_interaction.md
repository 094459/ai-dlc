# Phase 3: Community Interaction - Detailed Test Cases

## TC_US09_Voting_OtherUserFact_SuccessfulVote

**Objective**: Verify voting on other users' facts

**Test Steps**:
1. Login as User A and submit a fact: "Photosynthesis converts CO2 to oxygen"
2. Logout and login as User B
3. Navigate to User A's fact
4. Verify "Fact" and "Fake" voting buttons are visible
5. Click "Fact" button
6. Verify vote is recorded and count updates
7. Verify visual feedback shows vote was cast
8. Refresh page and verify vote persists
9. Test voting "Fake" on different fact

**Assumptions**:
- Voting buttons are clearly visible and labeled
- Vote counts are displayed in real-time
- Users can vote on any fact except their own

**Success Criteria**:
- Voting buttons are accessible for other users' facts
- Vote is immediately recorded and count updates
- Visual feedback confirms vote was cast
- Vote persists across page refreshes
- Both "Fact" and "Fake" voting work correctly

**Sample Data**:
- User A fact: "Photosynthesis converts CO2 to oxygen"
- User B (voter) account for testing

---

## TC_US09_Voting_OwnFact_NoVotingOption

**Objective**: Verify cannot vote on own facts

**Test Steps**:
1. Login as User A
2. Submit a fact: "Water has the chemical formula H2O"
3. Navigate to the submitted fact
4. Verify voting buttons are not visible or disabled
5. Attempt to access voting functionality through direct methods (if applicable)
6. Verify no vote can be cast on own fact
7. Test with multiple facts from same user

**Assumptions**:
- System prevents self-voting through UI and backend
- Own facts are clearly distinguishable from others
- Voting restrictions are consistently enforced

**Success Criteria**:
- No voting buttons appear on own facts
- If buttons exist, they are clearly disabled
- Direct voting attempts are blocked
- Consistent behavior across all own facts
- Clear indication why voting is not available

**Sample Data**:
- User A fact: "Water has the chemical formula H2O"
- Same user (User A) attempting to vote

---

## TC_US09_Voting_ChangeVote_UpdatedCount

**Objective**: Verify ability to change vote and count update

**Test Steps**:
1. Login as User B
2. Navigate to User A's fact
3. Vote "Fact" and verify count increases
4. Click "Fake" button to change vote
5. Verify "Fact" count decreases by 1
6. Verify "Fake" count increases by 1
7. Change vote back to "Fact"
8. Verify counts update correctly again
9. Test vote removal (if supported)

**Assumptions**:
- Users can change their vote on same fact
- Vote counts update accurately when votes change
- Only one vote per user per fact is allowed

**Success Criteria**:
- Vote can be changed from Fact to Fake and vice versa
- Vote counts update immediately and accurately
- Previous vote is replaced, not added to
- Visual feedback shows current vote status
- Vote changes persist across sessions

**Sample Data**:
- Test fact with existing votes for realistic count testing
- User account for vote changing

---

## TC_US09_Voting_VoteCount_RealTimeUpdate

**Objective**: Verify real-time vote count updates

**Test Steps**:
1. Open fact in two browser windows/tabs
2. Login as different users in each window
3. In window 1 (User B), vote "Fact" on a fact
4. In window 2 (User C), verify count updates without refresh
5. In window 2, vote "Fake" on same fact
6. In window 1, verify count updates in real-time
7. Test with multiple rapid votes from different users

**Assumptions**:
- Real-time updates are implemented (WebSocket, polling, etc.)
- Vote counts sync across all user sessions
- Updates happen without page refresh

**Success Criteria**:
- Vote counts update in real-time across all sessions
- Updates appear within reasonable time (< 5 seconds)
- No page refresh required to see updates
- Counts remain accurate across all views
- System handles concurrent voting gracefully

**Sample Data**:
- Multiple user accounts for concurrent testing
- Test fact for voting

---

## TC_US09_Voting_BothCounts_VisibleDisplay

**Objective**: Verify both Fact and Fake vote counts are visible

**Test Steps**:
1. Navigate to facts with various vote distributions
2. Verify both "Fact" and "Fake" counts are displayed
3. Check facts with: only Fact votes, only Fake votes, mixed votes, no votes
4. Verify count format is clear and readable
5. Verify counts are properly labeled
6. Test display on different screen sizes/devices

**Assumptions**:
- Both vote types are always visible regardless of count
- Vote display is clear and unambiguous
- Counts are properly labeled to avoid confusion

**Success Criteria**:
- Both Fact and Fake counts are always visible
- Counts are clearly labeled (e.g., "Fact: 15", "Fake: 3")
- Zero counts are displayed (not hidden)
- Display is consistent across all facts
- Counts are readable and well-formatted

**Sample Data**:
- Facts with various vote patterns:
  - Fact: 10, Fake: 0
  - Fact: 0, Fake: 5
  - Fact: 8, Fake: 12
  - Fact: 0, Fake: 0

---

## TC_US10_Comments_ValidContent_SuccessfulPost

**Objective**: Verify posting comment within character limit

**Test Steps**:
1. Login as registered user
2. Navigate to a fact
3. Locate comment section
4. Enter valid comment: "This is supported by recent NASA research findings"
5. Verify character count shows within 250 limit
6. Click submit/post comment button
7. Verify comment appears below the fact
8. Verify comment shows author name and timestamp

**Assumptions**:
- Comment section is accessible on all facts
- Comment form is clearly visible and functional
- Comments appear immediately after posting

**Success Criteria**:
- Comment is successfully posted and visible
- Comment displays with correct author attribution
- Timestamp is accurate and properly formatted
- Comment appears in chronological order
- Character count validation works correctly

**Sample Data**:
- Valid comment: "This is supported by recent NASA research findings" (52 characters)

---

## TC_US10_Comments_CharacterLimit_PreventSubmission

**Objective**: Verify prevention of comment over 250 characters

**Test Steps**:
1. Login as registered user
2. Navigate to a fact and locate comment section
3. Enter text exceeding 250 characters
4. Verify character count shows over limit (e.g., 275/250)
5. Attempt to submit comment
6. Verify submission is prevented
7. Verify appropriate warning message
8. Reduce text to under 250 characters and verify submission works

**Assumptions**:
- Character limit is enforced at 250 characters
- Real-time character counting is implemented
- Submission prevention is user-friendly

**Success Criteria**:
- Character count accurately reflects input length
- Warning appears when limit is exceeded
- Submit button is disabled or submission blocked
- Clear error message explains the limit
- User can edit and successfully submit within limit

**Sample Data**:
- Long comment: 275-character string exceeding limit
- Valid comment: Edited version under 250 characters

---

## TC_US10_Comments_EmptyContent_ValidationError

**Objective**: Verify validation for empty comment

**Test Steps**:
1. Login as registered user
2. Navigate to a fact and locate comment section
3. Leave comment field empty
4. Attempt to submit comment
5. Verify validation error message appears
6. Verify submission is prevented
7. Enter valid content and verify submission works

**Assumptions**:
- Comment content is required
- Empty submission validation is implemented
- Error messages are helpful and clear

**Success Criteria**:
- Error message indicates comment content is required
- Submission is prevented when field is empty
- Error message is clear and helpful
- Field is highlighted as invalid
- User can correct and successfully submit

**Sample Data**:
- Empty comment field
- Valid comment for successful submission test

---

## TC_US10_Comments_ChronologicalOrder_ProperDisplay

**Objective**: Verify comments displayed chronologically

**Test Steps**:
1. Navigate to a fact with existing comments
2. Add new comment as User A: "First new comment"
3. Wait 1 minute, add comment as User B: "Second new comment"
4. Add comment as User C: "Third new comment"
5. Verify comments appear in chronological order
6. Check timestamps are accurate and properly ordered
7. Refresh page and verify order is maintained

**Assumptions**:
- Comments are timestamped when created
- Chronological ordering is implemented (newest first or oldest first)
- Order is consistent and predictable

**Success Criteria**:
- Comments display in consistent chronological order
- Timestamps are accurate and properly formatted
- Order is maintained across page refreshes
- New comments appear in correct position
- Order is logical and user-friendly

**Sample Data**:
- Multiple comments from different users at different times
- Test comments: "First new comment", "Second new comment", "Third new comment"

---

## TC_US10_Comments_AuthorTimestamp_ProperDisplay

**Objective**: Verify comment shows author name and timestamp

**Test Steps**:
1. Login as User A with profile name "John Doe"
2. Post comment: "Great scientific evidence here"
3. Verify comment displays author name "John Doe"
4. Verify timestamp shows current date/time
5. Login as different user and verify author attribution is correct
6. Test with users having different name formats
7. Verify timestamp format is consistent and readable

**Assumptions**:
- Author names are pulled from user profiles
- Timestamps are generated server-side for accuracy
- Display format is consistent across all comments

**Success Criteria**:
- Author name displays correctly for each comment
- Author name links to user profile (if applicable)
- Timestamp is accurate and properly formatted
- Attribution is consistent across all comments
- Display format is readable and professional

**Sample Data**:
- User profiles: "John Doe", "Jane Smith", "Dr. Science"
- Test comments from each user

---

## TC_US10_Comments_OwnFact_AllowCommenting

**Objective**: Verify can comment on own facts

**Test Steps**:
1. Login as User A
2. Submit a fact: "The periodic table has 118 elements"
3. Navigate to the submitted fact
4. Verify comment section is available
5. Post comment: "Updated as of 2023 discoveries"
6. Verify comment is posted successfully
7. Verify own comment appears with other comments
8. Test interaction with other users' comments on own fact

**Assumptions**:
- Users can comment on their own facts
- Own comments are treated same as others' comments
- No restrictions on self-commenting

**Success Criteria**:
- Comment section is available on own facts
- Own comments post successfully
- Own comments display with proper attribution
- Own comments appear in chronological order with others
- No special treatment or restrictions for own comments

**Sample Data**:
- User A fact: "The periodic table has 118 elements"
- User A comment: "Updated as of 2023 discoveries"

---

## TC_US11_NestedComments_ReplyFunctionality_ProperNesting

**Objective**: Verify reply creates proper nesting

**Test Steps**:
1. Navigate to fact with existing comment
2. Click "Reply" button on existing comment
3. Enter reply: "I agree with this assessment"
4. Submit reply
5. Verify reply appears nested under original comment
6. Verify visual indentation shows nesting level
7. Test multiple replies to same comment
8. Test reply to reply (second level nesting)

**Assumptions**:
- Reply functionality is available on all comments
- Visual nesting is implemented with indentation
- Nested structure is clear and intuitive

**Success Criteria**:
- Reply button is visible and functional on comments
- Replies appear visually nested under parent comments
- Indentation clearly shows comment hierarchy
- Multiple replies to same comment work correctly
- Second-level nesting (reply to reply) works

**Sample Data**:
- Original comment: "This fact needs more evidence"
- Reply: "I agree with this assessment"
- Second-level reply: "Here's additional research"

---

## TC_US11_NestedComments_ThreeLevelLimit_NoFurtherNesting

**Objective**: Verify nesting limited to 3 levels

**Test Steps**:
1. Create comment thread with 3 levels of nesting:
   - Level 1: Original comment
   - Level 2: Reply to original
   - Level 3: Reply to level 2 reply
2. Attempt to reply to level 3 comment
3. Verify no reply option or reply is flattened
4. Test with multiple branches at each level
5. Verify limit is consistently enforced

**Assumptions**:
- Three-level nesting limit is implemented
- System prevents or flattens deeper nesting
- Limit is enforced consistently across all threads

**Success Criteria**:
- Nesting works correctly for levels 1, 2, and 3
- Level 4 nesting is prevented or flattened
- Reply button is hidden/disabled at level 3
- Limit enforcement is consistent
- User experience remains intuitive despite limit

**Sample Data**:
- Level 1: "Original scientific observation"
- Level 2: "Reply with additional context"
- Level 3: "Further clarification needed"
- Attempted Level 4: "This should not nest further"

---

## TC_US11_NestedComments_VisualHierarchy_ClearIndication

**Objective**: Verify visual hierarchy shows nesting levels

**Test Steps**:
1. Create nested comment thread with all 3 levels
2. Verify each level has distinct visual indentation
3. Check that nesting is clear and easy to follow
4. Test with long comments at each level
5. Verify hierarchy is maintained with different screen sizes
6. Test with multiple nested threads on same fact

**Assumptions**:
- Visual design clearly indicates comment hierarchy
- Indentation or other visual cues show nesting levels
- Design is responsive and works on different devices

**Success Criteria**:
- Each nesting level has distinct visual treatment
- Hierarchy is immediately clear to users
- Visual design doesn't break with long comments
- Nesting remains clear on mobile devices
- Multiple nested threads don't interfere with each other

**Sample Data**:
- Multi-level nested comments with varying lengths
- Test on different screen sizes and devices

---

## TC_US11_NestedComments_CharacterLimit_SameAsRegular

**Objective**: Verify replies follow same character limit

**Test Steps**:
1. Navigate to existing comment
2. Click reply button
3. Enter reply text approaching 250 character limit
4. Verify character count displays and enforces limit
5. Attempt to exceed 250 characters in reply
6. Verify same validation as regular comments
7. Test with valid reply under limit

**Assumptions**:
- Reply character limit matches regular comment limit (250)
- Same validation rules apply to replies
- Character counting works in reply interface

**Success Criteria**:
- Reply character limit is 250 characters (same as comments)
- Character count displays in real-time for replies
- Over-limit replies are prevented
- Validation messages are consistent with regular comments
- Reply submission works correctly within limit

**Sample Data**:
- Valid reply: "This provides excellent supporting evidence for the claim" (65 characters)
- Over-limit reply: 275-character string

---

## TC_US12_ThreadManagement_CollapseExpand_ProperFunctionality

**Objective**: Verify thread collapse/expand functionality

**Test Steps**:
1. Navigate to fact with nested comment thread
2. Locate collapse/expand button for thread
3. Click collapse button
4. Verify entire thread collapses (hides nested comments)
5. Verify collapse indicator shows thread is collapsed
6. Click expand button
7. Verify thread expands showing all nested comments
8. Test with multiple threads on same fact

**Assumptions**:
- Collapse/expand controls are visible and intuitive
- Collapsing hides nested comments but preserves parent
- Expand restores full thread visibility

**Success Criteria**:
- Collapse button is clearly visible and functional
- Collapsing hides all nested comments in thread
- Collapsed state is visually indicated
- Expand button restores full thread visibility
- Functionality works for all comment threads
- State changes are smooth and immediate

**Sample Data**:
- Comment thread with 2-3 levels of nesting for testing

---

## TC_US12_ThreadManagement_CollapsedState_CommentCount

**Objective**: Verify collapsed state shows comment count

**Test Steps**:
1. Create comment thread with multiple nested replies (e.g., 5 total comments)
2. Collapse the thread
3. Verify collapsed state shows comment count (e.g., "5 replies")
4. Test with threads of different sizes
5. Verify count is accurate and updates when new comments added
6. Test count display format and clarity

**Assumptions**:
- Collapsed threads display total comment count
- Count includes all nested comments in thread
- Count updates dynamically when comments are added

**Success Criteria**:
- Collapsed thread shows accurate comment count
- Count format is clear (e.g., "5 replies", "3 comments")
- Count includes all nested levels
- Count updates when new comments are added to collapsed thread
- Display is consistent across different thread sizes

**Sample Data**:
- Thread with 5 nested comments
- Thread with 1 reply
- Thread with 10+ comments for large number testing

---

## TC_US12_ThreadManagement_SessionPersistence_StateRetained

**Objective**: Verify thread state persists during session

**Test Steps**:
1. Navigate to fact with multiple comment threads
2. Collapse some threads and leave others expanded
3. Navigate away from the fact page
4. Return to the same fact page
5. Verify collapsed threads remain collapsed
6. Verify expanded threads remain expanded
7. Test across browser refresh
8. Test with multiple facts and thread states

**Assumptions**:
- Thread collapse/expand state is stored during session
- State persistence works across page navigation
- Session storage maintains thread states

**Success Criteria**:
- Collapsed threads remain collapsed when returning to page
- Expanded threads remain expanded
- State persists across page navigation within session
- State persists across browser refresh
- Multiple thread states are maintained independently

**Sample Data**:
- Multiple facts with comment threads
- Mixed collapsed/expanded states for testing

---

## TC_US12_ThreadManagement_NestedCollapse_AnyLevel

**Objective**: Verify collapsing works at any nesting level

**Test Steps**:
1. Create deeply nested comment thread (3 levels)
2. Test collapsing at level 1 (collapses entire thread)
3. Expand level 1, then collapse level 2 sub-thread
4. Verify only level 2 and below collapse
5. Test collapsing individual level 3 comments
6. Verify each level can be collapsed independently
7. Test mixed collapse states within same thread

**Assumptions**:
- Collapse functionality is available at each nesting level
- Collapsing affects only that level and below
- Independent collapse control for each sub-thread

**Success Criteria**:
- Collapse buttons available at each nesting level
- Collapsing level affects only that branch and below
- Parent levels remain visible when child levels collapse
- Independent control of each sub-thread
- Visual hierarchy maintained with partial collapses

**Sample Data**:
- Complex nested thread with multiple branches at each level

---

## TC_US13_CommentVoting_OtherUserComment_SuccessfulVote

**Objective**: Verify voting on other users' comments

**Test Steps**:
1. Login as User A and post comment: "This fact is well-documented"
2. Login as User B
3. Navigate to User A's comment
4. Verify upvote and downvote buttons are visible
5. Click upvote button
6. Verify vote is recorded and score updates
7. Test downvote on different comment
8. Verify vote counts display correctly

**Assumptions**:
- Comment voting uses upvote/downvote system
- Vote buttons are clearly visible on others' comments
- Vote scores are displayed and update in real-time

**Success Criteria**:
- Upvote and downvote buttons are accessible
- Votes are immediately recorded and displayed
- Vote scores update correctly (+1 for upvote, -1 for downvote)
- Visual feedback confirms vote was cast
- Vote persists across page refreshes

**Sample Data**:
- User A comment: "This fact is well-documented"
- User B account for voting

---

## TC_US13_CommentVoting_OwnComment_NoVotingOption

**Objective**: Verify cannot vote on own comments

**Test Steps**:
1. Login as User A
2. Post comment: "I believe this needs more research"
3. Verify no voting buttons appear on own comment
4. Attempt direct access to voting (if applicable)
5. Test with multiple own comments
6. Verify consistent behavior across all own comments

**Assumptions**:
- Self-voting on comments is prevented
- UI hides voting options for own comments
- Backend enforces voting restrictions

**Success Criteria**:
- No voting buttons visible on own comments
- Direct voting attempts are blocked
- Consistent behavior across all own comments
- Clear indication why voting is not available (optional)

**Sample Data**:
- User A comment: "I believe this needs more research"
- Same user attempting to vote on own comment

---

## TC_US13_CommentVoting_ChangeVote_UpdatedScore

**Objective**: Verify ability to change comment vote

**Test Steps**:
1. Login as User B
2. Navigate to User A's comment
3. Upvote the comment (+1 to score)
4. Change vote to downvote
5. Verify score decreases by 2 (from +1 to -1)
6. Change back to upvote
7. Verify score increases by 2 (from -1 to +1)
8. Test vote removal (if supported)

**Assumptions**:
- Users can change their vote on same comment
- Vote changes update score correctly
- Only one vote per user per comment allowed

**Success Criteria**:
- Vote can be changed from upvote to downvote and vice versa
- Score updates accurately reflect vote changes
- Previous vote is replaced, not added to
- Visual feedback shows current vote status
- Vote changes persist across sessions

**Sample Data**:
- Test comment with existing votes for realistic scoring

---

## TC_US13_CommentVoting_NetScore_ProperCalculation

**Objective**: Verify net score calculation (upvotes - downvotes)

**Test Steps**:
1. Create comment and have multiple users vote:
   - User B: Upvote (+1)
   - User C: Upvote (+1)
   - User D: Downvote (-1)
   - User E: Upvote (+1)
2. Verify net score displays as +2 (3 upvotes - 1 downvote)
3. Have User C change to downvote
4. Verify score updates to 0 (2 upvotes - 2 downvotes)
5. Test with various vote combinations
6. Verify score calculation is always accurate

**Assumptions**:
- Score displays net result of upvotes minus downvotes
- Score calculation updates in real-time
- Score can be positive, negative, or zero

**Success Criteria**:
- Net score calculation is mathematically correct
- Score updates immediately when votes change
- Negative scores are properly displayed
- Zero scores are shown (not hidden)
- Score format is clear and readable

**Sample Data**:
- Test scenarios:
  - 5 upvotes, 2 downvotes = +3
  - 3 upvotes, 7 downvotes = -4
  - 4 upvotes, 4 downvotes = 0
  - 0 upvotes, 0 downvotes = 0
