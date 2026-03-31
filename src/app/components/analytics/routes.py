"""
Analytics routes for dashboard access and API endpoints.
"""

import logging
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, session, abort
from functools import wraps

from app.models import db, User
from app.components.security.services import AuditService
from .services import (
    AnalyticsService, MetricsCalculationService, 
    DashboardService, UserEngagementService
)

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            abort(401)
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def moderator_required(f):
    """Decorator to require moderator or admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            abort(401)
        
        user = db.session.get(User, user_id)
        if not user or not (user.is_moderator or user.is_admin):
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def authenticated_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


# Dashboard Routes

@analytics_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin analytics dashboard."""
    user_id = session.get('user_id')
    
    # Track page view
    AnalyticsService.track_event(
        event_type='page_view',
        event_category='system',
        user_id=user_id,
        page_url='/analytics/dashboard'
    )
    
    # Get available dashboards
    dashboards = DashboardService.get_dashboards(
        dashboard_type='admin',
        user_id=user_id,
        include_public=True
    )
    
    return render_template('analytics/admin_dashboard.html', dashboards=dashboards)


@analytics_bp.route('/dashboard/moderator')
@moderator_required
def moderator_dashboard():
    """Moderator analytics dashboard."""
    user_id = session.get('user_id')
    
    # Track page view
    AnalyticsService.track_event(
        event_type='page_view',
        event_category='system',
        user_id=user_id,
        page_url='/analytics/dashboard/moderator'
    )
    
    # Get available dashboards
    dashboards = DashboardService.get_dashboards(
        dashboard_type='moderator',
        user_id=user_id,
        include_public=True
    )
    
    return render_template('analytics/moderator_dashboard.html', dashboards=dashboards)


@analytics_bp.route('/dashboard/user')
@authenticated_required
def user_dashboard():
    """User analytics dashboard."""
    user_id = session.get('user_id')
    
    # Track page view
    AnalyticsService.track_event(
        event_type='page_view',
        event_category='user',
        user_id=user_id,
        page_url='/analytics/dashboard/user'
    )
    
    # Get user engagement summary
    engagement_summary = UserEngagementService.get_user_engagement_summary(user_id, days=30)
    
    return render_template('analytics/user_dashboard.html', engagement=engagement_summary)


# API Endpoints

