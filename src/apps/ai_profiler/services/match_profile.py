from __future__ import annotations

from apps.ai_profiler.rubric import MEDIAN_LEVEL, ORDINAL_KEYS, WEIGHTS


def match_profile(
    *, vector: dict, profiles: list[dict], weights: dict[str, float] | None = None,
) -> dict:
    """Pick the profile whose centroid sits closest to the user's vector.

    Pure: no database, no clock, no request. Given the same vector and the same
    profile table it returns the same profile, which is the whole basis of the
    guarantee that two users with matching behaviours are graded identically
    however differently their questions were worded.

    Ties break toward the lower-risk centroid, so ambiguity always resolves in
    the more cautious direction.
    """
    if not profiles:
        msg = "match_profile requires at least one profile"
        raise ValueError(msg)

    scale = weights or WEIGHTS

    return min(
        profiles,
        key=lambda profile: (
            weighted_distance(
                vector=vector, centroid=profile["centroid"], weights=scale,
            ),
            profile["centroid"].get("risk", MEDIAN_LEVEL),
            profile["investor_type"],
        ),
    )


def weighted_distance(
    *, vector: dict, centroid: dict, weights: dict[str, float],
) -> float:
    """Weighted Manhattan distance across the ordinal behaviours only.

    Categorical behaviours are deliberately excluded — they have no ordering,
    so a numeric distance across them would be meaningless. They influence
    playlist theme, not which profile a user lands in.
    """
    total = 0.0
    for key in ORDINAL_KEYS:
        level = vector.get(key)
        if level is None:
            level = MEDIAN_LEVEL
        total += weights.get(key, 1.0) * abs(int(level) - int(centroid[key]))
    return total
