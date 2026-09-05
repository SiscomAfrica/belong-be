from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.common.services.image_variants import VARIANT_WIDTHS
from apps.common.tasks import generate_image_variants
from apps.funds.selectors.list_catalogue_image_keys import list_catalogue_image_keys


class Command(BaseCommand):
    """Generate the resized variants for catalogue art uploaded before this existed.

    The app requests a variant by key, so an image with none serves a 404. Every
    image already in the catalogue predates the generator and needs one pass.
    Safe to re-run: variants are overwritten in place.
    """

    help = "Generate resized WebP variants for all existing catalogue images."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Run inline instead of queueing, so failures surface here.",
        )

    def handle(self, *args, **options) -> None:
        keys = list_catalogue_image_keys()
        if not keys:
            self.stdout.write("No catalogue images found.")
            return

        widths = ", ".join(str(w) for w in VARIANT_WIDTHS.values())
        self.stdout.write(f"{len(keys)} image(s) -> widths {widths}")

        failed = 0
        for key in keys:
            if options["sync"]:
                try:
                    generate_image_variants(key)
                except Exception as exc:
                    failed += 1
                    self.stderr.write(self.style.ERROR(f"  {key}: {exc}"))
                    continue
            else:
                generate_image_variants.delay(key)
            self.stdout.write(f"  {key}")

        verb = "generated" if options["sync"] else "queued"
        self.stdout.write(self.style.SUCCESS(f"{len(keys) - failed} {verb}."))
        if failed:
            self.stderr.write(self.style.ERROR(f"{failed} failed."))
