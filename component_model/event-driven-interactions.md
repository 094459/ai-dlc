# Event-Driven Interactions and Notifications

## Overview
This document defines the event-driven architecture for the Fact Checker application, including event types, publishers, subscribers, and notification flows. This approach enables loose coupling between components and supports scalable, asynchronous processing.

## Event Architecture Pattern

### Event-Driven Flow
```
Event Source → Event Publisher → Event Bus → Event Handlers → Target Components
```

### Event Processing Models
1. **Fire-and-Forget**: Events published without expecting response
2. **Request-Response**: Events that expect acknowledgment
3. **Publish-Subscribe**: Multiple subscribers for single event type
4. **Event Sourcing**: Events as source of truth for state changes

## Core Event Types

### 1. User Events

#### UserRegistered Event
```typescript
interface UserRegisteredEvent {
  eventType: 'user.registered'
  eventId: string
  timestamp: string
  userId: string
  email: string
  registrationSource: string
}
```
- **Publisher**: User Authentication Component
- **Subscribers**: Analytics Component, Notification Component
- **Actions**: Track registration, send welcome notification

#### UserLoggedIn Event
```typescript
interface UserLoggedInEvent {
  eventType: 'user.logged_in'
  eventId: string
  timestamp: string
  userId: string
  sessionId: string
  ipAddress: string
  userAgent: string
}
```
- **Publisher**: User Authentication Component
- **Subscribers**: Analytics Component, Security Component
- **Actions**: Track login activity, monitor security

#### UserProfileUpdated Event
```typescript
interface UserProfileUpdatedEvent {
  eventType: 'user.profile_updated'
  eventId: string
  timestamp: string
  userId: string
  updatedFields: string[]
  previousValues: Record<string, any>
  newValues: Record<string, any>
}
```
- **Publisher**: User Profile Component
- **Subscribers**: Analytics Component, UI Framework Component
- **Actions**: Track profile changes, invalidate cache

### 2. Content Events

#### FactCreated Event
```typescript
interface FactCreatedEvent {
  eventType: 'fact.created'
  eventId: string
  timestamp: string
  factId: string
  userId: string
  content: string
  hashtags: string[]
  resourceCount: number
}
```
- **Publisher**: Fact Component
- **Subscribers**: Analytics Component, Notification Component, Hashtag Component
- **Actions**: Track content creation, update hashtag usage, notify followers

#### FactUpdated Event
```typescript
interface FactUpdatedEvent {
  eventType: 'fact.updated'
  eventId: string
  timestamp: string
  factId: string
  userId: string
  previousContent: string
  newContent: string
  editReason?: string
}
```
- **Publisher**: Fact Component
- **Subscribers**: Analytics Component, Security Component
- **Actions**: Track edits, audit changes

#### FactDeleted Event
```typescript
interface FactDeletedEvent {
  eventType: 'fact.deleted'
  eventId: string
  timestamp: string
  factId: string
  userId: string
  deletionReason?: string
}
```
- **Publisher**: Fact Component
- **Subscribers**: Analytics Component, Voting Component, Comment Component
- **Actions**: Update statistics, clean up related data

### 3. Interaction Events

#### VoteCast Event
```typescript
interface VoteCastEvent {
  eventType: 'vote.cast'
  eventId: string
  timestamp: string
  voteId: string
  userId: string
  contentType: 'fact' | 'comment'
  contentId: string
  voteType: string
  previousVote?: string
}
```
- **Publisher**: Voting Component
- **Subscribers**: Analytics Component, Notification Component
- **Actions**: Track engagement, notify content owner

#### CommentCreated Event
```typescript
interface CommentCreatedEvent {
  eventType: 'comment.created'
  eventId: string
  timestamp: string
  commentId: string
  factId: string
  userId: string
  parentCommentId?: string
  content: string
  nestingLevel: number
}
```
- **Publisher**: Comment Component
- **Subscribers**: Analytics Component, Notification Component, Thread Management Component
- **Actions**: Track engagement, notify fact/comment owner, update thread structure

#### CommentDeleted Event
```typescript
interface CommentDeletedEvent {
  eventType: 'comment.deleted'
  eventId: string
  timestamp: string
  commentId: string
  factId: string
  userId: string
  deletionReason?: string
}
```
- **Publisher**: Comment Component
- **Subscribers**: Analytics Component, Thread Management Component
- **Actions**: Update statistics, restructure threads

### 4. Moderation Events

#### ContentReported Event
```typescript
interface ContentReportedEvent {
  eventType: 'content.reported'
  eventId: string
  timestamp: string
  reportId: string
  reporterUserId: string
  contentType: 'fact' | 'comment'
  contentId: string
  reasonId: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
}
```
- **Publisher**: Report Component
- **Subscribers**: Analytics Component, Notification Component, Moderation Component
- **Actions**: Track reports, alert moderators, queue for review

#### ModerationActionTaken Event
```typescript
interface ModerationActionTakenEvent {
  eventType: 'moderation.action_taken'
  eventId: string
  timestamp: string
  actionId: string
  moderatorId: string
  targetType: 'fact' | 'comment' | 'user'
  targetId: string
  actionType: 'remove' | 'restore' | 'warn' | 'suspend' | 'ban'
  reason: string
  relatedReportId?: string
}
```
- **Publisher**: Moderation Component
- **Subscribers**: Analytics Component, Notification Component, Security Component
- **Actions**: Track moderation, notify affected user, audit action

### 5. System Events

