from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import os
app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created.")

        # Check if super admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin = User(
                username='admin',
                email='admin@carbonx.com',
                password_hash=generate_password_hash(admin_password),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Super Admin created. Credentials -> admin / {admin_password}")
        else:
            print("Super Admin already exists.")

if __name__ == '__main__':
    init_db()
