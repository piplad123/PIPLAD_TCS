from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import GalleryItem, UpcomingProject, VideoGallery
from ..schemas import (
    GalleryItemResponse,
    UpcomingProjectResponse,
    VideoGalleryResponse,
)

router = APIRouter(tags=["Media & Awards"])


@router.get("/api/gallery", response_model=List[GalleryItemResponse])
def get_public_gallery(db: Session = Depends(get_db)):
    """Return all administrator-managed photo-gallery images."""
    return (
        db.query(GalleryItem)
        .order_by(GalleryItem.created_at.desc(), GalleryItem.id.desc())
        .all()
    )


@router.get("/api/videos", response_model=List[VideoGalleryResponse])
def get_public_videos(db: Session = Depends(get_db)):
    """Return administrator-managed videos."""
    return (
        db.query(VideoGallery)
        .order_by(VideoGallery.created_at.desc(), VideoGallery.id.desc())
        .all()
    )


@router.get("/api/projects", response_model=List[UpcomingProjectResponse])
def get_public_projects(
    status: str = Query("upcoming", pattern="^(upcoming)$"),
    db: Session = Depends(get_db),
):
    """Publicly expose upcoming projects only."""
    return (
        db.query(UpcomingProject)
        .filter(UpcomingProject.status == status)
        .order_by(UpcomingProject.expected_date.asc(), UpcomingProject.id.desc())
        .all()
    )
