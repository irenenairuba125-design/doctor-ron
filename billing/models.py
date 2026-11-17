from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from core.models import code


class Bill(models.Model):
    """11. Billing model."""

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partially paid"
        PAID = "paid", "Paid"

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="bills")
    consultation_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    laboratory_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medicine_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    admission_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices,
                                      default=PaymentStatus.UNPAID, editable=False)
    bill_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "bills"
        ordering = ["-bill_date", "-id"]

    @property
    def bill_id(self):
        return code("BIL", self.pk)

    @property
    def amount_paid(self):
        if not self.pk:
            return Decimal("0")
        return self.payments.aggregate(s=Sum("amount_paid"))["s"] or Decimal("0")

    @property
    def balance(self):
        return self.total_amount - self.amount_paid

    def compute_status(self):
        paid = self.amount_paid
        if paid <= 0:
            return self.PaymentStatus.UNPAID
        if paid < self.total_amount:
            return self.PaymentStatus.PARTIAL
        return self.PaymentStatus.PAID

    def save(self, *args, **kwargs):
        self.total_amount = (
            self.consultation_fees + self.laboratory_fees
            + self.medicine_charges + self.admission_charges
        )
        self.payment_status = self.compute_status()
        super().save(*args, **kwargs)

    def refresh_payment_status(self):
        self.payment_status = self.compute_status()
        Bill.objects.filter(pk=self.pk).update(payment_status=self.payment_status)

    def populate_from_records(self):
        """Fill charges from the patient's records since their previous bill."""
        patient = self.patient
        previous = patient.bills.exclude(pk=self.pk).filter(bill_date__lt=self.bill_date) \
            .order_by("-bill_date").values_list("bill_date", flat=True).first()
        until = self.bill_date

        def in_period(field):
            # Records after the previous bill (or all records if this is the first bill)
            period = {f"{field}__lte": until}
            if previous:
                period[f"{field}__gt"] = previous
            return period

        def total(qs, field):
            return qs.aggregate(s=Sum(field))["s"] or Decimal("0")

        self.consultation_fees = total(
            patient.consultations.filter(**in_period("consultation_date")), "fee")
        self.laboratory_fees = total(
            patient.lab_tests.filter(**in_period("test_date")).exclude(status="cancelled"), "fee")
        self.medicine_charges = sum(
            (p.cost for p in patient.prescriptions.select_related("medicine")
             .filter(**in_period("prescription_date"))),
            Decimal("0"),
        )
        self.admission_charges = sum(
            (a.charges for a in patient.admissions.select_related("ward")
             .filter(**in_period("admission_date"))),
            Decimal("0"),
        )
        self.save()

    def get_absolute_url(self):
        return reverse("billing:detail", args=[self.pk])

    def __str__(self):
        return f"{self.bill_id} - {self.patient.full_name} ({self.total_amount:,.2f})"
