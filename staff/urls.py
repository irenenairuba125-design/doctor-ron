from core.crud import Module
from core.permissions import ACCOUNTANT

from .models import Staff

app_name = "staff"

module = Module(
    Staff,
    namespace=app_name,
    title="Staff",
    icon="person-vcard-fill",
    order=100,
    fields=["first_name", "last_name", "gender", "position", "phone_number", "email",
            "department", "salary", "user"],
    list_display=["staff_id", "full_name", "gender", "position", "department", "phone_number"],
    detail_fields=["staff_id", "first_name", "last_name", "gender", "position", "phone_number",
                   "email", "department", "salary", "user", "date_joined"],
    search_fields=["first_name", "last_name", "position", "email"],
    list_filter="gender",
    roles=[],
    view_roles=[ACCOUNTANT],
)

urlpatterns = module.urls
