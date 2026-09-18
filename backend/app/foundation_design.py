"""Procedural design system for official Piplad Welfare Foundation documents.

A print-quality A4-landscape (3508 x 2480 px @ 300 dpi) renderer built on
Pillow. Every credential shares one visual identity (frame, masthead,
typography, seal, signature and QR verification block) while each document
type plugs in its own palette and wording.

The Certificate of Appreciation, Internship, Completion and Participation are
all implemented today. Each type plugs a new ``PALETTES["<type>"]`` entry plus
a ``_render_*_body()`` function into the same shared layout and dispatch code.
"""

import functools
import math
import threading
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ============================================================
# Canvas
# ============================================================
# The design coordinate space stays a print-accurate A4 landscape sheet
# (3508 x 2480 px @ 300 dpi) so every layout rule, tracking / wrap threshold
# and element position keeps behaving exactly as before.
CANVAS_W = 3508
CANVAS_H = 2480
CX = CANVAS_W // 2

# The rendered output is the low-memory clean-master resolution. All drawing
# is translated from the design space above onto this smaller canvas through
# :class:`ScaledDraw`, so the final JPEG drops from ~26 MB of pixel data to
# ~4.7 MB without changing the visible layout.
OUTPUT_W = 1536
OUTPUT_H = 1024

# Serialize certificate / ID-card rendering so a burst of admin actions never
# stacks multiple full renders in memory at once on the small Render worker.
_RENDER_LOCK = threading.RLock()

# ============================================================
# Brand palette
# ============================================================
GREEN_950 = "#0B3929"
GREEN_800 = "#0E5138"
GREEN_700 = "#116B46"
GOLD = "#C9A227"
GOLD_BRIGHT = "#D4A72C"
GOLD_LIGHT = "#E6C877"
GOLD_PALE = "#F2E2A8"
TEAL = "#176E75"
BLUE = "#1D5F8A"
SAGE = "#A4C3AF"
AMBER = "#D89B3E"
CHARCOAL = "#2B2B2B"
MUTED = "#5C5C5C"
IVORY = "#F7F1E3"
WHITE = "#FFFFFF"
# Full-page background: a soft mint-green wash behind all content.
PAGE_BG = "#EAF3EC"

PALETTES = {
    # Shared identity used across every credential type.
    "base": {
        "green_950": GREEN_950,
        "green_800": GREEN_800,
        "green_700": GREEN_700,
        "gold": GOLD,
        "gold_bright": GOLD_BRIGHT,
        "gold_light": GOLD_LIGHT,
        "gold_pale": GOLD_PALE,
        "charcoal": CHARCOAL,
        "muted": MUTED,
        "ivory": IVORY,
    },
    # Certificate of Appreciation: deep green + warm gold.
    "appreciation": {
        "primary": GREEN_800,
        "primary_deep": GREEN_950,
        "accent": TEAL,  # subtle teal accent line under the name
        "title_color": GREEN_800,
        "name_color": CHARCOAL,
        "program_color": TEAL,
        "motif_color": TEAL,
    },
    # Certificate of Internship: teal/blue primary accent, deep green
    # supporting headlines, warm gold premium touches. Same shared identity.
    "internship": {
        "primary": BLUE,
        "primary_deep": GREEN_950,
        "accent": TEAL,
        "title_color": GREEN_800,
        "name_color": CHARCOAL,
        "program_color": BLUE,
        "motif_color": TEAL,
    },
    # Certificate of Completion: deep green + warm gold on a warm ivory
    # sheet, with subtle teal accents for the achievement lines.
    "completion": {
        "primary": GREEN_800,
        "primary_deep": GREEN_950,
        "accent": TEAL,
        "title_color": GREEN_800,
        "name_color": CHARCOAL,
        "program_color": TEAL,
        "motif_color": TEAL,
        "page_bg": IVORY,
    },
    # Certificate of Participation: a touch more vibrant - teal and blue
    # accents over deep green and warm gold, still on a warm ivory sheet.
    "participation": {
        "primary": BLUE,
        "primary_deep": GREEN_950,
        "accent": TEAL,
        "title_color": GREEN_800,
        "name_color": CHARCOAL,
        "program_color": BLUE,
        "motif_color": TEAL,
        "page_bg": IVORY,
    },
    # Future types register here (e.g. "internship", "completion",
    # "participation") and reuse the whole shared layout.
}

# ============================================================
# Typography
# ============================================================
_ASSETS = Path(__file__).resolve().parent / "assets"
_FONT_DIR = _ASSETS / "fonts"

_FONT_FILES = {
    "serif": _FONT_DIR / "PlayfairDisplay.ttf",
    "serif_italic": _FONT_DIR / "PlayfairDisplay-Italic.ttf",
    "sans": _FONT_DIR / "OpenSans.ttf",
}
_FALLBACK_FONT = _ASSETS / "DejaVuSans.ttf"


def _resolve_font(name: str) -> str:
    candidate = _FONT_FILES.get(name)
    if candidate and candidate.is_file():
        return str(candidate)
    return str(_FALLBACK_FONT)


# Registered (name, weight) for each live font object so :func:`_scaled_font`
# can rebuild a scaled instance for the smaller output canvas. Bounded by the
# lru_cache on :func:`_font` (128 entries).
_FONT_META: dict[int, tuple[str, int | None]] = {}