#### SystemMaintenanceScheduled Event
```typescript
interface SystemMaintenanceScheduledEvent {
  eventType: 'system.maintenance_scheduled'
  eventId: string
  timestamp: string
  maintenanceStart: string
  maintenanceEnd: string
  affectedServices: string[]
  description: string
}
```
- **Publisher**: Admin Dashboard Component
- **Subscribers**: Notification Component, UI Framework Component
- **Actions**: Notify all users, display maintenance banner

#### SecurityThreatDetected Event
```typescript
interface SecurityThreatDetectedEvent {
  eventType: 'security.threat_detected'
  eventId: string
  timestamp: string
  threatType: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  affectedUserId?: string
  ipAddress?: string
  details: Record<string, any>
}
```
- **Publisher**: Security Component
- **Subscribers**: Notification Component, Admin Dashboard Component
- **Actions**: Alert administrators, trigger security measures

## Event Handlers and Subscribers

### Analytics Event Handler
Subscribes to all events for comprehensive analytics:
```typescript
class AnalyticsEventHandler {
  handleUserRegistered(event: UserRegisteredEvent): void
  handleFactCreated(event: FactCreatedEvent): void
  handleVoteCast(event: VoteCastEvent): void
  handleCommentCreated(event: CommentCreatedEvent): void
  handleContentReported(event: ContentReportedEvent): void
  handleModerationActionTaken(event: ModerationActionTakenEvent): void
}
```

### Notification Event Handler
Handles events that trigger user notifications:
```typescript
class NotificationEventHandler {
  handleUserRegistered(event: UserRegisteredEvent): void
  handleVoteCast(event: VoteCastEvent): void
  handleCommentCreated(event: CommentCreatedEvent): void
  handleContentReported(event: ContentReportedEvent): void
  handleModerationActionTaken(event: ModerationActionTakenEvent): void
  handleSystemMaintenanceScheduled(event: SystemMaintenanceScheduledEvent): void
}
```

### Security Event Handler
Monitors security-related events:
```typescript
class SecurityEventHandler {
  handleUserLoggedIn(event: UserLoggedInEvent): void
  handleFactUpdated(event: FactUpdatedEvent): void
  handleModerationActionTaken(event: ModerationActionTakenEvent): void
  handleSecurityThreatDetected(event: SecurityThreatDetectedEvent): void
}
```

## Notification Triggers and Rules

### User Interaction Notifications

#### Vote Notifications
- **Trigger**: VoteCast event where content owner ≠ voter
- **Recipients**: Content owner
- **Conditions**: User has vote notifications enabled
- **Template**: "Someone voted on your {contentType}"
- **Delivery**: In-app notification

#### Comment Notifications
- **Trigger**: CommentCreated event
- **Recipients**: 
  - Fact owner (if commenting on fact)
  - Parent comment owner (if replying to comment)
- **Conditions**: Recipients have comment notifications enabled
- **Template**: "{User} commented on your {contentType}"
- **Delivery**: In-app notification

#### Reply Notifications
- **Trigger**: CommentCreated event with parentCommentId
- **Recipients**: Parent comment owner
- **Conditions**: User has reply notifications enabled
- **Template**: "{User} replied to your comment"
- **Delivery**: In-app notification

### Moderation Notifications

#### Content Removed Notification
- **Trigger**: ModerationActionTaken event with actionType 'remove'
- **Recipients**: Content owner
- **Conditions**: Always sent (cannot be disabled)
- **Template**: "Your {contentType} has been removed"
- **Delivery**: In-app notification

#### Account Warning Notification
- **Trigger**: ModerationActionTaken event with actionType 'warn'
- **Recipients**: Warned user
- **Conditions**: Always sent (cannot be disabled)
- **Template**: "You have received a warning"
- **Delivery**: In-app notification

#### Account Suspension Notification
- **Trigger**: ModerationActionTaken event with actionType 'suspend'
- **Recipients**: Suspended user
- **Conditions**: Always sent (cannot be disabled)
- **Template**: "Your account has been suspended"
- **Delivery**: In-app splash screen

#### Report Resolution Notification
- **Trigger**: ModerationActionTaken event with relatedReportId
- **Recipients**: Report submitter
- **Conditions**: User has report resolution notifications enabled
- **Template**: "Your report has been resolved"
- **Delivery**: In-app notification

### System Notifications

#### Welcome Notification
- **Trigger**: UserRegistered event
- **Recipients**: New user
- **Conditions**: Always sent
- **Template**: "Welcome to Fact Checker!"
- **Delivery**: In-app notification

#### Maintenance Notification
- **Trigger**: SystemMaintenanceScheduled event
- **Recipients**: All active users
- **Conditions**: Always sent (cannot be disabled)
- **Template**: "Scheduled maintenance: {description}"
- **Delivery**: In-app notification


## Event Reliability and Error Handling

### Error Handling Strategies
```typescript
interface EventHandler {
  handle(event: Event): Promise<void>
  handleError(event: Event, error: Error): Promise<void>
  shouldRetry(error: Error): boolean
  getRetryDelay(attemptNumber: number): number
}
```

### Event Monitoring
- **Processing time tracking**: Monitor event handler performance
- **Error rate monitoring**: Track failed event processing
- **Queue depth monitoring**: Monitor event backlog
- **Dead letter queue alerts**: Alert on failed events

## Event Storage and Audit

### Event Store Schema
```typescript
interface StoredEvent {
  eventId: string
  eventType: string
  timestamp: string
  payload: any
  metadata: {
    source: string
    version: string
    correlationId?: string
  }
  processingStatus: 'pending' | 'processed' | 'failed'
  processedAt?: string
  errorMessage?: string
  retryCount: number
}
```

## Performance Considerations

## Security in Event Processing

