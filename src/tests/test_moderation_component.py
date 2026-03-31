"""
Unit tests for Moderation Component functionality.
"""

import pytest
from datetime import datetime, timedelta
from app.models import db, User, Fact, Comment, ModerationAction, UserModerationHistory, ModerationWorkflow
from app.components.moderation.services import (
    ContentModerationService,
    UserModerationService,
    ModerationWorkflowService,
    ModerationDashboardService
)


class TestContentModerationService:
    """Test cases for ContentModerationService."""
    
    def test_remove_content_success(self, app, sample_user, sample_moderator_user, sample_fact):
        """Test successful content removal."""
        with app.app_context():
            success, message = ContentModerationService.remove_content(
                content_type='fact',
                content_id=sample_fact.id,
                moderator_id=sample_moderator_user.id,
                reason='Content violates community guidelines'
            )
            
            assert success is True
            assert 'removed' in message.lower()
            
            # Verify content is marked as deleted
            updated_fact = db.session.get(Fact, sample_fact.id)
            assert updated_fact.is_deleted is True
            assert updated_fact.deleted_at is not None
    
    def test_remove_content_invalid_moderator(self, app, sample_user, sample_fact):
        """Test content removal with invalid moderator."""
        with app.app_context():
            success, message = ContentModerationService.remove_content(
                content_type='fact',
                content_id=sample_fact.id,
                moderator_id=sample_user.id,  # Regular user, not moderator
                reason='Test reason'
            )
            
            assert success is False
            assert 'insufficient permissions' in message.lower()
    
    def test_restore_content_success(self, app, sample_user, sample_moderator_user, sample_fact):
        """Test successful content restoration."""
        with app.app_context():
            # First remove the content
            ContentModerationService.remove_content(
                content_type='fact',
                content_id=sample_fact.id,
                moderator_id=sample_moderator_user.id,
                reason='Initial removal'
            )
            
            # Then restore it
            success, message = ContentModerationService.restore_content(
                content_type='fact',
                content_id=sample_fact.id,
                moderator_id=sample_moderator_user.id,
                reason='Content review completed - restoring'
            )
            
            assert success is True
            assert 'restored' in message.lower()
            
            # Verify content is no longer deleted
            updated_fact = db.session.get(Fact, sample_fact.id)
            assert updated_fact.is_deleted is False
            assert updated_fact.deleted_at is None
    
    def test_hide_content_with_duration(self, app, sample_user, sample_moderator_user, sample_fact):
        """Test hiding content with duration."""
        with app.app_context():
            success, message = ContentModerationService.hide_content(
                content_type='fact',
                content_id=sample_fact.id,
                moderator_id=sample_moderator_user.id,
                reason='Temporary hide for review',
                duration_hours=24
            )
            
            assert success is True
            assert 'hidden' in message.lower()
            assert '24 hours' in message
            
            # Verify moderation action was created
            action = ModerationAction.query.filter_by(
                target_type='fact',
                target_id=sample_fact.id,
                action_type='hide'
            ).first()
            
            assert action is not None
            assert action.duration_hours == 24
            assert action.expires_at is not None
    
    def test_get_moderated_content(self, app, sample_user, sample_moderator_user, sample_fact):
        """Test retrieving moderated content."""
        with app.app_context():
            # Create some moderation actions
            ContentModerationService.remove_content(
                content_type='fact',
                content_id=sample_fact.id,
                moderator_id=sample_moderator_user.id,
                reason='Test moderation'
            )
            
            data = ContentModerationService.get_moderated_content()
            
            assert len(data['actions']) >= 1
            assert data['pagination']['total'] >= 1
            
            # Check that our action is in the results
            our_action = next((a for a in data['actions'] if a['action'].target_id == sample_fact.id), None)
            assert our_action is not None
            assert our_action['action'].action_type == 'remove_temporary'


