from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class KYCTier(models.TextChoices):
    UNVERIFIED = "UNVERIFIED", "Unverified"
    BASIC = "BASIC", "Basic"
    FULL = "FULL", "Full"


class InvestmentLimit(BaseModel):
    kyc_tier = models.CharField(
        max_length=20,
        choices=KYCTier.choices,
        unique=True,
    )
    max_per_transaction = models.DecimalField(max_digits=18, decimal_places=2)
    max_per_month = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = "compliance_investment_limit"

    def __str__(self) -> str:
        return f"{self.kyc_tier}: txn={self.max_per_transaction}, mo={self.max_per_month}"
