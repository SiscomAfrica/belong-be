from __future__ import annotations

from django.db.models import QuerySet

from apps.funds.models import Playlist


def list_playlists() -> QuerySet[Playlist]:
    return (
        Playlist.objects.filter(is_active=True)
        .prefetch_related("playlist_funds__fund")
    )
