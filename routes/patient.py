import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user

from database.database import db
from database.models import Patient, Report, ReportVersion, AuditLog
from routes.auth import role_required
from services.qr_service import generate_report_qr_base64
from services.audit_service import log_event

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patient/dashboard')
@login_required
@role_required('PATIENT')
def dashboard():
    # Find patient record corresponding to the logged-in User (by name match)
    patient = Patient.query.filter_by(name=current_user.name).first()
    
    if not patient:
        flash("Could not associate your login with a patient record. Contact administrator.", "warning")
        return render_template('patient/dashboard.html', patient=None, reports=[])
        
    reports = Report.query.filter_by(patient_id=patient.id).order_by(Report.created_at.desc()).all()
    reports_count = len(reports)
    latest_status = reports[0].status if reports else "None"
    total_versions = sum([r.version for r in reports]) if reports else 0
    versions_per_report = round(total_versions / reports_count, 1) if reports_count > 0 else 1.0

    # Count QR checks / verifications on this patient's reports
    report_ids = [r.id for r in reports]
    qr_scans = AuditLog.query.filter(
        AuditLog.report_id.in_(report_ids),
        AuditLog.action.in_(['QR_GENERATED', 'REPORT_VERIFIED'])
    ).count() if report_ids else 0

    # Generate QR codes dictionary for fast popup display
    host_url = request.host_url.rstrip('/')
    qr_map = {r.report_id: generate_report_qr_base64(r.report_id, host_url) for r in reports}

    return render_template(
        'patient/dashboard.html',
        patient=patient,
        reports=reports,
        reports_count=reports_count,
        latest_status=latest_status,
        versions_per_report=versions_per_report,
        qr_scans=qr_scans,
        qr_map=qr_map
    )

@patient_bp.route('/patient/reports/<report_id>')
@login_required
@role_required('PATIENT')
def report_detail(report_id):
    report = Report.query.filter_by(report_id=report_id).first_or_404()
    patient = Patient.query.filter_by(name=current_user.name).first()
    
    # Secure access check: ensure patient only accesses their own report
    if not patient or report.patient_id != patient.id:
        return render_template(
            'error.html',
            error_title="Access Denied",
            error_message="You are not authorized to view this report."
        ), 403

    host_url = request.host_url.rstrip('/')
    qr_base64 = generate_report_qr_base64(report.report_id, host_url)
    
    # Fetch historical versions
    versions = ReportVersion.query.filter_by(report_id=report.id).order_by(ReportVersion.version.desc()).all()
    
    log_event(
        current_user.id,
        "QR_GENERATED",
        report_id=report.id,
        details="Patient generated QR verification code"
    )

    return render_template(
        'patient/report_detail.html',
        report=report,
        patient=patient,
        qr_code=qr_base64,
        versions=versions
    )

@patient_bp.route('/patient/reports/<report_id>/download')
@login_required
@role_required('PATIENT', 'LAB', 'HOSPITAL') # Allow all authorized roles to download
def download_report(report_id):
    report = Report.query.filter_by(report_id=report_id).first_or_404()
    
    # Check permissions
    if current_user.role == 'PATIENT':
        patient = Patient.query.filter_by(name=current_user.name).first()
        if not patient or report.patient_id != patient.id:
            return render_template(
                'error.html',
                error_title="Access Denied",
                error_message="You are not authorized to download this report."
            ), 403

    # Send file securely
    directory = current_app.config['UPLOAD_FOLDER']
    filename = os.path.basename(report.file_path)
    
    return send_from_directory(
        directory,
        filename,
        as_attachment=True,
        download_name=f"{report.report_id}_v{report.version}.pdf"
    )
