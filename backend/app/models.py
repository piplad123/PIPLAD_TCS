from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class FounderProfile(Base):
    """Single editable founder profile shown on the About page."""

    __tablename__ = "founder_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, default="Pushkar Kumar")
    role = Column(String(255), nullable=True, default="Founder")
    eyebrow = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    image_alt = Column(String(255), nullable=True)
    introduction = Column(Text, nullable=True)
    story = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    quote = Column(Text, nullable=True)

    milestones = relationship(
        "FounderMilestone",
        back_populates="founder",
        cascade="all, delete-orphan",
        order_by="FounderMilestone.display_order",
    )


class FounderMilestone(Base):
    """Milestone card shown under the founder story."""

    __tablename__ = "founder_milestones"

    id = Column(Integer, primary_key=True, index=True)
    founder_id = Column(Integer, ForeignKey("founder_profiles.id"), nullable=False)
    year = Column(String(20), nullable=False, default="01")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)

    founder = relationship("FounderProfile", back_populates="milestones")


class Mentor(Base):
    """Editable mentor shown in the toggleable mentors section of About."""

    __tablename__ = "founder_mentors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    quote = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_published = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CertificateTemplate(Base):
    """A certificate/template type whose layout the admin can configure.

    ``layout`` is a JSON object. The public rendering code reads the ``name`` /
    ``date`` / ``topic`` keys; each section supports ``x``, ``y``,
    ``font_size``, ``max_width``, ``color`` and an optional ``box`` blank box.
    """

    __tablename__ = "certificate_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    type_label = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    layout = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    issued = relationship("IssuedCertificate", back_populates="template")


class IssuedCertificate(Base):
    """Log entry for a certificate generated on demand by the admin."""

    __tablename__ = "issued_certificates"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("certificate_templates.id"), nullable=True)
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=True)
    event_topic = Column(String(500), nullable=True)
    event_date = Column(Date, nullable=True)
    type_label = Column(String(100), nullable=True)
    rendered_url = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="rendered")
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Dynamic certificate fields (official templates).
    certificate_number = Column(String(100), unique=True, index=True, nullable=True)
    certificate_type = Column(String(100), nullable=True, default="certificate")
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    program_name = Column(String(255), nullable=True)
    starting_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    organisation_name = Column(String(255), nullable=True)
    competition_date = Column(Date, nullable=True)
    competition_location = Column(String(255), nullable=True)
    issue_date = Column(Date, nullable=True)
    generated_file_path = Column(String(500), nullable=True)
    qr_verification_token = Column(String(100), unique=True, index=True, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    template = relationship("CertificateTemplate", back_populates="issued")


class FooterFocusItem(Base):
    """Editable bullet items under "Our Core Focus" in the website footer."""

    __tablename__ = "footer_focus_items"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    is_published = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FooterQuickLink(Base):
    """Editable link rows under "Quick Links" in the website footer."""

    __tablename__ = "footer_quick_links"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    is_published = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Cause(Base):
    __tablename__ = "causes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    category = Column(String(100), default="General")
    short_description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=True)
    target_amount = Column(Numeric(12, 2), default=100000.0)
    raised_amount = Column(Numeric(12, 2), default=0.0)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    donations = relationship("Donation", back_populates="cause")


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_name = Column(String(255), nullable=False)
    donor_email = Column(String(255), nullable=False)
    donor_phone = Column(String(50), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    cause_id = Column(Integer, ForeignKey("causes.id"), nullable=True)
    razorpay_order_id = Column(String(255), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)
    razorpay_signature = Column(String(512), nullable=True)
    status = Column(String(50), default="pending")
    receipt_sent_at = Column(DateTime, nullable=True)
    invoice_document_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cause = relationship("Cause", back_populates="donations")


class ContactInquiry(Base):
    __tablename__ = "contact_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class VolunteerApplication(Base):
    __tablename__ = "volunteer_applications"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    interest_area = Column(String(255), nullable=False)
    position = Column(String(255), nullable=True)
    about_yourself = Column(Text, nullable=True)
    profile_pic_url = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    volunteer_id = Column(String(100), nullable=True, unique=True, index=True)
    card_sent_at = Column(DateTime, nullable=True)
    rejection_email_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Official volunteer ID card fields.
    location = Column(String(255), nullable=True)
    issue_date = Column(Date, nullable=True)
    valid_till = Column(Date, nullable=True)
    card_file_path = Column(String(500), nullable=True)
    card_qr_token = Column(String(100), unique=True, index=True, nullable=True)
    card_revoked_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        String(255),
        nullable=True,
    )

    # Team/category in which this person belongs.
    #
    # Examples:
    # Education & Skill Development
    # Healthcare
    # Finance & Legal
    # Environment & Modern Agriculture
    # Social Welfare
    # Culture & Tourism
    # Sports & Yoga
    # IT & Social Media
    team = Column(
        String(255),
        nullable=False,
        default="General",
        index=True,
    )

    # Optional uploaded photograph.
    photo_url = Column(
        String(500),
        nullable=True,
    )

    bio = Column(
        Text,
        nullable=True,
    )

    # Stable public identifier used on the member ID card.
    member_id = Column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    joined_date = Column(
        Date,
        nullable=True,
    )

    email = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GalleryItem(Base):
    __tablename__ = "gallery_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    category = Column(String(100), default="Photo Gallery")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VideoGallery(Base):
    __tablename__ = "video_gallery"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    video_url = Column(String(500), nullable=False)
    category = Column(String(100), default="Video Gallery", index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UpcomingProject(Base):
    __tablename__ = "upcoming_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    expected_date = Column(Date, nullable=True)
    status = Column(
        String(50),
        nullable=False,
        default="upcoming",
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class NewsletterSubscriber(Base):
    """Email newsletter signup collected from the footer form."""

    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), default="General", index=True)
    meta_description = Column(String(300), nullable=True)
    image_url = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)
    published_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class About(Base):
    __tablename__ = "about_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tagline = Column(String(255), nullable=True)
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    founded = Column(String(100), nullable=True)
    registration = Column(String(255), nullable=True)


