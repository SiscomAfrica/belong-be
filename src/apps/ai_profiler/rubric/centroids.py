from __future__ import annotations

from typing import Final

# Each profile is a point in ordinal-behaviour space. Matching is nearest
# weighted centroid, so retuning a profile or adding a new one is a change to
# this table rather than a change to any branching logic.
#
# These seed the `centroid` column on ProfileTemplate; the matcher reads
# whatever the database holds, so this is a default, not the source of truth.

CENTROIDS: Final[dict[str, dict[str, int]]] = {
    "CONSERVATIVE": {"risk": 1, "horizon": 2, "involvement": 1, "mindset": 1},
    "MODERATE": {"risk": 2, "horizon": 3, "involvement": 2, "mindset": 3},
    "INTERMEDIATE": {"risk": 3, "horizon": 4, "involvement": 3, "mindset": 3},
    "AGGRESSIVE": {"risk": 4, "horizon": 4, "involvement": 3, "mindset": 4},
    "HIGH_RISK": {"risk": 5, "horizon": 5, "involvement": 4, "mindset": 5},
}

# Risk dominates because it is the axis where being wrong causes actual harm.
# Involvement is a preference, not a suitability constraint, so it barely moves
# the result on its own.
WEIGHTS: Final[dict[str, float]] = {
    "risk": 3.0,
    "horizon": 2.0,
    "mindset": 2.0,
    "involvement": 1.0,
}

# Used when a behaviour is still uncovered after the maximum question count.
# Recorded on the profile as imputed so the recommendation stays auditable.
MEDIAN_LEVEL: Final[int] = 3
