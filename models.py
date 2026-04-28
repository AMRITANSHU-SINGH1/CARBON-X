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
    district = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    
    # Verification states: 'pending', 'submitted', 'approved', 'rejected'
    verification_status = db.Column(db.String(20), default='pending')
    green_cover_details = db.Column(db.Text, nullable=True)
    site_verified = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)
