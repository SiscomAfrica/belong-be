from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class KYCInitResult:
    job_id: str
    upload_url: str = ""
    raw_response: dict = field(default_factory=dict)


@dataclass
class KYCCallbackResult:
    job_id: str
    success: bool
    result_code: str = ""
    result_text: str = ""
    raw_data: dict = field(default_factory=dict)


class BaseKYCProvider(ABC):
    @abstractmethod
    def submit_verification(
        self, *, partner_params: dict, images: list[dict],
    ) -> KYCInitResult:
        ...

    @abstractmethod
    def verify_callback(self, *, payload: dict) -> KYCCallbackResult:
        ...
