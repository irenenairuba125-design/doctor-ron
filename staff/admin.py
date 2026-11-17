from django.contrib import admin

from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["staff_id", "first_name", "last_name", "position", "department", "salary"]
    list_filter = ["department", "gender"]
    search_fields = ["first_name", "last_name", "position"]
