from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, SubordinateProfile

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        return render_template('dashboard/admin.html')
    elif current_user.role == 'subordinate':
        return render_template('dashboard/subordinate.html')
    elif current_user.role == 'company':
        # Check verification status
        if current_user.company_profile.verification_status == 'pending':
            flash('Please complete your verification first.', 'warning')
            return redirect(url_for('verification.company_form'))
        return render_template('dashboard/company.html', profile=current_user.company_profile)
    elif current_user.role == 'landowner':
        # Check verification status
        if current_user.landowner_profile.verification_status == 'pending':
            flash('Please complete your verification first.', 'warning')
            return redirect(url_for('verification.landowner_form'))
        return render_template('dashboard/landowner.html', profile=current_user.landowner_profile)
    else:
        return "Invalid role", 400

@dashboard_bp.route('/companies')
@login_required
def companies_list():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    companies = User.query.filter_by(role='company').all()
    
    authorised = [c for c in companies if c.company_profile and (c.company_profile.admin_approved or c.company_profile.verification_status == 'approved')]
    pending = [c for c in companies if not c.company_profile or not (c.company_profile.admin_approved or c.company_profile.verification_status == 'approved')]
    
    return render_template('dashboard/companies_list.html', authorised=authorised, pending=pending)

@dashboard_bp.route('/subordinates')
@login_required
def subordinates_list():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    subordinates = User.query.filter_by(role='subordinate').all()
    return render_template('dashboard/subordinates_list.html', subordinates=subordinates)

@dashboard_bp.route('/subordinates/edit/<int:sub_id>', methods=['GET', 'POST'])
@login_required
def edit_subordinate(sub_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    subordinate = User.query.get_or_404(sub_id)
    if subordinate.role != 'subordinate':
        flash('Invalid user.', 'danger')
        return redirect(url_for('dashboard.subordinates_list'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        district = request.form.get('district')
        password = request.form.get('password')
        
        # update user
        subordinate.email = email
        if password: # only update if a new password is provided
            subordinate.password_hash = generate_password_hash(password)
            
        # update profile
        if subordinate.subordinate_profile:
            subordinate.subordinate_profile.full_name = full_name
            subordinate.subordinate_profile.district = district
        else:
            new_profile = SubordinateProfile(
                user_id=subordinate.id,
                full_name=full_name,
                district=district
            )
            db.session.add(new_profile)
            
        db.session.commit()
        flash('Subordinate profile updated successfully.', 'success')
        return redirect(url_for('dashboard.subordinates_list'))
        
    return render_template('dashboard/edit_subordinate.html', subordinate=subordinate)
