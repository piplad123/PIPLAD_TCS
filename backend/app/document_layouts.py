"""Document layout coordinates for the official Piplad templates.

Single source of truth for where each dynamic field is stamped onto:

* the 4 official certificate backgrounds (1536 x 1024 landscape) and
* the official volunteer ID card background (1388 x 1133 portrait).

All pixel coordinates come from ``app/template_coordinates.py`` (the spec
from ``coordinates.json``). Official documents render onto committed *clean
master templates* on which every placeholder / stock QR / stock photo has
already been removed once, so the runtime layouts contain NO erase boxes -
dynamic data is simply drawn over the blank areas.
"""

from . import template_coordinates

# Official volunteer ID card background (clean master template).
VOLUNTEER_CARD_IMAGE = template_coordinates.CLEAN_VOLUNTEER_CARD

# Official certificate backgrounds, keyed by certificate document type.
CERTIFICATE_IMAGES = dict(template_coordinates.CLEAN_CERTIFICATE_TEMPLATES)

# Valid certificate document types that can be issued through the generator.
CERTIFICATE_TYPES = tuple(CERTIFICATE_IMAGES.keys())

# CertificateTemplate slug used when seeding / resolving each certificate type.
CERTIFICATE_TEMPLATE_SLUGS = {
    "appreciation": "certificate-of-appreciation",
    "completion": "certificate-of-completion",
    "internship": "certificate-of-internship",
    "participation": "certificate-of-participation",
}

# Human-facing label used in the admin generator dropdowns.
CERTIFICATE_LABELS = {
    "appreciation": "Certificate of Appreciation",
    "completion": "Certificate of Completion",
    "internship": "Certificate of Internship",
    "participation": "Certificate of Participation",
}

DOCUMENT_LAYOUTS = {}


def layout_for(document_type: str) -> dict:
    """Return a deep-copied layout dict for a document type (safe to mutate)."""
    import copy

    if not DOCUMENT_LAYOUTS:
        _build_layouts()
    return copy.deepcopy(DOCUMENT_LAYOUTS[document_type])


def _build_layouts() -> None:
    for doc_type in CERTIFICATE_TYPES:
        DOCUMENT_LAYOUTS[doc_type] = template_coordinates.certificate_layout(doc_type)
    DOCUMENT_LAYOUTS["volunteer"] = template_coordinates.volunteer_layout()