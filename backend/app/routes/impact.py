from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ImpactMetric
from ..schemas import (
    ImpactMetricResponse,
    ImpactMetricsUpdateRequest,
    PublicImpactGroup,
    PublicImpactMetric,
    PublicImpactResponse,
)
from .admin import get_current_admin


router = APIRouter(
    prefix="/api/impact",
    tags=["Impact"],
)


# ============================================================
# DEFAULT METRIC CATALOG
# ============================================================
#
# These are the metrics Piplad tracks. `verified_carbon_credits`
# is intentionally separate from environmental impact and should
# only hold a value once credits are formally verified.

DEFAULT_METRICS = [
    {
        "metric_key": "students_supported",
        "metric_name": "Students & Learners Supported",
        "category": "people",
        "unit": "people",
        "description": "Learners supported through Piplad Pathshala and education programmes.",
        "display_order": 10,
    },
    {
        "metric_key": "community_reached",
        "metric_name": "Families & Community Members Reached",
        "category": "people",
        "unit": "people",
        "description": "Community members reached across welfare and development initiatives.",
        "display_order": 20,
    },
    {
        "metric_key": "trees_planted",
        "metric_name": "Trees Planted",
        "category": "environmental",
        "unit": "trees",
        "description": "Trees planted through plantation and climate initiatives.",
        "display_order": 10,
    },
    {
        "metric_key": "environmental_initiatives",
        "metric_name": "Environmental Initiatives",
        "category": "environmental",
        "unit": "initiatives",
        "description": "Environment and conservation initiatives delivered.",
        "display_order": 20,
    },
    {
        "metric_key": "water_conservation",
        "metric_name": "Water & Conservation Activities",
        "category": "environmental",
        "unit": "activities",
        "description": "Water and conservation activities carried out.",
        "display_order": 30,
    },
    {
        "metric_key": "estimated_co2e",
        "metric_name": "Estimated CO₂e Impact",
        "category": "environmental",
        "unit": "tonnes",
        "description": "Estimated CO₂e impact from green initiatives (not verified credits).",
        "display_order": 40,
    },
    {
        "metric_key": "verified_carbon_credits",
        "metric_name": "Verified Carbon Credits",
        "category": "carbon",
        "unit": "credits",
        "description": "Formally verified / issued carbon credits. Leave at 0 until verified.",
        "display_order": 10,
    },
]

CATEGORY_LABELS = {
    "people": "People Impact",
    "environmental": "Environmental Impact",
    "carbon": "Verified Carbon Credits",
}

CARBON_KEYS = {"verified_carbon_credits"}


# ============================================================
# HELPERS
# ============================================================

def _round_to_int(value) -> float:
    """Metrics are whole counts; return as float for safety."""
    return float(value or 0)


def _ensure_metrics(db: Session) -> None:
    """Seed the default catalog, and repair it if any keys are missing.

    Only returning early when the table is completely empty left a
    partially-populated table permanently broken.
    """
    existing_keys = {
        key
        for (key,) in db.query(ImpactMetric.metric_key).all()
    }

    missing = [
        item
        for item in DEFAULT_METRICS
        if item["metric_key"] not in existing_keys
    ]

    if not missing:
        return

    for item in missing:
        db.add(
            ImpactMetric(
                metric_key=item["metric_key"],
                metric_name=item["metric_name"],
                category=item["category"],
                value=0,
                unit=item["unit"],
                description=item["description"],
                is_published=True,
                display_order=item["display_order"],
                last_updated=datetime.utcnow(),
            )
        )

    db.commit()


# ============================================================
# PUBLIC IMPACT
# ============================================================

