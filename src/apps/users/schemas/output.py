from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema


class UserOut(Schema):
    id: UUID
    phone: str
    first_name: str
    last_name: str
    investor_type: str
    preferred_currency: str
    is_onboarded: bool
    biometrics_enabled: bool
    terms_accepted_at: datetime | None
    referral_code: str
    created_at: datetime


class DeviceOut(Schema):
    id: UUID
    device_id: str
    platform: str
    fcm_token: str
    is_active: bool
    created_at: datetime
