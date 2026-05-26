from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field


class FeedPostCreateIn(Schema):
    investment_id: UUID | None = None
    auto_text: str = Field(default="", max_length=280)
    user_comment: str = Field(default="", max_length=500)
    is_public: bool = True


class FeedPostUpdateIn(Schema):
    user_comment: str | None = Field(default=None, max_length=500)
    is_public: bool | None = None
