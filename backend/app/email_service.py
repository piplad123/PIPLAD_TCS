"""Email sending via the Brevo HTTPS API only.

Render's free tier blocks outbound SMTP ports (25, 465, 587), so all email
sends through Brevo's REST API over HTTPS (port 443), which is never blocked.

When BREVO_API_KEY is missing the send is skipped with a logged warning so the
failure is visible (e.g. in the admin panel) instead of raising.
"""

import base64
import logging
import os
from html import escape

import requests

logger = logging.getLogger(__name__)

DEFAULT_FROM_NAME = "Piplad Welfare Foundation"
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def is_brevo_configured() -> bool:
    return bool(os.getenv("BREVO_API_KEY"))


def _from_address() -> tuple[str, str] | None:
    display = os.getenv("EMAIL_FROM_NAME") or DEFAULT_FROM_NAME
    address = os.getenv("EMAIL_FROM")
    if not address:
        return None
    return display, address


def _site_support() -> tuple[str, str]:
    """Return the support (email, phone) pair shown in email footers.

    Reads the admin-editable ``site_settings`` table and falls back to the
    classic hardcoded values when the table is missing or unavailable.
    """
    email = "info@pipladfoundation.in"
    phone = "+91-8981266033"

    try:
        from .database import SessionLocal
        from .models import SiteSetting

        with SessionLocal() as session:
            values = {
                row.key: row.value
                for row in session.query(SiteSetting).all()
            }

        email = values.get("email") or email
        phone = values.get("phone") or phone
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(
            "Could not load site settings for email footer: %s",
            exc,
        )

    return email, phone


def _brevo_attachment(attachment: dict) -> dict:
    return {
        "name": attachment["filename"],
        "content": base64.b64encode(attachment["data"]).decode("ascii"),
    }


def _deliver_via_brevo(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    attachments: list[dict] | None = None,
) -> bool:
    """Send via Brevo's transactional email API (POST over HTTPS, port 443).

    Returns False instead of raising when the API call fails, logging the
    reason so the admin panel can retry later.
    """
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    from_addr = _from_address()
    if not api_key or not from_addr:
        logger.warning("Brevo API key/from not configured; email NOT sent to %s", to_email)
        return False

    payload = {
        "sender": {"name": from_addr[0], "email": from_addr[1]},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_body,
    }
    if html_body:
        payload["htmlContent"] = html_body
    if attachments:
        payload["attachment"] = [_brevo_attachment(a) for a in attachments]

    try:
        response = requests.post(
            BREVO_API_URL,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            json=payload,
            timeout=60,
        )
        if response.status_code not in (200, 201):
            logger.error(
                "Brevo API error (%s) for %s (%s): %s",
                response.status_code,
                to_email,
                subject,
                response.text[:2000],
            )
            return False
        logger.info("Email sent via Brevo to %s: %s", to_email, subject)
        return True
    except Exception as exc:
        logger.error(
            "Failed to send email via Brevo to %s (%s): %s",
            to_email,
            subject,
            exc,
        )
        return False


def _deliver_email(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    attachments: list[dict] | None = None,
) -> bool:
    """Core sender supporting HTML bodies and attachments via the Brevo API.

    `attachments` is a list of {"filename", "data", "maintype", "subtype"}.

    Requires BREVO_API_KEY to be configured; otherwise the send is skipped
    with a logged warning (returns False) so failures stay visible.

    Always returns False (instead of raising) when email is unavailable or the
    send fails, logging the reason for the admin panel to show later.
    """
    if is_brevo_configured():
        return _deliver_via_brevo(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            attachments=attachments,
        )

    logger.warning(
        "Email not configured (BREVO_API_KEY missing); email NOT sent to %s",
        to_email,
    )
    return False


