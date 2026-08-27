from __future__ import annotations

import datetime as dt

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.common.services.s3 import generate_presigned_download


class FundOut(Schema):
    id: UUID = Field(description="Fund identifier")
    name: str = Field(description="Fund display name")
    slug: str = Field(description="URL-safe fund slug")
    ticker_symbol: str = Field(description="ETF ticker symbol (e.g. DRAM, QQQ)")
    fund_type: str = Field(description="Fund type: ETF | FUND | ASSET")
    category: str = Field(description="Fund category for grouping")
    risk_level: int = Field(description="Risk level 1-5 (5 = highest)")
    risk_level_display: str = Field(description="Human-readable risk label")
    currency: str = Field(description="Fund denomination currency (ISO 4217)")
    minimum_investment: Decimal = Field(description="Minimum investment amount")
    projected_annual_return: Decimal = Field(description="Projected annual return %")
    emoji: str = Field(description="Display emoji for the fund")
    hero_image_url: str = Field(description="Card hero image URL")
    is_trending: bool = Field(description="Whether fund is currently trending")
    is_active: bool = Field(description="Whether fund accepts new investments")

    @staticmethod
    def resolve_risk_level_display(obj: object) -> str:
        return getattr(obj, "get_risk_level_display", lambda: "")()

    @staticmethod
    def resolve_hero_image_url(obj: object) -> str:
        image = getattr(obj, "hero_image", None)
        if image and getattr(image, "name", ""):
            return generate_presigned_download(file_key=image.name)["download_url"]
        key = getattr(obj, "hero_image_url", "")
        if not key or key.startswith("http"):
            return key or ""
        return generate_presigned_download(file_key=key)["download_url"]


class FundNAVOut(Schema):
    id: UUID = Field(description="NAV record identifier")
    date: dt.date = Field(description="NAV valuation date")
    nav_value: Decimal = Field(description="Net Asset Value per unit")
    daily_change_pct: Decimal = Field(description="Day-over-day NAV change %")


class FundPerformanceOut(Schema):
    id: UUID = Field(description="Performance record identifier")
    period: str = Field(description="Period label (e.g. 1M, 3M, 1Y, YTD)")
    return_pct: Decimal = Field(description="Return % for the period")
    start_value: Decimal = Field(description="NAV at period start")
    end_value: Decimal = Field(description="NAV at period end")
    calculated_at: datetime = Field(description="When this metric was computed")


class FundListOut(Schema):
    items: list[FundOut] = Field(description="List of funds")
    count: int = Field(description="Total number of matching funds")
