"""Official coordinates + master-template metadata (from the Piplad spec).

This module is the single source of truth for where dynamic content is
stamped onto the 4 official certificates (1536 x 1024) and the official
volunteer ID card composite (1388 x 1133, front x~0-678 / back x~690-1388).

The spec was provided as ``coordinates.json`` (analyst-measured, top-left
origin, source-pixel units). It is used for two purposes:

* building the *clean master templates* on which the old placeholders /
  stock QR / stock photo have been removed once (scripts/
  clean_document_templates.py), and
* building the runtime render layouts (app/document_layouts.py) that paint
  only dynamic data at render time. No runtime erase happens for official
  documents; layouts simply have no ``box``.

The volunteer card BACK side is deliberately absent here: per the spec it is
``UNCHANGED`` - never erased, redrawn or QR-regenerated.
"""

# Source templates, keyed by certificate document type (cleaning/calibration tools).
SOURCE_CERTIFICATE_TEMPLATES = {
    "participation": "certificate_templates/Certificate of Participation.jpeg",
    "appreciation": "certificate_templates/Certificate of Appriciation.png",
    "completion": "certificate_templates/Certificate of Completion.png",
    "internship": "certificate_templates/Certificate of Internship.png",
}

SOURCE_VOLUNTEER_CARD = "certificate_templates/volunteer card.png"

# Clean master templates (committed under media so both the media-URL loading
# path and the paste/erase preview tooling can resolve them).
CLEAN_CERTIFICATE_TEMPLATES = {
    "participation": "certificate_templates/clean/certificate_participation_clean.png",
    "appreciation": "certificate_templates/clean/certificate_appreciation_clean.png",
    "completion": "certificate_templates/clean/certificate_completion_clean.png",
    "internship": "certificate_templates/clean/certificate_internship_clean.png",
}

CLEAN_VOLUNTEER_CARD = "certificate_templates/clean/volunteer_card_clean.png"

# Per-certificate field coordinates from the spec (erase box + draw anchor).
# ``key`` is the runtime layout key; ``spec`` is the source field name.
_CERT = {
    "participation": {
        "name": {"spec": "name", "color": "#1f2937"},
        "program_name": {"spec": "program_name", "color": "#334155"},
        "competition_date": {"spec": "date", "color": "#475569"},
        "competition_location": {"spec": "location", "color": "#475569"},
        "certificate_number": {"spec": "certificate_number", "color": "#475569"},
        "issue_date": {"spec": "issue_date", "color": "#475569"},
    },
    "appreciation": {
        "name": {"spec": "name", "color": "#1f2937"},
        "program_name": {"spec": "program_name", "color": "#334155"},
        "certificate_number": {"spec": "certificate_number", "color": "#475569"},
        "issue_date": {"spec": "issue_date", "color": "#475569"},
    },
    "completion": {
        "name": {"spec": "name", "color": "#1f2937"},
        "program_name": {"spec": "program_name", "color": "#334155"},
        "organisation_name": {"spec": "organisation_name", "color": "#475569"},
        "competition_date": {"spec": "date", "color": "#475569"},
        "competition_location": {"spec": "location", "color": "#475569"},
        "certificate_number": {"spec": "certificate_number", "color": "#475569"},
        "issue_date": {"spec": "issue_date", "color": "#475569"},
    },
    "internship": {
        "name": {"spec": "name", "color": "#1f2937"},
        "starting_date": {"spec": "starting_date", "color": "#475569"},
        "end_date": {"spec": "end_date", "color": "#475569"},
        "program_name": {"spec": "program_name", "color": "#334155"},
        "certificate_number": {"spec": "certificate_number", "color": "#475569"},
        "issue_date": {"spec": "issue_date", "color": "#475569"},
    },
}

