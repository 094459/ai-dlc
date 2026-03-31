# Hashtag Component

## Purpose and Responsibilities
The Hashtag Component manages hashtag functionality for fact categorization and discovery. It handles hashtag parsing, storage, linking, and provides hashtag-based filtering and search capabilities.

## Attributes and Data Models

### Hashtag Entity
```
Hashtag {
  id: UUID (Primary Key)
  tag_name: String (Unique, Case-insensitive)
  normalized_name: String (Lowercase version for matching)
  created_at: DateTime
  usage_count: Integer (Default: 0)
  last_used: DateTime
}
```

### FactHashtag Entity (Many-to-Many Relationship)
```
FactHashtag {
  id: UUID (Primary Key)
  fact_id: UUID (Foreign Key to Fact)
  hashtag_id: UUID (Foreign Key to Hashtag)
  created_at: DateTime
}
```

### HashtagTrend Entity
```
HashtagTrend {
  id: UUID (Primary Key)
  hashtag_id: UUID (Foreign Key to Hashtag)
  period_start: DateTime
  period_end: DateTime
  usage_count: Integer
  trend_score: Float
}
```

## Behaviors and Methods

### Hashtag Processing Methods
- **parseHashtagsFromText(content)**: Extracts hashtags from fact content
- **createOrGetHashtag(tagName)**: Creates new hashtag or returns existing
- **linkHashtagsToFact(factId, hashtags)**: Associates hashtags with fact
- **removeHashtagsFromFact(factId)**: Removes all hashtag associations from fact
- **normalizeHashtagName(tagName)**: Converts hashtag to normalized form

### Hashtag Retrieval Methods
- **getHashtagById(hashtagId)**: Retrieves specific hashtag details
- **getHashtagByName(tagName)**: Finds hashtag by name (case-insensitive)
- **getHashtagsForFact(factId)**: Gets all hashtags associated with fact
- **getPopularHashtags(limit)**: Returns most frequently used hashtags
- **getTrendingHashtags(period)**: Gets hashtags trending in time period

### Fact Discovery Methods
- **getFactsByHashtag(hashtagName, limit, offset)**: Retrieves facts with specific hashtag
- **searchHashtags(query)**: Searches hashtags by partial name match
- **getRelatedHashtags(hashtagName)**: Finds hashtags commonly used together
- **getHashtagSuggestions(partialName)**: Provides autocomplete suggestions

### Analytics Methods
- **updateHashtagUsageCount(hashtagId)**: Increments usage counter
- **calculateHashtagTrends(period)**: Analyzes hashtag usage trends
- **getHashtagStatistics(hashtagId)**: Returns usage stats for hashtag
- **cleanupUnusedHashtags()**: Removes hashtags with zero usage

## Interfaces Provided
- **HashtagProcessingService**: Interface for hashtag parsing and creation
- **HashtagDiscoveryService**: Interface for hashtag-based fact filtering
- **HashtagAnalyticsService**: Interface for hashtag statistics and trends

## Interfaces Required
- **DatabaseService**: For hashtag data persistence
- **FactRetrievalService**: For getting facts associated with hashtags
- **TextProcessingService**: For hashtag parsing and normalization

## Dependencies and Relationships
- **Depends on**: Fact Component, Text Processing utilities
- **Used by**: UI Framework Component, Analytics Component
- **Integrates with**: Fact Component (hashtags belong to facts)

## Business Rules and Constraints
- Hashtags are optional for fact submission
- Hashtags must start with # symbol
- Hashtag names are case-insensitive for matching but preserve original case
- Maximum 3 hashtags per fact (configurable)
- Hashtag names must be 1-50 characters (excluding #)
- Hashtags can contain letters, numbers, and underscores only
- Hashtags are clickable and lead to filtered fact views

## Error Handling
- **InvalidHashtagFormat**: When hashtag doesn't follow required format
- **HashtagTooLong**: When hashtag exceeds character limit
- **TooManyHashtags**: When fact exceeds maximum hashtag limit
- **HashtagNotFound**: When requested hashtag doesn't exist
- **InvalidCharacters**: When hashtag contains unsupported characters

## Hashtag Parsing Rules
- **Pattern**: `#[a-zA-Z0-9_]{1,50}`
- **Case Handling**: Preserve original case for display, normalize for matching
- **Duplicate Handling**: Remove duplicate hashtags within same fact
- **Position**: Hashtags can appear anywhere in fact content
- **Formatting**: Hashtags are automatically made clickable in display

## Hashtag Normalization
- Convert to lowercase for database storage and matching
- Remove special characters except underscores
- Trim whitespace
- Validate length constraints
- Check for reserved words or inappropriate content

## Trending Algorithm
```
Trend Score = (Recent Usage / Historical Average) * Recency Weight
Where:
- Recent Usage = hashtag usage in last 24 hours
- Historical Average = average daily usage over last 30 days
- Recency Weight = higher weight for more recent usage
```

## Integration Points
- **Fact Component**: Hashtags are extracted from and linked to facts
- **UI Framework Component**: Renders clickable hashtags and hashtag pages
- **Search Component**: Provides hashtag-based fact filtering
- **Analytics Component**: Tracks hashtag usage and trends
- **Admin Dashboard**: Provides hashtag management and moderation

## Display Formatting
- **In Fact Content**: Hashtags highlighted with different color/style
- **Clickable Links**: Hashtags link to filtered fact views
- **Hashtag Pages**: Show all facts containing specific hashtag
- **Popular Tags**: Display trending hashtags in sidebar or footer

## Moderation Features
- **Inappropriate Hashtags**: Ability to block or hide certain hashtags
- **Content Filtering**: Remove hashtags from reported/moderated facts

## Analytics and Insights
- **Usage Statistics**: Track hashtag popularity over time
- **Trend Analysis**: Identify emerging topics and discussions
- **User Behavior**: Analyze how users discover content via hashtags
- **Content Categorization**: Understand fact distribution across topics
