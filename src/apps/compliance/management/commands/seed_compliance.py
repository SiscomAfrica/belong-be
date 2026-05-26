from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.compliance.models import ConsentVersion, DocumentType, InvestmentLimit, KYCTier


class Command(BaseCommand):
    help = "Seed default investment limits and consent versions"

    def handle(self, *args, **options) -> None:
        self._seed_limits()
        self._seed_consents()
        self.stdout.write(self.style.SUCCESS("Compliance data seeded."))

    def _seed_limits(self) -> None:
        defaults = [
            (KYCTier.UNVERIFIED, Decimal("5000"), Decimal("10000")),
            (KYCTier.BASIC, Decimal("50000"), Decimal("200000")),
            (KYCTier.FULL, Decimal("500000"), Decimal("2000000")),
        ]
        for tier, txn, month in defaults:
            InvestmentLimit.objects.get_or_create(
                kyc_tier=tier,
                defaults={"max_per_transaction": txn, "max_per_month": month},
            )

    def _seed_consents(self) -> None:
        consents = [
            (DocumentType.TERMS, "1.0", "https://belong.co.ke/terms"),
            (DocumentType.PRIVACY, "1.0", "https://belong.co.ke/privacy"),
        ]
        for doc_type, version, url in consents:
            ConsentVersion.objects.get_or_create(
                document_type=doc_type,
                version=version,
                defaults={"effective_date": date(2026, 1, 1), "content_url": url},
            )
