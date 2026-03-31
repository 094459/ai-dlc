# Unit 3: Community Interaction & Engagement

## Unit Overview
This unit handles all community-driven interactions including voting on facts, commenting, threaded discussions, and comment voting. It provides the social engagement layer that enables community-based fact verification.

## Team Information
- **Team Size**: 3-4 developers
- **Skills Required**: Complex UI/UX for threaded comments, real-time updates, backend voting systems
- **Dependencies**: Unit 1 (user authentication), Unit 2 (facts to interact with)
- **Estimated Effort**: High

## User Stories Included

### User-Story-09: Vote on Facts

#### User Story
As a user, I want to vote on submitted facts as either "Fact" or "Fake" so that I can contribute to the community's assessment of the information's accuracy.

#### Acceptance Criteria
- **Given** I am viewing a fact submitted by another user
- **When** I click on "Fact" or "Fake" voting buttons
- **Then** my vote should be recorded and the vote count should update

- **Given** I have already voted on a fact
- **When** I try to vote again on the same fact
- **Then** I should either change my vote or see that I've already voted

- **Given** I am viewing a fact I submitted
- **When** I look for voting options
- **Then** I should not be able to vote on my own facts

#### Business Rules
- Users cannot vote on their own facts
- Each user can only vote once per fact
- Users can change their vote if needed
- Vote counts should be displayed in real-time
- Both "Fact" and "Fake" vote counts should be visible

#### Priority: High
#### Estimated Effort: Medium

---

### User-Story-10: Comment on Facts

#### User Story
As a user, I want to comment on facts so that I can provide additional context, ask questions, or explain my reasoning for voting.

#### Acceptance Criteria
- **Given** I am viewing a fact
- **When** I write a comment (up to 250 characters) and submit it
- **Then** my comment should appear below the fact with my name and timestamp

- **Given** I am writing a comment
- **When** I exceed 250 characters
- **Then** I should see a character count warning and be prevented from submitting

- **Given** I am viewing comments on a fact
- **When** multiple users have commented
- **Then** I should see all comments in chronological order

#### Business Rules
- Comments must be between 1 and 250 characters
- All users can comment on any fact (including their own)
- Comments are displayed in chronological order
- Character count should be displayed in real-time
- Comments show author name and timestamp

#### Priority: High
#### Estimated Effort: Medium

---

### User-Story-11: Nested Comments

#### User Story
As a user, I want to reply to specific comments to create threaded discussions so that conversations can be organized and easy to follow.

#### Acceptance Criteria
- **Given** I am viewing a comment
- **When** I click "Reply" and submit a response
- **Then** my reply should appear nested under the original comment

- **Given** I am viewing nested comments
- **When** comments reach 3 levels deep
- **Then** further replies should not create additional nesting levels

- **Given** I am viewing a comment thread
- **When** there are multiple nested levels
- **Then** the visual hierarchy should clearly show the relationship between comments

#### Business Rules
- Comments can be nested up to 3 levels deep
- Reply functionality should be available on all comments
- Visual indentation should indicate nesting level
- Same character limit (250) applies to replies
- Replies should show which comment they're responding to

#### Priority: Medium
#### Estimated Effort: Large

---

### User-Story-12: Thread View and Management

#### User Story
As a user, I want to view comment threads in an organized way and collapse/expand them so that I can follow conversations easily and focus on relevant discussions.

#### Acceptance Criteria
- **Given** I am viewing a fact with many comments
- **When** I click on a thread collapse/expand button
- **Then** the entire comment thread should hide/show while maintaining context

- **Given** I am viewing collapsed threads
- **When** I see the collapsed state
- **Then** I should see a summary indicating how many comments are hidden

- **Given** I am following a conversation
- **When** I expand a thread
- **Then** all nested comments should be visible in proper hierarchical order

#### Business Rules
- Thread collapsing should work at any level of nesting
- Collapsed threads should show comment count
- Thread state (collapsed/expanded) should persist during the session
- Visual indicators should clearly show collapsible threads
- Default state should be expanded for readability

#### Priority: Medium
#### Estimated Effort: Medium

---

### User-Story-13: Vote on Comments

#### User Story
As a user, I want to vote on comments (upvote/downvote) so that I can indicate which comments are helpful or unhelpful to the discussion.

#### Acceptance Criteria
- **Given** I am viewing a comment by another user
- **When** I click the upvote or downvote button
- **Then** my vote should be recorded and the vote score should update

- **Given** I have already voted on a comment
- **When** I click the opposite vote button
- **Then** my vote should change and the score should update accordingly

- **Given** I am viewing a comment I wrote
- **When** I look for voting options
- **Then** I should not be able to vote on my own comments

#### Business Rules
- Users cannot vote on their own comments
- Each user can only vote once per comment (upvote or downvote)
- Users can change their vote from upvote to downvote or vice versa
- Vote scores should be displayed as net score (upvotes - downvotes)
- Vote counts should update in real-time

#### Priority: Low
#### Estimated Effort: Medium

## Technical Interfaces

### Interfaces Provided to Other Units
- **Comment Retrieval Service**: Provides comment data for moderation and admin purposes
- **Voting Analytics Service**: Provides voting statistics and trends
- **Engagement Metrics Service**: Provides user engagement data

### Interfaces Required from Other Units
- **User Authentication Service** (Unit 1): Validates user sessions for all interactions
- **User Profile Service** (Unit 1): Gets user information for comment attribution
- **Fact Retrieval Service** (Unit 2): Gets fact information for voting and commenting
- **Fact Ownership Service** (Unit 2): Validates fact ownership for voting restrictions

### Data Models
- **FactVote**: id, fact_id, user_id, vote_type (fact/fake), created_at, updated_at
- **Comment**: id, fact_id, user_id, parent_comment_id, content, created_at, updated_at, is_deleted
- **CommentVote**: id, comment_id, user_id, vote_type (upvote/downvote), created_at, updated_at

### Integration Points
- **Unit 4 (Content Moderation)**: Exposes comments and votes for moderation actions
- **Unit 5 (Platform Infrastructure)**: Provides engagement data for admin dashboard

## Implementation Notes
- Implement comment threading with efficient tree traversal algorithms
- Implement notification system for comment replies
- Consider implementing comment sorting options (chronological, by votes, etc.)
