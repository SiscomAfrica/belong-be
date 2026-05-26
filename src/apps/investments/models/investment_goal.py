from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class InvestmentGoal(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investment_goals",
    )
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.PROTECT,
        related_name="investment_goals",
    )
    target_amount = models.DecimalField(max_digits=18, decimal_places=2)
    target_date = models.DateField()

    class Meta:
        db_table = "investments_investment_goal"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Goal: {self.user_id} -> {self.target_amount}"
