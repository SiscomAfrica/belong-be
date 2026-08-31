from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field


class QuestionOptionOut(Schema):
    label: str = Field(description="Option text shown to the user")
    sublabel: str = Field(description="Supporting line beneath the option")


class SessionQuestionOut(Schema):
    id: UUID = Field(description="Question identifier, used when answering")
    position: int = Field(description="1-indexed position in the session")
    total_expected: int = Field(description="Questions expected in total (4 or 5)")
    prompt: str = Field(description="The question text")
    subtitle: str = Field(description="Supporting line beneath the question")
    allows_multiple: bool = Field(description="Whether more than one option may be picked")
    selected_indexes: list[int] = Field(
        default_factory=list,
        description="Options already chosen, so a revisited question shows its answer",
    )
    has_previous: bool = Field(
        default=False, description="Whether the user can step back from here",
    )
    options: list[QuestionOptionOut] = Field(description="Options in display order")


class NextQuestionOut(Schema):
    question: SessionQuestionOut | None = Field(
        default=None, description="Next question, or null when scoring can begin",
    )
    complete: bool = Field(description="True when no further questions are needed")
