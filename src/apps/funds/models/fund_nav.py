from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class FundNAV(BaseModel):
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.CASCADE,
        related_name="nav_history",
    )
    date = models.DateField(db_index=True)
    nav_value = models.DecimalField(max_digits=18, decimal_places=2)
    daily_change_pct = models.DecimalField(max_digits=8, decimal_places=4)

    class Meta:
        db_table = "funds_nav"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["fund", "date"],
                name="unique_fund_nav_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.fund.name} - {self.date}"
