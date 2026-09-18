from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import FooterFocusItem, FooterQuickLink, FounderProfile, Mentor
from ..schemas import (
    FooterFocusItemResponse,
    FooterQuickLinkResponse,
    FounderProfileResponse,
    MentorResponse,
)

router = APIRouter(prefix="/api/about", tags=["About"])

_DEFAULT_FOUNDER = FounderProfileResponse(
    id=0,
    name="Pushkar Kumar",
    role="Founder",
    eyebrow="Our Founder's Vision",
    title="From Corporate Success to Rural Transformation",
    image_alt="Founder of Piplad Welfare Foundation",
    introduction=(
        "Pushkar Kumar believes that every village holds untapped potential and every child "
        "deserves a fair chance. After earning a B.Tech from SRM University and building a "
        "career in the IT sector, he chose to dedicate himself to rural development."
    ),
    story=(
        "His journey is rooted in a deep understanding of the gap between aspiration and "
        "opportunity. His experience with rural communities shaped a vision where education, "
        "healthcare, livelihoods and technology work together to create meaningful change."
    ),
    vision=(
        "The vision is to build digitally connected villages where children can access quality "
        "education, young people can gain market-ready skills, families can access healthcare, "
        "farmers can adopt climate-smart practices and communities can preserve their cultural identity."
    ),
    quote=(
        "The aim is to turn potential into prosperity — one village, one student, one livelihood at a time."
    ),
    milestones=[
        {
            "id": 0,
            "year": "01",
            "title": "Technology",
            "description": "Building technology-enabled solutions for communities with limited connectivity.",
        },
        {
            "id": 0,
            "year": "02",
            "title": "Education",
            "description": "Creating accessible learning pathways for rural students and educators.",
        },
        {
            "id": 0,
            "year": "03",
            "title": "Livelihoods",
            "description": "Connecting rural youth with skills, employment and entrepreneurship opportunities.",
        },
        {
            "id": 0,
            "year": "04",
            "title": "Transformation",
            "description": "Creating resilient communities through partnerships and measurable impact.",
        },
    ],
)


@router.get("/founder", response_model=FounderProfileResponse)
def get_founder_profile(db: Session = Depends(get_db)):
    founder = db.query(FounderProfile).order_by(FounderProfile.id.asc()).first()
    if not founder:
        return _DEFAULT_FOUNDER
    return founder


@router.get("/mentors", response_model=List[MentorResponse])
def get_mentors(db: Session = Depends(get_db)):
    return (
        db.query(Mentor)
        .filter(Mentor.is_published == True)  # noqa: E712
        .order_by(Mentor.display_order.asc(), Mentor.id.asc())
        .all()
    )


@router.get("/footer-focus", response_model=List[FooterFocusItemResponse])
def get_footer_focus_items(db: Session = Depends(get_db)):
    return (
        db.query(FooterFocusItem)
        .filter(FooterFocusItem.is_published == True)  # noqa: E712
        .order_by(FooterFocusItem.display_order.asc(), FooterFocusItem.id.asc())
        .all()
    )


@router.get("/footer-links", response_model=List[FooterQuickLinkResponse])
def get_footer_quick_links(db: Session = Depends(get_db)):
    return (
        db.query(FooterQuickLink)
        .filter(FooterQuickLink.is_published == True)  # noqa: E712
        .order_by(FooterQuickLink.display_order.asc(), FooterQuickLink.id.asc())
        .all()
    )
