from app import create_app
from extensions import db
from models import CarbonAssessment, CarbonCredit

app = create_app()

with app.app_context():
    db.create_all()
    print("Database migration completed: CarbonAssessment and CarbonCredit tables created.")