def send_newsletter_confirmation_email(
    *,
    to_email: str,
    name: str | None = None,
) -> bool:
    """Confirm a newsletter signup."""

    greeting = f"Hi {name.strip()}," if name and name.strip() else "Hello,"
    return _deliver_email(
        to_email=to_email,
        subject="Welcome to the Piplad Welfare Foundation newsletter",
        text_body=(
            f"{greeting}\n\n"
            "Thank you for subscribing to updates from Piplad Welfare Foundation. "
            "You will receive stories, impact reports, and opportunities to help "
            "create opportunities and lives.\n\n"
            "If you ever wish to unsubscribe, simply reply to this email and "
            "we will remove you.\n\n"
            "Warm regards,\n"
            "Piplad Welfare Foundation"
        ),
        html_body=(
            f"<p>{greeting}</p>"
            "<p>Thank you for subscribing to updates from Piplad Welfare Foundation. "
            "You will receive stories, impact reports, and opportunities to help "
            "create opportunities and lives.</p>"
            "<p>If you ever wish to unsubscribe, simply reply to this email and "
            "we will remove you.</p>"
            "<p>Warm regards,<br/>Piplad Welfare Foundation</p>"
        ),
    )


def send_admin_alert_email(
    *,
    subject: str,
    text_body: str,
) -> bool:
    """Notify the site administrator about a new submission.

    Recipient comes from ``ADMIN_NOTIFY_EMAIL`` (falls back to ``EMAIL_FROM``).
    No-op when neither is configured.
    """

    to_email = os.getenv("ADMIN_NOTIFY_EMAIL") or os.getenv("EMAIL_FROM")
    if not to_email:
        logger.warning(
            "Admin alert not sent: ADMIN_NOTIFY_EMAIL/EMAIL_FROM unset (%s)",
            subject,
        )
        return False

    return _deliver_email(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=f"<p>{escape(text_body).replace(chr(10), '<br/>')}</p>",
    )


def send_volunteer_welcome_email(
    *,
    to_email: str,
    volunteer_name: str,
    volunteer_email: str,
    volunteer_id: str,
    joined_date,
    id_card_jpg: bytes | None = None,
    id_card_pdf: bytes | None = None,
    verification_url: str | None = None,
) -> bool:
    """Share the official Volunteer ID Card with an accepted volunteer.

    The old graphical "welcome card" message has been removed. The e-mail now
    leads with the official ID card issued by the design system: the front face
    (JPG) and the print-ready double-sided CR80 PDF are attached, and the
    verification URL is included so the card can be verified online.
    """
    from datetime import date, datetime

    joined = joined_date
    if isinstance(joined, (date, datetime)):
        joined = joined.strftime("%d %B %Y")
    elif joined in (None, ""):
        joined = "Recently accepted"

    vid = volunteer_id or "PWF-VOL-STANDBY"

    support_email, support_phone = _site_support()

    text_body = "\n".join(
        [
            f"Dear {volunteer_name},",
            "",
            "Welcome to the Piplad Welfare Foundation family! We are delighted "
            "to have you join us as a volunteer.",
            "",
            "Your official Volunteer ID Card is attached to this e-mail.",
            "",
            "Your Volunteer Details",
            f"Name: {volunteer_name}",
            f"Email: {volunteer_email}",
            f"Volunteer ID: {vid}",
            f"Joining Date: {joined}",
            "",
            *(
                [
                    "You can verify your Volunteer ID Card online at:",
                    verification_url,
                    "",
                ]
                if verification_url
                else []
            ),
            "Please keep your card safe and carry it during volunteer activities.",
            "",
            "With regards,",
            "Piplad Welfare Foundation",
            "Creating Opportunities, Creating Lives",
            f"Support: {support_email} | {support_phone}",
        ]
    )

    html_body = _build_volunteer_id_email_html(
        volunteer_name=volunteer_name,
        volunteer_email=volunteer_email,
        volunteer_id=vid,
        joined_date=joined,
        verification_url=verification_url,
    )

    attachments = []
    if id_card_jpg:
        attachments.append(
            {
                "filename": "Volunteer_ID_Card_Front.jpg",
                "data": id_card_jpg,
                "maintype": "image",
                "subtype": "jpeg",
            }
        )
    if id_card_pdf:
        attachments.append(
            {
                "filename": "Volunteer_ID_Card.pdf",
                "data": id_card_pdf,
                "maintype": "application",
                "subtype": "pdf",
            }
        )

    return _deliver_email(
        to_email=to_email,
        subject="Your Official Volunteer ID Card - Piplad Welfare Foundation",
        text_body=text_body,
        html_body=html_body,
        attachments=attachments,
    )


