import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..email_service import send_admin_alert_email
from ..models import VolunteerApplication
from ..schemas import VolunteerApplicationResponse

from .admin import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_IMAGE_TYPES,
    MAX_IMAGE_SIZE,
    _validate_upload,
)

router = APIRouter(prefix="/api/volunteers", tags=["Volunteers"])


def _profile_pic_url(profile_pic: Optional[UploadFile]) -> str | None:
    if profile_pic is None or not profile_pic.filename:
        return None

    _validate_upload(
        profile_pic,
        ALLOWED_IMAGE_EXTENSIONS,
        ALLOWED_IMAGE_TYPES,
        MAX_IMAGE_SIZE,
    )

    # Prefer Cloudinary when configured (consistent with admin uploads).
    try:
        import os

        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")

        if (cloud_name and api_key and api_secret):
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )

            profile_pic.file.seek(0)
            content = profile_pic.file.read(MAX_IMAGE_SIZE + 1)

            if len(content) > MAX_IMAGE_SIZE:
                raise HTTPException(
                    413,
                    "File is too large. "
                    f"Maximum allowed size is {MAX_IMAGE_SIZE // (1024 * 1024)} MB.",
                )

            result = cloudinary.uploader.upload(
                content,
                folder="piplad/volunteers",
                resource_type="image",
                public_id=uuid.uuid4().hex,
            )

            if result.get("secure_url"):
                return result["secure_url"]

        # Local fallback when Cloudinary is not configured.
        extension = Path(profile_pic.filename or "").suffix.lower() or ".jpg"
        filename = f"{uuid.uuid4().hex}{extension}"

        base_dir = Path(__file__).resolve().parents[2]
        media_dir = base_dir / "media" / "volunteers"
        media_dir.mkdir(parents=True, exist_ok=True)

        destination = media_dir / filename

        profile_pic.file.seek(0)
        total = 0

        with destination.open("wb") as output:
            while True:
                chunk = profile_pic.file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_IMAGE_SIZE:
                    destination.unlink(missing_ok=True)
                    raise HTTPException(
                        413,
                        "File is too large. "
                        f"Maximum allowed size is {MAX_IMAGE_SIZE // (1024 * 1024)} MB.",
                    )
                output.write(chunk)

        return f"/media/volunteers/{filename}"
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            500,
            "Could not store profile picture.",
        )


@router.post("", response_model=VolunteerApplicationResponse, status_code=201)
def create_volunteer_application(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    interest_area: str = Form(...),
    about_yourself: Optional[str] = Form(None),
    profile_pic: UploadFile = File(...),
    website: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if website:
        return VolunteerApplicationResponse(
            id=0,
            full_name=full_name,
            email=email,
            phone=phone,
            interest_area=interest_area,
            about_yourself=about_yourself,
            profile_pic_url=None,
            status="pending",
            created_at=datetime.utcnow(),
        )

    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()
    interest_area = interest_area.strip()

    if not full_name or not email or not phone or not interest_area:
        raise HTTPException(400, "All required volunteer fields must be provided")

    if not profile_pic or not profile_pic.filename:
        raise HTTPException(400, "A profile picture is required")

    profile_pic_url = _profile_pic_url(profile_pic)

    volunteer = VolunteerApplication(
        full_name=full_name,
        email=email,
        phone=phone,
        interest_area=interest_area,
        about_yourself=(about_yourself or "").strip() or None,
        profile_pic_url=profile_pic_url,
    )

    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)

    send_admin_alert_email(
        subject="New volunteer application received",
        text_body=(
            f"A new volunteer application was submitted.\n\n"
            f"Name: {volunteer.full_name}\n"
            f"Email: {volunteer.email}\n"
            f"Phone: {volunteer.phone}\n"
            f"Interest area: {volunteer.interest_area}\n"
            f"Applied at: {volunteer.created_at.isoformat()} (UTC)"
        ),
    )

    return volunteer