from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TeamMember
from ..schemas import TeamMemberResponse


router = APIRouter(
    prefix="/api/team",
    tags=["Team"],
)


@router.get(
    "",
    response_model=List[TeamMemberResponse],
)
def get_all_team(
    db: Session = Depends(get_db),
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