def _build_volunteer_id_email_html(
    *,
    volunteer_name: str,
    volunteer_email: str,
    volunteer_id: str,
    joined_date: str,
    verification_url: str | None,
) -> str:
    """Branded, mobile-friendly HTML body for the Volunteer ID Card e-mail."""

    support_email, support_phone = _site_support()

    def row(label: str, value: str) -> str:
        return (
            f'<tr><td style="padding:8px 12px;color:#64748b;font-size:13px;'
            f'font-weight:600;white-space:nowrap;">{escape(label)}</td>'
            f'<td style="padding:8px 12px;color:#0f172a;font-size:13px;'
            f'font-weight:600;">{escape(value)}</td></tr>'
        )

    details_rows = (
        row("Name", volunteer_name)
        + row("Email", volunteer_email)
        + row("Volunteer ID", volunteer_id)
        + row("Joining Date", joined_date)
    )

    verify_button = (
        f'<table role="presentation" cellpadding="0" cellspacing="0" '
        f'style="margin:0 0 22px;"><tr><td align="center" bgcolor="#059669" '
        f'style="border-radius:8px;">'
        f'<a href="{escape(verification_url)}" '
        f'style="display:inline-block;padding:12px 26px;color:#ffffff;'
        f'font-size:14px;font-weight:bold;text-decoration:none;border-radius:8px;">'
        f'Verify Volunteer ID Card Online</a></td></tr></table>'
        if verification_url
        else ""
    )

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="background:#f4f6f8;padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
               style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;
                      overflow:hidden;font-family:Arial,Helvetica,sans-serif;
                      border:1px solid #e2e8f0;">
          <tr>
            <td style="background:#059669;padding:26px 32px;text-align:center;">
              <div style="color:#ffffff;font-size:20px;font-weight:bold;letter-spacing:.04em;">
                Piplad Welfare Foundation
              </div>
              <div style="color:#d1fae5;font-size:12px;margin-top:4px;letter-spacing:.12em;">
                Official Volunteer ID Card
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:30px 32px;">
              <p style="margin:0 0 16px;font-size:16px;color:#0f172a;">
                Dear {escape(volunteer_name)},
              </p>
              <p style="margin:0 0 20px;font-size:14px;color:#334155;line-height:1.6;">
                Welcome to the Piplad Welfare Foundation family! Your official
                <b>Volunteer ID Card</b> is attached with this e-mail.
              </p>

              <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                            margin:0 0 22px;">
                <tr>
                  <td style="padding:12px 12px 4px;color:#475569;font-size:11px;
                             text-transform:uppercase;letter-spacing:.08em;font-weight:700;">
                    Volunteer Details
                  </td>
                </tr>
                {details_rows}
              </table>

              {verify_button}

              <p style="margin:0 0 20px;font-size:13px;color:#475569;line-height:1.6;">
                The attached PDF is the print-ready version of your card
                (front and back). Please keep it safe and carry it during
                volunteer activities.
              </p>

              <p style="margin:0 0 8px;font-size:14px;color:#0f172a;">
                With regards,
              </p>
              <p style="margin:0;font-size:14px;color:#0f172a;">
                <b>Piplad Welfare Foundation</b>
              </p>

              <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                     style="margin-top:24px;background:#f0fdf4;border:1px solid #d1fae5;
                            border-radius:10px;">
                <tr>
                  <td style="padding:14px 16px;font-size:12px;color:#047857;line-height:1.7;">
                    <b>Need help?</b> Contact us at
                    <a href="mailto:{escape(support_email)}"
                       style="color:#047857;font-weight:bold;text-decoration:none;">
                      {escape(support_email)}</a>
                    or call {escape(support_phone)}.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="background:#f8fafc;padding:16px 32px;text-align:center;
                       border-top:1px solid #e2e8f0;">
              <div style="color:#94a3b8;font-size:11px;">
                Your card is verifiable at the link above. This e-mail was sent
                to you by the Piplad Welfare Foundation.
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_volunteer_rejection_email(
    *,
    to_email: str,
    volunteer_name: str,
    interest_area: str,
) -> bool:
    """Inform a volunteer that their application was declined by the admin."""
    support_email, _support_phone = _site_support()

    text_body = (
        f"Dear {volunteer_name},\n\n"
        "Thank you for your interest in volunteering with the Piplad Welfare "
        "Foundation. After careful review, we regret to inform you that your "
        "volunteer application"
        + (f" for the area of {interest_area}" if interest_area else "")
        + " has not been accepted at this time.\n\n"
        "We encourage you to apply again in the future. If you have any "
        f"questions, please reach out to us at {support_email}.\n\n"
        "With regards,\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    return _deliver_email(
        to_email=to_email,
        subject="Update on your Volunteer Application - Piplad Welfare Foundation",
        text_body=text_body,
    )


