from database.database import db
from database.models import AuditLog

def log_event(user_id, action, report_id=None, details=None):
    """
    Logs an audit event in the database for traceability and security.
    """
    try:
        log = AuditLog(
            user_id=user_id,
            report_id=report_id,
            action=action,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Fail-safe: print to server console, do not throw error to user
        print(f"Failed to write audit log: {e}")
