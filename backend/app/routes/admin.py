import json
import logging
import os
import re
import secrets
import uuid

import cloudinary
import cloudinary.uploader

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db

from ..models import (
    Cause,
    Certificate,
    ContactInquiry,
    Donation,
    FooterFocusItem,
    FooterQuickLink,
    FounderMilestone,
    FounderProfile,
    GalleryItem,
    Mentor,
    SiteVisit,
    TeamMember,
    UpcomingProject,
    VideoGallery,
    VolunteerApplication,
)

from ..schemas import (
    CertificateResponse,
    CauseResponse,
    DonationListResponse,
    DonationResponse,
FooterFocusItemResponse,
    FooterQuickLinkResponse,
    FounderProfileResponse,
    GalleryItemResponse,
    MentorResponse,
    TeamMemberResponse,
    UpcomingProjectResponse,
    VideoGalleryResponse,
    VolunteerApplicationResponse,
)

from ..email_service import (
    send_team_card_email,
    send_volunteer_rejection_email,
    send_volunteer_welcome_email,
)
from ..document_service import generate_qr_token
from ..donation_receipt import build_donation_receipt_html
from ..memory_util import log_rss
from ..welcome_card import (
    build_volunteer_qr_png,
    load_profile_photo,
)
from ..team_card import build_team_card_jpg


logger = logging.getLogger(__name__)

security = HTTPBasic()

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


# ============================================================
# MEDIA DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MEDIA_DIR = BASE_DIR / "media"


def _read_media_file(media_path: str | None) -> bytes | None:
    """Read a media-relative path (``/media/...``) into bytes, or None."""
    if not media_path:
        return None
    clean = media_path.removeprefix("/media/").removeprefix("media/")
    path = MEDIA_DIR / clean
    if not path.is_file():
        return None
    return path.read_bytes()


# ============================================================
# UPLOAD RULES
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-m4v",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024


# ============================================================
# GALLERY CATEGORIES
# ============================================================

DEFAULT_GALLERY_CATEGORIES = [
    "Photo Gallery",
    "Education",
    "Healthcare",
    "Environment",
    "Agriculture",
    "Sports",
    "Culture",
    "Social Welfare",
    "Finance & Legal",
    "General",
]


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security),
):
    correct_username = secrets.compare_digest(
        credentials.username,
        os.getenv("ADMIN_USER", "admin"),
    )

    correct_password = secrets.compare_digest(
        credentials.password,
         os.getenv("ADMIN_PASSWORD", "admin"),
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Basic",
            },
        )

    return credentials.username


# ============================================================
# FILE HELPERS
# ============================================================

def _safe_name(
    filename: str | None,
    default_extension: str,
) -> str:
    extension = Path(
        filename or ""
    ).suffix.lower()

    return (
        f"{uuid.uuid4().hex}"
        f"{extension or default_extension}"
    )


def _validate_upload(
    file: UploadFile,
    allowed_extensions,
    allowed_types,
    max_size: int,
):
    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            400,
            f"Unsupported file type: "
            f"{extension or 'unknown'}",
        )

    if (
        file.content_type
        and file.content_type not in allowed_types
    ):
        raise HTTPException(
            400,
            f"Unsupported MIME type: "
            f"{file.content_type}",
        )

    return extension


def _upload_to_cloudinary(
    file: UploadFile,
    folder: str,
    max_size: int,
    resource_type: str,
) -> str:
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all((cloud_name, api_key, api_secret)):
        raise HTTPException(
            503,
            "Cloudinary storage is not configured on the backend.",
        )

    file.file.seek(0)
    content = file.file.read(max_size + 1)

    if len(content) > max_size:
        raise HTTPException(
            413,
            "File is too large. "
            f"Maximum allowed size is {max_size // (1024 * 1024)} MB.",
        )

    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        result = cloudinary.uploader.upload(
            content,
            folder=f"piplad/{folder}",
            resource_type=resource_type,
            public_id=uuid.uuid4().hex,
        )

    except Exception as exc:
        raise HTTPException(
            502,
            f"Could not upload file to Cloudinary: {exc}",
        ) from exc

    secure_url = result.get("secure_url")

    if not secure_url:
        raise HTTPException(
            502,
            "Cloudinary did not return a media URL.",
        )

    return secure_url


def _delete_local_file(
    url: str | None,
):
    if not url or not url.startswith("/media/"):
        return

    relative = url.removeprefix("/media/")

    candidate = (
        MEDIA_DIR / relative
    ).resolve()

    media_root = MEDIA_DIR.resolve()

    if (
        candidate == media_root
        or media_root not in candidate.parents
    ):
        return

    if (
        candidate.exists()
        and candidate.is_file()
    ):
        candidate.unlink(
            missing_ok=True
        )


def _delete_cloudinary_file(
    url: str | None,
    resource_type: str,
):
    if not url or "res.cloudinary.com" not in url:
        return

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all((cloud_name, api_key, api_secret)):
        return

    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        public_id = url.split("/upload/", 1)[-1]

        if public_id.startswith("v") and "/" in public_id:
            public_id = public_id.split("/", 1)[1]

        public_id = public_id.rsplit(".", 1)[0]

        cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type,
            invalidate=True,
        )
    except Exception:
        return


def _public_url(
    folder: str,
    filename: str,
) -> str:
    return f"/media/{folder}/{filename}"


# ============================================================
# SHARED FILE HELPERS
# ============================================================

def _save_local_image(
    file: UploadFile,
    folder: str,
) -> str:
    """Store one image locally under backend/media/<folder> (size-checked)."""
    file.file.seek(0)
    filename = _safe_name(file.filename, ".jpg")
    destination_dir = MEDIA_DIR / folder
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / filename

    total = 0

    try:
        with destination.open("wb") as output:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_IMAGE_SIZE:
                    raise HTTPException(
                        413,
                        "File is too large. "
                        f"Maximum allowed size is {MAX_IMAGE_SIZE // (1024 * 1024)} MB.",
                    )
                output.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(500, f"Could not save uploaded file: {exc}") from exc

    return _public_url(folder, filename)


