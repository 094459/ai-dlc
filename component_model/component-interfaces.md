# Component Interfaces and APIs

## Overview
This document defines the interfaces and APIs between all components in the Fact Checker application. It establishes the contracts that components use to communicate with each other, ensuring loose coupling and clear separation of concerns.

## Interface Categories

### 1. Authentication and Authorization Interfaces

#### AuthenticationService (Provided by User Authentication Component)
```typescript
interface AuthenticationService {
  registerUser(email: string, password: string): Promise<User>
  authenticateUser(email: string, password: string): Promise<UserSession>
  validateSession(sessionToken: string): Promise<User | null>
  logoutUser(sessionToken: string): Promise<void>
  createSession(userId: string): Promise<UserSession>
  cleanupExpiredSessions(): Promise<void>
}
```

#### AuthorizationService (Provided by Security Component)
```typescript
interface AuthorizationService {
  checkPermission(userId: string, resource: string, action: string): Promise<boolean>
  getUserRoles(userId: string): Promise<UserRole[]>
  getUserPermissions(userId: string): Promise<Permission[]>
  assignRole(userId: string, roleName: string, grantedBy: string): Promise<void>
  revokeRole(userId: string, roleName: string, revokedBy: string): Promise<void>
}
```

### 2. User Management Interfaces

#### ProfileManagementService (Provided by User Profile Component)
```typescript
interface ProfileManagementService {
  createProfile(userId: string, name: string, biography?: string, profilePhoto?: File): Promise<UserProfile>
  updateProfile(userId: string, name: string, biography?: string, profilePhoto?: File): Promise<UserProfile>
  getProfile(userId: string): Promise<UserProfile | null>
  getPublicProfile(userId: string): Promise<PublicProfile>
  deleteProfile(userId: string): Promise<void>
}
```

#### ProfilePhotoService (Provided by User Profile Component)
```typescript
interface ProfilePhotoService {
  uploadProfilePhoto(userId: string, photoFile: File): Promise<string>
  deleteProfilePhoto(userId: string): Promise<void>
  getDefaultPhotoUrl(): string
  validatePhotoFile(file: File): Promise<boolean>
}
```

### 3. Content Management Interfaces

#### FactManagementService (Provided by Fact Component)
```typescript
interface FactManagementService {
  createFact(userId: string, content: string, resources?: Resource[], hashtags?: string[]): Promise<Fact>
  updateFact(factId: string, userId: string, content: string, resources?: Resource[], hashtags?: string[]): Promise<Fact>
  deleteFact(factId: string, userId: string): Promise<void>
  getFact(factId: string): Promise<Fact | null>
  getFactsByUser(userId: string, limit?: number, offset?: number): Promise<Fact[]>
  getAllFacts(limit?: number, offset?: number): Promise<Fact[]>
}
```

#### FactRetrievalService (Provided by Fact Component)
```typescript
interface FactRetrievalService {
  searchFacts(query: string): Promise<Fact[]>
  getFactsByHashtag(hashtag: string): Promise<Fact[]>
  getFactsWithResources(): Promise<Fact[]>
  getRecentFacts(limit: number): Promise<Fact[]>
  getFactEngagementStats(factId: string): Promise<EngagementStats>
}
```

#### ResourceManagementService (Provided by Resource Component)
```typescript
interface ResourceManagementService {
  addResourceToFact(factId: string, resourceType: ResourceType, resourceValue: string): Promise<FactResource>
  removeResourceFromFact(resourceId: string, userId: string): Promise<void>
  getResourcesByFact(factId: string): Promise<FactResource[]>
  validateUrlFormat(url: string): Promise<boolean>
  uploadImageResource(factId: string, imageFile: File): Promise<FactResource>
}
```

#### HashtagProcessingService (Provided by Hashtag Component)
```typescript
interface HashtagProcessingService {
  parseHashtagsFromText(content: string): string[]
  createOrGetHashtag(tagName: string): Promise<Hashtag>
  linkHashtagsToFact(factId: string, hashtags: string[]): Promise<void>
  getFactsByHashtag(hashtagName: string, limit?: number, offset?: number): Promise<Fact[]>
  getPopularHashtags(limit: number): Promise<Hashtag[]>
}
```

