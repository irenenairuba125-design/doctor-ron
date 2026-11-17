from core.crud import Module
from core.permissions import ACCOUNTANT, RECEPTIONIST

from .models import Payment

app_name = "payments"

module = Module(
    Payment,
    namespace=app_name,
    icon="cash-coin",
    order=95,
    fields=["patient", "bill", "amount_paid", "payment_method", "payment_date",
            "transaction_reference"],
    list_display=["payment_id", "transaction_reference", "patient", "bill", "amount_paid",
                  "payment_method", "payment_date"],
    search_fields=["transaction_reference", "patient__first_name", "patient__last_name"],
    list_filter="payment_method",
    roles=[ACCOUNTANT],
    view_roles=[RECEPTIONIST],
    initial_from_query=["patient", "bill"],
)

urlpatterns = module.urls
