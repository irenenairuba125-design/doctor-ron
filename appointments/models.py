from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from core.models import code


class Appointment(models.Model):
    """4. Appointment model."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No show"

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE,
                                related_name="appointments")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT,
                               related_name="appointments")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField("Reason for appointment")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-appointment_date", "-appointment_time"]

    @property
    def appointment_id(self):
        return code("APT", self.pk)

    def clean(self):
        # A doctor cannot have two active appointments at the same date and time.
        if self.doctor_id and self.appointment_date and self.appointment_time:
            clash = Appointment.objects.filter(
                doctor_id=self.doctor_id,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time,
            ).exclude(pk=self.pk).exclude(status__in=[self.Status.CANCELLED, self.Status.NO_SHOW])
            if clash.exists():
                raise ValidationError("This doctor already has an appointment at that date and time.")

    def get_absolute_url(self):
        return reverse("appointments:detail", args=[self.pk])

    def __str__(self):
        return f"{self.appointment_id} - {self.patient.full_name} with {self.doctor} on {self.appointment_date}"
