from __future__ import annotations

from django.db import models


class FundType(models.TextChoices):
    ETF = "ETF", "ETF"
    FUND = "FUND", "Fund"
    ASSET = "ASSET", "Asset"


class FundCategory(models.TextChoices):
    TECH = "TECH", "Technology"
    SEMICONDUCTOR = "SEMICONDUCTOR", "Semiconductor"
    DIVIDEND = "DIVIDEND", "Dividend"
    DIVERSIFIED = "DIVERSIFIED", "Diversified"
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


class ManagementType(models.TextChoices):
    PASSIVE = "PASSIVE", "Passive"
    ACTIVE = "ACTIVE", "Active"
    RULES_BASED = "RULES_BASED", "Rules-based passive"


class Currency(models.TextChoices):
    KES = "KES", "Kenyan Shilling"
    USD = "USD", "US Dollar"
