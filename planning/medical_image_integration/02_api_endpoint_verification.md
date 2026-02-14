# Task 02: API Endpoint Verification

**Duration:** 2 hours
**Priority:** P0 (Critical Path)
**Dependencies:** Task 01 (Database Seed Script)
**Output:** Verified API endpoints + Test suite

---

## Objective

Verify all FastAPI endpoints correctly serve MCQ and OSCE data from PostgreSQL database after seeding, ensuring proper filtering, pagination, and data structure compliance.

---

## Scope

### In Scope
- Test all MCQ endpoints (`/api/v1/mcqs/*`)
- Test all OSCE endpoints (`/api/v1/osces/*`)
- Verify filtering by specialty, difficulty, tags
- Test pagination and limits
- Validate response schemas
- Performance benchmarking (<100ms response time)
- Error handling (404, 422, 500)

### Out of Scope
- Authentication/authorization (covered separately)
- User progress endpoints
- Frontend integration (Task 03)
- Image serving (Task 06, 09)

---

## Prerequisites

### Completed Tasks
- ✅ Task 01: Database seeded with 1,000+ MCQs and 140+ OSCEs

### Running Services
- PostgreSQL database running
- FastAPI server running on port 8000
- Database connection valid

### Tools Needed
- `curl` or `httpie` for API testing
- `pytest` for automated tests
- `jq` for JSON parsing in bash

---

## Implementation Steps

### Step 1: Start FastAPI Server (10 min)

```bash
# Activate backend environment
cd backend
source venv/bin/activate

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/irstudy"
export SECRET_KEY="your-secret-key"

# Start server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verify health check
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

### Step 2: Test MCQ Endpoints (30 min)

#### 2.1 Get All MCQs (Paginated)

```bash
# Get first 10 MCQs
curl -s http://localhost:8000/api/v1/mcqs?limit=10&offset=0 | jq

# Expected structure
{
  "total": 1042,
  "limit": 10,
  "offset": 0,
  "mcqs": [
    {
      "id": 1,
      "question_id": "WEEK3-CARDIO-001",
      "question_text": "A 62-year-old man presents...",
      "options": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D",
        "E": "Option E"
      },
      "correct_answer": "E",
      "explanation": "...",
      "citation": "...",
      "specialty": "CARDIOLOGY",
      "difficulty": "MEDIUM",
      "tags": ["ACS", "ECG", "STEMI"],
      "image_url": null,
      "image_caption": null,
      "created_at": "2026-02-03T12:00:00Z"
    }
  ]
}
```

#### 2.2 Filter by Specialty

```bash
# Get Cardiology MCQs only
curl -s "http://localhost:8000/api/v1/mcqs?specialty=CARDIOLOGY&limit=5" | jq '.total'

# Expected: ~200 (cardiology MCQs)

# Get Respiratory MCQs
curl -s "http://localhost:8000/api/v1/mcqs?specialty=RESPIRATORY&limit=5" | jq '.total'

# Expected: ~200 (respiratory MCQs)

# Get Psychiatry MCQs
curl -s "http://localhost:8000/api/v1/mcqs?specialty=PSYCHIATRY&limit=5" | jq '.total'

# Expected: ~200 (psychiatry MCQs)
```

#### 2.3 Filter by Difficulty

```bash
# Get EASY MCQs
curl -s "http://localhost:8000/api/v1/mcqs?difficulty=EASY" | jq '.total'

# Get HARD MCQs
curl -s "http://localhost:8000/api/v1/mcqs?difficulty=HARD" | jq '.total'
```

#### 2.4 Get Single MCQ by ID

```bash
# Get specific MCQ
curl -s http://localhost:8000/api/v1/mcqs/WEEK3-CARDIO-001 | jq

# Expected: Full MCQ details

# Test 404 error
curl -s http://localhost:8000/api/v1/mcqs/INVALID-ID
# Expected: {"detail": "MCQ not found"}
```

#### 2.5 Search by Tags

```bash
# Get MCQs tagged with "ECG"
curl -s "http://localhost:8000/api/v1/mcqs?tags=ECG" | jq '.total'

# Multiple tags (AND logic)
curl -s "http://localhost:8000/api/v1/mcqs?tags=ECG,STEMI" | jq '.mcqs[].tags'
```

---

### Step 3: Test OSCE Endpoints (30 min)

#### 3.1 Get All OSCEs (Paginated)

```bash
# Get first 10 OSCEs
curl -s http://localhost:8000/api/v1/osces?limit=10&offset=0 | jq

