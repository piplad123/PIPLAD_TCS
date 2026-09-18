from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from ..database import get_db
from ..email_service import send_admin_alert_email
from ..models import ContactInquiry
from ..schemas import ContactCreate, ContactResponse
from .admin import get_current_admin

router = APIRouter(prefix="/api/contact", tags=["Contact"])

@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_form(contact_in: ContactCreate, db: Session = Depends(get_db)):
    if contact_in.website:
        return ContactResponse(
            id=0, **contact_in.model_dump(exclude={"website"}), created_at=datetime.utcnow()
        )

    inquiry = ContactInquiry(**contact_in.model_dump(exclude={"website"}))
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)

    send_admin_alert_email(
        subject=f"New contact inquiry: {inquiry.subject or 'No subject'}",
        text_body=(
            f"A new contact inquiry was submitted.\n\n"
            f"Name: {inquiry.name}\n"
            f"Email: {inquiry.email}\n"
            f"Subject: {inquiry.subject or '-'}\n\n"
            f"Message:\n{inquiry.message or '-'}"
        ),
    )

    return inquiry

@router.get("", response_model=List[ContactResponse])
def list_contact_inquiries(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return db.query(ContactInquiry).order_by(ContactInquiry.created_at.desc()).all()

@router.delete("/{inquiry_id}", status_code=status.HTTP_200_OK)
def delete_contact_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    inquiry = (
        db.query(ContactInquiry)
        .filter(ContactInquiry.id == inquiry_id)
        .first()
    )

    if not inquiry:
        raise HTTPException(
            status_code=404,
            detail="Contact inquiry not found",
        )

    db.delete(inquiry)
    db.commit()

    return {"message": "Contact inquiry deleted"}
