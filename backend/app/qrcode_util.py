"""QR code generation shared by certificates and volunteer ID cards.

Builds a single dynamic QR PNG per document via ``segno``. The encoded
payload is a public URL under PUBLIC_FRONTEND_URL so scanning the QR opens
the verification page (no hard-coded localhost URLs are ever embedded).
"""

import io
import logging
import os

logger = logging.getLogger(__name__)


def public_frontend_url() -> str:
    """Root URL used for QR payloads.

    Reads PUBLIC_FRONTEND_URL (production domain), falling back to the
    public site so verification links never point at a local dev server in
    production.
    """
    return (os.getenv("PUBLIC_FRONTEND_URL") or "https://pipladfoundation.in").rstrip("/")


def verify_url(kind: str, identifier: str) -> str:
    """Return the public verification URL for a certificate or volunteer.

    Certificates use the public short form ``/verify/{certificate_number}``;
    volunteer ID cards use ``/verify/volunteer/{volunteer_id}``.
    """
    if kind == "volunteer":
        return f"{public_frontend_url()}/verify/volunteer/{identifier}"
    return f"{public_frontend_url()}/verify/{identifier}"


def build_qr_png(
    data: str,
    scale: int = 8,
    border: int = 2,
    error: str = "m",
) -> bytes | None:
    """Return PNG bytes of a QR code for ``data``, or None if generation fails.

    The scale is tuned for embedding into certificates/cards (a generous
    module size keeps the printed scannable result crisp).
    """
    if not data:
        return None
    try:
        import segno

        qr = segno.make(data, error=error, micro=False)
        buffer = io.BytesIO()
        qr.save(buffer, kind="png", scale=scale, border=border)
        return buffer.getvalue()
    except Exception as exc:  # noqa: BLE001 - QR generation must never crash issuing
        logger.error("Failed to generate QR code: %s", exc)
        return None