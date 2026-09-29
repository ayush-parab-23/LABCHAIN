import os
from app import create_app
from database.database import db
from database.models import User, Patient, Report, ReportVersion, AuditLog

def seed_database():
    app = create_app()
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()

        # Clear existing data to make seeder idempotent
        print("Clearing existing data...")
        AuditLog.query.delete()
        ReportVersion.query.delete()
        Report.query.delete()
        Patient.query.delete()
        User.query.delete()
        db.session.commit()

        print("Seeding default roles...")
        
        # 1. Issuing Laboratory User
        lab_user = User(
            name="Apex Clinical Laboratory",
            email="lab@example.com",
            role="LAB"
        )
        lab_user.set_password("password123")
        db.session.add(lab_user)

        # 2. Patient User (Ayush - PAT-2001)
        patient_user = User(
            name="Ayush",
            email="patient@example.com",
            role="PATIENT"
        )
        patient_user.set_password("password123")
        db.session.add(patient_user)

        # 3. Verifying Hospital User
        hospital_user = User(
            name="City General Hospital",
            email="hospital@example.com",
            role="HOSPITAL"
        )
        hospital_user.set_password("password123")
        db.session.add(hospital_user)

        db.session.commit()

        patients = [
            Patient(patient_id="PAT-2001", name="Ayush", age=24, gender="Male"),
            Patient(patient_id="PAT-2002", name="Arya", age=22, gender="Male"),
            Patient(patient_id="PAT-2003", name="Piyush", age=25, gender="Male"),
            Patient(patient_id="PAT-2004", name="Rohan", age=23, gender="Male"),
            Patient(patient_id="PAT-2005", name="Archie", age=21, gender="Female"),
            Patient(patient_id="PAT-2006", name="Manaswi", age=22, gender="Female"),
            Patient(patient_id="PAT-2007", name="Riya", age=23, gender="Female"),
        ]
        db.session.add_all(patients)
        db.session.commit()


        print("\nDatabase seeded successfully!")
        print("----------------------------")
        print("Role accounts created:")
        print("1. LAB      - lab@example.com      / password123")
        print("2. PATIENT  - patient@example.com  / password123")
        print("3. HOSPITAL - hospital@example.com / password123")
        print("----------------------------")

if __name__ == '__main__':
    seed_database()
