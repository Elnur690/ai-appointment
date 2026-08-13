# AI Appointment SaaS — Master Multi-Tenant Enterprise Platform (100% Completed)

A high-performance, multi-tenant enterprise SaaS platform where businesses (from 1-person solo shops to multi-branch salon/clinic chains) let an autonomous AI Agent handle appointment bookings, rescheduling, cancellations, customer inquiries, and staff notifications over **WhatsApp**, **Instagram Direct**, and **Facebook Messenger**.

> **Zero-App / Zero-Web Requirement**: Customers and Staff can manage their entire booking workflow over WhatsApp using natural text or **voice notes (audio messages)** in **Azerbaijani (AZ)**, **English (EN)**, and **Russian (RU)**.

---

## 🌟 Master Platform Capabilities (Phases 1-4 Complete)

### 🤖 1. Multi-Provider AI Conversation Core
- **Multi-Model Dynamic Engine**: Hot-swappable support for **Google Gemini 3.5 Flash**, **Anthropic Claude 3.7 Sonnet**, and **OpenAI GPT-4o** with zero server downtime.
- **Live Source Model Discovery**: Automatically queries official provider REST APIs to discover and activate newly released AI models with 1 click.
- **RAG "Learn from Mistakes" Engine**: In-memory and PostgreSQL `pgvector` HNSW vector embeddings for instant business knowledge & mistake correction.
- **WhatsApp Voice Notes & Audio Messages**: Speech-to-intent processing for 5-second voice notes.
- **Internal WhatsApp Staff Group Bot (`@g.us`)**: Staff and owners run daily agenda, next-in-list, revenue, and no-show queries inside WhatsApp groups.

### 📅 2. Calendar Sync & Advanced Scheduling
- **Single-Truth Availability Engine**: Prevents double-booking across multi-branch staff schedules.
- **Google Calendar 2-Way Sync**: Real-time event creation & freeBusy checks.
- **Apple Calendar (CalDAV RFC 4791) 2-Way Sync**: iCloud CalDAV integration.
- **Waitlist & Auto-Backfill**: Automatically fills cancelled appointment slots with waitlisted customers over WhatsApp.
- **Dynamic Off-Peak Pricing & Surge Hours**: Time-based 15% off-peak morning discounts and 15% weekend afternoon peak surges.
- **Multi-Service Combo Packages**: Sequential time-block calculation and 15% combo package discounts.
- **AI Group & Event Scheduler**: Concurrent slot booking across multiple staff members for group visits.

### 💳 3. Payments & No-Show Safeguards
- **Azerbaijan Payment Gateways**: Native **Payriff** & **EPoint** REST API integrations for online deposit checkout links.
- **AI Dynamic No-Show Deposits**: Enforces mandatory deposits for high-risk customers (2+ past no-shows) or high-value bookings (>50 AZN).

### 📈 4. Customer Experience & Commercial Growth
- **Automated WhatsApp Reminders**: 24h and 2h pre-appointment alerts with quick reply buttons.
- **Automated Win-Back Campaigns**: Daily Celery Beat tasks re-engaging inactive customers (>30 days).
- **AI Customer Loyalty & VIP Rewards**: Milestone vouchers (5th visit = 10% off, 10th visit = VIP Platinum status).
- **Interactive Product Upsell Engine**: Post-confirmation retail product add-on recommendations.
- **Omnichannel DMs**: Seamless handling of Instagram Direct Messages & Facebook Messenger DMs.
- **Weekly AI Growth Advisor**: Executive Monday reports analyzing capacity utilization and revenue opportunities.

### 🎛️ 5. SaaS Admin, Feature Gating & White-Label Portals
- **100% Plan-Gated Entitlements**: 15 boolean feature switches editable per plan tier.
- **Tenant Unit Economics & Profit Margins**: Real-time API token cost vs subscription revenue tracking (99%+ net margins).
- **White-Label Custom CNAME Domain Portals**: SSL certificate provisioning for custom domains (`booking.mysalon.az`).

---

## 📱 Mobile & Web Applications

1. **SaaS Admin Web Panel** (`frontend/admin-dashboard`): SaaS owner plan gating, live AI model discovery, tenant profit analytics.
2. **Business Owner & Staff Web Panel** (`frontend/business-dashboard`): AI engine switcher, calendar, chat inbox, payment logs, RAG knowledge manager.
3. **Business Mobile App** (`mobile/business_app`): 16 screens in Flutter (Schedule agenda, Emergency staff replacement, CRM loyalty, Roster, Payments log).
4. **Customer Mobile App** (`mobile/customer_app`): 8 screens in Flutter (OTP login, Business directory, 4-step booking wizard, Visit history).

---

## 🛠️ Architecture & Stack

```
                    ┌─────────────────────────────────────────┐
                    │               CUSTOMERS                 │
                    │   WhatsApp / Voice Notes / IG / App     │
                    └────────────────────┬────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │         EVOLUTION API / META WEBHOOK    │
                    └────────────────────┬────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │       FASTAPI BACKEND & AI ENGINE       │
                    │ ┌─────────────────────────────────────┐ │
                    │ │       AIProviderFactory / RAG       │ │
                    │ │  Gemini 3.5 / Claude 3.7 / GPT-4o  │ │
                    │ └──────────────────┬──────────────────┘ │
                    │                    │                    │
                    │ ┌──────────────────▼──────────────────┐ │
                    │ │      AvailabilityEngine (Slots)     │ │
                    │ └─────────────────────────────────────┘ │
                    └────────────────────┬────────────────────┘
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          ▼                              ▼                              ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│  POSTGRES DB     │           │   REDIS / CELERY │           │ EXTERNAL APIS    │
│  pgvector HNSW   │           │   Beat Reminders │           │ GCal / Apple Cal │
│  Multi-Tenant    │           │   Win-Back Jobs  │           │ Payriff / EPoint │
└──────────────────┘           └──────────────────┘           └──────────────────┘
```

---

## 🚀 Quick Start & Launch Commands

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- Flutter 3.x

### Run Production Container Stack
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Start Backend API Server
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 22800
```

### Launch Web Dashboards
```bash
# SaaS Admin Dashboard (Port 22300)
cd frontend/admin-dashboard && npm run dev

# Business Owner Dashboard (Port 22301)
cd frontend/business-dashboard && npm run dev
```

### Launch Mobile Applications
```bash
# Business App
cd mobile/business_app && flutter run

# Customer App
cd mobile/customer_app && flutter run
```

---

## 🧪 Verification & Unit Tests

Run the full pytest suite verifying all multi-model, plan-gated, and commercial feature services:
```bash
pytest backend/tests/
```
