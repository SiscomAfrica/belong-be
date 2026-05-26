from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class ReferralStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONVERTED = "CONVERTED", "Converted"


class Referral(BaseModel):
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referrals_made",
    )
    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral",
    )
    status = models.CharField(
        max_length=20,
        choices=ReferralStatus.choices,
        default=ReferralStatus.PENDING,
        db_index=True,
    )
    converted_at = models.DateTimeField(null=True, blank=True)
    creds_awarded = models.IntegerField(default=0)

    class Meta:
        db_table = "referrals_referral"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["referrer", "referred_user"],
                name="unique_referral_pair",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.referrer_id} -> {self.referred_user_id}"
