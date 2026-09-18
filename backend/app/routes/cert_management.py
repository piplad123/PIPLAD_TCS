"""Certificate Management admin flow.

Provides the one-click Generate/preview/send flow for the four official
certificate types and the Volunteer ID card. Certificates and volunteer IDs
are always numbered server-side; nothing is emailed until a PDF + database
record already exist.

Rendering reuses the shared ``document_service`` / ``foundation_design``
pipeline so the output is identical to the rest of the admin.
"""

import base64
import io
import re
import secrets
from datetime import date, datetime

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from PIL import Image as PILImage
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .. import email_service, models, schemas
from ..database import get_db
from ..document_layouts import CERTIFICATE_LABELS
from ..document_service import (
    CERT_GENERATED_DIR,
    VOLUNTEER_GENERATED_DIR,
    _display_date,
    _logo_bytes,
    build_issued_certificate,
    build_volunteer_card,
    save_rendered_certificate,
    save_rendered_volunteer_card,
)
from ..email_service import (
    send_certificate_documents_email,
    send_volunteer_welcome_email,
)
from ..foundation_design import (
    FOUNDATION_CERT_TYPES,
    OUTPUT_W,
    OUTPUT_H,
    jpeg_bytes,
    render_certificate,
    render_volunteer_card_front,
)
from ..memory_util import log_rss
from ..qrcode_util import verify_url
from .admin import get_current_admin

router = APIRouter(prefix="/api/admin/cert-management", tags=["Admin Certificate Management"])

MANAGED_CERT_TYPES = ("appreciation", "internship", "completion", "participation")
VOLUNTEER_DOC_TYPE = "volunteer"

# Short code used in the auto-generated number, e.g. PWF-APPR-2026-0001.
CERT_TYPE_CODES = {
    "appreciation": "APPR",
    "internship": "INTR",
    "completion": "COMP",
    "participation": "PART",
}

# Volunteer statuses that keep the card verifiable (see routes/verify.py).
ALLOWED_VOLUNTEER_STATUSES = {"issued", "accepted", "active", "merged", "settings"}

MAX_PHOTO_BYTES = 6 * 1024 * 1024


def next_pwf_certificate_number(db: Session, certificate_type: str) -> str:
    """Next unique certificate number in the PWF-{CODE}-{YEAR}-{NNNN} scheme."""
    year = datetime.utcnow().year
    prefix = f"PWF-{CERT_TYPE_CODES.get(certificate_type, 'CERT')}-{year}-"
    used = {
        row[0]
        for row in db.query(models.IssuedCertificate.certificate_number)
        .filter(
            models.IssuedCertificate.certificate_number.isnot(None),
            models.IssuedCertificate.certificate_number.startswith(prefix),
        )
        .all()
        if row[0]
    }
    sequence = 1
    while f"{prefix}{sequence:04d}" in used:
        sequence += 1
    return f"{prefix}{sequence:04d}"


def _decode_photo_data_url(photo_data_url: str | None):
    """Decode an optional ``data:image/...;base64,...`` photo value.

    Returns ``(raw_bytes, extension)`` or ``(None, None)`` when empty.
    Raises HTTP 400 for malformed / oversized / invalid images.
    """
    if not photo_data_url:
        return None, None
    match = re.match(r"data:image/([\w+]+);base64,(.+)$", photo_data_url, re.DOTALL)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid photo data URI.")
    extension = match.group(1).lower()
    if extension not in ("jpeg", "jpg", "png", "webp"):
        raise HTTPException(status_code=400, detail="Photo must be JPG, PNG or WebP.")
    raw = base64.b64decode(match.group(2))
    if len(raw) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=400, detail="Photo is larger than 6 MB.")
    try:
        PILImage.open(io.BytesIO(raw)).verify()
    except Exception as exc:  # noqa: BLE001 - corrupted upload should be a 400
        raise HTTPException(status_code=400, detail="Uploaded photo is not a valid image.") from exc
    return raw, extension


