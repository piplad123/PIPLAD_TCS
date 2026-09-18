from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CauseBase(BaseModel):
    title: str
    category: Optional[str] = "General"
    short_description: str
    full_description: Optional[str] = None
    target_amount: float
    raised_amount: Optional[float] = 0.0
    image_url: Optional[str] = None


class CauseResponse(CauseBase):
    id: int
    slug: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str
    website: Optional[str] = None


class ContactResponse(ContactCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VolunteerApplicationCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    interest_area: str
    about_yourself: Optional[str] = None


class VolunteerApplicationResponse(VolunteerApplicationCreate):
    id: int
    profile_pic_url: Optional[str] = None
    status: str
    volunteer_id: Optional[str] = None
    position: Optional[str] = None
    card_sent_at: Optional[datetime] = None
    card_emailed: Optional[bool] = None
    rejection_email_sent_at: Optional[datetime] = None
    location: Optional[str] = None
    issue_date: Optional[date] = None
    valid_till: Optional[date] = None
    card_file_path: Optional[str] = None
    card_revoked_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RazorpayOrderCreate(BaseModel):
    amount: float
    currency: str = "INR"
    donor_name: str
    donor_email: str
    donor_phone: Optional[str] = None
    cause_id: Optional[int] = None


class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    donation_id: int


class DonationResponse(BaseModel):
    id: int
    donor_name: str
    donor_email: str
    donor_phone: Optional[str] = None
    amount: float
    cause_id: Optional[int] = None
    status: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    receipt_sent_at: Optional[datetime] = None
    invoice_document_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationListResponse(BaseModel):
    items: List[DonationResponse]
    total: int
    page: int
    page_size: int


class GalleryItemBase(BaseModel):
    title: str
    image_url: str
    category: Optional[str] = "Photo Gallery"
    description: Optional[str] = None


class GalleryItemResponse(GalleryItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoGalleryResponse(BaseModel):
    id: int
    title: str
    video_url: str
    category: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpcomingProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    expected_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TEAM
# ============================================================

class TeamMemberBase(BaseModel):
    name: str
    role: Optional[str] = None
    team: str = "General"
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    member_id: Optional[str] = None
    joined_date: Optional[date] = None
    email: Optional[str] = None


class TeamMemberResponse(TeamMemberBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CERTIFICATES
# ============================================================

class CertificateBase(BaseModel):
    title: str
    image_url: Optional[str] = None
    description: Optional[str] = None


class CertificateResponse(CertificateBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# BLOG
# ============================================================

class BlogBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    category: Optional[str] = "General"
    meta_description: Optional[str] = None
    image_url: Optional[str] = None
    published_date: Optional[datetime] = None


class BlogResponse(BlogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ABOUT
# ============================================================


# ============================================================
# MEDIA
# ============================================================


# ============================================================
# IMPACT METRICS
# ============================================================

class ImpactMetricResponse(BaseModel):
    id: int
    metric_key: str
    metric_name: str
    category: str
    value: float
    unit: Optional[str] = None
    description: Optional[str] = None
    is_published: bool
    display_order: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class ImpactMetricUpdate(BaseModel):
    value: float
    is_published: bool = True
    metric_name: Optional[str] = None
    description: Optional[str] = None


class ImpactMetricsUpdateRequest(BaseModel):
    metrics: List[ImpactMetricUpdate]


class PublicImpactMetric(BaseModel):
    key: str
    name: str
    value: float
    unit: Optional[str] = None
    display_order: int


class PublicImpactGroup(BaseModel):
    key: str
    name: str
    metrics: List[PublicImpactMetric]


class PublicImpactResponse(BaseModel):
    last_updated: Optional[date] = None
    groups: List[PublicImpactGroup]
    has_verified_carbon_credits: bool
    verified_carbon_credits_value: Optional[float] = None


# ============================================================
# FOUNDER & MENTORS
# ============================================================

class FounderMilestoneBase(BaseModel):
    year: str = "01"
    title: str
    description: Optional[str] = None
    display_order: int = 0


class FounderMilestoneResponse(FounderMilestoneBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class FounderProfileResponse(BaseModel):
    id: int
    name: str
    role: Optional[str] = None
    eyebrow: Optional[str] = None
    title: Optional[str] = None
    image_url: Optional[str] = None
    image_alt: Optional[str] = None
    introduction: Optional[str] = None
    story: Optional[str] = None
    vision: Optional[str] = None
    quote: Optional[str] = None
    milestones: List[FounderMilestoneResponse] = []

    model_config = ConfigDict(from_attributes=True)


class MentorBase(BaseModel):
    name: str
    role: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    quote: Optional[str] = None
    display_order: int = 0
    is_published: bool = True


class MentorResponse(MentorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# FOOTER FOCUS
# ============================================================

class FooterFocusItemBase(BaseModel):
    text: str
    display_order: int = 0
    is_published: bool = True


class FooterFocusItemResponse(FooterFocusItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# FOOTER QUICK LINKS
# ============================================================

class FooterQuickLinkBase(BaseModel):
    label: str
    path: str
    display_order: int = 0
    is_published: bool = True


class FooterQuickLinkResponse(FooterQuickLinkBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# GENERATED DOCUMENT RESPONSES (download/revoke + shared helpers)
# ============================================================

class GeneratedCertificateResponse(BaseModel):
    id: int
    certificate_number: Optional[str] = None
    certificate_type: Optional[str] = None
    recipient_name: str
    recipient_email: Optional[str] = None
    program_name: Optional[str] = None
    starting_date: Optional[date] = None
    end_date: Optional[date] = None
    organisation_name: Optional[str] = None
    competition_date: Optional[date] = None
    competition_location: Optional[str] = None
    issue_date: Optional[date] = None
    rendered_url: Optional[str] = None
    generated_file_path: Optional[str] = None
    verified_url: Optional[str] = None
    status: str
    sent_at: Optional[datetime] = None
    created_at: datetime
    revoked: bool = False

    model_config = ConfigDict(from_attributes=True)


class GeneratedVolunteerCardResponse(BaseModel):
    id: int
    volunteer_id: Optional[str] = None
    full_name: str
    email: str
    profile_pic_url: Optional[str] = None
    status: str
    position: Optional[str] = None
    location: Optional[str] = None
    issue_date: Optional[date] = None
    valid_till: Optional[date] = None
    card_file_path: Optional[str] = None
    verified_url: Optional[str] = None
    card_revoked_at: Optional[datetime] = None
    card_sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CERTIFICATE MANAGEMENT (admin generate flow)
# ============================================================

class ManagedDocGenerateRequest(BaseModel):
    """One request shape for the 4 certificate types + the Volunteer ID card.

    Certificate numbers / volunteer IDs are always generated server-side;
    the admin form never supplies them.
    """

    document_type: str
    first_name: str
    last_name: Optional[str] = None
    recipient_email: Optional[str] = None
    program_name: Optional[str] = None
    starting_date: Optional[date] = None
    end_date: Optional[date] = None
    organisation_name: Optional[str] = None
    competition_date: Optional[date] = None
    issue_date: Optional[date] = None

    # Volunteer ID card fields.
    phone: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[str] = "issued"
    photo_data_url: Optional[str] = None


class ManagedDocResponse(BaseModel):
    kind: str  # "certificate" | "volunteer"
    record_id: int
    document_type: str
    document_number: Optional[str] = None
    recipient_name: str
    recipient_email: Optional[str] = None
    rendered_url: Optional[str] = None
    verified_url: Optional[str] = None
    created_at: datetime


class CertificateHistoryItem(BaseModel):
    kind: str  # "certificate" | "volunteer"
    record_id: int
    document_number: Optional[str] = None
    recipient_name: str
    document_type: str
    type_label: str
    program: Optional[str] = None
    issue_date: Optional[date] = None
    email: Optional[str] = None
    status: str  # "valid" | "revoked"
    email_sent: bool = False
    created_at: datetime
    rendered_url: Optional[str] = None
    verified_url: Optional[str] = None


class CertificateHistoryResponse(BaseModel):
    items: List[CertificateHistoryItem]
    total: int
    page: int
    page_size: int


# ============================================================
# PUBLIC VERIFICATION
# ============================================================

class VerifiedCertificateResponse(BaseModel):
    valid: bool
    revoked: bool = False
    expired: bool = False
    reason: Optional[str] = None
    certificate_number: Optional[str] = None
    certificate_type: Optional[str] = None
    recipient_name: str
    program_name: Optional[str] = None
    issue_date: Optional[date] = None
    starting_date: Optional[date] = None
    end_date: Optional[date] = None
    organisation_name: Optional[str] = None
    competition_date: Optional[date] = None
    competition_location: Optional[str] = None
    issued_by: str = "Piplad Welfare Foundation"


class VerifiedVolunteerResponse(BaseModel):
    valid: bool
    revoked: bool = False
    expired: bool = False
    reason: Optional[str] = None
    full_name: str
    volunteer_id: Optional[str] = None
    interest_area: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    issue_date: Optional[date] = None
    valid_till: Optional[date] = None
    issued_by: str = "Piplad Welfare Foundation"


# ============================================================
# HOME PAGE HERO SLIDES
# ============================================================

class HomeSlideResponse(BaseModel):
    id: int
    eyebrow: Optional[str] = None
    title: str
    highlight: Optional[str] = None
    text: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# NEWSLETTER
# ============================================================

class NewsletterSubscribeRequest(BaseModel):
    email: str
    name: Optional[str] = None
    website: Optional[str] = None


class NewsletterSubscriberResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)