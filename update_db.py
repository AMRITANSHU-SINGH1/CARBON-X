from app import create_app
from extensions import db
from sqlalchemy import text
import uuid
from models import User

app = create_app()
with app.app_context():
    try:
        db.create_all()
        print("Successfully created verification_tasks table (and any other missing tables).")
    except Exception as e:
        print(f"Error creating tables: {e}")
