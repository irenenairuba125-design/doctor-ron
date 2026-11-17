from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import Gender, PersonMixin, code


class Staff(PersonMixin):
    """13. Staff model - hospital employees."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="staff_profile",
    )
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(
        "departments.Department", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="staff",
    )
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "staff"
        ordering = ["first_name", "last_name"]
        verbose_name_plural = "staff"

    @property
    def staff_id(self):
        return code("STF", self.pk)

    def get_absolute_url(self):
        return reverse("staff:detail", args=[self.pk])

    def __str__(self):
        return f"{self.staff_id} - {self.full_name} ({self.position})"
