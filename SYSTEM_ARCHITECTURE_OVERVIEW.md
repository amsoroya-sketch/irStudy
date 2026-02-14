# System Architecture Overview

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         irStudy Medical Platform                         │
│                  (ICRP Preparation - Australian Standards)               │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │   Main Frontend        │  │   EMR Practice Frontend             │   │
│  │   (React + TypeScript) │  │   (React + TypeScript)              │   │
│  │   Port: 5173           │  │   Port: 5174                        │   │
│  │                        │  │                                     │   │
│  │   Features:            │  │   Features:                         │   │
│  │   • MCQ Practice       │  │   • Cerner PowerChart Theme         │   │
│  │   • OSCE Practice      │  │   • Epic EHR Theme                  │   │
│  │   • Progress Tracking  │  │   • SOAP Note Editor                │   │
│  │   • Flashcards         │  │   • PBS Prescriptions               │   │
│  │   • Study Cards        │  │   • MBS Pathology Orders            │   │
│  └────────────────────────┘  │   • AI Validation (Kimi FREE)       │   │
│                              └─────────────────────────────────────┘   │
│                                                                          │
└───────────────┬──────────────────────────────────┬───────────────────────┘
                │                                  │
                │ HTTP/REST API                    │ HTTP/REST API
                │                                  │
┌───────────────▼──────────────────────────────────▼───────────────────────┐
│                         BACKEND LAYER (FastAPI)                          │
│                         Port: 8001                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    API Endpoints (v1)                            │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ • /api/v1/mcqs              - MCQ CRUD                          │   │
│  │ • /api/v1/osces             - OSCE CRUD                         │   │
│  │ • /api/v1/users             - User management                   │   │
│  │ • /api/v1/progress          - Progress tracking                 │   │
│  │ • /api/v1/auth              - Authentication (JWT)              │   │
│  │                                                                  │   │
│  │ EMR-Specific Endpoints:                                         │   │
│  │ • /api/v1/emr/sessions      - EMR practice sessions             │   │
│  │ • /api/v1/emr/soap-notes    - SOAP documentation                │   │
│  │ • /api/v1/emr/prescriptions - PBS prescriptions                 │   │
│  │ • /api/v1/emr/pathology     - MBS pathology orders              │   │
│  │ • /api/v1/validation        - Python validators (PBS/MBS)       │   │
│  │ • /api/v1/ai-validation     - AI validation (Kimi/Claude)       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Validation Pipeline (3 Layers)                      │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  Layer 1 (Frontend): Zod Schemas             <50ms    ⚡       │   │
│  │  Layer 2 (Backend):  PBS/MBS Validators      <1s     🔍       │   │
│  │  Layer 3 (AI):       Kimi/Claude             3-5s    🤖       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   AI Router (Kimi Adapter)                       │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  if AI_PROVIDER == 'kimi':                                      │   │
│  │      ➜ KimiAdapter ➜ Moonshot AI (FREE) ✅                     │   │
│  │  else:                                                           │   │
│  │      ➜ Anthropic SDK ➜ Claude API (PAID) 💰                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
                │ SQLAlchemy ORM
                │
┌───────────────▼──────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (PostgreSQL)                           │
│                    Port: 5432                                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Core Tables     │  │  EMR Tables      │  │  Analytics Tables    │  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────────┤  │
│  │ • users          │  │ • emr_sessions   │  │ • user_progress      │  │
│  │ • mcqs           │  │ • soap_notes     │  │ • mcq_attempts       │  │
│  │ • osces          │  │ • prescriptions  │  │ • weak_topics        │  │
│  │ • mock_patients  │  │ • pathology_orders│ │ • study_streaks     │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
│                                                                          │
│  Relationships:                                                          │
│  • users ──→ emr_sessions (user practices EMR)                          │
│  • osces ──→ emr_sessions (via linked_osce_id)                          │
│  • emr_sessions ──→ soap_notes, prescriptions, pathology_orders         │
│  • users ──→ user_progress (specialty-specific tracking)                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────┐           ┌──────────────────────────────┐  │
│  │  Kimi API (Moonshot)   │           │  Claude API (Anthropic)      │  │
│  │  api.moonshot.cn       │           │  api.anthropic.com           │  │
│  │                        │           │                              │  │
│  │  Model: moonshot-v1    │           │  Model: claude-3.5-sonnet    │  │
│  │  Cost: FREE ✅         │           │  Cost: $3-15/M tokens 💰    │  │
│  │  Context: 128K         │           │  Context: 200K               │  │
│  └────────────────────────┘           └──────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  📁 /data/mcqs/                                                          │
│     • week3_cardiology_200_mcqs.json      (1.1MB)                       │
│     • week3_respiratory_200_mcqs.json     (1.1MB)                       │
│     • psychiatry_*.json                   (286KB total)                 │
│     • missing_topics_comprehensive_mcqs.json                            │
│                                                                          │
│  📁 /data/osces/                                                         │
│     • cardiology_50_osces.json            (163KB)                       │
│     • respiratory_50_osces.json           (168KB)                       │
│     • psychiatry_40_osces.json            (137KB)                       │
│     • missing_topics_comprehensive_osces.json                           │
│                                                                          │
│  📜 Import: python scripts/load_sample_data.py                          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

