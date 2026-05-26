from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class InvestmentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class Investment(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investments",
    )
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.PROTECT,
        related_name="investments",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    units = models.DecimalField(max_digits=18, decimal_places=6)
    nav_at_purchase = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=InvestmentStatus.choices,
        default=InvestmentStatus.PENDING,
        db_index=True,
    )
    idempotency_key = models.CharField(max_length=64, unique=True, db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "investments_investment"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} - {self.fund_id} - {self.amount}"
