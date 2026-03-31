"""
Analytics services for event tracking, metrics calculation, and reporting.
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from app.models import db
from app.models.analytics import (
    MetricsAggregation, DashboardConfiguration, UserEngagementMetrics
)
from app.models.system import AnalyticsEvent
from app.models import User, Fact, Comment, FactVote, CommentVote, Report, ModerationAction

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking events and calculating analytics."""
    
    @staticmethod
    def track_event(event_type: str, event_category: str, user_id: str = None,
                   resource_type: str = None, resource_id: str = None,
                   event_data: Dict[str, Any] = None, duration_ms: int = None,
                   value: float = None, session_id: str = None,
                   ip_address: str = None, user_agent: str = None,
                   referrer: str = None, page_url: str = None) -> Tuple[bool, str]:
        """
        Track an analytics event.
        
        Args:
            event_type: Type of event (login, fact_created, vote_cast, etc.)
            event_category: Category (user, content, interaction, system)
            user_id: ID of the user (optional for anonymous events)
            resource_type: Type of resource involved (fact, comment, user, etc.)
            resource_id: ID of the resource
            event_data: Additional event-specific data
            duration_ms: Duration in milliseconds for timing events
            value: Numeric value for the event
            session_id: Session identifier
            ip_address: User's IP address
            user_agent: User's browser user agent
            referrer: Referring page URL
            page_url: Current page URL
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                event_category=event_category,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                event_data=event_data or {},
                duration_ms=duration_ms,
                value=value,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                page_url=page_url
            )
            
            db.session.add(event)
            db.session.commit()
            
            # Update user engagement metrics if user is provided
            if user_id and event_category in ['user', 'content', 'interaction']:
                AnalyticsService._update_user_engagement_metrics(user_id, event_type)
            
            return True, "Event tracked successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error tracking event: {str(e)}")
            return False, "Failed to track event"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error tracking event: {str(e)}")
            return False, "Failed to track event"
    
    @staticmethod
    def _update_user_engagement_metrics(user_id: str, event_type: str):
        """Update user engagement metrics for today."""
        try:
            today = date.today()
            
            # Get or create today's metrics
            metrics = UserEngagementMetrics.query.filter_by(
                user_id=user_id, metric_date=today
            ).first()
            
            if not metrics:
                metrics = UserEngagementMetrics(
                    user_id=user_id,
                    metric_date=today
                )
                db.session.add(metrics)
            
            # Update metrics based on event type
            if event_type == 'login':
                metrics.session_count += 1
            elif event_type == 'page_view':
                metrics.page_views += 1
            elif event_type == 'fact_created':
                metrics.facts_created += 1
            elif event_type == 'comment_created':
                metrics.comments_created += 1
            elif event_type in ['fact_vote', 'comment_vote']:
                metrics.votes_cast += 1
            elif event_type == 'profile_viewed':
                metrics.profile_views += 1
            elif event_type == 'report_handled':
                metrics.reports_handled += 1
            elif event_type in ['user_warned', 'user_suspended', 'user_banned', 'content_removed']:
                metrics.moderation_actions += 1
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating user engagement metrics: {str(e)}")
    
    @staticmethod
    def get_events(start_date: datetime = None, end_date: datetime = None,
                  event_types: List[str] = None, event_categories: List[str] = None,
                  user_id: str = None, limit: int = 1000) -> List[AnalyticsEvent]:
        """
        Retrieve analytics events with filtering.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            event_types: List of event types to include
            event_categories: List of event categories to include
            user_id: Filter by specific user
            limit: Maximum number of events to return
            
        Returns:
            List of AnalyticsEvent objects
        """
        try:
            query = AnalyticsEvent.query
            
            # Apply filters
            if start_date:
                query = query.filter(AnalyticsEvent.created_at >= start_date)
            if end_date:
                query = query.filter(AnalyticsEvent.created_at <= end_date)
            if event_types:
                query = query.filter(AnalyticsEvent.event_type.in_(event_types))
            if event_categories:
                query = query.filter(AnalyticsEvent.event_category.in_(event_categories))
            if user_id:
                query = query.filter(AnalyticsEvent.user_id == user_id)
            
            return query.order_by(desc(AnalyticsEvent.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error retrieving events: {str(e)}")
            return []
    
    @staticmethod
    def get_event_counts(start_date: datetime = None, end_date: datetime = None,
                        group_by: str = 'event_type') -> Dict[str, int]:
        """
        Get event counts grouped by specified field.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            group_by: Field to group by (event_type, event_category, user_id)
            
        Returns:
            Dictionary with counts
        """
        try:
            query = db.session.query(
                getattr(AnalyticsEvent, group_by),
                func.count(AnalyticsEvent.id).label('count')
            )
            
            # Apply date filters
            if start_date:
                query = query.filter(AnalyticsEvent.created_at >= start_date)
            if end_date:
                query = query.filter(AnalyticsEvent.created_at <= end_date)
            
            results = query.group_by(getattr(AnalyticsEvent, group_by)).all()
            
            return {str(result[0]): result[1] for result in results}
            
        except Exception as e:
            logger.error(f"Error getting event counts: {str(e)}")
            return {}


class MetricsCalculationService:
    """Service for calculating and aggregating metrics."""
    
    @staticmethod
    def calculate_daily_metrics(target_date: date = None) -> Tuple[bool, str]:
        """
        Calculate and store daily metrics for a specific date.
        
        Args:
            target_date: Date to calculate metrics for (defaults to yesterday)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        try:
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = start_datetime + timedelta(days=1)
            
            # Calculate various metrics
            metrics_to_calculate = [
                ('daily_active_users', MetricsCalculationService._calculate_daily_active_users),
                ('fact_creation_count', MetricsCalculationService._calculate_fact_creation_count),
                ('comment_creation_count', MetricsCalculationService._calculate_comment_creation_count),
                ('vote_count', MetricsCalculationService._calculate_vote_count),
                ('report_count', MetricsCalculationService._calculate_report_count),
                ('moderation_action_count', MetricsCalculationService._calculate_moderation_action_count),
                ('user_registration_count', MetricsCalculationService._calculate_user_registration_count),
                ('session_count', MetricsCalculationService._calculate_session_count),
                ('avg_session_duration', MetricsCalculationService._calculate_avg_session_duration),
            ]
            
            for metric_name, calculation_func in metrics_to_calculate:
                success, value, metadata = calculation_func(start_datetime, end_datetime)
                if success:
                    MetricsCalculationService._store_metric(
                        metric_name, 'daily', target_date, value, metadata
                    )
            
            return True, f"Daily metrics calculated for {target_date}"
            
        except Exception as e:
            logger.error(f"Error calculating daily metrics: {str(e)}")
            return False, "Failed to calculate daily metrics"
    
    @staticmethod
    def _calculate_daily_active_users(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate daily active users."""
        try:
            count = db.session.query(AnalyticsEvent.user_id).filter(
                and_(
                    AnalyticsEvent.created_at >= start_datetime,
                    AnalyticsEvent.created_at < end_datetime,
                    AnalyticsEvent.user_id.isnot(None)
                )
            ).distinct().count()
            
            return True, count, {}
        except Exception as e:
            logger.error(f"Error calculating daily active users: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_fact_creation_count(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate fact creation count."""
        try:
            count = Fact.query.filter(
                and_(
                    Fact.created_at >= start_datetime,
                    Fact.created_at < end_datetime,
                    Fact.is_deleted == False
                )
            ).count()
            
            return True, count, {}
        except Exception as e:
            logger.error(f"Error calculating fact creation count: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_comment_creation_count(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate comment creation count."""
        try:
            count = Comment.query.filter(
                and_(
                    Comment.created_at >= start_datetime,
                    Comment.created_at < end_datetime,
                    Comment.is_deleted == False
                )
            ).count()
            
            return True, count, {}
        except Exception as e:
            logger.error(f"Error calculating comment creation count: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_vote_count(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate total vote count."""
        try:
            fact_votes = FactVote.query.filter(
                and_(
                    FactVote.created_at >= start_datetime,
                    FactVote.created_at < end_datetime
                )
            ).count()
            
            comment_votes = CommentVote.query.filter(
                and_(
                    CommentVote.created_at >= start_datetime,
                    CommentVote.created_at < end_datetime
                )
            ).count()
            
            total_votes = fact_votes + comment_votes
            metadata = {'fact_votes': fact_votes, 'comment_votes': comment_votes}
            
            return True, total_votes, metadata
        except Exception as e:
            logger.error(f"Error calculating vote count: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_report_count(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate report count."""
        try:
            count = Report.query.filter(
                and_(
                    Report.created_at >= start_datetime,
                    Report.created_at < end_datetime
                )
            ).count()
            
            return True, count, {}
        except Exception as e:
            logger.error(f"Error calculating report count: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_moderation_action_count(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate moderation action count."""
        try:
            count = ModerationAction.query.filter(
                and_(
                    ModerationAction.created_at >= start_datetime,
                    ModerationAction.created_at < end_datetime
                )
            ).count()
            
            return True, count, {}
        except Exception as e:
            logger.error(f"Error calculating moderation action count: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_user_registration_count(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate user registration count."""
        try:
            count = User.query.filter(
                and_(
                    User.created_at >= start_datetime,
                    User.created_at < end_datetime,
                    User.is_deleted == False
                )
            ).count()
            
            return True, count, {}
        except Exception as e:
            logger.error(f"Error calculating user registration count: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_session_count(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, int, Dict]:
        """Calculate session count."""
        try:
            count = db.session.query(AnalyticsEvent.session_id).filter(
                and_(
                    AnalyticsEvent.created_at >= start_datetime,
                    AnalyticsEvent.created_at < end_datetime,
                    AnalyticsEvent.session_id.isnot(None),
                    AnalyticsEvent.event_type == 'login'
                )
            ).distinct().count()
            
            return True, count, {}
        except Exception as e:
            logger.error(f"Error calculating session count: {str(e)}")
            return False, 0, {}
    
    @staticmethod
    def _calculate_avg_session_duration(start_datetime: datetime, end_datetime: datetime) -> Tuple[bool, float, Dict]:
        """Calculate average session duration."""
        try:
            # This is a simplified calculation - in a real system you'd track session start/end
            avg_duration = db.session.query(func.avg(AnalyticsEvent.duration_ms)).filter(
                and_(
                    AnalyticsEvent.created_at >= start_datetime,
                    AnalyticsEvent.created_at < end_datetime,
                    AnalyticsEvent.duration_ms.isnot(None),
                    AnalyticsEvent.event_type == 'session_duration'
                )
            ).scalar()
            
            return True, float(avg_duration or 0), {}
        except Exception as e:
            logger.error(f"Error calculating average session duration: {str(e)}")
            return False, 0.0, {}
    
    @staticmethod
    def _store_metric(metric_name: str, aggregation_type: str, aggregation_date: date,
                     value: float, metadata: Dict = None):
        """Store calculated metric in the database."""
        try:
            # Check if metric already exists
            existing = MetricsAggregation.query.filter_by(
                metric_name=metric_name,
                aggregation_type=aggregation_type,
                aggregation_date=aggregation_date
            ).first()
            
            if existing:
                # Update existing metric
                if isinstance(value, int):
                    existing.count_value = value
                else:
                    existing.avg_value = value
                existing.extra_data = metadata or {}
                existing.updated_at = datetime.utcnow()
            else:
                # Create new metric
                metric = MetricsAggregation(
                    metric_name=metric_name,
                    aggregation_type=aggregation_type,
                    aggregation_date=aggregation_date,
                    extra_data=metadata or {}
                )
                
                if isinstance(value, int):
                    metric.count_value = value
                else:
                    metric.avg_value = value
                
                db.session.add(metric)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing metric: {str(e)}")
    
    @staticmethod
    def get_metrics(metric_names: List[str] = None, aggregation_type: str = 'daily',
                   start_date: date = None, end_date: date = None) -> List[MetricsAggregation]:
        """
        Retrieve stored metrics with filtering.
        
        Args:
            metric_names: List of metric names to retrieve
            aggregation_type: Type of aggregation (daily, weekly, monthly)
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of MetricsAggregation objects
        """
        try:
            query = MetricsAggregation.query.filter_by(aggregation_type=aggregation_type)
            
            if metric_names:
                query = query.filter(MetricsAggregation.metric_name.in_(metric_names))
            if start_date:
                query = query.filter(MetricsAggregation.aggregation_date >= start_date)
            if end_date:
                query = query.filter(MetricsAggregation.aggregation_date <= end_date)
            
            return query.order_by(asc(MetricsAggregation.aggregation_date)).all()
            
        except Exception as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            return []


class DashboardService:
    """Service for managing analytics dashboards."""
    
    @staticmethod
    def create_dashboard(name: str, dashboard_type: str, widget_config: Dict[str, Any],
                        description: str = None, filters: Dict[str, Any] = None,
                        refresh_interval: int = 300, is_public: bool = False,
                        creator_id: str = None) -> Tuple[bool, str, Optional[DashboardConfiguration]]:
        """
        Create a new dashboard configuration.
        
        Args:
            name: Dashboard name
            dashboard_type: Type of dashboard (admin, moderator, user)
            widget_config: Widget layout and configuration
            description: Dashboard description
            filters: Default filters
            refresh_interval: Refresh interval in seconds
            is_public: Whether dashboard is publicly accessible
            creator_id: ID of the user creating the dashboard
            
        Returns:
            Tuple of (success: bool, message: str, dashboard: DashboardConfiguration or None)
        """
        try:
            # Check if dashboard name already exists
            existing = DashboardConfiguration.query.filter_by(name=name).first()
            if existing:
                return False, "Dashboard name already exists", None
            
            dashboard = DashboardConfiguration(
                name=name,
                description=description,
                dashboard_type=dashboard_type,
                widget_config=widget_config,
                filters=filters or {},
                refresh_interval=refresh_interval,
                is_public=is_public,
                created_by=creator_id
            )
            
            db.session.add(dashboard)
            db.session.commit()
            
            return True, "Dashboard created successfully", dashboard
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating dashboard: {str(e)}")
            return False, "Failed to create dashboard", None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating dashboard: {str(e)}")
            return False, "Failed to create dashboard", None
    
    @staticmethod
    def get_dashboards(dashboard_type: str = None, user_id: str = None,
                      include_public: bool = True) -> List[DashboardConfiguration]:
        """
        Get available dashboards for a user.
        
        Args:
            dashboard_type: Filter by dashboard type
            user_id: User ID for access control
            include_public: Whether to include public dashboards
            
        Returns:
            List of DashboardConfiguration objects
        """
        try:
            query = DashboardConfiguration.query
            
            if dashboard_type:
                query = query.filter(DashboardConfiguration.dashboard_type == dashboard_type)
            
            # Access control
            if user_id:
                if include_public:
                    query = query.filter(
                        or_(
                            DashboardConfiguration.created_by == user_id,
                            DashboardConfiguration.is_public == True
                        )
                    )
                else:
                    query = query.filter(DashboardConfiguration.created_by == user_id)
            elif include_public:
                query = query.filter(DashboardConfiguration.is_public == True)
            else:
                return []  # No user ID and not including public dashboards
            
            return query.order_by(asc(DashboardConfiguration.name)).all()
            
        except Exception as e:
            logger.error(f"Error retrieving dashboards: {str(e)}")
            return []
    
    @staticmethod
    def get_dashboard_data(dashboard_id: str, date_range: int = 30) -> Dict[str, Any]:
        """
        Get data for a specific dashboard.
        
        Args:
            dashboard_id: Dashboard ID
            date_range: Number of days to include in data
            
        Returns:
            Dictionary with dashboard data
        """
        try:
            dashboard = db.session.get(DashboardConfiguration, dashboard_id)
            if not dashboard:
                return {}
            
            # Increment view count
            dashboard.increment_view_count()
            db.session.commit()
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=date_range)
            
            # Get metrics based on widget configuration
            widget_config = dashboard.widget_config
            dashboard_data = {
                'dashboard': {
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'description': dashboard.description,
                    'type': dashboard.dashboard_type,
                    'refresh_interval': dashboard.refresh_interval
                },
                'data': {},
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
            # Get metrics for each widget
            for widget_name, widget_settings in widget_config.items():
                if widget_settings.get('type') == 'metric':
                    metric_names = widget_settings.get('metrics', [])
                    metrics = MetricsCalculationService.get_metrics(
                        metric_names=metric_names,
                        start_date=start_date,
                        end_date=end_date
                    )
                    dashboard_data['data'][widget_name] = [
                        {
                            'date': metric.aggregation_date.isoformat(),
                            'metric': metric.metric_name,
                            'value': metric.count_value or metric.avg_value or 0,
                            'metadata': metric.extra_data
                        }
                        for metric in metrics
                    ]
                elif widget_settings.get('type') == 'events':
                    event_types = widget_settings.get('event_types', [])
                    start_datetime = datetime.combine(start_date, datetime.min.time())
                    end_datetime = datetime.combine(end_date, datetime.max.time())
                    
                    events = AnalyticsService.get_events(
                        start_date=start_datetime,
                        end_date=end_datetime,
                        event_types=event_types,
                        limit=widget_settings.get('limit', 100)
                    )
                    dashboard_data['data'][widget_name] = [
                        {
                            'timestamp': event.created_at.isoformat(),
                            'type': event.event_type,
                            'category': event.event_category,
                            'user_id': event.user_id,
                            'resource_type': event.resource_type,
                            'resource_id': event.resource_id,
                            'data': event.event_data
                        }
                        for event in events
                    ]
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {}


class UserEngagementService:
    """Service for analyzing user engagement metrics."""
    
    @staticmethod
    def get_user_engagement_summary(user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get engagement summary for a specific user.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with engagement summary
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            metrics = UserEngagementMetrics.query.filter(
                and_(
                    UserEngagementMetrics.user_id == user_id,
                    UserEngagementMetrics.metric_date >= start_date,
                    UserEngagementMetrics.metric_date <= end_date
                )
            ).all()
            
            if not metrics:
                return {
                    'user_id': user_id,
                    'period_days': days,
                    'total_sessions': 0,
                    'total_duration': 0,
                    'avg_session_duration': 0,
                    'total_page_views': 0,
                    'content_created': 0,
                    'interactions': 0,
                    'engagement_score': 0,
                    'daily_metrics': []
                }
            
            # Aggregate metrics
            total_sessions = sum(m.session_count for m in metrics)
            total_duration = sum(m.total_session_duration for m in metrics)
            total_page_views = sum(m.page_views for m in metrics)
            total_facts = sum(m.facts_created for m in metrics)
            total_comments = sum(m.comments_created for m in metrics)
            total_votes = sum(m.votes_cast for m in metrics)
            
            avg_session_duration = total_duration / total_sessions if total_sessions > 0 else 0
            avg_engagement_score = sum(m.engagement_score for m in metrics) / len(metrics)
            
            return {
                'user_id': user_id,
                'period_days': days,
                'total_sessions': total_sessions,
                'total_duration': total_duration,
                'avg_session_duration': avg_session_duration,
                'total_page_views': total_page_views,
                'content_created': total_facts + total_comments,
                'interactions': total_votes,
                'engagement_score': round(avg_engagement_score, 2),
                'daily_metrics': [
                    {
                        'date': m.metric_date.isoformat(),
                        'sessions': m.session_count,
                        'duration': m.total_session_duration,
                        'page_views': m.page_views,
                        'facts_created': m.facts_created,
                        'comments_created': m.comments_created,
                        'votes_cast': m.votes_cast,
                        'engagement_score': m.engagement_score
                    }
                    for m in sorted(metrics, key=lambda x: x.metric_date)
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user engagement summary: {str(e)}")
            return {}
    
    @staticmethod
    def get_top_engaged_users(days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top engaged users by engagement score.
        
        Args:
            days: Number of days to analyze
            limit: Maximum number of users to return
            
        Returns:
            List of user engagement summaries
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get users with engagement metrics in the period
            user_scores = db.session.query(
                UserEngagementMetrics.user_id,
                func.avg(UserEngagementMetrics.session_count +
                        UserEngagementMetrics.facts_created * 2 +
                        UserEngagementMetrics.comments_created +
                        UserEngagementMetrics.votes_cast * 0.5).label('avg_score')
            ).filter(
                and_(
                    UserEngagementMetrics.metric_date >= start_date,
                    UserEngagementMetrics.metric_date <= end_date
                )
            ).group_by(UserEngagementMetrics.user_id).order_by(
                desc('avg_score')
            ).limit(limit).all()
            
            # Get detailed summaries for top users
            top_users = []
            for user_id, score in user_scores:
                summary = UserEngagementService.get_user_engagement_summary(user_id, days)
                if summary:
                    # Add user info
                    user = db.session.get(User, user_id)
                    if user:
                        summary['user_email'] = user.email
                        summary['user_created'] = user.created_at.isoformat()
                    top_users.append(summary)
            
            return top_users
            
        except Exception as e:
            logger.error(f"Error getting top engaged users: {str(e)}")
            return []
