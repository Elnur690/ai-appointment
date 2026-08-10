# AI Appointment SaaS

Multi-tenant SaaS platform where businesses let an AI agent handle appointment booking over WhatsApp.

## Architecture

- **Backend**: FastAPI (Python), async PostgreSQL, Redis + Celery
- **WhatsApp**: Evolution API
- **AI**: Google Gemini API (provider-agnostic abstraction)
- **Dashboards**: React + Vite (SaaS Admin, Business/Staff)
- **Mobile** (Phase 3): Flutter

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+

### Development Setup

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your settings

# Start infrastructure
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Admin Dashboard
cd frontend/admin-dashboard
npm install
npm run dev

# Business Dashboard
cd frontend/business-dashboard
npm install
npm run dev
```

## Project Structure

```
ai-appointment/
├── backend/          # FastAPI backend
├── frontend/
│   ├── admin-dashboard/    # SaaS Owner dashboard
│   └── business-dashboard/ # Business Owner/Staff dashboard
├── docker-compose.yml
└── docs/
```

## Phase 1 (MVP)
- Single branch per business
- AI booking via WhatsApp (Gemini)
- Staff-level scheduling
- Business dashboard
- SaaS admin panel
- Cash payments only