@router.get("", response_model=PublicImpactResponse)
def get_public_impact(
    db: Session = Depends(get_db),
):
    _ensure_metrics(db)

    metrics = (
        db.query(ImpactMetric)
        .filter(
            ImpactMetric.is_published.is_(True)
        )
        .order_by(
            ImpactMetric.category.asc(),
            ImpactMetric.display_order.asc(),
            ImpactMetric.id.asc(),
        )
        .all()
    )

    grouped = {}

    for metric in metrics:
        grouped.setdefault(
            metric.category,
            [],
        ).append(
            PublicImpactMetric(
                key=metric.metric_key,
                name=metric.metric_name,
                value=_round_to_int(metric.value),
                unit=metric.unit,
                display_order=metric.display_order,
            )
        )

    groups = []

    for category in ("people", "environmental"):
        if category in grouped:
            groups.append(
                PublicImpactGroup(
                    key=category,
                    name=CATEGORY_LABELS[category],
                    metrics=grouped[category],
                )
            )

    carbon_metrics = grouped.get("carbon", [])
    carbon_value = None

    if carbon_metrics:
        # Only pretend credits are real once formally verified (value > 0).
        carbon_value = carbon_metrics[0].value

        groups.append(
            PublicImpactGroup(
                key="carbon",
                name=CATEGORY_LABELS["carbon"],
                metrics=carbon_metrics,
            )
        )

    last_updated = None

    if metrics:
        most_recent = max(
            (m.last_updated for m in metrics if m.last_updated),
            default=None,
        )

        if most_recent:
            last_updated = most_recent.date()

    return PublicImpactResponse(
        last_updated=last_updated,
        groups=groups,
        has_verified_carbon_credits=(
            carbon_value is not None and carbon_value > 0
        ),
        verified_carbon_credits_value=(
            carbon_value if carbon_value and carbon_value > 0 else None
        ),
    )


# ============================================================
# ADMIN IMPACT
# ============================================================

@router.get(
    "/admin",
    response_model=List[ImpactMetricResponse],
)
def get_impact_metrics(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    _ensure_metrics(db)

    return (
        db.query(ImpactMetric)
        .order_by(
            ImpactMetric.category.asc(),
            ImpactMetric.display_order.asc(),
            ImpactMetric.id.asc(),
        )
        .all()
    )


@router.put(
    "/admin",
    response_model=List[ImpactMetricResponse],
)
def update_impact_metrics(
    payload: ImpactMetricsUpdateRequest,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    _ensure_metrics(db)

    # Keyed lookup. Row order is irrelevant, so a metric can only ever be
    # written to the row the admin actually edited.
    rows = {
        metric.metric_key: metric
        for metric in db.query(ImpactMetric).all()
    }

    unknown = [
        update.metric_key
        for update in payload.metrics
        if update.metric_key not in rows
    ]

    if unknown:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unknown metric_key(s): "
                f"{', '.join(sorted(set(unknown)))}"
            ),
        )

    seen = set()
    now = datetime.utcnow()

    # Validate the entire payload before touching any row, so a rejected
    # request cannot leave the session holding a half-applied update.
    for update in payload.metrics:
        if update.metric_key in seen:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Duplicate metric_key in payload: "
                    f"{update.metric_key}"
                ),
            )

        seen.add(update.metric_key)

        if update.value < 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Impact value for "
                    f"'{update.metric_key}' cannot be negative."
                ),
            )

    for update in payload.metrics:
        metric = rows[update.metric_key]
        changed = False

        if _round_to_int(metric.value) != update.value:
            # Numeric columns come back as Decimal on PostgreSQL but as float
            # on SQLite; Decimal(str(...)) keeps both consistent.
            metric.value = Decimal(str(update.value))
            changed = True

        if (
            update.is_published is not None
            and bool(metric.is_published) != bool(update.is_published)
        ):
            metric.is_published = bool(update.is_published)
            changed = True

        if update.metric_name is not None:
            new_name = update.metric_name.strip()

            if new_name and new_name != metric.metric_name:
                metric.metric_name = new_name
                changed = True

        if update.description is not None:
            new_description = update.description.strip() or None

            if new_description != metric.description:
                metric.description = new_description
                changed = True

        # Only stamp rows that actually changed, otherwise "last updated"
        # on the public Impact page stops meaning anything.
        if changed:
            metric.last_updated = now

    db.commit()

    return (
        db.query(ImpactMetric)
        .order_by(
            ImpactMetric.category.asc(),
            ImpactMetric.display_order.asc(),
            ImpactMetric.id.asc(),
        )
        .all()
    )