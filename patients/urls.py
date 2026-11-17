from core.crud import Module, Related
from core.permissions import ACCOUNTANT, DOCTOR, LAB, NURSE, PHARMACIST, RECEPTIONIST

from .models import Patient

app_name = "patients"

module = Module(
    Patient,
    namespace=app_name,
    icon="people-fill",
    order=10,
    fields=["first_name", "last_name", "gender", "date_of_birth", "phone_number",
            "address", "next_of_kin", "next_of_kin_phone"],
    list_display=["patient_id", "first_name", "last_name", "gender", "age",
                  "phone_number", "registration_date"],
    detail_fields=["patient_id", "first_name", "last_name", "gender", "date_of_birth", "age",
                   "phone_number", "address", "next_of_kin", "next_of_kin_phone",
                   "registration_date"],
    search_fields=["first_name", "last_name", "phone_number", "next_of_kin"],
    list_filter="gender",
    roles=[RECEPTIONIST],
    view_roles=[DOCTOR, NURSE, LAB, PHARMACIST, ACCOUNTANT],
    related=[
        Related("Appointments", "appointments",
                ["appointment_id", "doctor", "appointment_date", "appointment_time", "status"],
                "appointments:create", "patient", [RECEPTIONIST, DOCTOR]),
        Related("Consultations", "consultations",
                ["consultation_id", "doctor", "diagnosis", "consultation_date"],
                "consultations:create", "patient", [DOCTOR]),
        Related("Admissions", "admissions",
                ["admission_id", "ward", "bed_number", "admission_date", "status"],
                "admissions:create", "patient", [NURSE, DOCTOR]),
        Related("Laboratory tests", "lab_tests",
                ["test_id", "test_name", "test_date", "status"],
                "laboratory:create", "patient", [DOCTOR, LAB]),
        Related("Prescriptions", "prescriptions",
                ["prescription_id", "medicine", "dosage", "frequency", "duration", "dispensed"],
                "pharmacy:prescription_create", "patient", [DOCTOR]),
        Related("Bills", "bills",
                ["bill_id", "bill_date", "total_amount", "payment_status"],
                "billing:create", "patient", [ACCOUNTANT]),
        Related("Payments", "payments",
                ["transaction_reference", "amount_paid", "payment_method", "payment_date"]),
    ],
)

urlpatterns = module.urls
