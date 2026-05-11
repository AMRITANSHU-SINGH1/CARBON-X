from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from models import User, SubordinateProfile, VerificationTask, CarbonAssessment, CarbonCredit
from datetime import datetime
import os
import json

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

@dashboard_bp.route('/landowners')
@login_required
def landowners_list():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    landowners = User.query.filter_by(role='landowner').all()
    
    authorised = [l for l in landowners if l.landowner_profile and (l.landowner_profile.admin_approved or l.landowner_profile.verification_status == 'approved')]
    pending = [l for l in landowners if not l.landowner_profile or not (l.landowner_profile.admin_approved or l.landowner_profile.verification_status == 'approved')]
    
    return render_template('dashboard/landowners_list.html', authorised=authorised, pending=pending)

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

@dashboard_bp.route('/allocations', methods=['GET', 'POST'])
@login_required
def allocations():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        subordinate_id = request.form.get('subordinate_id')
        target_id = request.form.get('target_id')
        target_type = request.form.get('target_type') # 'company' or 'landowner'
        due_date_str = request.form.get('due_date')
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format.', 'danger')
                return redirect(url_for('dashboard.allocations'))
        
        if not subordinate_id or not target_id or not target_type:
            flash('Invalid assignment data.', 'danger')
            return redirect(url_for('dashboard.allocations'))
            
        # Create verification task
        task = VerificationTask(
            subordinate_id=subordinate_id,
            due_date=due_date
        )
        if target_type == 'company':
            task.company_id = target_id
        elif target_type == 'landowner':
            task.landowner_id = target_id
            
        db.session.add(task)
        db.session.commit()
        flash('Task assigned successfully.', 'success')
        return redirect(url_for('dashboard.allocations'))

    # Get unassigned companies
    companies = User.query.filter_by(role='company').all()
    pending_companies = [
        c for c in companies 
        if c.company_profile 
        and c.company_profile.verification_status == 'submitted'
        and not VerificationTask.query.filter_by(company_id=c.id, status='assigned').first()
        and not VerificationTask.query.filter_by(company_id=c.id, status='in_progress').first()
    ]
    
    # Get unassigned landowners
    landowners = User.query.filter_by(role='landowner').all()
    pending_landowners = [
        l for l in landowners 
        if l.landowner_profile 
        and l.landowner_profile.verification_status == 'submitted'
        and not VerificationTask.query.filter_by(landowner_id=l.id, status='assigned').first()
        and not VerificationTask.query.filter_by(landowner_id=l.id, status='in_progress').first()
    ]
    
    # Get all subordinates
    subordinates = User.query.filter_by(role='subordinate').all()
    
    return render_template('dashboard/allocations.html', 
                          companies=pending_companies, 
                          landowners=pending_landowners, 
                          subordinates=subordinates)

@dashboard_bp.route('/tasks')
@login_required
def tasks():
    if current_user.role != 'subordinate':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    tasks = VerificationTask.query.filter_by(subordinate_id=current_user.id).order_by(VerificationTask.created_at.desc()).all()
    
    pending_tasks = [t for t in tasks if t.status in ('assigned', 'in_progress')]
    completed_tasks = [t for t in tasks if t.status in ('completed', 'rejected')]
    
    return render_template('dashboard/tasks.html', pending_tasks=pending_tasks, completed_tasks=completed_tasks)

@dashboard_bp.route('/allocated_tasks')
@login_required
def allocated_tasks():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    tasks = VerificationTask.query.order_by(VerificationTask.created_at.desc()).all()
    return render_template('dashboard/allocated_tasks.html', tasks=tasks)

# ── Wood density lookup (g/cm³) ─────────────────────────────────────────────
WOOD_DENSITY = {
    'teak': 0.65, 'neem': 0.72, 'mango': 0.60,
    'eucalyptus': 0.55, 'bamboo': 0.40, 'peepal': 0.58,
    'banyan': 0.60, 'sheesham': 0.77, 'sal': 0.80,
    'pine': 0.45, 'oak': 0.60, 'sandalwood': 0.90,
    'mahogany': 0.70, 'acacia': 0.75, 'arjun': 0.68,
}
DEFAULT_DENSITY = 0.60

