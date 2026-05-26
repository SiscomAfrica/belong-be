from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class Holding(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.PROTECT,
        related_name="holdings",
    )
    total_units = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    total_invested = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    average_nav = models.DecimalField(max_digits=18, decimal_places=6, default=0)

    class Meta:
        db_table = "investments_holding"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "fund"],
                name="unique_user_fund_holding",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} - {self.fund_id} - {self.total_units} units"
