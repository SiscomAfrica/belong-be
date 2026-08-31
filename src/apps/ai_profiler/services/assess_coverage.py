from __future__ import annotations

from collections import defaultdict

from apps.ai_profiler.rubric import BEHAVIOUR_KEYS
from apps.ai_profiler.services.score_vector import PRIMARY_WEIGHT

# A behaviour counts as understood once it has been read directly, or read
# indirectly enough times to be worth trusting. This is what lets question
# count vary between users without the grading varying with it: the vector
# always has six slots, only the route to filling them differs.

MIN_PRIMARY = 1
MIN_SECONDARY = 2


def assess_coverage(*, signals: list[dict]) -> dict[str, bool]:
    """Report which behaviours have been measured well enough to rely on."""
    primary: dict[str, int] = defaultdict(int)
    secondary: dict[str, int] = defaultdict(int)

    for signal in signals:
        behaviour = signal["behaviour"]
        if float(signal.get("weight", PRIMARY_WEIGHT)) >= PRIMARY_WEIGHT:
            primary[behaviour] += 1
        else:
            secondary[behaviour] += 1

    return {
        key: primary[key] >= MIN_PRIMARY or secondary[key] >= MIN_SECONDARY
        for key in BEHAVIOUR_KEYS
    }


def uncovered_behaviours(*, signals: list[dict]) -> list[str]:
    """Behaviours still unmeasured, in presentation order."""
    coverage = assess_coverage(signals=signals)
    return [key for key in BEHAVIOUR_KEYS if not coverage[key]]


def next_behaviour_to_probe(*, signals: list[dict]) -> str | None:
    """The behaviour a follow-up question should target, if any."""
    remaining = uncovered_behaviours(signals=signals)
    return remaining[0] if remaining else None
