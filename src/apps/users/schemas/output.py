from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field


class UserOut(Schema):
    id: UUID = Field(description="Unique user identifier")
    phone: str = Field(description="E.164 phone number")
    first_name: str = Field(description="User first name")
    last_name: str = Field(description="User last name")
    investor_type: str = Field(description="AI-assigned investor type (e.g. CONSERVATIVE)")
    preferred_currency: str = Field(description="ISO 4217 currency code")
    is_onboarded: bool = Field(description="Whether user completed onboarding")
    biometrics_enabled: bool = Field(description="Whether biometric login is active")
    terms_accepted_at: datetime | None = Field(default=None, description="When terms were last accepted")
    referral_code: str = Field(description="User's shareable referral code")
    created_at: datetime = Field(description="Account creation timestamp")


class DeviceOut(Schema):
    id: UUID = Field(description="Unique device record identifier")
    device_id: str = Field(description="OS-level device identifier")
    platform: str = Field(description="Device platform: IOS | ANDROID")
    fcm_token: str = Field(description="Firebase Cloud Messaging token")
    is_active: bool = Field(description="Whether this device is active")
    created_at: datetime = Field(description="Registration timestamp")
