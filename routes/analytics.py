from flask import Blueprint, jsonify
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta

from database.database import db
from database.models import Report, AuditLog
from routes.auth import role_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/analytics/summary')
@login_required
@role_required('LAB')
def summary_stats():
    total_reports = Report.query.count()
    active_reports = Report.query.filter_by(status='ACTIVE').count()
    superseded_reports = Report.query.filter_by(status='SUPERSEDED').count()
    revoked_reports = Report.query.filter_by(status='REVOKED').count()
    
    # Audit log counts
    verified_count = AuditLog.query.filter_by(action='REPORT_VERIFIED').count()
    failed_count = AuditLog.query.filter_by(action='VERIFICATION_FAILED').count()
    
    # Threshold anomaly detection
    # If verifications in the last hour exceed 30, trigger anomaly indicator
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_verifications = AuditLog.query.filter(
        AuditLog.action.in_(['REPORT_VERIFIED', 'VERIFICATION_FAILED']),
        AuditLog.timestamp >= one_hour_ago
    ).count()
    
    is_anomaly = recent_verifications > 30

    return jsonify({
        "total_reports": total_reports,
        "active_reports": active_reports,
        "superseded_reports": superseded_reports,
        "revoked_reports": revoked_reports,
        "verified_count": verified_count,
        "failed_count": failed_count,
        "recent_hour_verifications": recent_verifications,
        "is_anomaly": is_anomaly
    })

@analytics_bp.route('/api/analytics/test_types')
@login_required
@role_required('LAB')
def test_types_data():
    """Returns number of reports grouped by test type."""
    results = db.session.query(
        Report.test_type, 
        func.count(Report.id)
    ).group_by(Report.test_type).all()
    
    labels = [r[0] for r in results]
    counts = [r[1] for r in results]
    
    return jsonify({
        "labels": labels,
        "data": counts
    })

@analytics_bp.route('/api/analytics/verification_ratio')
@login_required
@role_required('LAB')
def verification_ratio():
    """Returns ratio of successful vs failed verification attempts."""
    verified = AuditLog.query.filter_by(action='REPORT_VERIFIED').count()
    failed = AuditLog.query.filter_by(action='VERIFICATION_FAILED').count()
    
    return jsonify({
        "labels": ["Verified (Success)", "Failed (Mismatch/Tampered)"],
        "data": [verified, failed]
    })

@analytics_bp.route('/api/analytics/monthly_trends')
@login_required
@role_required('LAB')
def monthly_trends():
    """Returns number of reports registered by month."""
    # Group by month (SQLite compatible strftime)
    results = db.session.query(
        func.strftime('%Y-%m', Report.created_at).label('month'),
        func.count(Report.id)
    ).group_by('month').order_by('month').all()
    
    labels = [r[0] for r in results]
    counts = [r[1] for r in results]
    
    return jsonify({
        "labels": labels,
        "data": counts
    })

@analytics_bp.route('/api/analytics/activity_log')
@login_required
@role_required('LAB')
def activity_log():
    """Returns verification activity over the last 7 days."""
    labels = []
    success_data = []
    failure_data = []
    
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        labels.append(day.strftime("%a (%d %b)"))
        
        # Get start/end timestamps for the day
        start_dt = datetime.combine(day, datetime.min.time())
        end_dt = datetime.combine(day, datetime.max.time())
        
        successes = AuditLog.query.filter(
            AuditLog.action == 'REPORT_VERIFIED',
            AuditLog.timestamp >= start_dt,
            AuditLog.timestamp <= end_dt
        ).count()
        
        failures = AuditLog.query.filter(
            AuditLog.action == 'VERIFICATION_FAILED',
            AuditLog.timestamp >= start_dt,
            AuditLog.timestamp <= end_dt
        ).count()
        
        success_data.append(successes)
        failure_data.append(failures)
        
    return jsonify({
        "labels": labels,
        "success": success_data,
        "failure": failure_data
    })
