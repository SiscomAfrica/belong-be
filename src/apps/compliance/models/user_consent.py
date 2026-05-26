from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class UserConsent(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consents",
    )
    consent_version = models.ForeignKey(
        "compliance.ConsentVersion",
        on_delete=models.PROTECT,
        related_name="acceptances",
    )
    accepted_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "compliance_user_consent"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "consent_version"],
                name="unique_user_consent_version",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} accepted {self.consent_version_id}"
