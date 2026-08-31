from __future__ import annotations

from apps.ai_profiler.rubric import ORDINAL_KEYS
from apps.ai_profiler.services.question_checks import (
    check_anchors,
    check_copy,
    values_for,
)
from apps.ai_profiler.services.question_schema import MAX_OPTIONS, MIN_OPTIONS

# An ordinal question must let a user reach both ends of the scale. Distinct
# anchors alone are not enough: three distinct integers always span three
# levels, so {2,3,4} would pass a naive span check while offering no way to
# say "not at all" or "very much" — the question would quietly compress
# everyone toward the middle.
LOW_ANCHOR_AT_MOST = 2
HIGH_ANCHOR_AT_LEAST = 4

MIN_PRIMARY_CATEGORIES = 3
MIN_SECONDARY_SPAN = 2


def validate_question(*, question: dict) -> list[str]:
    """Problems that make a generated question unusable. Empty means ship it.

    Generation is never trusted. A model that writes four options all meaning
    roughly the same thing produces a question that measures nothing, and the
    vector built from it would be silently worthless rather than obviously
    broken — which is the failure mode the old keyword scorer had.
    """
    primary = question.get("primary_behaviour")
    if not primary:
        return ["missing primary_behaviour"]

    options = question.get("options") or []
    problems: list[str] = []

    if not MIN_OPTIONS <= len(options) <= MAX_OPTIONS:
        problems.append(
            f"expected {MIN_OPTIONS}-{MAX_OPTIONS} options, got {len(options)}",
        )

    problems += check_copy(question=question, options=options)
    problems += check_anchors(options=options)
    problems += _check_span(primary=primary, options=options)
    problems += _check_secondary(question=question, options=options)

    return problems


def _check_span(*, primary: str, options: list[dict]) -> list[str]:
    """The primary behaviour must actually be discriminated by the options."""
    values = values_for(behaviour=primary, options=options)

    if len(values) != len(options):
        return [f"every option must carry a {primary} anchor"]
    if len(set(values)) != len(values):
        return [f"two options share the same {primary} anchor"]

    if primary in ORDINAL_KEYS:
        levels = [int(value) for value in values]
        if min(levels) > LOW_ANCHOR_AT_MOST or max(levels) < HIGH_ANCHOR_AT_LEAST:
            return [
                f"{primary} anchors must reach both ends of the scale "
                f"(one at {LOW_ANCHOR_AT_MOST} or below, one at "
                f"{HIGH_ANCHOR_AT_LEAST} or above)",
            ]
    elif len(set(values)) < MIN_PRIMARY_CATEGORIES:
        return [f"{primary} offers fewer than {MIN_PRIMARY_CATEGORIES} distinct values"]

    return []


def _check_secondary(*, question: dict, options: list[dict]) -> list[str]:
    """A claimed secondary read must be a real one, not a coverage freebie."""
    problems: list[str] = []

    for behaviour in question.get("secondary_behaviours") or []:
        distinct = set(values_for(behaviour=behaviour, options=options))
        if len(distinct) < MIN_SECONDARY_SPAN:
            problems.append(
                f"claims to read {behaviour} but offers "
                f"{len(distinct)} distinct value(s)",
            )

    return problems