def send_donation_documents_email(
    *,
    to_email: str,
    donor_name: str,
    receipt_html: str,
    receipt_pdf: bytes | None = None,
) -> bool:
    """Send the donation receipt e-mail: HTML receipt + 80G receipt PDF."""
    text_body = (
        f"Dear {donor_name},\n\n"
        "Thank you for your generous donation to the Piplad Welfare "
        "Foundation. Please find attached your Donation Receipt (80G) in "
        "PDF format. Keep it safe for your records and tax filing purposes.\n\n"
        "Thank you for making a difference.\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    attachments = []
    if receipt_pdf:
        attachments.append(
            {
                "filename": "Donation_Receipt_80G.pdf",
                "data": receipt_pdf,
                "maintype": "application",
                "subtype": "pdf",
            }
        )

    return _deliver_email(
        to_email=to_email,
        subject="Your Donation Receipt - Piplad Welfare Foundation",
        text_body=text_body,
        html_body=receipt_html,
        attachments=attachments,
    )


def send_certificate_documents_email(
    *,
    to_email: str,
    recipient_name: str,
    type_label: str,
    event_topic: str,
    event_date: str,
    certificate_number: str,
    verification_url: str,
    pdf_bytes: bytes,
    pdf_filename: str,
    subject: str | None = None,
) -> bool:
    """Email the official certificate PDF with the full verification details.

    Attaches the print-ready certificate PDF and includes the recipient name,
    certificate type, certificate number, issue date, program and the canonical
    verification URL in a professional branded (HTML + plain text) message.
    """
    clean_type = (type_label or "Certificate").strip() or "Certificate"
    cert_number = (certificate_number or "").strip()
    program = (event_topic or "").strip()
    issued_on = (event_date or "").strip()

    support_email, support_phone = _site_support()

    text_body = "\n".join(
        [
            f"Dear {recipient_name},",
            "",
            f"We are pleased to share your {clean_type} from the Piplad Welfare Foundation.",
            "",
            *([f"Certificate Number: {cert_number}"] if cert_number else []),
            *([f"Issue Date: {issued_on}"] if issued_on else []),
            *([f"Program: {program}"] if program else []),
            "",
            "You can verify this certificate online at:",
            verification_url,
            "",
            "Your certificate PDF is attached to this e-mail. Please keep it safe "
            "and feel free to share it on your social profiles.",
            "",
            "With regards,",
            "Piplad Welfare Foundation",
            "Creating Opportunities, Creating Lives",
            f"Support: {support_email} | {support_phone}",
        ]
    )

    html_body = _build_certificate_email_html(
        recipient_name=recipient_name,
        type_label=clean_type,
        event_topic=program,
        event_date=issued_on,
        certificate_number=cert_number,
        verification_url=verification_url,
    )

    return _deliver_email(
        to_email=to_email,
        subject=subject or f"Your {clean_type} - Piplad Welfare Foundation",
        text_body=text_body,
        html_body=html_body,
        attachments=[
            {
                "filename": pdf_filename,
                "data": pdf_bytes,
                "maintype": "application",
                "subtype": "pdf",
            }
        ],
    )


def _build_certificate_email_html(
    *,
    recipient_name: str,
    type_label: str,
    event_topic: str,
    event_date: str,
    certificate_number: str,
    verification_url: str,
) -> str:
    """Branded, mobile-friendly HTML body for certificate e-mails."""
    support_email, support_phone = _site_support()
    name = escape(recipient_name)
    doc_type = escape(type_label)
    program = escape(event_topic)
    issued_on = escape(event_date)
    number = escape(certificate_number)

    def detail_row(label: str, value: str) -> str:
        if not value:
            return ""
        return (
            f'<tr><td style="padding:8px 12px;color:#64748b;font-size:13px;'
            f'font-weight:600;white-space:nowrap;letter-spacing:.02em;">{label}</td>'
            f'<td style="padding:8px 12px;color:#0f172a;font-size:13px;'
            f'font-weight:600;">{value}</td></tr>'
        )

    details_rows = (
        detail_row("Certificate Number", number)
        + detail_row("Issue Date", issued_on)
        + detail_row("Program", program)
    )

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="background:#f4f6f8;padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
               style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;
                      overflow:hidden;font-family:Arial,Helvetica,sans-serif;
                      border:1px solid #e2e8f0;">
          <tr>
            <td style="background:#059669;padding:26px 32px;text-align:center;">
              <div style="color:#ffffff;font-size:20px;font-weight:bold;letter-spacing:.04em;">
                Piplad Welfare Foundation
              </div>
              <div style="color:#d1fae5;font-size:12px;margin-top:4px;letter-spacing:.12em;">
                Creating Opportunities, Creating Lives
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:30px 32px;">
              <p style="margin:0 0 16px;font-size:16px;color:#0f172a;">
                Dear {name},
              </p>
              <p style="margin:0 0 20px;font-size:14px;color:#334155;line-height:1.6;">
                We are pleased to share your <b>{doc_type}</b> with you from the
                Piplad Welfare Foundation. Your certificate of honour is now
                officially issued and digitally verifiable online.
              </p>

              <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                            margin:0 0 22px;">
                <tr>
                  <td style="padding:12px 12px 4px;color:#475569;font-size:11px;
                             text-transform:uppercase;letter-spacing:.08em;font-weight:700;">
                    Certificate Details
                  </td>
                </tr>
                {details_rows}
              </table>

              <table role="presentation" cellpadding="0" cellspacing="0"
                     style="margin:0 0 22px;">
                <tr>
                  <td align="center" style="border-radius:8px;"
                      bgcolor="#059669">
                    <a href="{escape(verification_url)}"
                       style="display:inline-block;padding:12px 26px;color:#ffffff;
                              font-size:14px;font-weight:bold;text-decoration:none;
                              border-radius:8px;">Verify Certificate Online</a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 20px;font-size:13px;color:#475569;line-height:1.6;">
                Your certificate PDF is attached to this e-mail. Please keep it
                safe and feel free to share it on your social profiles.
              </p>

              <p style="margin:0 0 8px;font-size:14px;color:#0f172a;">
                With regards,
              </p>
              <p style="margin:0;font-size:14px;color:#0f172a;">
                <b>Piplad Welfare Foundation</b>
              </p>

              <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                     style="margin-top:24px;background:#f0fdf4;border:1px solid #d1fae5;
                            border-radius:10px;">
                <tr>
                  <td style="padding:14px 16px;font-size:12px;color:#047857;line-height:1.7;">
                    <b>Need help?</b> Contact us at
                    <a href="mailto:{escape(support_email)}"
                       style="color:#047857;font-weight:bold;text-decoration:none;">
                      {escape(support_email)}</a>
                    or call {escape(support_phone)}.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="background:#f8fafc;padding:16px 32px;text-align:center;
                       border-top:1px solid #e2e8f0;">
              <div style="color:#94a3b8;font-size:11px;">
                Your certificate is verifiable at the link above. This e-mail was
                sent to you by the Piplad Welfare Foundation.
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_team_card_email(
    *,
    to_email: str,
    recipient_name: str,
    member_id: str,
    image_bytes: bytes,
) -> bool:
    """Email a rendered team member ID card to the member."""
    text_body = (
        f"Dear {recipient_name},\n\n"
        "Welcome to the Piplad Welfare Foundation family! Please find your "
        "Team Member ID Card attached to this e-mail.\n"
        f"Member ID: {member_id}\n\n"
        "Keep your ID card handy for team events, meetings and official "
        "communication.\n\n"
        "With regards,\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    return _deliver_email(
        to_email=to_email,
        subject="Your Team Member ID Card - Piplad Welfare Foundation",
        text_body=text_body,
        attachments=[
            {
                "filename": "Team_Member_ID_Card.jpg",
                "data": image_bytes,
                "maintype": "image",
                "subtype": "jpeg",
            }
        ],
    )