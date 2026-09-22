from __future__ import annotations

from django.db import models


class EmploymentStatus(models.TextChoices):
    """How the client earns. Informed by ILO ICSE-18 but deliberately not it:
    the standard's categories ("contributing family workers", "members of
    producers' cooperatives") are built for labour statistics and would be
    unanswerable in an onboarding form.
    """

    EMPLOYED = "EMPLOYED", "Employed"
    SELF_EMPLOYED = "SELF_EMPLOYED", "Self employed"
    BUSINESS_OWNER = "BUSINESS_OWNER", "Business owner"
    STUDENT = "STUDENT", "Student"
    RETIRED = "RETIRED", "Retired"
    UNEMPLOYED = "UNEMPLOYED", "Unemployed"


class IncomeSource(models.TextChoices):
    """Where the money being invested came from.

    There is no ISO or FATF-published enumeration for source of funds. This is
    the de-facto set that AML programmes converge on, and it is what POCAMLA
    source-of-funds enquiries are answered against in practice — treat it as a
    convention we have adopted, not a standard we are conforming to.
    """

    SALARY = "SALARY", "Salary or wages"
    BUSINESS = "BUSINESS", "Business income"
    INVESTMENTS = "INVESTMENTS", "Investment returns"
    PENSION = "PENSION", "Pension or retirement income"
    RENTAL = "RENTAL", "Rental income"
    INHERITANCE = "INHERITANCE", "Inheritance"
    GIFT = "GIFT", "Gift"
    ASSET_SALE = "ASSET_SALE", "Sale of property or an asset"
    SAVINGS = "SAVINGS", "Accumulated savings"
    OTHER = "OTHER", "Other"
