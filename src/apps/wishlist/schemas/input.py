from __future__ import annotations

from uuid import UUID

from ninja import Schema


class WishlistAddIn(Schema):
    fund_id: UUID
