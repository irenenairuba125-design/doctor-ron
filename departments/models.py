from django.db import models
from django.urls import reverse

from core.models import code


class Department(models.Model):
    """3. Department model (Pediatrics, Surgery, Maternity, Laboratory, Emergency...)."""

    name = models.CharField("Department name", max_length=100, unique=True)
    description = models.TextField(blank=True)
    location = models.CharField("Department location", max_length=150, blank=True)
    head_of_department = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
    )

    class Meta:
        db_table = "departments"
        ordering = ["name"]

    @property
    def department_id(self):
        return code("DEP", self.pk)

    def get_absolute_url(self):
        return reverse("departments:detail", args=[self.pk])

    def __str__(self):
        return self.name
