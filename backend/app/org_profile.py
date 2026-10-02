"""Single source of truth for Piplad Welfare Foundation's organisation profile.

These values appear on donation receipts (HTML + PDF), ID cards and outbound
emails. Keeping them in one module means the wording can never drift between
the two receipt formats again.

Registration note: Piplad Welfare Foundation is a **Section 8 Company**
registered under the Companies Act, 2013. It is NOT a trust and is NOT
registered under the Indian Trusts Act.
"""

ORG_NAME = "Piplad Welfare Foundation"
ORG_TAGLINE = "Creating Opportunities, Creating Lives"

ORG_LEGAL_FORM = "Section 8 Company"

# Deliberately no CIN / PAN / registration number is printed on receipts. Those
# identifiers are legal registration data that must be entered and verified by
# the organisation itself before being published; an unverified number on an
# 80G receipt is worse than no number at all. Add them here only once confirmed.
ORG_REGISTRATION_LINE = (
    f"{ORG_NAME} is a {ORG_LEGAL_FORM} registered under the Companies Act, 2013."
)

# The exact Section 80G deduction percentage depends on the order granted
# (80G(1)(i) vs 80G(1)(ii)) and on any annual cap. We deliberately do not state
# a percentage so the receipt never over-claims a deduction.
ORG_DETAILS = (
    f"{ORG_NAME} is a {ORG_LEGAL_FORM} registered under the Companies Act, 2013, "
    "and holds a tax exemption certificate under Section 12A. Donations to this "
    "organisation are eligible for deduction under Section 80G of the Income "
    "Tax Act, 1961."
)

ORG_CONTACT_EMAIL = "info@pipladfoundation.in"
ORG_CONTACT_PHONE = "+91-8981266033"
