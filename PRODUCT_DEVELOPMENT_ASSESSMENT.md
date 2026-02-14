# AMC Exam Preparation Platform - Product Development Assessment

## Executive Summary

Your project has a **strong foundation** for commercialization with:
- ✅ 18,000+ RAG-validated MCQs across specialties
- ✅ Multi-agent AI system for content generation
- ✅ Australian-focused medical content (eTG, AMH, AMC format)
- ✅ Self-hosted infrastructure (Qdrant, PostgreSQL, Redis)
- ✅ Quality validation systems (citations, clinical accuracy)

---

## 1. Product Tier Strategy

### Tier 1: "AMC Prep Free" (Freemium)
**Purpose:** User acquisition and trial

| Feature | Details |
|---------|---------|
| MCQ Access | 100 questions per specialty (800 total) |
| OSCE Scenarios | 5 per specialty |
| Practice Exams | 1 timed exam |
| Progress Tracking | Basic (questions attempted, score) |
| Mobile Access | Web app only |
| Ads | Optional (revenue stream) |

**Target:** 10,000+ users for lead generation

---

### Tier 2: "AMC Prep Pro" ($29/month or $149/year)
**Purpose:** Core revenue driver

| Feature | Details |
|---------|---------|
| MCQ Access | Unlimited (18,000+ questions) |
| OSCE Scenarios | 3,000+ scenarios |
| Practice Exams | Unlimited timed exams |
| RAG-Powered AI Tutor | Ask questions, get cited answers |
| Personalized Study Plans | AI-generated based on weak areas |
| Performance Analytics | Detailed breakdown by topic |
| Citation Access | Full textbook references |
| Offline Mode | Download for study without internet |
| Device Sync | Progress across all devices |

**Target:** 1,000-2,000 paying subscribers

---

### Tier 3: "AMC Prep Ultimate" ($79/month or $399/year)
**Purpose:** High-value offering for serious candidates

| Feature | Details |
|---------|---------|
| Everything in Pro | Plus: |
| 1-on-1 Virtual OSCE Practice | AI-simulated examiner |
| Essay Feedback | AI + human expert review (2/month) |
| Live Group Sessions | Weekly webinars with AMC veterans |
| Priority Support | <4 hour response time |
| Custom Question Sets | Focus on specific weaknesses |
| Mock Exam Analysis | Detailed performance review |
| Study Buddy Matching | Connect with other candidates |
| Guarantee | Pass or get extended access |

**Target:** 200-500 high-value subscribers

---

### Tier 4: "Institutional License" ($5,000-$20,000/year)
**Purpose:** B2B revenue from medical colleges

| Feature | Details |
|---------|---------|
| Multi-User Licenses | 50-500 students |
| Admin Dashboard | Track all students' progress |
| Custom Branding | White-label option |
| Integration APIs | LMS integration (Canvas, Moodle) |
| Bulk User Management | CSV import, SSO |
| Analytics Reports | Institution-wide performance |
| Priority Content Updates | Latest AMC changes |
| Dedicated Account Manager | |

**Target:** 20-50 medical colleges in Australia, India, Pakistan, Philippines

---

## 2. Multi-Device Architecture

### Current State Analysis
- Current: Single-page web app (respiratory-mcq-app)
- Tech: Vanilla JS, no backend API
- Limitation: No user accounts, no sync

### Recommended Multi-Device Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│  Web App    │  iOS App    │ Android App │   Desktop App         │
│  (React)    │  (Swift)    │  (Kotlin)   │   (Electron/Tauri)    │
└──────┬──────┴──────┬──────┴──────┬──────┴───────────┬───────────┘
       │             │             │                  │
       └─────────────┴──────┬──────┴──────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     API GATEWAY (Kong/AWS API GW)              │
