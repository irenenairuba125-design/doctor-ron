from django.contrib import admin

from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["doctor_id", "first_name", "last_name", "specialization", "department",
                    "availability"]
    list_filter = ["availability", "department"]
    search_fields = ["first_name", "last_name", "specialization", "email"]
