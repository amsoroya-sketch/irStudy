# Architecture Decision Records (ADRs)

## How to Use This Document

This document tracks architectural decisions for the AMC Prep Platform. Each ADR follows this format:
- **Status**: Proposed / Accepted / Deprecated / Superseded
- **Context**: Why we need to make this decision
- **Decision**: What we decided
- **Consequences**: Trade-offs and implications

---

## ADR 001: Multi-Device Client Strategy

**Status**: ✅ Accepted

**Context**: 
The platform needs to support web (desktop/mobile), iOS, and Android. We need to decide how to build and maintain these clients efficiently.

**Decision**: 
Use **React Native (Expo)** for mobile, **Next.js 14** for web, and skip native desktop (use PWA).

**Rationale**:
- Team already knows React (from existing vanilla JS app)
- Expo provides fast development and easy deployment
- Code sharing possible between web and mobile (logic, types)
- Next.js 14 provides SEO benefits critical for "AMC prep" search traffic

**Consequences**:
- ✅ Single language (TypeScript) across platforms
- ✅ Fast development velocity
- ✅ Large ecosystem and community
- ⚠️ Mobile apps won't feel 100% native (acceptable trade-off)
- ⚠️ Need to handle platform-specific features (push notifications, deep links)

**Alternatives Considered**:
- Flutter: Better performance but team would need to learn Dart
- Native (Swift/Kotlin): Best performance but requires 2x development effort
- Ionic/Cordova: WebView-based, poor performance for complex apps

---

## ADR 002: Backend Service Architecture

**Status**: ✅ Accepted

**Context**: 
Need to build backend for auth, MCQ serving, progress tracking, and subscriptions. Team size is small (1-3 developers initially).

**Decision**: 
Use **Modular Monolith** with FastAPI. Organize by domain (auth/, mcqs/, billing/) but deploy as single service.

**Rationale**:
- Small team can't effectively manage microservices complexity
- Network latency matters for MCQ practice (needs to feel instant)
- Debugging is easier in single codebase
- Can extract services later when needed (billing, AI tutor)

**Consequences**:
- ✅ Simple deployment and monitoring
- ✅ Shared database transactions where needed
- ✅ Easier testing and refactoring
- ⚠️ Must maintain clear module boundaries to enable future extraction
- ⚠️ Whole service redeploy on any change (mitigated by fast deploys)

**Alternatives Considered**:
- Microservices: Too complex for initial team size
- Serverless (Lambda): Cold start latency unacceptable for MCQ serving
- Next.js API routes: Tightly coupled to frontend deployment

---

## ADR 003: Database and Data Storage

**Status**: ✅ Accepted

**Context**: 
Need to store user data, progress, subscriptions, and serve MCQ content. Existing Qdrant handles vector search for AI tutor.

**Decision**: 
**PostgreSQL** as primary database, **Redis** for caching/sessions, keep existing **Qdrant** for vector search.

**Rationale**:
- PostgreSQL ACID compliance critical for billing/subscriptions
- JSONB columns allow flexible MCQ metadata
- Full-text search for content discovery
- Redis for fast session storage and rate limiting

**Consequences**:
- ✅ Proven, reliable technology
- ✅ Can scale vertically then horizontally (read replicas)
- ✅ Strong consistency for financial data
- ⚠️ Need to manage schema migrations (use Alembic)
- ⚠️ Multiple databases to monitor

**Alternatives Considered**:
- MongoDB: Flexible schema but weaker consistency guarantees
- DynamoDB: Good for scale but query patterns too limited
- Single database (PostgreSQL only): Redis needed for rate limiting anyway

---

## ADR 004: Authentication Strategy

**Status**: ✅ Accepted

**Context**: 
Need secure auth for medical students. Must support social login, password reset, and device management. HIPAA-level security not required but good to have.

**Decision**: 
Use **Clerk** for authentication (managed service).

**Rationale**:
- Fastest time to market
- Built-in social providers (Google, Apple)
- Pre-built UI components
- JWT standard (easy to migrate if needed)
- Device management included

**Consequences**:
- ✅ Ship auth in days not weeks
- ✅ Security handled by experts
- ✅ MFA support for Ultimate tier
- ⚠️ Vendor lock-in (mitigated by JWT standard)
- ⚠️ Monthly cost ($25/month for 10K users)

**Alternatives Considered**:
- Supabase Auth: Good free tier but fewer enterprise features
- Auth0: More expensive, overkill for needs
- Custom auth: Security risk, time sink

---

## ADR 005: Offline Support Strategy

**Status**: ✅ Accepted

**Context**: 
Medical students study on trains, buses, with poor hospital WiFi. Need offline access to MCQs but AI tutor requires internet.

**Decision**: 
Implement **offline-first for MCQ practice, online-only for AI tutor**.

**Mobile**: WatermelonDB (SQLite wrapper with sync)
**Web**: Service Worker with Cache API (500 questions cached)

