import sys
import os
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.document_layouts import (
    CERTIFICATE_IMAGES,
    CERTIFICATE_LABELS,
    CERTIFICATE_TEMPLATE_SLUGS,
    layout_for,
)
from app.models import (
    Cause,
    GalleryItem,
    ContactInquiry,
    Donation,
    CertificateTemplate,
    FounderProfile,
    FounderMilestone,
    Mentor,
    FooterFocusItem,
)

BASE_DIR = Path(__file__).resolve().parent


def _media_url(relative: str) -> str:
    """Return the /media/<path> URL for a file, normalising slashes."""
    return "/media/" + relative.replace("\\", "/")


def _ensure_template_assets() -> dict:
    """Ensure the default volunteer template is under media/certificate_templates."""
    source = BASE_DIR / "app" / "assets" / "piplad-volunteering-certificate.jpg"
    target_dir = BASE_DIR / "media" / "certificate_templates"
    target_dir.mkdir(parents=True, exist_ok=True)

    if source.is_file():
        target = target_dir / source.name
        if not target.is_file():
            shutil.copy2(source, target)

    return {
        "volunteer": _media_url("certificate_templates/piplad-volunteering-certificate.jpg"),
    }


def _auto_layout(w: int, h: int) -> dict:
    """Return a centred name/topic/date layout proportional to image *w* x *h*.

    Text is drawn at anchor="mm" so (x,y) is the centre of each line.
    Font sizes and max_widths scale with image dimensions so even small
    backgrounds render readably.
    """
    base = min(w, h)
    name_fs = max(12, int(base * 0.11))
    topic_fs = max(10, int(base * 0.07))
    date_fs = max(9, int(base * 0.055))
    return {
        "name": {
            "x": w // 2,
            "y": int(h * 0.44),
            "font_size": name_fs,
            "max_width": int(w * 0.82),
            "color": "#1f2937",
            "box": None,
        },
        "topic": {
            "x": w // 2,
            "y": int(h * 0.53),
            "font_size": topic_fs,
            "max_width": int(w * 0.78),
            "color": "#334155",
            "box": None,
        },
        "date": {
            "x": w // 2,
            "y": int(h * 0.62),
            "font_size": date_fs,
            "max_width": int(w * 0.50),
            "color": "#475569",
            "box": None,
        },
    }


def _img_dimensions(url: str) -> tuple[int, int]:
    """Return (width, height) for a /media/ local path, or a safe default."""
    try:
        from PIL import Image as _Img

        rel = url.removeprefix("/media/")
        path = (BASE_DIR / "media" / rel).resolve()
        if path.is_file():
            with _Img.open(path) as img:
                return img.size
    except Exception:
        pass
    return (1200, 800)


# Mapping of filename → (template_name, type_label, display_order).
# Slugs are derived deterministically from the filename stem.
# NOTE: this old second-batch mapping pointed at the legacy 01_–08_ template
# PNGs that were removed from the repo. Official documents now seed from
# ``app.document_layouts`` (see _seed_official_certificate_templates).
_NEW_TEMPLATE_META = []


