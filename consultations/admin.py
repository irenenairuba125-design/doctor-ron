from django.contrib import admin

from .models import Consultation


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ["consultation_id", "patient", "doctor", "diagnosis", "consultation_date"]
    list_filter = ["consultation_date", "doctor"]
    search_fields = ["patient__first_name", "patient__last_name", "diagnosis"]
