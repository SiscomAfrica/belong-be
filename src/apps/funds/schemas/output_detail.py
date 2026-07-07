from __future__ import annotations

import datetime as dt

from datetime import datetime
from decimal import Decimal

from ninja import Schema
from pydantic import Field

from apps.funds.schemas.output import FundOut, FundPerformanceOut


class FundDetailOut(FundOut):
    description: str = Field(description="Fund description")
    lock_in_days: int = Field(description="Minimum holding period in days")
    effective_annual_yield: Decimal = Field(description="Current effective annual yield")
    annualized_daily_yield: Decimal = Field(description="Daily yield annualized")
    expense_ratio: Decimal | None = Field(description="Fund expense ratio %")
    aum: Decimal | None = Field(description="Assets Under Management in USD")
    ytd_return: Decimal | None = Field(description="Year-to-date return %")
    launched_date: dt.date | None = Field(description="ETF launch date")
    management_type: str = Field(description="PASSIVE | ACTIVE | RULES_BASED")
    listed_country: str = Field(description="Country where ETF is listed")
    fund_manager: str = Field(description="Fund manager name")
    top_holdings: list[str] = Field(description="Top holdings list")
    perfect_for: str = Field(description="Ideal investor description")
    chart_url: str = Field(description="External performance chart URL")
    performances: list[FundPerformanceOut] = Field(description="Historical performance")
    created_at: datetime = Field(description="Fund creation timestamp")

    @staticmethod
    def resolve_performances(obj):  # noqa: ANN001, ANN205
        return obj.performances.all()


class ProjectionDataPoint(Schema):
    year: int = Field(description="Projection year (1-based)")
    value: Decimal = Field(description="Projected portfolio value at year end")
    contributions: Decimal = Field(description="Cumulative contributions")
    earnings: Decimal = Field(description="Cumulative earnings")


class ProjectionOut(Schema):
    data_points: list[ProjectionDataPoint] = Field(description="Year-by-year projection")
    total_contributions: Decimal = Field(description="Sum of all contributions")
    total_earnings: Decimal = Field(description="Sum of all projected earnings")
    final_value: Decimal = Field(description="Projected final portfolio value")
