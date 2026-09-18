"""Build clean master document templates for the official Piplad documents.

Performance note: this is a ONE-TIME import step, NOT part of runtime
rendering. The spec forbids runtime average-color rectangle erasing
(``_blank_region()``); instead the placeholders / stock QR / stock photo are
removed ONCE up front here and the resulting PNGs are committed under
``backend/media/certificate_templates/clean/``. At render time only dynamic
data is drawn.

Erasing uses OpenCV inpainting when available and falls back to a PIL
blur-fill otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from app.template_coordinates import (  # noqa: E402
    CLEAN_CERTIFICATE_TEMPLATES,
    CLEAN_VOLUNTEER_CARD,
    SOURCE_CERTIFICATE_TEMPLATES,
    SOURCE_VOLUNTEER_CARD,
    erase_boxes,
    volunteer_front_erase_boxes,
)

MEDIA = BACKEND / "media"


def _border_average(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """Average colour of the ring just outside ``box`` (feeds the fill)."""
    left, top, right, bottom = (int(v) for v in box)
    offset = 6
    samples = []
    w, h = image.size
    xs = [max(0, left - offset), right + offset, (left + right) // 2]
    ys = [max(0, top - offset), bottom + offset]
    for x in xs:
        if (right + offset) >= w:
            continue
        for y in ys:
            if (bottom + offset) >= h:
                continue
            if 0 <= x < w and 0 <= y < h:
                samples.append(image.getpixel((x, y))[:3])
    if not samples:
        return (255, 255, 255)
    n = len(samples)
    return tuple(sum(p[i] for p in samples) // n for i in range(3))


def _inpaint_cv2(path: Path, boxes, out: Path) -> bool:
    try:
        import cv2
        import numpy as np
    except ImportError:
        return False

    img = cv2.imread(str(path))
    if img is None:
        return False
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for box in boxes:
        x1, y1, x2, y2 = (int(v) for v in box)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    inpainted = cv2.inpaint(img, mask, inpaintRadius=6, flags=cv2.INPAINT_TELEA)
    cv2.imwrite(str(out), inpainted)
    return True


def _erase_pil(image: Image.Image, box: tuple[int, int, int, int], feather: int = 8) -> None:
    """Erase a region with a feathered, border-coloured blur fill."""
    left, top, right, bottom = (int(v) for v in box)
    fill = _border_average(image, box)
    draw = ImageDraw.Draw(image)
    draw.rectangle([left, top, right, bottom], fill=fill)

    margin = feather
    crop_l = max(0, left - margin)
    crop_t = max(0, top - margin)
    crop_r = min(image.width, right + margin)
    crop_b = min(image.height, bottom + margin)
    if crop_r <= crop_l or crop_b <= crop_t:
        return
    region = image.crop((crop_l, crop_t, crop_r, crop_b)).filter(
        ImageFilter.GaussianBlur(radius=feather / 2)
    )
    image.paste(region, (crop_l, crop_t))


def clean_certificate(document_type: str) -> Path:
    src = MEDIA / SOURCE_CERTIFICATE_TEMPLATES[document_type]
    out = MEDIA / CLEAN_CERTIFICATE_TEMPLATES[document_type]
    out.parent.mkdir(parents=True, exist_ok=True)
    boxes = erase_boxes(document_type)
    if not _inpaint_cv2(src, boxes, out):
        image = Image.open(src).convert("RGB")
        for box in boxes:
            _erase_pil(image, box)
        image.save(out, format="PNG")
    print(f"clean-cert [{document_type}] -> {out.relative_to(BACKEND)}")
    return out


def clean_volunteer_card() -> Path:
    src = MEDIA / SOURCE_VOLUNTEER_CARD
    out = MEDIA / CLEAN_VOLUNTEER_CARD
    out.parent.mkdir(parents=True, exist_ok=True)
    boxes = volunteer_front_erase_boxes()
    if not _inpaint_cv2(src, boxes, out):
        image = Image.open(src).convert("RGB")
        for box in boxes:
            _erase_pil(image, box)
        image.save(out, format="PNG")
    print(f"clean-volunteer -> {out.relative_to(BACKEND)}")
    return out


def main() -> None:
    for doc_type in SOURCE_CERTIFICATE_TEMPLATES:
        clean_certificate(doc_type)
    clean_volunteer_card()
    print("Done.")


if __name__ == "__main__":
    main()