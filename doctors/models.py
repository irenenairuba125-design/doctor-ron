from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import PersonMixin, code


class Doctor(PersonMixin):
    """2. Doctor model."""

    class Availability(models.TextChoices):
        AVAILABLE = "available", "Available"
        ON_DUTY = "on_duty", "On duty"
        ON_LEAVE = "on_leave", "On leave"
        UNAVAILABLE = "unavailable", "Unavailable"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
        help_text="Optional login account linked to this doctor",
    )
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    specialization = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(
        "departments.Department", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="doctors",
    )
    availability = models.CharField(
        max_length=15, choices=Availability.choices, default=Availability.AVAILABLE
    )
    consultation_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "doctors"
        ordering = ["first_name", "last_name"]

    @property
    def doctor_id(self):
        return code("DOC", self.pk)

    def get_absolute_url(self):
        return reverse("doctors:detail", args=[self.pk])

    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialization})"
