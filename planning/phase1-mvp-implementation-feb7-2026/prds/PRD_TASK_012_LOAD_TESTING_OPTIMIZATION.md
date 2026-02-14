# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_012 - Load Testing & Optimization (4-5 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/backend

# Install Locust
pip install locust

# Create load test scenarios
mkdir -p tests/load

cat > tests/load/locustfile.py <<'EOF'
# Locust load test scenarios will be implemented here
EOF

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

**DO NOT**:
- ❌ Ask "Would you like me to test with 50 or 500 users?"
- ❌ Ask "Should I implement Redis caching first?"
- ❌ Wait for approval
- ❌ Ask "Which endpoints should I load test?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 3
- **Day:** 3 (Feb 23, 2026)
- **Duration:** 4-5 hours
- **Priority:** P1-High
- **Dependencies:** TASK_010 (E2E tests must pass)
- **Owner:** testing-qa-expert + general-purpose agent
- **Status:** 🟡 Not Started
- **Blocks:** TASK_013 (Deployment)

---

## 🎯 Objectives

1. **Create Locust load test scenarios** (50, 100, 250, 500 users)
2. **Verify performance benchmarks:** API <200ms, Page load <2s
3. **Optimize database queries** (add indexes where needed)
4. **Implement Redis caching** for frequently accessed data
5. **Configure CDN** for medical images (3,168 images)
6. **Pass load test:** 500 concurrent users with <2s page load

---

## 📝 Implementation Guide

### Step 1: Create Locust Scenarios (1.5 hours)

```bash
cat > tests/load/locustfile.py <<'EOF'
from locust import HttpUser, task, between
import random

class MCQPracticeUser(HttpUser):
    """Simulate user practicing MCQs"""
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get auth token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def get_random_mcq(self):
        """Get random MCQ (most frequent operation)"""
        self.client.get("/api/v1/mcqs/random", headers=self.headers)

    @task(3)
    def submit_mcq_answer(self):
        """Submit MCQ answer"""
        self.client.post("/api/v1/mcqs/submit-answer", json={
            "mcq_id": random.randint(1, 1208),
            "selected_answer": random.choice(["A", "B", "C", "D", "E"]),
            "time_taken_seconds": random.randint(30, 120)
        }, headers=self.headers)

    @task(2)
    def get_dashboard(self):
        """View progress dashboard"""
        self.client.get("/api/v1/progress/dashboard", headers=self.headers)

    @task(1)
    def get_study_cards(self):
        """Get due study cards"""
        self.client.get("/api/v1/study-cards/due-cards", headers=self.headers)

class StudyCardUser(HttpUser):
    """Simulate user reviewing study cards"""
    wait_time = between(2, 5)

    def on_start(self):
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test2@example.com",
            "password": "TestPassword123!"
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def review_study_cards(self):
        """Review study cards"""
        # Get due cards
        response = self.client.get("/api/v1/study-cards/due-cards", headers=self.headers)
        cards = response.json()

        if cards:
            # Review first card
            self.client.post("/api/v1/study-cards/review", json={
                "card_id": cards[0]["id"],
                "quality": random.randint(3, 5),
                "time_taken_seconds": random.randint(10, 60)
            }, headers=self.headers)
EOF

echo "✅ Locust scenarios created"
```

### Step 2: Run Load Tests (1 hour)

```bash
# Test with 50 users (baseline)
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 10 --run-time 2m --headless

# Test with 100 users
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 20 --run-time 2m --headless

# Test with 250 users
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users 250 --spawn-rate 50 --run-time 2m --headless

# Test with 500 users (target)
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users 500 --spawn-rate 100 --run-time 5m --headless --csv=results/load_test_500users

# Generate report
echo "Load test results saved to results/load_test_500users_*.csv"
```

### Step 3: Database Optimization (1 hour)

```bash
# Create database indexes for frequently queried fields
cat > backend/alembic/versions/$(date +%Y%m%d)_add_performance_indexes.py <<'EOF'
"""add_performance_indexes

Revision ID: xxxxx
Create Date: 2026-02-23
"""
from alembic import op

def upgrade():
    # MCQ indexes
    op.create_index('idx_mcqs_specialty', 'mcqs', ['specialty'])
    op.create_index('idx_mcqs_difficulty', 'mcqs', ['difficulty'])
    op.create_index('idx_mcqs_specialty_difficulty', 'mcqs', ['specialty', 'difficulty'])

    # MCQ Attempt indexes
    op.create_index('idx_mcq_attempts_user_id', 'mcq_attempts', ['user_id'])
    op.create_index('idx_mcq_attempts_created_at', 'mcq_attempts', ['created_at'])

    # Study Card Review indexes (if not already added in TASK_005)
    op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_study_card_reviews_user_next_review ON study_card_reviews(user_id, next_review_date);")

def downgrade():
    op.drop_index('idx_mcqs_specialty_difficulty', table_name='mcqs')
    op.drop_index('idx_mcqs_difficulty', table_name='mcqs')
    op.drop_index('idx_mcqs_specialty', table_name='mcqs')
    op.drop_index('idx_mcq_attempts_created_at', table_name='mcq_attempts')
    op.drop_index('idx_mcq_attempts_user_id', table_name='mcq_attempts')
EOF

alembic upgrade head
```

### Step 4: Implement Redis Caching (1.5 hours)

```bash
cat > src/services/cache_service.py <<'EOF'
import redis
import json
from typing import Optional, Any
import os

class CacheService:
    """Redis caching service for frequently accessed data"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (default 1 hour)"""
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            print(f"Cache set error: {e}")

    def delete(self, key: str):
        """Delete key from cache"""
        self.redis_client.delete(key)

# Usage in endpoints
cache = CacheService()

# Example: Cache MCQ data
@router.get("/api/v1/mcqs/{mcq_id}")
async def get_mcq_cached(mcq_id: int):
    cache_key = f"mcq:{mcq_id}"

    # Try cache first
    cached_mcq = cache.get(cache_key)
    if cached_mcq:
        return cached_mcq

    # Fetch from database
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    # Store in cache for 1 hour
    cache.set(cache_key, mcq, ttl=3600)

    return mcq
EOF
```

---

## ✅ Success Criteria

1. ✅ Locust scenarios created (50, 100, 250, 500 users)
2. ✅ Performance benchmarks met: API <200ms, Page <2s
3. ✅ Database indexes added (specialty, difficulty, user_id, created_at)
4. ✅ Redis caching implemented
5. ✅ CDN configured for images
6. ✅ Load test passed: 500 concurrent users

---

## 🔄 When Complete

```bash
sed -i 's/TASK_012.*TODO/TASK_012: ✅ DONE/' @fix_plan.md

git commit -m "perf(backend): Complete TASK_012 Load Testing & Optimization - 500 concurrent users

- Locust load test scenarios (50-500 users)
- Database indexes for performance
- Redis caching for frequent queries
- CDN configuration for medical images
- Load test passed: 500 users, <2s page load
- API response time: <200ms (95th percentile)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_012 complete. Starting TASK_013..."
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