**Rationale**:
- Core value (MCQs) works offline
- AI tutor inherently needs cloud processing
- Progressive enhancement approach

**Consequences**:
- ✅ Users can study anywhere
- ✅ Reduced server load (cached content)
- ⚠️ Complex sync logic needed
- ⚠️ Conflict resolution required
- ⚠️ Storage limits on devices

**Sync Strategy**:
- Last-write-wins for simple conflicts
- Audit log keeps all versions
- Real-time sync not required (polling every 30s sufficient)

**Alternatives Considered**:
- Full offline (including AI): Not technically feasible
- No offline: Poor user experience for target market
- Realm database: Good but less React Native community support

---

## ADR 006: API Design Pattern

**Status**: ✅ Accepted

**Context**: 
Need APIs for web and mobile clients. Different clients have different needs (web needs SEO, mobile needs bandwidth efficiency).

**Decision**: 
**Hybrid approach**:
- Web: GraphQL (flexible queries, reduce over-fetching)
- Mobile: REST (simpler, better caching, bandwidth efficient)
- Internal: gRPC (if/when we split services)

**Rationale**:
- Web app benefits from GraphQL's flexibility
- Mobile benefits from REST's simplicity and HTTP caching
- Can share underlying business logic

**Consequences**:
- ✅ Optimized for each client type
- ✅ Can evolve independently
- ⚠️ Two API implementations to maintain
- ⚠️ Need documentation for both

**Alternatives Considered**:
- GraphQL everywhere: Mobile caching harder
- REST everywhere: Web over-fetching issues
- tRPC: Great for full-stack TypeScript but not mobile-friendly

---

## ADR 007: Hosting and Infrastructure

**Status**: ✅ Accepted

**Context**: 
Need to deploy web app, backend API, databases, and AI services. Budget-conscious initially but needs to scale.

**Decision**: 
**Phase 1**: Vercel (web) + Railway (backend) + Supabase (database)
**Phase 2**: AWS (when >10K users)

**Rationale**:
- Managed services reduce operational burden
- Pay-as-you-scale pricing
- Easy to migrate to AWS when needed
- Vercel optimal for Next.js

**Consequences**:
- ✅ Fast deployment (git push)
- ✅ Auto-scaling included
- ✅ Monitoring built-in
- ⚠️ Vendor lock-in (but standard technologies)
- ⚠️ Higher cost per unit at scale (migrate to AWS later)

**Alternatives Considered**:
- AWS from start: More complex, slower development
- Google Cloud: Similar to AWS, no strong advantage
- Self-hosted: Too much operational overhead

---

## ADR 008: Real-Time Features

**Status**: ✅ Accepted

**Context**: 
Need to sync progress across devices and optionally support live collaboration features.

**Decision**: 
**Start with polling (30 second intervals), upgrade to WebSockets only if needed.**

**Rationale**:
- Polling is simpler to implement and debug
- Most features don't need true real-time
- Can add WebSockets later without breaking changes
- Reduces server complexity

**Consequences**:
- ✅ Simpler architecture
- ✅ Lower server resource usage
- ✅ Works through corporate firewalls
- ⚠️ 30-second delay for cross-device sync (acceptable)
- ⚠️ Not suitable for live collaboration (future feature)

**When to Upgrade**:
- >1000 concurrent users
- Launch live study groups feature
- User complaints about sync delay

**Alternatives Considered**:
- WebSockets from start: Overkill, harder to scale
- Server-Sent Events: Good middle ground but less supported
- Firebase Realtime DB: Vendor lock-in, cost concerns

---

## ADR 009: Content Protection

**Status**: ✅ Accepted

**Context**: 
18,000 MCQs are valuable IP. Need to prevent bulk scraping while maintaining good user experience.

**Decision**: 
**Multi-layer protection**:
1. Rate limiting (10 questions/minute free, 100/minute paid)
2. Dynamic option shuffling (prevents answer memorization by position)
3. Invisible watermarking (identify source if leaked)
4. Terms of Service with copyright notices
5. Bot detection (Cloudflare)