# Expected structure
{
  "total": 142,
  "limit": 10,
  "offset": 0,
  "osces": [
    {
      "id": 1,
      "osce_id": "CARDIO-OSCE-001",
      "title": "Chest Pain Assessment",
      "specialty": "CARDIOLOGY",
      "topic": "Acute Coronary Syndrome",
      "station_type": "HISTORY_TAKING",
      "duration_minutes": 8,
      "instructions": "...",
      "patient_profile": "...",
      "rubric": {
        "introduction": {"max_score": 2, "criteria": "..."},
        "history": {"max_score": 8, "criteria": "..."}
      },
      "supporting_documents": null,
      "created_at": "2026-02-03T12:00:00Z"
    }
  ]
}
```

#### 3.2 Filter by Specialty

```bash
# Get Cardiology OSCEs
curl -s "http://localhost:8000/api/v1/osces?specialty=CARDIOLOGY" | jq '.total'

# Expected: ~50 (cardiology OSCEs)

# Get ObGyn OSCEs
curl -s "http://localhost:8000/api/v1/osces?specialty=OBSTETRICS_GYNAECOLOGY" | jq '.total'
```

#### 3.3 Filter by Station Type

```bash
# Get History Taking stations
curl -s "http://localhost:8000/api/v1/osces?station_type=HISTORY_TAKING" | jq '.total'

# Get Physical Examination stations
curl -s "http://localhost:8000/api/v1/osces?station_type=PHYSICAL_EXAMINATION" | jq '.total'

# Get Breaking Bad News stations
curl -s "http://localhost:8000/api/v1/osces?station_type=BREAKING_BAD_NEWS" | jq '.total'
```

#### 3.4 Get OSCE Categories (NEW ENDPOINT)

```bash
# Get hierarchical categories
curl -s http://localhost:8000/api/v1/osces/categories | jq

# Expected structure
{
  "specialties": [
    {
      "specialty": "CARDIOLOGY",
      "count": 50,
      "topics": [
        {
          "topic": "Acute Coronary Syndrome",
          "count": 8,
          "station_types": ["HISTORY_TAKING", "PHYSICAL_EXAMINATION"]
        },
        {
          "topic": "Heart Failure",
          "count": 6,
          "station_types": ["HISTORY_TAKING", "MANAGEMENT"]
        }
      ]
    }
  ]
}
```

**API Implementation (if not exists):**

```python
# backend/src/api/v1/osces.py

@router.get("/categories")
async def get_osce_categories(
    specialty: Optional[MedicalSpecialty] = None,
    db: Session = Depends(get_db)
):
    """Get hierarchical OSCE categories for search/filtering"""

    query = db.query(
        OSCE.specialty,
        OSCE.topic,
        OSCE.station_type,
        func.count(OSCE.id).label('count')
    )

    if specialty:
        query = query.filter(OSCE.specialty == specialty)

    results = query.group_by(
        OSCE.specialty,
        OSCE.topic,
        OSCE.station_type
    ).all()

    # Transform to hierarchical structure
    specialties_dict = {}
    for row in results:
        spec = row.specialty.value
        topic = row.topic
        station_type = row.station_type.value
        count = row.count

        if spec not in specialties_dict:
            specialties_dict[spec] = {
                "specialty": spec,
                "count": 0,
                "topics": {}
            }

        if topic not in specialties_dict[spec]["topics"]:
            specialties_dict[spec]["topics"][topic] = {
                "topic": topic,
                "count": 0,
                "station_types": []
            }

        specialties_dict[spec]["topics"][topic]["count"] += count
        specialties_dict[spec]["topics"][topic]["station_types"].append(station_type)
        specialties_dict[spec]["count"] += count

    # Convert to list format
    specialties = []
    for spec_data in specialties_dict.values():
        spec_data["topics"] = list(spec_data["topics"].values())
        specialties.append(spec_data)

    return {"specialties": specialties}
```

---

### Step 4: Performance Testing (20 min)

#### 4.1 Response Time Benchmarking

```bash
# Test MCQ endpoint response time
time curl -s http://localhost:8000/api/v1/mcqs?limit=100 > /dev/null

# Expected: <100ms

# Benchmark with Apache Bench (ab)
ab -n 100 -c 10 http://localhost:8000/api/v1/mcqs?limit=10

# Expected results:
# - Requests per second: >100
# - Mean time per request: <100ms
# - No failed requests
```

#### 4.2 Database Query Optimization Check

```bash
# Enable query logging in PostgreSQL
# Check slow queries