def _save_photo_data_url(photo_data_url: str | None) -> str | None:
    """Persist an optional photo data URI under media/generated and return its media path."""
    raw, extension = _decode_photo_data_url(photo_data_url)
    if raw is None:
        return None
    photos_dir = VOLUNTEER_GENERATED_DIR / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    extension = "jpg" if extension == "jpeg" else extension
    filename = f"cm-{secrets.token_hex(6)}.{extension}"
    (photos_dir / filename).write_bytes(raw)
    return f"/media/generated/volunteers/photos/{filename}"


# ============================================================
# Dashboard stats
# ============================================================

@router.get("/stats")
def cert_management_stats(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    counts = dict(
        db.query(models.IssuedCertificate.certificate_type, func.count())
        .group_by(models.IssuedCertificate.certificate_type)
        .all()
    )
    by_type = {doc_type: int(counts.get(doc_type, 0)) for doc_type in MANAGED_CERT_TYPES}
    volunteer_cards = (
        db.query(models.VolunteerApplication.id)
        .filter(models.VolunteerApplication.card_file_path.isnot(None))
        .count()
    )
    return {
        "total_certificates": sum(by_type.values()),
        "by_type": by_type,
        "total_volunteer_cards": int(volunteer_cards),
    }


# ============================================================
# Preview (renders without persisting anything)
# ============================================================

def _preview_certificate_fields(payload: schemas.ManagedDocGenerateRequest) -> dict:
    fields = {
        "first_name": payload.first_name or "",
        "last_name": payload.last_name or "",
        "name": " ".join(part for part in (payload.first_name, payload.last_name) if part),
        "program_name": payload.program_name or "",
        "certificate_number": "",
        "issue_date": _display_date(payload.issue_date) or _display_date(datetime.utcnow().date()),
        "email": payload.recipient_email or "",
    }
    if payload.document_type == "internship":
        fields["starting_date"] = _display_date(payload.starting_date)
        fields["end_date"] = _display_date(payload.end_date)
    if payload.document_type == "completion":
        fields["organisation_name"] = payload.organisation_name or ""
        fields["completion_date"] = _display_date(payload.competition_date)
    return fields


def _preview_volunteer_fields(payload: schemas.ManagedDocGenerateRequest) -> dict:
    photo, _ = _decode_photo_data_url(payload.photo_data_url)
    return {
        "name": " ".join(part for part in (payload.first_name, payload.last_name) if part),
        "volunteer_id": "",
        "email": payload.recipient_email or "",
        "phone": payload.phone or "",
        "designation": payload.designation or "Volunteer",
        "joining_date": _display_date(payload.issue_date),
        "status": payload.status or "issued",
        "photo": photo,
        "qr_data": verify_url("volunteer", "PWF-PREVIEW"),
    }


@router.post("/preview")
def preview_managed_document(
    payload: schemas.ManagedDocGenerateRequest,
    scale: float = Query(0.5, ge=0.25, le=1.0),
    _=Depends(get_current_admin),
):
    """Render the selected document as a JPEG without storing anything.

    Previews use a half-resolution render by default so the small Render
    worker never spikes its resident footprint just to show a thumbnail.
    """
    log_rss("preview render start")
    if payload.document_type in FOUNDATION_CERT_TYPES:
        image = render_certificate(
            payload.document_type,
            out_w=round(OUTPUT_W * scale),
            out_h=round(OUTPUT_H * scale),
            qr_data=verify_url("certificate", "PWF-PREVIEW"),
            logo_bytes=_logo_bytes(),
            **_preview_certificate_fields(payload),
        )
        data = jpeg_bytes(image)
        log_rss("preview render end")
        return Response(content=data, media_type="image/jpeg")

    if payload.document_type == VOLUNTEER_DOC_TYPE:
        image = render_volunteer_card_front(
            logo_bytes=_logo_bytes(), **_preview_volunteer_fields(payload)
        )
        data = jpeg_bytes(image)
        log_rss("preview render end")
        return Response(content=data, media_type="image/jpeg")

    raise HTTPException(status_code=400, detail="Unsupported document type.")


# ============================================================
# Generate (persists a DB record + files)
# ============================================================

def _issue_certificate(db: Session, payload: schemas.ManagedDocGenerateRequest) -> schemas.ManagedDocResponse:
    if payload.document_type not in MANAGED_CERT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported certificate type.")
    try:
        cert = build_issued_certificate(
            db,
            certificate_type=payload.document_type,
            first_name=payload.first_name,
            last_name=payload.last_name,
            recipient_email=payload.recipient_email,
            program_name=payload.program_name,
            starting_date=payload.starting_date,
            end_date=payload.end_date,
            organisation_name=payload.organisation_name,
            competition_date=payload.competition_date,
            issue_date=payload.issue_date,
            certificate_number=next_pwf_certificate_number(db, payload.document_type),
            status="issued",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    qr_token = cert.certificate_number or cert.qr_verification_token or ""
    return schemas.ManagedDocResponse(
        kind="certificate",
        record_id=cert.id,
        document_type=cert.certificate_type,
        document_number=cert.certificate_number,
        recipient_name=cert.recipient_name,
        recipient_email=cert.recipient_email,
        rendered_url=cert.rendered_url,
        verified_url=verify_url("certificate", qr_token),
        created_at=cert.created_at,
    )


def _issue_volunteer_card(db: Session, payload: schemas.ManagedDocGenerateRequest) -> schemas.ManagedDocResponse:
    full_name = " ".join(part for part in (payload.first_name, payload.last_name) if part).strip()
    if not full_name:
        raise HTTPException(status_code=400, detail="First name is required.")
    if not payload.recipient_email:
        raise HTTPException(status_code=400, detail="Email is required for a Volunteer ID card.")
    if not payload.phone:
        raise HTTPException(status_code=400, detail="Phone is required for a Volunteer ID card.")

    status = (payload.status or "issued").strip().lower()
    if status == "active":
        status = "accepted"
    if status not in ALLOWED_VOLUNTEER_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid volunteer status.")

    profile_pic_url = _save_photo_data_url(payload.photo_data_url)

    app = models.VolunteerApplication(
        full_name=full_name,
        email=payload.recipient_email.strip(),
        phone=payload.phone.strip(),
        interest_area=(payload.designation or "Volunteer").strip() or "Volunteer",
        profile_pic_url=profile_pic_url,
        status=status,
    )
    db.add(app)
    db.flush()
    # Same scheme the volunteer accept flow uses: PWF-{year}-{sequential id}.
    app.volunteer_id = f"PWF-{datetime.utcnow().year}-{app.id:04d}"
    db.commit()

    issue_date = payload.issue_date or date.today()
    try:
        build_volunteer_card(
            db,
            app,
            issue_date=issue_date,
            status=status,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return schemas.ManagedDocResponse(
        kind="volunteer",
        record_id=app.id,
        document_type="volunteer",
        document_number=app.volunteer_id,
        recipient_name=app.full_name,
        recipient_email=app.email,
        rendered_url=app.card_file_path,
        verified_url=verify_url("volunteer", app.volunteer_id or app.card_qr_token or str(app.id)),
        created_at=app.created_at,
    )


@router.post("/generate", response_model=schemas.ManagedDocResponse)
def generate_managed_document(
    payload: schemas.ManagedDocGenerateRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Persist the selected document: DB record + JPEG + print-ready PDF."""
    if payload.document_type in MANAGED_CERT_TYPES:
        return _issue_certificate(db, payload)
    if payload.document_type == VOLUNTEER_DOC_TYPE:
        return _issue_volunteer_card(db, payload)
    raise HTTPException(status_code=400, detail="Unsupported document type.")


# ============================================================
# Certificate history (searchable, filterable, paginated)
# ============================================================

def _history_cert_row(cert) -> schemas.CertificateHistoryItem:
    return schemas.CertificateHistoryItem(
        kind="certificate",
        record_id=cert.id,
        document_number=cert.certificate_number or f"Certificate #{cert.id}",
        recipient_name=cert.recipient_name,
        document_type=cert.certificate_type or "certificate",
        type_label=cert.type_label or CERTIFICATE_LABELS.get(cert.certificate_type) or "Certificate",
        program=cert.program_name,
        issue_date=cert.issue_date,
        email=cert.recipient_email,
        status="valid" if not cert.revoked_at else "revoked",
        email_sent=bool(cert.sent_at),
        created_at=cert.created_at,
        rendered_url=cert.rendered_url or cert.generated_file_path,
        verified_url=verify_url("certificate", cert.certificate_number or cert.qr_verification_token or ""),
    )


def _history_volunteer_row(app) -> schemas.CertificateHistoryItem:
    return schemas.CertificateHistoryItem(
        kind="volunteer",
        record_id=app.id,
        document_number=app.volunteer_id or f"Volunteer #{app.id}",
        recipient_name=app.full_name,
        document_type="volunteer",
        type_label="Volunteer ID Card",
        program=app.interest_area,
        issue_date=app.issue_date,
        email=app.email,
        status="valid" if not app.card_revoked_at else "revoked",
        email_sent=bool(app.card_sent_at),
        created_at=app.created_at,
        rendered_url=app.card_file_path,
        verified_url=verify_url("volunteer", app.card_qr_token or app.volunteer_id or ""),
    )


@router.get("/history", response_model=schemas.CertificateHistoryResponse)
def certificate_history(
    search: str | None = None,
    doc_type: Annotated[str | None, Query(alias="type")] = None,
    status: str | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Paginated view of every issued certificate and volunteer ID card.

    Search covers recipient name, document number and e-mail; the ``type``
    filter accepts the four certificate slugs or ``volunteer``.
    """
    term = (search or "").strip()
    doc_type = doc_type or "all"

    rows = []

    # Certificates (excluded entirely when filtering for Volunteer cards only).
    if doc_type != "volunteer":
        cert_query = db.query(models.IssuedCertificate)
        if doc_type != "all":
            cert_query = cert_query.filter(models.IssuedCertificate.certificate_type == doc_type)
        if status and status != "all":
            if status == "revoked":
                cert_query = cert_query.filter(models.IssuedCertificate.revoked_at.isnot(None))
            else:
                cert_query = cert_query.filter(models.IssuedCertificate.revoked_at.is_(None))
        if term:
            like = f"%{term}%"
            cert_query = cert_query.filter(
                or_(
                    models.IssuedCertificate.recipient_name.ilike(like),
                    models.IssuedCertificate.recipient_email.ilike(like),
                    models.IssuedCertificate.certificate_number.ilike(like),
                )
            )
        rows.extend(_history_cert_row(cert) for cert in cert_query.all())

    # Volunteer ID cards are only part of the history once a card exists.
    if doc_type == "all" or doc_type == "volunteer":
        vol_query = (
            db.query(models.VolunteerApplication)
            .filter(models.VolunteerApplication.card_file_path.isnot(None))
        )
        if status and status != "all":
            if status == "revoked":
                vol_query = vol_query.filter(models.VolunteerApplication.card_revoked_at.isnot(None))
            else:
                vol_query = vol_query.filter(models.VolunteerApplication.card_revoked_at.is_(None))
        if term:
            like = f"%{term}%"
            vol_query = vol_query.filter(
                or_(
                    models.VolunteerApplication.full_name.ilike(like),
                    models.VolunteerApplication.email.ilike(like),
                    models.VolunteerApplication.volunteer_id.ilike(like),
                )
            )
        rows.extend(_history_volunteer_row(app) for app in vol_query.all())

    rows.sort(key=lambda row: row.created_at, reverse=True)
    total = len(rows)
    start = (page - 1) * page_size
    return schemas.CertificateHistoryResponse(
        items=rows[start:start + page_size],
        total=total,
        page=page,
        page_size=page_size,
    )


# ============================================================
# Send email (only after generation succeeded)
# ============================================================

def _certificate_pdf_bytes(db: Session, cert) -> bytes:
    """Return the print-ready certificate PDF, re-rendering it if missing."""
    path = CERT_GENERATED_DIR / f"{cert.certificate_number or cert.id}.pdf"
    if not path.is_file():
        save_rendered_certificate(cert)
        db.commit()
    return path.read_bytes()


@router.post("/certificate/{cert_id}/send-email")
def send_certificate_managed_email(
    cert_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Attach the official PDF and e-mail the full certificate details.

    Delivery only counts as sent once Brevo confirms it; on failure the
    ``sent_at`` timestamp is left untouched so the admin can resend safely.
    """
    cert = db.query(models.IssuedCertificate).filter(models.IssuedCertificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    if not cert.recipient_email:
        raise HTTPException(status_code=400, detail="This certificate has no recipient email to send to.")
    try:
        pdf_bytes = _certificate_pdf_bytes(db, cert)
    except Exception as exc:  # noqa: BLE001 - surface render failure clearly
        raise HTTPException(status_code=400, detail=f"Certificate PDF unavailable: {exc}") from exc
    log_rss("certificate email before")

    label = cert.type_label or CERTIFICATE_LABELS.get(cert.certificate_type) or "Certificate"
    sent = send_certificate_documents_email(
        to_email=cert.recipient_email,
        recipient_name=cert.recipient_name,
        type_label=label,
        event_topic=cert.program_name,
        event_date=_display_date(cert.issue_date),
        certificate_number=cert.certificate_number or "",
        verification_url=verify_url(
            "certificate", cert.certificate_number or cert.qr_verification_token or ""
        ),
        pdf_bytes=pdf_bytes,
        pdf_filename=f"{cert.certificate_number or cert.id}.pdf",
    )
    log_rss("certificate email after")
    if sent:
        cert.sent_at = datetime.utcnow()
        db.commit()
        return {
            "sent": True,
            "message": f"Certificate emailed to {cert.recipient_email}.",
        }
    if not email_service.is_brevo_configured():
        return {
            "sent": False,
            "message": "Email service is not configured (BREVO_API_KEY missing). Nothing was sent.",
        }
    return {
        "sent": False,
        "message": "Email delivery failed. Check the server logs and try resending.",
    }


@router.post("/volunteer/{application_id}/send-email")
def send_volunteer_managed_email(
    application_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    app = db.query(models.VolunteerApplication).filter(models.VolunteerApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Volunteer not found.")
    if not app.card_file_path:
        raise HTTPException(status_code=400, detail="Volunteer ID card has not been generated yet.")
    basename = app.volunteer_id or app.id
    try:
        front_jpg = (VOLUNTEER_GENERATED_DIR / f"{basename}.jpg").read_bytes()
        card_pdf = (VOLUNTEER_GENERATED_DIR / f"{basename}.pdf").read_bytes()
    except FileNotFoundError:
        save_rendered_volunteer_card(app)
        db.commit()
        front_jpg = (VOLUNTEER_GENERATED_DIR / f"{basename}.jpg").read_bytes()
        card_pdf = (VOLUNTEER_GENERATED_DIR / f"{basename}.pdf").read_bytes()
    log_rss("volunteer email before")

    sent = send_volunteer_welcome_email(
        to_email=app.email,
        volunteer_name=app.full_name,
        volunteer_email=app.email,
        volunteer_id=app.volunteer_id or "",
        joined_date=app.issue_date,
        id_card_jpg=front_jpg,
        id_card_pdf=card_pdf,
        verification_url=verify_url("volunteer", app.volunteer_id or app.card_qr_token or str(app.id)),
    )
    log_rss("volunteer email after")
    if sent:
        app.card_sent_at = datetime.utcnow()
        db.commit()
        message = f"Volunteer ID card emailed to {app.email}."
    else:
        message = "Email not sent (sending is not configured or the delivery failed)."
    return {"sent": bool(sent), "message": message}