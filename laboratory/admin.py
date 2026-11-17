from django.contrib import admin

from .models import LabTest


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ["test_id", "patient", "doctor", "test_name", "test_date", "status"]
    list_filter = ["status", "test_date"]
    search_fields = ["test_name", "patient__first_name", "patient__last_name"]
