from __future__ import annotations

import logging

from django.db import transaction

from apps.ai_profiler.models import ProfileTemplate
from apps.ai_profiler.services.select_funds import band_covers, select_funds
from apps.funds.models import Fund, PlaylistFund

logger = logging.getLogger(__name__)

RETURNS_LABEL = "YTD returns"


def sync_playlist(*, template: ProfileTemplate) -> int:
    """Rebuild one profile's playlist from its criteria. Returns funds placed.

    The playlist is a cache of a query, not a curated list. Rebuilding is how a
    newly added fund reaches the profiles it qualifies for without anyone
    editing a fixture — and how a profile becomes structurally incapable of
    holding a fund outside its risk band.
    """
    if template.playlist is None:
        logger.warning("Template %s has no playlist to sync", template.slug)
        return 0

    funds = list(Fund.objects.filter(is_active=True))

    if not band_covers(funds=funds, risk_band=template.risk_band):
        logger.error(
            "No active fund matches risk band %s for %s — playlist left unchanged",
            template.risk_band, template.slug,
        )
        return 0

    chosen = select_funds(
        funds=funds,
        risk_band=template.risk_band,
        category_weights=template.category_weights or {},
        max_funds=template.max_funds,
    )

    with transaction.atomic():
        PlaylistFund.objects.filter(playlist=template.playlist).delete()
        PlaylistFund.objects.bulk_create([
            PlaylistFund(
                playlist=template.playlist,
                fund=fund,
                position=position,
                returns_label=RETURNS_LABEL,
            )
            for position, fund in enumerate(chosen)
        ])

    return len(chosen)


def sync_all_playlists() -> dict[str, int]:
    """Rebuild every active profile's playlist. Safe to run repeatedly."""
    templates = ProfileTemplate.objects.filter(is_active=True).select_related("playlist")
    return {
        template.slug: sync_playlist(template=template)
        for template in templates
    }
