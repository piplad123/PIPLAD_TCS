import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles


class _CachedStaticFiles(StaticFiles):
    """StaticFiles that adds cache headers; `headers=` kwarg is not
    available on older Starlette versions."""

    def create_response(self, *args, **kwargs):
        response = super().create_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=86400"
        return response
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)

from .admin_panel import setup_admin
from .database import Base, engine
from .document_service import ensure_generated_dirs
from .routes import (
    about,
    admin,
    blog,
    causes,
    certificates,
    cert_management,
    contact,
    donation,
    generation,
    home,
    impact,
    media,
    newsletter,
    settings,
    team,
    verify,
    visits,
    volunteers,
)


# ============================================================
# DATABASE
# ============================================================

# Creates tables that do not already exist.
#
# IMPORTANT:
# create_all() does NOT modify an existing table.
# Therefore, the compatibility block below handles the
# team_members.team column if the table already existed
# before that column was introduced.
Base.metadata.create_all(bind=engine)


# ============================================================
# TEAM TABLE COMPATIBILITY
# ============================================================

# If an existing team_members table was created before the
# "team" column was introduced, add that column automatically.
#
# This is useful during the transition from the older SQLite
# schema to the current PostgreSQL schema.
with engine.begin() as connection:
    inspector = inspect(connection)

    existing_tables = inspector.get_table_names()

    if "team_members" in existing_tables:
        columns = {
            column["name"]
            for column in inspector.get_columns("team_members")
        }

        if "team" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE team_members
                    ADD COLUMN team VARCHAR(255)
                    """
                )
            )

        if "member_id" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE team_members
                    ADD COLUMN member_id VARCHAR(100)
                    """
                )
            )

        if "joined_date" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE team_members
                    ADD COLUMN joined_date DATE
                    """
                )
            )

        if "email" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE team_members
                    ADD COLUMN email VARCHAR(255)
                    """
                )
            )

    if "video_gallery" in existing_tables:
        columns = {
            column["name"]
            for column in inspector.get_columns("video_gallery")
        }

        if "category" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE video_gallery
                    ADD COLUMN category VARCHAR(100)
                    """
                )
            )

    if "volunteer_applications" in existing_tables:
        columns = {
            column["name"]
            for column in inspector.get_columns("volunteer_applications")
        }

        if "volunteer_id" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN volunteer_id VARCHAR(100)
                    """
                )
            )

        if "card_sent_at" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN card_sent_at TIMESTAMP WITHOUT TIME ZONE
                    """
                )
            )

        if "position" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN position VARCHAR(255)
                    """
                )
            )

        if "rejection_email_sent_at" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN rejection_email_sent_at TIMESTAMP WITHOUT TIME ZONE
                    """
                )
            )

        if "location" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN location VARCHAR(255)
                    """
                )
            )

        if "issue_date" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN issue_date DATE
                    """
                )
            )

        if "valid_till" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN valid_till DATE
                    """
                )
            )

        if "card_file_path" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN card_file_path VARCHAR(500)
                    """
                )
            )

        if "card_qr_token" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN card_qr_token VARCHAR(100)
                    """
                )
            )

        if "card_revoked_at" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN card_revoked_at TIMESTAMP WITHOUT TIME ZONE
                    """
                )
            )

        if "updated_at" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE volunteer_applications
                    ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE
                    """
                )
            )

    if "issued_certificates" in existing_tables:
        columns = {
            column["name"]
            for column in inspector.get_columns("issued_certificates")
        }

        if "certificate_number" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN certificate_number VARCHAR(100)
                    """
                )
            )

        if "certificate_type" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN certificate_type VARCHAR(100)
                    """
                )
            )

        if "first_name" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN first_name VARCHAR(255)
                    """
                )
            )

        if "last_name" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN last_name VARCHAR(255)
                    """
                )
            )

        if "program_name" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN program_name VARCHAR(255)
                    """
                )
            )

        if "starting_date" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN starting_date DATE
                    """
                )
            )

        if "end_date" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN end_date DATE
                    """
                )
            )

        if "organisation_name" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN organisation_name VARCHAR(255)
                    """
                )
            )

        if "competition_date" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN competition_date DATE
                    """
                )
            )

        if "competition_location" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN competition_location VARCHAR(255)
                    """
                )
            )

        if "issue_date" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN issue_date DATE
                    """
                )
            )

        if "generated_file_path" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN generated_file_path VARCHAR(500)
                    """
                )
            )

        if "qr_verification_token" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN qr_verification_token VARCHAR(100)
                    """
                )
            )

        if "revoked_at" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN revoked_at TIMESTAMP WITHOUT TIME ZONE
                    """
                )
            )

        if "updated_at" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE issued_certificates
                    ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE
                    """
                )
            )

    # Unique constraints for the new official-document columns. Adding these
    # to existing tables needs explicit index creation (create_all does not
    # touch existing tables), so we create them idempotently here.
    created_indexes = {
        row[0]
        for row in connection.execute(
            text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
        ).fetchall()
    }
    _CREATE_INDEXES = {
        "ix_issued_certificates_certificate_number": (
            "CREATE UNIQUE INDEX IF NOT EXISTS "
            "ix_issued_certificates_certificate_number "
            "ON issued_certificates (certificate_number)"
        ),
        "ix_issued_certificates_qr_verification_token": (
            "CREATE UNIQUE INDEX IF NOT EXISTS "
            "ix_issued_certificates_qr_verification_token "
            "ON issued_certificates (qr_verification_token)"
        ),
        "ix_volunteer_applications_card_qr_token": (
            "CREATE UNIQUE INDEX IF NOT EXISTS "
            "ix_volunteer_applications_card_qr_token "
            "ON volunteer_applications (card_qr_token)"
        ),
        "ix_volunteer_applications_volunteer_id": (
            "CREATE UNIQUE INDEX IF NOT EXISTS "
            "ix_volunteer_applications_volunteer_id "
            "ON volunteer_applications (volunteer_id)"
        ),
    }
    if "issued_certificates" in existing_tables or "volunteer_applications" in existing_tables:
        for name, ddl in _CREATE_INDEXES.items():
            if name not in created_indexes:
                connection.execute(text(ddl))

    if "donations" in existing_tables:
        columns = {
            column["name"]
            for column in inspector.get_columns("donations")
        }

        if "razorpay_signature" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE donations
                    ADD COLUMN razorpay_signature VARCHAR(512)
                    """
                )
            )

        if "receipt_sent_at" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE donations
                    ADD COLUMN receipt_sent_at TIMESTAMP WITHOUT TIME ZONE
                    """
                )
            )

        if "invoice_document_path" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE donations
                    ADD COLUMN invoice_document_path VARCHAR(500)
                    """
                )
            )


