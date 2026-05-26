from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class PerformancePeriod(models.TextChoices):
    ONE_MONTH = "1M", "1 Month"
    THREE_MONTHS = "3M", "3 Months"
    SIX_MONTHS = "6M", "6 Months"
    ONE_YEAR = "1Y", "1 Year"
    FIVE_YEARS = "5Y", "5 Years"


class FundPerformance(BaseModel):
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.CASCADE,
        related_name="performances",
    )
    period = models.CharField(max_length=5, choices=PerformancePeriod.choices)
    return_pct = models.DecimalField(max_digits=8, decimal_places=4)
    start_value = models.DecimalField(max_digits=18, decimal_places=2)
    end_value = models.DecimalField(max_digits=18, decimal_places=2)
    calculated_at = models.DateTimeField()

    class Meta:
        db_table = "funds_performance"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["fund", "period"],
                name="unique_fund_performance_period",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.fund.name} - {self.period}"
