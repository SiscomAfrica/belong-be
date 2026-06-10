from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field


class NotificationOut(Schema):
    id: UUID = Field(description="Notification identifier")
    type: str = Field(description="Notification type (e.g. INVESTMENT_CONFIRMED, KYC_APPROVED)")
    title: str = Field(description="Notification title")
    body: str = Field(description="Notification body text")
    is_read: bool = Field(description="Whether the user has read this notification")
    action_url: str = Field(description="Deep-link URL for tap action")
    metadata: dict = Field(description="Additional key-value data for the client")
    created_at: datetime = Field(description="Notification timestamp")


class NotificationListOut(Schema):
    items: list[NotificationOut] = Field(description="List of notifications")
    count: int = Field(description="Total number of matching notifications")
    unread_count: int = Field(description="Total unread notifications for the user")


class PushTokenOut(Schema):
    id: UUID = Field(description="Push token record identifier")
    token: str = Field(description="Device push token string")
    platform: str = Field(description="Device platform: IOS | ANDROID")
    is_active: bool = Field(description="Whether this token is active")
    created_at: datetime = Field(description="Registration timestamp")


class MarkAllReadOut(Schema):
    marked_count: int = Field(description="Number of notifications marked as read")
