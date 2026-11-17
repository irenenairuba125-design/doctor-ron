from django.contrib import admin
from django.urls import include, path

from .api import router

admin.site.site_header = "Hospital Management System"
admin.site.site_title = "HMS Admin"
admin.site.index_title = "Administration"

urlpatterns = [
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("patients/", include("patients.urls")),
    path("doctors/", include("doctors.urls")),
    path("departments/", include("departments.urls")),
    path("appointments/", include("appointments.urls")),
    path("consultations/", include("consultations.urls")),
    path("admissions/", include("admissions.urls")),
    path("laboratory/", include("laboratory.urls")),
    path("pharmacy/", include("pharmacy.urls")),
    path("billing/", include("billing.urls")),
    path("payments/", include("payments.urls")),
    path("staff/", include("staff.urls")),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
]

handler403 = "core.views.permission_denied"
