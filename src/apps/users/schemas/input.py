from __future__ import annotations

from ninja import Schema
from pydantic import Field


class UserUpdateIn(Schema):
    first_name: str | None = Field(default=None, description="User first name")
    last_name: str | None = Field(default=None, description="User last name")
    preferred_currency: str | None = Field(default=None, description="ISO 4217 currency code (e.g. KES, USD)")
    profile_image_key: str | None = Field(default=None, description="S3 object key for profile photo")


class TermsAcceptIn(Schema):
    accepted: bool = Field(description="Must be true to accept current terms")


class DeviceRegisterIn(Schema):
    device_id: str = Field(description="Unique device identifier from OS")
    platform: str = Field(description="Device platform: IOS | ANDROID")
    fcm_token: str = Field(default="", description="Firebase Cloud Messaging token for push notifications")
