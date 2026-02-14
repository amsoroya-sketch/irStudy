# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_002 - Question Management CRUD (6-8 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/backend

# Create API endpoints for MCQ and OSCE management
mkdir -p src/api/v1/mcqs src/api/v1/osces tests/api/v1

# Create MCQ router
cat > src/api/v1/mcqs/router.py <<'EOF'
# MCQ endpoints will be implemented here
EOF

# Create OSCE router
cat > src/api/v1/osces/router.py <<'EOF'
# OSCE endpoints will be implemented here
EOF

# Run database to verify connection
python -c "from src.db.session import SessionLocal; db = SessionLocal(); print('✅ Database connected')"
```

**DO NOT**:
- ❌ Ask "Would you like me to create the MCQ endpoints first?"
- ❌ Ask "Should I implement validation for Australian drug names?"
- ❌ Wait for approval before creating endpoints
- ❌ Ask "Which HTTP methods should I use?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 1
- **Day:** 3-4 (Feb 9-10, 2026)
- **Duration:** 6-8 hours
- **Priority:** P0-Critical (blocks frontend development)
- **Dependencies:** TASK_001 (security audit must be complete)
- **Owner:** general-purpose agent (Python/FastAPI)
- **Status:** 🟡 Not Started
- **Blocks:** TASK_004 (User Progress), TASK_006 (Quiz Interface), TASK_011 (RAG Explanation)

---

## 🎯 Objectives

1. **Implement MCQ CRUD endpoints** (GET /random, GET /{id}, POST /submit-answer, GET /explanations)
2. **Implement OSCE CRUD endpoints** (GET /random, GET /{id}, POST /complete-station)
3. **Validate Australian drug names** (paracetamol NOT acetaminophen) on all question content
4. **Verify citations** reference Australian guidelines (eTG, PBS, AMH, AHPRA)
5. **Achieve 100% test coverage** on all endpoints with pytest
6. **Ensure API response time <200ms** (95th percentile)

---

## 🚨 Constraints (READ FIRST)

**From `/home/dev/Development/irStudy/constraints/01-medical-accuracy.md` and `/home/dev/Development/irStudy/constraints/13-ralph-execution.md`:**

❌ **NEVER:**
- Allow American drug names in questions (acetaminophen, albuterol, epinephrine)
- Return questions without citations
- Skip input validation (use Pydantic schemas for ALL endpoints)
- Use raw SQL queries (SQLAlchemy ORM ONLY)
- Return user IDs or sensitive data in responses
- Allow SQL injection vectors

✅ **ALWAYS:**
- Use Australian drug names (paracetamol, salbutamol, adrenaline)
- Validate all citations reference Australian sources (eTG, PBS, AMH, AHPRA)
- Use Pydantic schemas for request/response validation
- Use SQLAlchemy ORM for database queries
- Implement rate limiting (60 requests/minute for authenticated users)
- Return only necessary data (follow principle of least privilege)
- Hash or truncate sensitive identifiers in logs

**Australian Medical Context:**
- ✅ REQUIRED: eTG (Therapeutic Guidelines), PBS (Pharmaceutical Benefits Scheme), AMH (Australian Medicines Handbook), AHPRA (Australian Health Practitioner Regulation Agency)
- ❌ FORBIDDEN: American sources without Australian context, non-Australian drug names

**API Performance:**
- Response time target: <200ms (95th percentile)
- Database queries: <100ms per query
- Use database indexing on frequently queried fields (specialty, difficulty, topic)

---

## 📝 Implementation Guide

### Step 1: Create Database Models (if not exist) (30 minutes)

```bash
cd /home/dev/Development/irStudy/backend

# Verify MCQ model exists
python -c "from src.db.models.mcq import MCQ; print('✅ MCQ model exists')" || echo "❌ Create MCQ model"

# Verify OSCE model exists
python -c "from src.db.models.osce import OSCE; print('✅ OSCE model exists')" || echo "❌ Create OSCE model"

# Check existing MCQ count
python <<EOF
from src.db.session import SessionLocal
from src.db.models.mcq import MCQ

