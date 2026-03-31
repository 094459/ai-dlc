# User-Story-05: Submit Facts

## User Story
As a user, I want to submit facts for verification so that the community can help determine if they are true or false.

## Acceptance Criteria
- **Given** I am logged in and on the fact submission page
- **When** I enter a fact (up to 500 characters) and submit it
- **Then** the fact should be posted and visible to other users for verification

- **Given** I am entering a fact
- **When** I exceed 500 characters
- **Then** I should see a character count warning and be prevented from submitting

- **Given** I am submitting a fact
- **When** I leave the fact field empty
- **Then** I should see an error message that the fact is required

## Business Rules
- Facts must be between 1 and 500 characters
- All submitted facts are immediately visible to the community
- Users can submit multiple facts
- Character count should be displayed in real-time

## Priority
High

## Estimated Effort
Medium
