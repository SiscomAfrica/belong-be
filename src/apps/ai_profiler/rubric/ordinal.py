from __future__ import annotations

from typing import Final

# Ordinal behaviours are measured on a fixed 1-5 scale. The anchor text is the
# contract with the generator: it may write any wording it likes for an option,
# but it must declare which anchor that option represents. The scale itself is
# never generated, never inferred, and never varies between users.

SCALE_MIN: Final = 1
SCALE_MAX: Final = 5

RISK: Final[dict[int, str]] = {
    1: "Cannot tolerate loss of capital; would exit at the first drawdown.",
    2: "Tolerates small dips; prioritises stability over return.",
    3: "Accepts moderate swings in exchange for moderate growth.",
    4: "Comfortable with large swings in pursuit of higher returns.",
    5: "Actively seeks volatility; would add to a position during a drawdown.",
}

HORIZON: Final[dict[int, str]] = {
    1: "Needs the money within a year.",
    2: "Investing for roughly one to three years.",
    3: "Investing for roughly three to seven years.",
    4: "Investing for ten years or more.",
    5: "No fixed end date; building wealth across a generation.",
}

INVOLVEMENT: Final[dict[int, str]] = {
    1: "Wants to invest once and never think about it again.",
    2: "Happy to review occasionally; no interest in decisions.",
    3: "Checks in periodically and adjusts now and then.",
    4: "Follows markets closely and expects to act on what they see.",
    5: "Wants full control and frequent, hands-on decisions.",
}

MINDSET: Final[dict[int, str]] = {
    1: "Protecting the money already saved matters more than growing it.",
    2: "Leans toward protection, accepts modest growth.",
    3: "Balances protection and growth evenly.",
    4: "Leans toward growth, accepts meaningful downside.",
    5: "Maximising long-term return is the only objective that matters.",
}

ORDINAL_ANCHORS: Final[dict[str, dict[int, str]]] = {
    "risk": RISK,
    "horizon": HORIZON,
    "involvement": INVOLVEMENT,
    "mindset": MINDSET,
}

ORDINAL_KEYS: Final[tuple[str, ...]] = tuple(ORDINAL_ANCHORS)


def is_valid_level(*, behaviour: str, level: int) -> bool:
    """True when `level` is a defined anchor for an ordinal behaviour."""
    anchors = ORDINAL_ANCHORS.get(behaviour)
    return anchors is not None and level in anchors
