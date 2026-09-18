"""Calibration preview for the official document layouts.

Draws every field anchor as a labelled bounding box directly on the
registered template image so positions can be tuned visually by editing
``app/document_layouts.py`` (the single source of truth), then re-running::

    .venv\\Scripts\\python.exe scripts\\calibrate_templates.py

Preview JPEGs are written to ``backend/previews/`` and a mean-luminance
report is printed so fields placed over dark ornamentation are easy to spot.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from app.document_layouts import (  # noqa: E402
    CERTIFICATE_IMAGES,
    DOCUMENT_LAYOUTS,
    VOLUNTEER_CARD_IMAGE,
)
from app.document_service import MEDIA_DIR  # noqa: E402

SAMPLE_TEXT = {
    "name": "ANANYA SHARMA",
    "program_name": "Software Development Internship",
    "certificate_number": "CERT-2026-000001",
    "organisation_name": "Piplad Welfare Foundation",
    "competition_date": "10 August 2026",
    "competition_location": "Patna, Bihar",
    "starting_date": "01 June 2026",
    "end_date": "31 August 2026",
    "issue_date": "14 September 2026",
    "valid_till": "14 September 2028",
    "volunteer_id": "PWF-VOL-0001",
    "location": "Patna, Bihar",
}

ACCENT = (220, 38, 38)
LABEL = (255, 255, 255)
OK = (34, 197, 94)


def _font(size: int):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _region_stats(img: Image.Image, box) -> tuple[float, bool]:
    l, t, r, b = [max(0, int(v)) for v in box]
    l, t = min(l, img.width - 1), min(t, img.height - 1)
    r, b = min(r, img.width), min(b, img.height)
    region = img.crop((l, t, r, b))
    pixels = list(region.getdata())
    if not pixels:
        return 0.0, False
    mean = sum(pixels) / len(pixels)
    return mean, mean < 140


def _box_for(anchor: dict, text: str or None) -> list[int] | None:
    if not isinstance(anchor, dict):
        return None
    if "size" in anchor and "font_size" not in anchor:
        size = int(anchor.get("size", 150) or 50)
        return [anchor["x"] - size / 2, anchor["y"] - size / 2,
                anchor["x"] + size / 2, anchor["y"] + size / 2]
    if "font_size" not in anchor:
        return None
    fs = int(anchor.get("font_size", 24) or 24)
    text = text or "XXXX"
    anchor_mode = anchor.get("anchor", "mm")
    width = min(int(anchor.get("max_width", 600) or 600),
                max(80, int(fs * len(text) * 0.58)))
    height = int(fs * 1.55)
    x, y = int(anchor["x"]), int(anchor["y"])
    if anchor_mode == "rm":
        left, right = x - width, x
    elif anchor_mode == "lm":
        left, right = x, x + width
    else:
        left, right = x - width / 2, x + width / 2
    return [left, y - height / 2, right, y + height / 2]


def _annotate(image_path: Path, layout: dict, out_path: Path) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    gray = image.convert("L")
    report = []
    for key, anchor in layout.items():
        if not isinstance(anchor, dict):
            continue
        text = SAMPLE_TEXT.get(key)
        box = _box_for(anchor, text)
        if not box:
            continue
        mean, dark = _region_stats(gray, box)
        draw.rectangle(box, outline=ACCENT, width=3)
        draw.rectangle(box, outline=OK if not dark else ACCENT, width=1)
        label = f"{key} ({round(mean)})"
        lfont = _font(18)
        tb = draw.textbbox((0, 0), label, font=lfont)
        lw, lh = tb[2] - tb[0], tb[3] - tb[1]
        lx, ly = max(0, int(box[0] - 2)), max(0, int(box[1]) - lh - 8)
        draw.rectangle((lx, ly, lx + lw + 6, ly + lh + 4), fill=ACCENT)
        draw.text((lx + 3, ly + 2), label, font=lfont, fill=LABEL)
        report.append((key, round(mean, 1), "dark" if dark else "ok"))

    image.save(out_path, format="JPEG", quality=92)
    return report


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "previews"
    out_dir.mkdir(parents=True, exist_ok=True)

    for doc_type, image in CERTIFICATE_IMAGES.items():
        report = _annotate(
            MEDIA_DIR / image,
            DOCUMENT_LAYOUTS[doc_type],
            out_dir / f"preview-{doc_type}.jpg",
        )
        print(f"\n{doc_type}: {' | '.join(f'{k}={v}{"*" if d=="dark" else ""}' for k, v, d in report)}")

    report = _annotate(
        MEDIA_DIR / VOLUNTEER_CARD_IMAGE,
        DOCUMENT_LAYOUTS["volunteer"],
        out_dir / "preview-volunteer.jpg",
    )
    print(f"\nvolunteer: {' | '.join(f'{k}={v}{"*" if d=="dark" else ""}' for k, v, d in report)}")
    print(f"\nPreviews written to {out_dir}")


if __name__ == "__main__":
    main()