class Media(Base):
    __tablename__ = "media_coverage"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    published_date = Column(
        DateTime,
        default=datetime.utcnow,
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class ImpactMetric(Base):
    __tablename__ = "impact_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Stable machine-readable key, e.g. "students_supported".
    metric_key = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    # Human-readable name, e.g. "Students & Learners Supported".
    metric_name = Column(
        String(255),
        nullable=False,
    )

    # Grouping used by the public API, e.g. "people" | "environmental".
    category = Column(
        String(100),
        nullable=False,
        default="people",
        index=True,
    )

    # Numeric value for the metric.
    value = Column(
        Numeric(18, 2),
        nullable=False,
        default=0.0,
    )

    # Unit label, e.g. "people", "trees", "tonnes", "credits".
    unit = Column(
        String(100),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    # Whether the metric is shown on the public site.
    is_published = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    display_order = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    last_updated = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class SiteVisit(Base):
    """One row per unique visitor per day (used for the admin visitor counter)."""

    __tablename__ = "site_visits"
    __table_args__ = (
        UniqueConstraint(
            "visitor_key",
            "visit_date",
            name="uq_site_visits_visitor_key_date",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    visitor_key = Column(String(100), nullable=False, index=True)
    visit_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SiteSetting(Base):
    """Editable site-wide settings (phone, email, address, map query, ...).

    Stored as simple key/value rows so new settings can be added without a
    schema change. The site reads these through GET /api/settings; admins
    edit them through PUT /api/admin/settings.
    """

    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(String(1000), nullable=False, default="")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class HomeSlide(Base):
    """Home-page hero slider slide, editable by the admin.

    When no slides are configured the frontend falls back to its built-in
    defaults, so the homepage keeps rendering correctly out of the box.
    """

    __tablename__ = "home_slides"

    id = Column(Integer, primary_key=True, index=True)
    eyebrow = Column(String(255), nullable=True, default="")
    title = Column(String(255), nullable=False)
    highlight = Column(String(255), nullable=True, default="")
    text = Column(Text, nullable=True, default="")
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, nullable=False, default=0, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )