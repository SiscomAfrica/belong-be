from __future__ import annotations

from ninja import Schema
from pydantic import Field


class PushTokenRegisterIn(Schema):
    token: str = Field(min_length=10, max_length=500, description="FCM or APNs push notification token")
    platform: str = Field(pattern="^(IOS|ANDROID)$", description="Device platform: IOS | ANDROID")
