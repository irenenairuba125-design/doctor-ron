from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Sum
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .permissions import has_role


def object_action(model, roles, func, success_message):
    """Build a POST-only view that runs func(obj) and redirects back to the object."""

    @login_required
    @require_POST
    def view(request, pk):
        if not has_role(request.user, roles):
            raise PermissionDenied
        obj = get_object_or_404(model, pk=pk)
        try:
            func(obj)
            messages.success(request, success_message)
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        return redirect(obj.get_absolute_url())

    return view


@login_required
def dashboard(request):
    from admissions.models import Admission, Ward
    from appointments.models import Appointment
    from billing.models import Bill
    from doctors.models import Doctor
    from laboratory.models import LabTest
    from patients.models import Patient
    from payments.models import Payment
    from pharmacy.models import Medicine, Prescription

    today = timezone.localdate()
    month_start = today.replace(day=1)
    user = request.user

    stats = [
        ("Patients", Patient.objects.count(), "people-fill", "primary", "patients:list"),
        ("Doctors", Doctor.objects.count(), "person-badge-fill", "info", "doctors:list"),
        ("Today's appointments", Appointment.objects.filter(appointment_date=today).count(),
         "calendar-check-fill", "success", "appointments:list"),
        ("Admitted patients", Admission.objects.filter(status="admitted").count(),
         "hospital-fill", "warning", "admissions:list"),
        ("Pending lab tests", LabTest.objects.exclude(status__in=["completed", "cancelled"]).count(),
         "eyedropper", "secondary", "laboratory:list"),
        ("Undispensed prescriptions", Prescription.objects.filter(dispensed=False).count(),
         "capsule", "danger", "pharmacy:prescription_list"),
    ]

    # Appointments over the last 7 days (bar chart)
    week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    per_day = dict(Appointment.objects.filter(appointment_date__gte=week[0], appointment_date__lte=today)
                   .values_list("appointment_date").annotate(n=Count("id")))
    # Appointment status breakdown for this month (doughnut chart)
    status_counts = dict(Appointment.objects.filter(appointment_date__gte=month_start)
                         .values_list("status").annotate(n=Count("id")))
    status_labels = dict(Appointment.Status.choices)

    wards = list(Ward.objects.all())
    total_beds = sum(w.number_of_beds for w in wards)
    free_beds = sum(w.available_beds for w in wards)

    # Shortcuts to "add" pages the user is allowed to use
    from .crud import REGISTRY
    wanted = ["patients", "appointments", "consultations", "laboratory", "billing", "payments"]
    quick_actions = [
        {"label": f"New {m.singular.lower()}", "icon": m.icon, "url": reverse(m.url_name("create"))}
        for ns in wanted for m in REGISTRY if m.namespace == ns and not m.prefix and m.can_edit(user)
    ][:4]

    hour = timezone.localtime().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    context = {
        "greeting": greeting,
        "quick_actions": quick_actions,
        "total_beds": total_beds,
        "free_beds": free_beds,
        "occupied_pct": round((total_beds - free_beds) * 100 / total_beds) if total_beds else 0,
        "chart_week": {
            "labels": [d.strftime("%a %d") for d in week],
            "values": [per_day.get(d, 0) for d in week],
        },
        "chart_status": {
            "labels": [status_labels[k] for k in status_labels],
            "values": [status_counts.get(k, 0) for k in status_labels],
        },
        "stats": stats,
        "today": today,
        "todays_appointments": Appointment.objects.filter(appointment_date=today)
        .select_related("patient", "doctor").order_by("appointment_time")[:10],
        "wards": wards,
        "low_stock": Medicine.objects.filter(quantity__lte=Medicine.LOW_STOCK_LEVEL)[:8],
        "expiring": Medicine.objects.filter(expiry_date__lte=today + timedelta(days=30))
        .order_by("expiry_date")[:8],
        "recent_patients": Patient.objects.all()[:6],
        "show_finance": has_role(user, ["accountant"]),
    }
    if context["show_finance"]:
        context.update({
            "revenue_month": Payment.objects.filter(payment_date__date__gte=month_start)
            .aggregate(s=Sum("amount_paid"))["s"] or 0,
            "revenue_today": Payment.objects.filter(payment_date__date=today)
            .aggregate(s=Sum("amount_paid"))["s"] or 0,
            "unpaid_bills": Bill.objects.exclude(payment_status="paid").count(),
        })
    return render(request, "core/dashboard.html", context)


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)