def _upload_image(
    file: UploadFile,
    folder: str,
) -> str:
    """Validate and store an image, preferring Cloudinary with local fallback."""
    _validate_upload(
        file,
        ALLOWED_IMAGE_EXTENSIONS,
        ALLOWED_IMAGE_TYPES,
        MAX_IMAGE_SIZE,
    )

    try:
        return _upload_to_cloudinary(
            file,
            folder,
            MAX_IMAGE_SIZE,
            "image",
        )
    except HTTPException as exc:
        if exc.status_code == 503:
            # Cloudinary not configured on the backend: persist locally.
            return _save_local_image(file, folder)
        raise


def _parse_date_value(value: Optional[str], field_name: str):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            400,
            f"{field_name} must be a valid date in YYYY-MM-DD format",
        )


def _json_value(raw, field_name: str, default=None):
    """Parse a JSON string form field; returns `default` when empty."""
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        raise HTTPException(
            400,
            f"{field_name} must be valid JSON",
        )


# ============================================================
# DASHBOARD STATS
# ============================================================

@router.get("/stats")
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    total_donations = (
        db.query(
            func.sum(Donation.amount)
        )
        .filter(
            Donation.status == "completed"
        )
        .scalar()
        or 0.0
    )

    total_donors = (
        db.query(Donation)
        .filter(
            Donation.status == "completed"
        )
        .count()
    )

    active_causes = (
        db.query(Cause).count()
    )

    inquiries_count = (
        db.query(ContactInquiry).count()
    )

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    total_visitors = (
        db.query(func.count(func.distinct(SiteVisit.visitor_key)))
        .scalar()
        or 0
    )

    visitors_today = (
        db.query(func.count(func.distinct(SiteVisit.visitor_key)))
        .filter(SiteVisit.visit_date == today)
        .scalar()
        or 0
    )

    visitors_this_week = (
        db.query(func.count(func.distinct(SiteVisit.visitor_key)))
        .filter(SiteVisit.visit_date >= week_start)
        .scalar()
        or 0
    )

    return {
        "total_donations": total_donations,
        "total_donors": total_donors,
        "active_causes": active_causes,
        "inquiries_count": inquiries_count,
        "total_visitors": total_visitors,
        "visitors_today": visitors_today,
        "visitors_this_week": visitors_this_week,
    }


# ============================================================
# VISITS ADMIN
# ============================================================