# If response time >100ms, add indexes:
# CREATE INDEX idx_mcqs_specialty ON mcqs(specialty);
# CREATE INDEX idx_mcqs_difficulty ON mcqs(difficulty);
# CREATE INDEX idx_osces_specialty ON osces(specialty);
# CREATE INDEX idx_osces_station_type ON osces(station_type);
```

---

### Step 5: Error Handling Verification (10 min)

```bash
# Test invalid specialty
curl -s "http://localhost:8000/api/v1/mcqs?specialty=INVALID"
# Expected: 422 Unprocessable Entity

# Test invalid limit (too high)
curl -s "http://localhost:8000/api/v1/mcqs?limit=10000"
# Expected: 422 or capped at 100

# Test invalid question_id
curl -s http://localhost:8000/api/v1/mcqs/DOES-NOT-EXIST
# Expected: 404 Not Found

# Test database connection failure
# Stop PostgreSQL temporarily
curl -s http://localhost:8000/api/v1/mcqs
# Expected: 500 Internal Server Error with message
```

---

### Step 6: Automated Test Suite (40 min)

Create comprehensive pytest suite:

**File:** `backend/tests/test_api_mcqs.py`

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.models import MedicalSpecialty, DifficultyLevel

client = TestClient(app)

def test_get_mcqs_paginated():
    """Test MCQ pagination"""
    response = client.get("/api/v1/mcqs?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "mcqs" in data
    assert len(data["mcqs"]) <= 10
    assert data["total"] > 1000  # Should have 1000+ MCQs

def test_get_mcqs_filter_specialty():
    """Test filtering by specialty"""
    response = client.get("/api/v1/mcqs?specialty=CARDIOLOGY")
    assert response.status_code == 200
    data = response.json()
    for mcq in data["mcqs"]:
        assert mcq["specialty"] == "CARDIOLOGY"

def test_get_mcq_by_id():
    """Test getting single MCQ"""
    # First, get list to find valid ID
    response = client.get("/api/v1/mcqs?limit=1")
    mcq_id = response.json()["mcqs"][0]["question_id"]

    # Get specific MCQ
    response = client.get(f"/api/v1/mcqs/{mcq_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["question_id"] == mcq_id
    assert "question_text" in data
    assert "options" in data
    assert "correct_answer" in data

def test_get_mcq_not_found():
    """Test 404 for invalid MCQ ID"""
    response = client.get("/api/v1/mcqs/INVALID-ID-12345")
    assert response.status_code == 404

def test_mcq_response_structure():
    """Test MCQ response has correct structure"""
    response = client.get("/api/v1/mcqs?limit=1")
    mcq = response.json()["mcqs"][0]

    required_fields = [
        "question_id", "question_text", "options",
        "correct_answer", "explanation", "citation",
        "specialty", "difficulty", "tags"
    ]
    for field in required_fields:
        assert field in mcq, f"Missing field: {field}"

    # Validate types
    assert isinstance(mcq["options"], dict)
    assert isinstance(mcq["tags"], list)
    assert mcq["specialty"] in [s.value for s in MedicalSpecialty]

def test_mcqs_performance():
    """Test response time <100ms"""
    import time
    start = time.time()
    response = client.get("/api/v1/mcqs?limit=100")
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 0.1  # 100ms
```

