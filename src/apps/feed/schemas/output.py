from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class FeedUserOut(Schema):
    id: UUID = Field(description="User identifier")
    first_name: str = Field(description="User first name")
    last_name: str = Field(description="User last name")


class FeedInvestmentOut(Schema):
    id: UUID = Field(description="Investment identifier")
    fund_name: str = Field(description="Fund name associated with the investment")
    amount: Decimal = Field(description="Investment amount in KES")

    @staticmethod
    def resolve_fund_name(obj) -> str:  # noqa: ANN001
        return obj.fund.name if obj.fund else ""


class FeedPostOut(Schema):
    id: UUID = Field(description="Post identifier")
    user: FeedUserOut = Field(description="Post author")
    investment: FeedInvestmentOut | None = Field(default=None, description="Associated investment if any")
    auto_text: str = Field(description="Auto-generated post text")
    user_comment: str = Field(description="User-written comment")
    is_public: bool = Field(description="Whether visible to all users")
    likes_count: int = Field(description="Total number of likes")
    is_liked: bool = Field(description="Whether the requesting user liked this post")
    created_at: datetime = Field(description="Post creation timestamp")

    @staticmethod
    def resolve_is_liked(obj) -> bool:  # noqa: ANN001
        return getattr(obj, "is_liked", False)


class FeedListOut(Schema):
    items: list[FeedPostOut] = Field(description="List of feed posts")
    count: int = Field(description="Total number of matching posts")


class LikeToggleOut(Schema):
    liked: bool = Field(description="True if the post is now liked, false if unliked")
