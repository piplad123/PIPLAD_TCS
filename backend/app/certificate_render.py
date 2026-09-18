"""Generic certificate renderer backed by an admin-managed template image.

A ``CertificateTemplate`` row stores the background image URL plus a JSON
``layout``. Each text field (name / date / topic) is an anchor with:

    x, y, font_size, max_width, color, box

where ``box`` is an optional (left, top, right, bottom) pixel rectangle that
is blanked out (filled with the sampled surrounding background) before the
real text is stamped. Official Piplad documents use pre-cleaned master
templates and therefore ship layouts WITHOUT ``box`` - nothing is erased at
render time, only dynamic data is drawn.
"""

import io
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/georgiab.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
]

# Bundled font (license-clean) used as a guaranteed fallback on any host.
_BUNDLED_FONT = str(Path(__file__).resolve().parent / "assets" / "DejaVuSans.ttf")

_FONT_CACHE = {}


def _load_font(size: int, path: str | None = None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    cache_key = (size, path)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    candidates = [path] if path else _FONT_CANDIDATES
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            try:
                font = ImageFont.truetype(candidate, size)
                _FONT_CACHE[cache_key] = font
                return font
            except Exception:
                continue
    if _BUNDLED_FONT and Path(_BUNDLED_FONT).is_file():
        try:
            font = ImageFont.truetype(_BUNDLED_FONT, size)
            _FONT_CACHE[cache_key] = font
            return font
        except Exception:
            pass
    try:
        font = ImageFont.load_default(size=size)
    except TypeError:
        font = ImageFont.load_default()
    _FONT_CACHE[cache_key] = font
    return font


def _clean(value) -> str:
    return str(value or "").replace("\n", " ").strip()


def _blank_region(image: Image.Image, box) -> None:
    if not box:
        return
    left, top, right, bottom = [int(x) for x in box]
    sample_coords = [
        (left - 5, top - 5), (right + 5, top - 5),
        (left - 5, bottom + 5), (right + 5, bottom + 5),
        ((left + right) // 2, top - 8), ((left + right) // 2, bottom + 8),
    ]
    r_sum = g_sum = b_sum = 0
    count = 0
    w, h = image.size
    for sx, sy in sample_coords:
        if 0 <= sx < w and 0 <= sy < h:
            pr, pg, pb = image.getpixel((sx, sy))[:3]
            r_sum += pr
            g_sum += pg
            b_sum += pb
            count += 1
    if count == 0:
        avg = (255, 255, 255)
    else:
        avg = (r_sum // count, g_sum // count, b_sum // count)
    ImageDraw.Draw(image).rectangle(box, fill=avg)


def _hex_color(value) -> tuple[int, int, int]:
    text = _clean(value)
    try:
        text = text.lstrip("#")
        if len(text) == 6:
            return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))
        if len(text) == 3:
            return tuple(int(c * 2, 16) for c in text)
    except (TypeError, ValueError):
        pass
    return (31, 41, 55)


def _draw_anchor(
    draw: ImageDraw.ImageDraw,
    anchor,
    text: str,
) -> None:
    if not anchor or not text:
        return
    x = float(anchor.get("x", 0))
    y = float(anchor.get("y", 0))
    size = int(anchor.get("font_size", 24) or 24)
    color = _hex_color(anchor.get("color"))
    max_width = int(anchor.get("max_width", 800) or 800)
    anchor_name = str(anchor.get("anchor") or "mm")
    font_path = anchor.get("font_path")

    font = _load_font(size, font_path)
    while size > 10 and draw.textlength(text, font=font) > max_width:
        size -= 1
        font = _load_font(size, font_path)
    draw.text((x, y), text, font=font, fill=color, anchor=anchor_name)


def load_background_image(image_url: str | None) -> Image.Image:
    """Load a template image from a local /media path or an http(s) URL."""
    if not image_url:
        raise FileNotFoundError("Certificate template has no background image.")

    if image_url.startswith(("/media/", "media/")):
        relative = image_url.removeprefix("/media/")
        candidate = Path(__file__).resolve().parents[1] / "media" / relative
        if not candidate.is_file():
            raise FileNotFoundError(f"Template image not found on disk: {image_url}")
        return Image.open(candidate).convert("RGB")

    if image_url.startswith(("http://", "https://", "res.cloudinary.com/")):
        import requests

        url = image_url if "://" in image_url else f"https://{image_url}"
        response = requests.get(url, timeout=(3.05, 15))
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")

    if Path(image_url).is_file():
        return Image.open(image_url).convert("RGB")

    raise FileNotFoundError(f"Template image could not be loaded: {image_url}")


def normalize_layout(layout) -> dict:
    """Accept a raw dict or list-of-dicts layout and return the dict form."""
    if not layout:
        return {}
    if hasattr(layout, "model_dump"):
        layout = layout.model_dump()
    return dict(layout)


def _anchor_w_h(anchor) -> tuple[int, int]:
    size = anchor.get("size", None)
    if isinstance(size, (list, tuple)) and len(size) >= 2:
        return int(size[0]), int(size[1])
    square = int(size or anchor.get("size", 150) or 100)
    return square, square


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def _overlay_png(image: Image.Image, png_bytes, anchor, kind: str = "generic") -> None:
    """Paste a PNG (QR / photo / logo) onto the image at the given anchor.

    Photos (``kind="photo"``) are cover-cropped inside their box to avoid
    distortion and may be rounded. QRs (``kind="qr"``) are stamped with
    nearest-neighbour resampling so the modules stay crisp.
    """
    if not anchor or not png_bytes:
        return
    x = float(anchor.get("x", 0))
    y = float(anchor.get("y", 0))
    anchor_name = str(anchor.get("anchor") or "mm")
    width, height = _anchor_w_h(anchor)

    overlay = Image.open(io.BytesIO(png_bytes)).convert("RGB")

    if kind == "photo":
        src_w, src_h = overlay.size
        target_ratio = width / height
        src_ratio = src_w / src_h
        if src_ratio > target_ratio:
            crop_w = int(src_h * target_ratio)
            crop_h = src_h
            left = (src_w - crop_w) // 2
            top = 0
        else:
            crop_w = src_w
            crop_h = int(src_w / target_ratio)
            left = 0
            top = (src_h - crop_h) // 2
        overlay = overlay.crop((left, top, left + crop_w, top + crop_h))
        overlay = overlay.resize((width, height), Image.Resampling.LANCZOS)
        if str(anchor.get("shape") or "").startswith("rounded"):
            radius = int(anchor.get("radius") or min(width, height) * 14 // 100)
            overlay.putalpha(_rounded_mask((width, height), radius))
    elif kind == "qr":
        overlay = overlay.resize((width, height), Image.Resampling.NEAREST)
    else:
        overlay = overlay.resize((width, height), Image.Resampling.LANCZOS)

    left, top = {"mm": (x - width / 2, y - height / 2)}.get(
        anchor_name, (x - width / 2, y - height / 2)
    )
    if overlay.mode == "RGBA":
        image.paste(overlay, (int(round(left)), int(round(top))), overlay)
    else:
        image.paste(overlay, (int(round(left)), int(round(top))))

    return None


def _overlay_qr(image: Image.Image, qr_data: str, anchor) -> None:
    """Generate and paste a dynamic QR onto the image."""
    from .qrcode_util import build_qr_png

    if not qr_data:
        return
    png = build_qr_png(qr_data)
    if png is None:
        return
    _overlay_png(image, png, anchor, kind="qr")


def build_certificate_image(
    *,
    image_url: str | None,
    layout=None,
    recipient_name: str = "",
    event_topic: str = "",
    event_date=None,
    fields: dict | None = None,
    qr_data: str | None = None,
    qr_anchor=None,
    overlay_pngs: list[tuple[bytes, dict]] | None = None,
) -> bytes:
    """Render dynamic fields + optional QR code onto a template image.

    ``fields`` maps layout keys (name, program_name, dates, certificate
    number, ...) to their display strings. Legacy ``recipient_name`` /
    ``event_topic`` / ``event_date`` behave exactly as before and are drawn
    through the ``name`` / ``topic`` / ``program_name`` and the available
    date anchors.

    ``qr_data`` + ``qr_anchor`` (or ``layout["qr"]``) stamp a verification
    QR into the document. ``overlay_pngs`` pastes arbitrary PNGs (e.g. the
    volunteer photo) at their given anchor dicts.
    """
    layout = normalize_layout(layout)
    image = load_background_image(image_url)

    # Blank every field box before drawing so pre-printed placeholders are
    # cleared (legacy Admin-mangemented templates only; official Piplad
    # documents render onto pre-cleaned masters and carry no boxes).
    for key, anchor in layout.items():
        if not isinstance(anchor, dict):
            continue
        box = anchor.get("box")
        if box:
            _blank_region(image, box)

    draw = ImageDraw.Draw(image)
    fields = dict(fields or {})

    name = _clean(recipient_name or fields.pop("name", "") or "")
    name_anchor = layout.get("name")
    if name_anchor and name:
        _draw_anchor(draw, name_anchor, name)

    topic = _clean(event_topic or fields.pop("topic", "") or "")
    topic_anchor = layout.get("topic") or layout.get("program_name")
    if topic_anchor and topic and not fields.get("program_name"):
        _draw_anchor(draw, topic_anchor, topic)

    date_text = _clean(event_date) or ""
    date_anchors = [
        layout.get("date"),
        layout.get("competition_date"),
        layout.get("starting_date"),
        layout.get("end_date"),
    ]
    if date_text and not fields.get("competition_date") and not fields.get("starting_date"):
        for date_anchor in date_anchors:
            if isinstance(date_anchor, dict):
                _draw_anchor(draw, date_anchor, date_text)

    for key, value in fields.items():
        if value in (None, ""):
            continue
        anchor = layout.get(key)
        if not isinstance(anchor, dict):
            continue
        _draw_anchor(draw, anchor, _clean(value))

    qr_anchor = qr_anchor or layout.get("qr")
    if qr_data:
        _overlay_qr(image, qr_data, qr_anchor)

    for png_bytes, anchor in overlay_pngs or []:
        kind = "photo" if (isinstance(anchor, dict) and anchor.get("role") == "photo") else "generic"
        _overlay_png(image, png_bytes, anchor, kind=kind)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()