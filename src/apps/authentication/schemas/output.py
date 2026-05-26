from __future__ import annotations

from ninja import Schema


class OTPSentOut(Schema):
    message: str
    expires_in_seconds: int = 300


class AuthTokenOut(Schema):
    access: str
    refresh: str
