from django.urls import path

from core.crud import Action, Module, Related
from core.permissions import ACCOUNTANT, DOCTOR, NURSE, RECEPTIONIST
from core.views import object_action

from .models import Admission, Ward

app_name = "admissions"


def discharge(admission):
    admission.status = Admission.Status.DISCHARGED
    admission.discharge_date = None  # save() sets today's date
    admission.save()


admission_module = Module(
    Admission,
    namespace=app_name,
    icon="hospital-fill",
    order=60,
    fields=["patient", "ward", "bed_number", "admission_date", "discharge_date", "status", "reason"],
    list_display=["admission_id", "patient", "ward", "bed_number", "admission_date",
                  "discharge_date", "status"],
    detail_fields=["admission_id", "patient", "ward", "bed_number", "admission_date",
                   "discharge_date", "days_admitted", "charges", "status", "reason"],
    search_fields=["patient__first_name", "patient__last_name", "ward__name"],
    list_filter="status",
    roles=[NURSE, DOCTOR],
    view_roles=[RECEPTIONIST, ACCOUNTANT],
    initial_from_query=["patient"],
    actions=[
        Action("Discharge patient", "admissions:discharge", icon="box-arrow-right",
               roles=[NURSE, DOCTOR], style="success", confirm="Discharge this patient today?",
               condition=lambda a: a.status == "admitted"),
    ],
)

ward_module = Module(
    Ward,
    namespace=app_name,
    prefix="ward_",
    icon="door-open-fill",
    order=65,
    fields=["name", "ward_type", "number_of_beds", "daily_charge"],
    list_display=["ward_id", "name", "ward_type", "number_of_beds", "available_beds", "daily_charge"],
    search_fields=["name"],
    list_filter="ward_type",
    roles=[],
    view_roles=[NURSE, DOCTOR, RECEPTIONIST],
    related=[
        Related("Current & past admissions", "admissions",
                ["admission_id", "patient", "bed_number", "admission_date", "status"]),
    ],
)

urlpatterns = admission_module.urls + ward_module.urls + [
    path("<int:pk>/discharge/",
         object_action(Admission, [NURSE, DOCTOR], discharge, "Patient discharged."),
         name="discharge"),
]
