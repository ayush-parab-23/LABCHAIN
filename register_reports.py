import os
import shutil
import datetime
from app import create_app
from database.database import db
from database.models import User, Patient, Report, ReportVersion, AuditLog
from blockchain.blockchain_service import BlockchainService
from services.hashing import calculate_sha256

def register_reports():
    app = create_app()
    with app.app_context():
        print("Checking lab administrator credentials...")
        lab_user = User.query.filter_by(role="LAB").first()
        if not lab_user:
            print("Error: No laboratory user found in the database. Please run seed.py first.")
            return

        print(f"Using Lab Admin: {lab_user.name} (ID: {lab_user.id})")

        # Ensure uploads folder exists
        uploads_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Uploads directory verified: {uploads_dir}")

        # Clear existing reports in DB for a completely clean start
        print("Clearing existing report and audit data from database...")
        AuditLog.query.delete()
        ReportVersion.query.delete()
        Report.query.delete()
        db.session.commit()
        print("Existing database report logs cleared.")

        # Setup blockchain service connection
        blockchain = BlockchainService()
        if not blockchain.is_connected():
            print("Error: Unable to connect to local Hardhat blockchain. Please make sure the node is running.")
            return

        reports_to_register = [
            {"patient_id": "PAT-2001", "filename": "Ayush_report.pdf", "test_type": "Lipid Profile", "report_id": "LAB-2026-0001"},
            {"patient_id": "PAT-2002", "filename": "Arya_report.pdf", "test_type": "Thyroid Profile", "report_id": "LAB-2026-0002"},
            {"patient_id": "PAT-2003", "filename": "Piyush_report.pdf", "test_type": "Liver Function Test", "report_id": "LAB-2026-0003"},
            {"patient_id": "PAT-2004", "filename": "Rohan_report.pdf", "test_type": "Kidney Function Test", "report_id": "LAB-2026-0004"},
            {"patient_id": "PAT-2005", "filename": "Archie_report.pdf", "test_type": "Complete Blood Count", "report_id": "LAB-2026-0005"},
            {"patient_id": "PAT-2006", "filename": "Manaswi_report.pdf", "test_type": "Diabetes Panel", "report_id": "LAB-2026-0006"},
            {"patient_id": "PAT-2007", "filename": "Riya_report.pdf", "test_type": "Vitamin Panel", "report_id": "LAB-2026-0007"},
        ]

        downloads_dir = os.path.join(app.root_path, "downloads")

        for item in reports_to_register:
            # Check patient
            patient = Patient.query.filter_by(patient_id=item["patient_id"]).first()
            if not patient:
                print(f"Error: Patient {item['patient_id']} not found in DB. Skipping.")
                continue

            source_path = os.path.join(downloads_dir, item["filename"])
            if not os.path.exists(source_path):
                print(f"Error: Report file {source_path} not found. Skipping.")
                continue

            # Calculate hash
            file_hash = calculate_sha256(source_path)
            print(f"Hashed {item['filename']} -> {file_hash}")

            # Define destination path and copy
            dest_filename = f"{item['report_id']}.pdf"
            dest_path = os.path.join(uploads_dir, dest_filename)
            shutil.copy2(source_path, dest_path)
            print(f"Copied to uploads: {dest_path}")

            # Register on Blockchain
            print(f"Submitting registration transaction to blockchain for {item['report_id']}...")
            tx_hash, block_number = blockchain.register_report(
                report_id=item["report_id"],
                report_hash=file_hash,
                lab_id=f"LAB-{lab_user.id}"
            )
            print(f"Registered on-chain! Tx: {tx_hash} | Block: {block_number}")

            # Register in Database
            report = Report(
                report_id=item["report_id"],
                patient_id=patient.id,
                lab_id=lab_user.id,
                test_type=item["test_type"],
                report_date=datetime.date.today(),
                file_path=dest_filename,
                file_hash=file_hash,
                version=1,
                status="ACTIVE",
                blockchain_tx_hash=tx_hash,
                block_number=block_number
            )
            db.session.add(report)
            db.session.flush() # Populate report.id for Version and Audit log

            # Register Version
            rv = ReportVersion(
                report_id=report.id,
                version=1,
                file_hash=file_hash,
                file_path=report.file_path,
                status="ACTIVE",
                blockchain_tx_hash=tx_hash,
                block_number=block_number
            )
            db.session.add(rv)

            # Log Audit
            audit = AuditLog(
                user_id=lab_user.id,
                report_id=report.id,
                action="REPORT_CREATED",
                details=f"Programmatic registration. Hash: {file_hash}, Block: {block_number}, Tx: {tx_hash}"
            )
            db.session.add(audit)
            print(f"Successfully recorded in database and audit log for {item['report_id']}.\n")

        db.session.commit()
        print("All reports successfully registered and saved!")

if __name__ == '__main__':
    register_reports()
