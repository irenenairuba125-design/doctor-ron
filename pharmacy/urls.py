from django.urls import path

from core.crud import Action, Module, Related
from core.permissions import ACCOUNTANT, DOCTOR, NURSE, PHARMACIST
from core.views import object_action

from .models import Medicine, Prescription

app_name = "pharmacy"

medicine_module = Module(
    Medicine,
    namespace=app_name,
    prefix="medicine_",
    title="Pharmacy",
    icon="capsule-pill",
    order=80,
    fields=["name", "category", "quantity", "unit_price", "expiry_date"],
    list_display=["medicine_id", "name", "category", "quantity", "unit_price",
                  "expiry_date", "is_low_stock", "is_expired"],
    search_fields=["name"],
    list_filter="category",
    roles=[PHARMACIST],
    view_roles=[DOCTOR, NURSE],
    related=[
        Related("Prescriptions", "prescriptions",
                ["prescription_id", "patient", "quantity", "prescription_date", "dispensed"]),
    ],
)

prescription_module = Module(
    Prescription,
    namespace=app_name,
    prefix="prescription_",
    icon="prescription2",
    order=85,
    fields=["patient", "doctor", "consultation", "medicine", "dosage", "frequency",
            "duration", "quantity", "prescription_date"],
    list_display=["prescription_id", "patient", "doctor", "medicine", "dosage",
                  "frequency", "duration", "dispensed"],
    detail_fields=["prescription_id", "patient", "doctor", "consultation", "medicine", "dosage",
                   "frequency", "duration", "quantity", "cost", "prescription_date", "dispensed"],
    search_fields=["patient__first_name", "patient__last_name", "medicine__name"],
    list_filter="dispensed",
    roles=[DOCTOR],
    view_roles=[PHARMACIST, NURSE, ACCOUNTANT],
    initial_from_query=["patient", "doctor", "consultation"],
    actions=[
        Action("Dispense", "pharmacy:prescription_dispense", icon="bag-check",
               roles=[PHARMACIST], style="success",
               confirm="Dispense this prescription and reduce stock?",
               condition=lambda p: not p.dispensed),
    ],
)

urlpatterns = medicine_module.urls + prescription_module.urls + [
    path("prescriptions/<int:pk>/dispense/",
         object_action(Prescription, [PHARMACIST], lambda p: p.dispense(),
                       "Prescription dispensed and stock updated."),
         name="prescription_dispense"),
]
