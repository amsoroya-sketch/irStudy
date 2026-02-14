# IRSTUDY COMMERCIALIZATION MASTERPLAN
## Medical Education Platform - Modular Business Architecture

---

## EXECUTIVE SUMMARY

### What You Own (Assets)
| Asset | Quantity | Value | Protection Status |
|-------|----------|-------|-------------------|
| RAG-Validated MCQs | 18,000+ | Core IP | ⚠️ Needs copyright |
| OSCE Scenarios | 3,000+ | Core IP | ⚠️ Needs copyright |
| Vector Embeddings | 42,647 | Competitive Moat | ✅ Trade secret |
| RAG System | Production | Tech Advantage | ✅ Protected |
| Medical Textbooks | 10+ books | Content Source | ✅ Licensed/Purchased |

### Market Opportunity
```
┌────────────────────────────────────────────────────────────────┐
│  MARKET SIZING                                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  AMC Candidates (Australia)     4,000/year × $200 = $800K     │
│  Medical Students (Australia)  20,000/year × $150 = $3M       │
│  Nursing Students              150,000/year × $100 = $15M     │
│  IMG Global Market              50,000/year × $300 = $15M     │
│  Clinical Reference             120,000 × $120 = $14.4M       │
│                                                                │
│  ADDRESSABLE MARKET: $48.2M/year                              │
│  REALISTIC CAPTURE (2%): $964K/year                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## PART 1: MODULAR PRODUCT ARCHITECTURE

### Core Platform (Build Once)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CORE PLATFORM MODULES                             │
│                    (Shared Infrastructure)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   IDENTITY   │  │   PAYMENT    │  │  ANALYTICS   │              │
│  │   MODULE     │  │   MODULE     │  │   MODULE     │              │
│  │              │  │              │  │              │              │
│  │ • Auth/JWT   │  │ • Stripe     │  │ • Mixpanel   │              │
│  │ • RBAC       │  │ • Subscriptions│ • Metabase   │              │
│  │ • Profiles   │  │ • Invoicing  │  │ • Custom     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   CONTENT    │  │     RAG      │  │   LEARNING   │              │
│  │   MODULE     │  │   MODULE     │  │   MODULE     │              │
│  │              │  │              │  │              │              │
│  │ • MCQ DB     │  │ • Qdrant     │  │ • SRS        │              │
│  │ • OSCE DB    │  │ • Embeddings │  │ • Adaptive   │              │
│  │ • Media      │  │ • Claude API │  │ • Tracking   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Product Modules (Sell Separately)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRODUCT MODULES (Revenue Streams)                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  MODULE 1: AMC PREP          MODULE 2: MED SCHOOL                  │
│  ─────────────────           ───────────────────                   │
│  Price: $49/month            Price: $29/month                      │
│  Market: 4,000/year          Market: 20,000/year                   │
│                                                                     │
│  Features:                   Features:                             │
│  • 18K AMC MCQs              • Basic science MCQs                  │
│  • 3K OSCE scenarios         • Clinical skills OSCEs               │
│  • AMC blueprint tracking    • Year 1-4 content                    │
│  • Australian guidelines     • University partnerships             │
│                                                                     │
│  Development: 4 weeks        Development: 6 weeks                  │
│  (Content ready)             (Adapt existing OSCEs)                │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  MODULE 3: NURSING PREP      MODULE 4: IMG PATHWAYS                │
│  ─────────────────────       ────────────────────                  │
│  Price: $19/month            Price: $39/month                      │
│  Market: 150,000/year        Market: 50,000/year                   │
│                                                                     │
│  Features:                   Features:                             │
│  • Drug calculations         • PLAB/USMLE prep                     │
│  • Clinical procedures       • Migration guidance                  │
│  • ANMF competency           • Multi-exam support                  │
│                                                                     │
│  Development: 8 weeks        Development: 6 weeks                  │
│  (New content needed)        (Adapt AMC content)                   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  MODULE 5: CLINICAL SEARCH   MODULE 6: ENTERPRISE                  │
│  ────────────────────────    ───────────────────                   │
│  Price: $15/month            Price: $5K-20K/year                   │
│  Market: 120,000             Market: 100+ institutions             │
│                                                                     │
│  Features:                   Features:                             │
│  • Evidence search           • White-label option                  │
│  • Guidelines access         • LMS integration                     │
│  • CPD tracking              • Bulk licensing                      │
│                                                                     │
│  Development: 4 weeks        Development: 8 weeks                  │
│  (RAG already built)         (Admin dashboard)                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PART 2: REVENUE MODEL COMPARISON

### Model A: Subscription Only (SaaS)

| Tier | Price | Features | Target % | Revenue/User |
|------|-------|----------|----------|--------------|
| Free | $0 | 200 MCQs, basic | 90% | $0 |
| Pro | $49/mo | Full access | 8% | $588/year |
| Ultimate | $79/mo | +1-on-1, OSCE practice | 2% | $948/year |

**Projections (Year 1)**:
- 5,000 free users
- 150 Pro subscribers = $88,200
- 50 Ultimate subscribers = $47,400
- **Total: $135,600**

### Model B: Freemium + B2B

| Segment | Price | Units | Revenue |
|---------|-------|-------|---------|
| Pro (B2C) | $49/mo | 150 | $88,200 |
| Ultimate (B2C) | $79/mo | 50 | $47,400 |
| Institutional | $10K/yr | 5 | $50,000 |
| White-label | $25K/yr | 2 | $50,000 |

**Projections (Year 1): $235,600**

### Model C: Usage-Based (Pay-Per-Question)

| Package | Price | Questions | Target |
|---------|-------|-----------|--------|
| Starter | $19 | 500 | Casual users |
| Standard | $49 | Unlimited/3mo | Regular prep |
| Intensive | $99 | Unlimited/6mo | Full prep |

**Risk**: Cannibalizes subscription model
**Benefit**: Lower barrier to entry

### Recommended Hybrid Model

```
┌────────────────────────────────────────────────────────────────┐
│  HYBRID: Subscription + Institutional                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  B2C (80% of revenue)                                          │
│  ├── Free: Lead generation (5,000 users)                      │
│  ├── Pro: $49/mo ($588/yr) - Core product                     │
│  └── Ultimate: $79/mo ($948/yr) - High-value features         │
│                                                                │
│  B2B (20% of revenue)                                          │
│  ├── Universities: $5K-10K/yr (50-200 students)               │
│  └── Hospitals: $10K-20K/yr (white-label)                     │
│                                                                │
│  YEAR 1 TARGET: $200K-300K                                    │
│  YEAR 2 TARGET: $600K-800K                                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## PART 3: LEGAL RISK ASSESSMENT MATRIX

