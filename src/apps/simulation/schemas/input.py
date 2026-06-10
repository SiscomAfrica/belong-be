from __future__ import annotations

from decimal import Decimal

from ninja import Schema
from pydantic import Field


class SimulationIn(Schema):
    goal: Decimal = Field(gt=0, description="Target investment goal amount in KES")
    contribution: Decimal = Field(gt=0, description="Periodic contribution amount in KES")
    frequency: str = Field(pattern="^(DAILY|WEEKLY|BIWEEKLY|MONTHLY)$", description="Contribution frequency")
    years: int = Field(ge=1, le=50, description="Investment horizon in years (1-50)")
    avg_return: Decimal = Field(gt=0, le=100, description="Expected average annual return percentage")
