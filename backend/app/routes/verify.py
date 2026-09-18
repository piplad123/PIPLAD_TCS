"""Public document verification endpoints.

Both QR codes and certificate/card numbers resolve to these URLs. If a
document was revoked or a volunteer card is past its validity window the
response reports that so the public page can show a clear status.
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/verify", tags=["verify"])


@router.get("/certificate/{identifier}", response_model=schemas.VerifiedCertificateResponse)
def verify_certificate(identifier: str, db: Session = Depends(get_db)):
    cert = (
        db.query(models.IssuedCertificate)
        .filter(
            (models.IssuedCertificate.certificate_number == identifier)
            | (models.IssuedCertificate.qr_verification_token == identifier)
        )
        .first()
    )
    if not cert or not cert.qr_verification_token:
        return schemas.VerifiedCertificateResponse(
            valid=False,
            reason="Certificate number not found or never issued.",
            recipient_name="Unknown",
        )
    if cert.revoked_at:
        return schemas.VerifiedCertificateResponse(
            valid=False,
            revoked=True,
            reason="This certificate has been revoked by the issuer.",
            certificate_number=cert.certificate_number,
            certificate_type=cert.certificate_type,
            recipient_name=cert.recipient_name,
            program_name=cert.program_name,
            issue_date=cert.issue_date,
            starting_date=cert.starting_date,
            end_date=cert.end_date,
            organisation_name=cert.organisation_name,
            competition_date=cert.competition_date,
            competition_location=cert.competition_location,
        )
    return schemas.VerifiedCertificateResponse(
        valid=True,
        certificate_number=cert.certificate_number,
        certificate_type=cert.certificate_type,
        recipient_name=cert.recipient_name,
        program_name=cert.program_name,
        issue_date=cert.issue_date,
        starting_date=cert.starting_date,
        end_date=cert.end_date,
        organisation_name=cert.organisation_name,
        competition_date=cert.competition_date,
        competition_location=cert.competition_location,
    )


@router.get("/volunteer/{identifier}", response_model=schemas.VerifiedVolunteerResponse)
def verify_volunteer(identifier: str, db: Session = Depends(get_db)):
    app = (
        db.query(models.VolunteerApplication)
        .filter(
            (models.VolunteerApplication.volunteer_id == identifier)
            | (models.VolunteerApplication.card_qr_token == identifier)
        )
        .first()
    )
    if not app or not app.card_file_path:
        return schemas.VerifiedVolunteerResponse(
            valid=False,
            reason="Volunteer ID not found.",
            full_name="Unknown",
        )
    if app.status not in ("accepted", "merged", "settings", "issued"):
        return schemas.VerifiedVolunteerResponse(
            valid=False,
            reason="Volunteer card is not currently active.",
            full_name=app.full_name,
        )
    if app.card_revoked_at:
        return schemas.VerifiedVolunteerResponse(
            valid=False,
            revoked=True,
            reason="This Volunteer ID has been revoked.",
            full_name=app.full_name,
            volunteer_id=app.volunteer_id,
            interest_area=app.interest_area,
            position=app.position,
            location=app.location,
            issue_date=app.issue_date,
            valid_till=app.valid_till,
        )
    expired = bool(app.valid_till and app.valid_till < datetime.utcnow().date())
    if expired:
        return schemas.VerifiedVolunteerResponse(
            valid=False,
            expired=True,
            reason="This Volunteer ID has expired.",
            full_name=app.full_name,
            volunteer_id=app.volunteer_id,
            interest_area=app.interest_area,
            position=app.position,
            location=app.location,
            issue_date=app.issue_date,
            valid_till=app.valid_till,
        )
    return schemas.VerifiedVolunteerResponse(
        valid=True,
        full_name=app.full_name,
        volunteer_id=app.volunteer_id,
        interest_area=app.interest_area,
        position=app.position,
        location=app.location,
        issue_date=app.issue_date,
        valid_till=app.valid_till,
    )