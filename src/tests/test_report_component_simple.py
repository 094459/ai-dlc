"""
Simplified unit tests for Report Component functionality.
"""

import pytest
from app.models import db, ReportCategory
from app.components.report.services import ReportManagementService, ReportQueueService


class TestReportComponent:
    """Simplified test cases for Report Component."""
    
    def _create_test_category(self):
        """Helper method to create a test category."""
        category = ReportCategory(
            name='Test Spam',
            description='Test spam category',
            severity_level=2,
            auto_escalate=False
        )
        category.save()
        return category
    
    def test_create_report_success(self, app, sample_user, sample_fact):
        """Test successful report creation."""
        with app.app_context():
            # Create a different user for reporting (not the fact author)
            from app.models import User
            reporter = User(
                email='reporter@test.com',
                password_hash='hashed_password',
                is_active=True
            )
            reporter.save()
            
            category = self._create_test_category()
            
            success, message, report = ReportManagementService.create_report(
                reporter_id=reporter.id,  # Use different user
                content_type='fact',
                content_id=sample_fact.id,
                category_id=category.id,
                reason='This content contains false information and misleads readers.'
            )
            
            assert success is True
            assert 'successfully' in message.lower()
            assert report is not None
            assert report.reporter_id == reporter.id
            assert report.reported_content_type == 'fact'
            assert report.reported_content_id == sample_fact.id
            assert report.status == 'pending'
    
    def test_create_report_invalid_content_type(self, app, sample_user, sample_fact):
        """Test report creation with invalid content type."""
        with app.app_context():
            category = self._create_test_category()
            
            success, message, report = ReportManagementService.create_report(
                reporter_id=sample_user.id,
                content_type='invalid',
                content_id=sample_fact.id,
                category_id=category.id,
                reason='Test reason with sufficient length'
            )
            
            assert success is False
            assert 'invalid content type' in message.lower()
            assert report is None
    
    def test_create_report_short_reason(self, app, sample_user, sample_fact):
        """Test report creation with too short reason."""
        with app.app_context():
            category = self._create_test_category()
            
            success, message, report = ReportManagementService.create_report(
                reporter_id=sample_user.id,
                content_type='fact',
                content_id=sample_fact.id,
                category_id=category.id,
                reason='Short'
            )
            
            assert success is False
            assert 'at least 10 characters' in message
            assert report is None
    
    def test_get_pending_reports(self, app, sample_user, sample_fact):
        """Test retrieving pending reports."""
        with app.app_context():
            # Create a different user for reporting (not the fact author)
            from app.models import User
            reporter = User(
                email='reporter2@test.com',
                password_hash='hashed_password',
                is_active=True
            )
            reporter.save()
            
            category = self._create_test_category()
            
            # Create a pending report
            success, message, report = ReportManagementService.create_report(
                reporter_id=reporter.id,  # Use different user
                content_type='fact',
                content_id=sample_fact.id,
                category_id=category.id,
                reason='Test report for queue retrieval test with sufficient length'
            )
            
            # Verify report was created successfully
            assert success is True, f"Report creation failed: {message}"
            assert report is not None
            
            reports_data = ReportQueueService.get_pending_reports()
            
            assert len(reports_data['reports']) >= 1
            # Find our report in the results
            our_report = next((r for r in reports_data['reports'] if r['report'].reporter_id == reporter.id), None)
            assert our_report is not None
            assert our_report['report'].status == 'pending'
    
    def test_assign_report_to_moderator(self, app, sample_user, sample_moderator_user, sample_fact):
        """Test assigning report to moderator."""
        with app.app_context():
            # Create a different user for reporting (not the fact author)
            from app.models import User
            reporter = User(
                email='reporter3@test.com',
                password_hash='hashed_password',
                is_active=True
            )
            reporter.save()
            
            category = self._create_test_category()
            
            # Create a pending report
            success, message, report = ReportManagementService.create_report(
                reporter_id=reporter.id,  # Use different user
                content_type='fact',
                content_id=sample_fact.id,
                category_id=category.id,
                reason='Test report for assignment test with sufficient length'
            )
            
            # Verify report was created successfully
            assert success is True, f"Report creation failed: {message}"
            assert report is not None
            
            # Assign to moderator
            success, message = ReportQueueService.assign_report_to_moderator(
                report_id=report.id,
                moderator_id=sample_moderator_user.id
            )
            
            assert success is True
            assert 'assigned successfully' in message.lower()
            
            # Verify assignment
            from app.models import Report
            updated_report = db.session.get(Report, report.id)
            assert updated_report.status == 'assigned'
            assert updated_report.moderator_id == sample_moderator_user.id
    
    def test_update_report_status(self, app, sample_user, sample_moderator_user, sample_fact):
        """Test updating report status."""
        with app.app_context():
            # Create a different user for reporting (not the fact author)
            from app.models import User
            reporter = User(
                email='reporter4@test.com',
                password_hash='hashed_password',
                is_active=True
            )
            reporter.save()
            
            category = self._create_test_category()
            
            # Create a report
            success, message, report = ReportManagementService.create_report(
                reporter_id=reporter.id,  # Use different user
                content_type='fact',
                content_id=sample_fact.id,
                category_id=category.id,
                reason='Test report for status update test with sufficient length'
            )
            
            # Verify report was created successfully
            assert success is True, f"Report creation failed: {message}"
            assert report is not None
            
            # Update status
            success, message = ReportManagementService.update_report_status(
                report_id=report.id,
                status='resolved',
                moderator_id=sample_moderator_user.id,
                notes='Report reviewed and resolved'
            )
            
            assert success is True
            assert 'resolved' in message.lower()
            
            # Verify status was updated
            from app.models import Report
            updated_report = db.session.get(Report, report.id)
            assert updated_report.status == 'resolved'
            assert updated_report.moderator_id == sample_moderator_user.id
            assert updated_report.resolution_notes == 'Report reviewed and resolved'
            assert updated_report.resolved_at is not None
