# AI Appointment SaaS — Master Multi-Tenant Enterprise Platform (100% Completed)

A high-performance, multi-tenant enterprise SaaS platform where businesses (from 1-person solo shops to multi-branch salon/clinic chains) let an autonomous AI Agent handle appointment bookings, rescheduling, cancellations, customer inquiries, and staff notifications over **WhatsApp**, **Instagram Direct**, and **Facebook Messenger**.

> **Zero-App / Zero-Web Requirement**: Customers and Staff can manage their entire booking workflow over WhatsApp using natural text or **voice notes (audio messages)** in **Azerbaijani (AZ)**, **English (EN)**, and **Russian (RU)**.

---

## 🌟 Master Platform Capabilities (Phases 1-5 Complete)

### 🤖 1. Multi-Provider AI Conversation Core (SaaS Owner Controlled)
- **SaaS Model Assignment Control**: AI Model selection is 100% managed by the SaaS Owner per Plan tier (**Google Gemini 3.5 Flash**, **Anthropic Claude 3.7 Sonnet**, **OpenAI GPT-4o**).
- **Live Source Model Discovery**: Automatically queries official provider REST APIs to discover and activate newly released AI models with 1 click.
- **RAG "Learn from Mistakes" Engine**: In-memory and PostgreSQL `pgvector` HNSW vector embeddings for instant business knowledge & mistake correction.
- **WhatsApp Voice Notes & Audio Messages**: Speech-to-intent processing for 5-second voice notes.
- **Internal WhatsApp Staff Group Bot (`@g.us`)**: Staff and owners run daily agenda, next-in-list, revenue, and no-show queries inside WhatsApp groups.

### 📍 2. Geo-Location & Shift-Aware Overtime Scheduling
- **WhatsApp Geo-Routing (`GeoRoutingService`)**: Calculates Haversine GPS distance or matches Baku landmark keywords (28 May, Gənclik, Nərimanov, Elmlər) to route customers to the nearest branch (`allows_geo_routing`).
- **Shift-Aware Overtime Engine (`ShiftScheduleService`)**: Supports staff & solo-owner shifts (Morning 09-15, Evening 15-21, Full-Day, Custom) and restricts bookings to shift bounds unless marked for Overtime (`allows_shift_management`).

### 📅 3. Calendar Sync & Advanced Scheduling
- **Single-Truth Availability Engine**: Prevents double-booking across multi-branch staff schedules.
- **Google Calendar 2-Way Sync**: Real-time event creation & freeBusy checks.
- **Apple Calendar (CalDAV RFC 4791) 2-Way Sync**: iCloud CalDAV integration.
- **Waitlist & Auto-Backfill**: Automatically fills cancelled appointment slots with waitlisted customers over WhatsApp.
- **Dynamic Off-Peak Pricing & Surge Hours**: Time-based 15% off-peak morning discounts and 15% weekend afternoon peak surges.
- **Multi-Service Combo Packages**: Sequential time-block calculation and 15% combo package discounts.
- **AI Group & Event Scheduler**: Concurrent slot booking across multiple staff members for group visits.

### 🔒 4. Unexposed WhatsApp Security & Payments
- **Unexposed Evolution API Container**: Evolution API is 100% internal and unexposed to public internet for enterprise security.
- **In-Dashboard WhatsApp QR Pairing Modal**: Business Owners generate and scan base64 pairing QR codes directly inside the Business Web Dashboard (`http://localhost:22301`).
- **Azerbaijan Payment Gateways**: Native **Payriff** & **EPoint** REST API integrations for online deposit checkout links.
- **AI Dynamic No-Show Deposits**: Enforces mandatory deposits for high-risk customers (2+ past no-shows) or high-value bookings (>50 AZN).

### 🎛️ 5. 100% Plan-Gated SaaS Entitlements (17 Features)
- **17 Plan-Gated Entitlement Switches**: Editable per plan tier in SaaS Admin Panel.
- **Tenant Unit Economics & Profit Margins**: Real-time API token cost vs subscription revenue tracking (99%+ net margins).
- **White-Label Custom Domain Portals**: SSL certificate provisioning for custom Apex domains (`beautystudio.az`) and subdomains (`booking.beautystudio.az`).

---

## 📱 Mobile & Web Applications

1. **SaaS Admin Web Panel** (`frontend/admin-dashboard` on **Port 22300**): SaaS owner plan gating, model assignment, live AI model discovery, tenant profit analytics.
2. **Business Owner & Staff Web Panel** (`frontend/business-dashboard` on **Port 22301**): Read-only plan assigned AI model badge, calendar, chat inbox, in-dashboard WhatsApp QR pairing modal, payment logs, RAG knowledge manager.
3. **Business Mobile App** (`mobile/business_app`): 16 screens in Flutter (Schedule agenda, Emergency staff replacement, CRM loyalty, Roster, Payments log).
4. **Customer Mobile App** (`mobile/customer_app`): 8 screens in Flutter (OTP login, Business directory, 4-step booking wizard, Visit history).

---

## 🚀 Quick Start & Launch Commands

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- Flutter 3.x

### Run Production Container Stack
```bash
docker compose up -d
```

### Run Local Development Stack (Hot-Reloading & Debug Logs)
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

---

## 🧪 Verification & Unit Tests

Run the full pytest suite verifying all multi-model, plan-gated, geo-routing, shift-aware, and commercial feature services:
```bash
pytest backend/tests/
```
