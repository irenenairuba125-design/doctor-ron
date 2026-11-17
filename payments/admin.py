from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["payment_id", "transaction_reference", "patient", "bill", "amount_paid",
                    "payment_method", "payment_date"]
    list_filter = ["payment_method"]
    search_fields = ["transaction_reference"]
