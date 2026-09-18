import os
import hmac
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Donation, Cause
from ..schemas import RazorpayOrderCreate, RazorpayVerifyRequest, DonationResponse
from ..donation_receipt import build_donation_receipt_html
from ..email_service import send_admin_alert_email, send_donation_documents_email
from ..certificate_pdf import build_donation_receipt_pdf

try:
    import razorpay
except ImportError:
    razorpay = None

router = APIRouter(prefix="/api/donate", tags=["Donations"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_PWF123456789")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "pwf_secret_key_123")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "").strip()


def _razorpay_mode() -> str:
    """Resolve the current payment mode.

    Explicit env override (RAZORPAY_MODE=test|live|mock) wins; otherwise the
    mode is derived from the key prefix so test keys work like test mode.
    """
    mode = os.getenv("RAZORPAY_MODE", "").strip().lower()
    if mode in ("live", "test", "mock"):
        return mode
    if RAZORPAY_KEY_ID.startswith("rzp_live"):
        return "live"
    if RAZORPAY_KEY_ID.startswith("rzp_test"):
        return "test"
    return "mock"


def _razorpay_client():
    if not razorpay:
        raise HTTPException(
            status_code=503,
            detail="Razorpay SDK is not installed on the server",
        )
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def _verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify a Razorpay payment signature (HMAC-SHA256)."""
    if razorpay:
        try:
            razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)).utility.verify_payment_signature(
                {
                    "razorpay_order_id": order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                }
            )
            return True
        except Exception:
            return False

    # Manual fallback: expected = HMAC-SHA256(secret, "{order_id}|{payment_id}")
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        f"{order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _verify_webhook_signature(body: bytes, header: str) -> bool:
    """Verify the X-Razorpay-Signature header on a webhook request."""
    if not header:
        return False
    if razorpay:
        try:
            razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)).utility.verify_webhook_signature(
                body,
                {"X-Razorpay-Signature": header},
                RAZORPAY_WEBHOOK_SECRET,
            )
            return True
        except Exception:
            pass

    # Manual fallback: header may be "<timestamp>|<signature>" comma separated
    for token in header.split(","):
        candidate = token.strip().rsplit("|", 1)[-1]
        expected = hmac.new(
            RAZORPAY_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if hmac.compare_digest(expected, candidate):
            return True
    return False


def _find_donation_by_order(db: Session, order_id: str):
    return db.query(Donation).filter(Donation.razorpay_order_id == order_id).first()


def _invoice_storage_dir(donation_id: int) -> Path:
    """Local folder that holds a donation's receipt PDF.

    PDF documents are stored on disk (and served through the /media static
    mount); only their web paths live in the database so the DB stays light.
    """
    base = Path(__file__).resolve().parents[1] / "media"
    folder = base / "invoices" / f"donation_{donation_id}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _save_donation_documents(
    donation: Donation,
    receipt_pdf: bytes | None,
) -> None:
    """Persist the generated receipt PDF to disk and record its web path.

    Called on every (re)generation so the latest version is always stored.
    The returned /media/... URL is served by the backend static mount.
    """
    folder = _invoice_storage_dir(donation.id)

    if receipt_pdf:
        try:
            (folder / "receipt.pdf").write_bytes(receipt_pdf)
            donation.invoice_document_path = (
                f"/media/invoices/donation_{donation.id}/receipt.pdf"
            )
        except Exception:
            logger.exception("Failed to store donation receipt PDF")


def _email_donation_documents(
    donation: Donation,
    payment_id: str,
) -> bool:
    """Generate the 80G receipt PDF, store it on disk, and email it to the
    donor along with an HTML copy of the receipt.
    """
    receipt_html = build_donation_receipt_html(
        full_name=donation.donor_name,
        email=donation.donor_email,
        phone=donation.donor_phone or "",
        amount=donation.amount,
        order_id=donation.razorpay_order_id or "",
        payment_id=payment_id,
        paid_at=donation.created_at,
    )

    receipt_pdf = None
    try:
        receipt_pdf = build_donation_receipt_pdf(
            full_name=donation.donor_name,
            email=donation.donor_email,
            phone=donation.donor_phone or "",
            amount=donation.amount,
            order_id=donation.razorpay_order_id or "",
            payment_id=payment_id,
            paid_at=donation.created_at,
        )
    except Exception:
        logger.exception("Failed to generate donation receipt PDF")

    _save_donation_documents(donation, receipt_pdf)

    return send_donation_documents_email(
        to_email=donation.donor_email,
        donor_name=donation.donor_name,
        receipt_html=receipt_html,
        receipt_pdf=receipt_pdf,
    )


def _finalize_donation(
    db: Session,
    donation: Donation,
    payment_id: str,
    signature: str = "",
) -> Donation:
    """Idempotently mark a donation completed, credit its cause, and email the
    80G receipt. Safe to call from /verify and /webhook.
    """
    was_pending = donation.status != "completed"

    donation.status = "completed"
    donation.razorpay_payment_id = payment_id
    if signature:
        donation.razorpay_signature = signature

    if was_pending and donation.cause_id:
        cause = db.query(Cause).filter(Cause.id == donation.cause_id).first()
        if cause:
            cause.raised_amount = (cause.raised_amount or 0.0) + donation.amount

    if was_pending:
        send_admin_alert_email(
            subject=f"New donation received — ₹{donation.amount:,.0f}",
            text_body=(
                f"A new donation was completed on the website.\n\n"
                f"Donor: {donation.donor_name}\n"
                f"Email: {donation.donor_email}\n"
                f"Amount: ₹{donation.amount:,.0f}\n"
                f"Payment ID: {payment_id}\n"
                f"Order ID: {donation.razorpay_order_id or '-'}\n"
                f"Date: {datetime.utcnow().isoformat()} (UTC)\n\n"
                f"The 80G receipt email is handled automatically."
            ),
        )

    if not donation.receipt_sent_at:
        sent = _email_donation_documents(donation, payment_id)
        if sent:
            donation.receipt_sent_at = datetime.utcnow()

    db.commit()
    db.refresh(donation)
    return donation


@router.post("/create-order")
def create_razorpay_order(req: RazorpayOrderCreate, db: Session = Depends(get_db)):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    # Create pending donation record in DB
    db_donation = Donation(
        donor_name=req.donor_name,
        donor_email=req.donor_email,
        donor_phone=req.donor_phone,
        amount=req.amount,
        cause_id=req.cause_id,
        status="pending",
    )
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)

    mode = _razorpay_mode()
    use_mock = mode == "mock"

    if not use_mock:
        client = _razorpay_client()
        try:
            data = {
                "amount": int(req.amount * 100),  # amount in paise
                "currency": req.currency,
                "receipt": f"receipt_pwf_{db_donation.id}",
                "notes": {
                    "donor_name": req.donor_name,
                    "donor_email": req.donor_email,
                    "cause_id": str(req.cause_id or ""),
                },
            }
            order = client.order.create(data=data)
            order_id = order["id"]
        except Exception as e:
            db.delete(db_donation)
            db.commit()
            raise HTTPException(
                status_code=502,
                detail=f"Failed to create Razorpay order in {mode} mode: {e}",
            )
    else:
        order_id = f"order_mock_{db_donation.id}"

    db_donation.razorpay_order_id = order_id
    db.commit()

    return {
        "order_id": order_id,
        "amount": req.amount,
        "currency": req.currency,
        "key_id": RAZORPAY_KEY_ID,
        "donation_id": db_donation.id,
        "mode": mode,
        "use_mock": use_mock,
    }


@router.post("/verify")
def verify_payment(req: RazorpayVerifyRequest, db: Session = Depends(get_db)):
    donation = db.query(Donation).filter(Donation.id == req.donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation record not found")

    if donation.status != "completed" and _razorpay_mode() != "mock":
        if not _verify_payment_signature(
            req.razorpay_order_id,
            req.razorpay_payment_id,
            req.razorpay_signature,
        ):
            raise HTTPException(status_code=400, detail="Payment signature verification failed")

    _finalize_donation(
        db,
        donation,
        payment_id=req.razorpay_payment_id,
        signature=req.razorpay_signature,
    )

    return {
        "status": "success",
        "message": "Payment verified successfully. Thank you for your support!",
        "donation_id": donation.id,
        "receipt_emailed": donation.receipt_sent_at is not None,
    }


@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Server-side payment confirmation from Razorpay. Signature protected via
    RAZORPAY_WEBHOOK_SECRET; no basic auth required.
    """
    if not RAZORPAY_WEBHOOK_SECRET:
        return {"status": "ok", "message": "webhook not configured"}

    header = request.headers.get("X-Razorpay-Signature", "")
    body = await request.body()

    if not _verify_webhook_signature(body, header):
        return {"status": "ok", "message": "invalid signature ignored"}

    try:
        payload = json.loads(body)
        event = payload.get("event", "")
        payment = (payload.get("payload") or {}).get("payment", {})
        entity = payment.get("entity", {})
        order_id = entity.get("order_id", "") or ""
        payment_id = entity.get("id", "") or ""

        if not order_id or not payment_id:
            return {"status": "ok", "message": "missing ids"}

        if event in ("payment.captured", "payment.authorized"):
            donation = _find_donation_by_order(db, order_id)
            if donation:
                _finalize_donation(db, donation, payment_id=payment_id)
    except Exception as e:
        logger.exception("Razorpay webhook error: %s", e)

    return {"status": "ok"}


@router.get("", response_model=List[DonationResponse])
def get_donations(db: Session = Depends(get_db)):
    return db.query(Donation).order_by(Donation.created_at.desc()).all()