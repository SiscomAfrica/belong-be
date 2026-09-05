from __future__ import annotations

from datetime import timedelta

import bcrypt
import pytest
from django.core.cache import cache
from django.utils import timezone
from ninja.testing import TestClient

from apps.authentication.models import OTP
from apps.authentication.otp_hashing import hash_otp_code
from apps.users.services.create_user import create_user
from config.urls import api

PHONE = "+254700000111"
CODE = "123456"
OLD_PIN = "1111"


@pytest.fixture(autouse=True)
def _clear_throttle_counters():
    """Counters live in the cache and would otherwise leak between tests."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(api)


@pytest.fixture
def user():
    person = create_user(phone=PHONE)
    person.pin_hash = bcrypt.hashpw(OLD_PIN.encode(), bcrypt.gensalt()).decode()
    person.save(update_fields=["pin_hash"])
    return person


@pytest.fixture
def make_otp():
    """Issue a reset code, defaulting to the state the app actually sends.

    `used=True` is the default because the client verifies the code on its own
    screen before collecting the new PIN, so every real reset arrives with the
    OTP already spent.
    """

    def _make(*, used: bool = True, age_minutes: int = 0, purpose: str = "LOGIN") -> OTP:
        otp = OTP.objects.create(
            phone=PHONE,
            code=hash_otp_code(CODE),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=used,
        )
        if age_minutes:
            OTP.objects.filter(pk=otp.pk).update(
                created_at=timezone.now() - timedelta(minutes=age_minutes),
            )
            otp.refresh_from_db()
        return otp

    return _make
