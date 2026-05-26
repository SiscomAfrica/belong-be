from __future__ import annotations

from django.utils import timezone

from apps.authentication.models import OTP


def count_active_otps(*, phone: str) -> int:
    return OTP.objects.filter(
        phone=phone,
        is_used=False,
        expires_at__gt=timezone.now(),
    ).count()