class TestUserModerationService:
    """Test cases for UserModerationService."""
    
    def test_warn_user_success(self, app, sample_user, sample_moderator_user):
        """Test successful user warning."""
        with app.app_context():
            initial_warning_count = sample_user.warning_count
            
            success, message = UserModerationService.warn_user(
                user_id=sample_user.id,
                moderator_id=sample_moderator_user.id,
                reason='Inappropriate behavior in comments',
                severity_level=2
            )
            
            assert success is True
            assert 'warning issued' in message.lower()
            
            # Verify user warning count increased
            updated_user = db.session.get(User, sample_user.id)
            assert updated_user.warning_count == initial_warning_count + 1
            assert updated_user.last_warning_date is not None
            
            # Verify moderation history was created
            history = UserModerationHistory.query.filter_by(
                user_id=sample_user.id,
                action_type='warning'
            ).first()
            
            assert history is not None
            assert history.severity_level == 2
            assert history.reason == 'Inappropriate behavior in comments'
    
    def test_warn_user_cannot_moderate_moderator(self, app, sample_moderator_user):
        """Test that regular moderators cannot warn other moderators."""
        with app.app_context():
            # Create another moderator
            other_moderator = User(
                email='other_mod@test.com',
                password_hash='hashed_password',
                is_moderator=True,
                is_active=True
            )
            other_moderator.save()
            
            success, message = UserModerationService.warn_user(
                user_id=other_moderator.id,
                moderator_id=sample_moderator_user.id,
                reason='Test reason'
            )
            
            assert success is False
            assert 'cannot moderate other moderators' in message.lower()
    
    def test_suspend_user_success(self, app, sample_user, sample_moderator_user):
        """Test successful user suspension."""
        with app.app_context():
            success, message = UserModerationService.suspend_user(
                user_id=sample_user.id,
                moderator_id=sample_moderator_user.id,
                reason='Repeated violations after warnings',
                duration_hours=72,
                severity_level=3
            )
            
            assert success is True
            assert 'suspended for 72 hours' in message.lower()
            
            # Verify user suspension status
            updated_user = db.session.get(User, sample_user.id)
            assert updated_user.is_suspended is True
            assert updated_user.suspension_expires is not None
            
            # Check user capabilities
            assert updated_user.can_post_content() is False
            assert updated_user.can_comment() is False
            assert updated_user.get_moderation_status() == 'suspended'
    
    def test_ban_user_success(self, app, sample_user):
        """Test successful user ban (admin only)."""
        with app.app_context():
            # Create admin user within test context
            admin_user = User(
                email='admin_test@test.com',
                password_hash='hashed_password',
                is_admin=True,
                is_moderator=True,
                is_active=True
            )
            admin_user.save()
            
            success, message = UserModerationService.ban_user(
                user_id=sample_user.id,
                moderator_id=admin_user.id,
                reason='Severe violations - permanent ban required',
                permanent=True
            )
            
            assert success is True
            assert 'banned permanently' in message.lower()
            
            # Verify user ban status
            updated_user = db.session.get(User, sample_user.id)
            assert updated_user.is_banned is True
            assert updated_user.is_active is False
            assert updated_user.ban_reason == 'Severe violations - permanent ban required'
            
            # Check user capabilities
            assert updated_user.can_post_content() is False
            assert updated_user.can_comment() is False
            assert updated_user.can_vote() is False
            assert updated_user.get_moderation_status() == 'banned'
    
    def test_lift_user_restriction_success(self, app, sample_user, sample_moderator_user):
        """Test lifting user restrictions."""
        with app.app_context():
            # First suspend the user
            UserModerationService.suspend_user(
                user_id=sample_user.id,
                moderator_id=sample_moderator_user.id,
                reason='Test suspension',
                duration_hours=24
            )
            
            # Then lift the restriction
            success, message = UserModerationService.lift_user_restriction(
                user_id=sample_user.id,
                moderator_id=sample_moderator_user.id,
                reason='Appeal approved - lifting suspension'
            )
            
            assert success is True
            assert 'restrictions lifted' in message.lower()
            assert 'suspension' in message.lower()
            
            # Verify user is no longer suspended
            updated_user = db.session.get(User, sample_user.id)
            assert updated_user.is_suspended is False
            assert updated_user.suspension_expires is None
            assert updated_user.get_moderation_status() == 'active'
    
    def test_get_user_moderation_history(self, app, sample_user, sample_moderator_user):
        """Test retrieving user moderation history."""
        with app.app_context():
            # Create some moderation history
            UserModerationService.warn_user(
                user_id=sample_user.id,
                moderator_id=sample_moderator_user.id,
                reason='First warning'
            )
            
            UserModerationService.warn_user(
                user_id=sample_user.id,
                moderator_id=sample_moderator_user.id,
                reason='Second warning'
            )
            
            data = UserModerationService.get_user_moderation_history(sample_user.id)
            
            assert len(data['history']) == 2
            assert data['pagination']['total'] == 2
            
            # Check that warnings are in chronological order (newest first)
            assert data['history'][0]['history'].reason == 'Second warning'
            assert data['history'][1]['history'].reason == 'First warning'
    
    def test_get_users_requiring_attention(self, app, sample_user, sample_moderator_user):
        """Test getting users requiring attention."""
        with app.app_context():
            # Give user multiple warnings to trigger attention threshold
            for i in range(4):  # Exceed threshold of 3
                UserModerationService.warn_user(
                    user_id=sample_user.id,
                    moderator_id=sample_moderator_user.id,
                    reason=f'Warning {i+1}'
                )
            
            data = UserModerationService.get_users_requiring_attention(threshold=3)
            
            assert len(data['users']) >= 1
            
            # Find our user in the results
            our_user = next((u for u in data['users'] if u['user'].id == sample_user.id), None)
            assert our_user is not None
            assert our_user['requires_attention'] is True
            assert our_user['user'].warning_count >= 3


