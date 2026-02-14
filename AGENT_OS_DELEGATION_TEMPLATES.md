# Agent OS Delegation Templates
## Constraint-Aware Expert Agent Delegation Framework

**Version:** 1.0
**Date:** 2026-02-06
**Purpose:** Prevent systematic mistakes by front-loading context and explicit constraints
**Based on:** ~/.claude/CLAUDE.md (Global Agent OS rules) + PROJECT_CONSTRAINTS.md

---

## 📋 TABLE OF CONTENTS

1. [Overview: Why These Templates Matter](#overview)
2. [Template Structure](#template-structure)
3. [Phase 0 Templates](#phase-0-templates)
4. [Phase 1 Templates (Mobile PWA)](#phase-1-templates)
5. [Phase 2 Templates (EMR Practice)](#phase-2-templates)
6. [Phase 3 Templates (AI Simulation)](#phase-3-templates)
7. [Validation Checklists](#validation-checklists)

---

## 1. OVERVIEW: WHY THESE TEMPLATES MATTER

### The Problem We're Solving

**Past Mistake (from your constraints):**
- Launched 5 agents in parallel to create Flutter providers
- None read PROJECT_CONSTRAINTS.md first
- Result: 124 hardcoded credentials across all files
- Cost: 3-6 hours to fix after the fact

**Root Cause:**
- Generic prompts without project context
- No upfront constraints provided
- No self-validation requirement
- Fire-and-forget delegation

### The Solution: Constraint-Aware Delegation

```
┌─────────────────────────────────────────────────────────────────┐
│              BEFORE (Generic Delegation)                         │
├─────────────────────────────────────────────────────────────────┤
│  PM: "Create a SOAP note editor component"                      │
│  Agent: [Creates code with hardcoded credentials]               │
│  PM: [Discovers 124 violations after all agents finish]         │
│  Time wasted: 6 hours fixing                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              AFTER (Constraint-Aware Delegation)                 │
├─────────────────────────────────────────────────────────────────┤
│  PM: "Create SOAP note editor component                         │
│                                                                  │
│       CONSTRAINTS (READ FIRST):                                 │
│       1. Read: PROJECT_CONSTRAINTS.md                           │
│       2. Security: NEVER hardcode database credentials          │
│       3. Example: Use ref.read(databaseConfigProvider)          │
│       4. Validation: Run flutter analyze before returning       │
│       5. Self-check: [ ] No hardcoded credentials               │
│                                                                  │
│       SEARCH EXISTING PATTERNS:                                 │
│       - lib/features/goals/providers/goals_provider.dart"       │
│                                                                  │
│  Agent: [Reads constraints, searches patterns, creates code]    │
│  Agent: [Self-validates: flutter analyze = 0 errors]            │
│  PM: [Validates once, proceeds to next agent]                   │
│  Time saved: 5 hours                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. TEMPLATE STRUCTURE

### Standard Delegation Template

Every agent delegation MUST include these sections:

```markdown
# Task: [Clear, specific task description]

## CONSTRAINTS (READ THESE FIRST)

### 1. Read Project Constraints
- [ ] Read: PROJECT_CONSTRAINTS.md (if exists)
- [ ] Read: constraints/[relevant-module].md
- [ ] Understand: Zero-tolerance policies for this project

### 2. Security Constraints
- ❌ NEVER: [Specific anti-patterns]
- ✅ ALWAYS: [Required patterns]
- 📖 Example: [Code snippet showing correct pattern]

### 3. Performance Constraints
- Target: [Specific metric, e.g., <100ms response time]
- Requirement: [Algorithmic complexity, e.g., O(1) lookups]

### 4. Quality Constraints
- Testing: [Coverage %, pass rate %]
- Accessibility: [WCAG level]
- Style: [Framework, linting rules]

## SEARCH EXISTING PATTERNS (BEFORE CODING)

**Look for similar implementations:**
- [ ] Read: [file path 1] (example of correct pattern)
- [ ] Read: [file path 2] (reusable component)
- [ ] Search: [keyword to find related code]

## VALIDATION CHECKLIST (BEFORE RETURNING)

**You MUST complete these checks:**
- [ ] Compilation: [command] shows 0 errors
- [ ] Security: No hardcoded credentials (grep check)
- [ ] Tests: All tests pass (100% requirement)
- [ ] Style: Linting passes
- [ ] Performance: Meets target metrics

## TASK DETAILS

[Detailed task description]

## EXPECTED OUTPUT

[Format, file structure, what to return]

## SUCCESS CRITERIA

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

---

## 3. PHASE 0 TEMPLATES

### Template 3.1: Security Infrastructure Setup

```markdown
# Task: Set up Clerk authentication + Stripe payments

## AGENT: project-manager-coordinator
## DELEGATING TO: security-compliance-expert

## CONSTRAINTS (READ THESE FIRST)

### 1. Read Project Constraints
- [ ] Read: PROJECT_CONSTRAINTS.md (security section)
- [ ] Read: constraints/03-security-configuration.md
- [ ] Read: cyberSecurity/README.md (existing framework)

### 2. Security Constraints (CRITICAL)

❌ **NEVER DO THIS:**
```python
# WRONG - Hardcoded credentials
CLERK_SECRET_KEY = "sk_test_abc123"
DATABASE_URL = "postgres://user:password@localhost/db"
```

✅ **ALWAYS DO THIS:**
```python
# CORRECT - Environment variables
import os
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Verify secrets are not None
if not CLERK_SECRET_KEY:
    raise ValueError("CLERK_SECRET_KEY not set in environment")
```

❌ **NEVER commit:**
- `.env` files with real credentials
- API keys in code
- Database passwords
- JWT secrets

✅ **ALWAYS use:**
- `.env.example` with placeholder values
- Environment variables (os.getenv)
- AWS Secrets Manager / HashiCorp Vault for production
- Pre-commit hooks (git-secrets) to prevent leaks

### 3. Implementation Constraints

**Authentication (Clerk):**
- Provider: Clerk (HIPAA-compliant tier if storing PHI)
- MFA: Required for Ultimate tier users
- Session: JWT with 15-min expiry, refresh tokens in HTTP-only cookies
- Password policy: 8+ chars, uppercase, lowercase, number

**Payments (Stripe):**
- Products: Free, Pro ($49/mo), Ultimate ($79/mo)
- Currency: AUD (Australian dollars)
- Webhook: Must verify signature before processing
- Fraud: Enable Stripe Radar rules

**Database Security:**
- Row-Level Security (RLS): Enabled on all user-facing tables
- Encryption: AES-256 at rest (AWS RDS)
- Backups: Daily automated, 30-day retention
- Access: No public internet access, private subnet only

### 4. Testing Constraints
- [ ] Test Clerk signup flow works
- [ ] Test Stripe checkout (test mode: card 4242 4242 4242 4242)
- [ ] Test webhook delivers event to backend
- [ ] Test RLS: User A cannot query User B's data
- [ ] Test backup restore: Restore from yesterday's backup

## SEARCH EXISTING PATTERNS

**Look for similar authentication implementations:**
- [ ] Search: `grep -r "Authentication" backend/src/`
- [ ] Check: `backend/src/auth/` directory (if exists)
- [ ] Review: Any existing FastAPI dependency injection patterns

**Check existing security tooling:**
- [ ] Read: `cyberSecurity/` folder contents
- [ ] Check: `.git/hooks/pre-commit` (if exists)
- [ ] Review: GitHub Actions workflows in `.github/workflows/`

## VALIDATION CHECKLIST (BEFORE RETURNING)

**Security Checks:**
- [ ] Run: `git secrets --scan` (no secrets detected)
- [ ] Run: `detect-secrets scan` (no new secrets vs baseline)
- [ ] Verify: `.env` is in `.gitignore`
- [ ] Verify: `.env.example` has only placeholders
- [ ] Check: No passwords in git history (`git log --all --full-history --source -- **/.env`)

**Functional Checks:**
- [ ] Clerk signup: New user created successfully
- [ ] Clerk login: Session token returned
- [ ] Stripe checkout: Payment intent created
- [ ] Stripe webhook: Event processed correctly
- [ ] Database RLS: SELECT query with wrong user_id returns empty

**Documentation:**
- [ ] Created: Setup instructions in README.md
- [ ] Created: Environment variable template (.env.example)
- [ ] Updated: cyberSecurity/README.md with new security measures

## TASK DETAILS

**Objective:** Implement secure authentication and payment processing infrastructure.

**Components to Build:**

1. **Clerk Authentication (Backend)**
   - File: `backend/src/auth/clerk_client.py`
   - Functions:
     - `verify_session(token: str) -> Session`
     - `get_user(user_id: str) -> User`
   - File: `backend/src/auth/dependencies.py`
   - Functions:
     - `require_auth() -> User` (FastAPI dependency)
     - `require_pro() -> User` (checks subscription tier)

2. **Clerk Authentication (Frontend)**
   - File: `frontend/src/main.tsx`
   - Wrap app with `<ClerkProvider>`
   - File: `frontend/src/components/auth/ProtectedRoute.tsx`
   - Implement: Route protection using `<SignedIn>` / `<SignedOut>`

3. **Stripe Payments (Backend)**
   - File: `backend/src/payments/stripe_client.py`
   - Functions:
     - `create_checkout_session(user_id, price_id) -> Session`
     - `handle_webhook(payload, signature) -> dict`
   - File: `backend/src/api/v1/payments.py`
   - Endpoints:
     - `POST /api/v1/payments/create-checkout`
     - `POST /api/v1/payments/webhook`

4. **Database Security**
   - File: `backend/alembic/versions/20260206_enable_rls.sql`
   - Enable RLS on: users, mcq_progress, osce_sessions, soap_notes
   - Create policies: user_isolation_policy (only see own data)
   - File: `backend/src/db/session.py`
   - Implement: RLS context setting on connection

5. **Pre-commit Hooks**
   - Install git-secrets: `brew install git-secrets`
   - Configure patterns: API keys, database URLs, passwords
   - File: `.git/hooks/pre-commit` (auto-generated)
   - Test: Attempt to commit a fake secret (should fail)

6. **Environment Configuration**
   - File: `.env.example` (safe to commit)
   - File: `.env.local` (gitignored, real secrets)
   - File: `backend/.env.example`
   - File: `frontend/.env.example`

## EXPECTED OUTPUT

**Files to Create:**
```
backend/
├── src/
│   ├── auth/
│   │   ├── clerk_client.py (new)
│   │   └── dependencies.py (new)
│   ├── payments/
│   │   └── stripe_client.py (new)
│   └── api/v1/
│       └── payments.py (new)
├── alembic/versions/
│   └── 20260206_enable_rls.sql (new)
└── .env.example (new)

frontend/
├── src/
│   ├── main.tsx (modified)
│   └── components/auth/
│       └── ProtectedRoute.tsx (new)
└── .env.example (new)

.gitignore (modified - add .env, .env.local)
.secrets.baseline (new - detect-secrets)
README.md (modified - add setup instructions)
```

**Return Format:**
```markdown
# Security Infrastructure Setup - Complete

## ✅ Completed Tasks

1. **Clerk Authentication**
   - Backend SDK integrated
   - Frontend provider configured
   - Test signup/login: PASS ✓

2. **Stripe Payments**
   - Products created (Free, Pro, Ultimate)
   - Webhook configured
   - Test checkout: PASS ✓

3. **Database Security**
   - RLS enabled on 4 tables
   - Policies tested: PASS ✓
   - Encryption at rest: ENABLED ✓

4. **Secret Scanning**
   - git-secrets installed
   - Pre-commit hook active
   - Test blocked fake secret: PASS ✓

## 📊 Validation Results

- Security scans: 0 secrets detected ✓
- Functional tests: 5/5 passed ✓
- Documentation: Updated ✓

## 📝 Setup Instructions

[Include instructions for next developer]

## 🚨 Important Notes

- Clerk uses HIPAA-compliant tier (if PHI stored)
- Stripe webhook secret must be configured in production
- Database RLS verified: users cannot see each other's data
```

## SUCCESS CRITERIA

- [ ] Clerk signup/login works end-to-end
- [ ] Stripe checkout redirects to payment page
- [ ] Webhook processes subscription.created event
- [ ] Database RLS prevents cross-user data access
- [ ] git-secrets blocks commits with fake API keys
- [ ] 0 secrets found in codebase (detect-secrets scan)
- [ ] All credentials in .env (not hardcoded)
- [ ] Documentation complete (setup instructions)

## ESTIMATED TIME

- **Research:** 1 hour (read Clerk/Stripe docs)
- **Implementation:** 4 hours
- **Testing:** 2 hours
- **Documentation:** 1 hour
- **TOTAL:** 8 hours (1 day)
```

---

### Template 3.2: Content Validation Script

```markdown
# Task: Create RAG Citation Validation Script

## AGENT: project-manager-coordinator
## DELEGATING TO: testing-qa-expert + clinical-accuracy-validator

## CONSTRAINTS (READ THESE FIRST)

### 1. Read Project Constraints
- [ ] Read: PROJECT_CONSTRAINTS.md (medical accuracy + citation requirements)
- [ ] Read: constraints/11-rag-citation-requirements.md
- [ ] Read: constraints/12-content-generation-requirements.md

### 2. Medical Accuracy Constraints (CRITICAL)

**Requirement:** 100% of MCQs must have 3 citations with >80% RAG confidence

❌ **NOT ACCEPTABLE:**
- Generic citations ("Medical textbook, chapter 5")
- Missing page numbers
- No RAG verification
- Confidence score <80%

✅ **REQUIRED FORMAT:**
```json
{
  "citations": [
    {
      "source_name": "eTG Complete",
      "edition": "March 2024",
      "chapter_section": "Cardiovascular → Atrial Fibrillation",
      "page_number": 147,
      "rag_verified": true,
      "confidence_score": 0.92,
      "chunk_id": "etg-2024-cardio-147-chunk-3",
      "verified_excerpt": "CHA₂DS₂-VASc score guides anticoagulation..."
    }
  ]
}
```

### 3. Australian Compliance Constraints

**All content MUST use:**
- Australian spelling (paediatric, anaemia, oedema)
- SI units (mmol/L not mg/dL, °C not °F)
- PBS medication names (generic not brand)
- Australian guidelines (eTG, AMH, RACGP not UpToDate, NICE)
- MBS item numbers (not CPT codes)

### 4. Performance Constraints

**Target:** Validate 18,000 MCQs in <8 hours
- Concurrency: Process 50 MCQs in parallel
- Rate limiting: Max 100 Anthropic API requests/min
- Caching: Cache Qdrant embeddings to avoid redundant queries
- Progress: Use tqdm progress bar

### 5. Quality Constraints

**Output Requirements:**
- Validation report (JSON format)
- Flagged items exported (for manual review)
- Statistics by specialty
- Confidence distribution histogram
- Estimated time to complete remediation

## SEARCH EXISTING PATTERNS

**RAG implementation:**
- [ ] Read: `backend/src/services/rag_query_service.py`
- [ ] Read: `scripts/generate_embeddings.py`
- [ ] Check: Qdrant client configuration

**Existing validation scripts:**
- [ ] Search: `grep -r "validate" scripts/`
- [ ] Check: `scripts/validate_australian_compliance.py` (if exists)
- [ ] Review: How MCQs are currently loaded from database

**Anthropic API usage:**
- [ ] Read: `backend/src/models/ollama_client.py` (for API patterns)
- [ ] Check: Rate limiting implementation (if exists)

## VALIDATION CHECKLIST (BEFORE RETURNING)

**Code Quality:**
- [ ] Run: `python -m pytest scripts/test_validate_rag_citations.py` (100% pass)
- [ ] Run: `pylint scripts/validate_rag_citations.py` (score >8.0)
- [ ] Run: `mypy scripts/validate_rag_citations.py` (0 type errors)
- [ ] Check: No hardcoded API keys (uses os.getenv)

**Functional Tests:**
- [ ] Test: Validate 10 sample MCQs (verify JSON output)
- [ ] Test: Handle missing citations gracefully
- [ ] Test: Rate limiting works (doesn't exceed 100 req/min)
- [ ] Test: Progress bar updates correctly
- [ ] Test: Report generation works

**Performance:**
- [ ] Benchmark: 10 MCQs processed in <30 seconds
- [ ] Estimate: 18,000 MCQs × 3 sec/mcq = 15 hours (unacceptable)
- [ ] Optimize: Use async + parallel processing → Target 6-8 hours

**Documentation:**
- [ ] Docstrings: All functions documented
- [ ] Usage: CLI help text explains parameters
- [ ] Examples: README shows how to run script

## TASK DETAILS

**Objective:** Create a script that validates all MCQ citations against the Qdrant RAG database.

**Script: `scripts/validate_rag_citations.py`**

**Components:**

1. **MCQ Loader**
   - Load all MCQs from database or JSON files
   - Support filtering by specialty (for testing)
   - Handle large datasets (18,000+ MCQs)

2. **Fact Extractor**
   - Use Claude 3.5 Sonnet to extract medical facts from explanation
   - Target: 3 facts per MCQ (match 3 citations)
   - Handle edge cases (very short explanations)

3. **RAG Validator**
   - Query Qdrant for each fact
   - Calculate similarity score (confidence)
   - Extract source metadata (book name, page number)
   - Flag if confidence <80%

4. **Report Generator**
   - JSON report with detailed results
   - Statistics: total MCQs, verified facts, flagged items
   - Breakdown by specialty
   - Confidence distribution (histogram data)

5. **Flagged Items Exporter**
   - Export low-confidence items to separate JSON
   - Include recommendations (e.g., "regenerate with Claude")
   - Prioritize by severity (0-50% = critical, 50-80% = needs review)

**CLI Interface:**

```bash
# Validate all MCQs
python scripts/validate_rag_citations.py \
  --input data/mcqs/ \
  --output citation_validation_report.json \
  --flagged flagged_mcqs_for_review.json \
  --parallel 50 \
  --confidence-threshold 0.80

# Validate single specialty (testing)
python scripts/validate_rag_citations.py \
  --input data/mcqs/cardiology/ \
  --specialty cardiology \
  --output cardiology_validation.json

# Resume from checkpoint (if interrupted)
python scripts/validate_rag_citations.py \
  --resume checkpoint.json
```

**Algorithm:**

```python
async def validate_mcq(mcq: dict) -> dict:
    """
    Validate a single MCQ's citations.

    Steps:
    1. Extract facts from explanation (Claude API)
    2. For each fact:
       a. Generate embedding (sentence-transformers)
       b. Query Qdrant (similarity search)
       c. Calculate confidence score
       d. Extract source metadata
    3. Aggregate results
    4. Flag if avg confidence <80%

    Returns:
    {
      "mcq_id": "cardio_af_001",
      "facts_extracted": 3,
      "facts_verified": 3,
      "avg_confidence": 0.86,
      "flagged": false,
      "validations": [
        {
          "fact": "CHA₂DS₂-VASc guides anticoagulation",
          "verified": true,
          "confidence": 0.92,
          "source": "eTG Complete",
          "page": 147
        },
        ...
      ]
    }
    """
```

## EXPECTED OUTPUT

**File Structure:**
```
scripts/
├── validate_rag_citations.py (new)
├── test_validate_rag_citations.py (new)
└── requirements_validation.txt (new)

outputs/ (generated by script)
├── citation_validation_report.json
├── flagged_mcqs_for_review.json
└── validation_checkpoint.json (for resume)
```

**Report Format:**
```json
{
  "metadata": {
    "date": "2026-02-06T10:30:00Z",
    "mcqs_validated": 18000,
    "duration_seconds": 28800,
    "avg_time_per_mcq": 1.6
  },
  "summary": {
    "total_facts": 54000,
    "verified_facts": 45900,
    "verification_rate": 0.85,
    "flagged_mcqs": 2700,
    "flagged_percentage": 15.0,
    "avg_confidence": 0.86
  },
  "by_specialty": {
    "cardiology": {
      "mcqs": 2500,
      "flagged": 375,
      "avg_confidence": 0.88
    },
    ...
  },
  "confidence_distribution": {
    "0.0-0.5": 150,
    "0.5-0.7": 550,
    "0.7-0.8": 2000,
    "0.8-0.9": 10000,
    "0.9-1.0": 5300
  },
  "detailed_results": [...]
}
```

**Return Message:**
```markdown
# RAG Citation Validation - Complete

## ✅ Script Created

**File:** `scripts/validate_rag_citations.py`
**Lines of code:** 450
**Test coverage:** 85%

## 📊 Test Results (10 Sample MCQs)

- Execution time: 28 seconds
- Validated: 10/10 MCQs
- Average confidence: 0.84
- Flagged: 2/10 (20%)

## 🚀 Performance

- **Target:** 18,000 MCQs in 8 hours
- **Achieved:** Estimated 6-7 hours (parallel processing)
- **Optimization:** Async + batch Qdrant queries

## 📝 Usage Instructions

```bash
# Install dependencies
pip install -r scripts/requirements_validation.txt

# Run validation
python scripts/validate_rag_citations.py \
  --input data/mcqs/ \
  --output citation_validation_report.json
```

## 🧪 Validation Checklist

- [x] Unit tests: 12/12 passed
- [x] Type checking: 0 errors
- [x] Linting: Score 8.5/10
- [x] No hardcoded secrets
- [x] Performance target met

## 🔍 Next Steps

1. Run full validation on 18,000 MCQs (6-7 hours)
2. Review flagged items (~2,700 MCQs)
3. Prioritize remediation (critical <50% confidence)
```

## SUCCESS CRITERIA

- [ ] Script runs without errors on 10 sample MCQs
- [ ] Generates valid JSON report
- [ ] Exports flagged items correctly
- [ ] Processing time <8 hours for full dataset (18,000 MCQs)
- [ ] Progress bar updates in real-time
- [ ] Handles interruptions (checkpoint/resume)
- [ ] Tests pass (100% pass rate)
- [ ] Type hints for all functions
- [ ] Documentation complete

## ESTIMATED TIME

- **Planning:** 1 hour
- **Implementation:** 6 hours
- **Testing:** 2 hours
- **Documentation:** 1 hour
- **TOTAL:** 10 hours (1.25 days)
```

---

## 4. PHASE 1 TEMPLATES (Mobile PWA)

### Template 4.1: PWA Foundation

```markdown
# Task: Set up React + Vite PWA with Offline Support

## AGENT: project-manager-coordinator
## DELEGATING TO: flutter-desktop-expert (adapted for React)

## CONSTRAINTS (READ THESE FIRST)

### 1. Read Project Constraints
- [ ] Read: PROJECT_CONSTRAINTS.md (frontend architecture)
- [ ] Read: constraints/02-code-architecture.md
- [ ] Review: UI_MODULE_ORGANIZATION_ARCHITECTURE.md

### 2. Technology Constraints

**Framework:** React 18 + TypeScript + Vite
- ❌ NOT Next.js (too heavyweight for PWA)
- ❌ NOT Create React App (deprecated)
- ✅ Vite (faster dev server, better PWA support)

**Styling:** TailwindCSS + shadcn/ui
- ❌ NOT Material-UI (inconsistent with design system)
- ❌ NOT Bootstrap (outdated)
- ✅ Tailwind utility classes
- ✅ shadcn/ui for base components

**State:** Zustand + React Query
- ❌ NOT Redux (too verbose)
- ❌ NOT Context API alone (performance issues)
- ✅ Zustand for client state
- ✅ React Query for server state

### 3. PWA Requirements

**Service Worker:**
- Cache MCQs for offline access (500 most recent)
- Cache static assets (JS, CSS, images)
- Network-first for API calls (fallback to cache)
- Background sync for progress tracking

**Offline Storage:**
- IndexedDB for MCQ data (not localStorage - 5MB limit)
- Store user progress locally
- Sync to server when online

**Manifest:**
- App name: "irStudy - AMC Exam Prep"
- Icons: 192x192, 512x512 (PNG)
- Theme color: #0EA5E9 (sky blue)
- Display: standalone (fullscreen app)

### 4. Performance Constraints

**Target Metrics:**
- First Contentful Paint (FCP): <1.8s
- Time to Interactive (TTI): <3.0s
- Lighthouse PWA score: >90
- Bundle size: <500KB initial load

**Optimization:**
- Code splitting (React.lazy)
- Tree shaking (Vite does this)
- Image optimization (WebP)
- Font subsetting

### 5. Accessibility (WCAG 2.1 AA)

**Requirements:**
- All interactive elements: keyboard accessible
- Color contrast: 4.5:1 minimum
- ARIA labels: All buttons, inputs
- Focus indicators: Visible outline
- Screen reader: Semantic HTML

## SEARCH EXISTING PATTERNS

**Check existing frontend:**
- [ ] Read: `frontend/src/App.tsx` (current structure)
- [ ] Check: `frontend/package.json` (dependencies)
- [ ] Review: `frontend/vite.config.ts` (build config)

**Similar PWA implementations:**
- [ ] Search GitHub: "react vite pwa offline" (examples)
- [ ] Review: Vite PWA plugin docs (https://vite-pwa-org.netlify.app/)

## VALIDATION CHECKLIST (BEFORE RETURNING)

**Build & Lint:**
- [ ] Run: `npm run build` (0 errors)
- [ ] Run: `npm run lint` (0 errors)
- [ ] Run: `npm run type-check` (0 TypeScript errors)

**PWA Validation:**
- [ ] Lighthouse PWA audit: Score >90
- [ ] Manifest validation: All required fields present
- [ ] Service worker: Registered successfully
- [ ] Offline test: App loads with network disabled
- [ ] Install prompt: Works on mobile Chrome

**Performance:**
- [ ] Lighthouse Performance: Score >80
- [ ] Bundle size: Initial load <500KB
- [ ] First paint: <2 seconds on 3G

**Accessibility:**
- [ ] Lighthouse Accessibility: Score >90
- [ ] Keyboard navigation: All interactive elements reachable
- [ ] Screen reader test: VoiceOver/NVDA can navigate

## TASK DETAILS

**Objective:** Create a PWA foundation with offline support for MCQ practice.

**Components to Build:**

1. **Vite Configuration**
   ```typescript
   // vite.config.ts
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'
   import { VitePWA } from 'vite-plugin-pwa'

   export default defineConfig({
     plugins: [
       react(),
       VitePWA({
         registerType: 'autoUpdate',
         manifest: {
           name: 'irStudy - AMC Exam Preparation',
           short_name: 'irStudy',
           theme_color: '#0EA5E9',
           icons: [
             {
               src: '/icons/icon-192x192.png',
               sizes: '192x192',
               type: 'image/png'
             },
             {
               src: '/icons/icon-512x512.png',
               sizes: '512x512',
               type: 'image/png'
             }
           ]
         },
         workbox: {
           globPatterns: ['**/*.{js,css,html,png,svg,woff2}'],
           runtimeCaching: [
             {
               urlPattern: /^https:\/\/api\.irstudy\.com\.au\/api\/v1\/mcqs/,
               handler: 'NetworkFirst',
               options: {
                 cacheName: 'mcqs-cache',
                 expiration: {
                   maxEntries: 500,
                   maxAgeSeconds: 7 * 24 * 60 * 60 // 7 days
                 }
               }
             }
           ]
         }
       })
     ]
   })
   ```

2. **Offline Storage (IndexedDB)**
   ```typescript
   // src/lib/offline-storage.ts
   import { openDB, DBSchema } from 'idb';

   interface IRStudyDB extends DBSchema {
     mcqs: {
       key: string;
       value: MCQ;
       indexes: { 'by-specialty': string };
     };
     progress: {
       key: string;
       value: UserProgress;
     };
   }

   export async function getDB() {
     return openDB<IRStudyDB>('irstudy-db', 1, {
       upgrade(db) {
         const mcqStore = db.createObjectStore('mcqs', { keyPath: 'id' });
         mcqStore.createIndex('by-specialty', 'specialty');

         db.createObjectStore('progress', { keyPath: 'id' });
       },
     });
   }

   export async function cacheMCQ(mcq: MCQ) {
     const db = await getDB();
     await db.put('mcqs', mcq);
   }

   export async function getCachedMCQs(limit: number = 500) {
     const db = await getDB();
     return db.getAll('mcqs', undefined, limit);
   }
   ```

3. **App Shell**
   ```tsx
   // src/App.tsx
   import { Suspense } from 'react';
   import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
   import { ClerkProvider } from '@clerk/clerk-react';
   import { AppShell } from './components/layout/AppShell';
   import { Routes } from './routes';

   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 5 * 60 * 1000, // 5 minutes
         retry: 3,
       },
     },
   });

   export function App() {
     return (
       <ClerkProvider publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}>
         <QueryClientProvider client={queryClient}>
           <AppShell>
             <Suspense fallback={<div>Loading...</div>}>
               <Routes />
             </Suspense>
           </AppShell>
         </QueryClientProvider>
       </ClerkProvider>
     );
   }
   ```

4. **Install Prompt**
   ```tsx
   // src/components/InstallPWA.tsx
   import { useState, useEffect } from 'react';
   import { Button } from '@/components/ui/button';

   export function InstallPWA() {
     const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
     const [showInstall, setShowInstall] = useState(false);

     useEffect(() => {
       window.addEventListener('beforeinstallprompt', (e) => {
         e.preventDefault();
         setDeferredPrompt(e);
         setShowInstall(true);
       });
     }, []);

     const handleInstall = async () => {
       if (!deferredPrompt) return;

       deferredPrompt.prompt();
       const { outcome } = await deferredPrompt.userChoice;

       if (outcome === 'accepted') {
         setShowInstall(false);
       }
     };

     if (!showInstall) return null;

     return (
       <div className="fixed bottom-4 right-4 bg-sky-500 text-white p-4 rounded-lg shadow-lg">
         <p className="mb-2">Install irStudy for offline access</p>
         <Button onClick={handleInstall}>Install App</Button>
       </div>
     );
   }
   ```

## EXPECTED OUTPUT

**File Structure:**
```
frontend/
├── vite.config.ts (modified)
├── package.json (add dependencies)
├── public/
│   ├── manifest.json (new)
│   └── icons/
│       ├── icon-192x192.png (new)
│       └── icon-512x512.png (new)
├── src/
│   ├── App.tsx (modified)
│   ├── lib/
│   │   └── offline-storage.ts (new)
│   └── components/
│       ├── layout/
│       │   └── AppShell.tsx (new)
│       └── InstallPWA.tsx (new)
└── sw.js (auto-generated by Vite PWA)
```

**Dependencies to Add:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@clerk/clerk-react": "^4.29.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "idb": "^8.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.11",
    "vite-plugin-pwa": "^0.17.4",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.1"
  }
}
```

**Return Message:**
```markdown
# PWA Foundation - Complete

## ✅ Components Built

1. **Vite + PWA Plugin** configured
2. **Service Worker** registered (caches 500 MCQs)
3. **IndexedDB** offline storage implemented
4. **App Shell** with Clerk + React Query
5. **Install Prompt** component

## 📊 Validation Results

### Build & Lint
- Build: SUCCESS (0 errors)
- Lint: PASS (0 errors)
- Type check: PASS (0 errors)

### PWA Metrics (Lighthouse)
- PWA Score: 92/100 ✓
- Performance: 85/100 ✓
- Accessibility: 95/100 ✓

### Offline Test
- Network disabled: App loads ✓
- Cached MCQs: 500 available ✓
- Install prompt: Works on Chrome mobile ✓

## 📝 Next Steps

1. Add MCQ practice components (QuestionCard, AnswerOptions)
2. Implement RAG-powered search
3. Add citation display (CitationPanel)
4. Create progress tracking

## 🚀 How to Test

```bash
cd frontend
npm install
npm run dev

# Build for production
npm run build
npm run preview

# Test offline
1. Open in Chrome
2. Open DevTools → Application → Service Workers
3. Check "Offline"
4. Refresh page (should still load)
```
```

## SUCCESS CRITERIA

- [ ] PWA installable on mobile Chrome
- [ ] Service worker caches 500 MCQs
- [ ] App loads offline
- [ ] Lighthouse PWA score >90
- [ ] Performance score >80
- [ ] Accessibility score >90
- [ ] Bundle size <500KB
- [ ] Install prompt appears
- [ ] IndexedDB stores MCQs correctly

## ESTIMATED TIME

- **Setup:** 2 hours
- **Service Worker:** 3 hours
- **Offline Storage:** 2 hours
- **Testing:** 2 hours
- **Optimization:** 1 hour
- **TOTAL:** 10 hours (1.25 days)
```

---

## 5. VALIDATION CHECKLISTS

### Universal Pre-Return Checklist

**Every agent MUST complete before returning code:**

```markdown
## 🔍 AGENT SELF-VALIDATION CHECKLIST

### 1. Compilation / Build
- [ ] Code compiles without errors
- [ ] Command: [specific command for this project]
- [ ] Result: 0 errors, 0 critical warnings

### 2. Security
- [ ] No hardcoded credentials (grep check passed)
- [ ] No API keys in code (git-secrets passed)
- [ ] Environment variables used for secrets
- [ ] Pre-commit hook would allow this commit

### 3. Testing
- [ ] All existing tests still pass (100% requirement)
- [ ] New tests added for new functionality
- [ ] Test coverage maintained (≥70%)

### 4. Code Quality
- [ ] Linter passes (0 errors)
- [ ] Type checker passes (if TypeScript/Python)
- [ ] Follows project style guide
- [ ] Code reviewed against anti-patterns

### 5. Documentation
- [ ] Function/class docstrings added
- [ ] README updated (if setup changed)
- [ ] Comments explain complex logic
- [ ] API documentation generated (if public API)

### 6. Performance
- [ ] Meets performance targets (if specified)
- [ ] No obvious performance regressions
- [ ] Profiled if performance-critical code

### 7. Constraints Verified
- [ ] Re-read constraint sections relevant to my task
- [ ] All "NEVER" rules followed
- [ ] All "ALWAYS" patterns used
- [ ] Searched for and reused existing patterns
```

---

**Document Status:** COMPLETE
**Total Templates:** 3 detailed + 1 universal checklist
**Coverage:** Phase 0 (Security + Validation) + Phase 1 (PWA)
**Next:** Create Phase 2 (EMR) and Phase 3 (AI Simulation) templates

Would you like me to continue with Phase 2 & 3 templates, or move on to the other remaining documents (monitoring dashboard, B2B sales playbook)?
