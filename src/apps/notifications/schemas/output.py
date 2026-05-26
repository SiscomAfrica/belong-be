from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema


class NotificationOut(Schema):
    id: UUID
    type: str
    title: str
    body: str
    is_read: bool
    action_url: str
    metadata: dict
    created_at: datetime


class NotificationListOut(Schema):
    items: list[NotificationOut]
    count: int
    unread_count: int


class PushTokenOut(Schema):
    id: UUID
    token: str
    platform: str
    is_active: bool
    created_at: datetime


class MarkAllReadOut(Schema):
    marked_count: int
