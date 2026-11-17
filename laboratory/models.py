from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import code


class LabTest(models.Model):
    """8. Laboratory model - tests and results."""

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE,
                                related_name="lab_tests")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT,
                               related_name="lab_tests", help_text="Requesting doctor")
    test_name = models.CharField(max_length=150)
    test_date = models.DateField(default=timezone.localdate)
    test_result = models.TextField(blank=True)
    status = models.CharField("Test status", max_length=15, choices=Status.choices,
                              default=Status.REQUESTED)
    fee = models.DecimalField("Test fee", max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "laboratory_tests"
        ordering = ["-test_date", "-id"]
        verbose_name = "laboratory test"

    @property
    def test_id(self):
        return code("LAB", self.pk)

    def get_absolute_url(self):
        return reverse("laboratory:detail", args=[self.pk])

    def __str__(self):
        return f"{self.test_id} - {self.test_name} for {self.patient.full_name}"