@router.get("/visits")
def get_admin_visits(
    days: int = 30,
    months: int = 6,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Visitor breakdown for the admin: daily counts and monthly totals."""
    days = min(max(days or 30, 7), 90)
    months = min(max(months or 6, 1), 24)

    today = date.today()
    daily_start = today - timedelta(days=days - 1)

    month_start = today.replace(day=1)
    first_month_index = (
        month_start.year * 12
        + (month_start.month - 1)
        - (months - 1)
    )
    month_lower = date(
        first_month_index // 12,
        first_month_index % 12 + 1,
        1,
    )

    rows = (
        db.query(
            SiteVisit.visit_date,
            func.count(func.distinct(SiteVisit.visitor_key)),
        )
        .filter(SiteVisit.visit_date >= month_lower)
        .group_by(SiteVisit.visit_date)
        .all()
    )

    counts_by_day = {
        visit_date: int(count)
        for visit_date, count in rows
    }

    daily = []
    for offset in range(days):
        day = daily_start + timedelta(days=offset)
        daily.append(
            {
                "date": day.isoformat(),
                "count": counts_by_day.get(day, 0),
            }
        )

    month_counts = {}
    for visit_date, count in counts_by_day.items():
        key = f"{visit_date.year:04d}-{visit_date.month:02d}"
        month_counts[key] = month_counts.get(key, 0) + count

    monthly = []
    for offset in range(months):
        ym = (
            month_start.year * 12
            + (month_start.month - 1)
            - offset
        )
        key = f"{ym // 12:04d}-{ym % 12 + 1:02d}"
        monthly.append(
            {
                "month": key,
                "count": month_counts.get(key, 0),
            }
        )
    monthly.reverse()

    total_visitors = (
        db.query(func.count(func.distinct(SiteVisit.visitor_key)))
        .scalar()
        or 0
    )

    return {
        "total_visitors": total_visitors,
        "daily": daily,
        "monthly": monthly,
    }


# ============================================================
# CAUSES ADMIN
# ============================================================

def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return slug or "cause"


def _unique_cause_slug(
    db: Session,
    title: str,
    exclude_id: Optional[int] = None,
) -> str:
    base = _slugify(title)
    slug = base
    counter = 1

    while True:
        query = db.query(Cause).filter(Cause.slug == slug)
        if exclude_id:
            query = query.filter(Cause.id != exclude_id)
        if not query.first():
            return slug
        counter += 1
        slug = f"{base}-{counter}"


@router.get(
    "/causes",
    response_model=List[CauseResponse],
)
def get_admin_causes(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(Cause)
        .order_by(Cause.created_at.desc(), Cause.id.desc())
        .all()
    )


@router.post(
    "/causes",
    response_model=CauseResponse,
)
def create_admin_cause(
    title: str = Form(...),
    short_description: str = Form(...),
    category: Optional[str] = Form(None),
    full_description: Optional[str] = Form(None),
    target_amount: Optional[float] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    title = title.strip()
    short_description = (short_description or "").strip()

    if not title:
        raise HTTPException(400, "Cause title is required")
    if not short_description:
        raise HTTPException(400, "Cause short description is required")

    image_url = None

    if file and file.filename:
        image_url = _upload_image(file, "causes")

    cause = Cause(
        title=title,
        slug=_unique_cause_slug(db, title),
        category=(category or "").strip() or "General",
        short_description=short_description,
        full_description=(full_description or "").strip() or None,
        target_amount=target_amount or 0,
        raised_amount=0.0,
        image_url=image_url,
    )

    db.add(cause)
    db.commit()
    db.refresh(cause)

    return cause


@router.put(
    "/causes/{cause_id}",
    response_model=CauseResponse,
)
def update_admin_cause(
    cause_id: int,
    title: str = Form(...),
    short_description: str = Form(...),
    category: Optional[str] = Form(None),
    full_description: Optional[str] = Form(None),
    target_amount: Optional[float] = Form(None),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    cause = (
        db.query(Cause)
        .filter(Cause.id == cause_id)
        .first()
    )

    if not cause:
        raise HTTPException(404, "Cause not found")

    title = title.strip()
    short_description = (short_description or "").strip()

    if not title:
        raise HTTPException(400, "Cause title is required")
    if not short_description:
        raise HTTPException(400, "Cause short description is required")

    old_image = cause.image_url
    old_title = cause.title

    cause.title = title

    if title != old_title:
        cause.slug = _unique_cause_slug(db, title, exclude_id=cause.id)

    cause.category = (category or "").strip() or "General"
    cause.short_description = short_description
    cause.full_description = (full_description or "").strip() or None
    cause.target_amount = target_amount or 0

    if file and file.filename:
        cause.image_url = _upload_image(file, "causes")
    elif remove_image:
        cause.image_url = None

    db.commit()
    db.refresh(cause)

    if old_image and old_image != cause.image_url:
        _delete_local_file(old_image)
        _delete_cloudinary_file(old_image, "image")

    return cause


@router.delete("/causes/{cause_id}")
def delete_admin_cause(
    cause_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    cause = (
        db.query(Cause)
        .filter(Cause.id == cause_id)
        .first()
    )

    if not cause:
        raise HTTPException(404, "Cause not found")

    old_image = cause.image_url

    db.query(Donation).filter(Donation.cause_id == cause.id).update(
        {Donation.cause_id: None}
    )
    db.delete(cause)
    db.commit()

    _delete_local_file(old_image)
    _delete_cloudinary_file(old_image, "image")

    return {
        "message": "Cause deleted"
    }


# ============================================================
# PHOTO GALLERY ADMIN
# ============================================================

@router.get(
    "/gallery",
    response_model=List[GalleryItemResponse],
)
def get_gallery_items(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(GalleryItem)
        .order_by(
            GalleryItem.created_at.desc(),
            GalleryItem.id.desc(),
        )
        .all()
    )


@router.post(
    "/gallery/upload",
    response_model=List[GalleryItemResponse],
)
def upload_gallery_image(
    title: str = Form(...),
    category: str = Form("Photo Gallery"),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    items = []

    try:
        for file in files:
            _validate_upload(
                file,
                ALLOWED_IMAGE_EXTENSIONS,
                ALLOWED_IMAGE_TYPES,
                MAX_IMAGE_SIZE,
            )

            image_url = _upload_to_cloudinary(
                file,
                "gallery",
                MAX_IMAGE_SIZE,
                "image",
            )

            item = GalleryItem(
                title=title.strip(),
                image_url=image_url,
                category=(category or "").strip() or "Photo Gallery",
                description=(
                    (description or "").strip()
                    or None
                ),
            )

            db.add(item)
            items.append(item)

        db.commit()

        for item in items:
            db.refresh(item)

    except Exception as exc:
        db.rollback()

        if isinstance(exc, HTTPException):
            raise

        raise HTTPException(
            500,
            f"Could not upload images: {exc}",
        ) from exc

    return items


@router.delete(
    "/gallery/{item_id}"
)
def delete_gallery_image(
    item_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = (
        db.query(GalleryItem)
        .filter(GalleryItem.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            404,
            "Gallery image not found",
        )

    old_url = item.image_url

    db.delete(item)
    db.commit()

    _delete_local_file(old_url)
    _delete_cloudinary_file(old_url, "image")

    return {
        "message": "Gallery image deleted"
    }


# ============================================================
# VIDEO GALLERY ADMIN
# ============================================================

@router.get(
    "/videos",
    response_model=List[VideoGalleryResponse],
)
def get_video_items(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(VideoGallery)
        .order_by(
            VideoGallery.created_at.desc(),
            VideoGallery.id.desc(),
        )
        .all()
    )


@router.post(
    "/videos/upload",
    response_model=List[VideoGalleryResponse],
)
def upload_video(
    title: str = Form(...),
    category: str = Form("Video Gallery"),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    items = []

    try:
        for file in files:
            _validate_upload(
                file,
                ALLOWED_VIDEO_EXTENSIONS,
                ALLOWED_VIDEO_TYPES,
                MAX_VIDEO_SIZE,
            )

            video_url = _upload_to_cloudinary(
                file,
                "videos",
                MAX_VIDEO_SIZE,
                "video",
            )

            item = VideoGallery(
                title=title.strip(),
                video_url=video_url,
                category=(category or "").strip() or "Video Gallery",
                description=(
                    (description or "").strip()
                    or None
                ),
            )

            db.add(item)
            items.append(item)

        db.commit()

        for item in items:
            db.refresh(item)

    except Exception as exc:
        db.rollback()

        if isinstance(exc, HTTPException):
            raise

        raise HTTPException(
            500,
            f"Could not upload videos: {exc}",
        ) from exc

    return items


@router.delete(
    "/videos/{video_id}"
)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = (
        db.query(VideoGallery)
        .filter(
            VideoGallery.id == video_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            404,
            "Video not found",
        )

    old_url = item.video_url

    db.delete(item)
    db.commit()

    _delete_local_file(old_url)
    _delete_cloudinary_file(old_url, "video")

    return {
        "message": "Video deleted"
    }


# ============================================================
# GALLERY CATEGORIES
# ============================================================

def _merge_categories(
    defaults: List[str],
    used: List[str],
) -> List[str]:
    result = []
    seen = set()

    for value in defaults + used:
        normalized = (value or "").strip()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        result.append(normalized)

    return result


@router.get(
    "/gallery/categories"
)
def get_gallery_categories(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    used = [
        row[0]
        for row in db.query(
            GalleryItem.category
        )
        .distinct()
        .all()
    ]

    return _merge_categories(
        DEFAULT_GALLERY_CATEGORIES,
        used,
    )


@router.get(
    "/videos/categories"
)
def get_video_categories(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    used = [
        row[0]
        for row in db.query(
            VideoGallery.category
        )
        .distinct()
        .all()
    ]

    return _merge_categories(
        ["Video Gallery"]
        + DEFAULT_GALLERY_CATEGORIES,
        used,
    )


# ============================================================
# UPCOMING PROJECTS ADMIN
# ============================================================

@router.get(
    "/projects",
    response_model=List[UpcomingProjectResponse],
)
def get_projects(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(UpcomingProject)
        .order_by(
            UpcomingProject.expected_date.asc(),
            UpcomingProject.id.desc(),
        )
        .all()
    )


@router.post(
    "/projects",
    response_model=UpcomingProjectResponse,
)
def create_project(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    expected_date: Optional[date] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    image_url = None

    if file and file.filename:
        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        image_url = _upload_to_cloudinary(
            file,
            "projects",
            MAX_IMAGE_SIZE,
            "image",
        )

    project = UpcomingProject(
        title=title.strip(),
        description=(
            (description or "").strip()
            or None
        ),
        image_url=image_url,
        expected_date=expected_date,
        status="upcoming",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.put(
    "/projects/{project_id}",
    response_model=UpcomingProjectResponse,
)
def update_project(
    project_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    expected_date: Optional[date] = Form(None),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    project = (
        db.query(UpcomingProject)
        .filter(
            UpcomingProject.id
            == project_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            404,
            "Project not found",
        )

    old_image = project.image_url

    project.title = title.strip()

    project.description = (
        (description or "").strip()
        or None
    )

    project.expected_date = expected_date
    project.status = "upcoming"

    if file and file.filename:

        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        project.image_url = _upload_to_cloudinary(
            file,
            "projects",
            MAX_IMAGE_SIZE,
            "image",
        )

    elif remove_image:
        project.image_url = None

    db.commit()
    db.refresh(project)

    if (
        old_image
        and old_image != project.image_url
    ):
        _delete_local_file(old_image)
        _delete_cloudinary_file(old_image, "image")

    return project


@router.delete(
    "/projects/{project_id}"
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    project = (
        db.query(UpcomingProject)
        .filter(
            UpcomingProject.id
            == project_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            404,
            "Project not found",
        )

    old_image = project.image_url

    db.delete(project)
    db.commit()

    _delete_local_file(old_image)
    _delete_cloudinary_file(old_image, "image")

    return {
        "message": "Project deleted"
    }

# ============================================================
# TEAM MEMBERS ADMIN
# ============================================================

@router.get(
    "/team",
    response_model=List[TeamMemberResponse],
)
def get_team_members(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(TeamMember)
        .order_by(
            TeamMember.team.asc(),
            TeamMember.created_at.asc(),
            TeamMember.id.asc(),
        )
        .all()
    )


@router.post(
    "/team",
    response_model=TeamMemberResponse,
)
def create_team_member(
    name: str = Form(...),
    role: Optional[str] = Form(None),
    team: str = Form("General"),
    bio: Optional[str] = Form(None),
    member_id: Optional[str] = Form(None),
    joined_date: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    name = name.strip()
    team = (team or "").strip() or "General"
    role = (role or "").strip()
    member_id = (member_id or "").strip()
    email = (email or "").strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Team member name is required",
        )
    if not role:
        raise HTTPException(
            status_code=400,
            detail="Team member role is required",
        )
    if not member_id:
        raise HTTPException(
            status_code=400,
            detail="Team member ID is required",
        )
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Team member email is required",
        )

    existing = (
        db.query(TeamMember)
        .filter(TeamMember.member_id == member_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Team member ID '{member_id}' is already in use",
        )

    photo_url = None

    # Photo is required on creation.
    if file and file.filename:
        photo_url = _upload_image(file, "team")
    else:
        raise HTTPException(
            status_code=400,
            detail="A profile photo is required for team members",
        )

    member = TeamMember(
        name=name,
        role=role,
        team=team,
        photo_url=photo_url,
        bio=(
            (bio or "").strip()
            or None
        ),
        member_id=member_id,
        joined_date=_parse_date_value(joined_date, "joined_date"),
        email=email,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


@router.put(
    "/team/{member_id}",
    response_model=TeamMemberResponse,
)
def update_team_member(
    member_id: int,
    name: str = Form(...),
    role: Optional[str] = Form(None),
    team: str = Form("General"),
    bio: Optional[str] = Form(None),
    member_id_value: Optional[str] = Form(None),
    joined_date: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id)
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Team member not found",
        )

    name = name.strip()
    role = (role or "").strip()
    member_id = (member_id_value or "").strip()
    email = (email or "").strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Team member name is required",
        )
    if not role:
        raise HTTPException(
            status_code=400,
            detail="Team member role is required",
        )
    if not member_id:
        raise HTTPException(
            status_code=400,
            detail="Team member ID is required",
        )
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Team member email is required",
        )

    duplicate = (
        db.query(TeamMember)
        .filter(
            TeamMember.member_id == member_id,
            TeamMember.id != member.id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=400,
            detail=f"Team member ID '{member_id}' is already in use",
        )

    old_photo = member.photo_url

    member.name = name
    member.role = role
    member.team = (team or "").strip() or "General"
    member.bio = (bio or "").strip() or None
    member.member_id = member_id
    member.joined_date = _parse_date_value(joined_date, "joined_date")
    member.email = email

    if file and file.filename:
        member.photo_url = _upload_image(file, "team")
    elif remove_image:
        raise HTTPException(
            status_code=400,
            detail="Replacing or removing the photo requires uploading a new one. "
            "A profile photo is required for team members.",
        )

    db.commit()
    db.refresh(member)

    if old_photo and old_photo != member.photo_url:
        _delete_local_file(old_photo)
        _delete_cloudinary_file(old_photo, "image")

    return member


@router.delete(
    "/team/{member_id}",
)
def delete_team_member(
    member_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    member = (
        db.query(TeamMember)
        .filter(
            TeamMember.id == member_id
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Team member not found",
        )

    old_photo = member.photo_url

    db.delete(member)
    db.commit()

    _delete_local_file(old_photo)
    _delete_cloudinary_file(old_photo, "image")

    return {
        "message": "Team member deleted"
    }


# ============================================================
# TEAM MEMBER ID CARD
# ============================================================

def _ensure_member_id(member: TeamMember) -> str:
    if member.member_id:
        return member.member_id
    return f"PWF-TM-{member.id:04d}"


def _render_team_card_bytes(member: TeamMember) -> bytes:
    member.member_id = _ensure_member_id(member)
    photo_bytes, _ = load_profile_photo(member.photo_url or "")
    qr_png = build_volunteer_qr_png(member.member_id)
    try:
        return build_team_card_jpg(
            full_name=member.name,
            member_id=member.member_id,
            role=member.role or "",
            team=member.team or "General",
            joined_date=member.joined_date,
            photo_bytes=photo_bytes,
            qr_png=qr_png,
        )
    except Exception as exc:
        raise HTTPException(500, f"Could not render team member card: {exc}") from exc


@router.get(
    "/team/{member_id}/card",
)
def get_team_member_card_bytes(
    member_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Return the rendered team member ID card as a downloadable JPEG."""
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id)
        .first()
    )

    if not member:
        raise HTTPException(404, "Team member not found")

    data = _render_team_card_bytes(member)
    db.commit()

    from fastapi.responses import Response

    slug = member.member_id or f"team-{member.id}"
    return Response(
        content=data,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{slug}-id-card.jpg"'
        },
    )


