from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ai_profiler.models import ProfileTemplate
from apps.funds.models import Fund, Playlist, PlaylistFund

DEFAULT_FILE = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "fixtures"
    / "profile_templates.json"
)


class Command(BaseCommand):
    help = "Seed playlists and profile templates from JSON fixture."

    def add_arguments(self, parser) -> None:  # noqa: ANN001
        parser.add_argument("--file", type=str, default=str(DEFAULT_FILE))

    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003
        path = Path(options["file"])
        data = json.loads(path.read_text())

        playlists = self._seed_playlists(data["playlists"])
        self._seed_profiles(data["profiles"], playlists)
        self.stdout.write(self.style.SUCCESS("Seeded profile templates."))

    def _seed_playlists(self, entries: list[dict]) -> dict[str, Playlist]:
        playlists: dict[str, Playlist] = {}

        for entry in entries:
            playlist, created = Playlist.objects.get_or_create(
                slug=entry["slug"],
                defaults={
                    "name": entry["name"],
                    "description": entry.get("description", ""),
                },
            )
            action = "Created" if created else "Exists"
            self.stdout.write(f"  Playlist {action}: {playlist.name}")
            playlists[entry["slug"]] = playlist

            for position, fund_entry in enumerate(entry.get("funds", [])):
                slug = fund_entry["slug"] if isinstance(fund_entry, dict) else fund_entry
                label = fund_entry.get("returns_label", "") if isinstance(fund_entry, dict) else ""
                fund = Fund.objects.filter(slug=slug).first()
                if not fund:
                    self.stdout.write(f"    Skip fund (not found): {slug}")
                    continue
                PlaylistFund.objects.get_or_create(
                    playlist=playlist,
                    fund=fund,
                    defaults={"position": position, "returns_label": label},
                )

        return playlists

    def _seed_profiles(
        self, entries: list[dict], playlists: dict[str, Playlist]
    ) -> None:
        for entry in entries:
            playlist = playlists.get(entry["playlist_slug"])
            template, created = ProfileTemplate.objects.get_or_create(
                slug=entry["slug"],
                defaults={
                    "investor_type": entry["investor_type"],
                    "name": entry["name"],
                    "accent": entry.get("accent", "investor."),
                    "badge_label": entry["badge_label"],
                    "description": entry["description"],
                    "playlist": playlist,
                    "position": entry.get("position", 0),
                },
            )
            action = "Created" if created else "Exists"
            self.stdout.write(f"  Template {action}: {template.name}")
