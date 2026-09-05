from __future__ import annotations

import hashlib


def hash_otp_code(code: str) -> str:
    """Digest an OTP for storage and comparison. Codes are never held in clear."""
    return hashlib.sha256(code.encode()).hexdigest()
