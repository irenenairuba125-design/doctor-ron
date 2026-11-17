from core.crud import Module, Related
from core.permissions import ALL_ROLES

from .models import Doctor

app_name = "doctors"

module = Module(
    Doctor,
    namespace=app_name,
    icon="person-badge-fill",
    order=20,
    fields=["first_name", "last_name", "specialization", "phone_number", "email",
            "department", "availability", "consultation_fee", "user"],
    list_display=["doctor_id", "full_name", "specialization", "department",
                  "phone_number", "availability"],
    search_fields=["first_name", "last_name", "specialization", "email"],
    list_filter="availability",
    roles=[],  # administrators only
    view_roles=ALL_ROLES,
    related=[
        Related("Upcoming appointments", "appointments",
                ["appointment_id", "patient", "appointment_date", "appointment_time", "status"]),
        Related("Consultations", "consultations",
                ["consultation_id", "patient", "diagnosis", "consultation_date"]),
    ],
)

urlpatterns = module.urls
