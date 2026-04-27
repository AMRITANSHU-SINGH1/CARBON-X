from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created.")

        # Check if super admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@carbonx.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Super Admin created. Credentials -> admin / admin123")
        else:
            print("Super Admin already exists.")

if __name__ == '__main__':
    init_db()
