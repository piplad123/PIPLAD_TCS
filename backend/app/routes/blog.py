from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Blog
from ..schemas import BlogResponse


router = APIRouter(
    prefix="/api/blog",
    tags=["Blog"]
)


@router.get("", response_model=List[BlogResponse])
def get_blog_posts(
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Return all published blog posts ordered by publication date.
    Optional ``category`` and free-text ``q`` (title/summary) filters.
    Posts without a ``published_date`` are drafts and stay hidden.
    """

    query = db.query(Blog).filter(Blog.published_date.isnot(None))

    if category:
        query = query.filter(Blog.category == category)

    if q:
        search = f"%{q.strip()}%"
        query = query.filter(
            (Blog.title.ilike(search)) | (Blog.summary.ilike(search))
        )

    return query.order_by(Blog.published_date.desc()).all()


@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog_post(
    blog_id: int,
    db: Session = Depends(get_db)
):
    """
    Return a single published blog post by ID.
    Drafts (no ``published_date``) are treated as not found.
    """

    post = (
        db.query(Blog)
        .filter(Blog.id == blog_id, Blog.published_date.isnot(None))
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Blog post not found"
        )

    return post