### MCQ Practice Flow

```
User → Frontend (MCQ List) → API /api/v1/mcqs
                                   ↓
                            Database: mcqs table
                                   ↓
User selects MCQ ← Frontend ← API returns MCQ
                                   ↓
User answers ──────→ Frontend → API /api/v1/mcq-attempts
                                   ↓
                            Database: mcq_attempts table
                                   ↓
                            Update: user_progress table
                                   ↓
Statistics & Feedback ← Frontend ← API returns result
```

### OSCE Practice Flow

```
User → Frontend (OSCE List) → API /api/v1/osces
                                   ↓
                            Database: osces table
                                   ↓
User selects OSCE ← Frontend ← API returns OSCE
                                   ↓
User practices ──────────────────────┐
(reads scenario, practices clinically)│
                                     ↓
Optional: Practice documentation in EMR
                                     ↓
User → EMR Frontend → API /api/v1/emr/sessions
                           (linked_osce_id set)
                                   ↓
User documents SOAP note, orders tests, etc.
                                   ↓
                            Database: soap_notes, etc.
```

### EMR Practice Flow (Standalone or OSCE-Linked)

```
User → Dashboard → Select Theme (Cerner/Epic)
                         ↓
              Create Session → API /api/v1/emr/sessions
                         ↓
              Database: emr_sessions table
                         ↓
┌────────────────────────┴────────────────────────┐
│                                                 │
│  User documents in EMR:                        │
│  • SOAP Note ──→ API /api/v1/emr/soap-notes   │
│  • Prescription ─→ API /api/v1/emr/prescriptions│
│  • Pathology ───→ API /api/v1/emr/pathology    │
│                                                 │
│  Auto-save every 30 seconds ⏱️                 │
│                                                 │
└────────────────────────┬────────────────────────┘
                         ↓
              Validation Pipeline:
                         ↓
        ┌────────────────┴────────────────┐
        │                                 │
    Layer 1 (Zod)              Layer 2 (Python)
    <50ms ⚡                   <1s 🔍
    Client-side                PBS/MBS validators
        │                                 │
        └────────────────┬────────────────┘
                         ↓
                    Layer 3 (AI)
                    3-5s 🤖
                    Kimi/Claude
                         ↓
        Educational Feedback to User:
        • Clinical accuracy score
        • Documentation quality
        • Areas for improvement
        • Learning points
```

---

## 🔄 Integration Points

### 1. Shared User Authentication
```
Frontend (Main) ────┐
                    ├──→ Backend /api/v1/auth ──→ users table
Frontend (EMR) ─────┘
                    ↓
              Same JWT token works for both
```

### 2. OSCE → EMR Practice
```
User completes OSCE scenario
       ↓
Option to practice documenting in EMR
       ↓
EMR session created with linked_osce_id
       ↓
User documents the same case in EMR format
       ↓
Both OSCE attempt and EMR session tracked in progress
```

### 3. Unified Progress Tracking
```
user_progress table tracks:
• MCQ performance (per specialty)
• OSCE scores (per specialty)
• EMR documentation quality (per specialty)
• Weak topics across all modalities
• Study streaks
```

---

