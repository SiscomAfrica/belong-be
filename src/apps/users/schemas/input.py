from __future__ import annotations

from ninja import Schema


class UserUpdateIn(Schema):
    first_name: str | None = None
    last_name: str | None = None
    preferred_currency: str | None = None


class TermsAcceptIn(Schema):
    accepted: bool


class DeviceRegisterIn(Schema):
    device_id: str
    platform: str
    fcm_token: str = ""