@functools.lru_cache(maxsize=128)
def _font(name: str, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    """Load a truetype font, applying the requested weight to variable fonts."""
    font = ImageFont.truetype(_resolve_font(name), size)
    try:
        axes = font.get_variation_axes() or []
    except Exception:
        axes = []
    if axes and weight is not None:
        values = []
        for axis in axes:
            lo, hi = float(axis["minimum"]), float(axis["maximum"])
            label = axis["name"]
            if isinstance(label, bytes):
                label = label.decode("utf-8", "ignore")
            if "weight" in label.lower():
                values.append(max(lo, min(hi, float(weight))))
            else:
                values.append(hi)
        try:
            font.set_variation_by_axes(values)
        except Exception:  # noqa: BLE001 - keep the default instance on failure
            pass
    _FONT_META[id(font)] = (name, weight)
    return font


_SCALED_FONT_CACHE: dict[tuple[int, int], ImageFont.FreeTypeFont] = {}


def _scaled_font(font, sx: float):
    """Return ``font`` sized for the output canvas (identity when un-scaled).

    Scaling is intentional: the coordinate transform scales the pixel width of
    every glyph proportionally, so typography, spacing and wrap decisions stay
    faithful to the full-resolution design.
    """
    if font is None:
        return None
    size = getattr(font, "size", 0) or 0
    target = max(1, round(size * sx))
    if target == size:
        return font
    key = (id(font), target)
    cached = _SCALED_FONT_CACHE.get(key)
    if cached is not None:
        return cached
    name, weight = _FONT_META.get(id(font), ("sans", None))
    scaled = _font(name, target, weight)
    _SCALED_FONT_CACHE[key] = scaled
    return scaled


def serif(size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    return _font("serif", size, weight)


def serif_italic(size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    return _font("serif_italic", size, weight)


def sans(size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    return _font("sans", size, weight)


# ============================================================
# Drawing helpers
# ============================================================

def _hex(hex_value: str) -> tuple[int, int, int]:
    hex_value = hex_value.lstrip("#")
    return tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _hexa(hex_value: str, alpha: int) -> tuple[int, int, int, int]:
    r, g, b = _hex(hex_value)
    return r, g, b, alpha


def _blend(bg: tuple[int, int, int], fg: tuple[int, int, int], alpha: int) -> tuple[int, int, int]:
    """Alpha-blend ``fg`` over an opaque ``bg`` into a single RGB color.

    Lets the faint motif / grain layers draw directly on the small RGB canvas
    instead of materializing a full-page RGBA overlay and compositing it.
    """
    if alpha >= 255:
        return fg[:3]
    if alpha <= 0:
        return bg
    a = alpha / 255.0
    return tuple(round(b * (1 - a) + c * a) for b, c in zip(bg, fg[:3]))


def _scale_xy(img: Image.Image) -> tuple[float, float]:
    """Output scale factors for ``img`` against its design coordinate space."""
    design_w, design_h = getattr(img, "_canvas_design", (CANVAS_W, CANVAS_H))
    return img.width / design_w, img.height / design_h


class ScaledDraw:
    """Translate design-space drawing commands onto a smaller output canvas.

    Every coordinate, size, stroke width and font is scaled by ``img``'s scale
    factor, while measurement (``textlength``) keeps using the design-space
    font so the existing layout / wrapping / shrink logic runs unchanged.
    """

    __slots__ = ("_d", "sx", "sy")

    def __init__(self, draw, sx: float = 1.0, sy: float = 1.0):
        self._d = draw
        self.sx = float(sx)
        self.sy = float(sy)

    def _pts(self, xy):
        sx, sy = self.sx, self.sy
        if isinstance(xy, (tuple, list)) and len(xy) == 4 and all(
            isinstance(v, (int, float)) for v in xy
        ):
            x0, y0, x1, y1 = xy
            return [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        return [(x * sx, y * sy) for x, y in xy]

    def _w(self, width):
        if width is None:
            return None
        return max(1, round(width * (self.sx + self.sy) / 2))

    def _font(self, font):
        return _scaled_font(font, self.sx)

    # --- Measurement stays in the design space -----------------------------
    def textlength(self, text, font=None, **kwargs):
        return self._d.textlength(text, font=font, **kwargs)

    # --- Primitives scale onto the output canvas --------------------------
    def text(self, xy, text, fill=None, font=None, anchor=None, spacing=4,
             align="left", stroke_width=0, **kwargs):
        x, y = xy
        return self._d.text(
            (x * self.sx, y * self.sy),
            text, fill=fill, font=self._font(font), anchor=anchor,
            spacing=spacing, align=align,
            stroke_width=self._w(stroke_width), **kwargs,
        )

    def line(self, xy, fill=None, width=1, joint=None):
        return self._d.line(self._pts(xy), fill=fill, width=self._w(width), joint=joint)

    def rectangle(self, xy, fill=None, outline=None, width=1):
        return self._d.rectangle(
            self._pts(xy), fill=fill, outline=outline, width=self._w(width)
        )

    def rounded_rectangle(self, xy, radius=0, fill=None, outline=None, width=1, corners=None):
        return self._d.rounded_rectangle(
            self._pts(xy), radius=self._w(radius), fill=fill,
            outline=outline, width=self._w(width), corners=corners,
        )

    def ellipse(self, xy, fill=None, outline=None, width=1):
        return self._d.ellipse(self._pts(xy), fill=fill, outline=outline, width=self._w(width))

    def polygon(self, xy, fill=None, outline=None):
        return self._d.polygon(self._pts(xy), fill=fill, outline=outline)

    def __getattr__(self, item):
        # Unused drawing primitives degrade to direct (un-scaled) calls.
        return getattr(self._d, item)


def _draw(img: Image.Image) -> ScaledDraw:
    """A ``ScaledDraw`` bound to ``img`` using its design coordinate space."""
    sx, sy = _scale_xy(img)
    return ScaledDraw(ImageDraw.Draw(img), sx, sy)


def _locked_render(fn):
    """Hold the render lock for one document-rendering entry point."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with _RENDER_LOCK:
            return fn(*args, **kwargs)

    return wrapper


def _draw_tracked(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    text: str,
    font,
    fill,
    tracking: int = 0,
    anchor: str = "mm",
) -> float:
    """Draw letterspaced text; ``x`` is the anchor x (center/left/right).

    ``y`` is the baseline. Returns the total drawn width.
    """
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    if anchor.startswith("r"):
        start_x = x - total
    elif anchor.startswith("m"):
        start_x = x - total / 2
    else:
        start_x = x
    for ch, width in zip(text, widths):
        draw.text((start_x, y), ch, font=font, fill=fill, anchor="ls")
        start_x += width + tracking
    return total


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _rounded_panel(img: Image.Image, box, radius: int, fill, outline=None, width: int = 2):
    """Draw a rounded rectangle plus an optional outline ring."""
    dr = _draw(img)
    x0, y0, x1, y1 = box
    if fill is not None:
        dr.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
    if outline is not None:
        dr.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=outline, width=width)
    return dr


# --- Botanical (leaf) decoration ----------------------------------------
# Subtle background greenery: a pointed teardrop leaf (base at origin, tip
# at (length, 0)) drawn along any direction, kept faint so it reads as a
# quiet textured border rather than a loud ornament.
def _leaf_pts(length: float, halfw: float, n: int = 16):
    pts = []
    for i in range(n + 1):
        u = i / n
        pts.append((length * u, -halfw * math.sin(math.pi * u)))
    for i in range(n, -1, -1):
        u = i / n
        pts.append((length * u, halfw * math.sin(math.pi * u)))
    return pts


def _draw_leaf(dr, x, y, length, angle, fill, outline=None, vein=None):
    """Draw a leaf pointing from (x, y) at `angle` degrees (0 = east, cw)."""
    halfw = length * 0.34
    rad = math.radians(angle)
    c, s = math.cos(rad), math.sin(rad)
    xy = [(x + px * c - py * s, y + px * s + py * c) for px, py in _leaf_pts(length, halfw)]
    dr.polygon(xy, fill=fill)
    if outline is not None:
        dr.polygon(xy, outline=outline)
    if vein is not None:
        dr.line([(x, y), (x + length * c, y + length * s)], fill=vein, width=max(1, int(length * 0.045)))


def _centre_motif(img: Image.Image, palette: dict):
    """Soft medallion in the middle of the sheet under the recipient's name.

    Faint gold rings, whisper-thin radial rays and a small leaf rosette sit
    behind the headline content to add depth without stealing legibility.

    The faint tints are pre-blended onto the page colour and drawn straight
    onto the sheet, so no full-page RGBA overlay is materialized.
    """
    dr = _draw(img)
    bg = _hex(palette.get("page_bg", PAGE_BG))
    gold = _hex(GOLD_LIGHT)
    teal = _hex(palette.get("motif_color", TEAL))
    cx, cy = CX, 1160

    # Concentric rings.
    for r, w, a in ((560, 2, 70), (430, 1, 58), (150, 1, 80)):
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=_blend(bg, gold, a), width=w)

    # Whisper-thin radial rays.
    ray_col = _blend(bg, teal, 13)
    for i in range(48):
        ang = math.radians(i * (360 / 48))
        c, s = math.cos(ang), math.sin(ang)
        r0 = 100 + (40 if i % 2 == 0 else 90)
        r1 = 585 if i % 2 == 0 else 545
        dr.line([(cx + r0 * c, cy + r0 * s), (cx + r1 * c, cy + r1 * s)], fill=ray_col, width=3)

    # Eight faint leaves radiating like a distant sunburst, alternating
    # gold / green / teal / sage so the centre carries a little colour.
    cols = [gold, _hex(palette["green_700"]), teal, _hex(SAGE)]
    tinted = [_blend(bg, col, 34) for col in cols]
    for i in range(8):
        ang = math.radians(-90 + i * 45)
        c, s = math.cos(ang), math.sin(ang)
        bx, by = cx + 70 * c, cy + 70 * s
        _draw_leaf(dr, bx, by, 205, math.degrees(ang), tinted[i % 4])


def _background_fill(img: Image.Image, palette: dict):
    """A whisper of dotted paper grain so the sheet never feels flat.

    Faint dots across the field (skipping the QR region) that stay well
    behind the text, medallion and QR code. Tints are pre-blended onto the
    page colour and drawn directly, avoiding a full-page RGBA overlay.
    """
    dr = _draw(img)
    bg = _hex(palette.get("page_bg", PAGE_BG))
    green = _hex(palette["green_800"])

    # Dotted paper grain (skip the QR region so scanning stays clean).
    dot_col = _blend(bg, green, 9)
    for y in range(170, CANVAS_H - 170, 46):
        off = 23 if (y // 46) % 2 else 0
        for x in range(170 + off, CANVAS_W - 170, 46):
            if 2558 <= x <= 3300 and 1800 <= y <= 2300:
                continue
            dr.ellipse([x, y, x + 3, y + 3], fill=dot_col)

    # A quiet scatter of small leaves filling the open areas.
    scatter = [
        (600, 430, 105), (2900, 430, -105),
        (700, 760, 100), (2800, 760, -100),
        (600, 1150, 95), (2900, 1150, -95),
        (650, 1400, 112), (2920, 1400, -112),
        (1430, 1700, 105), (2200, 1700, -105),
        (1430, 1900, 120), (2200, 1920, -60),
    ]
    cols = [green, _hex(palette["green_700"]), _hex(SAGE), _hex(GOLD_BRIGHT)]
    tinted = [_blend(bg, col, 26) for col in cols]
    for i, (x, y, ang) in enumerate(scatter):
        _draw_leaf(dr, x, y, 76 + 18 * (i % 3), ang, tinted[i % 4])


def _frame(img: Image.Image, palette: dict):
    """Airy triple-line border with a light leaf garland in the middle band.

    A fine outer hairline, a soft pale mid-rule and an inner green rule,
    with a delicate garland of light leaves (no gold, no dark tones) and a
    simple gold diamond at each corner.
    """
    dr = _draw(img)

    def garland_leaf(x, y, length, ang, col, idx):
        # Teal leaves stay fainter than the sage ones so the band stays airy.
        base = 150 if col[0] > 100 else 100
        _draw_leaf(dr, x, y, length, ang, col + (base,))
        dr.ellipse([x - 3, y - 3, x + 3, y + 3], fill=_hex(SAGE) + (200,))

    gold_soft = _hex(palette["green_800"])
    green = _hex(palette["green_800"])
    sage = _hex(SAGE)
    aqua = _hex("#93C0BC")

    oi, mid, ii = 92, 150, 206
    dr.rectangle([oi, oi, CANVAS_W - oi, CANVAS_H - oi], outline=gold_soft, width=2)
    dr.rectangle([mid, mid, CANVAS_W - mid, CANVAS_H - mid], outline=_hexa(SAGE, 140), width=2)
    dr.rectangle([ii, ii, CANVAS_W - ii, CANVAS_H - ii], outline=green, width=3)

    # Light leaf garland along each edge in the middle band.
    leaf_len = 32
    step = 88
    garland_cols = [sage, aqua]
    n = 0
    for y in (mid, CANVAS_H - mid):
        inward = 90 if y == mid else 270  # top edge leaves hang down, bottom point up
        for x in range(mid + 110, CANVAS_W - mid - 110, step):
            tilt = -22 if n % 2 == 0 else 22
            garland_leaf(x, y, leaf_len, inward + tilt, garland_cols[n % 2], n)
            n += 1
    for x in (mid, CANVAS_W - mid):
        inward = 0 if x == mid else 180  # left edge points right, right edge points left
        for y in range(mid + 110, CANVAS_H - mid - 110, step):
            tilt = -22 if n % 2 == 0 else 22
            garland_leaf(x, y, leaf_len, inward + tilt, garland_cols[n % 2], n)
            n += 1

    return dr


def _paste_emblem(img: Image.Image, logo: Image.Image, cx: float, cy: float, diameter: int, ring_color):
    """Paste the foundation logo cropped into a ringed medallion.

    A faint halo, a warm gold ring, a slim teal ringlet and a hairline gold
    ring frame the logo without adding bulk to the masthead. The medallion is
    rasterized in design space and scaled onto the (smaller) output canvas.
    """
    sx, sy = _scale_xy(img)
    size = max(1, int(diameter))
    halo = _hexa(ring_color, 110)
    _draw(img).ellipse(
        [cx - size / 2 - 15, cy - size / 2 - 15, cx + size / 2 + 15, cy + size / 2 + 15],
        outline=halo,
        width=2,
    )
    circle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    # Shrink the raw logo before decoding so huge source images never load
    # at native resolution just to be pasted at ~170 px.
    resized = logo
    if min(resized.size) > size * 2:
        resized = resized.copy()
        resized.thumbnail((size * 2, size * 2), Image.LANCZOS)
    resized = resized.convert("RGBA").resize((size, size), Image.LANCZOS)
    circle.paste(resized, (0, 0), mask)
    draw = ImageDraw.Draw(circle)
    draw.ellipse([2, 2, size - 2, size - 2], outline=_hex(ring_color), width=6)
    draw.ellipse([15, 15, size - 15, size - 15], outline=_hex(TEAL), width=3)
    draw.ellipse([24, 24, size - 24, size - 24], outline=_hexa(ring_color, 170), width=2)
    out_w = max(1, round(size * sx))
    out_h = max(1, round(size * sy))
    if (out_w, out_h) != circle.size:
        circle = circle.resize((out_w, out_h), Image.BILINEAR)
    img.paste(circle, (int(cx * sx - out_w / 2), int(cy * sy - out_h / 2)), circle)
    circle.close()


def _text_on_circle(img: Image.Image, cx: float, cy: float, radius: float, text: str, font, fill, start_deg: float):
    """Draw text following the top of a circle (chiaroscuro on a seal)."""
    dr = _draw(img)
    sx, sy = _scale_xy(img)
    total = sum(dr.textlength(ch, font=font) for ch in text)
    span_deg = (total / (2 * math.pi * radius)) * 360
    angle = math.radians(start_deg)
    step = math.radians(span_deg / max(len(text) - 1, 1))
    fallback = int(radius * 0.9) * 2
    fs = max(1, round(fallback * sx))
    fh = max(1, round(fallback * sy))
    sfont = _scaled_font(font, sx)
    for ch in text:
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        temp = Image.new("RGBA", (fs, fh), (0, 0, 0, 0))
        tdr = ImageDraw.Draw(temp)
        bbox = tdr.textbbox((0, 0), ch, font=sfont)
        cw = tdr.textlength(ch, font=sfont)
        chx = (fs - cw) / 2 - bbox[0]
        chy = (fh - (bbox[3] - bbox[1])) / 2 - bbox[1]
        tdr.text((chx, chy), ch, font=sfont, fill=fill)
        tilt = math.degrees(angle) + 90
        temp = temp.rotate(-tilt, resample=Image.BICUBIC)
        img.paste(temp, (int(px * sx - fs / 2), int(py * sy - fh / 2)), temp)
        angle += step


def _seal(img: Image.Image, cx: float, cy: float, radius: float, palette: dict):
    """Draw the procedural official seal (double ring, scallops, arched text)."""
    px = int(cx)
    py = int(cy)
    dr = _draw(img)
    gold = _hex(palette["gold_bright"])
    green = _hex(palette["green_800"])
    ivory_rgb = _hex(palette["ivory"])

    # Scalloped edge tick marks.
    ticks = 36
    for i in range(ticks):
        a0 = (i / ticks) * 2 * math.pi
        a1 = ((i + 0.5) / ticks) * 2 * math.pi
        r_outer = radius
        r_inner = radius - 10
        dr.line(
            [
                (px + r_outer * math.cos(a0), py + r_outer * math.sin(a0)),
                (px + r_inner * math.cos(a0), py + r_inner * math.sin(a0)),
            ],
            fill=gold,
            width=3,
        )
        dr.line(
            [
                (px + r_outer * math.cos(a1), py + r_outer * math.sin(a1)),
                (px + r_inner * math.cos(a1), py + r_inner * math.sin(a1)),
            ],
            fill=gold,
            width=3,
        )

    # Outer gold ring, inner green ring, ivory field.
    dr.ellipse([px - radius, py - radius, px + radius, py + radius], outline=gold, width=6)
    dr.ellipse([px - (radius - 18), py - (radius - 18), px + (radius - 18), py + (radius - 18)], outline=green, width=4)
    dr.ellipse([px - (radius - 30), py - (radius - 30), px + (radius - 30), py + (radius - 30)], fill=ivory_rgb)

    # Arched brand text + central star emblem (decorative seal, distinct
    # from the foundation logo shown in the masthead).
    _text_on_circle(
        img,
        px,
        py - 10,
        radius - 26,
        "PIPLAD WELFARE FOUNDATION",
        sans(int(radius * 0.22), 600),
        _hex(palette["green_800"]),
        180,
    )
    star_outer = radius * 0.40
    star_inner = star_outer * 0.46
    star_pts = []
    for i in range(10):
        rad = star_outer if i % 2 == 0 else star_inner
        ang = math.radians(-90 + i * 36)
        star_pts.append((px + rad * math.cos(ang), py + 4 + rad * math.sin(ang)))
    dr.polygon(star_pts, fill=_hex(palette["green_800"]))
    dr.ellipse([px - 4, py - 15, px + 4, py - 7], fill=_hex(GOLD_BRIGHT))


def _qr_image(data: str, target: int = 350, border: int = 4):
    """Return a crisp, padded QR image (dark modules on white quiet zone)."""
    import io

    import segno

    qr = segno.make(data, error="m", micro=False)
    dim = qr.symbol_size(scale=1)[0] + 2 * border
    scale = max(1, target // dim)
    buffer = io.BytesIO()
    qr.save(
        buffer,
        kind="png",
        scale=scale,
        border=border,
        dark=(26, 26, 26),
        light=(255, 255, 255),
    )
    buffer.seek(0)
    try:
        return Image.open(buffer).convert("RGBA")
    finally:
        buffer.close()


# ============================================================
# Shared layout blocks (used by every certificate type)
# ============================================================

def _page_background(img: Image.Image, palette: dict):
    """Apply the shared full-page backdrop: frame, texture grain, medallion."""
    _frame(img, palette)
    _background_fill(img, palette)
    _centre_motif(img, palette)


def _blank_canvas(palette: dict, w: int | None = None, h: int | None = None) -> Image.Image:
    """A fresh sheet in the palette's page colour at the output resolution.

    The canvas records its design coordinate space so :func:`_draw` can scale
    every primitive down from the full-resolution layout.
    """
    img = Image.new("RGB", (w or OUTPUT_W, h or OUTPUT_H), _hex(palette.get("page_bg", PAGE_BG)))
    img._canvas_design = (CANVAS_W, CANVAS_H)
    return img


def _masthead(img: Image.Image, palette: dict, logo_bytes: bytes | None):
    """Logo medallion, foundation name, tagline and divider rule."""
    dr = _draw(img)
    emblem_d = 170
    if logo_bytes:
        import io

        try:
            # Opened lazily; _paste_emblem shrinks it before decoding.
            logo = Image.open(io.BytesIO(logo_bytes))
            _paste_emblem(img, logo, CX, 330, emblem_d, GOLD_BRIGHT)
        except Exception:  # noqa: BLE001 - logo must never break rendering
            pass

    _draw_tracked(
        dr, CX, 512, "PIPLAD WELFARE FOUNDATION", sans(54, 600),
        _hex(GREEN_800), tracking=14,
    )
    _draw_tracked(
        dr, CX, 566, "Transforming Lives Through Compassion & Service",
        serif_italic(32), _hex(MUTED), tracking=2,
    )
    # Divider rule with center diamond (teal diamonds at the tips).
    gold = _hex(GOLD_BRIGHT)
    teal = _hex(TEAL)
    dr.line([CX - 310, 600, CX - 18, 600], fill=gold, width=3)
    dr.line([CX + 18, 600, CX + 310, 600], fill=gold, width=3)
    dr.polygon([(CX - 12, 600), (CX, 588), (CX + 12, 600), (CX, 612)], fill=gold)
    for sx in (-1, 1):
        ex = CX + 310 * sx
        dr.polygon([(ex - 10, 600), (ex, 591), (ex + 10, 600), (ex, 609)], fill=teal)
    return dr


def _title_block(img: Image.Image, palette: dict, big_word: str):
    """Two-line certificate title with letterspacing and the type's big word."""
    dr = _draw(img)
    _draw_tracked(dr, CX, 716, "CERTIFICATE OF", serif(104, 700), _hex(palette["title_color"]), tracking=8)
    _draw_tracked(dr, CX, 852, big_word, serif(146, 800), _hex(palette["title_color"]), tracking=9)
    return dr


def _presentation_line(img: Image.Image):
    """The 'proudly presented to' line shared by appreciation and internship."""
    dr = _draw(img)
    _draw_tracked(dr, CX, 972, "This certificate is proudly presented to", serif_italic(44), _hex(CHARCOAL), tracking=1)
    return dr


def _recipient_element(img: Image.Image, palette: dict, recipient: str):
    """The dominant recipient name plus its gold flourish underline.

    Long names balance across two serif lines instead of shrinking until the
    identity loses its presence; the underline tapers with a teal hairline and
    gold diamond tips that echo the masthead rule.
    """
    dr = _draw(img)
    max_line = 2500
    full_font = serif(212, 800)
    single_w = dr.textlength(recipient, font=full_font)
    single_font = full_font if single_w <= max_line else serif(int(212 * max_line / single_w), 800)

    gold = _hex(GOLD_BRIGHT)
    teal = _hex(TEAL)
    if single_font.size >= 135:
        dr.text((CX, 1210), recipient, font=single_font, fill=_hex(palette["name_color"]), anchor="ms")
        underline_y, sub_y = 1302, 1313
        wide, tee = 470, 60
    else:
        lines = _wrap_text(dr, recipient, full_font, max_line)
        widest = max(dr.textlength(ln, font=full_font) for ln in lines)
        target = max(min(int(212 * max_line / widest), 132), 132)
        name_font = serif(target, 800)
        lines = _wrap_text(dr, recipient, name_font, max_line)[:2]
        baseline = 1130
        gap = int(name_font.size * 1.15)
        for line in lines:
            dr.text((CX, baseline), line, font=name_font, fill=_hex(palette["name_color"]), anchor="ms")
            baseline += gap
        underline_y, sub_y = baseline - gap + 60, baseline - gap + 67
        wide, tee = 430, 52

    dr.line([CX - wide, underline_y, CX - tee, underline_y], fill=gold, width=4)
    dr.line([CX + tee, underline_y, CX + wide, underline_y], fill=gold, width=4)
    dr.line([CX - wide + 14, sub_y, CX - tee + 14, sub_y], fill=teal, width=2)
    dr.line([CX + tee - 14, sub_y, CX + wide - 14, sub_y], fill=teal, width=2)
    dr.polygon([(CX - 15, underline_y), (CX, underline_y - 15), (CX + 15, underline_y), (CX, underline_y + 15)], fill=gold)
    for sx in (-1, 1):
        ex = CX + wide * sx
        dr.polygon([(ex - 8, underline_y), (ex, underline_y - 9), (ex + 8, underline_y), (ex, underline_y + 9)], fill=gold)
    return dr


# ============================================================
# Certificate of Appreciation
# ============================================================

@_locked_render
def render_appreciation_certificate(
    *,
    first_name: str = "",
    last_name: str = "",
    name: str | None = None,
    program_name: str = "",
    certificate_number: str = "",
    issue_date: str = "",
    email: str = "",
    qr_data: str = "",
    logo_bytes: bytes | None = None,
    out_w: int | None = None,
    out_h: int | None = None,
) -> Image.Image:
    """Render the premium A4 Certificate of Appreciation.

    ``email`` is accepted for parity with the issuance pipeline but is never
    printed on the certificate (privacy).
    """
    palette = dict(PALETTES["base"])
    palette.update(PALETTES["appreciation"])

    recipient = (name or " ".join(filter(None, (first_name, last_name)))).strip() or "Recipient"
    program = program_name.strip() or "Piplad Welfare Foundation Volunteer Programme"
    cert_no = certificate_number.strip() or "CERT-YYYY-000000"
    issued = issue_date.strip() or ""

    img = _blank_canvas(palette, out_w, out_h)
    _page_background(img, palette)
    _masthead(img, palette, logo_bytes)
    dr = _draw(img)

    # --- Title -----------------------------------------------------------
    _title_block(img, palette, "APPRECIATION")

    # --- Presentation line ------------------------------------------------
    _presentation_line(img)

    # --- Recipient name (dominant element) --------------------------------
    _recipient_element(img, palette, recipient)

    # --- Achievement block ------------------------------------------------
    lead = sans(44)
    grey = _hex("#3D4A44")
    lead_lines = [
        "For your valuable contribution, dedication and",
        "meaningful participation in",
    ]
    baseline = 1396
    for line in lead_lines:
        dr.text((CX, baseline), line, font=lead, fill=grey, anchor="ma")
        baseline += 54

    program_font = serif_italic(76, 500)
    program_lines = _wrap_text(dr, program, program_font, 2600)
    pbase = 1600
    if len(program_lines) > 1:
        # Shrink toward a wrapped fit rather than clipping the programme name.
        program_font = serif_italic(60, 500)
        program_lines = _wrap_text(dr, program, program_font, 2600)
        while len(program_lines) > 2 and program_font.size > 48:
            program_font = serif_italic(program_font.size - 4, 500)
            program_lines = _wrap_text(dr, program, program_font, 2600)
        pbase = 1580
    for line in program_lines:
        dr.text((CX, pbase), line, font=program_font, fill=_hex(palette["program_color"]), anchor="ma")
        pbase += 82

    # --- Bottom band: signature (left) / seal+dates (center) / QR (right) ---
    _signature_block(img, CX - 1134)
    _identity_block(img, palette, issued, cert_no)
    _qr_block(img, palette, qr_data)
    _footer_strip(img, palette)

    return img


def _bezier_points(p0, c1, c2, p1, n: int = 24):
    """Sample a cubic Bezier curve as a list of (x, y) points."""
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t**3 * p1[0]
        y = mt**3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t**3 * p1[1]
        pts.append((x, y))
    return pts[:-1]


def _signature_flourish(img: Image.Image, cx: float):
    """Draw a sign-off flourish directly on the sheet (no image asset).

    A script-style monogram with a tall looped ascender, a closing bowl,
    and a long sweeping underline that waves onto the rule - drawn from
    cubic Beziers so it never rasterizes and matches any palette.
    """
    ink = _hex("#2B3A35")
    ox, oy = cx, 2092

    def stroke(segments, width):
        dr = _draw(img)
        pts = []
        for p0, c1, c2, p1 in segments:
            sample = _bezier_points(
                (ox + p0[0], oy + p0[1]),
                (ox + c1[0], oy + c1[1]),
                (ox + c2[0], oy + c2[1]),
                (ox + p1[0], oy + p1[1]),
            )
            if pts:
                pts.extend(sample[1:])
            else:
                pts.extend(sample)
        dr.line(pts, fill=ink, width=width, joint="curve")
        dr.line(pts[-3:], fill=ink, width=max(2, width - 3), joint="curve")
        dr.line(pts[:3], fill=ink, width=max(2, width - 3), joint="curve")

    # Tall ascender forming the monogram loop, closed by a soft bowl.
    stroke(
        [
            ((-240, -22), (-150, -192), (-95, -230), (-55, -224)),
            ((-55, -224), (-10, -217), (58, -192), (92, -147)),
            ((92, -147), (115, -117), (70, -77), (30, -70)),
            ((30, -70), (10, -67), (-8, -82), (-30, -94)),
        ],
        6,
    )
    # Sweeping underline that waves across and feathers off the rule.
    stroke(
        [
            ((-150, -10), (-30, -57), (10, -7), (70, -24)),
            ((70, -24), (130, -42), (180, -2), (250, -20)),
            ((250, -20), (285, -30), (300, -2), (320, 4)),
        ],
        5,
    )
    # Small rising accent flick above the sweep.
    stroke([((70, -234), (120, -267), (165, -262), (182, -217))], 4)


def _signature_block(img: Image.Image, cx: float):
    """Authorized sign-off flourish, rule, and role (lower-left)."""
    _signature_flourish(img, cx)
    dr = _draw(img)
    dr.line([cx - 320, 2120, cx + 320, 2120], fill=_hex(TEAL), width=3)
    dr.text((cx, 2180), "Authorized Signature", font=sans(34, 600), fill=_hex(CHARCOAL), anchor="ms")
    dr.text((cx, 2238), "PIPLAD WELFARE FOUNDATION", font=sans(28, 400), fill=_hex(MUTED), anchor="ms")


def _identity_block(img: Image.Image, palette: dict, issued: str, cert_no: str):
    """Issue date and certificate number (bottom-center).

    A hairline separator with a gold diamond divides the date from the number,
    which is set on a slim ivory plate with a hairline gold outline so it reads
    as an engraved, officially stamped credential number.
    """
    dr = _draw(img)

    _draw_tracked(dr, CX, 2030, "DATE OF ISSUE", sans(30, 600), _hex(MUTED), tracking=5)
    _draw_tracked(dr, CX, 2100, issued, serif(54, 600), _hex(palette["primary"]), tracking=1)

    num_font = sans(42, 600)
    nw = dr.textlength(cert_no, font=num_font)
    sep_w = max(nw / 2 + 96, 220)
    gold = _hex(GOLD_BRIGHT)
    for side in (-1, 1):
        x0 = CX + side * (nw / 2 + 78)
        dr.line([CX + side * (sep_w + 14), 2147, x0 - 12, 2147], fill=_hexa(SAGE, 200), width=2)
    dr.polygon([(CX - 10, 2147), (CX, 2139), (CX + 10, 2147), (CX, 2155)], fill=gold)

    _draw_tracked(dr, CX, 2186, "CERTIFICATE NO.", sans(30, 600), _hex(MUTED), tracking=5)
    px0 = CX - nw / 2 - 44
    px1 = CX + nw / 2 + 44
    dr.rounded_rectangle(
        [px0, 2208, px1, 2266],
        radius=16,
        fill=_hexa(palette.get("ivory", IVORY), 205),
        outline=_hexa(GOLD_BRIGHT, 190),
        width=2,
    )
    dr.text((CX, 2238), cert_no, font=num_font, fill=_hex(CHARCOAL), anchor="mm")


def _qr_block(img: Image.Image, palette: dict, qr_data: str):
    """Verification QR (lower-right) without any panel border.

    The code sits directly on the certificate with its own white quiet zone,
    framed by four delicate gold corner brackets drawn just outside the quiet
    zone so scanning is never affected - it belongs to the page rather than
    looking like a pasted-on sticker.
    """
    cx = CX + 1174
    box = (cx - 370, 1800, cx + 370, 2300)
    dr = _draw(img)

    _draw_tracked(dr, cx, 2150, "SCAN TO VERIFY", sans(32, 700), _hex(palette["primary"]), tracking=5)

    url_font = sans(22)
    url_lines = _wrap_text(dr, qr_data, url_font, 690) if qr_data else []
    url_lines = url_lines[:2]
    ubase = 2212
    for line in url_lines:
        dr.text((cx, ubase), line, font=url_font, fill=_hex(MUTED), anchor="ma")
        ubase += 36

    if qr_data:
        qr_top = box[1] + 30
        qr_bottom = 2124
        avail = qr_bottom - qr_top
        qr = _qr_image(qr_data, target=avail, border=4)
        qy = qr_top + (avail - qr.height) // 2
        qx = int(cx - qr.width // 2)
        qw, qh = qr.size
        sx, sy = _scale_xy(img)
        out_w = max(1, round(qw * sx))
        out_h = max(1, round(qh * sy))
        if (out_w, out_h) != (qw, qh):
            qr = qr.resize((out_w, out_h), Image.BILINEAR)
        img.paste(qr, (int(qx * sx), int(qy * sy)), qr)
        qr.close()

        n = 34  # bracket arm length (design space; scaled through dr)
        off = 14  # clear of the quiet zone so scanning is never affected
        gold = _hexa(GOLD_BRIGHT, 180)
        corners = [
            (qx - off, qy - off),
            (qx + qw + off, qy - off),
            (qx - off, qy + qh + off),
            (qx + qw + off, qy + qh + off),
        ]
        for bx, by in corners:
            sdx = -1 if bx < qx else 1
            sdy = -1 if by < qy else 1
            dr.line([(bx, by + sdy * n), (bx, by)], fill=gold, width=3)
            dr.line([(bx, by), (bx + sdx * n, by)], fill=gold, width=3)
    else:
        dr.text((cx, 2000), "QR unavailable", font=sans(30), fill=_hex(MUTED), anchor="ms")


def _footer_strip(img: Image.Image, palette: dict):
    """A short 'verify online' inscription centered in the lower frame band.

    A letterspaced small-caps line sits on the mid-line with gold hairlines
    and a diamond on each side, echoing the masthead rule. The tone stays
    quiet so the certificate reads as an official, self-authenticating
    document.
    """
    dr = _draw(img)
    text = "VERIFIABLE AT PIPLADFOUNDATION.IN/VERIFY"
    font = sans(24, 700)
    half = _draw_tracked(dr, CX, 2296, text, font, _hex(GREEN_800), tracking=4) / 2
    gold = _hex(GOLD_BRIGHT)
    for side in (-1, 1):
        bx = CX + side * (half + 66)
        dr.line([bx - 168, 2296, bx - 20, 2296], fill=gold, width=2)
        dr.line([bx + 20, 2296, bx + 168, 2296], fill=gold, width=2)
        dr.polygon([(bx - 8, 2296), (bx, 2288), (bx + 8, 2296), (bx, 2304)], fill=gold)


# ============================================================
# Certificate of Internship
# ============================================================

def _internship_period_block(img: Image.Image, palette: dict, start: str, end: str):
    """The Internship Period band: a small-caps label, the date range in the
    primary accent, and warm gold diamond dots flanking the dates."""
    period = f"{start} — {end}".strip(" —")
    if not period:
        return
    dr = _draw(img)

    _draw_tracked(dr, CX, 1830, "INTERNSHIP PERIOD", sans(30, 600), _hex(MUTED), tracking=5)

    period_font = serif(56, 700)
    if dr.textlength(period, font=period_font) > 2400:
        period_font = serif(int(56 * 2400 / dr.textlength(period, font=period_font)), 700)
    dr.text((CX, 1905), period, font=period_font, fill=_hex(palette["primary"]), anchor="ms")

    half = dr.textlength(period, font=period_font) / 2
    gold = _hex(GOLD_BRIGHT)
    for side in (-1, 1):
        dx = CX + side * (half + 90)
        dr.polygon([(dx - 9, 1905), (dx, 1896), (dx + 9, 1905), (dx, 1914)], fill=gold)


@_locked_render
def render_internship_certificate(
    *,
    first_name: str = "",
    last_name: str = "",
    name: str | None = None,
    program_name: str = "",
    certificate_number: str = "",
    issue_date: str = "",
    starting_date: str = "",
    end_date: str = "",
    email: str = "",
    qr_data: str = "",
    logo_bytes: bytes | None = None,
    out_w: int | None = None,
    out_h: int | None = None,
) -> Image.Image:
    """Render the premium A4 Certificate of Internship.

    ``email`` is accepted for parity with the issuance pipeline but is never
    printed on the certificate (privacy).
    """
    palette = dict(PALETTES["base"])
    palette.update(PALETTES["internship"])

    recipient = (name or " ".join(filter(None, (first_name, last_name)))).strip() or "Recipient"
    program = program_name.strip() or "Piplad Welfare Foundation Internship Programme"
    cert_no = certificate_number.strip() or "CERT-YYYY-000000"
    issued = issue_date.strip() or ""

    img = _blank_canvas(palette, out_w, out_h)
    _page_background(img, palette)
    _masthead(img, palette, logo_bytes)
    dr = _draw(img)

    # --- Title -----------------------------------------------------------
    _title_block(img, palette, "INTERNSHIP")

    # --- Presentation line ------------------------------------------------
    _presentation_line(img)

    # --- Recipient name (dominant element) --------------------------------
    _recipient_element(img, palette, recipient)

    # --- Achievement block ------------------------------------------------
    lead = sans(44)
    grey = _hex("#3D4A44")
    dr.text((CX, 1396), "For successfully completing the internship / program in", font=lead, fill=grey, anchor="ma")

    program_font = serif_italic(76, 500)
    program_lines = _wrap_text(dr, program, program_font, 2600)
    pbase = 1620
    if len(program_lines) > 1:
        # Shrink toward a wrapped fit rather than clipping the programme name.
        program_font = serif_italic(60, 500)
        program_lines = _wrap_text(dr, program, program_font, 2600)
        while len(program_lines) > 2 and program_font.size > 48:
            program_font = serif_italic(program_font.size - 4, 500)
            program_lines = _wrap_text(dr, program, program_font, 2600)
        pbase = 1600
    for line in program_lines:
        dr.text((CX, pbase), line, font=program_font, fill=_hex(palette["program_color"]), anchor="ma")
        pbase += 82

    # --- Internship Period (dates clearly visible) -------------------------
    _internship_period_block(img, palette, starting_date.strip(), end_date.strip())

    # --- Bottom band: signature (left) / seal+dates (center) / QR (right) ---
    _signature_block(img, CX - 1134)
    _identity_block(img, palette, issued, cert_no)
    _qr_block(img, palette, qr_data)
    _footer_strip(img, palette)

    return img


# ============================================================
# Certificate of Completion
# ============================================================

def _completion_org_line(dr: ImageDraw.ImageDraw, org_name: str):
    """A single elegant line for the host organisation, shrunk to fit."""
    if not org_name:
        return
    font = serif_italic(56, 500)
    while font.size > 44 and dr.textlength(org_name, font=font) > 2540:
        size = max(44, int(font.size - 4))
        font = serif_italic(size, 500)
    dr.text((CX, 1710), org_name, font=font, fill=_hex(GREEN_800), anchor="ma")


def _completion_date_block(img: Image.Image, palette: dict, date_value: str):
    """The 'Date:' band: a small-caps label, the event date in the primary
    accent, and warm gold diamond dots flanking the value."""
    date_value = date_value.strip()
    if not date_value:
        return
    dr = _draw(img)

    _draw_tracked(dr, CX, 1860, "DATE", sans(30, 600), _hex(MUTED), tracking=5)

    period_font = serif(56, 700)
    if dr.textlength(date_value, font=period_font) > 2400:
        period_font = serif(int(56 * 2400 / dr.textlength(date_value, font=period_font)), 700)
    y = 1935
    dr.text((CX, y), date_value, font=period_font, fill=_hex(palette["primary"]), anchor="ms")

    half = dr.textlength(date_value, font=period_font) / 2
    gold = _hex(GOLD_BRIGHT)
    for side in (-1, 1):
        dx = CX + side * (half + 90)
        dr.polygon([(dx - 9, y), (dx, y - 9), (dx + 9, y), (dx, y + 9)], fill=gold)


@_locked_render
def render_completion_certificate(
    *,
    first_name: str = "",
    last_name: str = "",
    name: str | None = None,
    program_name: str = "",
    organisation_name: str = "",
    completion_date: str = "",
    certificate_number: str = "",
    issue_date: str = "",
    email: str = "",
    qr_data: str = "",
    logo_bytes: bytes | None = None,
    out_w: int | None = None,
    out_h: int | None = None,
) -> Image.Image:
    """Render the premium A4 Certificate of Completion.

    ``email`` is accepted for parity with the issuance pipeline but is never
    printed on the certificate (privacy).
    """
    palette = dict(PALETTES["base"])
    palette.update(PALETTES["completion"])

    recipient = (name or " ".join(filter(None, (first_name, last_name)))).strip() or "Recipient"
    program = program_name.strip() or "Piplad Welfare Foundation Programme"
    org_name = organisation_name.strip()
    cert_no = certificate_number.strip() or "CERT-YYYY-000000"
    issued = issue_date.strip() or ""

    img = _blank_canvas(palette, out_w, out_h)
    _page_background(img, palette)
    _masthead(img, palette, logo_bytes)
    dr = _draw(img)

    # --- Title -----------------------------------------------------------
    _title_block(img, palette, "COMPLETION")

    # --- Presentation line ------------------------------------------------
    _presentation_line(img)

    # --- Recipient name (dominant element) --------------------------------
    _recipient_element(img, palette, recipient)

    # --- Achievement block ------------------------------------------------
    lead = sans(44)
    grey = _hex("#3D4A44")
    dr.text((CX, 1396), "For successfully completing", font=lead, fill=grey, anchor="ma")

    program_font = serif_italic(76, 500)
    program_lines = _wrap_text(dr, program, program_font, 2600)
    pbase = 1580
    if len(program_lines) > 1:
        # Shrink toward a wrapped fit rather than clipping the programme name.
        program_font = serif_italic(60, 500)
        program_lines = _wrap_text(dr, program, program_font, 2600)
        while len(program_lines) > 2 and program_font.size > 48:
            program_font = serif_italic(program_font.size - 4, 500)
            program_lines = _wrap_text(dr, program, program_font, 2600)
        # Two lines max so the host organisation line below never clips.
        program_lines = _wrap_text(dr, program, program_font, 2600)[:2]
        pbase = 1560
    for line in program_lines:
        dr.text((CX, pbase), line, font=program_font, fill=_hex(palette["program_color"]), anchor="ma")
        pbase += 82

    _completion_org_line(dr, org_name)

    # --- Event date (clearly visible) --------------------------------------
    _completion_date_block(img, palette, completion_date)

    # --- Bottom band: signature (left) / seal+dates (center) / QR (right) ---
    _signature_block(img, CX - 1134)
    _identity_block(img, palette, issued, cert_no)
    _qr_block(img, palette, qr_data)
    _footer_strip(img, palette)

    return img


# ============================================================
# Certificate of Participation
# ============================================================

def _participation_motif(img: Image.Image, palette: dict):
    """A faint 'community' network behind the content: a ring of small nodes
    joined by delicate rays, with a warm gold node every fourth place.

    It evokes people coming together without introducing childish graphics -
    the tones stay quiet so the sheet keeps reading as an official document.
    Tints are pre-blended onto the page colour and drawn directly, avoiding a
    full-page RGBA overlay.
    """
    dr = _draw(img)
    bg = _hex(palette.get("page_bg", PAGE_BG))
    cx, cy = CX, 1160
    teal = _hex(TEAL)
    gold = _hex(GOLD_BRIGHT)
    nodes = 12
    radius = 620
    pts = [
        (cx + radius * math.cos(math.radians(-90 + i * (360 / nodes))),
         cy + radius * math.sin(math.radians(-90 + i * (360 / nodes))))
        for i in range(nodes)
    ]
    edge_col = _blend(bg, teal, 24)
    node_col = _blend(bg, teal, 50)
    gold_col = _blend(bg, gold, 70)
    for i in range(nodes):
        dr.line([pts[i], pts[(i + 1) % nodes]], fill=edge_col, width=2)
    for i, (px, py) in enumerate(pts):
        if i % 4 == 3:
            s = 8
            dr.polygon([(px - s, py), (px, py - s), (px + s, py), (px, py + s)], fill=gold_col)
        else:
            dr.ellipse([px - 2, py - 2, px + 2, py + 2], fill=node_col)


@_locked_render
def render_participation_certificate(
    *,
    first_name: str = "",
    last_name: str = "",
    name: str | None = None,
    program_name: str = "",
    certificate_number: str = "",
    issue_date: str = "",
    email: str = "",
    qr_data: str = "",
    logo_bytes: bytes | None = None,
    out_w: int | None = None,
    out_h: int | None = None,
) -> Image.Image:
    """Render the premium A4 Certificate of Participation.

    ``email`` is accepted for parity with the issuance pipeline but is never
    printed on the certificate (privacy).
    """
    palette = dict(PALETTES["base"])
    palette.update(PALETTES["participation"])

    recipient = (name or " ".join(filter(None, (first_name, last_name)))).strip() or "Recipient"
    program = program_name.strip() or "Piplad Welfare Foundation Programme"
    cert_no = certificate_number.strip() or "CERT-YYYY-000000"
    issued = issue_date.strip() or ""

    img = _blank_canvas(palette, out_w, out_h)
    _page_background(img, palette)
    _participation_motif(img, palette)
    _masthead(img, palette, logo_bytes)
    dr = _draw(img)

    # --- Title -----------------------------------------------------------
    _title_block(img, palette, "PARTICIPATION")

    # --- Presentation line ------------------------------------------------
    _presentation_line(img)

    # --- Recipient name (dominant element) --------------------------------
    _recipient_element(img, palette, recipient)

    # --- Achievement block ------------------------------------------------
    lead = sans(44)
    grey = _hex("#3D4A44")
    dr.text((CX, 1396), "In recognition of your active participation in", font=lead, fill=grey, anchor="ma")

    program_font = serif_italic(76, 500)
    program_lines = _wrap_text(dr, program, program_font, 2600)
    pbase = 1580
    if len(program_lines) > 1:
        # Shrink toward a wrapped fit rather than clipping the programme name.
        program_font = serif_italic(60, 500)
        program_lines = _wrap_text(dr, program, program_font, 2600)
        while len(program_lines) > 2 and program_font.size > 48:
            program_font = serif_italic(program_font.size - 4, 500)
            program_lines = _wrap_text(dr, program, program_font, 2600)
        pbase = 1560
    for line in program_lines:
        dr.text((CX, pbase), line, font=program_font, fill=_hex(palette["program_color"]), anchor="ma")
        pbase += 82

    # --- Bottom band: signature (left) / seal+dates (center) / QR (right) ---
    _signature_block(img, CX - 1134)
    _identity_block(img, palette, issued, cert_no)
    _qr_block(img, palette, qr_data)
    _footer_strip(img, palette)

    return img


# ============================================================
# Volunteer ID Card (CR80 wallet size)
# ============================================================
# CR80 card printed at 300 dpi with 3 mm bleed around a 85.6 x 53.98 mm trim.
CARD_TRIM_W = round(85.6 / 25.4 * 300)   # 1011 px trim width
CARD_TRIM_H = round(53.98 / 25.4 * 300)  # 638 px trim height
CARD_BLEED = round(3.0 / 25.4 * 300)     # 35 px bleed (3 mm)
CARD_W = CARD_TRIM_W + 2 * CARD_BLEED    # 1081 px full canvas
CARD_H = CARD_TRIM_H + 2 * CARD_BLEED    # 708 px full canvas
CARD_CX = CARD_W // 2
CARD_L = CARD_BLEED                      # trim left
CARD_T = CARD_BLEED                      # trim top
CARD_R = CARD_W - CARD_BLEED             # trim right
CARD_B = CARD_H - CARD_BLEED             # trim bottom


def _center_square(img: Image.Image) -> Image.Image:
    """Crop the centred square used for the round ID photo (no distortion)."""
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def _card_trim_marks(img: Image.Image, mark):
    """Light crop ticks just outside each trim corner (cut in the bleed)."""
    dr = _draw(img)
    for lx, ty in ((CARD_L, CARD_T), (CARD_R, CARD_T), (CARD_L, CARD_B), (CARD_R, CARD_B)):
        sx = 1 if lx == CARD_L else -1
        sy = 1 if ty == CARD_T else -1
        dr.line([(lx, ty - 12 * sy), (lx, ty + 5 * sy)], fill=mark, width=2)
        dr.line([(lx - 12 * sx, ty), (lx + 5 * sx, ty)], fill=mark, width=2)


def _card_top_band(img: Image.Image, palette: dict, logo_bytes: bytes | None, subtitle: str = "VOLUNTEER IDENTIFICATION CARD"):
    """Deep-green institutional header band (bleed-safe, soft fade into the
    ivory field) carrying the emblem, brand and card-type subtitle."""
    c1, c2 = _hex(GREEN_950), _hex(GREEN_800)
    ivory = (252, 253, 251)
    solid = CARD_T + 132
    fade = 24
    band = _draw(img)
    for y in range(solid + fade):
        if y < solid:
            t = y / max(solid - 1, 1)
            row = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        else:
            t = (y - solid) / fade
            row = tuple(int(c2[i] + (ivory[i] - c2[i]) * t) for i in range(3))
        band.line([(0, y), (CARD_W, y)], fill=row)

    if logo_bytes:
        import io

        try:
            # Opened lazily; _paste_emblem shrinks it before decoding.
            logo = Image.open(io.BytesIO(logo_bytes))
            _paste_emblem(img, logo, CARD_L + 54, CARD_T + 72, 50, GOLD_BRIGHT)
        except Exception:  # noqa: BLE001 - logo must never break rendering
            pass

    dr = _draw(img)
    _draw_tracked(dr, CARD_L + 96, CARD_T + 56, "PIPLAD WELFARE FOUNDATION", sans(20, 700), (255, 255, 255), tracking=5, anchor="ls")
    if subtitle:
        _draw_tracked(dr, CARD_L + 97, CARD_T + 94, subtitle, sans(11, 700), _hex("#DDEBE6"), tracking=4, anchor="ls")


def _id_qr_zone(img: Image.Image, palette: dict, right: float, top: float, bottom: float, qr_data: str, label: str, max_w: float = 290):
    """Design-integrated QR: no box, sits flush on the card below a tracked
    label, with the short verify URL right-aligned beneath."""
    dr = _draw(img)
    right = int(right)
    _draw_tracked(dr, right, top + 24, label, sans(13, 700), _hex(GREEN_800), tracking=4, anchor="rs")

    if qr_data:
        avail = min(int(bottom - top - 96), int(max_w) - 4)
        qr = _qr_image(qr_data, target=avail, border=4)
        qy = top + 46 + (int(bottom - top - 96) - qr.height) // 2
        img.paste(qr, (right - qr.width, qy), qr)
    else:
        dr.text((right - 120, top + 130), "QR", font=sans(26), fill=_hex(MUTED), anchor="rs")

    url_font = sans(10)
    url_lines = _wrap_text(dr, qr_data, url_font, int(max_w) - 10)[:2] if qr_data else []
    base = bottom - 24
    for line in reversed(url_lines):
        dr.text((right, base), line, font=url_font, fill=_hex(MUTED), anchor="rs")
        base -= 16


def _paste_card_photo(img: Image.Image, photo, center, diameter: int, initials: str):
    """Consistent centre-square-cropped photo in a rounded institutional frame;
    a serif monogram fills the frame when no photo is available."""
    import io

    d = diameter
    pad = 4
    canvas = Image.new("RGBA", (d + pad, d + pad), (0, 0, 0, 0))
    mask = Image.new("L", (d + pad, d + pad), 0)
    ImageDraw.Draw(mask).rounded_rectangle([2, 2, d + 1, d + 1], radius=14, fill=255)

    if photo is not None:
        stream = None
        try:
            if isinstance(photo, bytes):
                stream = io.BytesIO(photo)
                photo = Image.open(stream)
            # Shrink before decoding: the pasted image is only `d` px after the
            # centre-square crop, so holding the photo at native resolution is
            # pure memory waste on the small Render worker.
            if min(photo.size) > d * 3:
                photo.thumbnail((d * 3, d * 3), Image.LANCZOS)
            photo_rgb = photo.convert("RGB")
            square = _center_square(photo_rgb).resize((d, d), Image.LANCZOS)
            canvas.paste(square, (2, 2))
            square.close()
            photo_rgb.close()
            photo.close()
            if stream is not None:
                stream.close()
        except Exception:  # noqa: BLE001 - photo must never break rendering
            photo = None
    if photo is None:
        ImageDraw.Draw(canvas).rounded_rectangle([2, 2, d + 1, d + 1], radius=14, fill=_hex("#F2EFE6"))
        monogram = (initials or "P").upper()[:2]
        mfont = serif(52, 800)
        ImageDraw.Draw(canvas).text((d / 2 + 2, d / 2 + 2), monogram, font=mfont, fill=_hex(GREEN_800), anchor="mm")

    ring_draw = ImageDraw.Draw(canvas)
    ring_draw.rounded_rectangle([0, 0, d + pad - 1, d + pad - 1], radius=16, outline=_hex(GOLD_BRIGHT), width=2)
    ring_draw.rounded_rectangle([5, 5, d + pad - 6, d + pad - 6], radius=12, outline=(255, 255, 255, 235), width=1)
    img.paste(canvas, (int(center[0] - (d + pad) / 2), int(center[1] - (d + pad) / 2)), canvas)


@_locked_render
def render_volunteer_card_front(
    *,
    name: str = "",
    volunteer_id: str = "",
    designation: str = "",
    joining_date: str = "",
    email: str = "",
    phone: str = "",
    status: str = "",
    photo=None,
    qr_data: str = "",
    logo_bytes: bytes | None = None,
) -> Image.Image:
    """Front of the CR80 volunteer ID card: deep-green header band over an
    ivory field with photo, identity and a flush verification code."""
    palette = dict(PALETTES["base"])
    palette.update({
        "primary": GREEN_800,
        "accent": GOLD_BRIGHT,
        "motif_color": TEAL,
    })

    full_name = (name or "Volunteer").strip()
    vol_id = volunteer_id.strip() or "PWF-VOL-0000"
    designation = (designation or "Volunteer").strip()
    joining_date = joining_date.strip()

    img = Image.new("RGB", (CARD_W, CARD_H), _hex("#FCFDFB"))
    img._canvas_design = (CARD_W, CARD_H)
    _card_top_band(img, palette, logo_bytes)

    dr = _draw(img)
    green_ink = _hex(GREEN_950)
    muted = _hex(MUTED)

    # --- Photo ------------------------------------------------------------
    initials = "".join(w[0] for w in full_name.split()[:2])
    _paste_card_photo(img, photo, (CARD_L + 150, CARD_T + 225), 130, initials)

    # --- Identity block ----------------------------------------------------
    x = CARD_L + 250
    _draw_tracked(dr, x, CARD_T + 200, "VOLUNTEER", sans(13, 700), _hex(GOLD), tracking=6, anchor="ls")
    name_font = serif(46, 800)
    if dr.textlength(full_name, font=name_font) > 445:
        name_font = serif(int(46 * 445 / dr.textlength(full_name, font=name_font)), 800)
    dr.text((x, CARD_T + 252), full_name, font=name_font, fill=green_ink, anchor="ls")
    deg_font = serif_italic(21)
    if dr.textlength(designation, font=deg_font) > 420:
        deg_font = serif_italic(int(21 * 420 / dr.textlength(designation, font=deg_font)))
    dr.text((x, CARD_T + 300), designation, font=deg_font, fill=muted, anchor="ls")

    # --- Header fields ------------------------------------------------------
    fx = CARD_L + 102
    label_font = sans(12, 700)
    value_font = sans(20, 700)
    _draw_tracked(dr, fx, CARD_T + 400, "VOLUNTEER ID", label_font, muted, tracking=3, anchor="ls")
    dr.text((fx, CARD_T + 432), vol_id, font=value_font, fill=green_ink, anchor="ls")
    _draw_tracked(dr, fx, CARD_T + 490, "JOINING DATE", label_font, muted, tracking=3, anchor="ls")
    dr.text((fx, CARD_T + 522), joining_date or "", font=value_font, fill=green_ink, anchor="ls")

    # --- Verification column (flush, bottom right) ----------------------------
    _id_qr_zone(img, palette, CARD_R - 22, CARD_T + 352, CARD_B - 42, qr_data, "SCAN TO VERIFY", max_w=288)

    # --- Tagline ---------------------------------------------------------------
    _draw_tracked(
        dr, CARD_CX, CARD_B - 16, "Transforming Lives Through Compassion & Service",
        sans(10, 600), muted, tracking=2,
    )
    _card_trim_marks(img, (196, 202, 198))
    return img


@_locked_render
def render_volunteer_card_back(
    *,
    name: str = "",
    volunteer_id: str = "",
    designation: str = "",
    joining_date: str = "",
    email: str = "",
    phone: str = "",
    status: str = "",
    photo=None,
    qr_data: str = "",
    logo_bytes: bytes | None = None,
) -> Image.Image:
    """Back of the CR80 volunteer ID card: matching header band, a soft data
    panel of labelled fields and a large flush verification code."""
    palette = dict(PALETTES["base"])
    palette.update({
        "primary": GREEN_800,
        "accent": GOLD_BRIGHT,
        "motif_color": TEAL,
    })

    full_name = (name or "Volunteer").strip()
    vol_id = volunteer_id.strip() or "PWF-VOL-0000"
    status_text = (status or "issued").strip().title() or "Issued"

    img = Image.new("RGB", (CARD_W, CARD_H), _hex("#FCFDFB"))
    img._canvas_design = (CARD_W, CARD_H)
    _card_top_band(img, palette, logo_bytes)

    dr = _draw(img)
    green_ink = _hex(GREEN_950)
    muted = _hex(MUTED)

    # --- Soft data panel -----------------------------------------------------
    px0, py0 = CARD_L + 40, CARD_T + 210
    px1, py1 = CARD_R - 300, CARD_B - 52
    dr.rounded_rectangle([px0, py0, px1, py1], radius=18, fill=_hex("#EFF4EF"))

    label_font = sans(11, 700)
    value_font = sans(20, 700)
    rows = [
        ("NAME", full_name),
        ("VOLUNTEER ID", vol_id),
        ("EMAIL", email.strip()),
        ("CONTACT", phone.strip()),
        ("JOINING DATE", joining_date.strip()),
        ("STATUS", status_text),
    ]
    x = CARD_L + 70
    y = CARD_T + 217
    for label, value in rows:
        _draw_tracked(dr, x, y, label, label_font, muted, tracking=3, anchor="ls")
        vfont = value_font
        if dr.textlength(value or " ", font=vfont) > 610:
            vfont = sans(int(20 * 610 / max(dr.textlength(value, font=vfont), 1)), 700)
        status_ok = label == "STATUS" and status_text.lower() in ("active", "issued", "accepted")
        if label == "STATUS":
            dot_col = _hex(GREEN_800 if status_ok else AMBER)
            dr.ellipse([x, y + 24, x + 10, y + 34], fill=dot_col)
            dr.text((x + 22, y + 34), value, font=vfont, fill=dot_col, anchor="ls")
        else:
            dr.text((x, y + 30), value, font=vfont, fill=green_ink, anchor="ls")
        y += 62

    # --- Verification column (flush, right) ----------------------------------
    _id_qr_zone(img, palette, CARD_R - 22, CARD_T + 170, CARD_B - 42, qr_data, "VERIFICATION", max_w=258)

    # --- Tagline ---------------------------------------------------------------
    _draw_tracked(
        dr, CARD_CX, CARD_B - 16, "Transforming Lives Through Compassion & Service",
        sans(10, 600), muted, tracking=2,
    )
    _card_trim_marks(img, (196, 202, 198))
    return img


# ============================================================
# Public dispatch & serialization
# ============================================================

@_locked_render
def render_certificate(
    cert_type: str,
    *,
    out_w: int | None = None,
    out_h: int | None = None,
    **fields,
) -> Image.Image:
    """Render any registered certificate type (reusable dispatch).

    ``out_w`` / ``out_h`` override the default clean-master resolution, e.g.
    for a lower-resolution/preview render.
    """
    factory = {
        "appreciation": render_appreciation_certificate,
        "internship": render_internship_certificate,
        "completion": render_completion_certificate,
        "participation": render_participation_certificate,
    }
    if cert_type not in factory:
        raise NotImplementedError(
            f"Certificate type {cert_type!r} is not implemented yet. "
            "Register it in FOUNDATION_CERT_TYPES to reuse this design system."
        )
    return factory[cert_type](out_w=out_w, out_h=out_h, **fields)


FOUNDATION_CERT_TYPES = ("appreciation", "internship", "completion", "participation")


def jpeg_bytes(image: Image.Image, quality: int = 95) -> bytes:
    """Serialize a rendered canvas to print-quality JPEG bytes."""
    import io

    buffer = io.BytesIO()
    out = image if image.mode == "RGB" else image.convert("RGB")
    out.save(buffer, format="JPEG", quality=quality, optimize=True, dpi=(140, 140))
    data = buffer.getvalue()
    buffer.close()
    return data