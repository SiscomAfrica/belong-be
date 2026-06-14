from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.funds.schemas import PlaylistListOut, PlaylistOut
from apps.funds.selectors.get_playlist import get_playlist
from apps.funds.selectors.list_playlists import list_playlists

playlists_router = Router(tags=["playlists"], auth=None)


@playlists_router.get("/", response=PlaylistListOut)
def list_playlists_endpoint(request):
    """List all active playlists with their ordered funds."""
    qs = list_playlists()
    return PlaylistListOut(items=list(qs), count=qs.count())


@playlists_router.get("/{playlist_id}", response=PlaylistOut)
def get_playlist_endpoint(request, playlist_id: UUID):
    """Return a single playlist with its ordered funds."""
    return get_playlist(playlist_id=playlist_id)
