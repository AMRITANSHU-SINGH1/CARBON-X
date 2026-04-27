from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

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
