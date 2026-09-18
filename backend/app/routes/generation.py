"""Admin API for downloading and revoking official Piplad documents.

Certificates (4 official types) and the official Volunteer ID card are
rendered dynamically, stored under media/generated, and exposed for
download (JPEG or PDF). Each document carries a unique QR pointing at the
public verification page.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..document_pdf import document_pdf_bytes
from ..document_service import (
    CERT_GENERATED_DIR,
    VOLUNTEER_GENERATED_DIR,
    certificate_download_name,
    volunteer_card_download_name,
)
from ..qrcode_util import verify_url
from .admin import get_current_admin

router = APIRouter(prefix="/api/admin/generated", tags=["Admin Generated Documents"])


def _cert_to_response(cert) -> schemas.GeneratedCertificateResponse:
    qr_token = cert.certificate_number or cert.qr_verification_token or ""
    return schemas.GeneratedCertificateResponse(
        id=cert.id,
        certificate_number=cert.certificate_number,
        certificate_type=cert.certificate_type,
        recipient_name=cert.recipient_name,
        recipient_email=cert.recipient_email,
        program_name=cert.program_name,
        starting_date=cert.starting_date,
        end_date=cert.end_date,
        organisation_name=cert.organisation_name,
        competition_date=cert.competition_date,
        competition_location=cert.competition_location,
        issue_date=cert.issue_date,
        rendered_url=cert.rendered_url,
        generated_file_path=cert.generated_file_path,
        verified_url=verify_url("certificate", qr_token),
        status=cert.status,
        sent_at=cert.sent_at,
        created_at=cert.created_at,
        revoked=bool(cert.revoked_at),
    )


def _volunteer_to_response(app) -> schemas.GeneratedVolunteerCardResponse:
    qr_token = app.card_qr_token or app.volunteer_id or ""
    return schemas.GeneratedVolunteerCardResponse(
        id=app.id,
        volunteer_id=app.volunteer_id,
        full_name=app.full_name,
        email=app.email,
        profile_pic_url=app.profile_pic_url,
        status=app.status,
        position=app.position,
        location=app.location,
        issue_date=app.issue_date,
        valid_till=app.valid_till,
        card_file_path=app.card_file_path,
        verified_url=verify_url("volunteer", qr_token),
        card_revoked_at=app.card_revoked_at,
        card_sent_at=app.card_sent_at,
        created_at=app.created_at,
    )


# ============================================================
# Certificates – download / revoke
# ============================================================

@router.get("/certificates/{cert_id}/download")
def download_certificate(
    cert_id: int,
    format: str = Query("jpg"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    cert = (
        db.query(models.IssuedCertificate)
        .filter(models.IssuedCertificate.id == cert_id)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    path = CERT_GENERATED_DIR / f"{cert.certificate_number or cert.id}.jpg"
    if not path.is_file():
        cert.rendered_url = None
        from ..document_service import save_rendered_certificate

        save_rendered_certificate(cert)
        db.commit()
    if format == "pdf":
        pdf_bytes = document_pdf_bytes(
            path.read_bytes(),
            orientation="landscape",
            title=f"Certificate {cert.certificate_number}",
        )
        from fastapi.responses import Response

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{certificate_download_name(cert)}"'
                    .replace(".jpg", ".pdf")
                )
            },
        )
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=certificate_download_name(cert),
    )


@router.post("/certificates/{cert_id}/revoke", response_model=schemas.GeneratedCertificateResponse)
def revoke_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    cert = (
        db.query(models.IssuedCertificate)
        .filter(models.IssuedCertificate.id == cert_id)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    cert.revoked_at = cert.revoked_at or datetime.utcnow()
    cert.status = "revoked"
    db.commit()
    db.refresh(cert)
    return _cert_to_response(cert)


# ============================================================
# Volunteer ID cards – download / revoke
# ============================================================

@router.get("/volunteers/{application_id}/download")
def download_volunteer_card(
    application_id: int,
    format: str = Query("jpg"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    app = (
        db.query(models.VolunteerApplication)
        .filter(models.VolunteerApplication.id == application_id)
        .first()
    )
    if not app or not app.card_file_path:
        raise HTTPException(status_code=404, detail="Volunteer card not found.")
    path = VOLUNTEER_GENERATED_DIR / f"{app.volunteer_id or app.id}.jpg"
    if not path.is_file():
        from ..document_service import save_rendered_volunteer_card

        app.card_file_path = None
        save_rendered_volunteer_card(app)
        db.commit()
    if format == "pdf":
        pdf_path = VOLUNTEER_GENERATED_DIR / f"{app.volunteer_id or app.id}.pdf"
        if not pdf_path.is_file():
            from ..document_service import save_rendered_volunteer_card

            app.card_file_path = None
            save_rendered_volunteer_card(app)
            db.commit()
        from fastapi.responses import Response

        return Response(
            content=pdf_path.read_bytes(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{volunteer_card_download_name(app)}"'
                    .replace(".jpg", ".pdf")
                )
            },
        )
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=volunteer_card_download_name(app),
    )


@router.post("/volunteers/{application_id}/revoke", response_model=schemas.GeneratedVolunteerCardResponse)
def revoke_volunteer_card(
    application_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    app = (
        db.query(models.VolunteerApplication)
        .filter(models.VolunteerApplication.id == application_id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Volunteer application not found.")
    app.card_revoked_at = app.card_revoked_at or datetime.utcnow()
    app.status = "revoked"
    db.commit()
    db.refresh(app)
    return _volunteer_to_response(app)