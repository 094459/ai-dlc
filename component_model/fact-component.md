# Fact Component

## Purpose and Responsibilities
The Fact Component manages the core content of the application - user-submitted facts. It handles fact creation, editing, deletion, retrieval, and validation. This component serves as the central content entity that other components interact with.

## Attributes and Data Models

### Fact Entity
```
Fact {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to User)
  content: Text (Required, Max 500 characters)
  created_at: DateTime
  updated_at: DateTime
  is_deleted: Boolean (Default: false)
  edit_count: Integer (Default: 0)
  last_edited_at: DateTime
}
```

### FactEditHistory Entity
```
FactEditHistory {
  id: UUID (Primary Key)
  fact_id: UUID (Foreign Key to Fact)
  previous_content: Text
  edited_at: DateTime
  edit_reason: String (Optional)
}
```

## Behaviors and Methods

### Core Fact Management Methods
- **createFact(userId, content, resources, hashtags)**: Creates new fact with validation
- **updateFact(factId, userId, content, resources, hashtags)**: Updates existing fact
- **deleteFact(factId, userId)**: Soft deletes fact (marks as deleted)
- **getFact(factId)**: Retrieves single fact with all related data
- **getFactsByUser(userId)**: Gets all facts submitted by specific user
- **getAllFacts(limit, offset)**: Retrieves paginated list of active facts

### Validation Methods
- **validateFactContent(content)**: Ensures content meets length and format requirements
- **checkFactOwnership(factId, userId)**: Verifies user owns the fact
- **sanitizeContent(content)**: Cleans content for safe display
- **validateFactExists(factId)**: Confirms fact exists and is not deleted

### Search and Filter Methods
- **searchFacts(query)**: Full-text search across fact content
- **getFactsByHashtag(hashtag)**: Retrieves facts containing specific hashtag
- **getFactsWithResources()**: Gets facts that have attached resources
- **getRecentFacts(limit)**: Gets most recently created facts

### Statistics Methods
- **getFactCount()**: Returns total number of active facts
- **getFactCountByUser(userId)**: Returns fact count for specific user
- **getFactEngagementStats(factId)**: Gets vote and comment counts for fact

## Interfaces Provided
- **FactManagementService**: Primary interface for fact CRUD operations
- **FactRetrievalService**: Interface for fact querying and display
- **FactOwnershipService**: Interface for validating fact ownership
- **FactSearchService**: Interface for fact search and filtering

## Interfaces Required
- **AuthenticationService**: For user session validation
- **DatabaseService**: For fact data persistence
- **ResourceService**: For managing attached resources
- **HashtagService**: For hashtag processing and linking
- **ValidationService**: For content validation and sanitization

## Dependencies and Relationships
- **Depends on**: User Authentication Component, Resource Component, Hashtag Component
- **Used by**: Voting Component, Comment Component, UI Framework Component
- **Integrates with**: User Profile Component (for fact attribution)

## Business Rules and Constraints
- Facts must be between 1 and 500 characters
- Only fact owners can edit or delete their facts
- Deleted facts are soft-deleted to maintain referential integrity
- All fact modifications are logged in edit history
- Facts are immediately visible to community upon creation
- Character count validation occurs in real-time during input
- Edit history preserves previous versions for audit purposes

## Error Handling
- **FactNotFound**: When requested fact doesn't exist or is deleted
- **ContentTooLong**: When fact content exceeds 500 characters
- **ContentEmpty**: When fact content is empty or only whitespace
- **UnauthorizedEdit**: When user tries to edit fact they don't own
- **UnauthorizedDelete**: When user tries to delete fact they don't own
- **FactAlreadyDeleted**: When operation attempted on deleted fact

## Content Validation Rules
- **Length**: 1-500 characters (excluding leading/trailing whitespace)
- **Content**: Basic HTML sanitization to prevent XSS
- **Encoding**: UTF-8 support for international characters
- **Formatting**: Preserve line breaks and basic formatting

## Soft Delete Implementation
- Facts marked as `is_deleted = true` instead of physical deletion
- Deleted facts excluded from public queries but preserved for data integrity
- Related votes, comments, and reports remain linked to deleted facts
- Admin users can view deleted facts for moderation purposes

## Integration Points
- **Resource Component**: Links facts to attached URLs and images
- **Hashtag Component**: Processes and links hashtags within fact content
- **Voting Component**: Provides facts for community voting
- **Comment Component**: Enables commenting on facts
- **Report Component**: Allows reporting of inappropriate facts
- **User Profile Component**: Displays facts on user profile pages
- **Admin Dashboard**: Provides fact management and statistics