│  • Rate limiting  • Authentication  • SSL termination          │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                   BACKEND SERVICES (FastAPI)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │
│  │   Auth      │ │   MCQ       │ │    AI Tutor             │  │
│  │  Service    │ │  Service    │ │   (RAG + Agents)        │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │
│  │  Progress   │ │  Payment    │ │  Notification           │  │
│  │  Service    │ │  Service    │ │  Service                │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     DATA LAYER                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐  │
│  │  PostgreSQL │ │   Qdrant    │ │    Redis    │  Neo4j  │  │
│  │  (Users)    │ │  (Vectors)  │ │   (Cache)   │ (Graph) │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack Recommendations

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Web Frontend** | Next.js 14 + TypeScript | SEO, SSR, API routes |
| **Mobile Apps** | React Native / Flutter | Single codebase, native feel |
| **Desktop** | Tauri (Rust) | Lightweight, secure, native |
| **Backend API** | FastAPI + Python | Already in your stack |
| **Database** | PostgreSQL 16 | ACID compliance, JSON support |
| **Auth** | Clerk / Auth0 / Supabase Auth | Secure, MFA, social login |
| **Payments** | Stripe | Subscription management |
| **CDN** | Cloudflare / AWS CloudFront | Global edge caching |
| **Storage** | AWS S3 / Cloudflare R2 | MCQ data, user uploads |

---

## 3. Core Product Features

### 3.1 Adaptive Learning Engine
```python
# Concept: Spaced repetition + weak area targeting
class AdaptiveLearningEngine:
    def calculate_next_review(self, question_id, user_performance):
        """
        - Correct answer: Increase interval (1 day → 3 days → 7 days → 14 days)
        - Incorrect answer: Reset interval, add to weak topics
        - AMC focus: Prioritize high-frequency topics
        """
        pass
    
    def generate_daily_queue(self, user_id):
        """
        Mix of:
        - 40% Due for review (spaced repetition)
        - 30% Weak topics (low performance)
        - 20% New topics (not yet covered)
        - 10% Random (prevent context cueing)
        """
        pass
```

### 3.2 AI Tutor (RAG-Powered)
```python
# Students can ask: "Why is asthma worse at night?"
class AITutor:
    def answer_question(self, query, user_context):
        # 1. Retrieve relevant chunks from Qdrant
        # 2. Check user subscription tier
        # 3. Generate answer with citations
        # 4. Track learning gaps
        pass
```

### 3.3 OSCE Simulator
- **Video-based scenarios:** Patient actors with branching paths
- **Timer:** 8-minute station simulation
- **Checklist grading:** AI + self-assessment
- **Peer review:** Submit for community feedback (Ultimate tier)

### 3.4 Performance Dashboard
- **Spider chart:** Performance across AMC blueprint domains
- **Predicted score:** ML model based on practice performance
- **Study streak:** Gamification element
- **Comparison:** Anonymous percentile ranking

---

## 4. Security Architecture

### 4.1 Authentication & Authorization
```yaml
Auth Strategy:
  Primary: JWT tokens (access + refresh)
  MFA: TOTP (Google Authenticator) - required for Ultimate tier
  Social: Google, Apple Sign-In
  Session: 
    Access token: 15 minutes
    Refresh token: 7 days
    Max sessions: 5 devices
```

### 4.2 Data Protection
```yaml
Encryption:
  In Transit: TLS 1.3 (mandatory)
  At Rest: 
    PostgreSQL: AES-256
    Backups: GPG encrypted
  Sensitive Fields:
    - Email: Hashed (for lookup)
    - Payment: Tokenized (Stripe)
    - Progress: Encrypted per-user key

PII Handling:
  - Minimize collection (email only required)
  - GDPR/CCPA compliant deletion
  - Audit logs for data access
```

### 4.3 API Security
```python
# Rate Limiting (per user tier)
RATE_LIMITS = {
    "free": "100 requests/hour",
    "pro": "1000 requests/hour", 
    "ultimate": "5000 requests/hour"
}

# Additional protections:
# - CORS: Whitelist domains only
# - CSRF: Double-submit cookie pattern
# - SQL Injection: Parameterized queries (SQLAlchemy)
# - XSS: Output encoding, CSP headers
```

### 4.4 Content Protection (Critical for MCQs)
```python
class ContentProtection:
    """Prevent bulk scraping of your MCQ database"""
    
    measures = {
        "rate_limiting": "Max 10 questions/minute per IP",
        "watermarking": "Invisible user ID in exports",
        "obfuscation": "Dynamic option ordering",
        "bot_detection": "CAPTCHA after suspicious patterns",
        "legal": "Terms of Service + Copyright notices"
    }
```

