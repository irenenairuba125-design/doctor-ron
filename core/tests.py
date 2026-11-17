from datetime import timedelta
from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from admissions.models import Admission, Ward
from billing.models import Bill
from core.crud import REGISTRY
from payments.models import Payment
from pharmacy.models import Medicine, Prescription


class SmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def test_every_page_renders_for_admin(self):
        self.client.login(username="admin", password="Hospital@123")
        self.assertEqual(self.client.get("/").status_code, 200)
        for module in REGISTRY:
            for name in ("list", "create"):
                url = reverse(module.url_name(name))
                self.assertEqual(self.client.get(url).status_code, 200, url)
            self.assertEqual(self.client.get(reverse(module.url_name("list")), {"q": "a"}).status_code, 200)
            obj = module.model.objects.first()
            for name in ("detail", "update", "delete"):
                url = reverse(module.url_name(name), args=[obj.pk])
                self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_role_access(self):
        self.client.login(username="pharmacist", password="Hospital@123")
        self.assertEqual(self.client.get(reverse("pharmacy:medicine_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("billing:list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("pharmacy:prescription_create")).status_code, 403)
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_every_role_dashboard_and_nav(self):
        for role, _ in User.Role.choices:
            username = "admin" if role == "administrator" else role
            self.client.login(username=username, password="Hospital@123")
            self.assertEqual(self.client.get("/").status_code, 200, role)

    def test_login_required(self):
        self.assertRedirects(self.client.get("/patients/"), "/accounts/login/?next=/patients/")

    def test_dispense_reduces_stock(self):
        rx = Prescription.objects.filter(dispensed=False).first()
        stock = rx.medicine.quantity
        self.client.login(username="pharmacist", password="Hospital@123")
        self.client.post(reverse("pharmacy:prescription_dispense", args=[rx.pk]))
        rx.refresh_from_db()
        self.assertTrue(rx.dispensed)
        self.assertEqual(Medicine.objects.get(pk=rx.medicine_id).quantity, stock - rx.quantity)

    def test_ward_beds_and_discharge(self):
        ward = Ward.objects.get(name="ICU")
        before = ward.available_beds
        adm = Admission.objects.filter(ward=ward, status="admitted").first()
        self.client.login(username="nurse", password="Hospital@123")
        self.client.post(reverse("admissions:discharge", args=[adm.pk]))
        ward.refresh_from_db()
        self.assertEqual(ward.available_beds, before + 1)

    def test_double_booked_bed_rejected(self):
        adm = Admission.objects.filter(status="admitted").first()
        from patients.models import Patient
        free_patient = Patient.objects.exclude(admissions__status="admitted").first()
        self.client.login(username="nurse", password="Hospital@123")
        resp = self.client.post(reverse("admissions:create"), {
            "patient": free_patient.pk, "ward": adm.ward_id, "bed_number": adm.bed_number,
            "admission_date": timezone.localdate(), "status": "admitted"})
        self.assertContains(resp, "already occupied")

    def test_payments_update_bill_status(self):
        bill = Bill.objects.create(patient_id=Bill.objects.first().patient_id,
                                   consultation_fees=Decimal("1000"))
        self.assertEqual(bill.payment_status, "unpaid")
        Payment.objects.create(patient=bill.patient, bill=bill, amount_paid=Decimal("400"))
        bill.refresh_from_db()
        self.assertEqual(bill.payment_status, "partial")
        Payment.objects.create(patient=bill.patient, bill=bill, amount_paid=Decimal("600"))
        bill.refresh_from_db()
        self.assertEqual(bill.payment_status, "paid")

    def test_overpayment_rejected(self):
        bill = Bill.objects.create(patient_id=Bill.objects.first().patient_id,
                                   consultation_fees=Decimal("1000"))
        self.client.login(username="accountant", password="Hospital@123")
        resp = self.client.post(reverse("payments:create"), {
            "patient": bill.patient_id, "bill": bill.pk, "amount_paid": "5000",
            "payment_method": "cash", "payment_date": timezone.now().strftime("%Y-%m-%dT%H:%M")})
        self.assertContains(resp, "exceeds the outstanding balance")

    def test_api(self):
        self.client.login(username="admin", password="Hospital@123")
        root = self.client.get("/api/").json()
        for name, url in root.items():
            self.assertEqual(self.client.get(url).status_code, 200, name)
        resp = self.client.post("/api/patients/", {
            "first_name": "Api", "last_name": "Test", "gender": "F",
            "date_of_birth": "1990-01-01", "phone_number": "0700", "address": "X",
            "next_of_kin": "Y"})
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["patient_id"], f"PAT{resp.json()['id']:05d}")
        # role restrictions apply to the API too
        self.client.login(username="pharmacist", password="Hospital@123")
        self.assertEqual(self.client.get("/api/bills/").status_code, 403)

    def test_api_enforces_model_rules(self):
        self.client.login(username="admin", password="Hospital@123")
        med = Medicine.objects.filter(expiry_date__lt=timezone.localdate()).first()
        rx = Prescription.objects.first()
        resp = self.client.post("/api/prescriptions/", {
            "patient": rx.patient_id, "doctor": rx.doctor_id, "medicine": med.pk,
            "dosage": "1", "frequency": "1", "duration": "1", "quantity": 1,
            "prescription_date": str(timezone.localdate() - timedelta(days=0))})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("expired", str(resp.content))

    def test_user_create_hashes_password(self):
        self.client.login(username="admin", password="Hospital@123")
        self.client.post(reverse("accounts:user_create"), {
            "username": "newnurse", "email": "n@x.com", "role": "nurse",
            "account_status": "active", "password1": "Str0ng!Pass99", "password2": "Str0ng!Pass99"})
        user = User.objects.get(username="newnurse")
        self.assertNotEqual(user.password, "Str0ng!Pass99")  # stored hashed
        self.assertTrue(user.check_password("Str0ng!Pass99"))
