"""Donation receipt PDF generator using ReportLab.

Generates a single document:

1. Donation receipt (80G)   (A4 portrait)

Returns the raw PDF bytes so the caller can attach them to an email without
writing to disk.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdf_canvas

ORG_NAME = "Piplad Welfare Foundation"
ORG_TAGLINE = "Creating Opportunities, Creating Lives"
ORG_DETAILS = (
    "Registered under the Indian Trusts Act. Donations are eligible for "
    "50% deduction under Section 80G of the Income Tax Act, 1961."
)

EMERALD = colors.HexColor("#059669")
LIME = colors.HexColor("#65a30d")
SLATE = colors.HexColor("#0f172a")
SLATE_LIGHT = colors.HexColor("#64748b")
GOLD = colors.HexColor("#ca8a04")

_LOGO_CANDIDATES = [
    Path(__file__).resolve().parents[2] / "frontend" / "public" / "piplad-logo.png",
    Path(__file__).resolve().parents[1] / "media" / "brand" / "piplad-logo.png",
]

_FONT_CANDIDATES_NORMAL = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
]

_FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
]

_FONT_NAME = "AppFont"
_FONT_BOLD = "AppFont-Bold"

_FONT_RESOLVED = {}


def _register_font(name: str, candidates: list[str], fallback: str) -> None:
    for path in candidates:
        if Path(path).is_file():
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                _FONT_RESOLVED[name] = name
                return
            except Exception:
                continue
    # Built-in font fallback (Helvetica family) - no registration required.
    _FONT_RESOLVED[name] = fallback


def _init_fonts() -> None:
    if _FONT_RESOLVED:
        return
    _register_font(_FONT_NAME, _FONT_CANDIDATES_NORMAL, "Helvetica")
    _register_font(_FONT_BOLD, _FONT_CANDIDATES_BOLD, "Helvetica-Bold")


def _font() -> str:
    _init_fonts()
    return _FONT_RESOLVED.get(_FONT_NAME, "Helvetica")


def _font_bold() -> str:
    _init_fonts()
    return _FONT_RESOLVED.get(_FONT_BOLD, "Helvetica-Bold")


def _logo_path() -> Path | None:
    for candidate in _LOGO_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _draw_logo(c: pdf_canvas.Canvas, width: float, y: float, max_height: float = 34) -> None:
    logo = _logo_path()
    if not logo:
        return
    try:
        from reportlab.lib.utils import ImageReader

        image = ImageReader(str(logo))
        iw, ih = image.getSize()
        scale = min(max_height / ih, 90 / iw)
        draw_w = iw * scale
        draw_h = ih * scale
        c.drawImage(image, (width - draw_w) / 2, y - draw_h, draw_w, draw_h, mask="auto")
    except Exception:
        return


def _format_amount(amount) -> str:
    try:
        return f"Inr {float(amount):,.2f}"
    except (TypeError, ValueError):
        return "Inr 0.00"


def _format_date(value) -> str:
    if not value:
        return datetime.utcnow().strftime("%d %B %Y")
    if isinstance(value, datetime):
        return value.strftime("%d %B %Y")
    return str(value)


def _clean(value) -> str:
    """Safely render user-provided text without quote/double-escape issues."""
    return str(value or "").replace("\n", " ").strip()


def build_donation_receipt_pdf(
    *,
    full_name: str,
    email: str,
    phone: str = "",
    amount,
    order_id: str = "",
    payment_id: str = "",
    paid_at=None,
) -> bytes:
    """Generate an A4 portrait 80G donation receipt PDF."""
    from io import BytesIO

    _init_fonts()
    width, height = A4
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=(width, height))
    c.setTitle("Donation Receipt - Piplad Welfare Foundation")

    # Header band
    c.setFillColor(SLATE)
    c.rect(0, height - 110, width, 110, stroke=0, fill=1)
    _draw_logo(c, width, height - 34, max_height=26)
    c.setFont(_font_bold(), 18)
    c.setFillColor(colors.HexColor("#a3e635"))
    c.drawCentredString(width / 2, height - 46, ORG_NAME)
    c.setFont(_font(), 9)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawCentredString(width / 2, height - 60, ORG_TAGLINE)

    c.setFont(_font_bold(), 15)
    c.setFillColor(GOLD)
    c.drawCentredString(width / 2, height - 92, "DONATION RECEIPT")

    # Title
    c.setFont(_font_bold(), 20)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, height - 142, "Thank you for your donation!")

    c.setFont(_font(), 10)
    c.setFillColor(SLATE_LIGHT)
    c.drawCentredString(width / 2, height - 160, "This receipt acknowledges your donation to the Piplad Welfare Foundation.")

    # Details table
    left = 60
    top = height - 180
    col_width = width - 120
    row_height = 40
    labels = [
        ("Donor Name", _clean(full_name)),
        ("Donor Email", _clean(email)),
        ("Donor Phone", _clean(phone) or "-"),
        ("Amount Donated", _format_amount(amount)),
        ("Date", _format_date(paid_at)),
        ("Transaction ID", _clean(payment_id) or "N/A"),
        ("Order / Reference ID", _clean(order_id) or "N/A"),
    ]

    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(left, top - row_height * len(labels), col_width, row_height * len(labels), stroke=0, fill=1)
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setLineWidth(0.6)

    for index, (label, value) in enumerate(labels):
        y = top - index * row_height
        c.roundRect(left, y - row_height, col_width, row_height, 0, stroke=1, fill=0)
        c.setFont(_font_bold(), 9)
        c.setFillColor(SLATE_LIGHT)
        c.drawString(left + 14, y - row_height + 12, label.upper())
        c.setFont(_font(), 11)
        c.setFillColor(SLATE)
        value_display = value
        if value_display and c.stringWidth(value_display, _font(), 11) > col_width - 30:
            value_display = value_display[:60] + "..."
        c.drawRightString(left + col_width - 14, y - row_height + 24, value_display)
        if label == "Amount Donated":
            c.setFont(_font_bold(), 13)
            c.setFillColor(EMERALD)

    # Legal note
    note_y = top - row_height * len(labels) - 24
    c.setFont(_font(), 9)
    c.setFillColor(SLATE_LIGHT)
    text = (
        f"This is a system-generated receipt. {ORG_DETAILS} "
        "Kindly keep this receipt and your payment transaction reference for your records."
    )
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if c.stringWidth(candidate, _font(), 9) < width - 120:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    for line in lines:
        c.drawCentredString(width / 2, note_y, line)
        note_y -= 13

    c.setFillColor(SLATE_LIGHT)
    c.setFont(_font(), 8)
    c.drawCentredString(width / 2, 40, f"{ORG_NAME}  |  {ORG_TAGLINE}")

    c.showPage()
    c.save()
    return buffer.getvalue()