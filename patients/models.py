from datetime import date

from django.db import models
from django.urls import reverse

from core.models import Gender, PersonMixin, code


class Patient(PersonMixin):
    """1. Patient model."""

    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    next_of_kin = models.CharField(max_length=120, help_text="Name of next of kin")
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patients"
        ordering = ["-registration_date"]

    @property
    def patient_id(self):
        return code("PAT", self.pk)

    @property
    def age(self):
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def get_absolute_url(self):
        return reverse("patients:detail", args=[self.pk])

    def __str__(self):
        return f"{self.patient_id} - {self.full_name}"
