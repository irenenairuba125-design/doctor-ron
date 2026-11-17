from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import code


class Consultation(models.Model):
    """5. Consultation model - examinations, diagnosis and treatment."""

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE,
                                related_name="consultations")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT,
                               related_name="consultations")
    appointment = models.OneToOneField(
        "appointments.Appointment", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="consultation",
    )
    symptoms = models.TextField()
    diagnosis = models.TextField()
    treatment = models.TextField()
    consultation_date = models.DateField(default=timezone.localdate)
    fee = models.DecimalField("Consultation fee", max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "consultations"
        ordering = ["-consultation_date", "-id"]

    @property
    def consultation_id(self):
        return code("CON", self.pk)

    def save(self, *args, **kwargs):
        if not self.fee and self.doctor_id:
            self.fee = self.doctor.consultation_fee
        super().save(*args, **kwargs)
        # Completing a consultation completes its appointment.
        if self.appointment_id and self.appointment.status != "completed":
            self.appointment.status = "completed"
            self.appointment.save(update_fields=["status"])

    def get_absolute_url(self):
        return reverse("consultations:detail", args=[self.pk])

    def __str__(self):
        return f"{self.consultation_id} - {self.patient.full_name} ({self.consultation_date})"