@analytics_bp.route('/api/track', methods=['POST'])
def track_event():
    """API endpoint for tracking events."""
    try:
        # Handle JSON parsing errors
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract event data
        event_type = data.get('event_type')
        event_category = data.get('event_category')
        
        if not event_type or not event_category:
            return jsonify({'error': 'event_type and event_category are required'}), 400
        
        # Get user from session
        user_id = session.get('user_id')
        
        # Track the event
        success, message = AnalyticsService.track_event(
            event_type=event_type,
            event_category=event_category,
            user_id=user_id,
            resource_type=data.get('resource_type'),
            resource_id=data.get('resource_id'),
            event_data=data.get('event_data'),
            duration_ms=data.get('duration_ms'),
            value=data.get('value'),
            session_id=session.get('session_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            referrer=request.headers.get('Referer'),
            page_url=data.get('page_url')
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        logger.error(f"Error tracking event: {str(e)}")
        return jsonify({'error': 'Failed to track event'}), 500


@analytics_bp.route('/api/metrics')
@moderator_required
def get_metrics():
    """API endpoint for retrieving metrics."""
    try:
        # Get query parameters
        metric_names = request.args.getlist('metrics')
        aggregation_type = request.args.get('aggregation_type', 'daily')
        days = int(request.args.get('days', 30))
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get metrics
        metrics = MetricsCalculationService.get_metrics(
            metric_names=metric_names if metric_names else None,
            aggregation_type=aggregation_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Format response
        response_data = []
        for metric in metrics:
            response_data.append({
                'metric_name': metric.metric_name,
                'aggregation_type': metric.aggregation_type,
                'date': metric.aggregation_date.isoformat(),
                'count_value': metric.count_value,
                'sum_value': metric.sum_value,
                'avg_value': metric.avg_value,
                'min_value': metric.min_value,
                'max_value': metric.max_value,
                'metadata': metric.extra_data
            })
        
        return jsonify({
            'metrics': response_data,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return jsonify({'error': 'Failed to retrieve metrics'}), 500


@analytics_bp.route('/api/events')
@admin_required
def get_events():
    """API endpoint for retrieving events."""
    try:
        # Get query parameters
        event_types = request.args.getlist('event_types')
        event_categories = request.args.getlist('event_categories')
        user_id = request.args.get('user_id')
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 100))
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get events
        events = AnalyticsService.get_events(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types if event_types else None,
            event_categories=event_categories if event_categories else None,
            user_id=user_id,
            limit=limit
        )
        
        # Format response
        response_data = []
        for event in events:
            response_data.append({
                'id': event.id,
                'event_type': event.event_type,
                'event_category': event.event_category,
                'user_id': event.user_id,
                'resource_type': event.resource_type,
                'resource_id': event.resource_id,
                'event_data': event.event_data,
                'duration_ms': event.duration_ms,
                'value': event.value,
                'created_at': event.created_at.isoformat(),
                'ip_address': event.ip_address,
                'page_url': event.page_url
            })
        
        return jsonify({
            'events': response_data,
            'total_count': len(response_data),
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving events: {str(e)}")
        return jsonify({'error': 'Failed to retrieve events'}), 500


@analytics_bp.route('/api/dashboard/<dashboard_id>')
@moderator_required
def get_dashboard_data(dashboard_id):
    """API endpoint for retrieving dashboard data."""
    try:
        # Get query parameters
        date_range = int(request.args.get('days', 30))
        
        # Get dashboard data
        dashboard_data = DashboardService.get_dashboard_data(dashboard_id, date_range)
        
        if not dashboard_data:
            return jsonify({'error': 'Dashboard not found'}), 404
        
        # Log dashboard access
        user_id = session.get('user_id')
        AuditService.log_action(
            user_id=user_id,
            action_type='dashboard_accessed',
            resource_type='dashboard',
            resource_id=dashboard_id
        )
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        return jsonify({'error': 'Failed to retrieve dashboard data'}), 500


@analytics_bp.route('/api/engagement/user/<user_id>')
@moderator_required
def get_user_engagement(user_id):
    """API endpoint for retrieving user engagement data."""
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get engagement summary
        engagement_summary = UserEngagementService.get_user_engagement_summary(user_id, days)
        
        if not engagement_summary:
            return jsonify({'error': 'User not found or no engagement data'}), 404
        
        return jsonify(engagement_summary), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user engagement: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user engagement'}), 500


@analytics_bp.route('/api/engagement/top-users')
@admin_required
def get_top_engaged_users():
    """API endpoint for retrieving top engaged users."""
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 10))
        
        # Get top engaged users
        top_users = UserEngagementService.get_top_engaged_users(days, limit)
        
        return jsonify({
            'top_users': top_users,
            'period_days': days,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving top engaged users: {str(e)}")
        return jsonify({'error': 'Failed to retrieve top engaged users'}), 500


@analytics_bp.route('/api/summary')
@admin_required
def get_analytics_summary():
    """API endpoint for retrieving analytics summary."""
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get key metrics
        metrics = MetricsCalculationService.get_metrics(
            metric_names=[
                'daily_active_users', 'fact_creation_count', 'comment_creation_count',
                'vote_count', 'report_count', 'user_registration_count'
            ],
            aggregation_type='daily',
            start_date=start_date,
            end_date=end_date
        )
        
        # Aggregate metrics
        summary = {
            'period_days': days,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'totals': {},
            'averages': {},
            'trends': {}
        }
        
        # Group metrics by name
        metrics_by_name = {}
        for metric in metrics:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = []
            metrics_by_name[metric.metric_name].append(metric)
        
        # Calculate totals and averages
        for metric_name, metric_list in metrics_by_name.items():
            values = [m.count_value or m.avg_value or 0 for m in metric_list]
            summary['totals'][metric_name] = sum(values)
            summary['averages'][metric_name] = sum(values) / len(values) if values else 0
            
            # Simple trend calculation (last 7 days vs previous 7 days)
            if len(values) >= 14:
                recent_avg = sum(values[-7:]) / 7
                previous_avg = sum(values[-14:-7]) / 7
                if previous_avg > 0:
                    trend_pct = ((recent_avg - previous_avg) / previous_avg) * 100
                    summary['trends'][metric_name] = round(trend_pct, 2)
                else:
                    summary['trends'][metric_name] = 0
            else:
                summary['trends'][metric_name] = 0
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analytics summary: {str(e)}")
        return jsonify({'error': 'Failed to retrieve analytics summary'}), 500


# Dashboard Management Routes

@analytics_bp.route('/api/dashboards', methods=['GET'])
@moderator_required
def list_dashboards():
    """API endpoint for listing available dashboards."""
    try:
        user_id = session.get('user_id')
        user = db.session.get(User, user_id)
        
        # Determine dashboard type based on user role
        if user.is_admin:
            dashboard_types = ['admin', 'moderator', 'user']
        elif user.is_moderator:
            dashboard_types = ['moderator', 'user']
        else:
            dashboard_types = ['user']
        
        all_dashboards = []
        for dashboard_type in dashboard_types:
            dashboards = DashboardService.get_dashboards(
                dashboard_type=dashboard_type,
                user_id=user_id,
                include_public=True
            )
            all_dashboards.extend(dashboards)
        
        # Format response
        response_data = []
        for dashboard in all_dashboards:
            response_data.append({
                'id': dashboard.id,
                'name': dashboard.name,
                'description': dashboard.description,
                'type': dashboard.dashboard_type,
                'is_public': dashboard.is_public,
                'view_count': dashboard.view_count,
                'last_viewed': dashboard.last_viewed.isoformat() if dashboard.last_viewed else None,
                'created_at': dashboard.created_at.isoformat()
            })
        
        return jsonify({'dashboards': response_data}), 200
        
    except Exception as e:
        logger.error(f"Error listing dashboards: {str(e)}")
        return jsonify({'error': 'Failed to list dashboards'}), 500


@analytics_bp.route('/api/dashboards', methods=['POST'])
@admin_required
def create_dashboard():
    """API endpoint for creating a new dashboard."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = session.get('user_id')
        
        success, message, dashboard = DashboardService.create_dashboard(
            name=data.get('name'),
            dashboard_type=data.get('dashboard_type'),
            widget_config=data.get('widget_config', {}),
            description=data.get('description'),
            filters=data.get('filters'),
            refresh_interval=data.get('refresh_interval', 300),
            is_public=data.get('is_public', False),
            creator_id=user_id
        )
        
        if success:
            return jsonify({
                'message': message,
                'dashboard': {
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'type': dashboard.dashboard_type
                }
            }), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"Error creating dashboard: {str(e)}")
        return jsonify({'error': 'Failed to create dashboard'}), 500