# Spec field coordinate dicts (transcribed from coordinates.json).
_FIELD_COORDS = {
    "participation": {
        "name": {
            "erase_box": [430, 388, 1115, 462],
            "anchor": [768, 425], "font_size": 52, "max_width": 760,
            "align": "center",
        },
        "program_name": {
            "erase_box": [570, 535, 965, 592],
            "anchor": [768, 564], "font_size": 24, "max_width": 760,
            "align": "center",
        },
        "date": {
            "erase_box": [632, 645, 736, 685],
            "anchor": [684, 665], "font_size": 20, "max_width": 110,
            "align": "center",
        },
        "location": {
            "erase_box": [766, 645, 956, 685],
            "anchor": [861, 665], "font_size": 20, "max_width": 190,
            "align": "center",
        },
        "certificate_number": {
            "erase_box": [298, 731, 515, 760],
            "anchor": [407, 746], "font_size": 18, "max_width": 215,
            "align": "left",
        },
        "issue_date": {
            "erase_box": [204, 775, 398, 802],
            "anchor": [301, 789], "font_size": 18, "max_width": 195,
            "align": "left",
        },
        "qr": {
            "erase_box": [1330, 760, 1460, 887],
            "paste_box": [1336, 766, 1452, 882],
            "anchor": [1394, 824], "size": 116,
        },
    },
    "appreciation": {
        "name": {
            "erase_box": [420, 390, 1135, 464],
            "anchor": [775, 427], "font_size": 52, "max_width": 800,
            "align": "center",
        },
        "program_name": {
            "erase_box": [540, 585, 995, 632],
            "anchor": [768, 609], "font_size": 24, "max_width": 455,
            "align": "center",
        },
        "certificate_number": {
            "erase_box": [296, 727, 505, 754],
            "anchor": [400, 741], "font_size": 18, "max_width": 210,
            "align": "left",
        },
        "issue_date": {
            "erase_box": [201, 767, 430, 794],
            "anchor": [315, 781], "font_size": 18, "max_width": 230,
            "align": "left",
        },
        "qr": {
            "erase_box": [1330, 762, 1460, 889],
            "paste_box": [1339, 769, 1451, 881],
            "anchor": [1395, 825], "size": 112,
        },
    },
    "completion": {
        "name": {
            "erase_box": [420, 383, 1125, 472],
            "anchor": [773, 428], "font_size": 52, "max_width": 800,
            "align": "center",
        },
        "program_name": {
            "erase_box": [338, 540, 668, 572],
            "anchor": [503, 556], "font_size": 24, "max_width": 330,
            "align": "center",
        },
        "organisation_name": {
            "erase_box": [570, 589, 926, 626],
            "anchor": [748, 607], "font_size": 20, "max_width": 350,
            "align": "center",
        },
        "date": {
            "erase_box": [970, 590, 1060, 626],
            "anchor": [1015, 608], "font_size": 20, "max_width": 90,
            "align": "center",
        },
        "location": {
            "erase_box": [1095, 590, 1275, 626],
            "anchor": [1185, 608], "font_size": 20, "max_width": 180,
            "align": "center",
        },
        "certificate_number": {
            "erase_box": [298, 721, 510, 749],
            "anchor": [404, 736], "font_size": 18, "max_width": 212,
            "align": "left",
        },
        "issue_date": {
            "erase_box": [204, 768, 430, 796],
            "anchor": [317, 783], "font_size": 18, "max_width": 226,
            "align": "left",
        },
        "qr": {
            "erase_box": [1330, 759, 1460, 888],
            "paste_box": [1338, 766, 1454, 882],
            "anchor": [1396, 824], "size": 116,
        },
    },
    "internship": {
        "name": {
            "erase_box": [425, 385, 1128, 468],
            "anchor": [777, 426], "font_size": 52, "max_width": 800,
            "align": "center",
        },
        "starting_date": {
            "erase_box": [778, 550, 1040, 588],
            "anchor": [909, 569], "font_size": 20, "max_width": 260,
            "align": "center",
        },
        "end_date": {
            "erase_box": [1080, 550, 1258, 588],
            "anchor": [1169, 569], "font_size": 20, "max_width": 178,
            "align": "center",
        },
        "program_name": {
            "erase_box": [535, 645, 850, 684],
            "anchor": [693, 664], "font_size": 20, "max_width": 315,
            "align": "center",
        },
        "certificate_number": {
            "erase_box": [295, 722, 505, 750],
            "anchor": [400, 737], "font_size": 18, "max_width": 210,
            "align": "left",
        },
        "issue_date": {
            "erase_box": [202, 765, 430, 792],
            "anchor": [316, 779], "font_size": 18, "max_width": 228,
            "align": "left",
        },
        "qr": {
            "erase_box": [1329, 760, 1460, 887],
            "paste_box": [1336, 767, 1452, 879],
            "anchor": [1394, 823], "size": 112,
        },
    },
}

# Volunteer card FRONT dynamic fields (back untouched by design).
_VOLUNTEER_FRONT = {
    "photo": {
        "template_box": [210, 218, 465, 465],
        "anchor": [337, 342], "size": [250, 245], "fit": "cover",
        "shape": "rounded_rectangle", "color": None,
    },
    "name": {
        "erase_box": [108, 482, 580, 530],
        "anchor": [344, 507], "font_size": 32, "max_width": 480,
        "align": "center", "color": "#1f2937",
    },
    "position": {
        "erase_box": [270, 526, 420, 561],
        "anchor": [345, 544], "font_size": 22, "max_width": 190,
        "align": "center", "color": "#475569",
    },
    "piplad_id": {
        "erase_box": [150, 564, 530, 616],
        "anchor": [340, 590], "font_size": 21, "max_width": 340,
        "align": "center", "color": "#ffffff",
    },
    "programme": {
        "erase_box": [326, 649, 565, 684],
        "anchor": [446, 667], "font_size": 18, "max_width": 235,
        "align": "left", "color": "#1f2937",
    },
    "location": {
        "erase_box": [326, 704, 565, 741],
        "anchor": [446, 722], "font_size": 18, "max_width": 235,
        "align": "left", "color": "#1f2937",
    },
    "valid_till": {
        "erase_box": [326, 758, 565, 795],
        "anchor": [446, 777], "font_size": 18, "max_width": 235,
        "align": "left", "color": "#1f2937",
    },
    "qr": {
        "erase_box": [272, 819, 405, 947],
        "paste_box": [278, 825, 400, 943],
        "anchor": [339, 884], "size": 118,
    },
}

