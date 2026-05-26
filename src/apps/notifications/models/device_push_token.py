from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class DevicePlatform(models.TextChoices):
    IOS = "IOS", "iOS"
    ANDROID = "ANDROID", "Android"


class DevicePushToken(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_tokens",
    )
    token = models.CharField(max_length=500, unique=True, db_index=True)
    platform = models.CharField(max_length=10, choices=DevicePlatform.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notifications_device_push_token"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "token"], name="unique_user_push_token"),
        ]

    def __str__(self) -> str:
        return f"{self.platform} token for {self.user_id}"
