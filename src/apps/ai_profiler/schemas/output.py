from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema


class SessionOut(Schema):
    id: UUID
    status: str
    summary: str
    created_at: datetime


class MessageOut(Schema):
    id: UUID
    role: str
    content: str
    created_at: datetime


class SessionDetailOut(Schema):
    id: UUID
    status: str
    summary: str
    created_at: datetime
    messages: list[MessageOut]

    @staticmethod
    def resolve_messages(obj):
        return obj.messages.all()


class InvestorProfileOut(Schema):
    id: UUID
    risk_tolerance: int
    time_horizon: str
    investment_goal: str
    interests: list
    investor_type: str
    recommended_fund_id: UUID | None = None
    created_at: datetime

    @staticmethod
    def resolve_investor_type(obj):
        return obj.user.investor_type


class SessionListOut(Schema):
    items: list[SessionOut]
    count: int
