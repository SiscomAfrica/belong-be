from __future__ import annotations

from apps.ai_profiler.rubric import (
    CATEGORICAL_VALUES,
    ORDINAL_ANCHORS,
    ORDINAL_KEYS,
)
from apps.ai_profiler.services.question_exemplar import style_exemplar
from apps.ai_profiler.services.question_style import (
    SUBTITLE_RULES,
    VOICE_RULES,
    anchor_guidance,
)


def build_generation_prompt(*, behaviour: str, asked: list[dict]) -> str:
    """The per-question instruction: what to measure, and what not to repeat.

    Prior questions are included only so the model varies its framing. It is
    never shown prior *answers* — the questions must not adapt their difficulty
    or slant to what the user has already said, or two users with the same
    behaviour could be measured on differently-calibrated ground.
    """
    return "\n\n".join(
        part
        for part in (
            f"Write one question that measures: {behaviour}.",
            _anchor_block(behaviour=behaviour),
            VOICE_RULES,
            SUBTITLE_RULES,
            style_exemplar(behaviour=behaviour),
            _avoid_block(asked=asked),
            "Return only the structured question.",
        )
        if part
    )


def _anchor_block(*, behaviour: str) -> str:
    if behaviour in ORDINAL_KEYS:
        lines = "\n".join(
            f"  {level} = {text}"
            for level, text in ORDINAL_ANCHORS[behaviour].items()
        )
    else:
        values = CATEGORICAL_VALUES.get(behaviour, {})
        lines = "\n".join(f"  {key} = {text}" for key, text in values.items())

    return anchor_guidance(behaviour=behaviour, lines=lines)


def _avoid_block(*, asked: list[dict]) -> str:
    previous = [question.get("question", "") for question in asked]
    previous = [text for text in previous if text]
    if not previous:
        return ""

    lines = "\n".join(f"  - {text}" for text in previous)
    return (
        "Already asked in this session. Do not reuse the situation, the "
        "sentence shape, or the opening words — a user should not feel they "
        "are answering the same question twice:\n"
        f"{lines}"
    )
