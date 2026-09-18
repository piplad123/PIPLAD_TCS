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
    Return all blog posts ordered by publication date.
    Optional ``category`` and free-text ``q`` (title/summary) filters.
    """

    query = db.query(Blog)

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
    Return a single blog post by ID.
    """

    post = (
        db.query(Blog)
        .filter(Blog.id == blog_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Blog post not found"
        )

    return post