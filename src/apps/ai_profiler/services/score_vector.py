from __future__ import annotations

from collections import defaultdict

from apps.ai_profiler.rubric import (
    CATEGORICAL_KEYS,
    ORDINAL_KEYS,
    SCALE_MAX,
    SCALE_MIN,
)

# A signal is one behavioural reading taken from one selected option. It names
# the behaviour, the anchor value the option represents, and a weight: 1.0 when
# the question led on that behaviour, 0.5 when it was a secondary read.
#
# Nothing about the question's wording reaches this function. That is precisely
# what makes two differently-worded sessions grade identically.

PRIMARY_WEIGHT = 1.0
SECONDARY_WEIGHT = 0.5


def score_vector(*, signals: list[dict]) -> dict[str, int | str | None]:
    """Collapse behavioural signals into one fixed-shape vector.

    Ordinal behaviours resolve to a weighted mean, rounded and clamped to the
    scale. Categorical behaviours resolve to the highest-weighted value, with
    ties broken by first appearance so the result is order-stable.
    Behaviours with no signal resolve to None for the caller to impute.
    """
    ordinal: dict[str, list[tuple[float, int]]] = defaultdict(list)
    categorical: dict[str, dict[str, float]] = defaultdict(dict)
    first_seen: dict[str, list[str]] = defaultdict(list)

    for signal in signals:
        behaviour = signal["behaviour"]
        value = signal["value"]
        weight = float(signal.get("weight", PRIMARY_WEIGHT))

        if behaviour in ORDINAL_KEYS:
            ordinal[behaviour].append((weight, int(value)))
        elif behaviour in CATEGORICAL_KEYS:
            bucket = categorical[behaviour]
            bucket[value] = bucket.get(value, 0.0) + weight
            if value not in first_seen[behaviour]:
                first_seen[behaviour].append(value)

    vector: dict[str, int | str | None] = {}

    for key in ORDINAL_KEYS:
        vector[key] = _resolve_ordinal(ordinal.get(key, []))

    for key in CATEGORICAL_KEYS:
        vector[key] = _resolve_categorical(
            categorical.get(key, {}), first_seen.get(key, []),
        )

    return vector


def _resolve_ordinal(readings: list[tuple[float, int]]) -> int | None:
    if not readings:
        return None
    total_weight = sum(weight for weight, _ in readings)
    if total_weight <= 0:
        return None
    weighted = sum(weight * level for weight, level in readings) / total_weight
    return max(SCALE_MIN, min(SCALE_MAX, round(weighted)))


def _resolve_categorical(
    tallies: dict[str, float], order: list[str],
) -> str | None:
    if not tallies:
        return None
    best = max(tallies.values())
    winners = [value for value, weight in tallies.items() if weight == best]
    if len(winners) == 1:
        return winners[0]
    return next(value for value in order if value in winners)
