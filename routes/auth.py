from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, CompanyProfile, LandownerProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company_name')
        registration_number = request.form.get('registration_number')
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register_company'))
            
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='company'
        )
        db.session.add(new_user)
        db.session.flush() # To get new_user.id
        
        company_profile = CompanyProfile(
            user_id=new_user.id,
            company_name=company_name,
            registration_number=registration_number
        )
        db.session.add(company_profile)
        db.session.commit()
        
        login_user(new_user)
        flash('Registration successful! Please complete your verification.', 'success')
        return redirect(url_for('verification.company_form'))
        
    return render_template('auth/register_company.html')

@auth_bp.route('/register/landowner', methods=['GET', 'POST'])
def register_landowner():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register_landowner'))
            
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='landowner'
        )
        db.session.add(new_user)
        db.session.flush()
        
        landowner_profile = LandownerProfile(
            user_id=new_user.id,
            full_name=full_name
        )
        db.session.add(landowner_profile)
        db.session.commit()
        
        login_user(new_user)
        flash('Registration successful! Please complete your verification.', 'success')
        return redirect(url_for('verification.landowner_form'))
        
    return render_template('auth/register_landowner.html')

@auth_bp.route('/register/subordinate', methods=['GET', 'POST'])
@login_required
def register_subordinate():
    if current_user.role != 'admin':
        flash('Only admins can register subordinates.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register_subordinate'))
            
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='subordinate'
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Subordinate registered successfully!', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/register_subordinate.html')
