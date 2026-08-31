from __future__ import annotations

from apps.ai_profiler.rubric import (
    CATEGORICAL_KEYS,
    ORDINAL_KEYS,
    is_valid_level,
    is_valid_value,
)
from apps.ai_profiler.services.banned_copy import copy_problems
from apps.ai_profiler.services.question_schema import MAX_LABEL, MAX_SUBLABEL


def values_for(*, behaviour: str, options: list[dict]) -> list[str]:
    """Every anchor value recorded against `behaviour` across the options."""
    return [
        anchor["value"]
        for option in options
        for anchor in option.get("anchors", [])
        if anchor.get("behaviour") == behaviour
    ]


def check_copy(*, question: dict, options: list[dict]) -> list[str]:
    """Length and compliance problems in the user-visible strings."""
    problems: list[str] = []

    for field in ("question", "subtitle"):
        problems += [
            f"{field}: {problem}"
            for problem in copy_problems(text=question.get(field, ""))
        ]

    for index, option in enumerate(options):
        label = option.get("label", "")
        sublabel = option.get("sublabel", "")
        if len(label) > MAX_LABEL:
            problems.append(f"option {index}: label exceeds {MAX_LABEL} chars")
        if len(sublabel) > MAX_SUBLABEL:
            problems.append(f"option {index}: sublabel exceeds {MAX_SUBLABEL} chars")
        problems += [
            f"option {index}: {problem}"
            for problem in copy_problems(text=f"{label} {sublabel}")
        ]

    return problems


def check_anchors(*, options: list[dict]) -> list[str]:
    """Every anchor must name a behaviour we measure and a value we defined."""
    problems: list[str] = []

    for index, option in enumerate(options):
        for anchor in option.get("anchors", []):
            behaviour = anchor.get("behaviour")
            raw = anchor.get("value")

            if behaviour in ORDINAL_KEYS:
                if not _is_defined_level(behaviour=behaviour, raw=raw):
                    problems.append(
                        f"option {index}: {raw!r} is not a {behaviour} anchor",
                    )
            elif behaviour in CATEGORICAL_KEYS:
                if not is_valid_value(behaviour=behaviour, value=str(raw)):
                    problems.append(
                        f"option {index}: {raw!r} is not a {behaviour} value",
                    )
            else:
                problems.append(f"option {index}: unknown behaviour {behaviour!r}")

    return problems


def _is_defined_level(*, behaviour: str, raw: object) -> bool:
    text = str(raw).lstrip("-")
    if not text.isdigit():
        return False
    return is_valid_level(behaviour=behaviour, level=int(str(raw)))