def _seed_certificate_templates(db) -> None:
    """Add the default certificate templates, skipping any that already exist by slug."""
    existing_slugs = {s for (s,) in db.query(CertificateTemplate.slug).all()}

    assets = _ensure_template_assets()

    # First batch: the original defaults (kept for backward-compat).
    base_templates = [
        {
            "name": "Volunteer Certificate",
            "slug": "volunteer-certificate",
            "type_label": "Certificate of Volunteering",
            "image_url": assets["volunteer"],
            "display_order": 0,
            "layout": {
                "name": {
                    "x": 568,
                    "y": 487,
                    "font_size": 44,
                    "max_width": 460,
                    "color": "#1f2937",
                    "box": [310, 452, 826, 522],
                },
                "date": {
                    "x": 568,
                    "y": 668,
                    "font_size": 18,
                    "max_width": 450,
                    "color": "#475569",
                    "box": [340, 638, 790, 690],
                },
                "topic": None,
            },
        },
        {
            "name": "Training Certificate",
            "slug": "training-certificate",
            "type_label": "Certificate of Training",
            "image_url": _media_url("Certificate/AI training with TCS.jpeg"),
            "display_order": 1,
            "layout": {
                "name": {"x": 640, "y": 420, "font_size": 40, "max_width": 700, "color": "#1f2937", "box": None},
                "date": {"x": 640, "y": 620, "font_size": 18, "max_width": 500, "color": "#475569", "box": None},
                "topic": {"x": 640, "y": 540, "font_size": 22, "max_width": 650, "color": "#334155", "box": None},
            },
        },
        {
            "name": "Certificate of Appreciation",
            "slug": "appreciation-certificate",
            "type_label": "Certificate of Appreciation",
            "image_url": _media_url("Certificate/Certificate of appriciation.jpeg"),
            "display_order": 2,
            "layout": {
                "name": {"x": 640, "y": 430, "font_size": 38, "max_width": 700, "color": "#1f2937", "box": None},
                "date": {"x": 640, "y": 610, "font_size": 18, "max_width": 500, "color": "#475569", "box": None},
                "topic": {"x": 640, "y": 520, "font_size": 22, "max_width": 650, "color": "#334155", "box": None},
            },
        },
        {
            "name": "Team Member Certificate",
            "slug": "team-member-certificate",
            "type_label": "Team Member Certificate",
            "image_url": _media_url("Certificate/AI ML Education with TCS.jpeg"),
            "display_order": 3,
            "layout": {
                "name": {"x": 640, "y": 420, "font_size": 38, "max_width": 700, "color": "#1f2937", "box": None},
                "date": {"x": 640, "y": 610, "font_size": 18, "max_width": 500, "color": "#475569", "box": None},
                "topic": {"x": 640, "y": 530, "font_size": 22, "max_width": 650, "color": "#334155", "box": None},
            },
        },
    ]

    added = 0
    for tpl in base_templates:
        if tpl["slug"] not in existing_slugs:
            db.add(CertificateTemplate(**tpl))
            added += 1

    # Second batch: official Piplad templates (registered backgrounds with the
    # calibrated multi-field layout from app/document_layouts).
    for document_type, image in CERTIFICATE_IMAGES.items():
        slug = CERTIFICATE_TEMPLATE_SLUGS[document_type]
        if slug in existing_slugs:
            continue
        url = _media_url(image)
        db.add(
            CertificateTemplate(
                name=CERTIFICATE_LABELS[document_type],
                slug=slug,
                type_label=document_type,
                image_url=url,
                display_order=20,
                layout=layout_for(document_type),
            )
        )
        added += 1

    if added:
        print(f"Seeded {added} certificate template(s)!")


