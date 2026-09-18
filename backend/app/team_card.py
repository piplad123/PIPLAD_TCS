"""Render the Piplad team member ID card as a JPEG image.

The card is drawn entirely with Pillow so the QR code and the member's
profile photo are baked into the pixels and display everywhere.
"""

import io
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# ============================================================
# Card geometry (720 x 1180 px portrait)
# ============================================================
CARD_W = 720
CARD_H = 1180

HEADER_H = 150
PHOTO_DIAM = 130
PHOTO_RING = 6
PHOTO_CENTER_Y = 215

DETAILS_TOP = 392
DETAILS_HEIGHT = 372
ROW_HEIGHT = 62

QR_SIZE = 200
QR_TOP = 790
QR_CENTER_X = CARD_W // 2

FOOTER_TOP = 1110
MARGIN_X = 70

# Palette (mirrors the site + existing welcome card)
SLATE = (15, 23, 42)
LIME_BADGE = (132, 204, 22)
LIME_BRIGHT = (163, 230, 53)
LIME_RING = (190, 242, 100)
INK = (15, 23, 42)
GREEN = (5, 150, 105)
SUBTLE = (100, 116, 139)
MUTED = (148, 163, 184)
BOX_BG = (248, 250, 252)
BOX_BORDER = (226, 232, 240)
FOOTER_TEXT = (203, 213, 225)
FOOTER_BOLD = (255, 255, 255)
AVATAR_BG = (247, 254, 231)
AVATAR_TEXT = (63, 98, 18)

_FONT_DIR = Path(__file__).resolve().parent / "assets"
_FONT_CANDIDATES = [
    (_FONT_DIR / "DejaVuSans-Bold.ttf", (_FONT_DIR / "DejaVuSans.ttf")),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"),
    ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"),
    ("C:/Windows/Fonts/calibrib.ttf", "C:/Windows/Fonts/calibri.ttf"),
]

_FONT_CACHE = {}


