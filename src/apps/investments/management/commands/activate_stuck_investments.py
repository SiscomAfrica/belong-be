from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from apps.investments.models import Investment, InvestmentStatus
from apps.investments.services.activate_pending_investments import (
    activate_pending_investments,
)
from apps.kyc.models import KYCStatus, KYCSubmission


class Command(BaseCommand):
    help = (
        "Activate investments left in PENDING_KYC for members who are already "
        "verified. Repairs records stranded while admin approval skipped "
        "activation — paid-for investments that never confirmed."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List who would be affected without changing anything.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        verified = set(
            KYCSubmission.objects.filter(
                status=KYCStatus.VERIFIED,
            ).values_list("user_id", flat=True),
        )
        stranded = set(
            Investment.objects.filter(
                status=InvestmentStatus.PENDING_KYC,
                user_id__in=verified,
            ).values_list("user_id", flat=True),
        )

        if not stranded:
            self.stdout.write(self.style.SUCCESS("Nothing stranded."))
            return

        if options["dry_run"]:
            for user_id in sorted(stranded, key=str):
                count = Investment.objects.filter(
                    user_id=user_id, status=InvestmentStatus.PENDING_KYC,
                ).count()
                self.stdout.write(f"{user_id}: {count} investment(s)")
            self.stdout.write(
                self.style.WARNING(f"{len(stranded)} member(s) — dry run, nothing changed."),
            )
            return

        total = 0
        for user_id in stranded:
            # Reuses the same service the KYC decision calls, so a paid
            # investment confirms and an unpaid one drops back to PENDING —
            # exactly as it would have at the moment of approval.
            total += activate_pending_investments(user_id=user_id)

        self.stdout.write(
            self.style.SUCCESS(
                f"Activated {total} investment(s) across {len(stranded)} member(s).",
            ),
        )
