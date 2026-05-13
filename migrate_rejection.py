"""
One-time migration: Add rejection_reason and rejected_by columns to verification_tasks.
Run with: python migrate_rejection.py
"""
from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text(
                "ALTER TABLE verification_tasks ADD COLUMN IF NOT EXISTS rejection_reason TEXT"
            ))
            conn.execute(text(
                "ALTER TABLE verification_tasks ADD COLUMN IF NOT EXISTS rejected_by VARCHAR(20)"
            ))
            conn.commit()
            print("Migration complete: rejection_reason and rejected_by columns added.")
        except Exception as e:
            print(f"Migration failed: {e}")
