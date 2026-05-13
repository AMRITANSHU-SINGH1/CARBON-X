from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        # CarbonAssessment alterations
        try:
            db.session.execute(text("ALTER TABLE carbon_assessments ADD COLUMN additionality_score INTEGER"))
            db.session.execute(text("ALTER TABLE carbon_assessments ADD COLUMN permanence_score INTEGER"))
            db.session.execute(text("ALTER TABLE carbon_assessments ADD COLUMN biodiversity_score INTEGER"))
            db.session.execute(text("ALTER TABLE carbon_assessments ADD COLUMN precision_score INTEGER"))
            db.session.execute(text("ALTER TABLE carbon_assessments ADD COLUMN final_quality_score FLOAT"))
            print("Added columns to carbon_assessments.")
        except Exception as e:
            print(f"Error altering carbon_assessments (might already exist): {e}")

        # CarbonCredit alterations
        try:
            db.session.execute(text("ALTER TABLE carbon_credits ADD COLUMN price_per_credit FLOAT"))
            db.session.execute(text("ALTER TABLE carbon_credits ADD COLUMN market_tier VARCHAR(50)"))
            db.session.execute(text("ALTER TABLE carbon_credits ADD COLUMN rating VARCHAR(10)"))
            db.session.execute(text("ALTER TABLE carbon_credits ADD COLUMN quality_score FLOAT"))
            print("Added columns to carbon_credits.")
        except Exception as e:
            print(f"Error altering carbon_credits (might already exist): {e}")

        db.session.commit()
        print("Migration complete.")

if __name__ == '__main__':
    migrate()
