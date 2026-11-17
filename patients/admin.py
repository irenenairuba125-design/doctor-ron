from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["patient_id", "first_name", "last_name", "gender", "date_of_birth",
                    "phone_number", "registration_date"]
    list_filter = ["gender"]
    search_fields = ["first_name", "last_name", "phone_number"]
