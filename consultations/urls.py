from core.crud import Action, Module, Related
from core.permissions import DOCTOR, NURSE

from .models import Consultation

app_name = "consultations"

module = Module(
    Consultation,
    namespace=app_name,
    icon="clipboard2-pulse",
    order=50,
    fields=["patient", "doctor", "appointment", "symptoms", "diagnosis", "treatment",
            "consultation_date", "fee"],
    list_display=["consultation_id", "patient", "doctor", "diagnosis", "consultation_date"],
    search_fields=["patient__first_name", "patient__last_name", "diagnosis", "symptoms"],
    roles=[DOCTOR],
    view_roles=[NURSE],
    initial_from_query=["patient", "doctor", "appointment"],
    related=[
        Related("Prescriptions", "prescriptions",
                ["prescription_id", "medicine", "dosage", "frequency", "duration", "dispensed"]),
    ],
    actions=[
        Action("Prescribe medicine", "pharmacy:prescription_create", icon="capsule",
               roles=[DOCTOR], method="get",
               query=lambda c: f"patient={c.patient_id}&doctor={c.doctor_id}&consultation={c.pk}"),
        Action("Request lab test", "laboratory:create", icon="eyedropper",
               roles=[DOCTOR], method="get", style="info",
               query=lambda c: f"patient={c.patient_id}&doctor={c.doctor_id}"),
        Action("Admit patient", "admissions:create", icon="hospital", roles=[DOCTOR],
               method="get", style="warning", query=lambda c: f"patient={c.patient_id}"),
    ],
)

urlpatterns = module.urls
