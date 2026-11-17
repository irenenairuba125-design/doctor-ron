from django.contrib import admin

from .models import Medicine, Prescription


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ["medicine_id", "name", "category", "quantity", "unit_price", "expiry_date"]
    list_filter = ["category"]
    search_fields = ["name"]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ["prescription_id", "patient", "doctor", "medicine", "dosage", "frequency",
                    "duration", "dispensed"]
    list_filter = ["dispensed"]
    search_fields = ["patient__first_name", "patient__last_name", "medicine__name"]
