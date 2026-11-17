from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class HMSUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "role", "account_status"]
    list_filter = ["role", "account_status"]
    fieldsets = UserAdmin.fieldsets + (("Hospital", {"fields": ("role", "account_status")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Hospital", {"fields": ("email", "role", "account_status")}),)
