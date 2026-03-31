# User-Story-11: Nested Comments

## User Story
As a user, I want to reply to specific comments to create threaded discussions so that conversations can be organized and easy to follow.

## Acceptance Criteria
- **Given** I am viewing a comment
- **When** I click "Reply" and submit a response
- **Then** my reply should appear nested under the original comment

- **Given** I am viewing nested comments
- **When** comments reach 3 levels deep
- **Then** further replies should not create additional nesting levels

- **Given** I am viewing a comment thread
- **When** there are multiple nested levels
- **Then** the visual hierarchy should clearly show the relationship between comments

## Business Rules
- Comments can be nested up to 3 levels deep
- Reply functionality should be available on all comments
- Visual indentation should indicate nesting level
- Same character limit (250) applies to replies
- Replies should show which comment they're responding to

## Priority
Medium

## Estimated Effort
Large