def _calc_net_credits(species_rows, fertilizer_kg, diesel_l):
    """Returns (gross, net) in tCO2e."""
    total_stock = 0.0
    for row in species_rows:
        rho    = WOOD_DENSITY.get(row['species'].strip().lower(), DEFAULT_DENSITY)
        count  = int(row['count'])
        dbh    = float(row['dbh'])
        height = float(row['height'])
        agb    = 0.0673 * ((rho * dbh ** 2 * height) ** 0.976)
        total_stock += (agb * 1.25) * 0.5 * count

    gross  = total_stock * 3.67
    net    = gross - (gross * 0.15) - (fertilizer_kg * 5.35) - (diesel_l * 2.68)
    return round(gross, 4), round(max(net, 0.0), 4)


@dashboard_bp.route('/task/<int:task_id>/process', methods=['GET', 'POST'])
@login_required
def process_task(task_id):
    if current_user.role != 'subordinate':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    task = VerificationTask.query.get_or_404(task_id)
    if task.subordinate_id != current_user.id:
        flash('Unauthorized to process this task.', 'danger')
        return redirect(url_for('dashboard.tasks'))
        
    if request.method == 'POST':
        if task.company_id:
            # Handle company file upload
            document_file = request.files.get('document')
            document_path = None
            if document_file and document_file.filename:
                filename = secure_filename(document_file.filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                unique_filename = f"task_{task.id}_{timestamp}_{filename}"
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                document_file.save(save_path)
                document_path = unique_filename
                
            form_data = {
                'sources_of_emission': request.form.get('sources_of_emission'),
                'amount_of_emission': request.form.get('amount_of_emission'),
                'daily_emission': request.form.get('daily_emission'),
                'is_verified': request.form.get('is_verified') == 'on'
            }
            task.report_data = json.dumps(form_data)
            if document_path:
                task.document_path = document_path
                
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            db.session.commit()
            flash('Verification report submitted successfully.', 'success')
            return redirect(url_for('dashboard.tasks'))
            
        elif task.landowner_id:
            # Handle landowner carbon assessment
            land_name = request.form.get('land_name', '').strip()
            total_area = request.form.get('total_area', '0').strip()
            fertilizer_kg = request.form.get('nitrogen_fertilizer', '0').strip()
            diesel_l = request.form.get('diesel_liters', '0').strip()

            species_names = request.form.getlist('species_name[]')
            tree_counts = request.form.getlist('tree_count[]')
            dbh_values = request.form.getlist('avg_dbh[]')
            height_values = request.form.getlist('avg_height[]')

            if not land_name or not species_names:
                flash('Land Name and at least one tree species are required.', 'danger')
                return redirect(url_for('dashboard.process_task', task_id=task.id))

            species_rows = []
            for i in range(len(species_names)):
                try:
                    species_rows.append({
                        'species': species_names[i].strip() or 'unknown',
                        'count': int(tree_counts[i]) if i < len(tree_counts) else 0,
                        'dbh': float(dbh_values[i]) if i < len(dbh_values) else 0.0,
                        'height': float(height_values[i]) if i < len(height_values) else 0.0,
                    })
                except (ValueError, IndexError):
                    flash('Invalid value in species data. Please check your entries.', 'danger')
                    return redirect(url_for('dashboard.process_task', task_id=task.id))

            try:
                total_area = float(total_area)
                fertilizer_kg = float(fertilizer_kg)
                diesel_l = float(diesel_l)
            except ValueError:
                flash('Invalid value in operational data.', 'danger')
                return redirect(url_for('dashboard.process_task', task_id=task.id))

            gross, net = _calc_net_credits(species_rows, fertilizer_kg, diesel_l)
            raw_data_json = json.dumps(species_rows)

            assessment = CarbonAssessment(
                task_id=task.id,
                subordinate_id=current_user.id,
                landowner_id=task.landowner_id,
                land_name=land_name,
                total_area_ha=total_area,
                raw_data=raw_data_json,
                nitrogen_fertilizer_kg=fertilizer_kg,
                diesel_liters=diesel_l,
                gross_credits=gross,
                total_credits_calculated=net,
                status='Pending'
            )
            db.session.add(assessment)
            db.session.flush() # Get assessment ID for the credit record

            # Create the Carbon Credit record
            credit = CarbonCredit(
                carbon_assessment_id=assessment.id,
                subordinate_id=current_user.id,
                landowner_id=task.landowner_id,
                land_name=land_name,
                total_area_ha=total_area,
                raw_data=raw_data_json,
                gross_credits=gross,
                total_credits_calculated=net,
                status='Active'
            )
            db.session.add(credit)

            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            task.report_data = json.dumps({'gross_credits': gross, 'net_credits': net})
            
            # Update landowner profile verification status
            if task.landowner and task.landowner.landowner_profile:
                task.landowner.landowner_profile.verification_status = 'submitted'

            db.session.commit()
            flash(f'Assessment submitted successfully! {net:.4f} tCO2e active credits registered.', 'success')
            return redirect(url_for('dashboard.tasks'))

    # GET request
    if task.company_id:
        return render_template('dashboard/process_task.html', task=task)
    elif task.landowner_id:
        return render_template('dashboard/subordinate_form.html', task=task)
    
    return redirect(url_for('dashboard.tasks'))



@dashboard_bp.route('/task/<int:task_id>/reject', methods=['POST'])
@login_required
def reject_task(task_id):
    """Subordinate rejects an assigned task with a reason."""
    if current_user.role != 'subordinate':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    task = VerificationTask.query.get_or_404(task_id)
    if task.subordinate_id != current_user.id:
        flash('Unauthorized to reject this task.', 'danger')
        return redirect(url_for('dashboard.tasks'))

    if task.status not in ('assigned', 'in_progress'):
        flash('This task cannot be rejected in its current state.', 'warning')
        return redirect(url_for('dashboard.tasks'))

    reason = request.form.get('rejection_reason', '').strip()
    if not reason:
        flash('A rejection reason is required.', 'danger')
        return redirect(url_for('dashboard.tasks'))

    task.status = 'rejected'
    task.rejection_reason = reason
    task.rejected_by = 'subordinate'
    task.completed_at = datetime.utcnow()

    # Reset the profile verification status so the client knows
    if task.company_id and task.company and task.company.company_profile:
        task.company.company_profile.verification_status = 'rejected'
    elif task.landowner_id and task.landowner and task.landowner.landowner_profile:
        task.landowner.landowner_profile.verification_status = 'rejected'

    db.session.commit()
    flash('Task has been rejected successfully. The client has been notified.', 'success')
    return redirect(url_for('dashboard.tasks'))


@dashboard_bp.route('/task/<int:task_id>/admin_reject', methods=['POST'])
@login_required
def admin_reject_task(task_id):
    """Admin rejects any task from the allocated tasks / allocations queue."""
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    task = VerificationTask.query.get_or_404(task_id)

    if task.status == 'rejected':
        flash('This task is already rejected.', 'warning')
        return redirect(url_for('dashboard.allocated_tasks'))

    reason = request.form.get('rejection_reason', '').strip()
    if not reason:
        flash('A rejection reason is required.', 'danger')
        return redirect(url_for('dashboard.allocated_tasks'))

    task.status = 'rejected'
    task.rejection_reason = reason
    task.rejected_by = 'admin'
    task.completed_at = datetime.utcnow()

    # Reset the profile verification status so the client knows
    if task.company_id and task.company and task.company.company_profile:
        task.company.company_profile.verification_status = 'rejected'
    elif task.landowner_id and task.landowner and task.landowner.landowner_profile:
        task.landowner.landowner_profile.verification_status = 'rejected'

    db.session.commit()
    flash('Task has been rejected. The subordinate and client have been notified.', 'success')
    return redirect(url_for('dashboard.allocated_tasks'))