# ============================================================
# BLOG CATEGORY / META DESCRIPTION COMPATIBILITY
# ============================================================

# Adds blog filtering (category) and SEO (meta_description) columns
# to pre-existing ``blogs`` tables.

with engine.begin() as connection:
    table_names = {name.lower() for name in inspect(connection).get_table_names()}
    if "blogs" in table_names:
        blog_columns = {
            column["name"] for column in inspect(connection).get_columns("blogs")
        }

        if "category" not in blog_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE blogs
                    ADD COLUMN category VARCHAR(100)
                    """
                )
            )

        if "meta_description" not in blog_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE blogs
                    ADD COLUMN meta_description VARCHAR(300)
                    """
                )
            )


# ============================================================
# CERTIFICATE TEMPLATE IMAGE URL COMPATIBILITY
# ============================================================

# The official certificate images were renamed from the legacy
# "01_/03_/05_..." filenames to the human-friendly names used in
# app/document_layouts.py. Templates seeded before the rename still
# reference the removed files, which surfaces as
# "Template image not found on disk: /media/certificate_templates/07_certificate_internship.png".
# Remap those rows at startup so rendering works again.

_TEMPLATE_IMAGE_RENAMES = {
    "05_certificate_program_completion.png": "Certificate of Completion.png",
    "07_certificate_internship.png": "Certificate of Internship.png",
    "08_certificate_appreciation.png": "Certificate of Appriciation.png",
    "03_certificate_participation.png": "Certificate of Participation.jpeg",
}

# Official certificate template rows are pointed at committed clean
# master templates below (separate ORM block), keeping the legacy
# Admin "Certificates" tab identical to the official generator.

with engine.begin() as connection:
    table_names = {name.lower() for name in inspect(connection).get_table_names()}
    if "certificate_templates" in table_names:
        for old_name, new_name in _TEMPLATE_IMAGE_RENAMES.items():
            old_pattern = f"%/certificate_templates/{old_name}"
            new_url = f"/media/certificate_templates/{new_name}"
            connection.execute(
                text(
                    "UPDATE certificate_templates "
                    "SET image_url = :new_url "
                    "WHERE image_url LIKE :old_pattern"
                ),
                {"new_url": new_url, "old_pattern": old_pattern},
            )


# Official certificate templates now render onto committed clean master
# templates with the spec layout (JSON stored via the ORM so it round-trips
# correctly on PostgreSQL/SQLite).
from .document_layouts import CERTIFICATE_TEMPLATE_SLUGS, layout_for
from .models import CertificateTemplate
from .template_coordinates import CLEAN_CERTIFICATE_TEMPLATES
from sqlalchemy.orm import Session as _Session

