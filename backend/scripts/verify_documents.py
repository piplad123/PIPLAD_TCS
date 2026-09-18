"""Smoke-render one of each official document and save them for inspection.

Useful after any coordinate / renderer change:
    python backend/scripts/verify_documents.py
Writes PNG/JPEG previews under backend/media/generated/_preview/.
"""

from __future__ import annotations

import io
import sys
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from PIL import Image  # noqa: E402

from app.document_service import (  # noqa: E402
    MEDIA_DIR,
    render_certificate_jpeg,
    render_volunteer_card_jpeg,
)

OUT = MEDIA_DIR / "generated" / "_preview"

_FIELDS = {
    "participation": dict(program_name="Shiksha Utsav 2026", competition_date="12 March 2026"),
    "appreciation": dict(program_name="Community Health Camp 2026"),
    "completion": dict(
        program_name="Sunshine School Outreach",
        organisation_name="Piplad Welfare Foundation",
        competition_date="5 April 2026",
        competition_location="Delhi",
    ),
    "internship": dict(
        program_name="Content & Design Intern",
        starting_date="1 February 2026",
        end_date="31 March 2026",
    ),
}


def _cert(number: str, doctype: str) -> SimpleNamespace:
    f = _FIELDS[doctype]
    return SimpleNamespace(
        certificate_type=doctype,
        first_name="Aarav",
        last_name="Sharma",
        recipient_name="Aarav Sharma",
        certificate_number=number,
        qr_verification_token="verify-token-" + number.split("-")[-1],
        **f,
    )


def _sample_photo() -> bytes:
    img = Image.new("RGB", (320, 320), (120, 160, 220))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def _volunteer() -> SimpleNamespace:
    return SimpleNamespace(
        profile_pic_url=None,
        full_name="Ananya Gupta",
        position="Community Volunteer",
        volunteer_id="VLR-2026-0042",
        interest_area="Education",
        location="Noida, UP",
        issue_date=date(2026, 2, 1),
        valid_till=date(2028, 1, 31),
        card_qr_token="volunteer-token-0042",
        id=42,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for i, doctype in enumerate(_FIELDS, start=1):
        cert = _cert(f"CERT-2026-0000{i}", doctype)
        data = render_certificate_jpeg(cert)
        path = OUT / f"{doctype}.jpg"
        path.write_bytes(data)
        with Image.open(path) as img:
            print(f"{path.name}: {img.size} ({path.stat().st_size} bytes)")

    app = _volunteer()
    data = render_volunteer_card_jpeg(app)
    path = OUT / "volunteer_no_photo.jpg"
    path.write_bytes(data)
    with Image.open(path) as img:
        print(f"{path.name}: {img.size} ({path.stat().st_size} bytes)")

    app.profile_pic_url = "data"  # forces nothing; photo bytes are injected below
    from app.certificate_render import build_certificate_image
    from app.document_layouts import layout_for
    from app.template_coordinates import CLEAN_VOLUNTEER_CARD

    photo = _sample_photo()
    from app.qrcode_util import verify_url

    rendered = build_certificate_image(
        image_url=str(MEDIA_DIR / CLEAN_VOLUNTEER_CARD),
        layout=layout_for("volunteer"),
        fields={
            "name": "Ananya Gupta",
            "position": "Community Volunteer",
            "volunteer_id": "VLR-2026-0042",
            "programme": "Education",
            "location": "Noida, UP",
            "valid_till": "31 January 2028",
        },
        qr_data=verify_url("volunteer", "volunteer-token-0042"),
        overlay_pngs=[(photo, layout_for("volunteer").get("photo"))],
    )
    path = OUT / "volunteer_with_photo.jpg"
    path.write_bytes(rendered)
    with Image.open(path) as img:
        print(f"{path.name}: {img.size} ({path.stat().st_size} bytes)")
    print("OK")


if __name__ == "__main__":
    main()