class TestModerationWorkflowService:
    """Test cases for ModerationWorkflowService."""
    
    def test_create_workflow_success(self, app, sample_moderator_user):
        """Test successful workflow creation."""
        with app.app_context():
            conditions = {
                'report_count': {'operator': 'greater_than', 'value': 3}
            }
            actions = [
                {'type': 'hide_content', 'duration_hours': 24}
            ]
            
            success, message, workflow = ModerationWorkflowService.create_workflow(
                name='Auto-hide high report content',
                description='Automatically hide content with more than 3 reports',
                trigger_type='report_count',
                conditions=conditions,
                actions=actions,
                moderator_id=sample_moderator_user.id,
                priority=2
            )
            
            assert success is True
            assert 'workflow created successfully' in message.lower()
            assert workflow is not None
            assert workflow.name == 'Auto-hide high report content'
            assert workflow.trigger_type == 'report_count'
            assert workflow.priority == 2
            assert workflow.is_active is True
    
    def test_create_workflow_invalid_moderator(self, app, sample_user):
        """Test workflow creation with invalid moderator."""
        with app.app_context():
            success, message, workflow = ModerationWorkflowService.create_workflow(
                name='Test workflow',
                description='Test description',
                trigger_type='report_count',
                conditions={},
                actions=[],
                moderator_id=sample_user.id,  # Regular user, not moderator
                priority=1
            )
            
            assert success is False
            assert 'insufficient permissions' in message.lower()
            assert workflow is None
    
    def test_get_active_workflows(self, app, sample_moderator_user):
        """Test retrieving active workflows."""
        with app.app_context():
            # Create a workflow
            ModerationWorkflowService.create_workflow(
                name='Test workflow',
                description='Test description',
                trigger_type='report_count',
                conditions={},
                actions=[],
                moderator_id=sample_moderator_user.id
            )
            
            workflows = ModerationWorkflowService.get_active_workflows()
            
            assert len(workflows) >= 1
            
            # Find our workflow
            our_workflow = next((w for w in workflows if w.name == 'Test workflow'), None)
            assert our_workflow is not None
            assert our_workflow.is_active is True


class TestModerationDashboardService:
    """Test cases for ModerationDashboardService."""
    
    def test_get_moderation_overview(self, app, sample_user, sample_moderator_user, sample_fact):
        """Test getting moderation overview."""
        with app.app_context():
            # Create some moderation actions
            ContentModerationService.remove_content(
                content_type='fact',
                content_id=sample_fact.id,
                moderator_id=sample_moderator_user.id,
                reason='Test removal'
            )
            
            UserModerationService.warn_user(
                user_id=sample_user.id,
                moderator_id=sample_moderator_user.id,
                reason='Test warning'
            )
            
            overview = ModerationDashboardService.get_moderation_overview(time_period=7)
            
            assert 'content_actions' in overview
            assert 'user_actions' in overview
            assert 'total_actions' in overview
            assert overview['content_actions'] >= 1
            assert overview['user_actions'] >= 1
            assert overview['total_actions'] >= 2


# Fixtures for testing
@pytest.fixture
def sample_admin_user(app):
    """Create a test admin user."""
    with app.app_context():
        admin = User(
            email='admin@test.com',
            password_hash='hashed_password',
            is_admin=True,
            is_moderator=True,
            is_active=True
        )
        admin.save()
        return admin
