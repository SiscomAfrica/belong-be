from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class WishlistFundOut(Schema):
    id: UUID
    name: str
    slug: str
    currency: str
    hero_image_url: str
    risk_level: int
    projected_annual_return: Decimal
    is_trending: bool


class WishlistItemOut(Schema):
    id: UUID
    fund: WishlistFundOut
    created_at: datetime


class WishlistListOut(Schema):
    items: list[WishlistItemOut]
    count: int