db = SessionLocal()
count = db.query(MCQ).count()
print(f"📊 Current MCQ count: {count} (expected: 1,208)")
db.close()
EOF
```

**Expected Output:**
```
✅ MCQ model exists
✅ OSCE model exists
📊 Current MCQ count: 1208 (expected: 1,208)
```

---

### Step 2: Create Pydantic Schemas (1 hour)

Create request/response schemas with Australian validation:

```bash
cd /home/dev/Development/irStudy/backend

mkdir -p src/api/v1/schemas

cat > src/api/v1/schemas/mcq.py <<'EOF'
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

# Australian drug names validation list
AUSTRALIAN_DRUG_NAMES = [
    "paracetamol", "salbutamol", "adrenaline", "lignocaine",
    # Add more Australian drug names as needed
]

FORBIDDEN_DRUG_NAMES = [
    "acetaminophen", "albuterol", "epinephrine", "lidocaine",
    # American equivalents that should be rejected
]

class MCQBase(BaseModel):
    question_text: str = Field(..., min_length=10, max_length=2000)
    option_a: str = Field(..., min_length=1, max_length=500)
    option_b: str = Field(..., min_length=1, max_length=500)
    option_c: str = Field(..., min_length=1, max_length=500)
    option_d: str = Field(..., min_length=1, max_length=500)
    option_e: Optional[str] = Field(None, max_length=500)
    correct_answer: str = Field(..., regex="^[A-E]$")
    explanation: str = Field(..., min_length=10, max_length=3000)
    specialty: str = Field(..., max_length=100)
    topic: str = Field(..., max_length=200)
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")

    @validator("question_text", "explanation", "option_a", "option_b", "option_c", "option_d", "option_e")
    def validate_australian_drugs(cls, v):
        """Reject American drug names"""
        if v is None:
            return v
        v_lower = v.lower()
        for forbidden in FORBIDDEN_DRUG_NAMES:
            if forbidden in v_lower:
                raise ValueError(f"American drug name '{forbidden}' not allowed. Use Australian equivalent.")
        return v

class MCQResponse(MCQBase):
    id: int
    citations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class MCQSubmitAnswer(BaseModel):
    mcq_id: int
    selected_answer: str = Field(..., regex="^[A-E]$")
    time_taken_seconds: int = Field(..., ge=0, le=600)  # Max 10 minutes

class MCQSubmitResponse(BaseModel):
    correct: bool
    correct_answer: str
    explanation: str
    citations: List[str]
EOF

cat > src/api/v1/schemas/osce.py <<'EOF'
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class OSCEBase(BaseModel):
    scenario: str = Field(..., min_length=50, max_length=5000)
    station_type: str = Field(..., max_length=100)  # e.g., "History Taking", "Examination"
    specialty: str = Field(..., max_length=100)
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")
    marking_criteria: List[str] = Field(..., min_items=5, max_items=20)
    time_limit_minutes: int = Field(..., ge=5, le=20)

class OSCEResponse(OSCEBase):
    id: int
    citations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class OSCECompleteStation(BaseModel):
    osce_id: int
    performance_notes: str = Field(..., min_length=10, max_length=2000)
    time_taken_seconds: int = Field(..., ge=0, le=1200)  # Max 20 minutes

class OSCECompleteResponse(BaseModel):
    osce_id: int
    marking_criteria: List[str]
    citations: List[str]
EOF

echo "✅ Pydantic schemas created"
```

---

### Step 3: Create MCQ Endpoints (2 hours)

```bash
cd /home/dev/Development/irStudy/backend

