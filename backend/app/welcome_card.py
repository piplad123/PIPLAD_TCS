"""Volunteer ID helpers (QR PNG + profile photo loading) used by admin tooling."""

import logging
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)

ORG_NAME = "Piplad Welfare Foundation"

PROFILE_IMAGE_MIME = "image/jpeg"
MAX_EMAIL_PHOTO_BYTES = 2 * 1024 * 1024


def build_volunteer_id(volunteer_id: str) -> str:
    if volunteer_id:
        return volunteer_id
    return "PWF-VOL-STANDBY"


def build_volunteer_qr_png(
    volunteer_id: str,
    scale: int = 6,
    border: int = 2,
) -> bytes | None:
    """Return PNG bytes of the volunteer-ID QR code, or None if generation fails."""
    try:
        import io

        import segno

        qr = segno.make(
            build_volunteer_id(volunteer_id or ""),
            error="m",
            micro=False,
        )
        buffer = io.BytesIO()
        qr.save(buffer, kind="png", scale=scale, border=border)
        return buffer.getvalue()
    except Exception as exc:
        logger.error("Failed to generate volunteer QR code: %s", exc)
        return None


def load_profile_photo(profile_pic_url: str):
    """Return (content_bytes, mime) for a volunteer profile picture.

    Supports Cloudinary/http(s) URLs and local /media/ paths. Returns
    (None, None) if the image cannot be loaded or is not a valid image;
    the card then falls back to an initials avatar. Failures are logged.
    """
    if not profile_pic_url:
        return None, None

    try:
        mime = None
        if profile_pic_url.startswith(("/media/", "media/", "./", ".")):
            relative = profile_pic_url.removeprefix("/media/")
            candidate = Path(__file__).resolve().parents[1] / "media" / relative
            if not candidate.is_file():
                logger.warning("Profile photo not found on disk: %s", profile_pic_url)
                return None, None
            if candidate.stat().st_size > MAX_EMAIL_PHOTO_BYTES:
                logger.warning("Profile photo too large to email: %s", profile_pic_url)
                return None, None
            mime = mimetypes.guess_type(candidate.name)[0] or PROFILE_IMAGE_MIME
            data = candidate.read_bytes()
        else:
            import requests

            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=1)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            response = session.get(
                profile_pic_url,
                timeout=(3.05, 5),
                headers={"User-Agent": "Piplad-Welcome-Card/1.0", "Accept": "image/*"},
            )
            response.raise_for_status()
            if len(response.content) > MAX_EMAIL_PHOTO_BYTES:
                logger.warning("Profile photo too large to email: %s", profile_pic_url)
                return None, None
            mime = (
                (response.headers.get("Content-Type") or PROFILE_IMAGE_MIME)
                .split(";")[0]
                .strip()
                or PROFILE_IMAGE_MIME
            )
            data = response.content

        if not mime.lower().startswith("image/"):
            logger.warning("Profile photo has non-image MIME %r: %s", mime, profile_pic_url)
            return None, None
        return data, mime
    except Exception as exc:
        logger.warning("Could not load profile photo %s: %s", profile_pic_url, exc)
        return None, None