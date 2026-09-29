import os
from database.models import Report, ReportVersion, Patient, User
from blockchain.blockchain_service import BlockchainService, BlockchainConnectionError
from services.hashing import calculate_sha256

def verify_report_integrity(report_id, file_path_to_verify=None):
    """
    Verifies a report's integrity by comparing database, file, and blockchain records.
    Returns a dict with verification details.
    """
    blockchain = BlockchainService()
    
    # 1. Fetch from Database
    report = Report.query.filter_by(report_id=report_id).first()
    if not report:
        return {
            "verified": False,
            "reason": "REPORT_NOT_FOUND",
            "message": f"Report ID '{report_id}' was not found in the LABCHAIN registry."
        }

    # Fetch patient and lab details
    patient = Patient.query.get(report.patient_id)
    lab = User.query.get(report.lab_id)

    # 2. Fetch from Blockchain
    blockchain_available = blockchain.is_connected()
    on_chain_record = None
    
    if blockchain_available:
        try:
            on_chain_record = blockchain.get_report(report_id, version=0)
        except Exception as e:
            print(f"Blockchain error during verification: {e}")
            blockchain_available = False
    
    # 3. Calculate hash of file to verify (if provided)
    verification_hash = report.file_hash
    is_hash_match = True
    uploaded_hash = None
    
    if file_path_to_verify:
        uploaded_hash = calculate_sha256(file_path_to_verify)
        verification_hash = uploaded_hash
        is_hash_match = (uploaded_hash == report.file_hash)

    # 4. Check if blockchain hash matches database hash
    blockchain_hash = None
    blockchain_status = None
    blockchain_version = None
    blockchain_timestamp = None
    
    if on_chain_record and on_chain_record.get("exists"):
        blockchain_hash = on_chain_record["reportHash"]
        blockchain_status = on_chain_record["status"] # 0=ACTIVE, 1=SUPERSEDED, 2=REVOKED
        blockchain_version = on_chain_record["version"]
        blockchain_timestamp = on_chain_record["timestamp"]

    # Integrity evaluations
    db_bc_match = True
    if blockchain_available and blockchain_hash:
        db_bc_match = (report.file_hash == blockchain_hash)

    # Compile result
    verified = is_hash_match and db_bc_match and (report.status == 'ACTIVE')
    
    reason = "SUCCESS"
    if not is_hash_match:
        reason = "HASH_MISMATCH"
    elif not db_bc_match:
        reason = "BLOCKCHAIN_MISMATCH"
    elif report.status == 'SUPERSEDED':
        reason = "SUPERSEDED"
    elif report.status == 'REVOKED':
        reason = "REVOKED"
    elif not blockchain_available:
        reason = "BLOCKCHAIN_UNAVAILABLE"

    return {
        "verified": verified,
        "reason": reason,
        "blockchain_available": blockchain_available,
        "report_id": report_id,
        "test_type": report.test_type,
        "report_date": report.report_date.strftime("%Y-%m-%d"),
        "patient_name": patient.name if patient else "Unknown",
        "patient_id": patient.patient_id if patient else "Unknown",
        "lab_name": lab.name if lab else "Unknown",
        "db_hash": report.file_hash,
        "uploaded_hash": uploaded_hash,
        "blockchain_hash": blockchain_hash,
        "version": report.version,
        "status": report.status,
        "blockchain_tx_hash": report.blockchain_tx_hash,
        "block_number": report.block_number,
        "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }

def verify_report_by_file_only(file_path):
    """
    Attempts to verify a report using ONLY the uploaded file's hash.
    First, it looks up the hash in active reports, then in old versions.
    """
    file_hash = calculate_sha256(file_path)
    
    # Check active reports first
    report = Report.query.filter_by(file_hash=file_hash).first()
    if report:
        return verify_report_integrity(report.report_id, file_path)
    
    # Check old report versions
    old_version = ReportVersion.query.filter_by(file_hash=file_hash).first()
    if old_version:
        report = Report.query.get(old_version.report_id)
        if report:
            # Let's verify integrity of this specific report version
            result = verify_report_integrity(report.report_id, file_path)
            # Override current status to superseded since this hash belongs to an old version
            result["verified"] = False
            result["status"] = "SUPERSEDED"
            result["reason"] = "SUPERSEDED"
            result["version"] = old_version.version
            result["db_hash"] = old_version.file_hash
            result["blockchain_tx_hash"] = old_version.blockchain_tx_hash
            result["block_number"] = old_version.block_number
            return result

    # Not found at all
    return {
        "verified": False,
        "reason": "HASH_NOT_FOUND",
        "uploaded_hash": file_hash,
        "message": "This file hash does not match any registered report in the LABCHAIN database."
    }
