from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class TimeHorizon(models.TextChoices):
    SHORT = "SHORT", "Short Term"
    MEDIUM = "MEDIUM", "Medium Term"
    LONG = "LONG", "Long Term"


class InvestorProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investor_profile",
    )
    risk_tolerance = models.IntegerField(
        help_text="1 (very low) to 5 (very high)",
    )
    time_horizon = models.CharField(
        max_length=20,
        choices=TimeHorizon.choices,
    )
    investment_goal = models.TextField(blank=True, default="")
    interests = models.JSONField(default=list)
    recommended_fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "ai_profiler_investor_profile"

    def __str__(self) -> str:
        return f"Profile for {self.user_id}"
