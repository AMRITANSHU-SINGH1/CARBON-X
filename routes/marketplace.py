from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import CarbonCredit, EmissionReport

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/')
@login_required
def index():
    if current_user.role != 'company':
        flash('Access denied. Only companies can access the marketplace.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Fetch active credits with left_carbon_credits > 0
    active_credits = CarbonCredit.query.filter(CarbonCredit.left_carbon_credits > 0).all()
    
    # Fetch company wallet balance and latest emission report
    company_profile = current_user.company_profile
    wallet_balance = company_profile.wallet_balance if company_profile else 0.0
    
    latest_report = EmissionReport.query.filter_by(
        company_id=current_user.id,
        status='Submitted'
    ).order_by(EmissionReport.reported_date.desc()).first()
    
    required_credits = latest_report.Required_credits if latest_report else 0.0

    return render_template('marketplace.html', 
                           credits=active_credits, 
                           wallet_balance=wallet_balance, 
                           required_credits=required_credits)
