from __future__ import annotations

from apps.ai_profiler.rubric.categorical import (
    CATEGORICAL_KEYS,
    CATEGORICAL_VALUES,
    is_valid_value,
)
from apps.ai_profiler.rubric.centroids import CENTROIDS, MEDIAN_LEVEL, WEIGHTS
from apps.ai_profiler.rubric.ordinal import (
    ORDINAL_ANCHORS,
    ORDINAL_KEYS,
    SCALE_MAX,
    SCALE_MIN,
    is_valid_level,
)

# The six behaviours the profiler measures, in presentation order.
BEHAVIOUR_KEYS: tuple[str, ...] = (
    "motivation",
    "risk",
    "horizon",
    "involvement",
    "market",
    "mindset",
)

__all__ = [
    "BEHAVIOUR_KEYS",
    "CATEGORICAL_KEYS",
    "CATEGORICAL_VALUES",
    "CENTROIDS",
    "MEDIAN_LEVEL",
    "ORDINAL_ANCHORS",
    "ORDINAL_KEYS",
    "SCALE_MAX",
    "SCALE_MIN",
    "WEIGHTS",
    "is_valid_level",
    "is_valid_value",
]
