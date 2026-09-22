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

# Product nouns must not appear in a question. Naming an instrument inside a
# suitability assessment is a recommendation made before the assessment has
# concluded — recommendation happens after scoring, never inside it.
#
# Deliberately narrow, because a false positive here is not harmless: a
# rejected question is retried and then falls back to the bank, so an
# over-broad pattern quietly costs every user the same six banked questions.
#
# Excluded on purpose:
#   "portfolio" — the customer's own holdings, not a product. "Your portfolio
#     drops sharply over a bad month" is the banked risk question.
#   bare "fund"  — the verb. "How would you fund this?" is ordinary English.
#   "security"   — collides with the SECURITY motivation anchor, which is
#     literally "wants a safety net".
FUND_NAME_HINT = re.compile(
    r"\b(etfs?|mutual funds?|index funds?|money market funds?|unit trusts?"
    r"|stocks?|shares|bonds?)\b",
    re.IGNORECASE,
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

    named = FUND_NAME_HINT.search(text)
    if named:
        problems.append(f"names a product type ({named.group(0)!r})")

    return problems
