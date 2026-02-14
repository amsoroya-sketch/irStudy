# Architecture Quick Decision Guide

## Decision Tree: Choose Your Path

### Q1: What's your team size?

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   How many developers on the project?                          │
│                                                                 │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│   │    1     │  │   2-3    │  │   4-6    │  │    7+    │      │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│        │             │             │             │             │
│        ▼             ▼             ▼             ▼             │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │
│   │Monolith │   │Modular  │   │Modular  │   │Micro-   │       │
│   │+ Next.js│   │Monolith │   │Monolith │   │services │       │
│   │         │   │         │   │+ some   │   │         │       │
│   │Supabase │   │FastAPI  │   │split    │   │Full     │       │
│   │+ Vercel │   │+ Railway│   │services │   │orchestra│       │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: All Decisions

### Client Architecture

| Decision | Option A | Option B | Option C | Recommendation |
|----------|----------|----------|----------|----------------|
| **Web Framework** | Next.js 14 | React + Vite | Vue/Nuxt | **Next.js 14** - SEO critical for "AMC prep" searches |
| **Mobile** | React Native | Flutter | Native (Swift/Kotlin) | **React Native (Expo)** - Team likely knows React |
| **Desktop** | Tauri | Electron | Skip | **Skip for MVP** - Web PWA sufficient |
| **State Management** | Zustand | Redux | React Context | **Zustand** - Simple, fast, TypeScript |

### Backend Architecture

| Decision | Option A | Option B | Option C | Recommendation |
|----------|----------|----------|----------|----------------|
| **API Pattern** | REST | GraphQL | gRPC | **Hybrid** - GraphQL (web), REST (mobile) |
| **Service Style** | Monolith | Modular Monolith | Microservices | **Modular Monolith** - Best balance for small team |
| **Language** | Python/FastAPI | Node/Express | Go | **Python/FastAPI** - Your existing stack |
| **Auth Provider** | Clerk | Auth0 | Custom | **Clerk** - Fastest to market |
| **Payments** | Stripe | PayPal | Paddle | **Stripe** - Best subscription support |

### Data Architecture

| Decision | Option A | Option B | Option C | Recommendation |
|----------|----------|----------|----------|----------------|
| **Primary DB** | PostgreSQL | MySQL | MongoDB | **PostgreSQL** - ACID, JSONB, mature |
| **Cache** | Redis | Memcached | In-memory | **Redis** - Sessions, rate limits, pub/sub |
| **Vector DB** | Qdrant (existing) | Pinecone | Weaviate | **Keep Qdrant** - Already works |
| **Offline Storage** | SQLite (mobile) | WatermelonDB | Realm | **WatermelonDB** - Built for sync |

### Infrastructure

| Decision | Option A | Option B | Option C | Recommendation |
|----------|----------|----------|----------|----------------|
| **Hosting** | Vercel + Railway | AWS | GCP | **Vercel + Railway** - Fast, cost-effective |
| **Database Host** | Supabase | AWS RDS | Self-hosted | **Supabase** - Free tier, great DX |
| **CDN** | Cloudflare | AWS CloudFront | Vercel Edge | **Cloudflare** - Generous free tier |
| **Monitoring** | Sentry + LogRocket | Datadog | Custom | **Sentry** - Free tier sufficient |

### Sync Strategy

| Decision | Option A | Option B | Option C | Recommendation |
|----------|----------|----------|----------|----------------|
| **Sync Pattern** | Event Sourcing | CRUD + Timestamps | CQRS Full | **CRUD + Timestamps** - Start simple |
| **Real-time** | WebSockets | Server-Sent Events | Polling | **Polling (30s)** - Good enough for start |
| **Conflict Resolution** | Last-write-wins | Merge | Manual | **Last-write-wins** + audit log |

---

## Recommended Architecture (Start Here)

### For Solo Developer or 2-Person Team

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECOMMENDED: SOLO/2-PERSON STACK              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FRONTEND (Web)                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Next.js 14 (App Router)                                  │  │
│  │  • Deployed to Vercel ($0-20/mo)                          │  │
│  │  • Server Components for auth/protected routes            │  │
│  │  • Client Components for MCQ interactivity                │  │
│  │  • API Routes for backend logic                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  BACKEND (Minimal)                                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Next.js API Routes (initially)                           │  │
│  │  OR                                                       │  │
│  │  FastAPI on Railway ($5/mo)                               │  │
│  │                                                           │  │
│  │  Why: Keep it simple. Don't split until you need to.      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  DATABASE                                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Supabase PostgreSQL (Free tier: 500MB, 2GB bandwidth)    │  │
│  │  • Auth (can replace Clerk initially)                     │  │
│  │  • Database                                               │  │
│  │  • Real-time subscriptions (optional)                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ADDITIONAL SERVICES                                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Clerk (Auth) - $25/mo when ready                       │  │
│  │  • Stripe (Payments) - Pay per transaction                │  │
│  │  • Upstash (Redis) - $10/mo for caching                   │  │
│  │  • Qdrant (existing) - Self-host or managed               │  │
│  │  • Cloudflare (CDN) - Free tier                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  TOTAL COST: ~$35-60/month                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### For 3-4 Person Team

