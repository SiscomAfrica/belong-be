from __future__ import annotations

from decimal import Decimal

from ninja import Schema
from pydantic import Field


class SimulationIn(Schema):
    goal: Decimal = Field(gt=0)
    contribution: Decimal = Field(gt=0)
    frequency: str = Field(pattern="^(DAILY|WEEKLY|BIWEEKLY|MONTHLY)$")
    years: int = Field(ge=1, le=50)
    avg_return: Decimal = Field(gt=0, le=100)
