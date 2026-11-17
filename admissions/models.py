from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import code


class Ward(models.Model):
    """7. Ward model."""

    class WardType(models.TextChoices):
        GENERAL = "general", "General"
        PRIVATE = "private", "Private"
        ICU = "icu", "Intensive Care Unit"
        MATERNITY = "maternity", "Maternity"
        PEDIATRIC = "pediatric", "Pediatric"
        SURGICAL = "surgical", "Surgical"
        EMERGENCY = "emergency", "Emergency"

    name = models.CharField("Ward name", max_length=100, unique=True)
    ward_type = models.CharField(max_length=15, choices=WardType.choices, default=WardType.GENERAL)
    number_of_beds = models.PositiveIntegerField()
    available_beds = models.PositiveIntegerField(
        editable=False, default=0, help_text="Updated automatically from active admissions"
    )
    daily_charge = models.DecimalField("Daily charge per bed", max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "wards"
        ordering = ["name"]

    @property
    def ward_id(self):
        return code("WRD", self.pk)

    def occupied_beds(self):
        return self.admissions.filter(status=Admission.Status.ADMITTED).count()

    def refresh_available_beds(self, save=True):
        occupied = self.occupied_beds() if self.pk else 0
        self.available_beds = max(self.number_of_beds - occupied, 0)
        if save:
            Ward.objects.filter(pk=self.pk).update(available_beds=self.available_beds)

    def save(self, *args, **kwargs):
        self.refresh_available_beds(save=False)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("admissions:ward_detail", args=[self.pk])

    def __str__(self):
        return f"{self.name} ({self.available_beds}/{self.number_of_beds} beds free)"


class Admission(models.Model):
    """6. Admission model."""

    class Status(models.TextChoices):
        ADMITTED = "admitted", "Admitted"
        DISCHARGED = "discharged", "Discharged"
        TRANSFERRED = "transferred", "Transferred"
        DECEASED = "deceased", "Deceased"

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE,
                                related_name="admissions")
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT, related_name="admissions")
    bed_number = models.PositiveIntegerField()
    admission_date = models.DateField(default=timezone.localdate)
    discharge_date = models.DateField(null=True, blank=True)
    status = models.CharField("Admission status", max_length=15, choices=Status.choices,
                              default=Status.ADMITTED)
    reason = models.TextField("Reason for admission", blank=True)

    class Meta:
        db_table = "admissions"
        ordering = ["-admission_date", "-id"]

    @property
    def admission_id(self):
        return code("ADM", self.pk)

    @property
    def days_admitted(self):
        end = self.discharge_date or timezone.localdate()
        return max((end - self.admission_date).days, 1)

    @property
    def charges(self):
        return self.ward.daily_charge * self.days_admitted

    def clean(self):
        errors = {}
        if self.ward_id and self.bed_number:
            if self.bed_number > self.ward.number_of_beds:
                errors["bed_number"] = f"{self.ward.name} only has {self.ward.number_of_beds} beds."
            elif self.status == self.Status.ADMITTED and Admission.objects.filter(
                ward_id=self.ward_id, bed_number=self.bed_number, status=self.Status.ADMITTED
            ).exclude(pk=self.pk).exists():
                errors["bed_number"] = "This bed is already occupied."
        if self.discharge_date and self.admission_date and self.discharge_date < self.admission_date:
            errors["discharge_date"] = "Discharge date cannot be before the admission date."
        if self.status == self.Status.ADMITTED and self.patient_id and Admission.objects.filter(
            patient_id=self.patient_id, status=self.Status.ADMITTED
        ).exclude(pk=self.pk).exists():
            errors["patient"] = "This patient is already admitted."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.status != self.Status.ADMITTED and not self.discharge_date:
            self.discharge_date = timezone.localdate()
        old_ward_id = None
        if self.pk:
            old_ward_id = Admission.objects.filter(pk=self.pk).values_list("ward_id", flat=True).first()
        super().save(*args, **kwargs)
        self.ward.refresh_available_beds()
        if old_ward_id and old_ward_id != self.ward_id:
            Ward.objects.get(pk=old_ward_id).refresh_available_beds()

    def delete(self, *args, **kwargs):
        ward = self.ward
        result = super().delete(*args, **kwargs)
        ward.refresh_available_beds()
        return result

    def get_absolute_url(self):
        return reverse("admissions:detail", args=[self.pk])

    def __str__(self):
        return f"{self.admission_id} - {self.patient.full_name} ({self.ward.name}, bed {self.bed_number})"
