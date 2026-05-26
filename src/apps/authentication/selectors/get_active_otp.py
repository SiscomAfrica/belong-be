from __future__ import annotations

from django.utils import timezone

from apps.authentication.models import OTP


def get_active_otp(*, phone: str, purpose: str) -> OTP | None:
    return (
        OTP.objects.filter(
            phone=phone,
            purpose=purpose,
            is_used=False,
            expires_at__gt=timezone.now(),
        )
        .order_by("-created_at")
        .first()
    )
