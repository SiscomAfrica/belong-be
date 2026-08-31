from __future__ import annotations

import re
from typing import Final

# This copy reaches users unreviewed, inside a regulated suitability
# assessment. A generated question may describe how an investment behaves;
# it may never promise an outcome, rank a product, or quote a number.

BANNED_PHRASES: Final[tuple[str, ...]] = (
    "risk-free",
    "risk free",
    "no risk",
    "zero risk",
    "guaranteed",
    "guarantee",
    "can't lose",
    "cannot lose",
    "safe bet",
    "sure thing",
    "will double",
    "get rich",
    "best fund",
    "top performing",
    "beat the market",
    "outperform",
)

# Any explicit return figure — "12%", "12.5 %", "+130%".
PERCENTAGE = re.compile(r"[-+]?\d+(?:\.\d+)?\s*%")

# Fund names must not appear in questions; recommendation happens after
# scoring, never inside it.
FUND_NAME_HINT = re.compile(
    r"\b(etf|fund|stock|share|bond|portfolio name)\b", re.IGNORECASE,
)


def copy_problems(*, text: str) -> list[str]:
    """Compliance problems in a single piece of generated copy."""
    lowered = text.lower()
    problems = [
        f"banned phrase {phrase!r}"
        for phrase in BANNED_PHRASES
        if phrase in lowered
    ]

    if PERCENTAGE.search(text):
        problems.append("contains an explicit return figure")

    return problems
