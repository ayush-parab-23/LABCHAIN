import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import uuid

from database.database import db
from database.models import Report, AuditLog
from routes.auth import role_required
from services.verification import verify_report_integrity, verify_report_by_file_only
from services.audit_service import log_event

hospital_bp = Blueprint('hospital', __name__)

from datetime import datetime, date

@hospital_bp.route('/hospital/dashboard')
@login_required
@role_required('HOSPITAL')
def dashboard():
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    # Verifications today
    verifications_today = AuditLog.query.filter(
        AuditLog.action.in_(['REPORT_VERIFIED', 'VERIFICATION_FAILED']),
        AuditLog.timestamp >= today_start
    ).count()

    # Tamper flags caught (failed verification count)
    tamper_flags = AuditLog.query.filter_by(action='VERIFICATION_FAILED').count()
    verified_total = AuditLog.query.filter_by(action='REPORT_VERIFIED').count()
    total_checks = verified_total + tamper_flags
    pass_rate = round((verified_total / total_checks * 100), 1) if total_checks > 0 else 100.0
    avg_verification_time = "0.4s"

    # Recent verifications feed
    recent_verifications = AuditLog.query.filter(
        AuditLog.action.in_(['REPORT_VERIFIED', 'VERIFICATION_FAILED'])
    ).order_by(AuditLog.timestamp.desc()).limit(6).all()

    return render_template(
        'hospital/dashboard.html',
        verifications_today=verifications_today,
        tamper_flags=tamper_flags,
        pass_rate=pass_rate,
        avg_verification_time=avg_verification_time,
        recent_verifications=recent_verifications
    )

@hospital_bp.route('/hospital/verify', methods=['POST'])
@login_required
@role_required('HOSPITAL')
def verify_report():
    report_id = request.form.get('report_id', '').strip()
    file = request.files.get('report_file')
    
    temp_file_path = None
    
    try:
        # Check if file was uploaded
        if file and file.filename != '':
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext != 'pdf':
                flash("Invalid file format. Only PDF files can be verified.", "danger")
                return redirect(url_for('hospital.dashboard'))
                
            # Save file temporarily to calculate hash
            temp_filename = f"temp_verify_{uuid.uuid4().hex}.pdf"
            temp_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], temp_filename)
            file.save(temp_file_path)

            if report_id:
                # Method C: Both Report ID and File
                result = verify_report_integrity(report_id, temp_file_path)
            else:
                # Method B: PDF File only
                result = verify_report_by_file_only(temp_file_path)
        elif report_id:
            # Method A: Report ID only
            result = verify_report_integrity(report_id)
        else:
            flash("Please enter a Report ID or upload a PDF file for verification.", "warning")
            return redirect(url_for('hospital.dashboard'))

        # Log audit logs in database
        # Since hospital users are logged in, we use current_user.id
        associated_report_id = None
        if result.get("reason") != "REPORT_NOT_FOUND" and result.get("reason") != "HASH_NOT_FOUND":
            # Lookup report row in DB to associate audit log
            rep = Report.query.filter_by(report_id=result.get("report_id")).first()
            if rep:
                associated_report_id = rep.id

        if result.get("verified"):
            log_event(
                current_user.id,
                "REPORT_VERIFIED",
                report_id=associated_report_id,
                details=f"Verified successfully. Method: {'PDF' if file else 'Report ID'}"
            )
        else:
            log_event(
                current_user.id,
                "VERIFICATION_FAILED",
                report_id=associated_report_id,
                details=f"Verification failed. Reason: {result.get('reason')}"
            )

        # Cleanup temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return render_template('hospital/verification_result.html', result=result)

    except Exception as e:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        flash(f"Verification error: {e}", "danger")
        return redirect(url_for('hospital.dashboard'))

# Public Route for scanning QR code (No Login Required)
@hospital_bp.route('/verify/<report_id>')
def public_verify(report_id):
    """
    Publicly verifies report integrity based on QR code scan.
    Doesn't expose sensitive info if report doesn't exist.
    """
    result = verify_report_integrity(report_id)
    
    # Audit log (since public user, log as system user or creator of report, or simple guest account id)
    # Let's associate it with the report if found
    associated_report_id = None
    rep = Report.query.filter_by(report_id=report_id).first()
    if rep:
        associated_report_id = rep.id
        # Log public verification event
        # If no user is logged in, log as a Guest Action (we can use user_id = report.lab_id or system account)
        log_event(
            rep.lab_id, # Log under issuing lab as "public view"
            "REPORT_VERIFIED" if result.get("verified") else "VERIFICATION_FAILED",
            report_id=associated_report_id,
            details=f"Public QR scan verification. Status: {result.get('status')}"
        )

    return render_template('hospital/verification_result.html', result=result, is_public=True)
