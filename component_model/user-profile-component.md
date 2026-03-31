# User Profile Component

## Purpose and Responsibilities
The User Profile Component manages user profile information including name, biography, profile photos, and profile viewing functionality. It handles profile creation, updates, and public profile display.

## Attributes and Data Models

### UserProfile Entity
```
UserProfile {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to User, Unique)
  name: String (Required)
  biography: Text (Optional, Max 1000 characters)
  profile_photo_url: String (Optional)
  created_at: DateTime
  updated_at: DateTime
}
```

### ProfilePhoto Entity
```
ProfilePhoto {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to User)
  filename: String
  file_path: String
  file_size: Integer
  mime_type: String
  uploaded_at: DateTime
}
```

## Behaviors and Methods

### Profile Management Methods
- **createProfile(userId, name, biography, profilePhoto)**: Creates new user profile
- **updateProfile(userId, name, biography, profilePhoto)**: Updates existing profile
- **getProfile(userId)**: Retrieves user profile information
- **getPublicProfile(userId)**: Gets profile info for public viewing
- **deleteProfile(userId)**: Removes user profile (soft delete)

### Photo Management Methods
- **uploadProfilePhoto(userId, photoFile)**: Handles profile photo upload
- **validatePhotoFile(file)**: Validates image format and size
- **resizeProfilePhoto(file)**: Resizes image to standard dimensions
- **deleteProfilePhoto(userId)**: Removes current profile photo
- **getDefaultPhotoUrl()**: Returns default placeholder image URL

### Profile Display Methods
- **getUserProfileWithFacts(userId)**: Gets profile with user's submitted facts
- **formatProfileForDisplay(profile)**: Formats profile data for UI display
- **getProfileCompletionStatus(userId)**: Checks if profile is complete

## Interfaces Provided
- **ProfileManagementService**: Interface for profile CRUD operations
- **ProfileDisplayService**: Interface for public profile viewing
- **ProfilePhotoService**: Interface for photo upload and management

## Interfaces Required
- **AuthenticationService**: For user session validation
- **DatabaseService**: For profile data persistence
- **FileStorageService**: For profile photo storage
- **ImageProcessingService**: For photo validation and resizing

## Dependencies and Relationships
- **Depends on**: User Authentication Component, File Storage, Image Processing
- **Used by**: UI Framework Component, Admin Dashboard Component
- **Integrates with**: Fact Component (for displaying user's facts)

## Business Rules and Constraints
- Name is required for profile completion
- Biography is optional with 1000 character limit
- Profile photo is optional but must be valid image format
- Supported image formats: JPG, PNG, GIF
- Maximum photo file size: 5MB (configurable)
- Profile photos resized to standard dimensions (200x200px)
- All profiles are publicly viewable within the application
- Users can only edit their own profiles

## Error Handling
- **ProfileNotFound**: When requested profile doesn't exist
- **InvalidImageFormat**: When uploaded file is not supported image type
- **FileSizeExceeded**: When uploaded photo exceeds size limit
- **BiographyTooLong**: When biography exceeds character limit
- **UnauthorizedProfileEdit**: When user tries to edit another's profile

## File Storage Structure
```
/uploads/profile_photos/
  /{user_id}/
    /original_{timestamp}.{ext}
    /resized_{timestamp}.{ext}
```

## Validation Rules
- **Name**: Required, 1-100 characters, no special characters except spaces, hyphens, apostrophes
- **Biography**: Optional, 0-1000 characters, basic HTML sanitization
- **Profile Photo**: Optional, valid image format, under size limit

## Integration Points
- **User Authentication Component**: Validates user ownership of profiles
- **Fact Component**: Displays user's submitted facts on profile page
- **Comment Component**: Shows user name and photo in comments
- **Admin Dashboard**: Provides profile management capabilities
- **UI Framework**: Renders profile display components

## Default Behavior
- New users start with empty profile (name required for completion)
- Default placeholder image used when no profile photo uploaded
- Profile completion status tracked for UI prompts
- Profile photos automatically resized and optimized for web display
