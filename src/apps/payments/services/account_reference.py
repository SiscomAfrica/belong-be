from __future__ import annotations

import secrets

# Ratiba caps AccountReference at 12 alphanumeric characters, and it is what a
# customer sees on their M-PESA statement. Digits and uppercase letters only,
# minus the pairs that get misread when someone reads one back over the phone
# to support: O/0 and I/1.
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_PREFIX = "BL"
_BODY_LENGTH = 10


def generate_account_reference() -> str:
    """Return an unused 12-character Ratiba AccountReference."""
    from apps.payments.models import StandingOrder

    # 32^10 is a large enough space that a collision is a curiosity rather than
    # a risk, but the column is unique and a clash would surface as a 500 at
    # standing-order creation, so it is checked rather than assumed.
    for _ in range(5):
        body = "".join(secrets.choice(_ALPHABET) for _ in range(_BODY_LENGTH))
        reference = f"{_PREFIX}{body}"
        if not StandingOrder.objects.filter(account_reference=reference).exists():
            return reference

    msg = "Could not generate a unique Ratiba account reference."
    raise RuntimeError(msg)
