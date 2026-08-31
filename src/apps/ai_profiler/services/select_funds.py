from __future__ import annotations

from typing import Any, Protocol


class FundLike(Protocol):
    slug: str
    risk_level: int
    category: str


def select_funds(
    *,
    funds: list[Any],
    risk_band: list[int],
    category_weights: dict[str, float],
    max_funds: int,
) -> list[Any]:
    """Pick the funds a profile should be shown, from whatever the catalogue holds.

    Replaces the hand-curated profile-to-playlist join. Because membership is
    derived from criteria rather than a fixed list of slugs, a fund added to
    the catalogue flows into every profile it qualifies for without a fixture
    edit — and a profile can never be handed a fund outside its risk band.
    """
    if not risk_band:
        return []

    low, high = risk_band[0], risk_band[-1]
    eligible = [fund for fund in funds if low <= fund.risk_level <= high]

    ranked = sorted(
        eligible,
        key=lambda fund: (
            -category_weights.get(fund.category, 0.0),
            fund.risk_level,
            fund.slug,
        ),
    )
    return ranked[:max_funds]


def band_covers(*, funds: list[Any], risk_band: list[int]) -> bool:
    """Whether the catalogue can currently serve this profile at all.

    An empty result means a user completes onboarding and is shown nothing,
    so callers should treat a False here as a configuration problem rather
    than an empty state to render.
    """
    if not risk_band:
        return False
    low, high = risk_band[0], risk_band[-1]
    return any(low <= fund.risk_level <= high for fund in funds)
