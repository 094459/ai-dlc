# Data Dictionary - Part 3: Community Interaction Tables

## Overview
This document provides detailed field descriptions for all community interaction tables including comments, voting, and thread management.

## Table: comments
**Purpose**: Threaded comments on facts with nested reply support

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for comment (UUID format) |
| fact_id | VARCHAR(36) | NOT NULL, FK to facts.id | Fact this comment belongs to |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User who wrote this comment |
| parent_comment_id | VARCHAR(36) | NULL, FK to comments.id | Parent comment for replies (NULL for top-level) |
| content | TEXT | NOT NULL | Comment text (max 250 chars at app level) |
| nesting_level | INTEGER | NOT NULL, DEFAULT 0, CHECK (0-2) | Depth of nesting (0=top, 1=reply, 2=reply to reply) |
| reply_count | INTEGER | NOT NULL, DEFAULT 0 | Number of direct replies to this comment |
| edit_count | INTEGER | NOT NULL, DEFAULT 0 | Number of times comment has been edited |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Comment creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when comment was soft deleted |

**Business Rules**:
- Maximum 3 levels of nesting (0, 1, 2)
- Content limited to 250 characters (enforced at application level)
- Users can comment on any fact (including their own)
- Deleted comments show as "[deleted]" but preserve thread structure

## Table: comment_edit_history
**Purpose**: Audit trail for all comment modifications

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for edit record (UUID format) |
| comment_id | VARCHAR(36) | NOT NULL, FK to comments.id | Comment that was edited |
| previous_content | TEXT | NOT NULL | Content before the edit |
| edit_reason | VARCHAR(500) | NULL | Optional user-provided reason for edit |
| edited_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp when edit occurred |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when record was soft deleted |

**Business Rules**:
- Every comment edit creates a history record
- Previous content preserved for transparency
- Edit reason is optional but encouraged

## Table: comment_threads
**Purpose**: Thread organization and metadata for comment management

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for thread (UUID format) |
| fact_id | VARCHAR(36) | NOT NULL, FK to facts.id | Fact this thread belongs to |
| root_comment_id | VARCHAR(36) | NOT NULL, FK to comments.id | Top-level comment that started this thread |
| total_comments | INTEGER | NOT NULL, DEFAULT 1 | Total comments in this thread (including root) |
| last_activity | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Most recent activity in thread |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Thread creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when thread was soft deleted |

**Constraints**:
- UNIQUE(fact_id, root_comment_id) - One thread per root comment per fact

**Business Rules**:
- Only created for top-level comments (nesting_level = 0)
- Total comments updated when replies are added/removed
- Last activity updated for thread sorting

## Table: fact_votes
**Purpose**: Fact/Fake voting system for facts

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for vote (UUID format) |
| fact_id | VARCHAR(36) | NOT NULL, FK to facts.id | Fact being voted on |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User casting the vote |
| vote_type | VARCHAR(10) | NOT NULL, CHECK ('fact', 'fake') | Type of vote cast |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Vote creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp (vote changes) |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when vote was soft deleted |

**Constraints**:
- UNIQUE(fact_id, user_id) - One vote per user per fact

**Vote Types**:
- **fact**: User believes the statement is true/accurate
- **fake**: User believes the statement is false/inaccurate

**Business Rules**:
- Users cannot vote on their own facts (enforced at application level)
- Users can change their vote (updates existing record)
- Vote changes update statistics in real-time

## Table: comment_votes
**Purpose**: Upvote/Downvote voting system for comments

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for vote (UUID format) |
| comment_id | VARCHAR(36) | NOT NULL, FK to comments.id | Comment being voted on |
| user_id | VARCHAR(36) | NOT NULL, FK to users.id | User casting the vote |
| vote_type | VARCHAR(10) | NOT NULL, CHECK ('upvote', 'downvote') | Type of vote cast |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Vote creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when vote was soft deleted |

**Constraints**:
- UNIQUE(comment_id, user_id) - One vote per user per comment

**Vote Types**:
- **upvote**: User finds comment helpful/valuable
- **downvote**: User finds comment unhelpful/inappropriate

**Business Rules**:
- Users cannot vote on their own comments (enforced at application level)
- Users can change their vote (updates existing record)

## Table: vote_statistics
**Purpose**: Cached voting statistics for performance optimization

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Unique identifier for statistics record (UUID format) |
| content_type | VARCHAR(10) | NOT NULL, CHECK ('fact', 'comment') | Type of content these statistics apply to |
| content_id | VARCHAR(36) | NOT NULL | ID of the fact or comment |
| total_votes | INTEGER | NOT NULL, DEFAULT 0 | Total number of votes (positive + negative) |
| positive_votes | INTEGER | NOT NULL, DEFAULT 0 | Number of positive votes ('fact' or 'upvote') |
| negative_votes | INTEGER | NOT NULL, DEFAULT 0 | Number of negative votes ('fake' or 'downvote') |
| vote_score | DECIMAL(10,4) | NOT NULL, DEFAULT 0.0 | Calculated score for ranking |
| last_updated | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When statistics were last recalculated |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0, CHECK (0,1) | Soft delete flag |
| deleted_at | DATETIME | NULL | Timestamp when record was soft deleted |

**Constraints**:
- UNIQUE(content_type, content_id) - One statistics record per content item

**Vote Score Calculations**:
- **For facts**: (positive_votes - negative_votes) / total_votes
- **For comments**: positive_votes - negative_votes

**Business Rules**:
- Statistics updated when votes are cast or changed
- Cached for performance (avoids real-time calculations)
- Used for content ranking and display

## Relationships Summary

### Comment Threading
- **facts → comments (1:many)**: Facts can have multiple comments
- **comments → comments (self-referencing)**: Comments can reply to other comments
- **comments → comment_threads (1:1 for root)**: Root comments have thread metadata

### Voting Relationships
- **users + facts → fact_votes (many:many)**: Users vote on facts
- **users + comments → comment_votes (many:many)**: Users vote on comments
- **facts/comments → vote_statistics (1:1)**: Each content item has cached statistics

## Indexes for Community Interaction Tables

### Primary Key Indexes (Automatic)
- comments(id), comment_edit_history(id), comment_threads(id)
- fact_votes(id), comment_votes(id), vote_statistics(id)

### Foreign Key Indexes
- comments(fact_id, user_id, parent_comment_id)
- comment_edit_history(comment_id)
- comment_threads(fact_id, root_comment_id)
- fact_votes(fact_id, user_id)
- comment_votes(comment_id, user_id)

### Unique Constraint Indexes (Automatic)
- comment_threads(fact_id, root_comment_id)
- fact_votes(fact_id, user_id)
- comment_votes(comment_id, user_id)
- vote_statistics(content_type, content_id)

### Performance Indexes
- comments(fact_id, created_at)
- comments(parent_comment_id, created_at)
- comments(nesting_level)
- vote_statistics(vote_score DESC)
- vote_statistics(total_votes DESC)

## Threading Logic

### Nesting Level Rules
- **Level 0**: Direct comments on facts (parent_comment_id = NULL)
- **Level 1**: Replies to Level 0 comments
- **Level 2**: Replies to Level 1 comments (maximum depth)

### Thread Structure Example
```
Fact
├── Comment A (Level 0) → Creates comment_threads record
│   ├── Reply A1 (Level 1)
│   │   ├── Reply A1a (Level 2)
│   │   └── Reply A1b (Level 2)
│   └── Reply A2 (Level 1)
└── Comment B (Level 0) → Creates comment_threads record
    └── Reply B1 (Level 1)
```
