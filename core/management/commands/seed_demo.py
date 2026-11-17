"""Load sample data:  python manage.py seed_demo

Creates one login per role (password: Hospital@123), departments, doctors, wards,
medicines, patients and a few appointments / consultations / admissions / bills.
"""
import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from admissions.models import Admission, Ward
from appointments.models import Appointment
from billing.models import Bill
from consultations.models import Consultation
from departments.models import Department
from doctors.models import Doctor
from laboratory.models import LabTest
from patients.models import Patient
from payments.models import Payment
from pharmacy.models import Medicine, Prescription
from staff.models import Staff

PASSWORD = "Hospital@123"


class Command(BaseCommand):
    help = "Populate the database with demo hospital data."

    @transaction.atomic
    def handle(self, *args, **options):
        if Patient.objects.exists():
            self.stdout.write(self.style.WARNING("Data already exists - skipping."))
            return
        random.seed(7)
        today = timezone.localdate()

        # ---- users (one per role)
        users = {}
        for role, label in User.Role.choices:
            username = "admin" if role == "administrator" else role
            u = User(username=username, email=f"{username}@hospital.local",
                     first_name=label.split()[0], last_name="Demo", role=role,
                     is_staff=role == "administrator", is_superuser=role == "administrator")
            u.set_password(PASSWORD)
            u.save()
            users[role] = u

        # ---- departments
        depts = {}
        for name, loc, desc in [
            ("Pediatrics", "Block A, Floor 1", "Medical care for infants and children"),
            ("Surgery", "Block B, Floor 2", "General and specialised surgical procedures"),
            ("Maternity", "Block C, Floor 1", "Antenatal, delivery and postnatal care"),
            ("Laboratory", "Block A, Ground", "Diagnostic tests and analysis"),
            ("Emergency", "Main entrance", "24-hour emergency and trauma care"),
            ("Internal Medicine", "Block B, Floor 1", "Diagnosis and treatment of adult diseases"),
        ]:
            depts[name] = Department.objects.create(name=name, location=loc, description=desc)

        # ---- doctors
        doctors = []
        for i, (fn, ln, spec, dept, fee) in enumerate([
            ("Sarah", "Namukasa", "Pediatrician", "Pediatrics", 50000),
            ("James", "Okello", "General Surgeon", "Surgery", 80000),
            ("Grace", "Achieng", "Obstetrician", "Maternity", 70000),
            ("Peter", "Mugisha", "Emergency Physician", "Emergency", 60000),
            ("Ruth", "Nabirye", "Physician", "Internal Medicine", 55000),
        ]):
            d = Doctor.objects.create(
                first_name=fn, last_name=ln, specialization=spec, department=depts[dept],
                phone_number=f"+2567000000{i}", email=f"{fn.lower()}.{ln.lower()}@hospital.local",
                consultation_fee=Decimal(fee), user=users["doctor"] if i == 0 else None)
            depts[dept].head_of_department = d
            depts[dept].save()
            doctors.append(d)

        # ---- staff
        for i, (fn, ln, g, pos, dept, sal) in enumerate([
            ("Mary", "Auma", "F", "Head Nurse", "Maternity", 1800000),
            ("John", "Kato", "M", "Receptionist", "Emergency", 900000),
            ("Esther", "Nakato", "F", "Laboratory Technician", "Laboratory", 1400000),
            ("David", "Ssempala", "M", "Pharmacist", "Internal Medicine", 1600000),
            ("Agnes", "Atim", "F", "Accountant", "Internal Medicine", 1500000),
        ]):
            Staff.objects.create(first_name=fn, last_name=ln, gender=g, position=pos,
                                 department=depts[dept], phone_number=f"+2567110000{i}",
                                 email=f"{fn.lower()}.{ln.lower()}@hospital.local", salary=sal)

        # ---- wards
        wards = [
            Ward.objects.create(name="General Ward A", ward_type="general", number_of_beds=20,
                                daily_charge=30000),
            Ward.objects.create(name="Maternity Ward", ward_type="maternity", number_of_beds=12,
                                daily_charge=40000),
            Ward.objects.create(name="Children's Ward", ward_type="pediatric", number_of_beds=15,
                                daily_charge=25000),
            Ward.objects.create(name="ICU", ward_type="icu", number_of_beds=6,
                                daily_charge=250000),
            Ward.objects.create(name="Private Wing", ward_type="private", number_of_beds=8,
                                daily_charge=150000),
        ]

        # ---- medicines
        medicines = []
        for name, cat, qty, price, months in [
            ("Paracetamol 500mg", "tablet", 1200, 200, 18), ("Amoxicillin 250mg", "capsule", 600, 500, 12),
            ("Artemether/Lumefantrine", "tablet", 15, 3500, 10), ("ORS Sachets", "other", 300, 800, 24),
            ("Ibuprofen 400mg", "tablet", 800, 300, 20), ("Metformin 500mg", "tablet", 450, 400, 16),
            ("Ceftriaxone 1g", "injection", 90, 6000, 9), ("Cough Syrup 100ml", "syrup", 12, 4500, 0),
            ("Salbutamol Inhaler", "inhaler", 40, 15000, 14), ("Tetracycline Eye Ointment", "cream", 70, 2500, 11),
        ]:
            medicines.append(Medicine.objects.create(
                name=name, category=cat, quantity=qty, unit_price=price,
                expiry_date=today + timedelta(days=30 * months - (40 if months == 0 else 0))))

        # ---- patients
        first = ["Brian", "Faith", "Moses", "Joan", "Isaac", "Patience", "Samuel", "Doreen",
                 "Henry", "Lillian", "Daniel", "Prossy"]
        last = ["Wasswa", "Nalubega", "Opio", "Akello", "Tumusiime", "Kyomugisha", "Ochieng",
                "Namatovu", "Byaruhanga", "Nansubuga", "Odongo", "Kabuye"]
        patients = []
        for i, (fn, ln) in enumerate(zip(first, last)):
            patients.append(Patient.objects.create(
                first_name=fn, last_name=ln, gender="M" if i % 2 == 0 else "F",
                date_of_birth=date(1960 + i * 4 % 60, (i % 12) + 1, (i % 27) + 1),
                phone_number=f"+2567720000{i:02d}", address=f"Plot {10 + i}, Kampala Road",
                next_of_kin=f"{random.choice(first)} {ln}", next_of_kin_phone=f"+2567730000{i:02d}"))

        # ---- appointments, consultations, lab tests, prescriptions
        reasons = ["Fever and headache", "Routine check-up", "Abdominal pain", "Persistent cough",
                   "Antenatal visit", "Follow-up review"]
        diagnoses = ["Malaria", "Upper respiratory tract infection", "Gastritis", "Hypertension",
                     "Normal pregnancy", "Type 2 diabetes"]
        for i, p in enumerate(patients):
            doc = doctors[i % len(doctors)]
            Appointment.objects.create(
                patient=p, doctor=doc, appointment_date=today + timedelta(days=i % 3),
                appointment_time=time(8 + i % 9, 30 if i % 2 else 0), reason=reasons[i % len(reasons)])
            if i < 8:
                past = Appointment.objects.create(
                    patient=p, doctor=doc, appointment_date=today - timedelta(days=3 + i),
                    appointment_time=time(9 + i % 8, 0), reason=reasons[(i + 1) % len(reasons)],
                    status="confirmed")
                c = Consultation.objects.create(
                    patient=p, doctor=doc, appointment=past, symptoms=past.reason,
                    diagnosis=diagnoses[i % len(diagnoses)], treatment="Medication prescribed; review in 1 week.",
                    consultation_date=past.appointment_date)
                LabTest.objects.create(
                    patient=p, doctor=doc, test_name=random.choice(
                        ["Malaria RDT", "Complete blood count", "Urinalysis", "Blood sugar"]),
                    test_date=c.consultation_date, fee=random.choice([10000, 15000, 25000]),
                    status="completed" if i % 3 else "requested",
                    test_result="Within normal limits" if i % 3 else "")
                med = medicines[i % 6]
                rx = Prescription.objects.create(
                    patient=p, doctor=doc, consultation=c, medicine=med, dosage="1 tablet",
                    frequency="3 times a day", duration="5 days", quantity=15,
                    prescription_date=c.consultation_date)
                if i % 2:
                    rx.dispense()

        # ---- admissions
        for i, p in enumerate(patients[:5]):
            Admission.objects.create(patient=p, ward=wards[i % len(wards)], bed_number=i + 1,
                                     admission_date=today - timedelta(days=2 + i),
                                     reason="Observation and treatment")

        # ---- bills & payments
        for i, p in enumerate(patients[:6]):
            bill = Bill.objects.create(patient=p, bill_date=today)
            bill.populate_from_records()
            if i % 3 == 0 and bill.total_amount:
                Payment.objects.create(patient=p, bill=bill, amount_paid=bill.total_amount,
                                       payment_method="mobile_money")
            elif i % 3 == 1 and bill.total_amount:
                Payment.objects.create(patient=p, bill=bill,
                                       amount_paid=(bill.total_amount / 2).quantize(Decimal("1")),
                                       payment_method="cash")

        self.stdout.write(self.style.SUCCESS(
            "Demo data created. Log in as any of: "
            + ", ".join(u.username for u in users.values()) + f"  (password: {PASSWORD})"))
