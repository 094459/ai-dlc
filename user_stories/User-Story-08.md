# User-Story-08: Edit and Delete Own Facts

## User Story
As a user, I want to edit or delete facts that I have submitted so that I can correct mistakes or remove content I no longer want to share.

## Acceptance Criteria
- **Given** I am viewing a fact I submitted
- **When** I click the edit option
- **Then** I should be able to modify the fact text, resources, and hashtags

- **Given** I am viewing a fact I submitted
- **When** I click the delete option
- **Then** I should see a confirmation dialog and be able to permanently remove the fact

- **Given** I am viewing facts submitted by other users
- **When** I look for edit/delete options
- **Then** I should not see these options as they are only available for my own facts

## Business Rules
- Users can only edit/delete their own facts
- Edit functionality should maintain the same validation rules as creation
- Delete action should require confirmation
- Deleted facts should be permanently removed from the system
- Edit history is not required for MVP

## Priority
Medium

## Estimated Effort
Medium
