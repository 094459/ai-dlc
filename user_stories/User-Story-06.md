# User-Story-06: Add Resources to Facts

## User Story
As a user submitting a fact, I want to add optional supporting resources like URLs and images so that I can provide evidence and context for my fact.

## Acceptance Criteria
- **Given** I am creating a fact
- **When** I add a URL as a resource
- **Then** the URL should be validated and stored with the fact

- **Given** I am creating a fact
- **When** I upload an image as a resource
- **Then** the image should be properly stored and displayed with the fact

- **Given** I am adding resources
- **When** I provide an invalid URL format
- **Then** I should see an error message about the URL format

## Business Rules
- Resources are optional for fact submission
- URLs must be in valid format
- Images must be in supported formats (JPG, PNG, GIF)
- Multiple resources can be added to a single fact
- Image file size should have reasonable limits

## Priority
Medium

## Estimated Effort
Large
