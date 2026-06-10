from __future__ import annotations

import datetime as dt

from decimal import Decimal

from ninja import Schema
from pydantic import Field


class ChartDataPoint(Schema):
    date: dt.date = Field(description="Data point date")
    value: Decimal = Field(description="Projected portfolio value at this date")


class SimulationOut(Schema):
    projected_final_value: Decimal = Field(description="Projected portfolio value at end of horizon")
    months_to_goal: int | None = Field(default=None, description="Estimated months to reach goal (null if unreachable)")
    total_contributions: Decimal = Field(description="Sum of all contributions over the period")
    total_earnings: Decimal = Field(description="Projected total earnings from returns")
    chart_data_points: list[ChartDataPoint] = Field(description="Time-series data for charting projections")
