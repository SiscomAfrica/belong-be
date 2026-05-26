from __future__ import annotations

from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class OTPChannel(models.TextChoices):
    SMS = "SMS", "SMS"
    EMAIL = "EMAIL", "Email"


class OTPPurpose(models.TextChoices):
    REGISTER = "REGISTER", "Register"
    LOGIN = "LOGIN", "Login"
    RESET_PIN = "RESET_PIN", "Reset PIN"


class OTP(BaseModel):
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True, default="")
    code = models.CharField(max_length=128)
    channel = models.CharField(max_length=10, choices=OTPChannel.choices, default=OTPChannel.SMS)
    purpose = models.CharField(max_length=20, choices=OTPPurpose.choices)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "authentication_otp"
        ordering = ["-created_at"]

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def __str__(self) -> str:
        return f"OTP({self.phone}, {self.purpose})"
