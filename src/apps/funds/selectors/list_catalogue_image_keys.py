from __future__ import annotations

from itertools import chain

from apps.funds.models import Fund, FundHolding, Playlist


def list_catalogue_image_keys() -> list[str]:
    """Every stored object key for catalogue art, deduplicated.

    Absolute URLs are skipped — seed rows point at external hosts we do not own
    and cannot resize. Generated variants are skipped so a re-run does not
    recurse into its own output.
    """
    stored = chain(
        Fund.objects.exclude(hero_image_url="").values_list("hero_image_url", flat=True),
        Playlist.objects.exclude(hero_image_url="").values_list(
            "hero_image_url", flat=True,
        ),
        FundHolding.objects.exclude(logo_url="").values_list("logo_url", flat=True),
    )

    return sorted(
        {
            key
            for key in stored
            if key and not key.startswith("http") and "__" not in key.rsplit("/", 1)[-1]
        },
    )
