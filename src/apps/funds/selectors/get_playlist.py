from __future__ import annotations

from uuid import UUID

from django.db.models import Q

from apps.common.exceptions import NotFoundError
from apps.funds.models import Playlist


def get_playlist(*, playlist_id: str) -> Playlist:
    """Look up a playlist by UUID or slug."""
    try:
        uuid_val = UUID(playlist_id)
        lookup = Q(pk=uuid_val)
    except ValueError:
        lookup = Q(slug=playlist_id)

    try:
        return (
            Playlist.objects.prefetch_related("playlist_funds__fund")
            .get(lookup)
        )
    except Playlist.DoesNotExist:
        raise NotFoundError("Playlist not found")
