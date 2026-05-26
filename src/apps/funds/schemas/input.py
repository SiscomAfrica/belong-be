from __future__ import annotations

from decimal import Decimal

from ninja import Schema


class ProjectionIn(Schema):
    goal: Decimal
    contribution: Decimal
    frequency: str
    years: int
    annual_return_pct: Decimal
