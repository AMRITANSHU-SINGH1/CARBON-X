from app import create_app
from extensions import db
from models import LandownerProfile, CompanyProfile

app = create_app()

with app.app_context():
    # Update stuck profiles to approved
    landowners = LandownerProfile.query.filter_by(verification_status='submitted').all()
    for lp in landowners:
        lp.verification_status = 'approved'
        lp.site_verified = True
        
    companies = CompanyProfile.query.filter_by(verification_status='submitted').all()
    for cp in companies:
        cp.verification_status = 'approved'
        cp.site_verified = True
        
    db.session.commit()
    print(f"Updated {len(landowners)} landowners and {len(companies)} companies.")
