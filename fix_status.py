from app import create_app
from extensions import db
from models import CarbonAssessment, CarbonCredit

app = create_app()
with app.app_context():
    # Update CarbonAssessments
    assessments = CarbonAssessment.query.filter_by(status='Pending').all()
    count = 0
    for a in assessments:
        a.status = 'Completed'
        count += 1
    
    db.session.commit()
    print(f"Updated {count} CarbonAssessments to 'Completed'")
