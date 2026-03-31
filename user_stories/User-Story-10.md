# User-Story-10: Comment on Facts

## User Story
As a user, I want to comment on facts so that I can provide additional context, ask questions, or explain my reasoning for voting.

## Acceptance Criteria
- **Given** I am viewing a fact
- **When** I write a comment (up to 250 characters) and submit it
- **Then** my comment should appear below the fact with my name and timestamp

- **Given** I am writing a comment
- **When** I exceed 250 characters
- **Then** I should see a character count warning and be prevented from submitting

- **Given** I am viewing comments on a fact
- **When** multiple users have commented
- **Then** I should see all comments in chronological order

## Business Rules
- Comments must be between 1 and 250 characters
- All users can comment on any fact (including their own)
- Comments are displayed in chronological order
- Character count should be displayed in real-time
- Comments show author name and timestamp

## Priority
High

## Estimated Effort
Medium
