"""HTML 80G donation receipt generator."""

import html
from datetime import datetime


ORG_NAME = "Piplad Welfare Foundation"
ORG_TAGLINE = "Creating Opportunities, Creating Lives"
ORG_DETAILS = (
    "Registered under the Indian Trusts Act. Donations are eligible for "
    "50% deduction under Section 80G of the Income Tax Act, 1961."
)


def _format_amount(amount) -> str:
    try:
        return f"{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _format_date(value) -> str:
    if not value:
        return datetime.utcnow().strftime("%d %B %Y")
    if isinstance(value, datetime):
        return value.strftime("%d %B %Y")
    return str(value)


def build_donation_receipt_html(
    *,
    full_name: str,
    email: str,
    phone: str = "",
    amount,
    order_id: str = "",
    payment_id: str = "",
    paid_at=None,
) -> str:
    name = html.escape(full_name)
    email_esc = html.escape(email)
    phone_esc = html.escape(phone or "—")
    amt = html.escape(_format_amount(amount))
    order = html.escape(order_id or "N/A")
    payment = html.escape(payment_id or "N/A")
    date = html.escape(_format_date(paid_at or datetime.utcnow()))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Donation Receipt - 80G</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f1f5f9;padding:24px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 12px 32px rgba(15,23,42,0.12);">
          <tr>
            <td style="background:#0f172a;padding:28px 36px;text-align:center;">
              <div style="display:inline-block;background:#84cc16;color:#ffffff;font-size:13px;font-weight:800;letter-spacing:1px;padding:6px 16px;border-radius:999px;text-transform:uppercase;">{ORG_NAME}</div>
              <div style="color:#a3e635;font-size:13px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:12px;">Donation Receipt</div>
            </td>
          </tr>
          <tr>
            <td style="padding:30px 40px 10px;text-align:center;">
              <h1 style="margin:0 0 8px;font-size:24px;color:#0f172a;">Thank You, {name}!</h1>
              <p style="margin:0;color:#64748b;font-size:15px;line-height:1.7;">
                Your generous contribution has been received successfully.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:22px 40px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;">
                <tr>
                  <td style="padding:14px 18px;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Donor Name</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a;margin-top:4px;">{name}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Amount Donated</div>
                    <div style="font-size:20px;font-weight:800;color:#059669;margin-top:4px;">&#8377; {amt}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Donor Email</div>
                    <div style="font-size:15px;font-weight:600;color:#0f172a;margin-top:4px;">{email_esc}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Donor Phone</div>
                    <div style="font-size:15px;font-weight:600;color:#0f172a;margin-top:4px;">{phone_esc}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Date</div>
                    <div style="font-size:15px;font-weight:600;color:#0f172a;margin-top:4px;">{date}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Transaction ID</div>
                    <div style="font-size:14px;font-weight:600;color:#0f172a;margin-top:4px;word-break:break-all;">{payment}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Order / Reference ID</div>
                    <div style="font-size:14px;font-weight:600;color:#0f172a;margin-top:4px;word-break:break-all;">{order}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:0 40px 8px;">
              <p style="margin:0;color:#334155;font-size:14px;line-height:1.7;">
                This is an acknowledgment of your donation. {ORG_DETAILS} An
                official tax certificate with your PAN details and our 80G
                registration number will follow separately by email.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background:#0f172a;padding:20px 40px;text-align:center;margin-top:16px;">
              <div style="color:#cbd5e1;font-size:12px;line-height:1.6;">
                Thank you for making a difference.<br />
                <span style="color:#ffffff;font-weight:700;font-size:14px;">{ORG_TAGLINE}</span>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""