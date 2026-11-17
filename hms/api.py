"""Django REST Framework API for every HMS model.  Browse it at /api/."""
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, routers, serializers, viewsets

from accounts.models import User
from admissions.models import Admission, Ward
from appointments.models import Appointment
from billing.models import Bill
from consultations.models import Consultation
from core.permissions import (ACCOUNTANT, ALL_ROLES, DOCTOR, LAB, NURSE, PHARMACIST,
                              RECEPTIONIST, has_role)
from departments.models import Department
from doctors.models import Doctor
from laboratory.models import LabTest
from patients.models import Patient
from payments.models import Payment
from pharmacy.models import Medicine, Prescription
from staff.models import Staff


class ModelCleanSerializer(serializers.ModelSerializer):
    """Runs the model's clean() so the API enforces the same business rules as the UI."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance or self.Meta.model()
        for key, value in attrs.items():
            setattr(instance, key, value)
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "error_dict") else exc.messages)
        return attrs


class RolePermission(permissions.BasePermission):
    """Read access for view_roles, write access for edit_roles (admins always allowed)."""

    def has_permission(self, request, view):
        roles = view.edit_roles if request.method not in permissions.SAFE_METHODS \
            else view.edit_roles + view.view_roles
        return has_role(request.user, roles)


def make_viewset(model, edit_roles, view_roles=(), search=(), extra_fields=()):
    fields = ["id", *extra_fields] + [
        f.name for f in model._meta.concrete_fields if f.name != "id"]
    attrs = {"Meta": type("Meta", (), {"model": model, "fields": fields})}
    for name in extra_fields:  # read-only computed properties, e.g. patient_id
        attrs[name] = serializers.ReadOnlyField()
    serializer = type(f"{model.__name__}Serializer", (ModelCleanSerializer,), attrs)
    return type(f"{model.__name__}ViewSet", (viewsets.ModelViewSet,), {
        "queryset": model.objects.all(),
        "serializer_class": serializer,
        "permission_classes": [permissions.IsAuthenticated, RolePermission],
        "edit_roles": list(edit_roles),
        "view_roles": list(view_roles),
        "search_fields": list(search),
    })


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "role",
                  "account_status", "password", "last_login"]
        read_only_fields = ["last_login"]

    def _save(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def create(self, validated_data):
        return self._save(User(), validated_data)

    def update(self, instance, validated_data):
        return self._save(instance, validated_data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    edit_roles, view_roles = [], []
    search_fields = ["username", "email", "first_name", "last_name"]


NAME = ("first_name", "last_name")
PATIENT_NAME = ("patient__first_name", "patient__last_name")

router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("patients", make_viewset(
    Patient, [RECEPTIONIST], [DOCTOR, NURSE, LAB, PHARMACIST, ACCOUNTANT],
    NAME + ("phone_number",), ["patient_id", "age"]))
router.register("doctors", make_viewset(
    Doctor, [], ALL_ROLES, NAME + ("specialization",), ["doctor_id"]))
router.register("departments", make_viewset(
    Department, [], ALL_ROLES, ("name",), ["department_id"]))
router.register("appointments", make_viewset(
    Appointment, [RECEPTIONIST, DOCTOR], [NURSE], PATIENT_NAME, ["appointment_id"]))
router.register("consultations", make_viewset(
    Consultation, [DOCTOR], [NURSE], PATIENT_NAME + ("diagnosis",), ["consultation_id"]))
router.register("wards", make_viewset(
    Ward, [], [NURSE, DOCTOR, RECEPTIONIST], ("name",), ["ward_id"]))
router.register("admissions", make_viewset(
    Admission, [NURSE, DOCTOR], [RECEPTIONIST, ACCOUNTANT], PATIENT_NAME, ["admission_id"]))
router.register("laboratory", make_viewset(
    LabTest, [LAB, DOCTOR], [NURSE, ACCOUNTANT], PATIENT_NAME + ("test_name",), ["test_id"]))
router.register("medicines", make_viewset(
    Medicine, [PHARMACIST], [DOCTOR, NURSE], ("name",), ["medicine_id"]))
router.register("prescriptions", make_viewset(
    Prescription, [DOCTOR], [PHARMACIST, NURSE, ACCOUNTANT], PATIENT_NAME, ["prescription_id"]))
router.register("bills", make_viewset(
    Bill, [ACCOUNTANT], [RECEPTIONIST], PATIENT_NAME, ["bill_id", "amount_paid", "balance"]))
router.register("payments", make_viewset(
    Payment, [ACCOUNTANT], [RECEPTIONIST], ("transaction_reference",), ["payment_id"]))
router.register("staff", make_viewset(
    Staff, [], [ACCOUNTANT], NAME + ("position",), ["staff_id"]))
