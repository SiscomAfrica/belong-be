from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field


class SessionOut(Schema):
    id: UUID = Field(description="Profiler session identifier")
    status: str = Field(description="Session status: ACTIVE | COMPLETED")
    summary: str = Field(description="AI-generated session summary")
    created_at: datetime = Field(description="Session creation timestamp")


class MessageOut(Schema):
    id: UUID = Field(description="Message identifier")
    role: str = Field(description="Message author: USER | ASSISTANT")
    content: str = Field(description="Message text content")
    created_at: datetime = Field(description="Message timestamp")


class SessionDetailOut(Schema):
    id: UUID = Field(description="Profiler session identifier")
    status: str = Field(description="Session status: ACTIVE | COMPLETED")
    summary: str = Field(description="AI-generated session summary")
    created_at: datetime = Field(description="Session creation timestamp")
    messages: list[MessageOut] = Field(description="Ordered list of session messages")

    @staticmethod
    def resolve_messages(obj):
        return obj.messages.all()


class InvestorProfileOut(Schema):
    id: UUID = Field(description="Profile identifier")
    risk_tolerance: int = Field(description="Risk score 1-10 (10 = highest risk)")
    time_horizon: str = Field(description="Investment horizon: SHORT | MEDIUM | LONG")
    investment_goal: str = Field(description="Primary goal (e.g. RETIREMENT, EDUCATION)")
    interests: list = Field(description="List of investment interest tags")
    investor_type: str = Field(description="Assigned type (e.g. CONSERVATIVE, AGGRESSIVE)")
    recommended_fund_id: UUID | None = Field(default=None, description="AI-recommended fund UUID")
    created_at: datetime = Field(description="Profile creation timestamp")

    @staticmethod
    def resolve_investor_type(obj):
        return obj.user.investor_type


class SessionListOut(Schema):
    items: list[SessionOut] = Field(description="List of profiler sessions")
    count: int = Field(description="Total number of sessions")
