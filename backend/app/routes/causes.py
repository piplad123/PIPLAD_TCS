from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Cause
from ..schemas import CauseResponse

router = APIRouter(prefix="/api/causes", tags=["Causes"])

@router.get("", response_model=List[CauseResponse])
def get_all_causes(db: Session = Depends(get_db)):
    return db.query(Cause).all()