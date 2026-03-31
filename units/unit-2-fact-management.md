# Unit 2: Fact Management & Content Creation

## Unit Overview
This unit handles the core content functionality of the application, including fact submission, editing, resource management, and hashtag functionality. It provides the primary content that users interact with throughout the platform.

## Team Information
- **Team Size**: 3-4 developers
- **Skills Required**: Backend API development, file upload handling, content management, frontend forms
- **Dependencies**: Unit 1 (requires user authentication)
- **Estimated Effort**: High

## User Stories Included

### User-Story-05: Submit Facts

#### User Story
As a user, I want to submit facts for verification so that the community can help determine if they are true or false.

#### Acceptance Criteria
- **Given** I am logged in and on the fact submission page
- **When** I enter a fact (up to 500 characters) and submit it
- **Then** the fact should be posted and visible to other users for verification

- **Given** I am entering a fact
- **When** I exceed 500 characters
- **Then** I should see a character count warning and be prevented from submitting

- **Given** I am submitting a fact
- **When** I leave the fact field empty
- **Then** I should see an error message that the fact is required

#### Business Rules
- Facts must be between 1 and 500 characters
- All submitted facts are immediately visible to the community
- Users can submit multiple facts
- Character count should be displayed in real-time

#### Priority: High
#### Estimated Effort: Medium

---

### User-Story-06: Add Resources to Facts

#### User Story
As a user submitting a fact, I want to add optional supporting resources like URLs and images so that I can provide evidence and context for my fact.

#### Acceptance Criteria
- **Given** I am creating a fact
- **When** I add a URL as a resource
- **Then** the URL should be validated and stored with the fact

- **Given** I am creating a fact
- **When** I upload an image as a resource
- **Then** the image should be properly stored and displayed with the fact

- **Given** I am adding resources
- **When** I provide an invalid URL format
- **Then** I should see an error message about the URL format

#### Business Rules
- Resources are optional for fact submission
- URLs must be in valid format
- Images must be in supported formats (JPG, PNG, GIF)
- Multiple resources can be added to a single fact
- Image file size should have reasonable limits
- Image file size limits should be configurable at the application level

#### Priority: Medium
#### Estimated Effort: Large

---

### User-Story-07: Add Hashtags to Facts

#### User Story
As a user submitting a fact, I want to add hashtags so that my fact can be categorized and easily discovered by others interested in similar topics.

#### Acceptance Criteria
- **Given** I am creating a fact
- **When** I add hashtags using the # symbol
- **Then** the hashtags should be recognized, formatted, and made clickable

- **Given** I am viewing facts with hashtags
- **When** I click on a hashtag
- **Then** I should see all facts that contain that hashtag

- **Given** I am adding hashtags
- **When** I use special characters or spaces in hashtags
- **Then** the system should handle them appropriately or show validation errors

#### Business Rules
- Hashtags are optional for fact submission
- Hashtags should be clickable and lead to filtered views
- Multiple hashtags can be added to a single fact
- Hashtags should be case-insensitive for searching
- Hashtags should follow standard format (#word)

#### Priority: Medium
#### Estimated Effort: Medium

---

### User-Story-08: Edit and Delete Own Facts

#### User Story
As a user, I want to edit or delete facts that I have submitted so that I can correct mistakes or remove content I no longer want to share.

#### Acceptance Criteria
- **Given** I am viewing a fact I submitted
- **When** I click the edit option
- **Then** I should be able to modify the fact text, resources, and hashtags

- **Given** I am viewing a fact I submitted
- **When** I click the delete option
- **Then** I should see a confirmation dialog and be able to permanently remove the fact

- **Given** I am viewing facts submitted by other users
- **When** I look for edit/delete options
- **Then** I should not see these options as they are only available for my own facts

#### Business Rules
- Users can only edit/delete their own facts
- Edit functionality should maintain the same validation rules as creation
- Delete action should require confirmation
- Deleted facts should be permanently removed from the system
- Edit history should record when facts are edited

#### Priority: Medium
#### Estimated Effort: Medium

## Technical Interfaces

### Interfaces Provided to Other Units
- **Fact Retrieval Service**: Provides fact content and metadata to other units
- **Fact Ownership Service**: Validates if a user owns a specific fact
- **Hashtag Service**: Provides hashtag-based fact filtering and discovery

### Interfaces Required from Other Units
- **User Authentication Service** (Unit 1): Validates user sessions for fact operations
- **User Profile Service** (Unit 1): Gets user information for fact attribution

### Data Models
- **Fact**: id, user_id, content, created_at, updated_at, is_deleted
- **FactResource**: id, fact_id, resource_type (url/image), resource_value, created_at
- **Hashtag**: id, tag_name, created_at
- **FactHashtag**: fact_id, hashtag_id (many-to-many relationship)

### Integration Points
- **Unit 3 (Community Interaction)**: Provides facts for voting and commenting
- **Unit 4 (Content Moderation)**: Exposes facts for moderation actions
- **Unit 5 (Platform Infrastructure)**: Provides fact data for admin dashboard

## Implementation Notes
- Use file system for image resources
- Implement URL validation and preview generation
- Hashtag parsing should be case-insensitive but preserve original case
- Implement soft delete for facts to maintain referential integrity
- Add full-text search capabilities for fact discovery
