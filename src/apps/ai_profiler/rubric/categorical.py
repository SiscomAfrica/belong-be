from __future__ import annotations

from typing import Final

# Categorical behaviours have no ordering — "retirement" is not more or less
# than "home ownership". They never enter the distance calculation that picks a
# profile; they shape playlist theme and the explanation copy shown to the user.

MOTIVATION: Final[dict[str, str]] = {
    "FREEDOM": "Wants financial independence and optionality.",
    "WEALTH": "Wants to build long-term wealth.",
    "SECURITY": "Wants a safety net and protection from shocks.",
    "INCOME": "Wants investments that pay out regularly.",
    "MILESTONE": "Saving toward a specific purchase or life event.",
}

MARKET: Final[dict[str, str]] = {
    "DIVERSIFIED": "Prefers broad, all-in-one exposure.",
    "GLOBAL": "Prefers exposure beyond a single country.",
    "TECH": "Drawn to technology and AI.",
    "DIVIDEND": "Drawn to income-producing holdings.",
    "DEFENSIVE": "Drawn to capital preservation and lower volatility.",
}

CATEGORICAL_VALUES: Final[dict[str, dict[str, str]]] = {
    "motivation": MOTIVATION,
    "market": MARKET,
}

CATEGORICAL_KEYS: Final[tuple[str, ...]] = tuple(CATEGORICAL_VALUES)


def is_valid_value(*, behaviour: str, value: str) -> bool:
    """True when `value` is a defined category for a categorical behaviour."""
    values = CATEGORICAL_VALUES.get(behaviour)
    return values is not None and value in values
