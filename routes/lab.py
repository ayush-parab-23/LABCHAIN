import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import uuid

from database.database import db
from database.models import Patient, Report, ReportVersion, AuditLog, User
from routes.auth import role_required
from services.hashing import calculate_sha256
from services.qr_service import generate_report_qr_base64
from services.audit_service import log_event
from blockchain.blockchain_service import BlockchainService, BlockchainConnectionError

lab_bp = Blueprint('lab', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@lab_bp.route('/lab/dashboard')
@login_required
@role_required('LAB')
def dashboard():
    # Gather statistics
    total_reports = Report.query.count()
    active_reports = Report.query.filter_by(status='ACTIVE').count()
    corrected_reports = Report.query.filter(Report.version > 1).count()
    
    # Reports anchored this month
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    reports_this_month = Report.query.filter(Report.created_at >= start_of_month).count()

    # Pending anchoring
    pending_reports = Report.query.filter_by(status='PENDING').count()

    # Revocation rate
    revoked_count = Report.query.filter_by(status='REVOKED').count()
    revocation_rate = round((revoked_count / total_reports * 100), 1) if total_reports > 0 else 0.0

    # Avg anchoring time (EVM local node block interval)
    avg_anchoring_time = "< 2s"

    # Top test types
    from sqlalchemy import func
    top_tests_raw = db.session.query(
        Report.test_type, func.count(Report.id)
    ).group_by(Report.test_type).order_by(func.count(Report.id).desc()).limit(4).all()
    max_test_count = max([t[1] for t in top_tests_raw]) if top_tests_raw else 1
    top_test_types = [
        {"name": t[0], "count": t[1], "pct": int((t[1] / max_test_count) * 100)}
        for t in top_tests_raw
    ]

    # Audit verifications
    verification_attempts = AuditLog.query.filter(
        AuditLog.action.in_(['REPORT_VERIFIED', 'VERIFICATION_FAILED'])
    ).count()

    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(6).all()
    
    # Query blockchain connection state
    blockchain = BlockchainService()
    blockchain_connected = blockchain.is_connected()
    latest_block = blockchain.get_latest_block_number() if blockchain_connected else 0
    contract_address = blockchain.contract_address

    return render_template(
        'lab/dashboard.html',
        total_reports=total_reports,
        active_reports=active_reports,
        corrected_reports=corrected_reports,
        reports_this_month=reports_this_month,
        pending_reports=pending_reports,
        revocation_rate=revocation_rate,
        avg_anchoring_time=avg_anchoring_time,
        top_test_types=top_test_types,
        verification_attempts=verification_attempts,
        recent_reports=recent_reports,
        blockchain_connected=blockchain_connected,
        latest_block=latest_block,
        contract_address=contract_address
    )

@lab_bp.route('/lab/patients')
@login_required
@role_required('LAB')
def patients():
    search = request.args.get('search', '').strip()
    if search:
        patient_list = Patient.query.filter(
            (Patient.name.like(f"%{search}%")) | 
            (Patient.patient_id.like(f"%{search}%"))
        ).all()
    else:
        patient_list = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('lab/patients.html', patients=patient_list, search=search)

@lab_bp.route('/lab/patients/create', methods=['GET', 'POST'])
@login_required
@role_required('LAB')
def create_patient():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        gender = request.form.get('gender')

        if not name or not age or not gender:
            flash("All fields are required.", "danger")
            return redirect(url_for('lab.create_patient'))

        # Generate unique patient ID
        # e.g., PAT-1000 + number of current patients
        count = Patient.query.count()
        patient_id = f"PAT-{1000 + count + 1}"

        try:
            patient = Patient(
                patient_id=patient_id,
                name=name,
                age=int(age),
                gender=gender
            )
            db.session.add(patient)
            db.session.commit()
            log_event(current_user.id, "PATIENT_REGISTERED", details=f"Registered patient: {patient_id}")
            flash(f"Patient {name} ({patient_id}) registered successfully.", "success")
            return redirect(url_for('lab.patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error registering patient: {e}", "danger")
            return redirect(url_for('lab.create_patient'))

    return render_template('lab/register_patient.html')

@lab_bp.route('/lab/reports')
@login_required
@role_required('LAB')
def reports():
    report_list = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('lab/reports.html', reports=report_list)

@lab_bp.route('/lab/reports/create', methods=['GET', 'POST'])
@login_required
@role_required('LAB')
def create_report():
    patients = Patient.query.all()
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        test_type = request.form.get('test_type')
        report_date_str = request.form.get('report_date')
        
        # Check file
        if 'report_file' not in request.files:
            flash("No file part provided.", "danger")
            return redirect(request.url)
            
        file = request.files['report_file']
        
        if file.filename == '':
            flash("No selected file.", "danger")
            return redirect(request.url)
            
        if not (patient_id and test_type and report_date_str):
            flash("All text fields are required.", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
                
                # Generate unique Report ID
                # e.g., LAB-2026-0001
                year = datetime.now().year
                count = Report.query.count()
                report_id = f"LAB-{year}-{1000 + count + 1}"
                
                # Secure and randomize filename
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{report_id}_v1_{uuid.uuid4().hex[:8]}.{ext}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save file locally
                file.save(file_path)
                
                # Calculate Hash
                file_hash = calculate_sha256(file_path)
                
                # Save report locally in PENDING state
                report = Report(
                    report_id=report_id,
                    patient_id=int(patient_id),
                    lab_id=current_user.id,
                    test_type=test_type,
                    report_date=report_date,
                    file_path=unique_filename,
                    file_hash=file_hash,
                    version=1,
                    status='PENDING'
                )
                db.session.add(report)
                db.session.commit()
                
                log_event(current_user.id, "REPORT_CREATED", report_id=report.id, details=f"Report created in database: {report_id}")
                log_event(current_user.id, "HASH_GENERATED", report_id=report.id, details=f"SHA-256 hash generated: {file_hash}")
                
                # Redirect to confirmation step
                return redirect(url_for('lab.confirm_report', report_id=report.report_id))
            except Exception as e:
                db.session.rollback()
                flash(f"Error creating report record: {e}", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file type. Only PDF reports are accepted.", "danger")
            return redirect(request.url)

    return render_template('lab/create_report.html', patients=patients)

@lab_bp.route('/lab/reports/<report_id>/confirm')
@login_required
@role_required('LAB')
def confirm_report(report_id):
    report = Report.query.filter_by(report_id=report_id).first_or_404()
    patient = Patient.query.get(report.patient_id)
    return render_template('lab/confirm_report.html', report=report, patient=patient)

@lab_bp.route('/lab/reports/<report_id>/register', methods=['POST'])
@login_required
@role_required('LAB')
def register_on_blockchain(report_id):
    report = Report.query.filter_by(report_id=report_id).first_or_404()
    
    if report.status != 'PENDING':
        flash("This report is already registered or modified.", "warning")
        return redirect(url_for('lab.report_detail', report_id=report.report_id))
        
    blockchain = BlockchainService()
    if not blockchain.is_connected():
        flash("Blockchain service is offline. Unable to register report.", "danger")
        return redirect(url_for('lab.confirm_report', report_id=report.report_id))
        
    try:
        # Submit transaction to contract
        tx_hash, block_number = blockchain.register_report(
            report.report_id,
            report.file_hash,
            f"LAB-{report.lab_id}"
        )
        
        # Update database
        report.blockchain_tx_hash = tx_hash
        report.block_number = block_number
        report.status = 'ACTIVE'
        db.session.commit()
        
        log_event(
            current_user.id,
            "BLOCKCHAIN_REGISTERED",
            report_id=report.id,
            details=f"Registered on blockchain. Block: {block_number}, Tx: {tx_hash}"
        )
        
        flash("Medical report successfully registered on the blockchain!", "success")
        return redirect(url_for('lab.report_detail', report_id=report.report_id))
        
    except BlockchainConnectionError as e:
        flash(f"Blockchain connection lost: {e}", "danger")
        return redirect(url_for('lab.confirm_report', report_id=report.report_id))
    except Exception as e:
        db.session.rollback()
        flash(f"Smart contract transaction failed: {e}", "danger")
        return redirect(url_for('lab.confirm_report', report_id=report.report_id))

@lab_bp.route('/lab/reports/<report_id>/correct', methods=['GET', 'POST'])
@login_required
@role_required('LAB')
def correct_report(report_id):
    report = Report.query.filter_by(report_id=report_id).first_or_404()
    patient = Patient.query.get(report.patient_id)
    
    if report.status != 'ACTIVE':
        flash("Only ACTIVE reports can be corrected.", "danger")
        return redirect(url_for('lab.report_detail', report_id=report.report_id))
        
    if request.method == 'POST':
        if 'report_file' not in request.files:
            flash("No file part provided.", "danger")
            return redirect(request.url)
            
        file = request.files['report_file']
        
        if file.filename == '':
            flash("No selected file.", "danger")
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            blockchain = BlockchainService()
            if not blockchain.is_connected():
                flash("Blockchain is offline. Corrections require active blockchain connection.", "danger")
                return redirect(request.url)
                
            try:
                # Save the new file
                next_version = report.version + 1
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{report.report_id}_v{next_version}_{uuid.uuid4().hex[:8]}.{ext}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Hash of corrected file
                new_hash = calculate_sha256(file_path)
                
                # Check for duplicate hash
                if new_hash == report.file_hash:
                    flash("The uploaded file is identical to the current version. No corrections detected.", "warning")
                    return redirect(request.url)
                
                # 1. Update blockchain first (to keep atomic consistency)
                tx_hash, block_number = blockchain.update_report_version(report.report_id, new_hash)
                
                # 2. Archive current version to ReportVersion table
                old_version = ReportVersion(
                    report_id=report.id,
                    version=report.version,
                    file_hash=report.file_hash,
                    file_path=report.file_path,
                    status='SUPERSEDED',
                    blockchain_tx_hash=report.blockchain_tx_hash,
                    block_number=report.block_number
                )
                db.session.add(old_version)
                
                # 3. Update main Report table with new version details
                report.version = next_version
                report.file_hash = new_hash
                report.file_path = unique_filename
                report.blockchain_tx_hash = tx_hash
                report.block_number = block_number
                report.status = 'ACTIVE'
                
                db.session.commit()
                
                # Log events
                log_event(current_user.id, "VERSION_CREATED", report_id=report.id, details=f"Issued corrected version {next_version}")
                log_event(current_user.id, "REPORT_SUPERSEDED", report_id=report.id, details=f"Version {next_version-1} superseded on blockchain.")
                
                flash(f"Report version {next_version} registered on blockchain.", "success")
                return redirect(url_for('lab.report_detail', report_id=report.report_id))
                
            except BlockchainConnectionError as e:
                flash(f"Blockchain error: {e}", "danger")
                return redirect(request.url)
            except Exception as e:
                db.session.rollback()
                flash(f"Error issuing corrected report: {e}", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file type. Only PDFs are allowed.", "danger")
            return redirect(request.url)
            
    return render_template('lab/correct_report.html', report=report, patient=patient)

@lab_bp.route('/lab/reports/<report_id>/revoke', methods=['POST'])
@login_required
@role_required('LAB')
def revoke_report(report_id):
    report = Report.query.filter_by(report_id=report_id).first_or_404()
    
    if report.status != 'ACTIVE':
        flash("Only ACTIVE reports can be revoked.", "danger")
        return redirect(url_for('lab.report_detail', report_id=report.report_id))
        
    blockchain = BlockchainService()
    if not blockchain.is_connected():
        flash("Blockchain is offline. Revocations require active blockchain connection.", "danger")
        return redirect(url_for('lab.report_detail', report_id=report.report_id))
        
    try:
        tx_hash, block_number = blockchain.revoke_report(report.report_id)
        
        # Update DB
        report.status = 'REVOKED'
        report.blockchain_tx_hash = tx_hash
        report.block_number = block_number
        db.session.commit()
        
        log_event(current_user.id, "REPORT_REVOKED", report_id=report.id, details=f"Report revoked on blockchain.")
        flash("Report revoked successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to revoke report: {e}", "danger")
        
    return redirect(url_for('lab.report_detail', report_id=report.report_id))

@lab_bp.route('/lab/reports/<report_id>')
@login_required
@role_required('LAB')
def report_detail(report_id):
    report = Report.query.filter_by(report_id=report_id).first_or_404()
    patient = Patient.query.get(report.patient_id)
    
    # QR code base64 encoding (e.g. host: http://127.0.0.1:5000)
    host_url = request.host_url.rstrip('/')
    qr_base64 = generate_report_qr_base64(report.report_id, host_url)
    
    # Fetch database version history
    versions = ReportVersion.query.filter_by(report_id=report.id).order_by(ReportVersion.version.desc()).all()
    
    # Fetch Audit Trail
    audit_logs = AuditLog.query.filter_by(report_id=report.id).order_by(AuditLog.timestamp.desc()).all()
    
    return render_template(
        'lab/report_detail.html',
        report=report,
        patient=patient,
        qr_code=qr_base64,
        versions=versions,
        audit_logs=audit_logs
    )

@lab_bp.route('/lab/audit_logs')
@login_required
@role_required('LAB')
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('lab/audit_logs.html', logs=logs)

@lab_bp.route('/lab/analytics')
@login_required
@role_required('LAB')
def analytics():
    return render_template('lab/analytics.html')
