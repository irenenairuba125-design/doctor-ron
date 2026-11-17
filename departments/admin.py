from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["department_id", "name", "location", "head_of_department"]
    search_fields = ["name"]