@router.post(
    "/team/{member_id}/card/send",
)
def email_team_member_card(
    member_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id)
        .first()
    )

    if not member:
        raise HTTPException(404, "Team member not found")

    if not member.email:
        raise HTTPException(
            400,
            "This team member has no e-mail address on file. Please add one first.",
        )

    member.member_id = _ensure_member_id(member)
    data = _render_team_card_bytes(member)
    db.commit()

    sent = send_team_card_email(
        to_email=member.email,
        recipient_name=member.name,
        member_id=member.member_id,
        image_bytes=data,
    )

    if not sent:
        raise HTTPException(
            502,
            "Card was rendered but the e-mail could not be sent. "
            "Check that BREVO_API_KEY is configured.",
        )

    return {
        "message": f"Team member ID card emailed to {member.email}",
    }


# ============================================================
# CERTIFICATES ADMIN
# ============================================================

@router.get(
    "/certificates",
    response_model=List[CertificateResponse],
)
def get_certificates(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(Certificate)
        .order_by(
            Certificate.created_at.desc(),
            Certificate.id.desc(),
        )
        .all()
    )


@router.post(
    "/certificates",
    response_model=CertificateResponse,
)
def create_certificate(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    title = title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Certificate title is required",
        )

    image_url = None

    if file and file.filename:
        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        image_url = _upload_to_cloudinary(
            file,
            "certificates",
            MAX_IMAGE_SIZE,
            "image",
        )

    certificate = Certificate(
        title=title,
        image_url=image_url,
        description=(
            (description or "").strip()
            or None
        ),
    )

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return certificate


