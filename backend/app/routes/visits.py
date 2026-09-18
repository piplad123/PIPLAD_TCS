from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SiteVisit

router = APIRouter(prefix="/api/visits", tags=["Visits"])


class TrackVisitRequest(BaseModel):
    visitor_key: str


@router.post("/track")
def track_visit(
    payload: TrackVisitRequest,
    db: Session = Depends(get_db),
):
    """Count one visit for a visitor key on the current day.

    A visitor key is counted at most once per calendar day, so repeat
    page loads from the same browser do not inflate the stats.
    """
    visitor_key = (payload.visitor_key or "").strip()

    if not visitor_key or len(visitor_key) > 100:
        return {"tracked": False}

    existing = (
        db.query(SiteVisit)
        .filter(
            SiteVisit.visitor_key == visitor_key,
            SiteVisit.visit_date == date.today(),
        )
        .first()
    )

    if existing:
        return {"tracked": False}

    db.add(
        SiteVisit(
            visitor_key=visitor_key,
            visit_date=date.today(),
        )
    )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"tracked": False}

    return {"tracked": True}