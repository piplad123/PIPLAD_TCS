"""PDF export for rendered certificate/card JPEG images.

Converts a rendered JPEG into a single A4 PDF page (landscape for
certificates, portrait for cards) using ReportLab, so documents can be
emailed, archived or downloaded alongside the JPEG version.
"""

import io
import logging

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas

logger = logging.getLogger(__name__)

MARGIN = 4


def jpeg_to_pdf_bytes(
    jpeg_bytes: bytes,
    *,
    landscape_page: bool = True,
    title: str = "Piplad Welfare Foundation",
) -> bytes:
    """Return A4 PDF bytes containing the single JPEG scaled to fit."""
    buffer = io.BytesIO()
    stream = io.BytesIO(jpeg_bytes)
    page = landscape(A4) if landscape_page else A4
    c = pdf_canvas.Canvas(buffer, pagesize=page)
    c.setTitle(title)
    try:
        image = ImageReader(stream)
        iw, ih = image.getSize()
    except Exception as exc:  # noqa: BLE001 - surface as a clean PDF failure
        stream.close()
        logger.error("Could not read JPEG for PDF export: %s", exc)
        raise ValueError("JPEG could not be embedded in the PDF") from exc

    pw, ph = page
    draw_w = pw - 2 * MARGIN
    draw_h = ph - 2 * MARGIN
    scale = min(draw_w / iw, draw_h / ih)
    final_w = iw * scale
    final_h = ih * scale
    x = (pw - final_w) / 2
    y = (ph - final_h) / 2
    c.drawImage(image, x, y, final_w, final_h)
    c.showPage()
    c.save()
    # Free the embedded JPEG source and the output stream explicitly.
    del image
    stream.close()
    return buffer.getvalue()


def document_pdf_bytes(
    jpeg_bytes: bytes,
    *,
    orientation: str = "landscape",
    title: str = "Piplad Welfare Foundation",
) -> bytes:
    """Convenience wrapper choosing page orientation by document geometry.

    ``orientation`` is ``landscape`` (certificates) or ``portrait`` (cards).
    """
    landscape_page = orientation != "portrait"
    return jpeg_to_pdf_bytes(
        jpeg_bytes,
        landscape_page=landscape_page,
        title=title,
    )


def id_card_pdf_bytes(
    front_jpeg: bytes,
    back_jpeg: bytes | None = None,
    *,
    title: str = "Piplad Welfare Foundation Volunteer ID Card",
) -> bytes:
    """Return a CR80-size PDF (card + 3 mm bleed) for double-sided printing.

    Each page is exactly the rendered card canvas in physical size, so the
    file prints at real ID-card dimensions; the corner crop marks baked into
    the images define the 85.6 x 53.98 mm trim line.
    """
    buffer = io.BytesIO()
    c = pdf_canvas.Canvas(buffer)
    c.setTitle(title)
    for jpeg in (front_jpeg, back_jpeg):
        if not jpeg:
            continue
        stream = io.BytesIO(jpeg)
        image = ImageReader(stream)
        iw, ih = image.getSize()
        page_w = iw / 300 * 72
        page_h = ih / 300 * 72
        c.setPageSize((page_w, page_h))
        c.drawImage(image, 0, 0, page_w, page_h)
        c.showPage()
        del image
        stream.close()
    c.save()
    return buffer.getvalue()