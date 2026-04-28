from app import create_app
from extensions import db
from sqlalchemy import text
import uuid
from models import User

app = create_app()
with app.app_context():
    queries = [
        "ALTER TABLE company_profiles ADD COLUMN district VARCHAR(100);",
        "ALTER TABLE company_profiles ADD COLUMN address VARCHAR(255);",
        "ALTER TABLE landowner_profiles ADD COLUMN district VARCHAR(100);",
        "ALTER TABLE landowner_profiles ADD COLUMN address VARCHAR(255);"
    ]
    
    for q in queries:
        try:
            db.session.execute(text(q))
            db.session.commit()
            print(f"Success: {q}")
        except Exception as e:
            db.session.rollback()
            print(f"Failed or already exists: {q} ({e})")