## 🛠️ Technology Stack

### Frontend
- **React 18.2** + **TypeScript 5.3**
- **Vite 5.0** (build tool)
- **Tailwind CSS 3.4** (styling with Cerner/Epic themes)
- **TanStack Query 5.17** (API state management)
- **Zustand 4.4** (global state)
- **React Hook Form 7.49** + **Zod 3.22** (validation)
- **Framer Motion 11.0** (animations)

### Backend
- **FastAPI 0.109** (Python 3.11)
- **SQLAlchemy 2.0** (ORM)
- **Alembic 1.13** (migrations)
- **Pydantic 2.5** (validation)
- **Python-Jose 3.3** (JWT)
- **httpx 0.25** (HTTP client for Kimi)

### Database
- **PostgreSQL 15**
- **Redis 5.0** (caching - optional)

### AI
- **Kimi 2.5** (Moonshot AI) - FREE ✅
- **Claude 3.5 Sonnet** (Anthropic) - PAID (optional)

---

## 📍 File Locations Quick Reference

### Frontend (Main)
```
/home/dev/Development/irStudy/frontend/
├── src/
│   ├── components/      # MCQ, OSCE, flashcard components
│   ├── pages/           # Main pages
│   ├── hooks/           # Custom React hooks
│   └── api/             # API client
```

### Frontend (EMR)
```
/home/dev/Development/irStudy/emr-frontend/
├── src/
│   ├── components/
│   │   ├── cerner/      # Cerner PowerChart components
│   │   └── epic/        # Epic EHR components
│   ├── stores/          # Zustand stores
│   ├── hooks/           # Custom hooks (auto-save, typing metrics)
│   └── api/             # API client
```

### Backend
```
/home/dev/Development/irStudy/backend/
├── src/
│   ├── api/v1/          # API endpoints
│   ├── db/
│   │   ├── models.py    # SQLAlchemy models
│   │   └── base.py      # Database connection
│   ├── validators/      # PBS/MBS/AI validators
│   ├── ai_router/       # Kimi adapter
│   └── auth/            # JWT authentication
```

### Data
```
/home/dev/Development/irStudy/data/
├── mcqs/                # MCQ JSON files
├── osces/               # OSCE JSON files
└── embeddings/          # RAG embeddings (optional)
```

### Documentation
```
/home/dev/Development/irStudy/
├── KIMI_SETUP_GUIDE.md              # Kimi integration guide
├── DATABASE_IMPORT_GUIDE.md         # MCQ/OSCE import guide
├── AI_PROVIDER_QUICK_REFERENCE.md   # Switch Kimi/Claude
└── emr-practice-system/ralph-prds/  # Implementation PRDs
```

---

## 🚀 Quick Start Commands

### 1. Import Data
```bash
cd /home/dev/Development/irStudy
python scripts/load_sample_data.py --mcqs 200 --osces 50
```

### 2. Start Backend
```bash
cd backend
docker-compose up -d
# API: http://localhost:8001
```

### 3. Start Main Frontend
```bash
cd frontend
npm run dev
# App: http://localhost:5173
```

### 4. Start EMR Frontend
```bash
cd emr-frontend
npm run dev
# App: http://localhost:5174
```

### 5. Test API
```bash
# Get MCQs
curl http://localhost:8001/api/v1/mcqs | jq

# Get OSCEs
curl http://localhost:8001/api/v1/osces | jq

# Check AI validation
curl http://localhost:8001/api/v1/ai-validation/health | jq
```

---

## 💰 Cost Summary

| Component | Technology | Cost |
|-----------|-----------|------|
| Frontend (Main) | React + Vite | $0 (static) |
| Frontend (EMR) | React + Vite | $0 (static) |
| Backend | FastAPI + Docker | $0 (local) or ~$10/month (VPS) |
| Database | PostgreSQL | $0 (Docker) or ~$10/month (managed) |
| **AI Validation** | **Kimi 2.5** | **$0 FREE** ✅ |
| AI Validation (alt) | Claude 3.5 | ~$324/month (for 9K validations) |

**Total Monthly Cost (with Kimi)**: **$0-20** 🎉

---

**Last Updated**: 2026-02-03
**Status**: ✅ Complete System Architecture
