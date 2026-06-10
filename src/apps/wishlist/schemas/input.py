from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field


class WishlistAddIn(Schema):
    fund_id: UUID = Field(description="UUID of the fund to add to wishlist")
