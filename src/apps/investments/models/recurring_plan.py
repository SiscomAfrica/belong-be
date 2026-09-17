from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel


class PlanFrequency(models.TextChoices):
    """Contribution cadences, aligned 1:1 with M-Pesa Ratiba's Frequency enum.

    Ratiba is what collects the money, so a plan must never hold a cadence
    Ratiba cannot express — there would be no way to schedule the deduction.
    The numeric codes Ratiba wants live in apps.payments.providers.ratiba_request,
    so this app stays ignorant of Daraja's wire format.
    """

    ONE_OFF = "ONE_OFF", "One Off"
    DAILY = "DAILY", "Daily"
    WEEKLY = "WEEKLY", "Weekly"
    BIWEEKLY = "BIWEEKLY", "Bi-weekly"
    MONTHLY = "MONTHLY", "Monthly"
    BIMONTHLY = "BIMONTHLY", "Bi-monthly"
    QUARTERLY = "QUARTERLY", "Quarterly"
    HALF_YEARLY = "HALF_YEARLY", "Half Yearly"
    YEARLY = "YEARLY", "Yearly"


class RecurringPlan(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurring_plans",
    )
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.PROTECT,
        related_name="recurring_plans",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=PlanFrequency.choices)
    next_run_date = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "investments_recurring_plan"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "fund"],
                condition=Q(is_active=True),
                name="unique_active_user_fund_plan",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} -> {self.fund_id} ({self.frequency})"