def slugify(value: str) -> str:
    """Simple slugifier for certificate template filenames."""
    import re
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9-]", "", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "template"


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if causes exist
    if db.query(Cause).count() == 0:
        causes_data = [
            {
                "title": "Childhood Cancer Support & Treatment",
                "slug": "childhood-cancer-support",
                "category": "Healthcare",
                "short_description": "Helping children fight cancer and critical health illnesses with vital medical financial assistance and care.",
                "full_description": "Piplad Welfare Foundation supports underprivileged children fighting cancer and severe heart diseases. We provide access to specialized treatment, medications, and emotional support for families.",
                "target_amount": 500000.0,
                "raised_amount": 285000.0,
                "image_url": "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "Education for All - Empowering Young Minds",
                "slug": "education-for-all",
                "category": "Education",
                "short_description": "Providing quality education materials, tuition support, and school supplies to bright children in need.",
                "full_description": "Every child deserves a chance to learn and grow. We provide school kits, textbooks, digital learning tools, and scholarships to ensure underprivileged children stay in school and build a bright future.",
                "target_amount": 300000.0,
                "raised_amount": 190000.0,
                "image_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "Zero Hunger & Food Distribution Drive",
                "slug": "food-distribution-drive",
                "category": "Relief",
                "short_description": "Distributing warm meals, ration kits, and nutritional food to vulnerable communities and children daily.",
                "full_description": "Proper nutrition is vital for physical and mental development. Our foundation organizes daily and weekly food drives providing wholesome meals to destitute families, street kids, and rural communities.",
                "target_amount": 250000.0,
                "raised_amount": 142000.0,
                "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "Women Empowerment & Skill Development",
                "slug": "women-empowerment",
                "category": "Empowerment",
                "short_description": "Training women in vocational skills like sewing, handicrafts, and computer literacy to gain financial freedom.",
                "full_description": "Empowering a woman empowers an entire family. We offer skill development workshops, micro-entrepreneurship support, and self-reliance programs for women in rural and semi-urban areas.",
                "target_amount": 200000.0,
                "raised_amount": 85000.0,
                "image_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=800"
            }
        ]

        for c in causes_data:
            db.add(Cause(**c))
        print("Seeded Causes successfully!")

    # Check if gallery items exist
    if db.query(GalleryItem).count() == 0:
        gallery_data = [
            {
                "title": "Health Checkup & Medical Camp",
                "image_url": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&q=80&w=800",
                "category": "Healthcare"
            },
            {
                "title": "School Kit Distribution Event",
                "image_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=800",
                "category": "Education"
            },
            {
                "title": "Community Meal & Ration Drive",
                "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=800",
                "category": "Food Drive"
            },
            {
                "title": "Annual Excellence & Recognition Award",
                "image_url": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&q=80&w=800",
                "category": "Awards"
            }
        ]

        for g in gallery_data:
            db.add(GalleryItem(**g))
        print("Seeded Gallery items successfully!")

    # Add sample seed donations if empty
    if db.query(Donation).count() == 0:
        sample_donations = [
            Donation(donor_name="Rajesh Sharma", donor_email="rajesh@example.com", amount=5000.0, cause_id=1, status="completed"),
            Donation(donor_name="Ananya Gupta", donor_email="ananya@example.com", amount=2500.0, cause_id=2, status="completed"),
            Donation(donor_name="Vikram Verma", donor_email="vikram@example.com", amount=10000.0, cause_id=3, status="completed"),
        ]
        for d in sample_donations:
            db.add(d)
        print("Seeded sample donations!")

    # ============================================================
    # Default certificate templates
    # ============================================================
    _seed_certificate_templates(db)

    # ============================================================
    # Default founder profile
    # ============================================================
    if db.query(FounderProfile).count() == 0:
        founder = FounderProfile(
            name="Pushkar Kumar",
            role="Founder",
            eyebrow="Our Founder's Vision",
            title="From Corporate Success to Rural Transformation",
            introduction=(
                "Pushkar Kumar believes that every village holds untapped potential and every child "
                "deserves a fair chance. After earning a B.Tech from SRM University and building a "
                "career in the IT sector, he chose to dedicate himself to rural development."
            ),
            story=(
                "His journey is rooted in a deep understanding of the gap between aspiration and "
                "opportunity. His experience with rural communities shaped a vision where education, "
                "healthcare, livelihoods and technology work together to create meaningful change."
            ),
            vision=(
                "The vision is to build digitally connected villages where children can access quality "
                "education, young people can gain market-ready skills, families can access healthcare, "
                "farmers can adopt climate-smart practices and communities can preserve their cultural identity."
            ),
            quote=(
                "The aim is to turn potential into prosperity — one village, one student, one livelihood at a time."
            ),
        )
        db.add(founder)
        db.flush()

        founder.milestones = [
            FounderMilestone(
                founder_id=founder.id,
                year="01",
                title="Technology",
                description="Building technology-enabled solutions for communities with limited connectivity.",
                display_order=0,
            ),
            FounderMilestone(
                founder_id=founder.id,
                year="02",
                title="Education",
                description="Creating accessible learning pathways for rural students and educators.",
                display_order=1,
            ),
            FounderMilestone(
                founder_id=founder.id,
                year="03",
                title="Livelihoods",
                description="Connecting rural youth with skills, employment and entrepreneurship opportunities.",
                display_order=2,
            ),
            FounderMilestone(
                founder_id=founder.id,
                year="04",
                title="Transformation",
                description="Creating resilient communities through partnerships and measurable impact.",
                display_order=3,
            ),
        ]

        print("Seeded founder profile!")

    # ============================================================
    # Default mentors
    # ============================================================
    if db.query(Mentor).count() == 0:
        default_mentors = [
            Mentor(
                name="Satyanarayan Singh",
                role="Visionary Mentor & Champion of Rural Upliftment",
                description=(
                    "A respected grassroots leader who dedicated decades to rural development, "
                    "education, infrastructure and community welfare."
                ),
                quote="His life is not just part of our history — it is the heartbeat of our mission.",
                display_order=0,
                is_published=True,
            ),
            Mentor(
                name="Piplad Rishi",
                role="Source of Wisdom and Compassion",
                description=(
                    "Piplad Rishi's association with knowledge, inquiry, resilience and ethical "
                    "living provides an enduring philosophical inspiration for the Foundation."
                ),
                quote="Knowledge, resilience and compassionate action remain central to our journey.",
                display_order=1,
                is_published=True,
            ),
        ]
        for mentor in default_mentors:
            db.add(mentor)

        print("Seeded mentors!")

    # ============================================================
    # Default footer focus items
    # ============================================================
    if db.query(FooterFocusItem).count() == 0:
        default_focus = [
            "Childhood Cancer Healthcare",
            "Free Education & School Supplies",
            "Daily Ration & Warm Meals",
            "Women Skill Empowerment",
            "Emergency Medical Financial Aid",
        ]
        for index, text in enumerate(default_focus):
            db.add(
                FooterFocusItem(
                    text=text,
                    display_order=index,
                    is_published=True,
                )
            )

        print("Seeded footer focus items!")

    db.commit()
    db.close()
    print("Database seeding finished!")

if __name__ == "__main__":
    seed_database()