@router.put(
    "/certificates/{certificate_id}",
    response_model=CertificateResponse,
)
def update_certificate(
    certificate_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.id == certificate_id
        )
        .first()
    )

    if not certificate:
        raise HTTPException(
            404,
            "Certificate not found",
        )

    title = title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Certificate title is required",
        )

    old_image = certificate.image_url

    certificate.title = title

    certificate.description = (
        (description or "").strip()
        or None
    )

    if file and file.filename:
        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        certificate.image_url = _upload_to_cloudinary(
            file,
            "certificates",
            MAX_IMAGE_SIZE,
            "image",
        )

    elif remove_image:
        certificate.image_url = None

    db.commit()
    db.refresh(certificate)

    if (
        old_image
        and old_image != certificate.image_url
    ):
        _delete_local_file(old_image)
        _delete_cloudinary_file(old_image, "image")

    return certificate


@router.delete(
    "/certificates/{certificate_id}",
)
def delete_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.id == certificate_id
        )
        .first()
    )

    if not certificate:
        raise HTTPException(
            404,
            "Certificate not found",
        )

    old_image = certificate.image_url

    db.delete(certificate)
    db.commit()

    _delete_local_file(old_image)
    _delete_cloudinary_file(old_image, "image")

    return {
        "message": "Certificate deleted"
    }


# ============================================================
# VOLUNTEER APPLICATIONS ADMIN
# ============================================================

VALID_VOLUNTEER_STATUSES = {
    "pending",
    "accepted",
    "rejected",
}


def _issue_volunteer_id(volunteer: VolunteerApplication) -> str:
    if volunteer.volunteer_id:
        return volunteer.volunteer_id
    return f"PWF-{date.today().year}-{volunteer.id:04d}"


def _send_volunteer_welcome_card_background(volunteer_id: int) -> None:
    """Background task that emails an accepted volunteer's welcome card.

    Runs after the PATCH response is sent and opens its own DB session,
    because the request-scoped session is closed by then. Never raises.
    """
    db = SessionLocal()
    try:
        volunteer = (
            db.query(VolunteerApplication)
            .filter(VolunteerApplication.id == volunteer_id)
            .first()
        )
        if not volunteer:
            logger.error(
                "Welcome card background task: volunteer %s not found",
                volunteer_id,
            )
            return

        if volunteer.status != "accepted":
            logger.warning(
                "Welcome card background task: volunteer %s is %s, skipping",
                volunteer_id,
                volunteer.status,
            )
            return

        if volunteer.card_sent_at:
            logger.info(
                "Welcome card already sent for volunteer %s",
                volunteer_id,
            )
            return

        volunteer_id = _issue_volunteer_id(volunteer)

        # Use only the official Volunteer ID card generated from the registered
        # template, which already includes the uploaded profile photo, admin
        # entered location/validity data, and QR verification.
        official_card_jpg = None
        try:
            from ..document_service import build_volunteer_card, render_volunteer_card_jpeg
            from ..qrcode_util import verify_url

            if not volunteer.card_file_path:
                build_volunteer_card(
                    db,
                    volunteer,
                    location=volunteer.location,
                    status="accepted",
                )
            else:
                # Persist a fresh render so the file always matches the record.
                volunteer.card_qr_token = volunteer.card_qr_token or generate_qr_token()
                from pathlib import Path as _Path

                card_path = _Path(volunteer.card_file_path)
                saved_path = _Path(__file__).resolve().parents[2] / "media" / (
                    str(card_path).removeprefix("/media/").removeprefix("media/")
                )
                saved_path.parent.mkdir(parents=True, exist_ok=True)
                saved_path.write_bytes(render_volunteer_card_jpeg(volunteer))
                db.commit()
            official_card_jpg = _read_media_file(volunteer.card_file_path)
            official_card_pdf = None
            if volunteer.card_file_path:
                official_card_pdf = _read_media_file(
                    volunteer.card_file_path.replace(".jpg", ".pdf")
                )
            volunteer_verify_url = verify_url(
                "volunteer", volunteer.card_qr_token or volunteer_id
            )
        except Exception as exc:
            logger.error(
                "Failed to generate official volunteer ID card for %s: %s",
                volunteer_id,
                exc,
            )
            official_card_jpg = None
            volunteer_verify_url = None

        log_rss("volunteer welcome email before")
        sent = send_volunteer_welcome_email(
            to_email=volunteer.email,
            volunteer_name=volunteer.full_name,
            volunteer_email=volunteer.email,
            volunteer_id=volunteer_id,
            joined_date=datetime.utcnow(),
            id_card_jpg=official_card_jpg,
            id_card_pdf=official_card_pdf,
            verification_url=volunteer_verify_url,
        )
        log_rss("volunteer welcome email after")

        if sent:
            volunteer.card_sent_at = datetime.utcnow()
            db.commit()
            logger.info("Welcome card emailed to volunteer %s", volunteer_id)
        else:
            logger.error(
                "Welcome card email FAILED for volunteer %s (status left as accepted; use resend-card)",
                volunteer_id,
            )
    except Exception as exc:
        db.rollback()
        logger.error(
            "Unexpected error in welcome card background task for volunteer %s: %s",
            volunteer_id,
            exc,
        )
    finally:
        db.close()


