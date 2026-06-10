from __future__ import annotations

from ninja import Schema
from pydantic import Field


class OTPSentOut(Schema):
    message: str = Field(description="Human-readable confirmation message")
    expires_in_seconds: int = Field(default=300, description="OTP validity window in seconds")


class AuthTokenOut(Schema):
    access: str = Field(description="Short-lived JWT access token (15 min)")
    refresh: str = Field(description="Long-lived JWT refresh token (30 days)")
