# User-Story-09: Vote on Facts

## User Story
As a user, I want to vote on submitted facts as either "Fact" or "Fake" so that I can contribute to the community's assessment of the information's accuracy.

## Acceptance Criteria
- **Given** I am viewing a fact submitted by another user
- **When** I click on "Fact" or "Fake" voting buttons
- **Then** my vote should be recorded and the vote count should update

- **Given** I have already voted on a fact
- **When** I try to vote again on the same fact
- **Then** I should either change my vote or see that I've already voted

- **Given** I am viewing a fact I submitted
- **When** I look for voting options
- **Then** I should not be able to vote on my own facts

## Business Rules
- Users cannot vote on their own facts
- Each user can only vote once per fact
- Users can change their vote if needed
- Vote counts should be displayed in real-time
- Both "Fact" and "Fake" vote counts should be visible

## Priority
High

## Estimated Effort
Medium
