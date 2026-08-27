from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.funds.models import Fund, FundHolding

COMPANY_DOMAINS: dict[str, str] = {
    "apple": "apple.com",
    "microsoft": "microsoft.com",
    "nvidia": "nvidia.com",
    "amazon": "amazon.com",
    "alphabet": "abc.xyz",
    "google": "google.com",
    "meta": "meta.com",
    "tesla": "tesla.com",
    "broadcom": "broadcom.com",
    "jpmorgan": "jpmorganchase.com",
    "berkshire": "berkshirehathaway.com",
    "unitedhealth": "unitedhealthgroup.com",
    "visa": "visa.com",
    "mastercard": "mastercard.com",
    "netflix": "netflix.com",
    "adobe": "adobe.com",
    "amd": "amd.com",
    "intel": "intel.com",
    "cisco": "cisco.com",
    "qualcomm": "qualcomm.com",
    "micron": "micron.com",
    "tsmc": "tsmc.com",
    "taiwan": "tsmc.com",
    "samsung": "samsung.com",
    "oracle": "oracle.com",
    "ibm": "ibm.com",
    "nike": "nike.com",
    "disney": "disney.com",
    "coca-cola": "coca-cola.com",
    "pepsi": "pepsico.com",
    "pepsico": "pepsico.com",
    "walmart": "walmart.com",
    "starbucks": "starbucks.com",
    "boeing": "boeing.com",
    "goldman sachs": "goldmansachs.com",
    "morgan stanley": "morganstanley.com",
    "spotify": "spotify.com",
    "uber": "uber.com",
    "airbnb": "airbnb.com",
    "shopify": "shopify.com",
    "palantir": "palantir.com",
}


def _resolve_domain(name: str) -> str:
    lower = name.lower().strip()
    if lower in COMPANY_DOMAINS:
        return COMPANY_DOMAINS[lower]
    for key, domain in COMPANY_DOMAINS.items():
        if key in lower or lower in key:
            return domain
    import re

    cleaned = re.sub(r"\b(inc|corp|ltd|group|holdings|co|plc)\b", "", lower)
    cleaned = re.sub(r"[^a-z0-9]", "", cleaned)
    return f"{cleaned}.com"


def _logo_url(name: str) -> str:
    domain = _resolve_domain(name)
    return (
        f"https://t0.gstatic.com/faviconV2?client=SOCIAL"
        f"&type=FAVICON&fallback_opts=TYPE,SIZE,URL"
        f"&url=http://{domain}&size=128"
    )


class Command(BaseCommand):
    help = "Seed FundHolding records from legacy top_holdings JSON."

    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003
        funds = Fund.objects.exclude(top_holdings=[])
        created_total = 0

        for fund in funds:
            names: list[str] = fund.top_holdings or []
            for position, name in enumerate(names):
                _, created = FundHolding.objects.get_or_create(
                    fund=fund,
                    name=name,
                    defaults={
                        "logo_url": _logo_url(name),
                        "position": position,
                    },
                )
                if created:
                    created_total += 1
                    self.stdout.write(f"  + {fund.name}: {name}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {created_total} holdings."),
        )
