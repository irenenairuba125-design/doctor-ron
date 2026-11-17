import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import code


class Payment(models.Model):
    """12. Payment model - transactions made against a bill."""

    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        MOBILE_MONEY = "mobile_money", "Mobile money"
        CARD = "card", "Card"
        BANK = "bank", "Bank transfer"
        INSURANCE = "insurance", "Insurance"

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="payments")
    bill = models.ForeignKey("billing.Bill", on_delete=models.PROTECT, related_name="payments")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=Method.choices, default=Method.CASH)
    payment_date = models.DateTimeField(default=timezone.now)
    transaction_reference = models.CharField(
        max_length=64, unique=True, blank=True,
        help_text="Leave blank to generate automatically",
    )

    class Meta:
        db_table = "payments"
        ordering = ["-payment_date"]

    @property
    def payment_id(self):
        return code("PAY", self.pk)

    def clean(self):
        errors = {}
        if self.bill_id and self.patient_id and self.bill.patient_id != self.patient_id:
            errors["bill"] = "This bill belongs to a different patient."
        if self.amount_paid is not None and self.amount_paid <= 0:
            errors["amount_paid"] = "Amount must be greater than zero."
        elif self.bill_id and self.amount_paid:
            already = self.bill.amount_paid
            if self.pk:
                already -= Payment.objects.get(pk=self.pk).amount_paid
            if already + self.amount_paid > self.bill.total_amount:
                errors["amount_paid"] = (
                    f"Payment exceeds the outstanding balance of "
                    f"{self.bill.total_amount - already:,.2f}."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.transaction_reference:
            self.transaction_reference = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        if self.bill_id and not self.patient_id:
            self.patient_id = self.bill.patient_id
        super().save(*args, **kwargs)
        self.bill.refresh_payment_status()

    def delete(self, *args, **kwargs):
        bill = self.bill
        result = super().delete(*args, **kwargs)
        bill.refresh_payment_status()
        return result

    def get_absolute_url(self):
        return reverse("payments:detail", args=[self.pk])

    def __str__(self):
        return f"{self.transaction_reference} - {self.amount_paid:,.2f}"
