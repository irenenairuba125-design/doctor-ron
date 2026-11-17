from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """14. User model - people who log into the system.

    Inherits username, securely hashed password, email, first/last name
    from Django's AbstractUser.
    """

    class Role(models.TextChoices):
        ADMINISTRATOR = "administrator", "Administrator"
        DOCTOR = "doctor", "Doctor"
        NURSE = "nurse", "Nurse"
        RECEPTIONIST = "receptionist", "Receptionist"
        LAB_TECHNICIAN = "lab_technician", "Laboratory technician"
        PHARMACIST = "pharmacist", "Pharmacist"
        ACCOUNTANT = "accountant", "Accountant"

    class AccountStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECEPTIONIST)
    account_status = models.CharField(
        max_length=10, choices=AccountStatus.choices, default=AccountStatus.ACTIVE
    )

    class Meta:
        db_table = "users"
        ordering = ["username"]

    def save(self, *args, **kwargs):
        # Keep Django's is_active flag in sync with the account status
        self.is_active = self.account_status == self.AccountStatus.ACTIVE
        if self.is_superuser:
            self.role = self.Role.ADMINISTRATOR
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("accounts:user_detail", args=[self.pk])

    @property
    def is_administrator(self):
        return self.is_superuser or self.role == self.Role.ADMINISTRATOR

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
