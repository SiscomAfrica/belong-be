from __future__ import annotations

from ninja import Schema
from pydantic import Field


class MessageIn(Schema):
    content: str = Field(description="User message text sent to the AI profiler")


class AnswerIn(Schema):
    selected_indexes: list[int] = Field(
        description="Indexes of the chosen options, as shown in the question",
        min_length=1,
    )
