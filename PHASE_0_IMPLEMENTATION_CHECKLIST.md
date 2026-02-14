# Phase 0: Foundation & Content Validation
## Week-by-Week Implementation Checklist

**Duration:** 4 weeks
**Goal:** Secure infrastructure + Validated content ready for production
**Team:** 1.0 FTE Developer + 0.25 FTE Medical Reviewer + Legal Consultant

---

## 📅 WEEK 1: SECURITY FOUNDATION

### Day 1-2: Authentication Setup (Clerk)

**Prerequisites:**
- [ ] Create accounts:
  - [ ] Clerk account (https://clerk.com) - Select HIPAA-compliant tier if storing PHI
  - [ ] Get API keys (Development + Production)
  - [ ] Add to .env.example template (safe to commit)
  - [ ] Add to 1Password/AWS Secrets Manager (DO NOT commit)

**Implementation:**

```bash
# 1. Install Clerk
cd backend
pip install clerk-backend-api
cd ../frontend
npm install @clerk/clerk-react

# 2. Configure environment variables
cat > backend/.env.local << 'EOF'
# Clerk Configuration (DO NOT COMMIT)
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxx
CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Frontend will use VITE_CLERK_PUBLISHABLE_KEY
EOF

cat > frontend/.env.local << 'EOF'
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
EOF

# 3. Add to .gitignore
echo ".env.local" >> .gitignore
echo ".env" >> .gitignore

# 4. Create safe template
cat > .env.example << 'EOF'
# Clerk Configuration (Get from https://dashboard.clerk.com)
CLERK_SECRET_KEY=sk_test_your_key_here
CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_WEBHOOK_SECRET=whsec_your_secret_here

# Frontend
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
EOF
```

**Backend Integration:**

```python
# backend/src/auth/clerk_client.py
from clerk_backend_api import Clerk
import os

clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

async def verify_session(session_token: str):
    """Verify Clerk session token."""
    try:
        session = clerk.sessions.verify_session(session_token)
        return session
    except Exception as e:
        raise UnauthorizedException(f"Invalid session: {str(e)}")

async def get_user(user_id: str):
    """Get user details from Clerk."""
    return clerk.users.get(user_id)
```

**FastAPI Dependency:**

```python
# backend/src/auth/dependencies.py
from fastapi import Depends, HTTPException, Header
from .clerk_client import verify_session, get_user

async def require_auth(authorization: str = Header(...)):
    """Require valid authentication."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    session = await verify_session(token)
    user = await get_user(session.user_id)

    return {
        "user_id": user.id,
        "email": user.email_addresses[0].email_address,
        "subscription_tier": user.public_metadata.get("subscription_tier", "free"),
    }

async def require_pro(user = Depends(require_auth)):
    """Require Pro or Ultimate tier."""
    if user["subscription_tier"] not in ["pro", "ultimate"]:
        raise HTTPException(status_code=403, detail="Pro subscription required")
    return user
```

**Frontend Integration:**

```typescript
// frontend/src/main.tsx
import { ClerkProvider } from '@clerk/clerk-react';

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <App />
    </ClerkProvider>
  </StrictMode>
);
```

```typescript
// frontend/src/components/auth/ProtectedRoute.tsx
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
```

**Checklist:**
- [ ] Clerk SDK installed (backend + frontend)
- [ ] Environment variables configured
- [ ] .env.local NOT committed to git (verify with `git status`)
- [ ] .env.example committed with placeholder values
- [ ] Backend: verify_session() function works
- [ ] Frontend: ClerkProvider wraps app
- [ ] Test: Sign up new user via Clerk UI
- [ ] Test: require_auth dependency blocks unauthenticated requests
- [ ] Test: require_pro dependency blocks free users

---

### Day 2-3: Payment Setup (Stripe)

**Prerequisites:**
- [ ] Create Stripe account (https://stripe.com)
- [ ] Complete business verification
- [ ] Get API keys (Test + Live)
- [ ] Configure products and prices

**Stripe Product Configuration:**

```bash
# Use Stripe CLI to create products
stripe products create --name "irStudy Free" --description "200 MCQs, 10 OSCEs"
stripe prices create --product <free_product_id> --unit-amount 0 --currency aud

stripe products create --name "irStudy Pro" --description "18,000 MCQs, EMR Practice"
stripe prices create --product <pro_product_id> --unit-amount 4900 --currency aud --recurring interval=month
stripe prices create --product <pro_product_id> --unit-amount 58800 --currency aud --recurring interval=year

stripe products create --name "irStudy Ultimate" --description "Unlimited AI Simulation"
stripe prices create --product <ultimate_product_id> --unit-amount 7900 --currency aud --recurring interval=month
stripe prices create --product <ultimate_product_id> --unit-amount 94800 --currency aud --recurring interval=year
```

**Backend Integration:**

```python
# backend/src/payments/stripe_client.py
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

async def create_checkout_session(
    user_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str
):
    """Create Stripe Checkout session."""
    session = stripe.checkout.Session.create(
        customer_email=user.email,
        client_reference_id=user_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": user_id}
    )
    return session

async def handle_webhook(payload: bytes, signature: str):
    """Handle Stripe webhook events."""
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await update_subscription(
            user_id=session["metadata"]["user_id"],
            subscription_id=session["subscription"],
            status="active"
        )
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await update_subscription(
            subscription_id=subscription["id"],
            status=subscription["status"]
        )
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await cancel_subscription(subscription["id"])

    return {"status": "success"}
```

**API Endpoints:**

```python
# backend/src/api/v1/payments.py
from fastapi import APIRouter, Depends, Request
from src.auth.dependencies import require_auth
from src.payments.stripe_client import create_checkout_session, handle_webhook

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

@router.post("/create-checkout")
async def create_checkout(
    price_id: str,
    user = Depends(require_auth)
):
    """Create Stripe checkout session."""
    session = await create_checkout_session(
        user_id=user["user_id"],
        price_id=price_id,
        success_url=f"{os.getenv('FRONTEND_URL')}/payment/success",
        cancel_url=f"{os.getenv('FRONTEND_URL')}/payment/cancel"
    )
    return {"checkout_url": session.url}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    return await handle_webhook(payload, signature)
```

**Frontend Integration:**

```typescript
// frontend/src/services/payments.ts
export async function upgradeToProMonthly(token: string) {
  const response = await fetch('/api/v1/payments/create-checkout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      price_id: 'price_pro_monthly_xxxxxxxxxx' // From Stripe dashboard
    })
  });

  const { checkout_url } = await response.json();
  window.location.href = checkout_url; // Redirect to Stripe Checkout
}
```

**Checklist:**
- [ ] Stripe account created and verified
- [ ] Products created (Free, Pro Monthly, Pro Annual, Ultimate Monthly, Ultimate Annual)
- [ ] Prices configured in AUD
- [ ] Stripe SDK installed (backend)
- [ ] Webhook endpoint configured (backend)
- [ ] Webhook secret obtained from Stripe dashboard
- [ ] Test mode: Complete test checkout (card: 4242 4242 4242 4242)
- [ ] Webhook: Verify subscription.created event updates database
- [ ] Frontend: "Upgrade" button redirects to Stripe Checkout
- [ ] Success page: Show subscription confirmation

---

### Day 3-4: Database Security Hardening

**PostgreSQL Row-Level Security (RLS):**

```sql
-- backend/alembic/versions/20260206_1200_enable_rls.sql

-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcq_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE osce_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE soap_notes ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY user_isolation_policy ON users
  FOR ALL
  USING (id = current_setting('app.user_id')::uuid);

CREATE POLICY mcq_progress_isolation ON mcq_progress
  FOR ALL
  USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY osce_sessions_isolation ON osce_sessions
  FOR ALL
  USING (user_id = current_setting('app.user_id')::uuid);

CREATE POLICY soap_notes_isolation ON soap_notes
  FOR ALL
  USING (user_id = current_setting('app.user_id')::uuid);

-- Admin bypass (for admin queries)
CREATE POLICY admin_bypass ON users
  FOR ALL
  TO admin_role
  USING (true);
```

**Backend: Set RLS Context:**

```python
# backend/src/db/session.py
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_rls_context(dbapi_conn, connection_record):
    """Set RLS context for every connection."""
    cursor = dbapi_conn.cursor()
    user_id = connection_record.info.get('user_id')
    if user_id:
        cursor.execute(f"SET app.user_id = '{user_id}'")
    cursor.close()

async def get_db_with_context(user_id: str):
    """Get database session with RLS context."""
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    connection.info['user_id'] = user_id
    session = Session(bind=connection)
    return session
```

**Encryption at Rest (AWS RDS):**

```bash
# Enable encryption on existing RDS instance (requires backup/restore)
aws rds create-db-snapshot \
  --db-instance-identifier irstudy-prod \
  --db-snapshot-identifier irstudy-pre-encryption-$(date +%Y%m%d)

aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier irstudy-prod-encrypted \
  --db-snapshot-identifier irstudy-pre-encryption-20260206 \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:ap-southeast-2:123456789012:key/xxxxxxxx

# Update connection string to new encrypted instance
```

**Automated Backups:**

```bash
# Configure automated backups (via AWS RDS console or CLI)
aws rds modify-db-instance \
  --db-instance-identifier irstudy-prod-encrypted \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00" \
  --apply-immediately

# Enable point-in-time recovery (automatic with backups)
```

**Checklist:**
- [ ] RLS enabled on all user-facing tables
- [ ] RLS policies tested (user A cannot see user B's data)
- [ ] Database encryption at rest enabled (AWS RDS)
- [ ] Connection strings updated to encrypted instance
- [ ] Automated backups configured (30-day retention)
- [ ] Point-in-time recovery tested (restore to 24h ago)
- [ ] Database credentials rotated (never hardcode in code)
- [ ] Connection pooling configured (max 20 connections)

---

### Day 4-5: Pre-Commit Hooks & Secret Scanning

**Install git-secrets:**

```bash
# macOS
brew install git-secrets

# Linux
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
make install

# Configure for repository
cd /home/dev/Development/irStudy
git secrets --install
git secrets --register-aws  # AWS credential patterns

# Add custom patterns
git secrets --add 'API_KEY.*'
git secrets --add 'CLERK_SECRET_KEY.*'
git secrets --add 'STRIPE_SECRET_KEY.*'
git secrets --add 'ANTHROPIC_API_KEY.*'
git secrets --add 'OPENAI_API_KEY.*'
git secrets --add 'postgres://.*:.*@'  # Database URLs with passwords

# Test
echo "CLERK_SECRET_KEY=sk_test_abc123" > test_secret.txt
git add test_secret.txt
git commit -m "test secret"
# Should FAIL with: "test_secret.txt:1:CLERK_SECRET_KEY=sk_test_abc123"
rm test_secret.txt
```

**Alternative: detect-secrets (Python):**

```bash
pip install detect-secrets

# Generate baseline (scans existing repo)
detect-secrets scan > .secrets.baseline

# Add to pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
detect-secrets-hook --baseline .secrets.baseline
if [ $? -ne 0 ]; then
  echo "❌ SECRET DETECTED! Commit blocked."
  echo "If this is a false positive, add to .secrets.baseline"
  exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

**CI/CD Integration (GitHub Actions):**

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  secret-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install detect-secrets
        run: pip install detect-secrets
      - name: Scan for secrets
        run: |
          detect-secrets scan --baseline .secrets.baseline
          if [ $? -ne 0 ]; then
            echo "❌ Secrets detected in code!"
            exit 1
          fi

  dependency-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run npm audit
        working-directory: frontend
        run: npm audit --audit-level=high
      - name: Run pip-audit
        working-directory: backend
        run: |
          pip install pip-audit
          pip-audit -r requirements.txt

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Semgrep
        run: |
          docker run --rm -v "${PWD}:/src" returntocorp/semgrep semgrep \
            --config=auto \
            --error \
            --strict \
            /src
```

**Checklist:**
- [ ] git-secrets installed and configured
- [ ] Custom patterns added (API keys, database URLs)
- [ ] Test: Attempt to commit a fake secret (should fail)
- [ ] detect-secrets baseline generated
- [ ] Pre-commit hook installed (.git/hooks/pre-commit)
- [ ] CI/CD: GitHub Actions workflow created
- [ ] CI/CD: Secret scanning runs on every push
- [ ] CI/CD: Dependency scanning (npm audit, pip-audit)
- [ ] CI/CD: SAST (Semgrep) configured
- [ ] Documentation: Updated CONTRIBUTING.md with security guidelines

---

### Day 5: Monitoring & Alerting Setup

**Sentry (Error Tracking):**

```bash
# Backend
pip install sentry-sdk[fastapi]

# Frontend
npm install @sentry/react
```

```python
# backend/src/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development"),
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
    integrations=[FastApiIntegration()]
)
```

```typescript
// frontend/src/main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

**CloudWatch Logs (AWS):**

```python
# backend/src/logging/cloudwatch.py
import boto3
import logging
from pythonjsonlogger import jsonlogger

cloudwatch = boto3.client('logs', region_name='ap-southeast-2')

# Create log group
try:
    cloudwatch.create_log_group(logGroupName='/aws/irstudy/backend')
except cloudwatch.exceptions.ResourceAlreadyExistsException:
    pass

# Configure logger
logger = logging.getLogger()
handler = logging.StreamHandler()  # CloudWatch captures stdout
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Uptime Monitoring (UptimeRobot):**

```bash
# Create monitors via API or UI
# 1. Main site: https://app.irstudy.com.au (5-min intervals)
# 2. API health: https://api.irstudy.com.au/health (5-min)
# 3. Stripe webhook: https://api.irstudy.com.au/api/v1/payments/webhook (30-min)

# Alert contacts:
# - Email: ops@irstudy.com.au
# - Slack: #alerts channel
```

**Failed Login Alerting:**

```python
# backend/src/auth/monitoring.py
from collections import defaultdict
from datetime import datetime, timedelta

failed_logins = defaultdict(list)  # IP -> [timestamp, timestamp, ...]

async def track_failed_login(ip_address: str, email: str):
    """Track failed login attempts."""
    now = datetime.utcnow()

    # Clean old entries (older than 1 hour)
    failed_logins[ip_address] = [
        ts for ts in failed_logins[ip_address]
        if now - ts < timedelta(hours=1)
    ]

    # Add new failure
    failed_logins[ip_address].append(now)

    # Alert if 5+ failures in 1 hour
    if len(failed_logins[ip_address]) >= 5:
        await send_alert(
            subject="⚠️ Suspicious Login Activity",
            message=f"5+ failed login attempts from {ip_address} for {email}",
            severity="high"
        )

        # Lock account temporarily
        await lock_account(email, duration_minutes=15)
```

**Checklist:**
- [ ] Sentry account created (https://sentry.io)
- [ ] Sentry DSN configured (backend + frontend)
- [ ] Test: Trigger an error, verify it appears in Sentry
- [ ] CloudWatch Logs: Log group created
- [ ] CloudWatch: Test logs appear in AWS console
- [ ] UptimeRobot: 3 monitors configured (site, API, webhook)
- [ ] Failed login alerting: Tested with 5 fake failures
- [ ] Alert routing: Verify emails and Slack messages arrive
- [ ] Dashboard: Create Grafana/Datadog dashboard for key metrics

---

## 📅 WEEK 2: AUTOMATED CONTENT VALIDATION

### Day 1-3: RAG Citation Validation Script

**Objective:** Validate 54,000 facts (18,000 MCQs × 3 citations) against Qdrant database

**Script Structure:**

```python
# scripts/validate_rag_citations.py
import json
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from anthropic import Anthropic
from tqdm import tqdm

# Initialize clients
qdrant = QdrantClient(url="http://localhost:6333")
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def extract_facts_from_explanation(explanation: str) -> list[str]:
    """Extract medical facts from MCQ explanation using Claude."""
    prompt = f"""Extract discrete medical facts from this explanation.
Each fact should be a single, verifiable statement.

Explanation:
{explanation}

Return JSON array of facts:
["fact 1", "fact 2", "fact 3"]
"""

    message = anthropic.messages.create(
        model="claude-3-5-sonnet-20250116",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    facts = json.loads(message.content[0].text)
    return facts

async def validate_fact_against_rag(fact: str) -> dict:
    """Query Qdrant to find source for this fact."""
    # Generate embedding for fact
    embedding_response = anthropic.messages.create(
        model="claude-3-5-sonnet-20250116",
        max_tokens=10,
        messages=[{"role": "user", "content": f"Generate embedding: {fact}"}]
    )

    # Search Qdrant (simplified - actual implementation uses sentence-transformers)
    results = qdrant.search(
        collection_name="medical_knowledge",
        query_vector=embedding_response.embeddings[0],
        limit=5,
        score_threshold=0.75
    )

    if not results:
        return {
            "fact": fact,
            "verified": False,
            "confidence": 0.0,
            "source": None,
            "message": "No matching source found"
        }

    best_match = results[0]
    return {
        "fact": fact,
        "verified": True,
        "confidence": best_match.score,
        "source": best_match.payload.get("source_name"),
        "page": best_match.payload.get("page_number"),
        "chunk_id": best_match.id,
        "matched_text": best_match.payload.get("text")[:200]  # Preview
    }

async def validate_mcq(mcq: dict) -> dict:
    """Validate all facts in an MCQ explanation."""
    explanation = mcq["explanation"]

    # Extract facts
    facts = await extract_facts_from_explanation(explanation)

    # Validate each fact
    validations = []
    for fact in facts:
        validation = await validate_fact_against_rag(fact)
        validations.append(validation)

    # Calculate overall confidence
    verified_count = sum(1 for v in validations if v["verified"])
    avg_confidence = sum(v["confidence"] for v in validations) / len(validations)

    return {
        "mcq_id": mcq["id"],
        "specialty": mcq["specialty"],
        "topic": mcq["topic"],
        "facts_extracted": len(facts),
        "facts_verified": verified_count,
        "verification_rate": verified_count / len(facts),
        "avg_confidence": avg_confidence,
        "validations": validations,
        "flagged": avg_confidence < 0.80  # Flag if <80% confidence
    }

async def main():
    """Validate all MCQs."""
    # Load MCQs from database or JSON files
    mcqs = load_all_mcqs()  # Your implementation

    print(f"Validating {len(mcqs)} MCQs...")

    results = []
    flagged_count = 0

    for mcq in tqdm(mcqs):
        result = await validate_mcq(mcq)
        results.append(result)

        if result["flagged"]:
            flagged_count += 1

    # Generate report
    report = {
        "total_mcqs": len(mcqs),
        "total_facts": sum(r["facts_extracted"] for r in results),
        "verified_facts": sum(r["facts_verified"] for r in results),
        "flagged_mcqs": flagged_count,
        "flagged_percentage": (flagged_count / len(mcqs)) * 100,
        "avg_confidence": sum(r["avg_confidence"] for r in results) / len(results),
        "by_specialty": {},  # Breakdown by specialty
        "detailed_results": results
    }

    # Save report
    with open("citation_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Validation complete!")
    print(f"   Total MCQs: {len(mcqs)}")
    print(f"   Flagged: {flagged_count} ({flagged_count/len(mcqs)*100:.1f}%)")
    print(f"   Avg confidence: {report['avg_confidence']:.2f}")
    print(f"\n📊 Report saved: citation_validation_report.json")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run Script:**

```bash
cd /home/dev/Development/irStudy

# Install dependencies
pip install qdrant-client anthropic tqdm

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run validation (takes ~6-8 hours for 18,000 MCQs)
python scripts/validate_rag_citations.py

# Monitor progress
tail -f citation_validation.log
```

**Expected Output:**

```json
{
  "total_mcqs": 18000,
  "total_facts": 54000,
  "verified_facts": 45900,
  "flagged_mcqs": 2700,
  "flagged_percentage": 15.0,
  "avg_confidence": 0.86,
  "by_specialty": {
    "cardiology": {
      "mcqs": 2500,
      "flagged": 375,
      "avg_confidence": 0.88
    },
    ...
  },
  "detailed_results": [...]
}
```

**Checklist:**
- [ ] Script written: validate_rag_citations.py
- [ ] Dependencies installed (qdrant-client, anthropic)
- [ ] Qdrant database accessible (localhost:6333)
- [ ] Test run: Validate 10 sample MCQs (verify JSON output)
- [ ] Full run: Execute on all 18,000 MCQs (6-8 hours)
- [ ] Report generated: citation_validation_report.json
- [ ] Review: Check flagged_percentage (<20% is good)
- [ ] Export: Flagged items to flagged_mcqs_for_review.json

---

### Day 3-5: Australian Compliance Check

**Objective:** Ensure all content follows Australian medical guidelines

**Script:**

```python
# scripts/validate_australian_compliance.py
import json
import re
from dataclasses import dataclass

@dataclass
class ComplianceIssue:
    mcq_id: str
    issue_type: str  # "drug_name", "guideline", "terminology", "units", "coding"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    suggestion: str

# PBS medication database (simplified - load from PBS website)
PBS_MEDICATIONS = {
    "metformin": {"brand_names": ["Diabex", "Diaformin"], "pbs": True},
    "paracetamol": {"brand_names": ["Panadol", "Panamax"], "pbs": True},
    # ... 4,000+ medications
}

# Australian terminology preferences
AUSTRALIAN_SPELLING = {
    "pediatric": "paediatric",
    "anemia": "anaemia",
    "edema": "oedema",
    "fetus": "foetus",
    "liter": "litre",
    "meter": "metre",
}

# Unit conversions (SI units required in Australia)
UNIT_ISSUES = {
    r"mg/dL": "Use mmol/L for glucose, mg/L for other values",
    r"°F": "Use °C (Celsius) for temperature",
    r"lb": "Use kg for weight",
    r"inches": "Use cm for height",
}

def check_drug_names(text: str) -> list[ComplianceIssue]:
    """Check if medications use generic names (PBS requirement)."""
    issues = []

    # Find drug names (simplified - actual implementation uses NER)
    potential_drugs = re.findall(r'\b[A-Z][a-z]+\b', text)

    for drug in potential_drugs:
        # Check if it's a brand name when generic is available
        for generic, info in PBS_MEDICATIONS.items():
            if drug in info["brand_names"]:
                issues.append(ComplianceIssue(
                    mcq_id="",
                    issue_type="drug_name",
                    severity="high",
                    description=f"Brand name '{drug}' used instead of generic",
                    suggestion=f"Use generic name '{generic}' (PBS requirement)"
                ))

    return issues

def check_guideline_citations(citations: list) -> list[ComplianceIssue]:
    """Verify Australian guideline sources."""
    issues = []
    australian_sources = ["eTG", "AMH", "RACGP", "NSW Health", "NHMRC"]

    for citation in citations:
        source = citation.get("source_name", "")

        # Flag if using international guidelines without Australian equivalent
        if any(intl in source for intl in ["UpToDate", "NICE", "AHA", "ACC"]):
            if not any(aus in str(citations) for aus in australian_sources):
                issues.append(ComplianceIssue(
                    mcq_id="",
                    issue_type="guideline",
                    severity="medium",
                    description=f"International guideline '{source}' without Australian equivalent",
                    suggestion="Add eTG, AMH, or RACGP citation"
                ))

    return issues

def check_terminology(text: str) -> list[ComplianceIssue]:
    """Check for American spelling."""
    issues = []

    for american, australian in AUSTRALIAN_SPELLING.items():
        if re.search(rf'\b{american}\b', text, re.IGNORECASE):
            issues.append(ComplianceIssue(
                mcq_id="",
                issue_type="terminology",
                severity="low",
                description=f"American spelling: '{american}'",
                suggestion=f"Use Australian spelling: '{australian}'"
            ))

    return issues

def check_units(text: str) -> list[ComplianceIssue]:
    """Check for non-SI units."""
    issues = []

    for pattern, message in UNIT_ISSUES.items():
        if re.search(pattern, text):
            issues.append(ComplianceIssue(
                mcq_id="",
                issue_type="units",
                severity="medium",
                description=f"Non-SI unit found: {pattern}",
                suggestion=message
            ))

    return issues

def validate_mcq_compliance(mcq: dict) -> dict:
    """Check MCQ for Australian compliance."""
    issues = []

    # Check all text fields
    full_text = " ".join([
        mcq.get("question", ""),
        mcq.get("explanation", ""),
        " ".join([opt.get("text", "") for opt in mcq.get("options", [])])
    ])

    issues.extend(check_drug_names(full_text))
    issues.extend(check_guideline_citations(mcq.get("citations", [])))
    issues.extend(check_terminology(full_text))
    issues.extend(check_units(full_text))

    # Set MCQ ID on all issues
    for issue in issues:
        issue.mcq_id = mcq["id"]

    return {
        "mcq_id": mcq["id"],
        "compliant": len(issues) == 0,
        "issue_count": len(issues),
        "issues": [vars(issue) for issue in issues],
        "severity_breakdown": {
            "critical": sum(1 for i in issues if i.severity == "critical"),
            "high": sum(1 for i in issues if i.severity == "high"),
            "medium": sum(1 for i in issues if i.severity == "medium"),
            "low": sum(1 for i in issues if i.severity == "low"),
        }
    }

def main():
    mcqs = load_all_mcqs()

    results = []
    non_compliant_count = 0

    for mcq in tqdm(mcqs):
        result = validate_mcq_compliance(mcq)
        results.append(result)

        if not result["compliant"]:
            non_compliant_count += 1

    report = {
        "total_mcqs": len(mcqs),
        "compliant_mcqs": len(mcqs) - non_compliant_count,
        "non_compliant_mcqs": non_compliant_count,
        "compliance_rate": ((len(mcqs) - non_compliant_count) / len(mcqs)) * 100,
        "total_issues": sum(r["issue_count"] for r in results),
        "issues_by_type": {},
        "issues_by_severity": {},
        "detailed_results": results
    }

    with open("australian_compliance_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Australian compliance check complete!")
    print(f"   Compliance rate: {report['compliance_rate']:.1f}%")
    print(f"   Non-compliant: {non_compliant_count} MCQs")

if __name__ == "__main__":
    main()
```

**Checklist:**
- [ ] Script written: validate_australian_compliance.py
- [ ] PBS medication database loaded (or API integrated)
- [ ] Test run: Validate 10 sample MCQs
- [ ] Full run: Execute on all 18,000 MCQs (2-3 hours)
- [ ] Report generated: australian_compliance_report.json
- [ ] Review: Compliance rate >95% is target
- [ ] Export: Non-compliant items to non_compliant_mcqs.json

---

## 📅 WEEK 3: MANUAL REVIEW & REMEDIATION

### Day 1-5: Clinical Accuracy Review

**Objective:** Medical professional reviews 500 randomly sampled MCQs

**Setup Review Interface:**

```typescript
// scripts/clinical-review-app/src/App.tsx
import { useState } from 'react';

interface MCQ {
  id: string;
  specialty: string;
  question: string;
  options: { text: string; is_correct: boolean }[];
  explanation: string;
  citations: any[];
}

export function ReviewApp() {
  const [mcqs, setMcqs] = useState<MCQ[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [reviews, setReviews] = useState<Record<string, any>>({});

  const currentMcq = mcqs[currentIndex];

  const submitReview = (verdict: 'pass' | 'fail' | 'revise', comments: string) => {
    setReviews({
      ...reviews,
      [currentMcq.id]: {
        mcq_id: currentMcq.id,
        verdict,
        comments,
        reviewer: 'Dr. Smith',
        review_date: new Date().toISOString()
      }
    });

    // Move to next
    setCurrentIndex(currentIndex + 1);
  };

  return (
    <div className="p-8">
      <div className="mb-4">
        <span>Progress: {currentIndex + 1} / {mcqs.length}</span>
      </div>

      <div className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-bold mb-4">{currentMcq?.specialty}</h2>

        <div className="mb-4">
          <h3 className="font-semibold">Question:</h3>
          <p>{currentMcq?.question}</p>
        </div>

        <div className="mb-4">
          <h3 className="font-semibold">Options:</h3>
          <ul>
            {currentMcq?.options.map((opt, i) => (
              <li key={i} className={opt.is_correct ? 'font-bold' : ''}>
                {opt.text} {opt.is_correct && '✓'}
              </li>
            ))}
          </ul>
        </div>

        <div className="mb-4">
          <h3 className="font-semibold">Explanation:</h3>
          <p>{currentMcq?.explanation}</p>
        </div>

        <div className="mb-6">
          <h3 className="font-semibold">Citations:</h3>
          <ul>
            {currentMcq?.citations.map((cit, i) => (
              <li key={i}>{cit.source_name}, p.{cit.page_number}</li>
            ))}
          </ul>
        </div>

        <div className="flex gap-4">
          <button
            onClick={() => submitReview('pass', '')}
            className="bg-green-500 text-white px-6 py-2 rounded"
          >
            ✓ Pass
          </button>
          <button
            onClick={() => {
              const comments = prompt('Comments (required):');
              if (comments) submitReview('revise', comments);
            }}
            className="bg-yellow-500 text-white px-6 py-2 rounded"
          >
            ⚠ Needs Revision
          </button>
          <button
            onClick={() => {
              const comments = prompt('Comments (required):');
              if (comments) submitReview('fail', comments);
            }}
            className="bg-red-500 text-white px-6 py-2 rounded"
          >
            ✗ Fail (Clinically Incorrect)
          </button>
        </div>
      </div>

      <button
        onClick={() => {
          // Save reviews
          const blob = new Blob([JSON.stringify(reviews, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'clinical_reviews.json';
          a.click();
        }}
        className="mt-4 bg-blue-500 text-white px-6 py-2 rounded"
      >
        💾 Save Progress
      </button>
    </div>
  );
}
```

**Sampling Strategy:**

```python
# scripts/sample_mcqs_for_review.py
import json
import random

def stratified_sample(mcqs: list, sample_size: int = 500) -> list:
    """
    Stratified random sample:
    - 25 MCQs per specialty (18 specialties = 450)
    - 50 additional from flagged items (low confidence / non-compliant)
    """
    by_specialty = {}
    for mcq in mcqs:
        specialty = mcq["specialty"]
        if specialty not in by_specialty:
            by_specialty[specialty] = []
        by_specialty[specialty].append(mcq)

    sample = []

    # 25 per specialty
    for specialty, specialty_mcqs in by_specialty.items():
        sampled = random.sample(specialty_mcqs, min(25, len(specialty_mcqs)))
        sample.extend(sampled)

    # Load flagged items
    with open("flagged_mcqs_for_review.json") as f:
        flagged = json.load(f)

    # Add 50 flagged items
    flagged_sample = random.sample(flagged, min(50, len(flagged)))
    sample.extend(flagged_sample)

    return sample

if __name__ == "__main__":
    mcqs = load_all_mcqs()
    sample = stratified_sample(mcqs, 500)

    with open("mcqs_for_clinical_review.json", "w") as f:
        json.dump(sample, f, indent=2)

    print(f"✅ Sampled {len(sample)} MCQs for review")
```

**Checklist:**
- [ ] Recruit medical reviewer (GP or specialist, $100/hr)
- [ ] Sample 500 MCQs (stratified by specialty)
- [ ] Set up review interface (React app or spreadsheet)
- [ ] Reviewer completes 25 MCQs/day (5 days, 4 hours/day)
- [ ] Reviews saved: clinical_reviews.json
- [ ] Calculate pass rate: (pass_count / 500) * 100
- [ ] Target: >95% pass rate
- [ ] If <95%: Expand sample and re-review

---

### Day 1-3: Fix Critical Issues (Parallel with Review)

**Remediation Workflow:**

```python
# scripts/remediate_mcqs.py
import json
from anthropic import Anthropic

anthropic = Anthropic()

async def regenerate_mcq(mcq: dict, issue: str) -> dict:
    """Regenerate MCQ using Claude with issue context."""
    prompt = f"""You are a medical education expert creating MCQs for Australian medical exams.

ORIGINAL MCQ (has issues):
Question: {mcq['question']}
Options: {json.dumps(mcq['options'])}
Explanation: {mcq['explanation']}

ISSUE IDENTIFIED:
{issue}

REQUIREMENTS:
1. Fix the identified issue
2. Maintain clinical accuracy
3. Use Australian guidelines (eTG, AMH, RACGP)
4. Provide 3 citations with page numbers
5. Use Australian spelling and terminology

Generate a corrected MCQ in JSON format:
{{
  "question": "...",
  "options": [
    {{"text": "...", "is_correct": true}},
    {{"text": "...", "is_correct": false}},
    ...
  ],
  "explanation": "...",
  "citations": [
    {{"source_name": "eTG", "page_number": 123, ...}},
    ...
  ]
}}
"""

    message = anthropic.messages.create(
        model="claude-3-5-sonnet-20250116",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    regenerated = json.loads(message.content[0].text)
    return regenerated

async def main():
    # Load items needing remediation
    with open("flagged_mcqs_for_review.json") as f:
        flagged = json.load(f)

    with open("clinical_reviews.json") as f:
        reviews = json.load(f)

    # Prioritize critical issues
    critical = [
        mcq for mcq in flagged
        if reviews.get(mcq["id"], {}).get("verdict") == "fail"
    ]

    print(f"Remediating {len(critical)} critical MCQs...")

    for mcq in tqdm(critical):
        issue = reviews[mcq["id"]]["comments"]
        regenerated = await regenerate_mcq(mcq, issue)

        # Save updated MCQ
        update_mcq_in_database(mcq["id"], regenerated)

    print("✅ Critical issues remediated")

if __name__ == "__main__":
    asyncio.run(main())
```

**Checklist:**
- [ ] Load flagged items (low confidence + non-compliant + failed reviews)
- [ ] Prioritize: Critical (failed review) > High (non-compliant) > Medium (low confidence)
- [ ] Regenerate critical items (25 MCQs, ~2 hours with Claude)
- [ ] Regenerate high-priority items (720 MCQs, ~24 hours)
- [ ] Medium items: Flag as "Citation verification in progress" (defer to Phase 1)
- [ ] Update database with corrected MCQs
- [ ] Re-run validation on corrected items (verify fixes)

---

## 📅 WEEK 4: COPYRIGHT CLEARANCE

### Day 1-2: Copyright Risk Assessment

**Legal Review Template:**

```markdown
# Copyright Risk Assessment - irStudy Platform

## Date: 2026-02-06
## Prepared by: [Your Name]
## Reviewed by: [IP Lawyer Name] (optional)

### Source Materials Used

| Source | Copyright Holder | Copyright Status | Risk Level |
|--------|-----------------|------------------|------------|
| eTG Complete | Therapeutic Guidelines Ltd | © Subscription required | MEDIUM |
| AMH 2024 | AMH Pty Ltd | © Subscription required | MEDIUM |
| RACGP Guidelines | RACGP | CC BY-NC-SA | LOW |
| NSW Health Guidelines | NSW Government | Public domain | LOW |
| Cochrane Reviews | Cochrane | CC BY | LOW |
| StatPearls | US Government | Public domain | LOW |
| AMC Handbook | AMC | © All rights reserved | HIGH |
| Talley & O'Connor | Elsevier | © All rights reserved | HIGH |
| Oxford Handbook | Oxford UP | © All rights reserved | HIGH |

### Usage Analysis

**How We Use Sources:**
1. Extract text chunks (2-3 paragraphs per chunk)
2. Store in vector database (Qdrant)
3. Use for RAG (retrieval-augmented generation)
4. Generate MCQs based on retrieved information
5. Cite sources in MCQ explanations

**Are We Copying Verbatim?**
- No, MCQs are new creations
- Explanations paraphrase source material
- Citations reference but don't quote extensively

**Fair Dealing Analysis (Australia):**

1. **Purpose**: Educational (medical exam preparation) ✓
2. **Nature**: Factual medical information (not creative works) ✓
3. **Amount**: Small portions (<0.1% of each book) ✓
4. **Effect on Market**: Different product (exam prep vs textbook) ✓

**Risk Assessment:**
- **LOW RISK:** RACGP, NSW Health, Cochrane, StatPearls (open licenses)
- **MEDIUM RISK:** eTG, AMH (subscription services, fair use arguable)
- **HIGH RISK:** AMC Handbook, Talley, Oxford (commercial textbooks)

### Recommendation

**Option 1: Fair Use Defense (Risky)**
- Consult IP lawyer ($3K-5K)
- Document fair dealing rationale
- Accept risk of potential DMCA takedown

**Option 2: Licensing Agreements (Expensive)**
- Contact publishers (Elsevier, Oxford UP, AMC)
- Negotiate fees ($5K-20K/year)
- Get written permission

**Option 3: Source Replacement (Recommended)**
- Remove high-risk sources (AMC Handbook, Talley, Oxford)
- Keep safe sources (eTG, AMH, RACGP, StatPearls)
- Regenerate affected MCQs (~5,000 MCQs)
- Timeline: 3-5 days
- Cost: $0

**Legal Opinion Needed:**
□ Yes - Seek IP lawyer consultation
□ No - Proceed with Option 3 (source replacement)
```

**Checklist:**
- [ ] List all source materials in RAG database
- [ ] Classify each by copyright status
- [ ] Analyze usage (verbatim vs paraphrasing)
- [ ] Document fair dealing rationale
- [ ] Decide: Fair use defense, licensing, or source replacement
- [ ] If lawyer needed: Schedule consultation ($3K-5K)

---

### Day 3-5: Copyright Clearance Execution

**RECOMMENDED: Option 3 - Source Replacement**

```bash
# Day 3: Audit RAG database
python scripts/audit_rag_sources.py

# Output:
# High-risk sources: 13,500 chunks
# - AMC Handbook: 4,200 chunks
# - Talley & O'Connor: 5,500 chunks
# - Oxford Handbook: 3,800 chunks

# Day 4: Remove high-risk sources
python scripts/remove_risky_sources.py \
  --sources "amc_handbook,talley_oconnor,oxford_handbook" \
  --backup-first

# Backup created: qdrant_backup_20260206.tar.gz
# Removed: 13,500 chunks
# Remaining: 29,147 chunks (safe sources)

# Day 5: Regenerate affected MCQs
python scripts/regenerate_mcqs_safe_sources.py \
  --input mcqs_using_risky_sources.json \
  --safe-sources "etg,amh,racgp,statpearls,cochrane,nsw_health" \
  --output regenerated_mcqs.json

# Regenerating 5,247 MCQs (affected by removed sources)...
# Using Claude 3.5 Sonnet...
# Estimated time: 18-24 hours
# Cost estimate: ~$150 (Claude API)

# Progress: 1/5247 [00:00<18:32, 4.71mcqs/s]
```

**Verification:**

```python
# scripts/verify_copyright_clearance.py
def verify_no_risky_sources():
    """Verify all high-risk sources removed."""
    risky_sources = ["AMC Handbook", "Talley", "Oxford"]

    # Check Qdrant
    all_chunks = qdrant.scroll(collection_name="medical_knowledge")
    for chunk in all_chunks:
        source = chunk.payload.get("source_name", "")
        for risky in risky_sources:
            if risky in source:
                raise ValueError(f"High-risk source still in database: {source}")

    # Check MCQs
    mcqs = load_all_mcqs()
    for mcq in mcqs:
        for citation in mcq.get("citations", []):
            source = citation.get("source_name", "")
            for risky in risky_sources:
                if risky in source:
                    raise ValueError(f"High-risk citation in MCQ {mcq['id']}: {source}")

    print("✅ Copyright clearance verified - no high-risk sources")

verify_no_risky_sources()
```

**Legal Documentation:**

```markdown
# Copyright Compliance Certificate

**Date:** 2026-02-06
**Platform:** irStudy Medical Education

## Sources Used (Post-Clearance)

All content sources are either:
1. **Open license:** RACGP (CC BY-NC-SA), Cochrane (CC BY)
2. **Public domain:** NSW Health, StatPearls (US Govt)
3. **Licensed subscription:** eTG Complete, AMH (institutional subscriptions purchased)

## High-Risk Sources Removed

The following copyrighted sources were identified and **removed** from the platform:
- AMC Handbook of Clinical Assessment (4,200 chunks removed)
- Talley & O'Connor Clinical Examination (5,500 chunks removed)
- Oxford Handbook of Emergency Medicine (3,800 chunks removed)

Affected MCQs (5,247) were regenerated using only safe sources.

## Compliance Statement

As of 2026-02-06, the irStudy platform uses only:
- Licensed content (with valid subscriptions)
- Open-licensed content (RACGP, Cochrane)
- Public domain content (NSW Health, StatPearls)

No copyrighted textbooks are used without permission.

**Verified by:** [Your Name], Platform Owner
**Legal Review:** [Optional: IP Lawyer Name]
```

**Checklist:**
- [ ] Backup Qdrant database (before removing anything)
- [ ] Remove high-risk sources (13,500 chunks)
- [ ] Identify affected MCQs (5,247 MCQs)
- [ ] Regenerate affected MCQs using safe sources
- [ ] Re-validate regenerated MCQs (RAG + Australian compliance)
- [ ] Verify: No high-risk sources remain (run verification script)
- [ ] Document: Copyright compliance certificate
- [ ] Store: Backup and documentation in secure location

---

## 🎯 PHASE 0 COMPLETION CHECKLIST

### Week 1: Security Foundation
- [ ] Clerk authentication integrated (backend + frontend)
- [ ] Stripe payments configured (products created, webhooks working)
- [ ] Database security (RLS enabled, encryption at rest, backups)
- [ ] Pre-commit hooks (git-secrets, detect-secrets)
- [ ] Monitoring (Sentry, CloudWatch, UptimeRobot)

### Week 2: Automated Validation
- [ ] RAG citation validation (54,000 facts checked)
- [ ] Citation report generated (>85% confidence target)
- [ ] Australian compliance check (18,000 MCQs)
- [ ] Compliance report generated (>95% compliant target)
- [ ] Flagged items exported for review

### Week 3: Manual Review & Remediation
- [ ] 500 MCQs sampled (stratified by specialty)
- [ ] Medical professional review complete
- [ ] Clinical review report (>95% pass rate)
- [ ] Critical issues remediated (failed MCQs regenerated)
- [ ] High-priority issues fixed (non-compliant MCQs corrected)

### Week 4: Copyright Clearance
- [ ] Copyright risk assessment complete
- [ ] Legal consultation (if needed)
- [ ] High-risk sources removed (Option 3)
- [ ] Affected MCQs regenerated (5,247 MCQs)
- [ ] Copyright compliance certificate issued
- [ ] Verification: No risky sources remain

### Final Deliverables
- [ ] ✅ Secure authentication & payment infrastructure
- [ ] ✅ Validated content database (18,000 MCQs ready)
- [ ] ✅ Citation validation report (>85% confidence)
- [ ] ✅ Australian compliance report (>95% compliant)
- [ ] ✅ Clinical accuracy certification (>95% pass rate)
- [ ] ✅ Copyright clearance (legal risk mitigated)
- [ ] ✅ All validation reports archived
- [ ] ✅ Ready for Phase 1 (Mobile PWA development)

---

## 📊 BUDGET TRACKER

| Item | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| Medical reviewer (20h × $100/hr) | $2,000 | | Clinical review |
| Legal consultation (IP lawyer) | $3,000 | | Optional |
| Claude API (regeneration) | $150 | | 5,247 MCQs |
| Infrastructure (Clerk, Stripe) | $200 | | Monthly costs |
| Developer time (160h × $50/hr) | $8,000 | | 1 FTE, 4 weeks |
| **TOTAL** | **$13,350** | | Phase 0 budget |

---

## 🚀 NEXT STEPS

**After Phase 0 Completion:**
1. Review all deliverables with team
2. Make go/no-go decision for Phase 1
3. If go: Begin Phase 1 Week 5 (Mobile PWA development)
4. If no-go: Address any remaining issues

**Phase 1 Preview (Weeks 5-10):**
- React + Vite + TypeScript setup
- PWA service worker + offline mode
- MCQ practice interface with citations
- RAG-powered quick search
- Free tier launch (200 MCQs)

---

**Document Status:** COMPLETE
**Version:** 1.0
**Last Updated:** 2026-02-06
**Maintained by:** Development Team
