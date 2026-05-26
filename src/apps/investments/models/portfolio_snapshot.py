from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class PortfolioSnapshot(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolio_snapshots",
    )
    date = models.DateField(db_index=True)
    total_value = models.DecimalField(max_digits=18, decimal_places=2)
    total_invested = models.DecimalField(max_digits=18, decimal_places=2)
    daily_change = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    daily_change_pct = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    class Meta:
        db_table = "investments_portfolio_snapshot"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"],
                name="unique_user_portfolio_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} - {self.date} - {self.total_value}"
