from __future__ import annotations

_RISK_KEYWORDS = {
    1: ["safe", "secure", "no risk", "conservative", "preserve"],
    2: ["low risk", "cautious", "steady", "stable"],
    3: ["moderate", "balanced", "some risk", "medium"],
    4: ["growth", "aggressive", "higher returns", "willing to risk"],
    5: ["high risk", "maximum", "volatile", "crypto", "speculative"],
}

_HORIZON_KEYWORDS = {
    "SHORT": ["short term", "few months", "less than a year", "quick"],
    "MEDIUM": ["medium term", "few years", "3-5 years", "mid-term"],
    "LONG": ["long term", "retirement", "10 years", "decades"],
}

_TYPE_MAP = {1: "CONSERVATIVE", 2: "CONSERVATIVE", 3: "MODERATE", 4: "AGGRESSIVE", 5: "HIGH_RISK"}


def score_investor_type(*, messages: list) -> dict:
    text = " ".join(m.content.lower() for m in messages).lower()

    risk = _score_risk(text)
    horizon = _score_horizon(text)
    goal = _extract_goal(text)
    interests = _extract_interests(text)
    investor_type = _TYPE_MAP.get(risk, "MODERATE")

    if risk >= 3 and horizon == "LONG":
        investor_type = "INTERMEDIATE"

    return {
        "risk_tolerance": risk,
        "time_horizon": horizon,
        "investment_goal": goal,
        "interests": interests,
        "investor_type": investor_type,
    }


def _score_risk(text: str) -> int:
    for level in (5, 4, 3, 2, 1):
        if any(kw in text for kw in _RISK_KEYWORDS[level]):
            return level
    return 3


def _score_horizon(text: str) -> str:
    for horizon, keywords in _HORIZON_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return horizon
    return "MEDIUM"


def _extract_goal(text: str) -> str:
    goals = ["retirement", "wealth", "savings", "education", "house", "emergency"]
    found = [g for g in goals if g in text]
    return ", ".join(found) if found else ""


def _extract_interests(text: str) -> list[str]:
    topics = ["tech", "real estate", "bonds", "crypto", "sustainability", "etf"]
    return [t for t in topics if t in text]
