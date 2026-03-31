# Voting Component

## Purpose and Responsibilities
The Voting Component manages all voting functionality in the application, including fact voting (Fact/Fake) and comment voting (Upvote/Downvote). It handles vote creation, updates, retrieval, and provides voting statistics and analytics.

## Attributes and Data Models

### FactVote Entity
```
FactVote {
  id: UUID (Primary Key)
  fact_id: UUID (Foreign Key to Fact)
  user_id: UUID (Foreign Key to User)
  vote_type: Enum ('fact', 'fake')
  created_at: DateTime
  updated_at: DateTime
}
```

### CommentVote Entity
```
CommentVote {
  id: UUID (Primary Key)
  comment_id: UUID (Foreign Key to Comment)
  user_id: UUID (Foreign Key to User)
  vote_type: Enum ('upvote', 'downvote')
  created_at: DateTime
  updated_at: DateTime
}
```

### VoteStatistics Entity
```
VoteStatistics {
  id: UUID (Primary Key)
  content_type: Enum ('fact', 'comment')
  content_id: UUID
  total_votes: Integer (Default: 0)
  positive_votes: Integer (Default: 0)
  negative_votes: Integer (Default: 0)
  vote_score: Float (Calculated field)
  last_updated: DateTime
}
```

## Behaviors and Methods

### Fact Voting Methods
- **voteOnFact(factId, userId, voteType)**: Records or updates fact vote
- **removeFactVote(factId, userId)**: Removes user's vote on fact
- **getFactVote(factId, userId)**: Gets user's current vote on fact
- **getFactVoteStats(factId)**: Returns vote counts and percentages for fact
- **canUserVoteOnFact(factId, userId)**: Checks if user can vote (not own fact)

### Comment Voting Methods
- **voteOnComment(commentId, userId, voteType)**: Records or updates comment vote
- **removeCommentVote(commentId, userId)**: Removes user's vote on comment
- **getCommentVote(commentId, userId)**: Gets user's current vote on comment
- **getCommentVoteScore(commentId)**: Returns net score (upvotes - downvotes)
- **canUserVoteOnComment(commentId, userId)**: Checks if user can vote (not own comment)

### Vote Management Methods
- **changeVote(voteId, newVoteType)**: Changes existing vote to different type
- **getUserVotingHistory(userId, limit, offset)**: Gets user's voting activity
- **getVotesForContent(contentType, contentId)**: Gets all votes for specific content
- **updateVoteStatistics(contentType, contentId)**: Recalculates vote statistics

### Analytics Methods
- **getVotingTrends(period)**: Analyzes voting patterns over time
- **getUserVotingStats(userId)**: Gets user's voting statistics
- **getContentEngagement(contentId, contentType)**: Gets engagement metrics
- **calculateVoteReliability(userId)**: Analyzes user's voting consistency

## Interfaces Provided
- **FactVotingService**: Interface for fact voting operations
- **CommentVotingService**: Interface for comment voting operations
- **VotingAnalyticsService**: Interface for voting statistics and trends

## Interfaces Required
- **AuthenticationService**: For user session validation
- **DatabaseService**: For vote data persistence
- **FactRetrievalService**: For validating fact existence and ownership
- **CommentRetrievalService**: For validating comment existence and ownership
- **NotificationService**: For notifying content owners of votes

## Dependencies and Relationships
- **Depends on**: User Authentication Component, Fact Component, Comment Component
- **Used by**: UI Framework Component, Analytics Component
- **Integrates with**: Notification Component (for vote notifications)

## Business Rules and Constraints
- Users cannot vote on their own facts or comments
- Each user can only vote once per fact/comment
- Users can change their vote (from Fact to Fake, or Upvote to Downvote)
- Vote changes update statistics in real-time
- Voting requires user authentication
- Votes are permanent records (soft delete only)
- Vote statistics are cached for performance

## Error Handling
- **CannotVoteOnOwnContent**: When user tries to vote on their own fact/comment
- **ContentNotFound**: When trying to vote on non-existent fact/comment
- **InvalidVoteType**: When vote type is not recognized
- **VoteAlreadyExists**: When trying to create duplicate vote
- **UnauthorizedVoting**: When unauthenticated user tries to vote

## Vote Type Definitions

### Fact Votes
- **'fact'**: User believes the statement is true/accurate
- **'fake'**: User believes the statement is false/inaccurate

### Comment Votes
- **'upvote'**: User finds comment helpful/valuable
- **'downvote'**: User finds comment unhelpful/inappropriate

## Vote Statistics Calculations

### Fact Vote Statistics
```
Total Votes = Fact Votes + Fake Votes
Fact Percentage = (Fact Votes / Total Votes) * 100
Fake Percentage = (Fake Votes / Total Votes) * 100
Credibility Score = (Fact Votes - Fake Votes) / Total Votes
```

### Comment Vote Statistics
```
Vote Score = Upvotes - Downvotes
Engagement Score = Total Votes (Upvotes + Downvotes)
Helpfulness Ratio = Upvotes / Total Votes
```

## Integration Points
- **Fact Component**: Validates fact existence and ownership for voting
- **Comment Component**: Validates comment existence and ownership for voting
- **User Authentication Component**: Validates user sessions and permissions
- **UI Framework Component**: Displays vote buttons and statistics
- **Notification Component**: Sends notifications for significant vote milestones
- **Analytics Component**: Provides voting data for trend analysis


## Security Considerations
- Validate user ownership before allowing votes
- Prevent vote manipulation through session validation

## Display Features
- **Vote Buttons**: Clear visual indicators for voting options
- **Vote Counts**: Display current vote statistics
- **User Vote State**: Show user's current vote with different styling
- **Vote Percentages**: Visual representation of vote distribution
- **Vote History**: Timeline of user's voting activity

