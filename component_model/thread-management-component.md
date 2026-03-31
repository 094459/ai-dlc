# Thread Management Component

## Purpose and Responsibilities
The Thread Management Component handles the organization, display, and user interaction with comment threads. It manages thread collapse/expand functionality, thread navigation, and provides optimized thread rendering for the user interface.

## Attributes and Data Models

### ThreadState Entity
```
ThreadState {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to User)
  thread_id: UUID (Foreign Key to CommentThread)
  is_collapsed: Boolean (Default: false)
  last_viewed: DateTime
  created_at: DateTime
  updated_at: DateTime
}
```

### ThreadMetadata Entity
```
ThreadMetadata {
  id: UUID (Primary Key)
  thread_id: UUID (Foreign Key to CommentThread)
  depth: Integer (Maximum nesting level in thread)
  total_participants: Integer
  last_activity: DateTime
  activity_score: Float (Calculated engagement metric)
  is_hot: Boolean (Trending thread indicator)
}
```

### ThreadNavigation Entity
```
ThreadNavigation {
  id: UUID (Primary Key)
  fact_id: UUID (Foreign Key to Fact)
  thread_order: Integer (Display order)
  sort_criteria: Enum ('chronological', 'popular', 'recent_activity')
  updated_at: DateTime
}
```

## Behaviors and Methods

### Thread Organization Methods
- **organizeThreadsForFact(factId, sortCriteria)**: Organizes all threads for display
- **buildThreadHierarchy(rootCommentId)**: Constructs complete thread structure
- **calculateThreadDepth(threadId)**: Determines maximum nesting level in thread
- **getThreadParticipants(threadId)**: Gets list of users who participated in thread
- **updateThreadActivity(threadId)**: Updates last activity timestamp

### Thread State Management Methods
- **collapseThread(threadId, userId)**: Collapses thread for specific user
- **expandThread(threadId, userId)**: Expands thread for specific user
- **getThreadState(threadId, userId)**: Gets user's thread collapse/expand state
- **toggleThreadState(threadId, userId)**: Toggles between collapsed/expanded
- **resetThreadStates(userId)**: Resets all thread states for user

### Thread Display Methods
- **renderThreadForDisplay(threadId, userId)**: Prepares thread data for UI rendering
- **getCollapsedThreadSummary(threadId)**: Gets summary info for collapsed threads
- **formatThreadHierarchy(threadData)**: Formats thread data with proper indentation
- **getThreadNavigationData(factId)**: Gets thread list with navigation metadata

### Thread Analytics Methods
- **calculateThreadEngagement(threadId)**: Computes engagement metrics for thread
- **identifyHotThreads(factId)**: Finds threads with high recent activity
- **getThreadStatistics(threadId)**: Returns comprehensive thread statistics
- **updateThreadPopularity(threadId)**: Updates popularity scores based on activity

## Interfaces Provided
- **ThreadOrganizationService**: Interface for thread structure management
- **ThreadStateService**: Interface for user thread preferences
- **ThreadDisplayService**: Interface for thread rendering and formatting

## Interfaces Required
- **CommentRetrievalService**: For getting comment data within threads
- **UserAuthenticationService**: For user session validation
- **DatabaseService**: For thread state persistence
- **VotingAnalyticsService**: For thread engagement calculations

## Dependencies and Relationships
- **Depends on**: Comment Component, User Authentication Component
- **Used by**: UI Framework Component
- **Integrates with**: Voting Component (for thread popularity), Analytics Component

## Business Rules and Constraints
- Thread collapse state is per-user (different users can have different states)
- Maximum thread depth is 3 levels (enforced by Comment Component)
- Thread states persist during user session
- Collapsed threads show summary with comment count
- Thread ordering can be customized (chronological, popular, recent activity)
- Hot threads are highlighted based on recent activity
- Thread navigation preserves user's current position

## Error Handling
- **ThreadNotFound**: When requested thread doesn't exist
- **InvalidThreadState**: When trying to set invalid collapse/expand state
- **UnauthorizedThreadAccess**: When user tries to access private thread data
- **ThreadDepthExceeded**: When thread structure exceeds maximum depth
- **InvalidSortCriteria**: When unsupported sort option is requested

## Thread Collapse/Expand Logic

### Collapsed Thread Display
```
[+] John Doe: "This is interesting..." (5 replies)
    └── [Show 5 more replies]
```

### Expanded Thread Display
```
[-] John Doe: "This is interesting because..."
    ├── Jane Smith: "I agree, and here's why..."
    │   └── Bob Wilson: "Actually, I think..."
    ├── Alice Brown: "But consider this..."
    └── Mike Davis: "Great point about..."
```

## Thread Sorting Algorithms

### Chronological Sort
- Orders threads by creation time of root comment
- Most recent threads appear first
- Maintains consistent ordering

### Popular Sort
- Orders by engagement metrics (votes + replies)
- Considers both quantity and quality of interactions
- Updates periodically based on new activity

### Recent Activity Sort
- Orders by timestamp of most recent activity in thread
- Brings active discussions to the top
- Encourages ongoing participation

## Thread State Persistence
- Thread states stored per user in database
- Session-based caching for performance
- Automatic cleanup of old thread states
- Default state is expanded for new threads

## Integration Points
- **Comment Component**: Gets comment data for thread construction
- **Voting Component**: Uses vote data for thread popularity calculations
- **User Authentication Component**: Validates user for thread state operations
- **UI Framework Component**: Provides formatted thread data for rendering
- **Analytics Component**: Tracks thread engagement and user behavior

## User Experience Features
- **Visual Hierarchy**: Clear indentation and styling for thread levels
- **Collapse Indicators**: Visual cues showing collapsed/expanded state
- **Thread Summaries**: Meaningful previews of collapsed content
- **Navigation Aids**: Jump to specific comments within threads
- **Activity Indicators**: Highlight threads with recent activity
- **Responsive Design**: Thread display adapts to different screen sizes

## Thread Engagement Metrics
```
Activity Score = (Recent Comments × 2) + (Recent Votes × 1) + (Unique Participants × 3)
Hot Thread Threshold = Activity Score > Average + (2 × Standard Deviation)
Engagement Rate = Total Interactions / Thread Age in Hours
```

