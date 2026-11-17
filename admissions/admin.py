from django.contrib import admin

from .models import Admission, Ward


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ["ward_id", "name", "ward_type", "number_of_beds", "available_beds",
                    "daily_charge"]
    list_filter = ["ward_type"]


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ["admission_id", "patient", "ward", "bed_number", "admission_date",
                    "discharge_date", "status"]
    list_filter = ["status", "ward"]
    search_fields = ["patient__first_name", "patient__last_name"]