cat > src/api/v1/mcqs/router.py <<'EOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.db.session import get_db
from src.db.models.mcq import MCQ
from src.db.models.mcq_attempt import MCQAttempt
from src.api.v1.schemas.mcq import MCQResponse, MCQSubmitAnswer, MCQSubmitResponse
from src.auth.dependencies import get_current_user
from src.db.models.user import User
import random
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1/mcqs", tags=["MCQs"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/random", response_model=MCQResponse)
@limiter.limit("60/minute")
async def get_random_mcq(
    specialty: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a random MCQ, optionally filtered by specialty and difficulty.

    Rate limit: 60 requests/minute (authenticated users)
    Response time target: <200ms
    """
    query = db.query(MCQ)

    if specialty:
        query = query.filter(MCQ.specialty == specialty)
    if difficulty:
        query = query.filter(MCQ.difficulty == difficulty)

    # Get total count for random selection
    total_count = query.count()
    if total_count == 0:
        raise HTTPException(status_code=404, detail="No MCQs found with specified filters")

    # Select random offset
    random_offset = random.randint(0, total_count - 1)
    mcq = query.offset(random_offset).first()

    return mcq

@router.get("/{mcq_id}", response_model=MCQResponse)
@limiter.limit("60/minute")
async def get_mcq_by_id(
    mcq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific MCQ by ID.

    Rate limit: 60 requests/minute (authenticated users)
    """
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()
    if not mcq:
        raise HTTPException(status_code=404, detail=f"MCQ {mcq_id} not found")

    return mcq

@router.post("/submit-answer", response_model=MCQSubmitResponse)
@limiter.limit("60/minute")
async def submit_mcq_answer(
    submission: MCQSubmitAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit an answer to an MCQ and get instant feedback.

    Rate limit: 60 requests/minute (authenticated users)
    Creates an MCQAttempt record for progress tracking.
    """
    # Fetch MCQ
    mcq = db.query(MCQ).filter(MCQ.id == submission.mcq_id).first()
    if not mcq:
        raise HTTPException(status_code=404, detail=f"MCQ {submission.mcq_id} not found")

    # Check if correct
    is_correct = submission.selected_answer == mcq.correct_answer

    # Record attempt
    attempt = MCQAttempt(
        user_id=current_user.id,
        mcq_id=mcq.id,
        selected_answer=submission.selected_answer,
        is_correct=is_correct,
        time_taken_seconds=submission.time_taken_seconds
    )
    db.add(attempt)
    db.commit()

    return MCQSubmitResponse(
        correct=is_correct,
        correct_answer=mcq.correct_answer,
        explanation=mcq.explanation,
        citations=mcq.citations or []
    )

@router.get("/{mcq_id}/explanations", response_model=dict)
@limiter.limit("60/minute")
async def get_mcq_explanations(
    mcq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed explanations and citations for an MCQ.

    Rate limit: 60 requests/minute (authenticated users)
    """
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()
    if not mcq:
        raise HTTPException(status_code=404, detail=f"MCQ {mcq_id} not found")

    return {
        "mcq_id": mcq.id,
        "explanation": mcq.explanation,
        "citations": mcq.citations or [],
        "correct_answer": mcq.correct_answer,
        "difficulty": mcq.difficulty,
        "specialty": mcq.specialty
    }
EOF

echo "✅ MCQ endpoints created"
```

---

### Step 4: Create OSCE Endpoints (1.5 hours)

```bash
cd /home/dev/Development/irStudy/backend

cat > src/api/v1/osces/router.py <<'EOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.db.session import get_db
from src.db.models.osce import OSCE
from src.db.models.osce_attempt import OSCEAttempt
from src.api.v1.schemas.osce import OSCEResponse, OSCECompleteStation, OSCECompleteResponse
from src.auth.dependencies import get_current_user
from src.db.models.user import User
import random
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1/osces", tags=["OSCEs"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/random", response_model=OSCEResponse)
@limiter.limit("60/minute")
async def get_random_osce(
    specialty: Optional[str] = Query(None),
    station_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a random OSCE station, optionally filtered.

    Rate limit: 60 requests/minute (authenticated users)
    Response time target: <200ms
    """
    query = db.query(OSCE)

    if specialty:
        query = query.filter(OSCE.specialty == specialty)
    if station_type:
        query = query.filter(OSCE.station_type == station_type)
    if difficulty:
        query = query.filter(OSCE.difficulty == difficulty)

    total_count = query.count()
    if total_count == 0:
        raise HTTPException(status_code=404, detail="No OSCE stations found with specified filters")

    random_offset = random.randint(0, total_count - 1)
    osce = query.offset(random_offset).first()

    return osce

@router.get("/{osce_id}", response_model=OSCEResponse)
@limiter.limit("60/minute")
async def get_osce_by_id(
    osce_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific OSCE station by ID.

    Rate limit: 60 requests/minute (authenticated users)
    """
    osce = db.query(OSCE).filter(OSCE.id == osce_id).first()
    if not osce:
        raise HTTPException(status_code=404, detail=f"OSCE {osce_id} not found")

    return osce

@router.post("/complete-station", response_model=OSCECompleteResponse)
@limiter.limit("60/minute")
async def complete_osce_station(
    completion: OSCECompleteStation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete an OSCE station and record performance.

    Rate limit: 60 requests/minute (authenticated users)
    Creates an OSCEAttempt record for progress tracking.
    """
    osce = db.query(OSCE).filter(OSCE.id == completion.osce_id).first()
    if not osce:
        raise HTTPException(status_code=404, detail=f"OSCE {completion.osce_id} not found")

    # Record attempt
    attempt = OSCEAttempt(
        user_id=current_user.id,
        osce_id=osce.id,
        performance_notes=completion.performance_notes,
        time_taken_seconds=completion.time_taken_seconds
    )
    db.add(attempt)
    db.commit()

    return OSCECompleteResponse(
        osce_id=osce.id,
        marking_criteria=osce.marking_criteria or [],
        citations=osce.citations or []
    )
EOF

echo "✅ OSCE endpoints created"
```

---

### Step 5: Register Routers in Main App (15 minutes)

```bash
cd /home/dev/Development/irStudy/backend

# Add routers to main.py
python <<'EOF'
import re

with open("src/main.py", "r") as f:
    content = f.read()

# Check if routers already registered
if "mcqs.router" in content:
    print("✅ MCQ router already registered")
else:
    # Add import
    import_line = "from src.api.v1.mcqs import router as mcqs_router\n"
    content = re.sub(r"(from fastapi import FastAPI)", f"\\1\n{import_line}", content)

    # Add router registration
    router_line = "app.include_router(mcqs_router)\n"
    content = re.sub(r"(app = FastAPI\(\))", f"\\1\n\n{router_line}", content)

    print("✅ MCQ router added")

if "osces.router" in content:
    print("✅ OSCE router already registered")
else:
    # Add import
    import_line = "from src.api.v1.osces import router as osces_router\n"
    content = re.sub(r"(from fastapi import FastAPI)", f"\\1\n{import_line}", content)

    # Add router registration
    router_line = "app.include_router(osces_router)\n"
    content = re.sub(r"(app = FastAPI\(\))", f"\\1\n\n{router_line}", content)

    print("✅ OSCE router added")

with open("src/main.py", "w") as f:
    f.write(content)
EOF
```

---

### Step 6: Create Test Suite (2 hours)

```bash
cd /home/dev/Development/irStudy/backend

mkdir -p tests/api/v1

cat > tests/api/v1/test_mcqs.py <<'EOF'
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.session import get_db
from src.db.models.user import User
from src.auth.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    token = create_access_token(data={"sub": "test_user@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_get_random_mcq(auth_headers):
    """Test GET /api/v1/mcqs/random endpoint"""
    response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "question_text" in data
    assert "correct_answer" in data
    assert "citations" in data
    assert len(data["citations"]) >= 3  # Must have at least 3 citations

def test_get_random_mcq_with_filters(auth_headers):
    """Test GET /api/v1/mcqs/random with specialty and difficulty filters"""
    response = client.get(
        "/api/v1/mcqs/random?specialty=Cardiology&difficulty=medium",
        headers=auth_headers
    )
    assert response.status_code in [200, 404]  # 404 if no MCQs match filter
    if response.status_code == 200:
        data = response.json()
        assert data["specialty"] == "Cardiology"
        assert data["difficulty"] == "medium"

def test_get_mcq_by_id(auth_headers):
    """Test GET /api/v1/mcqs/{id} endpoint"""
    # First get a random MCQ to get a valid ID
    random_response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    assert random_response.status_code == 200
    mcq_id = random_response.json()["id"]

    # Now get by ID
    response = client.get(f"/api/v1/mcqs/{mcq_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mcq_id

def test_get_mcq_invalid_id(auth_headers):
    """Test GET /api/v1/mcqs/{id} with invalid ID"""
    response = client.get("/api/v1/mcqs/999999", headers=auth_headers)
    assert response.status_code == 404

def test_submit_mcq_answer_correct(auth_headers):
    """Test POST /api/v1/mcqs/submit-answer with correct answer"""
    # Get random MCQ
    mcq_response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    mcq = mcq_response.json()

    # Submit correct answer
    submission = {
        "mcq_id": mcq["id"],
        "selected_answer": mcq["correct_answer"],
        "time_taken_seconds": 60
    }
    response = client.post("/api/v1/mcqs/submit-answer", json=submission, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert data["explanation"] is not None
    assert len(data["citations"]) >= 3

def test_submit_mcq_answer_incorrect(auth_headers):
    """Test POST /api/v1/mcqs/submit-answer with incorrect answer"""
    # Get random MCQ
    mcq_response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    mcq = mcq_response.json()

    # Submit wrong answer (different from correct)
    wrong_answer = "A" if mcq["correct_answer"] != "A" else "B"
    submission = {
        "mcq_id": mcq["id"],
        "selected_answer": wrong_answer,
        "time_taken_seconds": 45
    }
    response = client.post("/api/v1/mcqs/submit-answer", json=submission, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["correct_answer"] == mcq["correct_answer"]

def test_get_mcq_explanations(auth_headers):
    """Test GET /api/v1/mcqs/{id}/explanations endpoint"""
    # Get random MCQ
    mcq_response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    mcq_id = mcq_response.json()["id"]

    # Get explanations
    response = client.get(f"/api/v1/mcqs/{mcq_id}/explanations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert "citations" in data
    assert "correct_answer" in data
    assert len(data["citations"]) >= 3

def test_australian_drug_name_validation():
    """Test that American drug names are rejected"""
    # This would be tested during MCQ creation, not retrieval
    # Placeholder for validation test
    pass

def test_api_response_time(auth_headers):
    """Test that API response time is <200ms"""
    import time
    start = time.time()
    response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    elapsed = (time.time() - start) * 1000  # Convert to milliseconds

    assert response.status_code == 200
    assert elapsed < 200, f"API response time {elapsed}ms exceeds 200ms threshold"
EOF

cat > tests/api/v1/test_osces.py <<'EOF'
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    token = create_access_token(data={"sub": "test_user@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_get_random_osce(auth_headers):
    """Test GET /api/v1/osces/random endpoint"""
    response = client.get("/api/v1/osces/random", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "scenario" in data
    assert "marking_criteria" in data
    assert "citations" in data

def test_get_osce_by_id(auth_headers):
    """Test GET /api/v1/osces/{id} endpoint"""
    # Get random OSCE first
    random_response = client.get("/api/v1/osces/random", headers=auth_headers)
    osce_id = random_response.json()["id"]

    # Get by ID
    response = client.get(f"/api/v1/osces/{osce_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == osce_id

def test_complete_osce_station(auth_headers):
    """Test POST /api/v1/osces/complete-station endpoint"""
    # Get random OSCE
    osce_response = client.get("/api/v1/osces/random", headers=auth_headers)
    osce_id = osce_response.json()["id"]

    # Complete station
    completion = {
        "osce_id": osce_id,
        "performance_notes": "Completed history taking with patient. Asked about onset, duration, severity.",
        "time_taken_seconds": 480
    }
    response = client.post("/api/v1/osces/complete-station", json=completion, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["osce_id"] == osce_id
    assert "marking_criteria" in data
    assert "citations" in data
EOF

echo "✅ Test suite created"
```

---

### Step 7: Run Tests and Verify (30 minutes)

```bash
cd /home/dev/Development/irStudy/backend

# Run all MCQ tests
pytest tests/api/v1/test_mcqs.py -v

# Run all OSCE tests
pytest tests/api/v1/test_osces.py -v

# Run with coverage
pytest tests/api/v1/ --cov=src/api/v1/mcqs --cov=src/api/v1/osces --cov-report=term-missing

# Expected output: 100% test pass rate, >70% code coverage
```

**Verify API response time:**

```bash
# Benchmark API endpoints
python <<'EOF'
import requests
import time

# Assuming dev server running on localhost:8000
BASE_URL = "http://localhost:8000"

# Create test token (replace with actual token generation)
token = "test_token_here"
headers = {"Authorization": f"Bearer {token}"}

# Test MCQ random endpoint
times = []
for i in range(10):
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/v1/mcqs/random", headers=headers)
    elapsed = (time.time() - start) * 1000
    times.append(elapsed)
    print(f"Request {i+1}: {elapsed:.2f}ms")

avg_time = sum(times) / len(times)
p95_time = sorted(times)[int(len(times) * 0.95)]

print(f"\nAverage response time: {avg_time:.2f}ms")
print(f"95th percentile: {p95_time:.2f}ms")

if p95_time < 200:
    print("✅ Performance target met (<200ms)")
else:
    print(f"❌ Performance target missed ({p95_time:.2f}ms > 200ms)")
EOF
```

---

## ✅ Validation Checklist

**Run these commands to verify completion:**

```bash
cd /home/dev/Development/irStudy/backend

# 1. Verify MCQ endpoints exist
[ -f src/api/v1/mcqs/router.py ] && echo "✅ MCQ endpoints: EXISTS" || echo "❌ MCQ endpoints: MISSING"

# 2. Verify OSCE endpoints exist
[ -f src/api/v1/osces/router.py ] && echo "✅ OSCE endpoints: EXISTS" || echo "❌ OSCE endpoints: MISSING"

# 3. Verify Pydantic schemas exist
[ -f src/api/v1/schemas/mcq.py ] && echo "✅ MCQ schemas: EXISTS" || echo "❌ MCQ schemas: MISSING"
[ -f src/api/v1/schemas/osce.py ] && echo "✅ OSCE schemas: EXISTS" || echo "❌ OSCE schemas: MISSING"

# 4. Verify Australian drug name validation
grep -q "FORBIDDEN_DRUG_NAMES" src/api/v1/schemas/mcq.py && echo "✅ Drug validation: CONFIGURED" || echo "❌ Drug validation: MISSING"

# 5. Verify tests exist
[ -f tests/api/v1/test_mcqs.py ] && echo "✅ MCQ tests: EXISTS" || echo "❌ MCQ tests: MISSING"
[ -f tests/api/v1/test_osces.py ] && echo "✅ OSCE tests: EXISTS" || echo "❌ OSCE tests: MISSING"

# 6. Run tests and verify 100% pass rate
pytest tests/api/v1/ -v && echo "✅ Tests: 100% PASS" || echo "❌ Tests: FAILED"

# 7. Verify routers registered
grep -q "mcqs_router" src/main.py && echo "✅ MCQ router: REGISTERED" || echo "❌ MCQ router: NOT REGISTERED"
grep -q "osces_router" src/main.py && echo "✅ OSCE router: REGISTERED" || echo "❌ OSCE router: NOT REGISTERED"

# 8. Verify API response time <200ms
# (Run manual benchmark script from Step 7)
```

**Expected Output:**
```
✅ MCQ endpoints: EXISTS
✅ OSCE endpoints: EXISTS
✅ MCQ schemas: EXISTS
✅ OSCE schemas: EXISTS
✅ Drug validation: CONFIGURED
✅ MCQ tests: EXISTS
✅ OSCE tests: EXISTS
✅ Tests: 100% PASS
✅ MCQ router: REGISTERED
✅ OSCE router: REGISTERED
```

---

## 🎯 Success Criteria

**This task is DONE when ALL of these are true:**

1. ✅ MCQ endpoints implemented: GET /random, GET /{id}, POST /submit-answer, GET /explanations
2. ✅ OSCE endpoints implemented: GET /random, GET /{id}, POST /complete-station
3. ✅ Australian drug name validation operational (rejects acetaminophen, albuterol, epinephrine)
4. ✅ Citation verification: All responses include ≥3 Australian citations (eTG, PBS, AMH, AHPRA)
5. ✅ Test suite complete: pytest shows 100% pass rate with >70% code coverage
6. ✅ API response time <200ms verified (95th percentile benchmark)
7. ✅ Pydantic schemas validated on all endpoints (input validation working)
8. ✅ Rate limiting configured (60 req/min for authenticated users)

---

## 🚦 Quality Gates

| Gate | Criteria | Status |
|------|----------|--------|
| **Gate 1: Schemas** | Pydantic schemas created with Australian validation | ⏳ Pending |
| **Gate 2: MCQ Endpoints** | All 4 MCQ endpoints operational | ⏳ Pending |
| **Gate 3: OSCE Endpoints** | All 3 OSCE endpoints operational | ⏳ Pending |
| **Gate 4: Tests** | 100% test pass rate, >70% coverage | ⏳ Pending |
| **Gate 5: Performance** | API <200ms (95th percentile) | ⏳ Pending |
| **Gate 6: Validation** | Australian drug names enforced | ⏳ Pending |

**All gates must be ✅ before proceeding to TASK_003.**

---

## 🔄 When Complete

```bash
cd /home/dev/Development/irStudy

# 1. Update @fix_plan.md
sed -i 's/TASK_002.*TODO/TASK_002: ✅ DONE/' @fix_plan.md

# 2. Commit changes
git add .
git commit -m "feat(api): Complete TASK_002 Question Management CRUD - MCQ and OSCE endpoints

- MCQ endpoints: GET /random, GET /{id}, POST /submit-answer, GET /explanations
- OSCE endpoints: GET /random, GET /{id}, POST /complete-station
- Australian drug name validation (paracetamol NOT acetaminophen)
- Citation verification (≥3 Australian sources per question)
- Pydantic schemas with input validation
- Rate limiting: 60 req/min (authenticated users)
- Test suite: 100% pass rate, >70% coverage
- API response time: <200ms (95th percentile)

Deliverables:
- backend/src/api/v1/mcqs/router.py
- backend/src/api/v1/osces/router.py
- backend/src/api/v1/schemas/mcq.py
- backend/src/api/v1/schemas/osce.py
- backend/tests/api/v1/test_mcqs.py
- backend/tests/api/v1/test_osces.py

Quality Gates: 6/6 passed ✅
Blocks: TASK_004, TASK_006, TASK_011 now unblocked

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 3. Move to next task
echo "✅ TASK_002 complete. Starting TASK_003..."
echo "Next PRD: /home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_003_STUDY_CARD_SYSTEM.md"
```

---

## ⚠️ Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **API response time >200ms** | Medium | High | Use database indexing on specialty, difficulty, topic fields |
| **Australian drug validation false positives** | Low | Medium | Maintain comprehensive list in `FORBIDDEN_DRUG_NAMES` |
| **Test failures in CI/CD** | Low | High | Run pytest locally before commit, fix all failures |
| **Missing citations in legacy data** | Medium | Medium | Add data migration script to add citations to existing MCQs |

---

## 📚 Resources Required

**Tools:**
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Pydantic (data validation)
- pytest (testing)
- slowapi (rate limiting)

**Documentation:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/usage/validators/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)

**Access:**
- Backend codebase read/write
- Database access (PostgreSQL @ localhost:5433)
- Test database (for pytest)

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
**Depends On:** TASK_001 (security audit)
**Blocks:** TASK_004 (User Progress), TASK_006 (Quiz Interface), TASK_011 (RAG Explanation)

---

**Full Task Specification:** [TASK_002_QUESTION_MANAGEMENT_CRUD.md](../TASK_002_QUESTION_MANAGEMENT_CRUD.md)
**Constraints:** [constraints/README.md](/home/dev/Development/irStudy/constraints/README.md)
**Ralph Execution Guide:** [constraints/13-ralph-execution.md](/home/dev/Development/irStudy/constraints/13-ralph-execution.md)
