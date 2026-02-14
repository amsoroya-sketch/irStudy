# Visual Architecture Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CLIENT LAYER                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │      WEB        │  │     iOS APP     │  │  ANDROID APP    │  │  DESKTOP (PWA)  │    │
│  │   (Next.js 14)  │  │ (React Native)  │  │ (React Native)  │  │   (Tauri)       │    │
│  │                 │  │                 │  │                 │  │                 │    │
│  │ • SEO Optimized │  │ • Offline Cache │  │ • Offline Cache │  │ • Focus Mode    │    │
│  │ • SSR Enabled   │  │ • Push Notif.   │  │ • Push Notif.   │  │ • Anki Export   │    │
│  │ • PWA Support   │  │ • Deep Links    │  │ • Deep Links    │  │ • PDF Reports   │    │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘    │
│           │                    │                    │                    │             │
│           │                    │                    │                    │             │
│           └────────────────────┴────────────────────┘────────────────────┘             │
│                                     │                                                    │
│                              ┌──────┴──────┐                                           │
│                              │   CDN/Edge  │  (Cloudflare/Vercel Edge)                │
│                              │   Caching   │  • Static assets                          │
│                              │             │  • MCQ content (cached)                   │
│                              └──────┬──────┘  • API response cache                     │
└─────────────────────────────────────┼──────────────────────────────────────────────────┘
                                      │
                                      ▼ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     API LAYER                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                          API GATEWAY (Kong/AWS API GW)                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │    │
