# User-Story-13: Vote on Comments

## User Story
As a user, I want to vote on comments (upvote/downvote) so that I can indicate which comments are helpful or unhelpful to the discussion.

## Acceptance Criteria
- **Given** I am viewing a comment by another user
- **When** I click the upvote or downvote button
- **Then** my vote should be recorded and the vote score should update

- **Given** I have already voted on a comment
- **When** I click the opposite vote button
- **Then** my vote should change and the score should update accordingly

- **Given** I am viewing a comment I wrote
- **When** I look for voting options
- **Then** I should not be able to vote on my own comments

## Business Rules
- Users cannot vote on their own comments
- Each user can only vote once per comment (upvote or downvote)
- Users can change their vote from upvote to downvote or vice versa
- Vote scores should be displayed as net score (upvotes - downvotes)
- Vote counts should update in real-time

## Priority
Low

## Estimated Effort
Medium
