from __future__ import annotations

from apps.ai_profiler.models.investor_profile import TimeHorizon
from apps.ai_profiler.rubric import MEDIAN_LEVEL

# The legacy InvestorProfile.time_horizon is a three-way choice, while the
# rubric measures horizon on the same 1-5 scale as everything else. This maps
# between them so the existing field keeps working for API consumers.

SHORT_AT_MOST = 2
LONG_AT_LEAST = 4


def horizon_label(*, level: int | None) -> str:
    if level is None:
        level = MEDIAN_LEVEL
    if level <= SHORT_AT_MOST:
        return TimeHorizon.SHORT
    if level >= LONG_AT_LEAST:
        return TimeHorizon.LONG
    return TimeHorizon.MEDIUM


def summarise(*, investor_type: str, vector: dict) -> str:
    """One-line session summary, used as context if the user profiles again."""
    parts = [f"Type: {investor_type}"]
    for key in ("risk", "horizon", "involvement", "mindset"):
        value = vector.get(key)
        if value is not None:
            parts.append(f"{key}: {value}")
    for key in ("motivation", "market"):
        value = vector.get(key)
        if value:
            parts.append(f"{key}: {value}")
    return ", ".join(parts)
