from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'LAB', 'PATIENT', 'HOSPITAL'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False) # e.g. PAT-1001
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reports = db.relationship('Report', backref='patient', lazy=True)

    def __repr__(self):
        return f"<Patient {self.patient_id} - {self.name}>"


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(50), unique=True, nullable=False) # e.g. LAB-2026-0001
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_type = db.Column(db.String(100), nullable=False) # e.g. CBC, Lipid Profile
    report_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(255), nullable=False) # Server file path
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash
    version = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(20), default='ACTIVE', nullable=False) # 'ACTIVE', 'SUPERSEDED', 'REVOKED'
    
    # Blockchain details
    blockchain_tx_hash = db.Column(db.String(66), nullable=True) # 0x... transaction hash
    block_number = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    versions = db.relationship('ReportVersion', backref='report', lazy=True, cascade="all, delete-orphan")
    audit_logs = db.relationship('AuditLog', backref='report', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Report {self.report_id} v{self.version} ({self.status})>"


class ReportVersion(db.Model):
    __tablename__ = 'report_versions'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'ACTIVE', 'SUPERSEDED', 'REVOKED'
    
    # Blockchain details
    blockchain_tx_hash = db.Column(db.String(66), nullable=True)
    block_number = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ReportVersion {self.report_id} v{self.version}>"


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False) # e.g. REPORT_CREATED, HASH_GENERATED, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} by User {self.user_id}>"
