from django.contrib import admin

from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ["bill_id", "patient", "bill_date", "total_amount", "payment_status"]
    list_filter = ["payment_status", "bill_date"]
    readonly_fields = ["total_amount", "payment_status"]
    search_fields = ["patient__first_name", "patient__last_name"]