**File:** `backend/tests/test_api_osces.py`

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_osces_paginated():
    """Test OSCE pagination"""
    response = client.get("/api/v1/osces?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "osces" in data
    assert len(data["osces"]) <= 10
    assert data["total"] >= 140  # Should have 140+ OSCEs

def test_get_osces_filter_specialty():
    """Test filtering by specialty"""
    response = client.get("/api/v1/osces?specialty=CARDIOLOGY")
    assert response.status_code == 200
    data = response.json()
    for osce in data["osces"]:
        assert osce["specialty"] == "CARDIOLOGY"

def test_get_osce_categories():
    """Test OSCE categories endpoint"""
    response = client.get("/api/v1/osces/categories")
    assert response.status_code == 200
    data = response.json()
    assert "specialties" in data

    # Validate structure
    for specialty in data["specialties"]:
        assert "specialty" in specialty
        assert "count" in specialty
        assert "topics" in specialty

        for topic in specialty["topics"]:
            assert "topic" in topic
            assert "count" in topic
            assert "station_types" in topic
            assert isinstance(topic["station_types"], list)

def test_get_osces_filter_station_type():
    """Test filtering by station type"""
    response = client.get("/api/v1/osces?station_type=HISTORY_TAKING")
    assert response.status_code == 200
    data = response.json()
    for osce in data["osces"]:
        assert osce["station_type"] == "HISTORY_TAKING"

def test_osce_response_structure():
    """Test OSCE response has correct structure"""
    response = client.get("/api/v1/osces?limit=1")
    osce = response.json()["osces"][0]

    required_fields = [
        "osce_id", "title", "specialty", "topic",
        "station_type", "duration_minutes", "instructions",
        "patient_profile", "rubric"
    ]
    for field in required_fields:
        assert field in osce, f"Missing field: {field}"

    # Validate types
    assert isinstance(osce["rubric"], dict)
    assert isinstance(osce["duration_minutes"], int)
```

**Run tests:**

```bash
cd backend
pytest tests/test_api_mcqs.py -v
pytest tests/test_api_osces.py -v

# Run with coverage
pytest tests/ --cov=src.api.v1 --cov-report=html
```

---

### Step 7: Documentation Update (10 min)

Update API documentation:

```bash
# Access Swagger UI
open http://localhost:8000/docs

# Verify all endpoints documented
# Verify request/response schemas
# Verify example responses
```

Add endpoint documentation to `backend/README.md`:

```markdown
## API Endpoints

### MCQs

- `GET /api/v1/mcqs` - List MCQs with pagination and filtering
  - Query params: `limit`, `offset`, `specialty`, `difficulty`, `tags`
  - Response: `{total, limit, offset, mcqs[]}`

- `GET /api/v1/mcqs/{question_id}` - Get single MCQ
  - Response: MCQ object

### OSCEs

- `GET /api/v1/osces` - List OSCEs with pagination and filtering
  - Query params: `limit`, `offset`, `specialty`, `station_type`
  - Response: `{total, limit, offset, osces[]}`

- `GET /api/v1/osces/categories` - Get hierarchical categories
  - Response: `{specialties[{specialty, count, topics[]}]}`

- `GET /api/v1/osces/{osce_id}` - Get single OSCE
  - Response: OSCE object
```

---

## Testing Checklist

Manual Testing:
- [ ] GET /api/v1/mcqs returns 1,000+ MCQs
- [ ] Filter by specialty works (CARDIOLOGY, RESPIRATORY, PSYCHIATRY)
- [ ] Filter by difficulty works (EASY, MEDIUM, HARD)
- [ ] Filter by tags works
- [ ] Pagination works (limit, offset)
- [ ] GET /api/v1/mcqs/{id} returns single MCQ
- [ ] 404 error for invalid MCQ ID
- [ ] GET /api/v1/osces returns 140+ OSCEs
- [ ] Filter by specialty works
- [ ] Filter by station_type works
- [ ] GET /api/v1/osces/categories returns hierarchical structure
- [ ] Response time <100ms for all endpoints
- [ ] Error handling returns proper HTTP codes

Automated Testing:
- [ ] All pytest tests pass (100%)
- [ ] Test coverage >80% for API routes
- [ ] Performance tests pass (<100ms)
- [ ] Error handling tests pass

---

## Success Criteria

- ✅ All MCQ endpoints return correct data
- ✅ All OSCE endpoints return correct data
- ✅ Filtering by specialty, difficulty, tags works
- ✅ OSCE categories endpoint implemented and tested
- ✅ Pagination works correctly
- ✅ Response time <100ms for all endpoints
- ✅ All automated tests pass (100%)
- ✅ Swagger documentation complete
- ✅ No database errors in logs
- ✅ Error handling returns proper HTTP codes

---

## Rollback Plan

If API verification fails:

1. Check database connection:
   ```bash
   psql -d irstudy -c "SELECT COUNT(*) FROM mcqs;"
   psql -d irstudy -c "SELECT COUNT(*) FROM osces;"
   ```

2. Check FastAPI logs:
   ```bash
   # Look for errors in server output
   tail -f backend/logs/app.log
   ```

3. Verify database indexes exist:
   ```sql
   SELECT indexname FROM pg_indexes WHERE tablename IN ('mcqs', 'osces');
   ```

4. If endpoints broken, restart services:
   ```bash
   # Restart PostgreSQL
   sudo systemctl restart postgresql

   # Restart FastAPI
   pkill uvicorn
   uvicorn src.main:app --reload
   ```

---

## Common Issues

### Issue 1: "Connection refused"
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct

### Issue 2: "No data returned"
**Solution:** Re-run Task 01 seed script to populate database

### Issue 3: "Slow response time (>100ms)"
**Solution:** Add database indexes on frequently queried columns

### Issue 4: "422 Unprocessable Entity"
**Solution:** Check enum values match database schema (MedicalSpecialty, DifficultyLevel)

---

## Next Task

After successful verification, proceed to **Task 03: Frontend Integration Testing**

File: `03_frontend_integration.md`
