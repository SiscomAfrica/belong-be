from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class ProviderInitResult:
    external_ref: str
    merchant_request_id: str = ""
    authorization_url: str = ""
    raw_response: dict = field(default_factory=dict)


@dataclass
class ProviderCallbackResult:
    external_ref: str
    success: bool
    amount: Decimal = Decimal("0")
    failure_reason: str = ""
    raw_data: dict = field(default_factory=dict)


class BasePaymentProvider(ABC):
    @abstractmethod
    def initiate_payment(
        self, *, amount: Decimal, phone_number: str, reference: str,
    ) -> ProviderInitResult:
        ...

    @abstractmethod
    def verify_callback(self, *, payload: dict) -> ProviderCallbackResult:
        ...
