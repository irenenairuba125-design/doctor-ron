from core.crud import Module
from core.permissions import ACCOUNTANT, DOCTOR, LAB, NURSE

from .models import LabTest

app_name = "laboratory"

module = Module(
    LabTest,
    namespace=app_name,
    title="Laboratory",
    icon="eyedropper",
    order=70,
    fields=["patient", "doctor", "test_name", "test_date", "test_result", "status", "fee"],
    list_display=["test_id", "patient", "doctor", "test_name", "test_date", "status"],
    search_fields=["patient__first_name", "patient__last_name", "test_name"],
    list_filter="status",
    roles=[LAB, DOCTOR],
    view_roles=[NURSE, ACCOUNTANT],
    initial_from_query=["patient", "doctor"],
)

urlpatterns = module.urls
