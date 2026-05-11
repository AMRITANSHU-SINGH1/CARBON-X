from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import CompanyProfile, LandownerProfile

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/company', methods=['GET', 'POST'])
@login_required
def company_form():
    if current_user.role != 'company':
        return redirect(url_for('dashboard.index'))
        
    profile = current_user.company_profile
    # Allow access for 'pending' (first submission) or 'rejected' (resubmission)
    if profile.verification_status not in ('pending', 'rejected'):
        flash('Verification already submitted or approved.', 'info')
        return redirect(url_for('dashboard.index'))

    is_resubmission = (profile.verification_status == 'rejected')

    if request.method == 'POST':
        emission_data = request.form.get('emission_data')
        
        if not emission_data:
            flash('Please provide emission data.', 'warning')
            return render_template('verification/company_form.html', is_resubmission=is_resubmission)
            
        profile.emission_data = emission_data
        profile.verification_status = 'submitted'
        db.session.commit()
        
        if is_resubmission:
            flash('Resubmission successful! Your updated details are under review.', 'success')
        else:
            flash('Verification form submitted successfully. Please wait for admin approval.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('verification/company_form.html', is_resubmission=is_resubmission)

@verification_bp.route('/landowner', methods=['GET', 'POST'])
@login_required
def landowner_form():
    if current_user.role != 'landowner':
        return redirect(url_for('dashboard.index'))
        
    profile = current_user.landowner_profile
    # Allow access for 'pending' (first submission) or 'rejected' (resubmission)
    if profile.verification_status not in ('pending', 'rejected'):
        flash('Verification already submitted or approved.', 'info')
        return redirect(url_for('dashboard.index'))

    is_resubmission = (profile.verification_status == 'rejected')

    if request.method == 'POST':
        green_cover_details = request.form.get('green_cover_details')
        
        if not green_cover_details:
            flash('Please provide green cover details.', 'warning')
            return render_template('verification/landowner_form.html', is_resubmission=is_resubmission)
            
        profile.green_cover_details = green_cover_details
        profile.verification_status = 'submitted'
        db.session.commit()
        
        if is_resubmission:
            flash('Resubmission successful! Your updated details are under review.', 'success')
        else:
            flash('Verification form submitted successfully. Please wait for admin approval.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('verification/landowner_form.html', is_resubmission=is_resubmission)
