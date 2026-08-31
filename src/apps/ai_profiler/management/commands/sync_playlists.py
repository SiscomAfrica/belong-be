from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.ai_profiler.services.sync_playlist import sync_all_playlists


class Command(BaseCommand):
    help = "Rebuild every profile playlist from its selection criteria."

    def handle(self, *args, **options) -> None:
        results = sync_all_playlists()

        for slug, placed in sorted(results.items()):
            if placed:
                self.stdout.write(f"  {slug}: {placed} fund(s)")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  {slug}: no eligible funds — left unchanged"),
                )

        total = sum(results.values())
        self.stdout.write(
            self.style.SUCCESS(f"Synced {len(results)} playlist(s), {total} placement(s)."),
        )
