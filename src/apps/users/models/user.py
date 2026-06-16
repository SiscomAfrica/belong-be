from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.models.manager import UserManager


class InvestorType(models.TextChoices):
    CONSERVATIVE = "CONSERVATIVE", "Conservative"
    MODERATE = "MODERATE", "Moderate"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    AGGRESSIVE = "AGGRESSIVE", "Aggressive"
    HIGH_RISK = "HIGH_RISK", "High Risk"


class CurrencyChoice(models.TextChoices):
    KES = "KES", "Kenyan Shilling"
    USD = "USD", "US Dollar"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True, db_index=True)
    pin_hash = models.CharField(max_length=128, blank=True, default="")
    biometrics_enabled = models.BooleanField(default=False)
    investor_type = models.CharField(
        max_length=20,
        choices=InvestorType.choices,
        blank=True,
        default="",
    )
    preferred_currency = models.CharField(
        max_length=3,
        choices=CurrencyChoice.choices,
        default=CurrencyChoice.KES,
    )
    is_onboarded = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(max_length=12, unique=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "users_user"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.phone
