"""Home-page hero slide management.

- ``GET /api/home/slides``          -> public, ordered, only active slides
- ``GET /api/admin/home/slides``    -> admin, all slides in display order
- ``POST /api/admin/home/slides``   -> admin, create a slide (image + text)
- ``PUT /api/admin/home/slides/{id}`` -> admin, edit a slide (image optional)
- ``DELETE /api/admin/home/slides/{id}`` -> admin, delete a slide
- ``POST /api/admin/home/slides/reorder`` -> admin, reorder slides by ids
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import HomeSlide
from ..schemas import HomeSlideResponse
from .admin import (
    _delete_cloudinary_file,
    _delete_local_file,
    _upload_image,
    get_current_admin,
)

router = APIRouter(tags=["Home"])


def _slide_visible(slide: HomeSlide) -> bool:
    return bool(slide.is_active) and bool(slide.title.strip())


# ============================================================
# PUBLIC
# ============================================================

@router.get("/api/home/slides", response_model=List[HomeSlideResponse])
def get_public_home_slides(db: Session = Depends(get_db)):
    slides = (
        db.query(HomeSlide)
        .filter(HomeSlide.is_active.is_(True))
        .order_by(HomeSlide.display_order.asc(), HomeSlide.id.asc())
        .all()
    )
    return [slide for slide in slides if _slide_visible(slide)]


# ============================================================
# ADMIN
# ============================================================

@router.get("/api/admin/home/slides", response_model=List[HomeSlideResponse])
def get_admin_home_slides(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(HomeSlide)
        .order_by(HomeSlide.display_order.asc(), HomeSlide.id.asc())
        .all()
    )


def _parse_bool(value: Optional[str], field_name: str) -> bool:
    if value is None or str(value).strip() == "":
        return True
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise HTTPException(400, f"{field_name} must be a boolean (true/false)")


def _clean_form_value(value: Optional[str]) -> str:
    return (value or "").strip()


def _clean_image_url(value: Optional[str]) -> Optional[str]:
    cleaned = _clean_form_value(value)
    if not cleaned:
        return None
    if cleaned.startswith(("http://", "https://", "/")):
        return cleaned
    return None


@router.post("/api/admin/home/slides", response_model=HomeSlideResponse)
def create_home_slide(
    title: str = Form(...),
    eyebrow: Optional[str] = Form(None),
    highlight: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    display_order: Optional[int] = Form(0),
    is_active: Optional[str] = Form("true"),
    image: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    clean_title = _clean_form_value(title)
    if not clean_title:
        raise HTTPException(400, "Slide title is required.")

    slide_image_url = None
    if image is not None and image.filename:
        slide_image_url = _upload_image(image, "home")
    else:
        slide_image_url = _clean_image_url(image_url)

    if display_order and display_order > 0:
        next_order = int(display_order)
    else:
        last = (
            db.query(HomeSlide)
            .order_by(HomeSlide.display_order.desc())
            .first()
        )
        next_order = (last.display_order + 1) if last else 1

    slide = HomeSlide(
        eyebrow=_clean_form_value(eyebrow),
        title=clean_title,
        highlight=_clean_form_value(highlight),
        text=_clean_form_value(text),
        image_url=slide_image_url,
        display_order=next_order,
        is_active=_parse_bool(is_active, "is_active"),
    )

    db.add(slide)
    db.commit()
    db.refresh(slide)

    return slide


@router.put("/api/admin/home/slides/{slide_id}", response_model=HomeSlideResponse)
def update_home_slide(
    slide_id: int,
    title: Optional[str] = Form(None),
    eyebrow: Optional[str] = Form(None),
    highlight: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    display_order: Optional[int] = Form(None),
    is_active: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    slide = (
        db.query(HomeSlide)
        .filter(HomeSlide.id == slide_id)
        .first()
    )

    if not slide:
        raise HTTPException(404, "Home slide not found.")

    if title is not None:
        clean_title = _clean_form_value(title)
        if not clean_title:
            raise HTTPException(400, "Slide title is required.")
        slide.title = clean_title

    if eyebrow is not None:
        slide.eyebrow = _clean_form_value(eyebrow)

    if highlight is not None:
        slide.highlight = _clean_form_value(highlight)

    if text is not None:
        slide.text = _clean_form_value(text)

    if display_order is not None:
        slide.display_order = int(display_order)

    if is_active is not None:
        slide.is_active = _parse_bool(is_active, "is_active")

    if image is not None and image.filename:
        old_url = slide.image_url
        slide.image_url = _upload_image(image, "home")
        if old_url and old_url != slide.image_url:
            _delete_local_file(old_url)
            _delete_cloudinary_file(old_url, "image")
    elif image_url is not None:
        resolved_url = _clean_image_url(image_url)
        if resolved_url != slide.image_url:
            old_url = slide.image_url
            slide.image_url = resolved_url
            if old_url and resolved_url:
                _delete_local_file(old_url)
                _delete_cloudinary_file(old_url, "image")

    db.commit()
    db.refresh(slide)

    return slide


@router.delete("/api/admin/home/slides/{slide_id}")
def delete_home_slide(
    slide_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    slide = (
        db.query(HomeSlide)
        .filter(HomeSlide.id == slide_id)
        .first()
    )

    if not slide:
        raise HTTPException(404, "Home slide not found.")

    old_url = slide.image_url

    db.delete(slide)
    db.commit()

    _delete_local_file(old_url)
    _delete_cloudinary_file(old_url, "image")

    return {
        "message": "Home slide deleted",
    }


@router.post("/api/admin/home/slides/reorder")
def reorder_home_slides(
    ordered_ids: List[int],
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    existing = {
        slide.id: slide
        for slide in db.query(HomeSlide).all()
    }

    for index, slide_id in enumerate(ordered_ids):
        slide = existing.get(slide_id)

        if slide is None:
            continue

        slide.display_order = index

    db.commit()

    return (
        db.query(HomeSlide)
        .order_by(HomeSlide.display_order.asc(), HomeSlide.id.asc())
        .all()
    )