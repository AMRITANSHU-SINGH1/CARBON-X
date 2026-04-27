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
    if profile.verification_status != 'pending':
        flash('Verification already submitted or approved.', 'info')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        emission_data = request.form.get('emission_data')
        
        # In a real setup, we would do some validation here
        if not emission_data:
            flash('Please provide emission data.', 'warning')
            return render_template('verification/company_form.html')
            
        profile.emission_data = emission_data
        profile.verification_status = 'submitted'
        db.session.commit()
        
        flash('Verification form submitted successfully. Please wait for admin approval.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('verification/company_form.html')

@verification_bp.route('/landowner', methods=['GET', 'POST'])
@login_required
def landowner_form():
    if current_user.role != 'landowner':
        return redirect(url_for('dashboard.index'))
        
    profile = current_user.landowner_profile
    if profile.verification_status != 'pending':
        flash('Verification already submitted or approved.', 'info')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        green_cover_details = request.form.get('green_cover_details')
        
        if not green_cover_details:
            flash('Please provide green cover details.', 'warning')
            return render_template('verification/landowner_form.html')
            
        profile.green_cover_details = green_cover_details
        profile.verification_status = 'submitted'
        db.session.commit()
        
        flash('Verification form submitted successfully. Please wait for admin approval.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('verification/landowner_form.html')
