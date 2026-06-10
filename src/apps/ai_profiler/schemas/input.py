from __future__ import annotations

from ninja import Schema
from pydantic import Field


class MessageIn(Schema):
    content: str = Field(description="User message text sent to the AI profiler")
