from django.urls import path

from core.crud import Action, Module, Related
from core.permissions import ACCOUNTANT, RECEPTIONIST
from core.views import object_action

from .models import Bill

app_name = "billing"

module = Module(
    Bill,
    namespace=app_name,
    icon="receipt",
    order=90,
    fields=["patient", "bill_date", "consultation_fees", "laboratory_fees",
            "medicine_charges", "admission_charges", "notes"],
    list_display=["bill_id", "patient", "bill_date", "total_amount", "amount_paid",
                  "balance", "payment_status"],
    detail_fields=["bill_id", "patient", "bill_date", "consultation_fees", "laboratory_fees",
                   "medicine_charges", "admission_charges", "total_amount", "amount_paid",
                   "balance", "payment_status", "notes"],
    search_fields=["patient__first_name", "patient__last_name"],
    list_filter="payment_status",
    roles=[ACCOUNTANT],
    view_roles=[RECEPTIONIST],
    initial_from_query=["patient"],
    related=[
        Related("Payments", "payments",
                ["payment_id", "transaction_reference", "amount_paid", "payment_method",
                 "payment_date"]),
    ],
    actions=[
        Action("Calculate charges from records", "billing:populate", icon="calculator",
               roles=[ACCOUNTANT], style="info",
               confirm="Replace the charges with totals from the patient's records?",
               condition=lambda b: b.payment_status == "unpaid"),
        Action("Record payment", "payments:create", icon="cash-coin", roles=[ACCOUNTANT],
               method="get", style="success",
               query=lambda b: f"patient={b.patient_id}&bill={b.pk}",
               condition=lambda b: b.balance > 0),
    ],
)

urlpatterns = module.urls + [
    path("<int:pk>/populate/",
         object_action(Bill, [ACCOUNTANT], lambda b: b.populate_from_records(),
                       "Charges calculated from patient records."),
         name="populate"),
]