def _send_volunteer_rejection_email(
    db: Session,
    volunteer: VolunteerApplication,
) -> None:
    """Email the applicant that their application was rejected.

    Sets volunteer.rejection_email_sent_at only when the email was delivered.
    Never raises; failures are logged so the admin can retry later.
    """
    sent = send_volunteer_rejection_email(
        to_email=volunteer.email,
        volunteer_name=volunteer.full_name,
        interest_area=volunteer.interest_area,
    )

    if sent:
        volunteer.rejection_email_sent_at = datetime.utcnow()

    db.commit()
    db.refresh(volunteer)


def _send_volunteer_rejection_email_background(volunteer_id: int) -> None:
    """Background task that emails a rejected volunteer the notification.

    Runs after the PATCH response is sent and opens its own DB session.
    Never raises.
    """
    db = SessionLocal()
    try:
        volunteer = (
            db.query(VolunteerApplication)
            .filter(VolunteerApplication.id == volunteer_id)
            .first()
        )
        if not volunteer:
            logger.error(
                "Rejection email background task: volunteer %s not found",
                volunteer_id,
            )
            return

        if volunteer.status != "rejected":
            logger.warning(
                "Rejection email background task: volunteer %s is %s, skipping",
                volunteer_id,
                volunteer.status,
            )
            return

        if volunteer.rejection_email_sent_at:
            logger.info(
                "Rejection email already sent for volunteer %s",
                volunteer_id,
            )
            return

        _send_volunteer_rejection_email(db, volunteer)
    except Exception as exc:
        db.rollback()
        logger.error(
            "Unexpected error in rejection email background task for volunteer %s: %s",
            volunteer_id,
            exc,
        )
    finally:
        db.close()


@router.get(
    "/volunteers",
    response_model=List[VolunteerApplicationResponse],
)
def get_volunteer_applications(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(VolunteerApplication)
        .order_by(
            VolunteerApplication.created_at.desc(),
            VolunteerApplication.id.desc(),
        )
        .all()
    )


