from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field


class FeedPostCreateIn(Schema):
    investment_id: UUID | None = Field(default=None, description="Optional investment to celebrate in this post")
    auto_text: str = Field(default="", max_length=280, description="Auto-generated post text (max 280 chars)")
    user_comment: str = Field(default="", max_length=500, description="User-written comment (max 500 chars)")
    is_public: bool = Field(default=True, description="Whether the post is visible to all users")


class FeedPostUpdateIn(Schema):
    user_comment: str | None = Field(default=None, max_length=500, description="Updated user comment")
    is_public: bool | None = Field(default=None, description="Updated visibility setting")