### Risk Heat Map

```
                    IMPACT
           Low      Medium      High
         ┌─────────┬─────────┬─────────┐
    High │    2    │    4    │    8    │
         │ Content │  Data   │ Piracy  │
         │ Quality │ Breach  │         │
         ├─────────┼─────────┼─────────┤
Medium   │    1    │    3    │    7    │
         │  GDPR   │ Compe-  │ Copy-   │
         │ (EU)    │ tition  │ right   │
         ├─────────┼─────────┼─────────┤
   Low   │    0    │    5    │    6    │
         │  None   │ Charge- │ False   │
         │         │ back    │ Claims  │
         └─────────┴─────────┴─────────┘
```

### Detailed Risk Analysis

| # | Risk | Likelihood | Impact | Mitigation | Cost |
|---|------|------------|--------|------------|------|
| 1 | **GDPR Violation** | Low | Medium | Block EU users initially | $0 |
| 2 | **Content Quality Issues** | High | Low | Medical review process | $5K |
| 3 | **Competitor Lawsuit** | Medium | Medium | Document originality | $10K |
| 4 | **Data Breach** | Medium | High | Security framework | $2K |
| 5 | **Chargeback Fraud** | Medium | Low | Stripe Radar | $0 |
| 6 | **False Advertising Claims** | Low | High | Legal disclaimers | $1K |
| 7 | **Copyright Infringement** | Medium | High | Content audit | $3K |
| 8 | **Content Piracy** | High | High | Watermarking, legal | $5K |

### Legal Budget Allocation

```
Pre-Launch Legal Costs:
├── Business registration & trademark: $2,000
├── Legal document drafting (ToS, Privacy): $3,000
├── IP audit & copyright registration: $2,000
├── Insurance (PI + Cyber): $4,000/year
└── Legal retainer (on-call): $2,000
    
TOTAL PRE-LAUNCH: $13,000

Ongoing (Annual):
├── Legal review & updates: $2,000
├── Compliance audit: $1,000
├── Insurance renewal: $4,000
└── Contingency: $3,000

TOTAL ANNUAL: $10,000
```

---

## PART 4: COMPLIANCE FRAMEWORK

### Australian Privacy Principles (APP) Checklist

| APP | Requirement | Implementation | Status |
|-----|-------------|----------------|--------|
| 1 | Privacy policy | Draft document | ☐ |
| 2 | Anonymity/pseudonymity | Allow anon browsing | ☐ |
| 3 | Collection of solicited info | Collection notice | ☐ |
| 5 | Notification | At point of collection | ☐ |
| 6 | Use/disclosure | Purpose limitation | ☐ |
| 11 | Security | Encryption, access controls | ✅ |
| 12 | Access | User data export | ☐ |
| 13 | Correction | Edit profile | ☐ |

### Medical Regulatory Compliance

```
REQUIRED DISCLAIMERS (All Pages):
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ EDUCATIONAL PURPOSE ONLY                                    │
│                                                                 │
│  This content is for exam preparation only and does not         │
│  constitute medical advice. Always consult qualified            │
│  healthcare professionals for clinical decisions.               │
│                                                                 │
│  This platform is not affiliated with or endorsed by the        │
│  Australian Medical Council (AMC) or AHPRA.                     │
│                                                                 │
│  Exam passage is not guaranteed. Individual results may vary.   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Breach Response Plan

```
HOUR 0-1: DETECTION & ASSESSMENT
□ Identify breach source
□ Determine data affected
□ Assess risk of harm
□ Contain breach

HOUR 1-24: NOTIFICATION PREPARATION
□ Document breach details
□ Prepare OAIC notification
□ Prepare user notification
□ Consult legal counsel

HOUR 24-72: NOTIFICATION
□ Notify OAIC (if required)
□ Notify affected individuals
□ Issue public statement (if needed)
□ Implement remediation

POST-BREACH:
□ Root cause analysis
□ Security improvements
□ Insurance claim
□ Regulatory follow-up
```

---

## PART 5: IMPLEMENTATION TIMELINE

### Phase 1: Foundation (Weeks 1-4)

```
WEEK 1: LEGAL & BUSINESS
├── Register business entity
├── Apply for trademark
├── Draft legal documents
├── Open business bank account
└── Set up Stripe business account

WEEK 2: SECURITY & COMPLIANCE
├── Apply security framework
├── Implement rate limiting
├── Set up monitoring/alerting
├── Create privacy policy
└── Create terms of service

WEEK 3: PAYMENT & SUBSCRIPTIONS
├── Integrate Stripe Checkout
├── Configure subscription tiers
├── Set up billing portal
├── Implement subscription gating
└── Test payment flows

WEEK 4: CONTENT PROTECTION
├── Implement watermarking
├── Add device tracking
├── Set up rate limiting
├── Create anti-scraping rules
└── Beta test with 10 users
```

### Phase 2: Launch (Weeks 5-8)

```
WEEK 5: BETA LAUNCH
├── Invite 50 beta users
├── Monitor for issues
├── Collect feedback
├── Fix critical bugs
└── Prepare marketing

WEEK 6: MARKETING PREP
├── Create landing page
├── Set up analytics
├── Create demo videos
├── Write launch copy
└── Prepare social media

WEEK 7: SOFT LAUNCH
├── Launch to email list
├── Post in AMC groups
├── Monitor conversion
├── Gather testimonials
└── Iterate on feedback

WEEK 8: PUBLIC LAUNCH
├── Press release
├── Influencer outreach
├── Paid ads (small test)
├── Content marketing
└── Target: 100 signups
```

### Phase 3: Growth (Months 3-6)

| Month | Goal | Actions | Target |
|-------|------|---------|--------|
| 3 | Product-Market Fit | Iterate based on feedback | 200 users, 10 paid |
| 4 | Acquisition | Marketing scale, SEO | 500 users, 30 paid |
| 5 | Retention | Feature improvements | 1,000 users, 60 paid |
| 6 | Revenue | Optimize pricing | 2,000 users, 100 paid |

### Phase 4: Expansion (Months 7-12)

```
MONTH 7-8: MEDICAL SCHOOL MODULE
├── Adapt OSCE content
├── Partner with universities
├── Create student pricing
└── Launch at $29/mo

MONTH 9-10: IMG PATHWAYS
├── Research PLAB/USMLE
├── Create migration content
├── International marketing
└── Launch at $39/mo