---

## 5. Infrastructure & Deployment

### 5.1 Recommended Cloud Architecture
```
Production Environment:
├── Load Balancer (AWS ALB / Cloudflare)
├── API Servers (3x t3.medium - auto-scaling)
├── Background Workers (Celery + Redis)
├── PostgreSQL (RDS / Supabase - HA)
├── Qdrant (Managed or self-hosted)
├── S3 (MCQ assets, backups)
└── CloudFront (CDN for static assets)
```

### 5.2 Cost Estimates (Monthly)

| Component | Free Tier | Pro Tier (1K users) | Scale (10K users) |
|-----------|-----------|---------------------|-------------------|
| Compute | $0 (Vercel) | $200 | $800 |
| Database | $0 (Supabase) | $150 | $500 |
| Vector DB | $0 (self-host) | $100 | $300 |
| CDN | $0 | $50 | $200 |
| Auth | $0 | $25 | $100 |
| Monitoring | $0 | $50 | $150 |
| **Total** | **$0** | **~$575** | **~$2,050** |
| Revenue | $0 | $29,000/mo | $290,000/mo |
| **Margin** | - | **98%** | **99%** |

---

## 6. Implementation Roadmap

### Phase 1: MVP (2-3 months)
- [ ] Set up FastAPI backend with auth
- [ ] PostgreSQL schema for users, progress
- [ ] React web app (feature parity with current)
- [ ] Stripe integration for subscriptions
- [ ] Basic progress tracking

### Phase 2: Mobile & Features (2-3 months)
- [ ] React Native apps (iOS/Android)
- [ ] AI Tutor integration
- [ ] Spaced repetition algorithm
- [ ] Offline mode
- [ ] Push notifications

### Phase 3: Scale & Enterprise (3-4 months)
- [ ] Admin dashboard for institutions
- [ ] Advanced analytics
- [ ] SSO/SAML integration
- [ ] White-label options
- [ ] API for third-party integrators

---

## 7. Competitive Differentiation

| Feature | Your Platform | Competitors (AMC Prep) |
|---------|---------------|------------------------|
| Australian Guidelines | ✅ Native eTG/AMH | ❌ Generic |
| RAG-verified content | ✅ Every MCQ cited | ❌ Often outdated |
| AI Tutor | ✅ Real-time answers | ❌ Static only |
| OSCE Focus | ✅ 3,000+ scenarios | ❌ Limited |
| Offline Access | ✅ Full app works offline | ❌ Web only |
| Price | $29/mo (expected) | $50-100/mo |

---

## 8. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCQ content theft | High | High | Watermarking, legal, rate limiting |
| AMC syllabus changes | Medium | Medium | Automated content regeneration |
| Server costs scaling | Low | Medium | Efficient caching, CDN |
| Payment fraud | Medium | Medium | Stripe Radar, strong auth |
| Data breach | Low | Critical | Encryption, pentesting, bug bounty |

---

## 9. Recommended Next Steps

### Immediate (Week 1-2):
1. **Set up FastAPI project structure**
2. **Design PostgreSQL schema** (users, subscriptions, progress)
3. **Choose auth provider** (Clerk recommended for speed)
4. **Stripe account setup** (test mode)

### Short-term (Month 1):
1. **Build core API endpoints** (auth, MCQ fetch, progress save)
2. **Create Next.js web app** (replace current vanilla JS)
3. **Implement subscription gating**
4. **Basic analytics dashboard**

### Medium-term (Months 2-3):
1. **Mobile app development** (React Native)
2. **AI Tutor integration**
3. **Offline mode**
4. **Launch beta** (limited users)

---

## 10. Success Metrics

| Metric | Target (6 months) |
|--------|-------------------|
| Free Users | 5,000+ |
| Pro Subscribers | 500+ |
| Ultimate Subscribers | 50+ |
| Monthly Revenue | $20,000+ |
| NPS Score | 50+ |
| Churn Rate | <5% monthly |

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-31  
**Next Review:** After MVP completion
