"""
Initialize default report categories in the database.
"""

from app import create_app
from app.models import db, ReportCategory

def init_report_categories():
    """Initialize default report categories."""
    
    categories = [
        {
            'name': 'Spam',
            'description': 'Unwanted promotional content or repetitive posts',
            'severity_level': 2,
            'auto_escalate': False
        },
        {
            'name': 'Harassment',
            'description': 'Bullying, threats, or targeted harassment of users',
            'severity_level': 4,
            'auto_escalate': True
        },
        {
            'name': 'Hate Speech',
            'description': 'Content promoting hatred based on identity or beliefs',
            'severity_level': 5,
            'auto_escalate': True
        },
        {
            'name': 'Misinformation',
            'description': 'Deliberately false or misleading information',
            'severity_level': 3,
            'auto_escalate': False
        },
        {
            'name': 'Inappropriate Content',
            'description': 'Content not suitable for the platform',
            'severity_level': 2,
            'auto_escalate': False
        },
        {
            'name': 'Copyright Violation',
            'description': 'Unauthorized use of copyrighted material',
            'severity_level': 3,
            'auto_escalate': False
        },
        {
            'name': 'Personal Information',
            'description': 'Sharing private or personal information without consent',
            'severity_level': 4,
            'auto_escalate': True
        },
        {
            'name': 'Off-Topic',
            'description': 'Content not relevant to the discussion or platform',
            'severity_level': 1,
            'auto_escalate': False
        },
        {
            'name': 'Impersonation',
            'description': 'Pretending to be someone else or creating fake accounts',
            'severity_level': 3,
            'auto_escalate': False
        },
        {
            'name': 'Other',
            'description': 'Other violations not covered by specific categories',
            'severity_level': 2,
            'auto_escalate': False
        }
    ]
    
    app = create_app()
    
    with app.app_context():
        # Check if categories already exist
        existing_categories = ReportCategory.query.count()
        
        if existing_categories > 0:
            print(f"Report categories already exist ({existing_categories} found). Skipping initialization.")
            return
        
        print("Initializing report categories...")
        
        for category_data in categories:
            # Check if category already exists
            existing = ReportCategory.query.filter_by(name=category_data['name']).first()
            
            if not existing:
                category = ReportCategory(**category_data)
                db.session.add(category)
                print(f"Added category: {category_data['name']}")
        
        try:
            db.session.commit()
            print(f"Successfully initialized {len(categories)} report categories.")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing categories: {str(e)}")

if __name__ == '__main__':
    init_report_categories()
