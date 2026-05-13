from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Drop existing tables to recreate them with the new schema (task_id column added)
    db.session.execute(text("DROP TABLE IF EXISTS carbon_credits CASCADE;"))
    db.session.execute(text("DROP TABLE IF EXISTS carbon_assessments CASCADE;"))
    db.session.commit()
    
    # Recreate all tables
    db.create_all()
    print("Database tables dropped and recreated successfully with the new schema.")