```
┌─────────────────────────────────────────────────────────────────┐
│                 RECOMMENDED: SMALL TEAM STACK                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FRONTEND TEAM                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Web: Next.js 14 on Vercel                                │  │
│  │  Mobile: React Native (Expo)                              │  │
│  │                                                           │  │
│  │  Shared: TypeScript configs, component library            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  BACKEND TEAM                                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  FastAPI application                                      │  │
│  │  • Modular structure (auth, mcqs, billing separate)       │  │
│  │  • Deployed to Railway or AWS ECS                         │  │
│  │  • Docker containers                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  INFRASTRUCTURE                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • PostgreSQL: AWS RDS or Supabase Scale                  │  │
│  │  • Redis: AWS ElastiCache or Upstash                      │  │
│  │  • Qdrant: Self-hosted on EC2 or managed                  │  │
│  │  • Storage: AWS S3 or Cloudflare R2                       │  │
│  │  • CDN: Cloudflare Pro                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  DEVOPS                                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • GitHub Actions for CI/CD                               │  │
│  │  • Docker Compose for local dev                           │  │
│  │  • Terraform for infrastructure (optional)                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  TOTAL COST: ~$150-300/month                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Decision Checklist

Mark your choices:

### Phase 1 Decisions (MVP)

- [ ] **Web Framework**: ☐ Next.js 14 ☐ React SPA ☐ Other: ___
- [ ] **Mobile**: ☐ React Native ☐ Flutter ☐ Skip mobile for now
- [ ] **Backend**: ☐ Next.js API routes ☐ FastAPI separate ☐ Other: ___
- [ ] **Database**: ☐ Supabase ☐ Railway PostgreSQL ☐ AWS RDS
- [ ] **Auth**: ☐ Supabase Auth ☐ Clerk ☐ Auth0
- [ ] **Hosting**: ☐ Vercel ☐ Railway ☐ AWS

### Phase 2 Decisions (Post-MVP)

- [ ] **Mobile Strategy**: ☐ Expo ☐ Ejected RN ☐ Flutter rewrite
- [ ] **API Style**: ☐ GraphQL ☐ REST ☐ Hybrid
- [ ] **Caching**: ☐ Redis ☐ In-memory ☐ CDN only
- [ ] **Offline**: ☐ WatermelonDB ☐ SQLite ☐ Basic cache

### Phase 3 Decisions (Scale)

- [ ] **Service Split**: ☐ Keep monolith ☐ Extract AI service ☐ Full microservices
- [ ] **Database**: ☐ Single instance ☐ Read replicas ☐ Sharding
- [ ] **Regions**: ☐ Single region ☐ Multi-region

---

## Risk Assessment

| Decision | Risk Level | Mitigation |
|----------|-----------|------------|
| **Supabase Auth** | Medium | Can migrate to Clerk later (same JWT standard) |
| **Next.js API routes** | Low | Easy to extract to FastAPI later |
| **React Native** | Low | Can add Flutter later or go native |
| **No offline support** | Medium | Add in v2, not blocking for MVP |
| **Single region** | Low | Add regions when you have users there |

---

## Common Mistakes to Avoid

### ❌ Don't Do This
1. **Microservices from day 1** - You'll spend more time on infrastructure than product
2. **Build your own auth** - Use Clerk/Supabase, focus on MCQs
3. **Perfect offline support** - Get online version working first
4. **Multi-region from start** - Start in Australia, expand later
5. **GraphQL everything** - REST is fine for simple CRUD

### ✅ Do This Instead
1. **Start monolith, split later** - When you have scaling pain
2. **Use managed services** - Clerk, Stripe, Supabase - focus on core value
3. **Ship fast, iterate** - Get paying customers, then perfect
4. **Measure before optimizing** - You might not need caching yet
5. **Document your decisions** - ADRs (Architecture Decision Records)

---

## Next Actions

### This Week
1. [ ] Choose your stack from recommendations above
2. [ ] Set up development environment
3. [ ] Create "Hello World" deployment
4. [ ] Verify team can work with chosen technologies

### Next 2 Weeks
1. [ ] Build auth system (login/register)
2. [ ] Connect to your existing MCQ data
3. [ ] Display first question in browser
4. [ ] Deploy to staging environment

### Month 1
1. [ ] Complete web app MVP
2. [ ] Add subscription gating
3. [ ] Launch beta to 10 users
4. [ ] Gather feedback

---

**Remember:** The best architecture is the one your team can build and maintain. Perfect architecture that never ships is worse than good architecture that helps students pass their exams.
