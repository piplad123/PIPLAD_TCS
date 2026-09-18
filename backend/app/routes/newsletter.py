import csv
import io
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..email_service import send_newsletter_confirmation_email
from ..models import NewsletterSubscriber
from ..schemas import (
    NewsletterSubscribeRequest,
    NewsletterSubscriberResponse,
)
from .admin import get_current_admin

router = APIRouter(tags=["Newsletter"])

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@router.post(
    "/api/newsletter/subscribe",
    response_model=NewsletterSubscriberResponse,
    status_code=201,
)
def subscribe_newsletter(
    payload: NewsletterSubscribeRequest,
    db: Session = Depends(get_db),
):
    if payload.website:
        return NewsletterSubscriberResponse(
            id=0, email=payload.email, name=payload.name, created_at=datetime.utcnow()
        )

    email = payload.email.strip().lower()

    if not _EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Please enter a valid email address.")

    existing = (
        db.query(NewsletterSubscriber)
        .filter(NewsletterSubscriber.email == email)
        .first()
    )

    if existing:
        return existing

    subscriber = NewsletterSubscriber(
        email=email,
        name=(payload.name or "").strip() or None,
    )
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    send_newsletter_confirmation_email(
        to_email=subscriber.email,
        name=subscriber.name,
    )

    return subscriber


@router.get("/api/admin/newsletter", response_model=List[NewsletterSubscriberResponse])
def list_newsletter_subscribers(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(NewsletterSubscriber)
        .order_by(NewsletterSubscriber.created_at.desc())
        .all()
    )


@router.get("/api/admin/newsletter/export")
def export_newsletter_subscribers(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    subscribers = (
        db.query(NewsletterSubscriber)
        .order_by(NewsletterSubscriber.created_at.asc())
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["email", "name", "subscribed_at"])
    for subscriber in subscribers:
        writer.writerow(
            [
                subscriber.email,
                subscriber.name or "",
                subscriber.created_at.isoformat() if subscriber.created_at else "",
            ]
        )

    return Response(
        content="\ufeff" + buffer.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=newsletter-subscribers.csv"
        },
    )