@router.patch(
    "/volunteers/{volunteer_id}/status",
    response_model=VolunteerApplicationResponse,
)
def update_volunteer_status(
    volunteer_id: int,
    status_value: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    volunteer = (
        db.query(VolunteerApplication)
        .filter(VolunteerApplication.id == volunteer_id)
        .first()
    )

    if not volunteer:
        raise HTTPException(
            404,
            "Volunteer application not found",
        )

    if status_value not in VALID_VOLUNTEER_STATUSES:
        raise HTTPException(
            400,
            f"Invalid status. Choose one of: "
            f"{', '.join(sorted(VALID_VOLUNTEER_STATUSES))}",
        )

    volunteer.status = status_value

    if status_value == "accepted":
        volunteer.volunteer_id = _issue_volunteer_id(volunteer)

    db.commit()
    db.refresh(volunteer)

    if status_value == "accepted" and not volunteer.card_sent_at:
        background_tasks.add_task(
            _send_volunteer_welcome_card_background,
            volunteer.id,
        )
    elif (
        status_value == "rejected"
        and not volunteer.rejection_email_sent_at
    ):
        background_tasks.add_task(
            _send_volunteer_rejection_email_background,
            volunteer.id,
        )

    card_emailed = (
        status_value == "accepted" and volunteer.card_sent_at is not None
    )

    db.commit()
    db.refresh(volunteer)

    data = VolunteerApplicationResponse.model_validate(volunteer).model_dump()
    data["card_emailed"] = card_emailed
    return data


@router.post(
    "/volunteers/{volunteer_id}/resend-card",
    response_model=VolunteerApplicationResponse,
)
def resend_volunteer_welcome_card(
    volunteer_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    volunteer = (
        db.query(VolunteerApplication)
        .filter(VolunteerApplication.id == volunteer_id)
        .first()
    )

    if not volunteer:
        raise HTTPException(
            404,
            "Volunteer application not found",
        )

    if volunteer.status != "accepted":
        raise HTTPException(
            400,
            "Welcome cards can only be sent to accepted volunteers.",
        )

    volunteer.volunteer_id = _issue_volunteer_id(volunteer)
    db.commit()
    db.refresh(volunteer)

    background_tasks.add_task(
        _send_volunteer_welcome_card_background,
        volunteer.id,
    )

    data = VolunteerApplicationResponse.model_validate(volunteer).model_dump()
    data["card_emailed"] = False
    return data


@router.post(
    "/volunteers/{volunteer_id}/resend-rejection-email",
    response_model=VolunteerApplicationResponse,
)
def resend_volunteer_rejection_email(
    volunteer_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    volunteer = (
        db.query(VolunteerApplication)
        .filter(VolunteerApplication.id == volunteer_id)
        .first()
    )

    if not volunteer:
        raise HTTPException(
            404,
            "Volunteer application not found",
        )

    if volunteer.status != "rejected":
        raise HTTPException(
            400,
            "Rejection emails can only be sent to rejected volunteers.",
        )

    background_tasks.add_task(
        _send_volunteer_rejection_email_background,
        volunteer.id,
    )

    return volunteer


@router.delete(
    "/volunteers/{volunteer_id}",
)
def delete_volunteer_application(
    volunteer_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    volunteer = (
        db.query(VolunteerApplication)
        .filter(VolunteerApplication.id == volunteer_id)
        .first()
    )

    if not volunteer:
        raise HTTPException(
            404,
            "Volunteer application not found",
        )

    old_photo = volunteer.profile_pic_url

    db.delete(volunteer)
    db.commit()

    if old_photo:
        _delete_local_file(old_photo)
        _delete_cloudinary_file(old_photo, "image")

    return {
        "message": "Volunteer application deleted"
    }


# ============================================================
# DONATIONS ADMIN
# ============================================================

@router.get(
    "/donations",
    response_model=DonationListResponse,
)
def get_admin_donations(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    page = max(1, page)
    page_size = min(100, max(1, page_size))

    query = (
        db.query(Donation)
        .order_by(Donation.created_at.desc(), Donation.id.desc())
    )

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post(
    "/donations/{donation_id}/resend-receipt",
    response_model=DonationResponse,
)
def resend_donation_documents(
    donation_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    from .donation import _email_donation_documents

    donation = (
        db.query(Donation)
        .filter(Donation.id == donation_id)
        .first()
    )

    if not donation:
        raise HTTPException(404, "Donation record not found")

    if donation.status != "completed":
        raise HTTPException(
            400,
            "Receipts can only be sent for completed donations.",
        )

    payment_id = donation.razorpay_payment_id or ""
    _email_donation_documents(donation, payment_id)

    db.commit()
    db.refresh(donation)

    return donation


@router.get("/donations/{donation_id}/email-preview")
def donation_email_preview(
    donation_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Return the exact HTML receipt that is emailed to the donor.

    Used by the admin panel to show what the donor receives in the mail
    (in place of a separate "invoice" download).
    """
    donation = (
        db.query(Donation)
        .filter(Donation.id == donation_id)
        .first()
    )

    if not donation:
        raise HTTPException(404, "Donation record not found")

    html_body = build_donation_receipt_html(
        full_name=donation.donor_name,
        email=donation.donor_email,
        phone=donation.donor_phone or "",
        amount=donation.amount,
        order_id=donation.razorpay_order_id or "",
        payment_id=donation.razorpay_payment_id or "",
        paid_at=donation.created_at,
    )

    return {
        "donation_id": donation.id,
        "html": html_body,
        "receipt_pdf_url": donation.invoice_document_path,
    }


# ============================================================
# ABOUT - FOUNDER & MENTORS
# ============================================================

def _founder_or_default(db: Session) -> FounderProfile:
    founder = db.query(FounderProfile).order_by(FounderProfile.id.asc()).first()
    if not founder:
        founder = FounderProfile(
            name="Pushkar Kumar",
            role="Founder",
            eyebrow="Our Founder's Vision",
            title="From Corporate Success to Rural Transformation",
            image_alt="Founder of Piplad Welfare Foundation",
        )
        db.add(founder)
        db.commit()
        db.refresh(founder)
    return founder


@router.get(
    "/about/founder",
    response_model=FounderProfileResponse,
)
def get_admin_founder(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return _founder_or_default(db)


@router.put(
    "/about/founder",
    response_model=FounderProfileResponse,
)
def update_admin_founder(
    name: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    eyebrow: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    image_alt: Optional[str] = Form(None),
    introduction: Optional[str] = Form(None),
    story: Optional[str] = Form(None),
    vision: Optional[str] = Form(None),
    quote: Optional[str] = Form(None),
    milestones: Optional[str] = Form(None),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    founder = _founder_or_default(db)
    old_image = founder.image_url

    if name is not None:
        founder.name = name.strip() or "Pushkar Kumar"
    if role is not None:
        founder.role = role.strip() or None
    if eyebrow is not None:
        founder.eyebrow = eyebrow.strip() or None
    if title is not None:
        founder.title = title.strip() or None
    if image_alt is not None:
        founder.image_alt = image_alt.strip() or None
    if introduction is not None:
        founder.introduction = introduction.strip() or None
    if story is not None:
        founder.story = story.strip() or None
    if vision is not None:
        founder.vision = vision.strip() or None
    if quote is not None:
        founder.quote = quote.strip() or None

    if file and file.filename:
        founder.image_url = _upload_image(file, "about")
    elif remove_image:
        founder.image_url = None

    if milestones is not None:
        parsed = _json_value(milestones, "milestones", []) or []
        for milestone in founder.milestones:
            db.delete(milestone)
        db.flush()
        for index, item in enumerate(parsed):
            db.add(
                FounderMilestone(
                    founder_id=founder.id,
                    year=str(item.get("year") or f"{index + 1:02d}"),
                    title=str(item.get("title") or "").strip(),
                    description=str(item.get("description") or "").strip() or None,
                    display_order=int(item.get("display_order", index)),
                )
            )

    db.commit()
    db.refresh(founder)

    if old_image and old_image != founder.image_url:
        _delete_local_file(old_image)
        _delete_cloudinary_file(old_image, "image")

    return founder


@router.get(
    "/about/mentors",
    response_model=List[MentorResponse],
)
def get_admin_mentors(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(Mentor)
        .order_by(Mentor.display_order.asc(), Mentor.id.asc())
        .all()
    )


@router.post(
    "/about/mentors",
    response_model=MentorResponse,
)
def create_admin_mentor(
    name: str = Form(...),
    role: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    quote: Optional[str] = Form(None),
    display_order: int = Form(0),
    is_published: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    name = name.strip()
    if not name:
        raise HTTPException(400, "Mentor name is required")

    image_url = None
    if file and file.filename:
        image_url = _upload_image(file, "about")

    mentor = Mentor(
        name=name,
        role=(role or "").strip() or None,
        image_url=image_url,
        description=(description or "").strip() or None,
        quote=(quote or "").strip() or None,
        display_order=display_order,
        is_published=is_published,
    )
    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    return mentor


@router.put(
    "/about/mentors/{mentor_id}",
    response_model=MentorResponse,
)
def update_admin_mentor(
    mentor_id: int,
    name: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    quote: Optional[str] = Form(None),
    display_order: int = Form(0),
    is_published: bool = Form(True),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    mentor = (
        db.query(Mentor)
        .filter(Mentor.id == mentor_id)
        .first()
    )
    if not mentor:
        raise HTTPException(404, "Mentor not found")

    old_image = mentor.image_url

    if name is not None:
        mentor.name = name.strip() or mentor.name
    if role is not None:
        mentor.role = role.strip() or None
    if description is not None:
        mentor.description = description.strip() or None
    if quote is not None:
        mentor.quote = quote.strip() or None
    mentor.display_order = display_order
    mentor.is_published = is_published

    if file and file.filename:
        mentor.image_url = _upload_image(file, "about")
    elif remove_image:
        mentor.image_url = None

    db.commit()
    db.refresh(mentor)

    if old_image and old_image != mentor.image_url:
        _delete_local_file(old_image)
        _delete_cloudinary_file(old_image, "image")

    return mentor


@router.delete("/about/mentors/{mentor_id}")
def delete_admin_mentor(
    mentor_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    mentor = (
        db.query(Mentor)
        .filter(Mentor.id == mentor_id)
        .first()
    )
    if not mentor:
        raise HTTPException(404, "Mentor not found")

    old_image = mentor.image_url
    db.delete(mentor)
    db.commit()

    _delete_local_file(old_image)
    _delete_cloudinary_file(old_image, "image")

    return {"message": "Mentor deleted"}


# ============================================================
# FOOTER FOCUS
# ============================================================

@router.get(
    "/footer-focus",
    response_model=List[FooterFocusItemResponse],
)
def get_footer_focus_items(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(FooterFocusItem)
        .order_by(FooterFocusItem.display_order.asc(), FooterFocusItem.id.asc())
        .all()
    )


@router.post(
    "/footer-focus",
    response_model=FooterFocusItemResponse,
)
def create_footer_focus_item(
    text: str = Form(...),
    display_order: int = Form(0),
    is_published: bool = Form(True),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    text = text.strip()
    if not text:
        raise HTTPException(400, "Focus item text is required")

    item = FooterFocusItem(
        text=text,
        display_order=display_order,
        is_published=is_published,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put(
    "/footer-focus/{item_id}",
    response_model=FooterFocusItemResponse,
)
def update_footer_focus_item(
    item_id: int,
    text: str = Form(...),
    display_order: int = Form(0),
    is_published: bool = Form(True),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = (
        db.query(FooterFocusItem)
        .filter(FooterFocusItem.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(404, "Footer focus item not found")

    text = text.strip()
    if not text:
        raise HTTPException(400, "Focus item text is required")

    item.text = text
    item.display_order = display_order
    item.is_published = is_published
    db.commit()
    db.refresh(item)
    return item


@router.post("/footer-focus/reorder")
def reorder_footer_focus(
    body: dict,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    order = body.get("order") or []
    for position, item_id in enumerate(order):
        item = (
            db.query(FooterFocusItem)
            .filter(FooterFocusItem.id == int(item_id))
            .first()
        )
        if item:
            item.display_order = position
    db.commit()
    return {"message": "Footer focus reordered"}


@router.delete("/footer-focus/{item_id}")
def delete_footer_focus_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = (
        db.query(FooterFocusItem)
        .filter(FooterFocusItem.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(404, "Footer focus item not found")

    db.delete(item)
    db.commit()
    return {"message": "Footer focus item deleted"}


# ============================================================
# FOOTER QUICK LINKS (admin)
# ============================================================

@router.get(
    "/footer-links",
    response_model=List[FooterQuickLinkResponse],
)
def get_footer_quick_links(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(FooterQuickLink)
        .order_by(FooterQuickLink.display_order.asc(), FooterQuickLink.id.asc())
        .all()
    )


@router.post(
    "/footer-links",
    response_model=FooterQuickLinkResponse,
)
def create_footer_quick_link(
    label: str = Form(...),
    path: str = Form(...),
    display_order: int = Form(0),
    is_published: bool = Form(True),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    label = label.strip()
    path = path.strip()
    if not label:
        raise HTTPException(400, "Link label is required")
    if not path:
        raise HTTPException(400, "Link path is required")

    link = FooterQuickLink(
        label=label,
        path=path,
        display_order=display_order,
        is_published=is_published,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.put(
    "/footer-links/{link_id}",
    response_model=FooterQuickLinkResponse,
)
def update_footer_quick_link(
    link_id: int,
    label: str = Form(...),
    path: str = Form(...),
    display_order: int = Form(0),
    is_published: bool = Form(True),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    link = (
        db.query(FooterQuickLink)
        .filter(FooterQuickLink.id == link_id)
        .first()
    )
    if not link:
        raise HTTPException(404, "Footer quick link not found")

    label = label.strip()
    path = path.strip()
    if not label:
        raise HTTPException(400, "Link label is required")
    if not path:
        raise HTTPException(400, "Link path is required")

    link.label = label
    link.path = path
    link.display_order = display_order
    link.is_published = is_published
    db.commit()
    db.refresh(link)
    return link


@router.post("/footer-links/reorder")
def reorder_footer_quick_links(
    body: dict,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    order = body.get("order") or []
    for position, link_id in enumerate(order):
        link = (
            db.query(FooterQuickLink)
            .filter(FooterQuickLink.id == int(link_id))
            .first()
        )
        if link:
            link.display_order = position
    db.commit()
    return {"message": "Footer quick links reordered"}


@router.delete("/footer-links/{link_id}")
def delete_footer_quick_link(
    link_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    link = (
        db.query(FooterQuickLink)
        .filter(FooterQuickLink.id == link_id)
        .first()
    )
    if not link:
        raise HTTPException(404, "Footer quick link not found")

    db.delete(link)
    db.commit()
    return {"message": "Footer quick link deleted"}
