from datetime import datetime
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
    """Seed the default catalog if the table is empty."""
    existing = db.query(ImpactMetric).count()

    if existing > 0:
        return

    for item in DEFAULT_METRICS:
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

    metrics = db.query(ImpactMetric).all()

    if len(payload.metrics) > len(metrics):
        raise HTTPException(
            status_code=400,
            detail="Too many metrics provided.",
        )

    for i, update in enumerate(payload.metrics):
        metric = metrics[i]

        metric.value = update.value

        if update.is_published is not None:
            metric.is_published = bool(update.is_published)

        if update.metric_name is not None:
            metric.metric_name = update.metric_name.strip()

        if update.description is not None:
            metric.description = (
                update.description.strip()
                or None
            )

        # last_updated refreshes automatically via onupdate,
        # but update it explicitly so the timestamp is reliable
        # even if the value itself did not change.
        metric.last_updated = datetime.utcnow()

    db.commit()

    for metric in metrics:
        db.refresh(metric)

    return (
        db.query(ImpactMetric)
        .order_by(
            ImpactMetric.category.asc(),
            ImpactMetric.display_order.asc(),
            ImpactMetric.id.asc(),
        )
        .all()
    )