### 4. Community Interaction Interfaces

#### VotingService (Provided by Voting Component)
```typescript
interface VotingService {
  voteOnFact(factId: string, userId: string, voteType: FactVoteType): Promise<FactVote>
  voteOnComment(commentId: string, userId: string, voteType: CommentVoteType): Promise<CommentVote>
  removeFactVote(factId: string, userId: string): Promise<void>
  removeCommentVote(commentId: string, userId: string): Promise<void>
  getFactVoteStats(factId: string): Promise<VoteStatistics>
  getCommentVoteScore(commentId: string): Promise<number>
}
```

#### CommentManagementService (Provided by Comment Component)
```typescript
interface CommentManagementService {
  createComment(factId: string, userId: string, content: string, parentCommentId?: string): Promise<Comment>
  updateComment(commentId: string, userId: string, content: string): Promise<Comment>
  deleteComment(commentId: string, userId: string): Promise<void>
  getComment(commentId: string): Promise<Comment | null>
  getCommentsByFact(factId: string, limit?: number, offset?: number): Promise<Comment[]>
}
```

#### ThreadManagementService (Provided by Thread Management Component)
```typescript
interface ThreadManagementService {
  organizeThreadsForFact(factId: string, sortCriteria: SortCriteria): Promise<ThreadStructure>
  collapseThread(threadId: string, userId: string): Promise<void>
  expandThread(threadId: string, userId: string): Promise<void>
  getThreadState(threadId: string, userId: string): Promise<ThreadState>
  renderThreadForDisplay(threadId: string, userId: string): Promise<ThreadDisplayData>
}
```

### 5. Moderation Interfaces

#### ReportManagementService (Provided by Report Component)
```typescript
interface ReportManagementService {
  createReport(reporterUserId: string, contentType: ContentType, contentId: string, reasonId: string, description?: string): Promise<Report>
  getReportQueue(moderatorId: string, status?: ReportStatus, priority?: Priority): Promise<Report[]>
  updateReportStatus(reportId: string, status: ReportStatus, moderatorId: string): Promise<void>
  getReportsByContent(contentType: ContentType, contentId: string): Promise<Report[]>
}
```

#### ModerationService (Provided by Moderation Component)
```typescript
interface ModerationService {
  removeContent(moderatorId: string, contentType: ContentType, contentId: string, reason: string): Promise<ModerationAction>
  restoreContent(moderatorId: string, contentType: ContentType, contentId: string, reason: string): Promise<ModerationAction>
  warnUser(moderatorId: string, userId: string, reason: string): Promise<ModerationAction>
  suspendUser(moderatorId: string, userId: string, duration: number, reason: string): Promise<ModerationAction>
  banUser(moderatorId: string, userId: string, reason: string): Promise<ModerationAction>
}
```

### 6. Infrastructure Interfaces

#### UIRenderingService (Provided by UI Framework Component)
```typescript
interface UIRenderingService {
  renderFactCard(factData: Fact, userVote?: Vote, canEdit?: boolean): Promise<HTMLElement>
  renderCommentThread(comments: Comment[], threadState: ThreadState, userPreferences: UserPreferences): Promise<HTMLElement>
  renderVotingButtons(contentType: ContentType, contentId: string, userVote?: Vote): Promise<HTMLElement>
  renderUserProfile(userData: User, isOwnProfile: boolean): Promise<HTMLElement>
  applyTheme(themeId: string, userId: string): Promise<void>
}
```

#### NotificationService (Provided by Notification Component)
```typescript
interface NotificationService {
  createNotification(userId: string, type: NotificationType, title: string, message: string, actionUrl?: string): Promise<Notification>
  sendInAppNotification(notificationId: string): Promise<void>
  sendEmailNotification(notificationId: string): Promise<void>
  getUserNotifications(userId: string, limit?: number, offset?: number, unreadOnly?: boolean): Promise<Notification[]>
  markNotificationAsRead(notificationId: string, userId: string): Promise<void>
}
```

