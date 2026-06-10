from __future__ import annotations

from decimal import Decimal

from ninja import Schema
from pydantic import Field


class ProjectionIn(Schema):
    goal: Decimal = Field(description="Target investment amount in KES")
    contribution: Decimal = Field(description="Periodic contribution amount in KES")
    frequency: str = Field(description="Contribution frequency: DAILY | WEEKLY | BIWEEKLY | MONTHLY")
    years: int = Field(description="Investment horizon in years")
    annual_return_pct: Decimal = Field(description="Expected annual return percentage")
