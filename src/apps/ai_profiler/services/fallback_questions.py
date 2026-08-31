from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# The shipped question set, re-tagged against the rubric and held as data
# alongside the other seed fixtures. Served whenever generation fails, times
# out, or blows its budget.
#
# Because banked questions carry the same anchors as generated ones, a user who
# lands here is graded on exactly the same scale as everyone else. The fallback
# costs variety, never fairness.

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "fallback_questions.json"


@lru_cache(maxsize=1)
def _load() -> tuple[dict, ...]:
    data = json.loads(FIXTURE.read_text())
    return tuple(data["questions"])


def fallback_questions() -> list[dict]:
    """The full banked set, in presentation order."""
    return [dict(question) for question in _load()]


def fallback_for(*, behaviour: str) -> dict | None:
    """The banked question that leads on `behaviour`, if one exists."""
    for question in _load():
        if question["primary_behaviour"] == behaviour:
            return dict(question)
    return None