# Certificate layout key -> spec source field name.
_CERT_KEYS = {
    doc_type: {layout_key: meta["spec"] for layout_key, meta in fields.items()}
    for doc_type, fields in _CERT.items()
}

_VOLUNTEER_KEYS = {
    "name": "name",
    "position": "position",
    "volunteer_id": "piplad_id",
    "programme": "programme",
    "location": "location",
    "valid_till": "valid_till",
}

_VOL_FIELD_COLOR = {
    "name": "#1f2937",
    "position": "#475569",
    "volunteer_id": "#ffffff",
    "programme": "#1f2937",
    "location": "#1f2937",
    "valid_till": "#1f2937",
}

_VOL_FIELD_ALIGN = {
    "name": "center",
    "position": "center",
    "volunteer_id": "center",
    "programme": "left",
    "location": "left",
    "valid_till": "left",
}

_VOL_FIELD_SIZE = {
    "name": 32,
    "position": 22,
    "volunteer_id": 21,
    "programme": 18,
    "location": 18,
    "valid_till": 18,
}

_VOL_FIELD_MAXW = {
    "name": 480,
    "position": 190,
    "volunteer_id": 340,
    "programme": 235,
    "location": 235,
    "valid_till": 235,
}


def _align_anchor(align: str) -> str:
    """Map the spec's textual alignment to a PIL text anchor."""
    return "mm" if align == "center" else "lm"


def certificate_layout(document_type: str) -> dict:
    """Runtime render layout (no erase boxes) for a certificate type."""
    layout = {}
    for layout_key in _CERT_KEYS[document_type]:
        layout[layout_key] = _text_anchor(
            document_type, _CERT_KEYS[document_type][layout_key], _CERT[document_type][layout_key]["color"]
        )
    layout["qr"] = _qr_anchor(_FIELD_COORDS[document_type]["qr"])
    return layout


def volunteer_layout() -> dict:
    """Runtime render layout for the volunteer card front."""
    layout = {}
    for layout_key in _VOLUNTEER_KEYS:
        layout[layout_key] = {
            "x": _VOLUNTEER_FRONT[_VOLUNTEER_KEYS[layout_key]]["anchor"][0],
            "y": _VOLUNTEER_FRONT[_VOLUNTEER_KEYS[layout_key]]["anchor"][1],
            "font_size": _VOL_FIELD_SIZE[layout_key],
            "max_width": _VOL_FIELD_MAXW[layout_key],
            "color": _VOL_FIELD_COLOR[layout_key],
            "anchor": _align_anchor(_VOL_FIELD_ALIGN[layout_key]),
        }
    photo = _VOLUNTEER_FRONT["photo"]
    layout["photo"] = {
        "x": photo["anchor"][0],
        "y": photo["anchor"][1],
        "size": list(photo["size"]),
        "anchor": "mm",
        "role": "photo",
        "fit": photo.get("fit", "cover"),
        "shape": photo.get("shape", "rounded_rectangle"),
    }
    layout["qr"] = _qr_anchor(_VOLUNTEER_FRONT["qr"])
    return layout


def _text_anchor(document_type: str, spec_field: str, color: str) -> dict:
    coord = _FIELD_COORDS[document_type][spec_field]
    return {
        "x": coord["anchor"][0],
        "y": coord["anchor"][1],
        "font_size": coord.get("font_size", 20),
        "max_width": coord.get("max_width", 300),
        "color": color,
        "anchor": _align_anchor(coord.get("align", "center")),
    }


def _qr_anchor(coord: dict) -> dict:
    return {
        "x": coord["anchor"][0],
        "y": coord["anchor"][1],
        "size": coord.get("size", 112),
        "anchor": "mm",
    }


def erase_boxes(document_type: str) -> list[tuple[int, int, int, int]]:
    """Erase boxes (left, top, right, bottom) to clear on the master template."""
    boxes = []
    for layout_key in _CERT_KEYS.get(document_type, {}):
        spec_field = _CERT_KEYS[document_type][layout_key]
        boxes.append(
            tuple(int(v) for v in _FIELD_COORDS[document_type][spec_field]["erase_box"])
        )
    boxes.append(
        tuple(int(v) for v in _FIELD_COORDS[document_type]["qr"]["erase_box"])
    )
    return boxes


def volunteer_front_erase_boxes() -> list[tuple[int, int, int, int]]:
    """Erase boxes for the volunteer card FRONT only."""
    boxes = [tuple(int(v) for v in _VOLUNTEER_FRONT["photo"]["template_box"])]
    for spec_field in (
        "name", "position", "piplad_id", "programme", "location", "valid_till", "qr",
    ):
        boxes.append(
            tuple(int(v) for v in _VOLUNTEER_FRONT[spec_field]["erase_box"])
        )
    return boxes