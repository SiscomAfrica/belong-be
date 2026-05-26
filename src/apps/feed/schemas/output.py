from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class FeedUserOut(Schema):
    id: UUID
    first_name: str
    last_name: str


class FeedInvestmentOut(Schema):
    id: UUID
    fund_name: str
    amount: Decimal

    @staticmethod
    def resolve_fund_name(obj) -> str:  # noqa: ANN001
        return obj.fund.name if obj.fund else ""


class FeedPostOut(Schema):
    id: UUID
    user: FeedUserOut
    investment: FeedInvestmentOut | None
    auto_text: str
    user_comment: str
    is_public: bool
    likes_count: int
    is_liked: bool
    created_at: datetime

    @staticmethod
    def resolve_is_liked(obj) -> bool:  # noqa: ANN001
        return getattr(obj, "is_liked", False)


class FeedListOut(Schema):
    items: list[FeedPostOut]
    count: int


class LikeToggleOut(Schema):
    liked: bool
