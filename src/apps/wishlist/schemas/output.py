from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class WishlistFundOut(Schema):
    id: UUID = Field(description="Fund identifier")
    name: str = Field(description="Fund display name")
    slug: str = Field(description="URL-safe fund slug")
    currency: str = Field(description="Fund denomination currency")
    hero_image_url: str = Field(description="Card hero image URL")
    risk_level: int = Field(description="Risk level 1-5")
    projected_annual_return: Decimal = Field(description="Projected annual return percentage")
    is_trending: bool = Field(description="Whether fund is currently trending")


class WishlistItemOut(Schema):
    id: UUID = Field(description="Wishlist item identifier")
    fund: WishlistFundOut = Field(description="Wishlisted fund details")
    created_at: datetime = Field(description="When the item was added to the wishlist")


class WishlistListOut(Schema):
    items: list[WishlistItemOut] = Field(description="List of wishlist items")
    count: int = Field(description="Total number of items in wishlist")
