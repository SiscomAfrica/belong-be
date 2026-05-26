from __future__ import annotations

from ninja import Schema
from pydantic import Field


class PushTokenRegisterIn(Schema):
    token: str = Field(min_length=10, max_length=500)
    platform: str = Field(pattern="^(IOS|ANDROID)$")