**Rationale**:
- No protection is perfect, but layers deter casual theft
- Must balance security with UX (can't be too restrictive)
- Legal protection as important as technical

**Consequences**:
- ✅ Makes bulk scraping harder
- ✅ Can identify leakers via watermarks
- ⚠️ Adds complexity to serving MCQs
- ⚠️ Slight performance impact (shuffling)

**Not Implemented (Intentionally)**:
- DRM (too restrictive, hurts legitimate users)
- Screenshot prevention (impossible to enforce)
- Client-side encryption (false sense of security)

---

## ADR 010: Payment and Subscription System

**Status**: ✅ Accepted

**Context**: 
Need to handle subscriptions (monthly/yearly), trials, upgrades/downgrades, and international payments.

**Decision**: 
Use **Stripe** with Stripe Billing for subscriptions.

**Rationale**:
- Industry standard, trusted by users
- Excellent subscription management (trials, proration)
- Strong webhook system for event handling
- Good international support (Australia, India, etc.)
- PCI compliance handled

**Consequences**:
- ✅ Comprehensive subscription features
- ✅ Excellent documentation and SDKs
- ✅ Handles tax (GST) in Australia
- ⚠️ 2.9% + 30¢ per transaction fee
- ⚠️ Need to handle webhook failures carefully

**Alternatives Considered**:
- PayPal: Poor subscription management
- Paddle: Good for SaaS but higher fees
- Chargebee: Additional layer on top of Stripe, adds complexity

---

## ADR 011: AI Tutor Implementation

**Status**: 🔄 Proposed

**Context**: 
AI Tutor feature allows students to ask questions and get cited answers. Need to decide between self-hosted vs API-based.

**Proposed Decision**: 
**Hybrid approach**:
- Use existing Qdrant (self-hosted) for RAG retrieval
- Use Claude API for answer generation (initially)
- Consider self-hosted LLM (llama3.1:70b) when scale justifies

**Rationale**:
- Claude provides best answers for medical content
- RAG already implemented (your existing Qdrant)
- Self-hosted LLM adds significant infrastructure complexity

**Cost Analysis**:
| Approach | Per 1000 Questions | Quality | Setup Complexity |
|----------|-------------------|---------|------------------|
| Claude API | $8-15 | ⭐⭐⭐⭐⭐ | Low |
| GPT-4 API | $10-30 | ⭐⭐⭐⭐ | Low |
| Self-hosted (70B) | $2-3 (GPU cost) | ⭐⭐⭐⭐ | High |
| Existing RAG only | $0 | ⭐⭐⭐ | Done |

**Decision Criteria**:
- Start with Claude API for quality
- Switch to self-hosted when:
  - >500 AI tutor queries/day
  - Have dedicated DevOps
  - Can manage GPU infrastructure

---

## ADR 012: Monitoring and Observability

**Status**: ✅ Accepted

**Context**: 
Need visibility into system health, user behavior, and errors. Critical for debugging and business decisions.

**Decision**: 
**Stack**: Sentry (errors) + PostHog (analytics) + Grafana (metrics)

**Rationale**:
- Sentry: Best-in-class error tracking, free tier generous
- PostHog: Product analytics, funnel analysis, feature flags
- Grafana: Infrastructure metrics, custom dashboards

**What to Track**:
| Category | Metrics | Tool |
|----------|---------|------|
| Errors | Exceptions, crashes | Sentry |
| Performance | API latency, DB queries | Sentry/Grafana |
| Business | Conversion, retention | PostHog |
| Infrastructure | CPU, memory, disk | Grafana |
| Security | Failed logins, rate limits | Grafana alerts |

**Consequences**:
- ✅ Comprehensive visibility
- ✅ Alerting on critical issues
- ⚠️ Multiple tools to learn
- ⚠️ Privacy considerations (PostHog data)

---

## ADR 013: Testing Strategy

**Status**: ✅ Accepted

**Context**: 
Need testing strategy that balances coverage with development speed for small team.

**Decision**: 
**Pragmatic testing pyramid**:
- Unit tests: Critical business logic (auth, billing)
- Integration tests: API endpoints
- E2E tests: Critical user flows (signup → subscribe → practice)
- No strict coverage requirements (focus on high-value tests)

**Rationale**:
- Small team can't maintain 100% coverage
- Medical content accuracy more important than code coverage
- Manual QA for content validation

**Tools**:
- Backend: pytest
- Frontend: Vitest + React Testing Library
- E2E: Playwright
- Mobile: Detox

---

## Proposed ADRs (To Be Decided)

### ADR 014: Internationalization (i18n)
**Question**: Do we need to support languages other than English?
**Context**: Many AMC candidates are from non-English speaking countries but exam is in English.
**Options**: English only vs Multi-language UI vs Full localization

### ADR 015: Third-Party Integrations
**Question**: Should we integrate with study tools (Anki, Notion)?
**Context**: Power users might want to export to their existing workflows.
**Options**: Build integrations vs API webhooks vs No integrations

### ADR 016: Community Features
**Question**: Should we add discussion forums, study groups?
**Context**: Community can improve retention but adds moderation burden.
**Options**: Built-in forums vs Discord integration vs No community

---

## How to Add New ADRs

1. Copy the template below
2. Fill in all sections
3. Number sequentially (ADR 017, 018, etc.)
4. Set status to "Proposed"
5. Discuss with team
6. Update status to "Accepted" or "Rejected"

### Template:

```markdown
## ADR XXX: [Title]

**Status**: ⏳ Proposed / ✅ Accepted / ❌ Rejected / 📦 Deprecated

**Context**: 
[Why we need to make this decision]

**Decision**: 
[What we decided]

**Rationale**:
[Why this decision]

**Consequences**:
- ✅ Positive
- ⚠️ Trade-off or risk

**Alternatives Considered**:
- Option A: Why rejected
- Option B: Why rejected
```

---

**Last Updated**: 2026-01-31  
**Next Review**: After Phase 1 completion
