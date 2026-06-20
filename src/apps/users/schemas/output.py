from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.common.services.s3 import generate_presigned_download


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
    profile_image_url: str | None = Field(default=None, description="Presigned URL for profile photo")
    created_at: datetime = Field(description="Account creation timestamp")

    @staticmethod
    def resolve_profile_image_url(obj: object) -> str | None:
        key = getattr(obj, "profile_image_key", "")
        if not key:
            return None
        return generate_presigned_download(file_key=key)["download_url"]


class DeviceOut(Schema):
    id: UUID = Field(description="Unique device record identifier")
    device_id: str = Field(description="OS-level device identifier")
    platform: str = Field(description="Device platform: IOS | ANDROID")
    fcm_token: str = Field(description="Firebase Cloud Messaging token")
    is_active: bool = Field(description="Whether this device is active")
    created_at: datetime = Field(description="Registration timestamp")
