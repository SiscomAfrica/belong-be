from __future__ import annotations

import pytest

from apps.common.services.s3 import get_s3_client
from apps.common.storage import PublicMediaStorage

# Headers that turn a PUT into an aws-chunked streaming upload with a trailing
# checksum. R2 does not implement trailer checksums and rejects the request.
TRAILER_HEADERS = frozenset(
    {"x-amz-trailer", "content-encoding", "transfer-encoding"},
)


def put_object_headers(client) -> dict[str, str]:
    """The headers botocore would put on the wire, captured before sending."""
    captured: dict[str, str] = {}

    def capture(request, **kwargs) -> None:
        captured.update(
            {
                k: v.decode() if isinstance(v, bytes) else str(v)
                for k, v in request.headers.items()
            },
        )
        raise _StopError

    client.meta.events.register("before-send.s3.PutObject", capture)
    try:
        client.put_object(
            Bucket="belong-media",
            Key="hero_images/funds/a__160.webp",
            Body=b"fake",
            ContentType="image/webp",
        )
    except _StopError:
        pass
    finally:
        client.meta.events.unregister("before-send.s3.PutObject", capture)

    return captured


class _StopError(Exception):
    """Abort the call once the request is built; nothing should reach R2."""


@pytest.fixture(params=["own", "django-storages"])
def client(request):
    """Both clients that write to R2 — they are built separately."""
    if request.param == "own":
        get_s3_client.cache_clear()
        return get_s3_client()
    return PublicMediaStorage().connection.meta.client


def test_uploads_carry_no_trailer_checksum(client) -> None:
    """boto3 1.36+ adds a CRC32 trailer by default and R2 rejects it.

    Without `request_checksum_calculation="when_required"` every direct upload
    fails — admin images and generated variants alike. This guards the setting
    against a boto3 upgrade quietly turning it back on.
    """
    headers = {k.lower(): v for k, v in put_object_headers(client).items()}

    offending = sorted(
        k for k in headers if "checksum" in k or k in TRAILER_HEADERS
    )

    assert not offending, f"R2-incompatible upload headers: {offending}"


def test_payload_is_signed_rather_than_streamed(client) -> None:
    headers = {k.lower(): v for k, v in put_object_headers(client).items()}

    assert "STREAMING" not in headers.get("x-amz-content-sha256", "")
