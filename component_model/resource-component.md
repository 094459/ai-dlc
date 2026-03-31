# Resource Component

## Purpose and Responsibilities
The Resource Component manages supporting resources (URLs and images) that users can attach to facts. It handles resource validation, storage, retrieval, and display, providing evidence and context for submitted facts.

## Attributes and Data Models

### FactResource Entity
```
FactResource {
  id: UUID (Primary Key)
  fact_id: UUID (Foreign Key to Fact)
  resource_type: Enum ('url', 'image')
  resource_value: String (URL or file path)
  display_title: String (Optional)
  file_size: Integer (For images, in bytes)
  mime_type: String (For images)
  created_at: DateTime
  is_active: Boolean (Default: true)
}
```

### ResourceValidation Entity
```
ResourceValidation {
  id: UUID (Primary Key)
  resource_id: UUID (Foreign Key to FactResource)
  validation_status: Enum ('pending', 'valid', 'invalid', 'broken')
  validation_message: String (Optional)
  last_checked: DateTime
  check_count: Integer (Default: 0)
}
```

## Behaviors and Methods

### Resource Management Methods
- **addResourceToFact(factId, resourceType, resourceValue)**: Adds new resource to fact
- **removeResourceFromFact(resourceId, userId)**: Removes resource from fact
- **getResourcesByFact(factId)**: Retrieves all resources for a specific fact
- **updateResourceTitle(resourceId, title)**: Updates display title for resource
- **getResourceById(resourceId)**: Retrieves specific resource details

### URL Resource Methods
- **validateUrlFormat(url)**: Validates URL format and accessibility
- **extractUrlMetadata(url)**: Extracts title and description from URL
- **checkUrlAccessibility(url)**: Verifies URL is accessible
- **generateUrlPreview(url)**: Creates preview data for URL display

### Image Resource Methods
- **uploadImageResource(factId, imageFile)**: Handles image file upload
- **validateImageFile(file)**: Validates image format, size, and content
- **resizeImage(file, maxWidth, maxHeight)**: Resizes image for web display
- **generateImageThumbnail(file)**: Creates thumbnail for image preview
- **deleteImageFile(resourceId)**: Removes image file from storage

### Validation Methods
- **validateResourceLimit(factId)**: Ensures fact doesn't exceed resource limit
- **sanitizeResourceValue(value)**: Cleans resource value for safe storage
- **checkResourceOwnership(resourceId, userId)**: Verifies user can modify resource

## Interfaces Provided
- **ResourceManagementService**: Interface for resource CRUD operations
- **ResourceValidationService**: Interface for resource validation
- **ResourceDisplayService**: Interface for resource rendering and preview

## Interfaces Required
- **AuthenticationService**: For user session validation
- **DatabaseService**: For resource data persistence
- **FileStorageService**: For image file storage and management
- **HttpService**: For URL validation and metadata extraction
- **ImageProcessingService**: For image validation and resizing

## Dependencies and Relationships
- **Depends on**: Fact Component, File Storage, HTTP client, Image Processing
- **Used by**: UI Framework Component for resource display
- **Integrates with**: Fact Component (resources belong to facts)

## Business Rules and Constraints
- Resources are optional for fact submission
- Maximum 5 resources per fact (configurable)
- Supported image formats: JPG, PNG, GIF, WebP
- Maximum image file size: 10MB (configurable)
- URLs must be valid HTTP/HTTPS format
- URLs must be accessible (return 200 status)
- Images automatically resized for consistent display
- Resource validation occurs asynchronously after upload

## Error Handling
- **InvalidUrlFormat**: When URL doesn't match required format
- **UrlNotAccessible**: When URL returns error or is unreachable
- **InvalidImageFormat**: When uploaded file is not supported image type
- **FileSizeExceeded**: When image file exceeds maximum size
- **ResourceLimitExceeded**: When fact already has maximum resources
- **UnauthorizedResourceEdit**: When user tries to modify resource they don't own
- **ResourceNotFound**: When requested resource doesn't exist

## File Storage Structure
```
/uploads/fact_resources/
  /{fact_id}/
    /images/
      /original_{resource_id}.{ext}
      /resized_{resource_id}.{ext}
      /thumbnail_{resource_id}.{ext}
```

## URL Validation Process
1. **Format Validation**: Check URL format using regex
2. **Accessibility Check**: Send HTTP HEAD request to verify URL is reachable
3. **Metadata Extraction**: Extract title, description, and favicon if available
4. **Content Type Check**: Verify URL points to appropriate content

## Image Processing Pipeline
1. **File Validation**: Check format, size, and basic image integrity
2. **Security Scan**: Scan for embedded malicious content
3. **Resize Original**: Create web-optimized version (max 800px width)
4. **Generate Thumbnail**: Create small preview (150x150px)
5. **Store Files**: Save original, resized, and thumbnail versions
6. **Update Database**: Record file paths and metadata

## Resource Display Formats

### URL Resources
- Display title (extracted or user-provided)
- Domain name and favicon
- Brief description (if available)
- Click-through link with security warnings

### Image Resources
- Thumbnail preview in fact display
- Full-size modal view on click
- File size and format information
- Alt text for accessibility

## Integration Points
- **Fact Component**: Resources are attached to specific facts
- **UI Framework Component**: Renders resource previews and full views
- **Security Component**: Validates resource safety and content
- **Admin Dashboard**: Provides resource management and statistics

