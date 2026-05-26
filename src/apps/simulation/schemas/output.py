from __future__ import annotations

from datetime import date
from decimal import Decimal

from ninja import Schema


class ChartDataPoint(Schema):
    date: date
    value: Decimal


class SimulationOut(Schema):
    projected_final_value: Decimal
    months_to_goal: int | None
    total_contributions: Decimal
    total_earnings: Decimal
    chart_data_points: list[ChartDataPoint]
