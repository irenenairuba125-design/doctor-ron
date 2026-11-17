from core.crud import Action, Module
from core.permissions import DOCTOR, NURSE, RECEPTIONIST

from .models import Appointment

app_name = "appointments"

module = Module(
    Appointment,
    namespace=app_name,
    icon="calendar-check-fill",
    order=40,
    fields=["patient", "doctor", "appointment_date", "appointment_time", "reason", "status"],
    list_display=["appointment_id", "patient", "doctor", "appointment_date",
                  "appointment_time", "status"],
    search_fields=["patient__first_name", "patient__last_name",
                   "doctor__first_name", "doctor__last_name", "reason"],
    list_filter="status",
    roles=[RECEPTIONIST, DOCTOR],
    view_roles=[NURSE],
    initial_from_query=["patient", "doctor"],
    actions=[
        Action("Start consultation", "consultations:create", icon="clipboard2-pulse",
               roles=[DOCTOR], method="get", style="success",
               query=lambda a: f"patient={a.patient_id}&doctor={a.doctor_id}&appointment={a.pk}",
               condition=lambda a: a.status in ("scheduled", "confirmed")
               and not hasattr(a, "consultation")),
    ],
)

urlpatterns = module.urls
