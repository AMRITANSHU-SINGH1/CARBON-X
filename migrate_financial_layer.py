from app import create_app
from extensions import db
from sqlalchemy import text
from models import CompanyProfile, LandownerProfile, CarbonCredit, EmissionReport, CarbonTransaction

app = create_app()

def migrate():
    with app.app_context():
        # Alter existing tables
        try:
            db.session.execute(text("ALTER TABLE company_profiles ADD COLUMN wallet_balance FLOAT DEFAULT 500000.0"))
            print("Added wallet_balance to company_profiles.")
        except Exception as e:
            print(f"Error altering company_profiles: {e}")

        try:
            db.session.execute(text("ALTER TABLE landowner_profiles ADD COLUMN wallet_balance FLOAT DEFAULT 0.0"))
            print("Added wallet_balance to landowner_profiles.")
        except Exception as e:
            print(f"Error altering landowner_profiles: {e}")

        try:
            db.session.execute(text("ALTER TABLE carbon_credits ADD COLUMN left_carbon_credits FLOAT"))
            db.session.execute(text("ALTER TABLE carbon_credits ADD COLUMN sold_credits FLOAT DEFAULT 0.0"))
            print("Added columns to carbon_credits.")
        except Exception as e:
            print(f"Error altering carbon_credits: {e}")

        try:
            # Need to quote the column name since we used capital 'R' in Python model, but postgres lowercases it usually. 
            # We'll use lowercase required_credits in table just in case but let's see. 
            # Actually SQLAlchemy translates "Required_credits" to "required_credits" if no quote is used or keeps it if __tablename__ ... wait. 
            # It's safer to just use exact matches, but let's try without quotes first, or with quotes. 
            # To be safe, let's use exact name from model: Required_credits
            db.session.execute(text('ALTER TABLE emission_reports ADD COLUMN "Required_credits" FLOAT'))
            db.session.execute(text("ALTER TABLE emission_reports ADD COLUMN credits_owned FLOAT DEFAULT 0.0"))
            print("Added columns to emission_reports.")
        except Exception as e:
            print(f"Error altering emission_reports: {e}")
            
        db.session.commit()
        
        # Create new tables (CarbonTransaction)
        db.create_all()
        print("Created new tables (CarbonTransaction).")

        # Sync Data
        companies = CompanyProfile.query.all()
        for c in companies:
            if c.wallet_balance is None:
                c.wallet_balance = 500000.0
                
        landowners = LandownerProfile.query.all()
        for l in landowners:
            if l.wallet_balance is None:
                l.wallet_balance = 0.0
                
        credits = CarbonCredit.query.all()
        for c in credits:
            if c.left_carbon_credits is None:
                c.left_carbon_credits = c.total_credits_calculated
            if c.sold_credits is None:
                c.sold_credits = 0.0
                
        reports = EmissionReport.query.all()
        for r in reports:
            if r.Required_credits is None:
                r.Required_credits = r.total_required_credits
            if r.credits_owned is None:
                r.credits_owned = 0.0
                
        db.session.commit()
        print("Data synced successfully.")

if __name__ == '__main__':
    migrate()
