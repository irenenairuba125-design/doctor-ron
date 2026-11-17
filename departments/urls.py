from core.crud import Module, Related
from core.permissions import ALL_ROLES

from .models import Department

app_name = "departments"

module = Module(
    Department,
    namespace=app_name,
    icon="building",
    order=30,
    fields=["name", "description", "location", "head_of_department"],
    list_display=["department_id", "name", "location", "head_of_department"],
    search_fields=["name", "location"],
    roles=[],
    view_roles=ALL_ROLES,
    related=[
        Related("Doctors", "doctors", ["doctor_id", "full_name", "specialization", "availability"]),
        Related("Staff", "staff", ["staff_id", "full_name", "position", "phone_number"]),
    ],
)

urlpatterns = module.urls
