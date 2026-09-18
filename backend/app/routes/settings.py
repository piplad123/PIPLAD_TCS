"""Site-wide settings (contact details and other public configuration).

Contact details used to be hardcoded in the React components. This module
exposes them through a simple key/value table (``site_settings``) so the
admin can change the phone number, email address and headquarters location
without touching code.

- ``GET /api/settings``          -> public, returns the settings object
- ``PUT /api/admin/settings``    -> admin-only, upserts the provided keys
"""

from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SiteSetting
from .admin import get_current_admin

router = APIRouter(tags=["Settings"])


# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_SETTINGS: Dict[str, str] = {
    "phone": "+91-8981266033",
    "email": "info@pipladfoundation.in",
    "address": "Vill-Manikpur, Shahkhund-813108, Bhagalpur, Bihar",
    "map_query": "Manik Pur Buzurg, माणिक पुर बुज़ुर्ग, Bihar",
    "mission": (
        "Piplad Welfare Foundation works with rural communities to bridge the gaps in "
        "education, health, livelihoods, water, environment and technology, building a "
        "future where every villager can unlock their true potential."
    ),
    "copyright": "Piplad Welfare Foundation",
}


def _settings_map(db: Session) -> Dict[str, str]:
    """Return every stored setting as {key: value}."""
    return {
        row.key: row.value
        for row in db.query(SiteSetting).all()
    }


def _ensure_defaults(db: Session) -> None:
    """Insert any missing default setting rows (idempotent)."""
    existing = set(_settings_map(db))
    missing = [
        key
        for key in DEFAULT_SETTINGS
        if key not in existing
    ]

    if not missing:
        return

    for key in missing:
        db.add(
            SiteSetting(
                key=key,
                value=DEFAULT_SETTINGS[key],
            )
        )

    db.commit()


def _read_settings(db: Session) -> Dict[str, str]:
    """Ensure defaults and return the full settings map."""
    _ensure_defaults(db)
    return _settings_map(db)


# ============================================================
# PUBLIC
# ============================================================

@router.get("/api/settings")
def get_site_settings(
    db: Session = Depends(get_db),
):
    return _read_settings(db)


# ============================================================
# ADMIN
# ============================================================

@router.put("/api/admin/settings")
def update_site_settings(
    payload: Dict[str, Optional[str]],
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    unknown = set(payload.keys()) - set(DEFAULT_SETTINGS.keys())

    if unknown:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unknown setting keys: "
                + ", ".join(sorted(unknown))
            ),
        )

    _ensure_defaults(db)

    for key, value in payload.items():
        row = (
            db.query(SiteSetting)
            .filter(SiteSetting.key == key)
            .first()
        )

        if row is None:
            continue

        row.value = (value or "").strip()

    db.commit()

    return _read_settings(db)