#### AnalyticsService (Provided by Analytics Component)
```typescript
interface AnalyticsService {
  trackEvent(eventType: string, userId?: string, eventData?: any, context?: any): Promise<void>
  getUserEngagementMetrics(userId: string, period: TimePeriod): Promise<UserMetrics>
  getContentPerformance(contentType: ContentType, contentId: string): Promise<ContentMetrics>
  getSystemPerformanceMetrics(period: TimePeriod): Promise<SystemMetrics>
  generateDashboardData(adminId: string, widgets: string[]): Promise<DashboardData>
}
```

### 7. Security Interfaces

#### ValidationService (Provided by Security Component)
```typescript
interface ValidationService {
  validateInput(input: string, validationType: ValidationType): Promise<ValidationResult>
  sanitizeHtml(content: string): string
  validateEmail(email: string): boolean
  validateUrl(url: string): Promise<boolean>
  escapeOutput(content: string, context: OutputContext): string
}
```

#### AuditService (Provided by Security Component)
```typescript
interface AuditService {
  logUserAction(userId: string, action: string, resourceType?: string, resourceId?: string, details?: any): Promise<void>
  logSystemEvent(event: string, severity: Severity, details?: any): Promise<void>
  logSecurityEvent(eventType: SecurityEventType, userId?: string, ipAddress?: string, details?: any): Promise<void>
  getAuditTrail(resourceType: string, resourceId: string, limit?: number): Promise<AuditLog[]>
}
```

## Error Handling Standards

### Standard Error Response Format
```typescript
interface APIError {
  code: string
  message: string
  details?: any
  timestamp: string
  requestId: string
}
```

### Common Error Codes
- `UNAUTHORIZED`: User lacks permission for action
- `NOT_FOUND`: Requested resource doesn't exist
- `VALIDATION_ERROR`: Input validation failed
- `RATE_LIMIT_EXCEEDED`: User exceeded allowed action rate
- `INTERNAL_ERROR`: Unexpected system error
- `SERVICE_UNAVAILABLE`: Dependent service is unavailable

## Data Transfer Objects (DTOs)

### User DTOs
```typescript
interface UserDTO {
  id: string
  email: string
  name?: string
  profilePhotoUrl?: string
  createdAt: string
}

interface PublicProfileDTO {
  id: string
  name: string
  biography?: string
  profilePhotoUrl?: string
  factsCount: number
  joinedAt: string
}
```

### Content DTOs
```typescript
interface FactDTO {
  id: string
  userId: string
  content: string
  resources: ResourceDTO[]
  hashtags: string[]
  voteStats: VoteStatsDTO
  commentCount: number
  createdAt: string
  updatedAt: string
}

interface CommentDTO {
  id: string
  factId: string
  userId: string
  parentCommentId?: string
  content: string
  nestingLevel: number
  voteScore: number
  replyCount: number
  createdAt: string
}
```

## Interface Dependencies Map

```
User Authentication Component
├── Provides: AuthenticationService
├── Requires: DatabaseService, SecurityService
└── Used by: All components requiring authentication

User Profile Component
├── Provides: ProfileManagementService, ProfilePhotoService
├── Requires: AuthenticationService, FileStorageService
└── Used by: UI Framework, Admin Dashboard

Fact Component
├── Provides: FactManagementService, FactRetrievalService
├── Requires: AuthenticationService, ResourceService, HashtagService
└── Used by: Voting, Comment, UI Framework

Voting Component
├── Provides: VotingService
├── Requires: AuthenticationService, FactRetrievalService, CommentRetrievalService
└── Used by: UI Framework, Analytics

Comment Component
├── Provides: CommentManagementService
├── Requires: AuthenticationService, FactRetrievalService
└── Used by: Voting, Thread Management, UI Framework

Security Component
├── Provides: AuthorizationService, ValidationService, AuditService
├── Requires: DatabaseService, UserRetrievalService
└── Used by: All components requiring security services
```
