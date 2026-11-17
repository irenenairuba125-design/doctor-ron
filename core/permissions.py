from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

ADMIN = "administrator"
DOCTOR = "doctor"
NURSE = "nurse"
RECEPTIONIST = "receptionist"
LAB = "lab_technician"
PHARMACIST = "pharmacist"
ACCOUNTANT = "accountant"

ALL_ROLES = (ADMIN, DOCTOR, NURSE, RECEPTIONIST, LAB, PHARMACIST, ACCOUNTANT)


def has_role(user, roles):
    """Administrators (and superusers) can access everything."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role == ADMIN:
        return True
    return user.role in roles


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not has_role(request.user, self.allowed_roles):
            raise PermissionDenied("Your role does not have access to this page.")
        return super().dispatch(request, *args, **kwargs)