with _Session(bind=engine) as session:
    for doc_type, slug in CERTIFICATE_TEMPLATE_SLUGS.items():
        tpl = session.query(CertificateTemplate).filter_by(slug=slug).first()
        if tpl:
            tpl.image_url = f"/media/{CLEAN_CERTIFICATE_TEMPLATES[doc_type]}"
            tpl.layout = layout_for(doc_type)
    session.commit()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Piplad Welfare Foundation API",
    description="Backend API for Piplad Welfare Foundation",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

# Starlette's ServerErrorMiddleware (the default 500 responder) lives
# OUTSIDE the CORSMiddleware, so even a registered catch-all handler here
# produces a response sent via the raw ASGI channel that carries no
# Access-Control-Allow-Origin header. A browser then reports such an
# unhandled error as "Failed to fetch" / "No 'Access-Control-Allow-Origin'
# header" and the real failure stays invisible. We therefore reproduce the
# CORSMiddleware header logic for the allowed origins manually so the client
# can actually read the error message. The traceback is logged server-side.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    headers = {}
    origin = request.headers.get("origin")
    if origin and origin in CORS_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Vary"] = "Origin"
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
        headers=headers,
    )


# ============================================================
# API ROUTES
# ============================================================

# Each router already defines its own prefix inside the
# respective route module.
#
# Therefore we intentionally do NOT provide another prefix
# here.

app.include_router(
    causes.router,
    tags=["Causes"],
)

app.include_router(
    contact.router,
    tags=["Contact"],
)

app.include_router(
    donation.router,
    tags=["Donations"],
)

app.include_router(
    admin.router,
    tags=["Admin"],
)

app.include_router(
    team.router,
    tags=["Team"],
)

app.include_router(
    certificates.router,
    tags=["Certificates"],
)

app.include_router(
    blog.router,
    tags=["Blog"],
)

app.include_router(
    about.router,
    tags=["About"],
)

app.include_router(
    media.router,
    tags=["Media"],
)

app.include_router(
    volunteers.router,
    tags=["Volunteers"],
)

app.include_router(
    impact.router,
    tags=["Impact"],
)

app.include_router(
    generation.router,
    tags=["Admin Generated Documents"],
)

app.include_router(
    cert_management.router,
    tags=["Admin Certificate Management"],
)

app.include_router(
    verify.router,
    tags=["Verify"],
)

app.include_router(
    visits.router,
    tags=["Visits"],
)

app.include_router(
    settings.router,
    tags=["Settings"],
)

app.include_router(
    home.router,
    tags=["Home"],
)

app.include_router(
    newsletter.router,
    tags=["Newsletter"],
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Piplad Welfare Foundation API",
        "status": "online",
        "organization": "Piplad Welfare Foundation",
        "tagline": "Creating Opportunities, Creating Lives",
        "docs_url": "/docs",
    }


# ============================================================
# ADMIN PANEL
# ============================================================

setup_admin(app)


# ============================================================
# MEDIA STORAGE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_DIR = BASE_DIR / "media"

MEDIA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

(MEDIA_DIR / "gallery").mkdir(
    parents=True,
    exist_ok=True,
)

(MEDIA_DIR / "videos").mkdir(
    parents=True,
    exist_ok=True,
)

(MEDIA_DIR / "projects").mkdir(
    parents=True,
    exist_ok=True,
)

# Team member uploads.
(MEDIA_DIR / "team").mkdir(
    parents=True,
    exist_ok=True,
)

# Certificate uploads.
(MEDIA_DIR / "certificates").mkdir(
    parents=True,
    exist_ok=True,
)

# About page founder / mentor photos.
(MEDIA_DIR / "about").mkdir(
    parents=True,
    exist_ok=True,
)

# Home-page hero slide uploads.
(MEDIA_DIR / "home").mkdir(
    parents=True,
    exist_ok=True,
)

# Certificate template backgrounds.
(MEDIA_DIR / "certificate_templates").mkdir(
    parents=True,
    exist_ok=True,
)

# Generated official certificates and volunteer ID cards.
ensure_generated_dirs()


# ============================================================
# STATIC MEDIA
# ============================================================

# /media/... -> backend/media/...
#
# This mount must appear before the frontend catch-all mount.

app.mount(
    "/media",
    _CachedStaticFiles(directory=MEDIA_DIR),
    name="media",
)


# ============================================================
# REACT FRONTEND
# ============================================================

# Serve the React production build when it exists locally.
#
# The frontend mount must remain LAST because "/" is a
# catch-all route.

frontend_dist = (
    Path(__file__).resolve().parents[2]
    / "frontend"
    / "dist"
)

if frontend_dist.is_dir():
    app.mount(
        "/",
        StaticFiles(
            directory=frontend_dist,
            html=True,
        ),
        name="frontend",
    )