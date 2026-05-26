from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Platform(models.TextChoices):
    IOS = "IOS", "iOS"
    ANDROID = "ANDROID", "Android"


class UserDevice(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=10, choices=Platform.choices)
    fcm_token = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users_device"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "device_id"],
                name="unique_user_device",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.device_id}"
