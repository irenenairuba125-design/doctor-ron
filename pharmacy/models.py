from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone

from core.models import code


class Medicine(models.Model):
    """9. Pharmacy model - medicine stock."""

    class Category(models.TextChoices):
        TABLET = "tablet", "Tablet"
        CAPSULE = "capsule", "Capsule"
        SYRUP = "syrup", "Syrup"
        INJECTION = "injection", "Injection"
        CREAM = "cream", "Cream / Ointment"
        DROPS = "drops", "Drops"
        INHALER = "inhaler", "Inhaler"
        OTHER = "other", "Other"

    LOW_STOCK_LEVEL = 20

    name = models.CharField("Medicine name", max_length=150)
    category = models.CharField(max_length=15, choices=Category.choices, default=Category.TABLET)
    quantity = models.PositiveIntegerField(default=0, help_text="Units in stock")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    expiry_date = models.DateField()

    class Meta:
        db_table = "medicines"
        ordering = ["name"]

    @property
    def medicine_id(self):
        return code("MED", self.pk)

    @property
    def is_expired(self):
        return self.expiry_date < timezone.localdate()

    @property
    def is_low_stock(self):
        return self.quantity <= self.LOW_STOCK_LEVEL

    def get_absolute_url(self):
        return reverse("pharmacy:medicine_detail", args=[self.pk])

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Prescription(models.Model):
    """10. Prescription model."""

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE,
                                related_name="prescriptions")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT,
                               related_name="prescriptions")
    consultation = models.ForeignKey(
        "consultations.Consultation", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="prescriptions",
    )
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name="prescriptions")
    dosage = models.CharField(max_length=100, help_text="e.g. 500mg, 2 tablets")
    frequency = models.CharField(max_length=100, help_text="e.g. 3 times a day")
    duration = models.CharField(max_length=100, help_text="e.g. 5 days")
    quantity = models.PositiveIntegerField(default=1, help_text="Units to dispense")
    prescription_date = models.DateField(default=timezone.localdate)
    dispensed = models.BooleanField(default=False)

    class Meta:
        db_table = "prescriptions"
        ordering = ["-prescription_date", "-id"]

    @property
    def prescription_id(self):
        return code("PRE", self.pk)

    @property
    def cost(self):
        return self.medicine.unit_price * self.quantity

    def clean(self):
        if self.medicine_id:
            if self.medicine.is_expired:
                raise ValidationError({"medicine": "This medicine has expired."})

    @transaction.atomic
    def dispense(self):
        """Reduce stock when the pharmacist dispenses the prescription."""
        if self.dispensed:
            raise ValidationError("Prescription already dispensed.")
        updated = Medicine.objects.filter(
            pk=self.medicine_id, quantity__gte=self.quantity
        ).update(quantity=F("quantity") - self.quantity)
        if not updated:
            raise ValidationError(f"Not enough {self.medicine.name} in stock.")
        self.dispensed = True
        self.save(update_fields=["dispensed"])

    def get_absolute_url(self):
        return reverse("pharmacy:prescription_detail", args=[self.pk])

    def __str__(self):
        return f"{self.prescription_id} - {self.medicine.name} for {self.patient.full_name}"
