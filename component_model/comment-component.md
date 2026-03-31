# Comment Component

## Purpose and Responsibilities
The Comment Component manages all commenting functionality including comment creation, editing, deletion, and retrieval. It handles both top-level comments on facts and nested replies, supporting threaded discussions up to 3 levels deep.

## Attributes and Data Models

### Comment Entity
```
Comment {
  id: UUID (Primary Key)
  fact_id: UUID (Foreign Key to Fact)
  user_id: UUID (Foreign Key to User)
  parent_comment_id: UUID (Foreign Key to Comment, Optional)
  content: Text (Required, Max 250 characters)
  nesting_level: Integer (0-2, calculated field)
  created_at: DateTime
  updated_at: DateTime
  is_deleted: Boolean (Default: false)
  edit_count: Integer (Default: 0)
  reply_count: Integer (Default: 0)
}
```

### CommentEditHistory Entity
```
CommentEditHistory {
  id: UUID (Primary Key)
  comment_id: UUID (Foreign Key to Comment)
  previous_content: Text
  edited_at: DateTime
  edit_reason: String (Optional)
}
```

### CommentThread Entity
```
CommentThread {
  id: UUID (Primary Key)
  fact_id: UUID (Foreign Key to Fact)
  root_comment_id: UUID (Foreign Key to Comment)
  total_comments: Integer (Default: 1)
  last_activity: DateTime
  is_collapsed: Boolean (Default: false)
}
```

## Behaviors and Methods

### Core Comment Management Methods
- **createComment(factId, userId, content, parentCommentId)**: Creates new comment or reply
- **updateComment(commentId, userId, content)**: Updates existing comment content
- **deleteComment(commentId, userId)**: Soft deletes comment (marks as deleted)
- **getComment(commentId)**: Retrieves single comment with metadata
- **getCommentsByFact(factId, limit, offset)**: Gets paginated comments for fact
- **getCommentReplies(parentCommentId)**: Gets direct replies to comment

### Thread Management Methods
- **getCommentThread(rootCommentId)**: Retrieves complete comment thread
- **getThreadedComments(factId)**: Gets all comments organized in thread structure
- **calculateNestingLevel(parentCommentId)**: Determines nesting level for new reply
- **updateReplyCount(commentId)**: Updates reply count for parent comment
- **collapseThread(threadId, userId)**: Marks thread as collapsed for user
- **expandThread(threadId, userId)**: Marks thread as expanded for user

### Validation Methods
- **validateCommentContent(content)**: Ensures content meets requirements
- **checkCommentOwnership(commentId, userId)**: Verifies user owns comment
- **validateNestingLevel(parentCommentId)**: Ensures reply doesn't exceed max depth
- **sanitizeContent(content)**: Cleans content for safe display
- **checkCommentExists(commentId)**: Confirms comment exists and is not deleted

### Search and Filter Methods
- **searchComments(query, factId)**: Searches comments within fact
- **getCommentsByUser(userId, limit, offset)**: Gets user's comment history
- **getRecentComments(limit)**: Gets most recently created comments
- **getPopularComments(factId, limit)**: Gets highest-voted comments for fact

## Interfaces Provided
- **CommentManagementService**: Interface for comment CRUD operations
- **CommentThreadService**: Interface for threaded comment organization
- **CommentRetrievalService**: Interface for comment querying and display

## Interfaces Required
- **AuthenticationService**: For user session validation
- **DatabaseService**: For comment data persistence
- **FactRetrievalService**: For validating fact existence
- **UserProfileService**: For comment author information
- **ValidationService**: For content validation and sanitization
- **NotificationService**: For reply notifications

## Dependencies and Relationships
- **Depends on**: User Authentication Component, Fact Component, User Profile Component
- **Used by**: Voting Component, UI Framework Component, Report Component
- **Integrates with**: Thread Management Component, Notification Component

## Business Rules and Constraints
- Comments must be between 1 and 250 characters
- All users can comment on any fact (including their own)
- Comments are displayed in chronological order by default
- Nested comments limited to 3 levels deep (0, 1, 2)
- Only comment owners can edit or delete their comments
- Deleted comments show as "[deleted]" but preserve thread structure
- Character count validation occurs in real-time during input
- Edit history preserves previous versions for audit purposes

## Error Handling
- **CommentNotFound**: When requested comment doesn't exist or is deleted
- **ContentTooLong**: When comment content exceeds 250 characters
- **ContentEmpty**: When comment content is empty or only whitespace
- **UnauthorizedEdit**: When user tries to edit comment they don't own
- **UnauthorizedDelete**: When user tries to delete comment they don't own
- **MaxNestingExceeded**: When reply would exceed 3-level nesting limit
- **FactNotFound**: When trying to comment on non-existent fact

## Threading Logic

### Nesting Level Calculation
```
Level 0: Direct comments on facts (parent_comment_id = null)
Level 1: Replies to Level 0 comments
Level 2: Replies to Level 1 comments (maximum depth)
```

### Thread Structure
```
Fact
├── Comment A (Level 0)
│   ├── Reply A1 (Level 1)
│   │   ├── Reply A1a (Level 2)
│   │   └── Reply A1b (Level 2)
│   └── Reply A2 (Level 1)
└── Comment B (Level 0)
    └── Reply B1 (Level 1)
```

## Content Validation Rules
- **Length**: 1-250 characters (excluding leading/trailing whitespace)
- **Content**: Basic HTML sanitization to prevent XSS
- **Encoding**: UTF-8 support for international characters
- **Formatting**: Preserve line breaks and basic formatting
- **Links**: Auto-detect and make URLs clickable

## Soft Delete Implementation
- Comments marked as `is_deleted = true` instead of physical deletion
- Deleted comments display as "[deleted]" with preserved thread structure
- Reply functionality disabled on deleted comments
- Related votes and reports remain linked to deleted comments
- Admin users can view original content of deleted comments

## Thread Collapse/Expand Features
- Users can collapse entire comment threads to reduce visual clutter
- Collapsed threads show summary: "[X comments hidden]"
- Thread state persists during user session
- Individual user preferences for thread display
- Automatic collapse for threads with many replies

## Integration Points
- **Fact Component**: Comments belong to specific facts
- **User Profile Component**: Displays comment author information
- **Voting Component**: Enables voting on comments
- **Report Component**: Allows reporting of inappropriate comments
- **Notification Component**: Sends notifications for replies and mentions
- **UI Framework Component**: Renders threaded comment display
- **Admin Dashboard**: Provides comment moderation and statistics


## Display Features
- **Threaded Layout**: Visual indentation showing comment hierarchy
- **Author Information**: User name, profile photo, and posting date
- **Reply Buttons**: Easy access to reply functionality at each level
- **Edit/Delete Options**: Available only for comment owners
- **Vote Integration**: Display vote scores and voting buttons
- **Collapse Controls**: Expand/collapse buttons for thread management

## Notification Integration
- Notify fact author when someone comments on their fact
- Notify comment author when someone replies to their comment
- Send digest notifications for active discussions
- Alert moderators when comments are reported
- Notify users when their comments receive significant votes