def _load_pair(size: int) -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
    key = ("pair", size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    bold_font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    regular_font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    for bold_path, regular_path in _FONT_CANDIDATES:
        bold_path, regular_path = Path(bold_path), Path(regular_path)
        if bold_path.is_file() and regular_path.is_file():
            try:
                bold_font = ImageFont.truetype(str(bold_path), size)
                regular_font = ImageFont.truetype(str(regular_path), size)
                _FONT_CACHE[key] = (bold_font, regular_font)
                return bold_font, regular_font
            except Exception:
                continue
    try:
        regular_font = ImageFont.load_default(size=size)
    except TypeError:
        regular_font = ImageFont.load_default()
    bold_font = regular_font
    _FONT_CACHE[key] = (bold_font, regular_font)
    return bold_font, regular_font


def _clean(value) -> str:
    return str(value or "").replace("\n", " ").strip()


def _initials(full_name: str) -> str:
    parts = [p for p in _clean(full_name).split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _format_date(value) -> str:
    if not value:
        return "—"
    if isinstance(value, str):
        return value
    return value.strftime("%d %B %Y")


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_x: int,
    center_y: int,
    size: int,
    color,
    max_width: int,
    anchor: str = "mm",
) -> None:
    font = _load_pair(size)[0]
    while size > 14 and draw.textlength(text, font=font) > max_width:
        size -= 1
        font = _load_pair(size)[0]
    draw.text((center_x, center_y), text, font=font, fill=color, anchor=anchor)


def _photo_layer(
    photo_bytes: bytes | None,
    full_name: str,
) -> Image.Image:
    layer = Image.new("RGBA", (PHOTO_DIAM, PHOTO_DIAM), (0, 0, 0, 0))
    ring_out = PHOTO_DIAM // 2
    ring_in = ring_out - PHOTO_RING
    ImageDraw.Draw(layer).ellipse((0, 0, PHOTO_DIAM - 1, PHOTO_DIAM - 1), fill=LIME_RING)

    inner_d = ring_in * 2
    ox = (PHOTO_DIAM - inner_d) // 2

    if photo_bytes:
        try:
            photo = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
            w, h = photo.size
            side = min(w, h)
            photo = photo.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
            photo = photo.resize((inner_d, inner_d), Image.LANCZOS)
            inner_mask = Image.new("L", (inner_d, inner_d), 0)
            ImageDraw.Draw(inner_mask).ellipse((0, 0, inner_d - 1, inner_d - 1), fill=255)
            inner = Image.new("RGBA", (inner_d, inner_d), (0, 0, 0, 0))
            inner.paste(photo, (0, 0), inner_mask)
            layer.alpha_composite(inner, (ox, ox))
        except Exception as exc:
            logger.warning("Could not embed profile photo, using initials avatar: %s", exc)
            _draw_initials_avatar(layer, full_name)
    else:
        _draw_initials_avatar(layer, full_name)
    return layer


def _draw_initials_avatar(layer: Image.Image, full_name: str) -> None:
    draw = ImageDraw.Draw(layer)
    draw.ellipse(
        (PHOTO_RING, PHOTO_RING, PHOTO_DIAM - 1 - PHOTO_RING, PHOTO_DIAM - 1 - PHOTO_RING),
        fill=AVATAR_BG,
    )
    bold, _ = _load_pair(58)
    initials = _initials(full_name)
    draw.text((PHOTO_DIAM / 2, PHOTO_DIAM / 2), initials, font=bold, fill=AVATAR_TEXT, anchor="mm")


def build_team_card_jpg(
    *,
    full_name: str,
    member_id: str = "",
    role: str = "",
    team: str = "",
    joined_date=None,
    photo_bytes: bytes | None = None,
    qr_png: bytes | None = None,
) -> bytes:
    """Render the team member ID card and return JPEG bytes."""
    image = Image.new("RGB", (CARD_W, CARD_H), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Header band
    draw.rectangle((0, 0, CARD_W, HEADER_H), fill=SLATE)
    badge_w, badge_h = 232, 30
    badge_box = ((CARD_W - badge_w) // 2, 32, (CARD_W + badge_w) // 2, 32 + badge_h)
    draw.rounded_rectangle(badge_box, radius=15, fill=LIME_BADGE)
    badge_font = _load_pair(11)[0]
    badge_text = "PIPLAD WELFARE FOUNDATION"
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    draw.text(
        ((CARD_W - (bbox[2] - bbox[0])) / 2 - bbox[0], 32 + (badge_h - (bbox[3] - bbox[1])) / 2 - bbox[1]),
        badge_text,
        font=badge_font,
        fill=(255, 255, 255),
    )
    _draw_centered(
        draw,
        "TEAM MEMBER ID CARD",
        CARD_W // 2,
        104,
        13,
        LIME_BRIGHT,
        CARD_W - 2 * MARGIN_X,
    )

    # Profile photo / avatar
    photo_layer = _photo_layer(photo_bytes, full_name)
    image.paste(
        photo_layer,
        ((CARD_W - PHOTO_DIAM) // 2, PHOTO_CENTER_Y - PHOTO_DIAM // 2),
        photo_layer,
    )

    name = _clean(full_name) or "Team Member"
    _draw_centered(draw, name, CARD_W // 2, 306, 30, INK, CARD_W - 2 * MARGIN_X)

    # Details box
    box_left, box_right = MARGIN_X, CARD_W - MARGIN_X
    box_bottom = DETAILS_TOP + DETAILS_HEIGHT
    draw.rounded_rectangle(
        (box_left, DETAILS_TOP, box_right, box_bottom),
        radius=14,
        fill=BOX_BG,
        outline=BOX_BORDER,
        width=2,
    )
    rows = [
        ("Member ID", _clean(member_id) or "PWF-MEMBER"),
        ("Role", _clean(role) or "—"),
        ("Team", _clean(team) or "General"),
        ("Joined", _format_date(joined_date)),
    ]
    row_top = DETAILS_TOP + 6
    for idx, (label, value) in enumerate(rows):
        y = row_top + idx * ROW_HEIGHT
        label_font = _load_pair(11)[0]
        value_font = _load_pair(17)[0]
        draw.text((box_left + 20, y + 8), label.upper(), font=label_font, fill=MUTED)
        value_color = GREEN if label == "Member ID" else INK
        draw.text((box_left + 20, y + 26), value, font=value_font, fill=value_color)
        if idx < len(rows) - 1:
            draw.line(
                (box_left + 20, y + ROW_HEIGHT - 1, box_right - 20, y + ROW_HEIGHT - 1),
                fill=BOX_BORDER,
                width=1,
            )

    # QR block
    if qr_png:
        try:
            qr = Image.open(io.BytesIO(qr_png)).convert("L")
            qr = qr.resize((QR_SIZE, QR_SIZE), Image.NEAREST).convert("RGB")
            image.paste(qr, ((CARD_W - QR_SIZE) // 2, QR_TOP))
        except Exception as exc:
            logger.warning("Failed to embed QR in card: %s", exc)
        _draw_centered(
            draw,
            f"Scan to verify: {_clean(member_id) or 'PWF-MEMBER'}",
            QR_CENTER_X,
            QR_TOP + QR_SIZE + 18,
            16,
            INK,
            CARD_W - 2 * MARGIN_X,
        )

    # Footer band
    draw.rectangle((0, FOOTER_TOP, CARD_W, CARD_H), fill=SLATE)
    footer_regular = _load_pair(13)[1]
    footer_text = "Proudly serving your community."
    bbox = draw.textbbox((0, 0), footer_text, font=footer_regular)
    draw.text(
        ((CARD_W - (bbox[2] - bbox[0])) / 2 - bbox[0], FOOTER_TOP + 22 - bbox[1]),
        footer_text,
        font=footer_regular,
        fill=FOOTER_TEXT,
    )
    _draw_centered(
        draw,
        "CREATING OPPORTUNITIES, CREATING LIVES",
        CARD_W // 2,
        FOOTER_TOP + 48,
        15,
        FOOTER_BOLD,
        CARD_W - 2 * MARGIN_X,
    )

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=92)
    return buffer.getvalue()