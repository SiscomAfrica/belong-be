from __future__ import annotations

from apps.ai_profiler.rubric import (
    CATEGORICAL_VALUES,
    ORDINAL_ANCHORS,
    ORDINAL_KEYS,
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
        return (
            f"Anchors for {behaviour} — write one option per anchor you use, "
            f"and tag it with that number:\n{lines}"
        )

    values = CATEGORICAL_VALUES.get(behaviour, {})
    lines = "\n".join(f"  {key} = {text}" for key, text in values.items())
    return (
        f"Categories for {behaviour} — write one option per category you use, "
        f"and tag it with that key:\n{lines}"
    )


def _avoid_block(*, asked: list[dict]) -> str:
    previous = [question.get("question", "") for question in asked]
    previous = [text for text in previous if text]
    if not previous:
        return ""

    lines = "\n".join(f"  - {text}" for text in previous)
    return (
        "Already asked in this session — use a clearly different framing "
        f"and different wording:\n{lines}"
    )
