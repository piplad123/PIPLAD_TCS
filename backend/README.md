# PWF Backend

FastAPI + SQLAlchemy 2.0 backend for the Piplad Welfare Foundation. Production
runs on Render with **PostgreSQL** (no SQLite).

## Prerequisites

- Python 3.12+
- PostgreSQL (Render managed instance, or a local Postgres for development)

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set the required environment variable(s). The app refuses to start without a
   database URL:

   ```bash
   # Linux/macOS
   export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require"

   # Windows (PowerShell)
   $env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require"
   ```

   A local `backend/.env` file (gitignored) is loaded automatically if present.
   Copy `backend/.env.example` to `backend/.env` and fill it in.

3. Boot:

   ```bash
   uvicorn app.main:app --reload
   ```

   Tables are created automatically on startup. `/docs` gives you the Swagger UI.

### Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL connection string (`postgresql+psycopg://...`) |
| `CORS_ORIGINS` | No | Comma-separated allowed browser origins (defaults to localhost dev ports) |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | No | Razorpay credentials; absent => mock orders for sandbox testing |
| `ADMIN_USER` / `ADMIN_PASSWORD` | No | Basic-auth credentials for `/api/admin` and SQL admin |
| `BREVO_API_KEY` | No | Brevo HTTPS API key; the only email transport. Absent => email sending is skipped (logged) so failures stay visible |
| `EMAIL_FROM` / `EMAIL_FROM_NAME` | No | Verified Brevo sender used for outbound email |
| `CONTACT_WEBSITE`/`CONTACT_EMAIL`/`CONTACT_PHONE` | No | Contact footer for the volunteer welcome email (defaults to the foundation website/email; phone only when set) |
| `PUBLIC_FRONTEND_URL` | No | Public frontend base URL embedded in certificate / volunteer-card QR codes. Defaults to `https://pip-dev.onrender.com` (the Render-hosted frontend) |

## Official Documents (certificates & Volunteer ID cards)

The admin "Official Documents" tab (`/api/admin/generated/**`) generates
documents from the 5 registered official templates:

- 4 certificates: Appreciation, Internship, Completion, Participation.
- 1 volunteer ID card rendered from `volunteer card.png`.

Every document is stamped with a unique number, an issue/validity window and a
QR code encoding `PUBLIC_FRONTEND_URL + /verify/<kind>/<token>`. The public
`/api/verify/certificate/{id}` and `/api/verify/volunteer/{id}` endpoints
validate documents (revocation and card expiry are reported). Accepted
volunteers automatically get the official card generated, saved under
`media/generated/volunteers/`, and emailed as `Volunteer_ID_Card.jpg`.

Field positions are the single source of truth in `app/document_layouts.py`.
Preview the tuned anchors with:

```bash
python scripts/calibrate_templates.py
```

Output (labelled bounding boxes) lands in `backend/previews/` plus a
mean-luminance report so fields sitting on dark ornamentation are easy to spot.

## Seeding

```bash
python seed_data.py
```

## Deploying the frontend to Render

The repository root contains `render.yaml` for the Vite static site. In Render,
create a Blueprint from this repository, or create a Static Site with:

- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Publish directory: `dist`
- Environment variable: `VITE_API_URL=https://piplad-api.onrender.com/api`

The blueprint also adds the SPA rewrite required by React Router. Set the
backend `CORS_ORIGINS` variable to the exact Render frontend URL after the site
is created. The example assumes `https://pip-found-frontend.onrender.com`.