│  │  │ Rate Limit   │  │    Auth      │  │   SSL/TLS    │  │  Request Routing     │ │    │
│  │  │ • Free: 100  │  │ • JWT Verify │  │ • TLS 1.3    │  │  • /api/* → Backend  │ │    │
│  │  │ • Pro: 1000  │  │ • API Keys   │  │ • HSTS       │  │  • /ws/* → WebSocket │ │    │
│  │  │ • Ult: 5000  │  │ • Device Mgmt│  │ • Cert Mgmt  │  │  • /graphql → Apollo │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────────┘ │    │
│  └─────────────────────────────────────────┬────────────────────────────────────────┘    │
│                                            │                                             │
│                    ┌───────────────────────┼───────────────────────┐                     │
│                    │                       │                       │                     │
│                    ▼                       ▼                       ▼                     │
│           ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│           │   GRAPHQL API   │    │    REST API     │    │  WEBSOCKET API  │             │
│           │   (Web Client)  │    │  (Mobile Apps)  │    │ (Real-time)     │             │
│           │                 │    │                 │    │                 │             │
│           │ • MCQ Queries   │    │ • Simple CRUD   │    │ • Sync Events   │             │
│           │ • Progress Sub  │    │ • Auth Endpoints│    │ • Collab Study  │             │
│           │ • AI Tutor      │    │ • File Uploads  │    │ • Notifications │             │
│           └────────┬────────┘    └────────┬────────┘    └────────┬────────┘             │
│                    │                       │                       │                     │
└────────────────────┼───────────────────────┼───────────────────────┼─────────────────────┘
                     │                       │                       │
                     └───────────────────────┼───────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   SERVICE LAYER                                          │
│                                                                                          │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │
│   │     AUTH      │  │     MCQ       │  │  SUBSCRIPTION │  │   PROGRESS    │            │
│   │   SERVICE     │  │   SERVICE     │  │   SERVICE     │  │   SERVICE     │            │
│   │               │  │               │  │               │  │               │            │
│   │ • Register    │  │ • Fetch MCQs  │  │ • Stripe Int. │  │ • Track Ans   │            │
│   │ • Login       │  │ • Shuffle Opt │  │ • Tier Check  │  │ • Analytics   │            │
│   │ • JWT Mgmt    │  │ • Watermark   │  │ • Webhooks    │  │ • Sync Engine │            │
│   │ • Device Mgmt │  │ • Rate Limit  │  │ • Trials      │  │ • SRS Cards   │            │
│   └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘            │
│           │                  │                  │                  │                    │
│           └──────────────────┴──────────────────┴──────────────────┘                    │
│                                    │                                                     │
│                                    ▼                                                     │
│   ┌───────────────────────────────────────────────────────────────────────────────┐    │
│   │                         AI TUTOR SERVICE (Optional)                            │    │
│   │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                     │    │
│   │  │  RAG Query   │───▶│   Qdrant     │    │    Claude    │                     │    │
│   │  │   Handler    │    │  Vector DB   │───▶│   API        │                     │    │
│   │  └──────────────┘    └──────────────┘    └──────────────┘                     │    │
│   │         │                                               │                     │    │
│   │         └───────────────────────────────────────────────┘                     │    │
│   │                              │                                                │    │
│   │                              ▼                                                │    │
│   │                     ┌─────────────────┐                                       │    │
│   │                     │  Answer with    │                                       │    │
│   │                     │  Citations      │                                       │    │
│   │                     └─────────────────┘                                       │    │
│   └───────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     DATA LAYER                                           │
│                                                                                          │
│   ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐             │
│   │    POSTGRESQL       │  │       REDIS         │  │      QDRANT         │             │
│   │   (Primary Store)   │  │      (Cache)        │  │    (Vector DB)      │             │
│   │                     │  │                     │  │                     │             │
│   │ • Users             │  │ • Sessions          │  │ • Medical Chunks    │             │
│   │ • Subscriptions     │  │ • Rate Limits       │  │ • Embeddings        │             │
│   │ • Progress          │  │ • Hot MCQs          │  │ • RAG Search        │             │
│   │ • Study Sessions    │  │ • Leaderboards      │  │ • Similarity        │             │
│   │ • SRS Cards         │  │ • Real-time Pub/Sub │  │ • Recommendations   │             │
│   │                     │  │                     │  │                     │             │
│   │ [HA: Primary+Replica│  │ [Cluster: 3 nodes]  │  │ [Single Node]       │             │
│   │  Daily Backups]     │  │  LRU Eviction       │  │  768-dim vectors    │             │
│   └─────────────────────┘  └─────────────────────┘  └─────────────────────┘             │
│                                                                                          │
│   ┌───────────────────────────────────────────────────────────────────────────────┐    │
│   │                           OBJECT STORAGE (S3/R2)                               │    │
│   │  • MCQ Image Assets          • User Exports          • Backups                 │    │
│   │  • OSCE Videos               • Study Reports         • Log Archives            │    │
│   └───────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EXTERNAL SERVICES                                        │
│                                                                                          │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │
│   │    STRIPE     │  │    CLERK      │  │    POSTMARK   │  │    SENTRY     │            │
│   │   Payments    │  │     Auth      │  │    Email      │  │ Error Tracking│            │
│   │               │  │               │  │               │  │               │            │
│   │ • Subscriptions│  │ • Social Login│  │ • Welcome     │  │ • Crash Reports│           │
│   │ • Webhooks    │  │ • MFA         │  │ • Reset Pass  │  │ • Performance │            │
│   │ • Invoicing   │  │ • Session Mgmt│  │ • Marketing   │  │ • Alerts      │            │
│   └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘            │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Study Session

```
User opens app → Check Auth → Load Cached MCQs
     │                │              │
     ▼                ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────────┐
│  Cache  │    │  Clerk  │    │  Watermelon │
│  Check  │    │  Verify │    │  DB (Mobile)│
└────┬────┘    └────┬────┘    └──────┬──────┘
     │              │                 │
     └──────────────┴─────────────────┘
                    │
                    ▼
         ┌─────────────────┐
         │  Device Online? │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
    ┌─────────┐      ┌─────────────┐
    │  SYNC   │      │  OFFLINE    │
    │  MODE   │      │  MODE       │
    │         │      │             │
    │• Fetch  │      │• Use local  │
    │  new MCQs     │  cache      │
    │• Sync   │      │• Queue     │
    │  progress     │  actions    │
    │• Update │      │• Sync later│
    │  SRS cards    │             │
    └────┬────┘      └─────────────┘
         │
         ▼
┌───────────────────────────┐
│   Answer Question         │
│   • Store locally         │
│   • Update UI             │
│   • Queue for sync        │
└───────────┬───────────────┘
            │
            ▼ (Background)
┌───────────────────────────┐
│   Sync to Server          │
│   • POST /progress        │
│   • Update leaderboard    │
│   • Recalc SRS schedule   │
└───────────────────────────┘
```

---

## Offline-First Strategy

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OFFLINE CAPABILITY MATRIX                         │
├──────────────────┬───────────┬───────────┬───────────┬──────────────┤
│    Feature       │   Web     │   iOS     │  Android  │   Desktop    │
├──────────────────┼───────────┼───────────┼───────────┼──────────────┤
│ MCQ Practice     │    ✅     │    ✅     │    ✅     │     ✅       │
│   Cache Size     │   500     │   2000    │   2000    │    5000      │
│                  │ questions │ questions │ questions │  questions   │
├──────────────────┼───────────┼───────────┼───────────┼──────────────┤
│ Progress Tracking│    ✅     │    ✅     │    ✅     │     ✅       │
│   Sync Strategy  │  SW Cache │  SQLite   │  SQLite   │  LocalStorage│
│                  │ + IndexedDB         + Background Jobs            │
├──────────────────┼───────────┼───────────┼───────────┼──────────────┤
│ AI Tutor         │    ❌     │    ❌     │    ❌     │     ❌       │
│   Reason         │     Requires internet connection                 │
├──────────────────┼───────────┼───────────┼───────────┼──────────────┤
│ OSCE Videos      │    ⚠️     │    ⚠️     │    ⚠️     │     ⚠️       │
│   Capability     │   Download on WiFi only (user preference)        │
├──────────────────┼───────────┼───────────┼───────────┼──────────────┤
│ Analytics        │    ⚠️     │    ✅     │    ✅     │     ⚠️       │
│   Behavior       │   Cached  │   Full    │   Full    │   Cached     │
│                  │   daily   │   offline │   offline │   daily      │
└──────────────────┴───────────┴───────────┴───────────┴──────────────┘

Legend: ✅ Full  ⚠️ Partial  ❌ None
```

---

## Security Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SECURITY ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  LAYER 1: PERIMETER                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • DDoS Protection (Cloudflare)                                  │    │
│  │  • WAF Rules (SQLi, XSS blocking)                               │    │
│  │  • Bot Detection (prevent scraping)                             │    │
│  │  • Geo-blocking (if needed)                                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  LAYER 2: TRANSPORT                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • TLS 1.3 (mandatory)                                          │    │
│  │  • Certificate pinning (mobile)                                 │    │
│  │  • HSTS headers                                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  LAYER 3: AUTHENTICATION                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • JWT Access Tokens (15 min expiry)                            │    │
│  │  • Refresh Tokens (7 day expiry, rotation)                      │    │
│  │  • Device fingerprinting                                        │    │
│  │  • MFA for Ultimate tier                                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  LAYER 4: AUTHORIZATION                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • Role-based (free/pro/ultimate)                               │    │
│  │  • Resource-based (own data only)                               │    │
│  │  • Rate limiting by tier                                        │    │
│  │  • Concurrent session limits                                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  LAYER 5: APPLICATION                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • Input validation (Pydantic schemas)                          │    │
│  │  • SQL injection prevention (parameterized queries)             │    │
│  │  • XSS protection (output encoding)                             │    │
│  │  • CSRF tokens (web)                                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  LAYER 6: DATA                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • Encryption at rest (AES-256)                                 │    │
│  │  • Field-level encryption (PII)                                 │    │
│  │  • Backup encryption (GPG)                                      │    │
│  │  • Secure key management (AWS KMS/HashiCorp Vault)              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  LAYER 7: AUDIT                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • Access logging (all API calls)                               │    │
│  │  • Data change audit trail                                      │    │
│  │  • Security event alerting                                        │    │
│  │  • Retention: 90 days hot, 1 year cold                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Scaling Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     HORIZONTAL SCALING PATH                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 1: SINGLE SERVER (0-1K users)                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │    │
│  │  │   Next.js    │    │   FastAPI    │    │  PostgreSQL  │      │    │
│  │  │   (Vercel)   │    │   (Railway)  │    │  (Supabase)  │      │    │
│  │  └──────────────┘    └──────────────┘    └──────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  PHASE 2: SEPARATION (1K-10K users)                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │    │
│  │  │   Next.js    │◄──►│   FastAPI    │◄──►│  PostgreSQL  │      │    │
│  │  │   (Vercel)   │    │   (Railway)  │    │   (RDS)      │      │    │
│  │  └──────────────┘    └──────┬───────┘    └──────┬───────┘      │    │
│  │                             │                   │              │    │
│  │                        ┌────┴────┐         ┌────┴────┐         │    │
│  │                        │  Redis  │         │  Read   │         │    │
│  │                        │  Cache  │         │ Replica │         │    │
│  │                        └─────────┘         └─────────┘         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  PHASE 3: MULTI-INSTANCE (10K-100K users)                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌──────────────┐    ┌──────────────────────────────────────┐  │    │
│  │  │   Next.js    │◄──►│   Load Balancer                      │  │    │
│  │  │   (Vercel)   │    │   (AWS ALB)                          │  │    │
│  │  └──────────────┘    └──────────┬───────────────────────────┘  │    │
│  │                                 │                              │    │
│  │         ┌───────────────────────┼───────────────────────┐      │    │
│  │         │                       │                       │      │    │
│  │         ▼                       ▼                       ▼      │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │    │
│  │  │  FastAPI #1  │    │  FastAPI #2  │    │  FastAPI #N  │      │    │
│  │  │  (ECS)       │    │  (ECS)       │    │  (ECS)       │      │    │
│  │  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │    │
│  │         └─────────────────────┼─────────────────────┘          │    │
│  │                               │                                │    │
│  │  ┌────────────────────────────┼────────────────────────────┐   │    │
│  │  │                     PostgreSQL Cluster                   │   │    │
│  │  │  (Primary + 2 Replicas + Connection Pooler - PgBouncer)  │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  │                               │                                 │    │
│  │                        ┌──────┴──────┐                         │    │
│  │                        │ Redis Cluster│                         │    │
│  │                        │ (3 Masters)  │                         │    │
│  │                        └─────────────┘                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  PHASE 4: GLOBAL (100K+ users)                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • Multi-region (Australia, India, Philippines)                 │    │
│  │  • Read replicas in each region                                 │    │
│  │  • CDN edge caching                                             │    │
│  │  • Database sharding by region                                  │    │
│  │  • Event-driven architecture (Kafka)                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Metrics by Phase

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|
| Users | <1,000 | 1K-10K | 10K-100K | >100K |
| API Requests/day | <100K | 1M | 10M | 100M+ |
| Database Size | <10GB | <100GB | <1TB | Sharded |
| Cache Hit Rate | N/A | >70% | >85% | >90% |
| p95 Latency | <500ms | <300ms | <200ms | <100ms |
| Uptime SLA | 99% | 99.5% | 99.9% | 99.99% |
| Team Size | 1-2 | 2-4 | 4-8 | 8+ |

---

**Files Created:**
- `ARCHITECTURE_DECISIONS.md` - Detailed decision matrix
- `ARCHITECTURE_DIAGRAM.md` - Visual system overview (this file)

**Next Step:** Review these diagrams and decisions, then choose your Phase 1 architecture to implement.
