from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel
from apps.common.storage import hero_image_upload_path
from apps.common.validators import validate_image_max_5mb
from apps.funds.models.enums import (
    Currency,
    FundCategory,
    FundType,
    ManagementType,
    RiskLevel,
)


class Fund(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)
    ticker_symbol = models.CharField(max_length=10, blank=True, default="")
    description = models.TextField()
    fund_type = models.CharField(max_length=10, choices=FundType.choices)
    category = models.CharField(max_length=20, choices=FundCategory.choices)
    risk_level = models.IntegerField(choices=RiskLevel.choices)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    minimum_investment = models.DecimalField(max_digits=18, decimal_places=2)
    lock_in_days = models.PositiveIntegerField(default=0)
    projected_annual_return = models.DecimalField(max_digits=6, decimal_places=2)
    effective_annual_yield = models.DecimalField(max_digits=6, decimal_places=2)
    annualized_daily_yield = models.DecimalField(max_digits=6, decimal_places=2)
    expense_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
    )
    aum = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True,
        help_text="Assets Under Management in USD",
    )
    ytd_return = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
    )
    launched_date = models.DateField(null=True, blank=True)
    management_type = models.CharField(
        max_length=20, choices=ManagementType.choices, blank=True, default="",
    )
    listed_country = models.CharField(max_length=50, blank=True, default="")
    fund_manager = models.CharField(max_length=100, blank=True, default="")
    top_holdings = models.JSONField(default=list)
    perfect_for = models.TextField(blank=True, default="")
    chart_url = models.URLField(max_length=500, blank=True, default="")
    emoji = models.CharField(max_length=10, blank=True, default="")
    hero_image_url = models.URLField(blank=True, default="")
    hero_image = models.ImageField(
        upload_to=hero_image_upload_path,
        blank=True,
        default="",
        validators=[validate_image_max_5mb],
    )
    is_trending = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "funds_fund"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
