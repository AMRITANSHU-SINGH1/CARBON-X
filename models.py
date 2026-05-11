from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(20), unique=True, nullable=True) # e.g. CXSO-A1B2C3
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'subordinate', 'company', 'landowner'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    landowner_profile = db.relationship('LandownerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    subordinate_profile = db.relationship('SubordinateProfile', backref='user', uselist=False, cascade='all, delete-orphan')

class SubordinateProfile(db.Model):
    __tablename__ = 'subordinate_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    district = db.Column(db.String(100), nullable=False)

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    registration_number = db.Column(db.String(64), unique=True, nullable=False) 
    district = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    
    # Verification states: 'pending', 'submitted', 'approved', 'rejected'
    verification_status = db.Column(db.String(20), default='pending')
    emission_data = db.Column(db.Text, nullable=True) # Text or JSON string to store form details
    site_verified = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)

class LandownerProfile(db.Model):
    __tablename__ = 'landowner_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    aadhaar_card_id = db.Column(db.String(12), unique=True, nullable=True) # 12 digit Aadhaar number
    district = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    
    # Verification states: 'pending', 'submitted', 'approved', 'rejected'
    verification_status = db.Column(db.String(20), default='pending')
    green_cover_details = db.Column(db.Text, nullable=True)
    site_verified = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)

class VerificationTask(db.Model):
    __tablename__ = 'verification_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    subordinate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    landowner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    status = db.Column(db.String(20), default='assigned') # 'assigned', 'in_progress', 'completed', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    report_data = db.Column(db.Text, nullable=True) # JSON string for flexible form data
    document_path = db.Column(db.String(255), nullable=True) # Path to uploaded PDF
    rejection_reason = db.Column(db.Text, nullable=True) # Reason provided when task is rejected
    rejected_by = db.Column(db.String(20), nullable=True) # 'subordinate' or 'admin'
    
    # Relationships
    subordinate = db.relationship('User', foreign_keys=[subordinate_id], backref='assigned_tasks')
    company = db.relationship('User', foreign_keys=[company_id], backref='company_verification_tasks')
    landowner = db.relationship('User', foreign_keys=[landowner_id], backref='landowner_verification_tasks')


class CarbonAssessment(db.Model):
    """Stores subordinate-submitted carbon calculation records for landowner sites."""
    __tablename__ = 'carbon_assessments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('verification_tasks.id'), nullable=False)
    subordinate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landowner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Project context
    land_name = db.Column(db.String(200), nullable=False)
    total_area_ha = db.Column(db.Float, nullable=False)

    # Stored as JSON string: list of {species, count, dbh, height}
    raw_data = db.Column(db.Text, nullable=False)

    # Calculated values
    total_credits_calculated = db.Column(db.Float, nullable=False, default=0.0)
    gross_credits = db.Column(db.Float, nullable=True)

    # Operational inputs (stored for audit trail)
    nitrogen_fertilizer_kg = db.Column(db.Float, nullable=False, default=0.0)
    diesel_liters = db.Column(db.Float, nullable=False, default=0.0)

    # Status: 'Pending', 'Verified', 'Rejected'
    status = db.Column(db.String(20), default='Pending', nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    task = db.relationship('VerificationTask', backref=db.backref('carbon_assessment', uselist=False))
    subordinate = db.relationship('User', foreign_keys=[subordinate_id], backref='carbon_assessments')
    landowner_user = db.relationship('User', foreign_keys=[landowner_id], backref='landowner_carbon_assessments')


class CarbonCredit(db.Model):
    """Stores the details of each registered carbon credit on the platform."""
    __tablename__ = 'carbon_credits'

    id = db.Column(db.Integer, primary_key=True)
    carbon_assessment_id = db.Column(db.Integer, db.ForeignKey('carbon_assessments.id'), nullable=False)
    subordinate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landowner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    land_name = db.Column(db.String(200), nullable=False)
    total_area_ha = db.Column(db.Float, nullable=False)
    raw_data = db.Column(db.Text, nullable=False)
    
    total_credits_calculated = db.Column(db.Float, nullable=False, default=0.0)
    gross_credits = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(20), default='Active', nullable=False)  # 'Active', 'Sold', 'Deactivated'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assessment = db.relationship('CarbonAssessment', backref=db.backref('credits', cascade='all, delete-orphan'))
    subordinate = db.relationship('User', foreign_keys=[subordinate_id], backref='created_credits')
    landowner = db.relationship('User', foreign_keys=[landowner_id], backref='owned_credits')




