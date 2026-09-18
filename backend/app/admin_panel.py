from sqladmin import Admin, ModelView

from .database import engine
from .models import (
    About,
    Blog,
    Cause,
    Certificate,
    CertificateTemplate,
    ContactInquiry,
    Donation,
    FooterFocusItem,
    FounderMilestone,
    FounderProfile,
    GalleryItem,
    ImpactMetric,
    IssuedCertificate,
    Media,
    Mentor,
    NewsletterSubscriber,
    TeamMember,
    UpcomingProject,
    VideoGallery,
    VolunteerApplication,
)


class CauseAdmin(ModelView, model=Cause):
    column_list = [Cause.id, Cause.title, Cause.category, Cause.target_amount, Cause.raised_amount, Cause.created_at]
    icon = "fa-solid fa-hands-holding-child"


class DonationAdmin(ModelView, model=Donation):
    column_list = [Donation.id, Donation.donor_name, Donation.amount, Donation.status, Donation.created_at]
    icon = "fa-solid fa-hand-holding-dollar"


class ContactInquiryAdmin(ModelView, model=ContactInquiry):
    column_list = [ContactInquiry.id, ContactInquiry.name, ContactInquiry.email, ContactInquiry.subject, ContactInquiry.created_at]
    icon = "fa-solid fa-envelope"


class VolunteerApplicationAdmin(ModelView, model=VolunteerApplication):
    column_list = [
        VolunteerApplication.id,
        VolunteerApplication.full_name,
        VolunteerApplication.email,
        VolunteerApplication.interest_area,
        VolunteerApplication.status,
        VolunteerApplication.volunteer_id,
        VolunteerApplication.card_sent_at,
        VolunteerApplication.created_at,
    ]
    column_searchable_list = [
        VolunteerApplication.full_name,
        VolunteerApplication.email,
        VolunteerApplication.volunteer_id,
    ]
    column_sortable_list = [
        VolunteerApplication.created_at,
        VolunteerApplication.status,
        VolunteerApplication.card_sent_at,
    ]
    icon = "fa-solid fa-handshake-angle"


class TeamMemberAdmin(ModelView, model=TeamMember):
    column_list = [TeamMember.id, TeamMember.name, TeamMember.role, TeamMember.created_at]
    icon = "fa-solid fa-users"


class CertificateAdmin(ModelView, model=Certificate):
    column_list = [Certificate.id, Certificate.title, Certificate.created_at]
    icon = "fa-solid fa-certificate"


class GalleryItemAdmin(ModelView, model=GalleryItem):
    column_list = [GalleryItem.id, GalleryItem.title, GalleryItem.category, GalleryItem.created_at]
    icon = "fa-solid fa-image"


class VideoGalleryAdmin(ModelView, model=VideoGallery):
    column_list = [VideoGallery.id, VideoGallery.title, VideoGallery.created_at]
    icon = "fa-solid fa-video"


class UpcomingProjectAdmin(ModelView, model=UpcomingProject):
    column_list = [UpcomingProject.id, UpcomingProject.title, UpcomingProject.status, UpcomingProject.expected_date]
    icon = "fa-solid fa-calendar-days"


class BlogAdmin(ModelView, model=Blog):
    column_list = [Blog.id, Blog.title, Blog.category, Blog.published_date]
    icon = "fa-solid fa-newspaper"


class NewsletterSubscriberAdmin(ModelView, model=NewsletterSubscriber):
    column_list = [
        NewsletterSubscriber.id,
        NewsletterSubscriber.email,
        NewsletterSubscriber.name,
        NewsletterSubscriber.created_at,
    ]
    column_searchable_list = [NewsletterSubscriber.email, NewsletterSubscriber.name]
    column_sortable_list = [NewsletterSubscriber.created_at]
    icon = "fa-solid fa-bell"


class AboutAdmin(ModelView, model=About):
    column_list = [About.id, About.name, About.tagline, About.founded]
    icon = "fa-solid fa-building"


class MediaAdmin(ModelView, model=Media):
    column_list = [Media.id, Media.title, Media.source, Media.published_date]
    icon = "fa-solid fa-newspaper"


class ImpactMetricAdmin(ModelView, model=ImpactMetric):
    column_list = [
        ImpactMetric.id,
        ImpactMetric.metric_key,
        ImpactMetric.metric_name,
        ImpactMetric.category,
        ImpactMetric.value,
        ImpactMetric.is_published,
        ImpactMetric.last_updated,
    ]
    column_searchable_list = [ImpactMetric.metric_key, ImpactMetric.metric_name]
    icon = "fa-solid fa-chart-simple"


class MentorAdmin(ModelView, model=Mentor):
    column_list = [Mentor.id, Mentor.name, Mentor.role, Mentor.is_published, Mentor.display_order]
    icon = "fa-solid fa-people-group"


class FounderProfileAdmin(ModelView, model=FounderProfile):
    column_list = [FounderProfile.id, FounderProfile.name, FounderProfile.role]
    icon = "fa-solid fa-user-tie"


class FounderMilestoneAdmin(ModelView, model=FounderMilestone):
    column_list = [FounderMilestone.id, FounderMilestone.title, FounderMilestone.year, FounderMilestone.display_order]
    icon = "fa-solid fa-list"


class CertificateTemplateAdmin(ModelView, model=CertificateTemplate):
    column_list = [CertificateTemplate.id, CertificateTemplate.name, CertificateTemplate.slug, CertificateTemplate.is_active]
    icon = "fa-solid fa-file-image"


class IssuedCertificateAdmin(ModelView, model=IssuedCertificate):
    column_list = [
        IssuedCertificate.id,
        IssuedCertificate.certificate_number,
        IssuedCertificate.recipient_name,
        IssuedCertificate.certificate_type,
        IssuedCertificate.status,
        IssuedCertificate.issue_date,
        IssuedCertificate.revoked_at,
        IssuedCertificate.created_at,
    ]
    icon = "fa-solid fa-certificate"


class FooterFocusItemAdmin(ModelView, model=FooterFocusItem):
    column_list = [FooterFocusItem.id, FooterFocusItem.text, FooterFocusItem.display_order, FooterFocusItem.is_published]
    icon = "fa-solid fa-arrow-down-wide-short"


def setup_admin(app):
    admin = Admin(app, engine, title="PWF Admin Dashboard")
    admin.add_view(CauseAdmin)
    admin.add_view(DonationAdmin)
    admin.add_view(BlogAdmin)
    admin.add_view(TeamMemberAdmin)
    admin.add_view(GalleryItemAdmin)
    admin.add_view(VideoGalleryAdmin)
    admin.add_view(UpcomingProjectAdmin)
    admin.add_view(CertificateAdmin)
    admin.add_view(CertificateTemplateAdmin)
    admin.add_view(IssuedCertificateAdmin)
    admin.add_view(MentorAdmin)
    admin.add_view(FounderProfileAdmin)
    admin.add_view(FounderMilestoneAdmin)
    admin.add_view(FooterFocusItemAdmin)
    admin.add_view(MediaAdmin)
    admin.add_view(ImpactMetricAdmin)
    admin.add_view(ContactInquiryAdmin)
    admin.add_view(VolunteerApplicationAdmin)
    admin.add_view(AboutAdmin)
