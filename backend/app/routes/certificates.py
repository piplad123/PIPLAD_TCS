from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Certificate
from ..schemas import CertificateResponse

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])

@router.get("", response_model=List[CertificateResponse])
def get_all_certificates(db: Session = Depends(get_db)):
    return db.query(Certificate).order_by(Certificate.created_at.desc()).all()
