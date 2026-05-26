from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel


class PlanFrequency(models.TextChoices):
    DAILY = "DAILY", "Daily"
    WEEKLY = "WEEKLY", "Weekly"
    BIWEEKLY = "BIWEEKLY", "Biweekly"
    MONTHLY = "MONTHLY", "Monthly"


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
