from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class FundType(models.TextChoices):
    ETF = "ETF", "ETF"
    FUND = "FUND", "Fund"
    ASSET = "ASSET", "Asset"


class FundCategory(models.TextChoices):
    TECH = "TECH", "Technology"
    BONDS = "BONDS", "Bonds"
    REAL_ESTATE = "REAL_ESTATE", "Real Estate"
    CRYPTO = "CRYPTO", "Crypto"
    SUSTAINABILITY = "SUSTAINABILITY", "Sustainability"
    GENERAL = "GENERAL", "General"


class RiskLevel(models.IntegerChoices):
    VERY_LOW = 1, "Very Low"
    LOW = 2, "Low"
    MEDIUM = 3, "Medium"
    HIGH = 4, "High"
    VERY_HIGH = 5, "Very High"


class Currency(models.TextChoices):
    KES = "KES", "Kenyan Shilling"
    USD = "USD", "US Dollar"


class Fund(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)
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
    emoji = models.CharField(max_length=10, blank=True, default="")
    hero_image_url = models.URLField(blank=True, default="")
    is_trending = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "funds_fund"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
