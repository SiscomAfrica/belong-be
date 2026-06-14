from __future__ import annotations

from uuid import UUID

from apps.common.exceptions import NotFoundError
from apps.funds.models import Playlist


def get_playlist(*, playlist_id: UUID) -> Playlist:
    try:
        return (
            Playlist.objects.prefetch_related("playlist_funds__fund")
            .get(pk=playlist_id)
        )
    except Playlist.DoesNotExist:
        raise NotFoundError("Playlist not found")
