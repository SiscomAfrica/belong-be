from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from apps.payments.services.register_c2b_urls import register_c2b_urls


class Command(BaseCommand):
    help = "Register the C2B confirmation and validation URLs with Safaricom."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--response-type",
            default="Completed",
            choices=["Completed", "Cancelled"],
            help="What Safaricom does when our validation URL is unreachable.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        result = register_c2b_urls(response_type=options["response_type"])
        self.stdout.write(self.style.SUCCESS(f"Registered: {result}"))