MONTH 11-12: ENTERPRISE
├── Build admin dashboard
├── LMS integration
├── Sales outreach
└── First institutional client
```

---

## PART 6: FINANCIAL PROJECTIONS

### Conservative Scenario

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Free Users | 2,000 | 4,000 | 6,000 |
| Pro Subscribers | 80 | 200 | 350 |
| Ultimate Subscribers | 20 | 60 | 120 |
| Institutional Clients | 2 | 5 | 10 |
| MRR | $5,520 | $15,400 | $30,680 |
| Annual Revenue | $66,240 | $184,800 | $368,160 |
| Costs | $40,000 | $80,000 | $150,000 |
| **Net Profit** | **$26,240** | **$104,800** | **$218,160** |

### Optimistic Scenario

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Free Users | 5,000 | 12,000 | 20,000 |
| Pro Subscribers | 200 | 600 | 1,200 |
| Ultimate Subscribers | 50 | 200 | 500 |
| Institutional Clients | 5 | 15 | 30 |
| MRR | $15,750 | $54,600 | $117,000 |
| Annual Revenue | $189,000 | $655,200 | $1,404,000 |
| Costs | $60,000 | $150,000 | $300,000 |
| **Net Profit** | **$129,000** | **$505,200** | **$1,104,000** |

### Break-Even Analysis

```
Fixed Costs (Monthly):
├── Infrastructure: $500
├── AI API: $300
├── Legal/Insurance: $800
├── Marketing: $1,000
└── Tools/Software: $400
    
TOTAL FIXED: $3,000/month

Break-Even:
At $49/mo average: 62 subscribers
At $60/mo average: 50 subscribers

Timeline to Break-Even: Month 4-6 (Conservative)
```

---

## PART 7: COMPETITIVE POSITIONING

### Unique Value Proposition

```
┌─────────────────────────────────────────────────────────────────┐
│  THE ONLY PLATFORM WITH:                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✓ 18,000+ RAG-verified questions (3x competitors)             │
│  ✓ Evidence citations on every answer (unique)                 │
│  ✓ Australian guidelines native (eTG, AMH)                     │
│  ✓ 3,000+ OSCE scenarios (6x competitors)                      │
│  ✓ AI-powered personalized study plans                         │
│  ✓ Offline mode for commute study                              │
│                                                                 │
│  POSITIONING: Premium quality at mid-tier pricing              │
│  TAGLINE: "The evidence-based path to AMC success"             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pricing Strategy

| Competitor | Price | Your Advantage |
|------------|-------|----------------|
| AceAMCQ | $140/6mo | You: 3x questions + AI |
| AMBOSS | $200-400 | You: Australian-specific |
| PassAMCQ | Unknown | You: Transparent pricing |
| MplusX | ~$200 | You: RAG validation |

**Your Pricing**: $49/mo ($588/year) = Competitive with premium positioning

---

## PART 8: DECISION MATRIX

### Which Module to Launch First?

| Criteria | AMC Prep | Med School | Nursing | IMG | Weight |
|----------|----------|------------|---------|-----|--------|
| Content Ready | 10 | 6 | 3 | 5 | 20% |
| Market Size | 5 | 8 | 10 | 7 | 15% |
| Competition | 7 | 4 | 3 | 6 | 15% |
| Your Advantage | 10 | 6 | 4 | 8 | 20% |
| Development Time | 10 | 7 | 4 | 6 | 15% |
| Revenue Potential | 6 | 8 | 7 | 7 | 15% |
| **WEIGHTED SCORE** | **8.1** | **6.6** | **5.3** | **6.4** | |

**DECISION**: Launch AMC Prep first (highest score), expand sequentially.

---

## APPENDICES

### A. Required Legal Documents

1. Terms of Service
2. Privacy Policy
3. Cookie Policy
4. Refund Policy
5. Acceptable Use Policy
6. Data Processing Agreement
7. Medical Disclaimer
8. Copyright Notice

### B. Insurance Checklist

- [ ] Professional Indemnity ($2M)
- [ ] Cyber Liability ($1M)
- [ ] Public Liability ($10M)
- [ ] Business Interruption

### C. Technical Checklist

- [ ] Security framework applied
- [ ] Rate limiting implemented
- [ ] Content watermarking
- [ ] Stripe integration
- [ ] Subscription gating
- [ ] Analytics tracking
- [ ] GDPR blocking (if needed)
- [ ] Accessibility audit

### D. Marketing Checklist

- [ ] Landing page
- [ ] Pricing page
- [ ] Demo video
- [ ] Testimonials
- [ ] FAQ page
- [ ] Blog/Content strategy
- [ ] Social media setup
- [ ] Email sequences

---

**Document Version**: 2.0  
**Last Updated**: 2026-02-04  
**Status**: Ready for Implementation

*Next Steps: Review with legal counsel, prioritize Phase 1 tasks, begin implementation.*
