import unittest
import os
import shutil
from datetime import datetime
from unittest.mock import patch

from app import create_app
from database.database import db
from database.models import User, Patient, Report
from services.hashing import calculate_sha256
from services.qr_service import generate_report_qr_base64
from services.verification import verify_report_integrity

class LabChainCoreTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize in-memory database
        db.create_all()
        
        # Create temp testing file in binary mode to prevent CRLF line ending differences on Windows
        self.test_file_path = "test_doc.pdf"
        with open(self.test_file_path, "wb") as f:
            f.write(b"LABCHAIN Test Document Integrity Check")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Cleanup temp file
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_hashing_calculation(self):
        """Verifies that calculate_sha256 computes consistent fingerprints."""
        calculated_hash = calculate_sha256(self.test_file_path)
        # Expected SHA-256 for string: "LABCHAIN Test Document Integrity Check"
        expected_hash = "342f0c975745b7550c1d166e83892bf73f59048148bb679625a771ea65f80a5b"
        self.assertEqual(calculated_hash, expected_hash)

    def test_qr_generation(self):
        """Ensures QR generation returns a valid, non-empty base64 string."""
        qr_base64 = generate_report_qr_base64("LAB-2026-1001", "http://localhost:5000")
        self.assertIsNotNone(qr_base64)
        self.assertTrue(len(qr_base64) > 100)

    def test_database_models(self):
        """Checks database model creation and querying."""
        # Add user
        user = User(name="Test Lab", email="test@lab.com", role="LAB")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        
        queried_user = User.query.filter_by(email="test@lab.com").first()
        self.assertIsNotNone(queried_user)
        self.assertEqual(queried_user.name, "Test Lab")
        self.assertTrue(queried_user.check_password("pass123"))

    @patch('blockchain.blockchain_service.BlockchainService.is_connected')
    def test_verification_flow_offline(self, mock_is_connected):
        """Verifies report integrity checks when blockchain is offline."""
        mock_is_connected.return_value = False
        
        # Register patient
        patient = Patient(patient_id="PAT-9999", name="John Tester", age=45, gender="Male")
        db.session.add(patient)
        
        # Register user
        user = User(name="Apex Lab", email="lab@apex.com", role="LAB")
        user.set_password("p")
        db.session.add(user)
        db.session.commit()

        # Register report
        report = Report(
            report_id="LAB-9999-9999",
            patient_id=patient.id,
            lab_id=user.id,
            test_type="Blood Test",
            report_date=datetime.now().date(),
            file_path="dummy_path.pdf",
            file_hash="342f0c975745b7550c1d166e83892bf73f59048148bb679625a771ea65f80a5b",
            version=1,
            status='ACTIVE'
        )
        db.session.add(report)
        db.session.commit()

        # Verify integrity with offline blockchain (it should return blockchain_available = False)
        result = verify_report_integrity("LAB-9999-9999", self.test_file_path)
        self.assertFalse(result["blockchain_available"])
        self.assertEqual(result["reason"], "BLOCKCHAIN_UNAVAILABLE")

if __name__ == '__main__':
    unittest.main()

