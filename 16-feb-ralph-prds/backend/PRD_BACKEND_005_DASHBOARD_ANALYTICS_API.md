# PRD_BACKEND_005: Dashboard Analytics API

**PRD ID**: PRD_BACKEND_005_DASHBOARD_ANALYTICS_API
**Title**: Unified Dashboard Analytics and Progress Tracking API
**Category**: Backend - Analytics API
**Priority**: P1-High (blocks PRD_FRONTEND_003 implementation)
**Owner**: Backend Engineer (Python FastAPI Expert)
**Estimated Effort**: 8-10 hours
**Dependencies**:
- PRD_BACKEND_001 (EMR Database Migration - user_progress EMR columns exist)
- PRD_BACKEND_002 (EMR Session API - session data available)
**Blocks**:
- PRD_FRONTEND_003 (EMR Dashboard Integration - needs these 3 endpoints)

**Created**: 2026-02-16
**Status**: Ready for Implementation

---

## R - REQUEST (What and Why)

### User Story

**AS A** medical student practicing for AMC Clinical Examination
**I WANT TO** see unified dashboard analytics showing MCQ, OSCE, and EMR progress in one API response
**SO THAT** I can track my improvement across all practice modes without making 10+ separate API calls (slow dashboard load)

### Business Context

**Current State**:
- PRD_FRONTEND_003 requires 3 dashboard endpoints:
  1. `GET /api/v1/progress/dashboard/emr` - EMR metrics (sessions, avg score, completion rate)
  2. `GET /api/v1/progress/weekly-trends/unified` - 3-line chart (MCQ + OSCE + EMR)
  3. `GET /api/v1/progress/weak-areas/emr` - Weak specialties for EMR
- **NONE of these endpoints exist in any backend PRD** (PRD_BACKEND_001-004)
- Frontend currently blocked from implementing dashboard integration
- Dashboard load time would be >2s with 4+ sequential API calls

**Problem**:
- **API Gap**: 3 critical endpoints missing from backend architecture
- **Performance**: Sequential API calls cause slow dashboard load (bad UX)
- **Data Duplication**: Frontend would need to fetch MCQ/OSCE/EMR data separately and merge
- **Caching**: No server-side caching strategy for expensive analytics queries
- **Progress Tracking**: No unified endpoint to get all user progress metrics

**Desired State**:
- 3 production-ready FastAPI endpoints with Pydantic schemas
- Efficient SQL queries (JOIN across mcq_sessions, osce_sessions, emr_sessions)
- Server-side caching (Redis, 5min TTL for analytics queries)
- Response time <500ms for all endpoints (p95)
- Support filtering by date range, specialty, EMR system
- Reusable service layer for progress calculations

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Response Time** | <500ms p95 | All 3 endpoints under load |
| **Cache Hit Rate** | >80% | Redis cache efficiency |
| **Dashboard Load Time** | <1s | Frontend parallel API calls |
| **Query Efficiency** | <100ms SQL | Indexed queries, no N+1 |
| **Test Coverage** | ≥70% | Unit + integration tests |
| **Concurrent Users** | 100+ | Load testing |

### Business Value

- **Faster UX**: Dashboard loads in <1s (vs 2-3s sequential calls)
- **Scalability**: Cached analytics reduce database load by 80%
- **Code Reuse**: Unified service layer for progress calculations
- **API Consistency**: Follows existing FastAPI patterns (osces.py, mcqs.py)
- **Student Insights**: Actionable data (weak areas, trends, improvement rate)

---

## A - ARCHITECTURE (How It Will Be Built)

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                Dashboard Analytics API Architecture              │
└─────────────────────────────────────────────────────────────────┘

LAYERS:
  │
  ├─► API LAYER (FastAPI Endpoints)
  │   ├─ GET /api/v1/progress/dashboard/emr
  │   ├─ GET /api/v1/progress/weekly-trends/unified
  │   └─ GET /api/v1/progress/weak-areas/emr
  │
  ├─► SERVICE LAYER (Business Logic)
  │   ├─ EMRAnalyticsService (calculate EMR metrics)
  │   ├─ UnifiedTrendsService (merge MCQ + OSCE + EMR data)
  │   ├─ WeakAreasService (identify low-performing specialties)
  │   └─ ProgressCalculator (shared utility for metrics)
  │
  ├─► CACHING LAYER (Redis)
  │   ├─ dashboard:emr:{user_id} (5min TTL)
  │   ├─ trends:unified:{user_id}:{weeks} (10min TTL)
  │   └─ weak-areas:emr:{user_id} (5min TTL)
  │
  ├─► DATA ACCESS LAYER (SQLAlchemy ORM)
  │   ├─ Complex queries (JOIN emr_sessions, emr_validations, mock_patients)
  │   ├─ Aggregations (AVG, COUNT, GROUP BY specialty/week)
  │   └─ Subqueries (latest validation per session, specialty rankings)
  │
  └─► DATABASE LAYER (PostgreSQL)
      ├─ emr_sessions (user_id, patient_id, started_at, completed_at)
      ├─ emr_validations (session_id, total_amc_score, pass_status)
      ├─ mock_patients (specialty, complexity_level)
      ├─ mcq_sessions (user_id, accuracy, completed_at)
      ├─ osce_sessions (user_id, final_score, completed_at)
      └─ user_progress (emr_sessions_total, emr_sessions_completed, etc.)

PERFORMANCE OPTIMIZATIONS:
- Database indexes on (user_id, completed_at) for fast filtering
- Redis caching (80%+ hit rate reduces DB load)
- Query result pagination (limit 1000 rows max)
- Connection pooling (SQLAlchemy AsyncEngine)
- Parallel query execution where possible
```

### API Endpoints Specification

#### Endpoint 1: EMR Dashboard Metrics

```python
GET /api/v1/progress/dashboard/emr
```

**Purpose**: Get EMR practice metrics for dashboard (sessions, avg score, completion rate, AHPRA compliance)

**Authentication**: JWT required (user_id from token)

**Query Parameters**: None (always returns current user's data)

**Response** (200 OK):
```python
class EMRDashboardMetrics(BaseModel):
    total_sessions: int
    completed_sessions: int
    in_progress_sessions: int
    avg_validation_score: float  # 0-100
    avg_typing_wpm: float
    improvement_percentage: float  # Last 5 sessions vs previous 5
    ahpra_compliance_rate: float  # % of sessions meeting AHPRA standards
    total_time_spent_seconds: int

    # EMR system breakdown
    epic_sessions: int
    cerner_sessions: int

    # Specialty breakdown (top 5)
    specialty_stats: List[SpecialtyStats]

    class SpecialtyStats(BaseModel):
        specialty: str
        session_count: int
        avg_score: float

# Example Response:
{
  "total_sessions": 45,
  "completed_sessions": 42,
  "in_progress_sessions": 3,
  "avg_validation_score": 78.5,
  "avg_typing_wpm": 42.3,
  "improvement_percentage": 12.5,
  "ahpra_compliance_rate": 85.7,
  "total_time_spent_seconds": 18000,
  "epic_sessions": 25,
  "cerner_sessions": 20,
  "specialty_stats": [
    {"specialty": "Cardiology", "session_count": 12, "avg_score": 82.0},
    {"specialty": "Respiratory", "session_count": 10, "avg_score": 75.5},
    {"specialty": "Neurology", "session_count": 8, "avg_score": 70.2}
  ]
}
```

**Business Logic**:
1. Check cache: `dashboard:emr:{user_id}` (Redis)
2. If cache miss:
   a. Query emr_sessions for user (JOIN emr_validations)
   b. Calculate aggregates:
      - total_sessions = COUNT(*)
      - completed_sessions = COUNT WHERE is_active=false
      - avg_validation_score = AVG(emr_validations.total_amc_score)
      - avg_typing_wpm = AVG(emr_validations.typing_wpm)
   c. Calculate improvement_percentage:
      - Last 5 sessions avg vs previous 5 sessions avg
   d. Calculate AHPRA compliance:
      - % of sessions with validation.ahpra_compliant=true
   e. Query specialty stats (GROUP BY mock_patients.specialty)
   f. Cache result (5min TTL)
3. Return metrics

**SQL Query Example**:
```sql
-- Main metrics query
SELECT
  COUNT(*) as total_sessions,
  COUNT(*) FILTER (WHERE is_active = false) as completed_sessions,
  COUNT(*) FILTER (WHERE is_active = true) as in_progress_sessions,
  AVG(v.total_amc_score) as avg_validation_score,
  AVG(v.typing_wpm) as avg_typing_wpm,
  SUM(EXTRACT(EPOCH FROM (completed_at - started_at))) as total_time_spent_seconds,
  COUNT(*) FILTER (WHERE emr_system = 'epic') as epic_sessions,
  COUNT(*) FILTER (WHERE emr_system = 'cerner') as cerner_sessions,
  SUM(CASE WHEN v.ahpra_compliant = true THEN 1 ELSE 0 END)::float /
    COUNT(v.id)::float * 100 as ahpra_compliance_rate
FROM emr_sessions s
LEFT JOIN emr_validations v ON s.id = v.session_id
WHERE s.user_id = :user_id
  AND s.completed_at IS NOT NULL;

-- Specialty breakdown query
SELECT
  p.specialty,
  COUNT(s.id) as session_count,
  AVG(v.total_amc_score) as avg_score
FROM emr_sessions s
JOIN mock_patients p ON s.patient_id = p.id
LEFT JOIN emr_validations v ON s.id = v.session_id
WHERE s.user_id = :user_id
  AND s.completed_at IS NOT NULL
GROUP BY p.specialty
ORDER BY session_count DESC
LIMIT 5;

-- Improvement calculation (subquery)
WITH recent_sessions AS (
  SELECT
    v.total_amc_score,
    ROW_NUMBER() OVER (ORDER BY s.completed_at DESC) as rn
  FROM emr_sessions s
  JOIN emr_validations v ON s.id = v.session_id
  WHERE s.user_id = :user_id
    AND s.completed_at IS NOT NULL
  LIMIT 10
)
SELECT
  AVG(total_amc_score) FILTER (WHERE rn <= 5) as recent_avg,
  AVG(total_amc_score) FILTER (WHERE rn > 5) as previous_avg
FROM recent_sessions;
```

**Error Responses**:
- 401 Unauthorized: Missing/invalid JWT
- 500 Internal Server Error: Database/cache error

**Performance Target**: <300ms (with cache miss), <50ms (with cache hit)

---

#### Endpoint 2: Unified Weekly Trends

```python
GET /api/v1/progress/weekly-trends/unified?weeks=12
```

**Purpose**: Get 3-line chart data (MCQ accuracy, OSCE pass rate, EMR score) by week for unified progress tracking

**Authentication**: JWT required

**Query Parameters**:
- `weeks` (optional, default=12): Number of weeks to return (max 52)
- `start_date` (optional): ISO date, default=12 weeks ago
- `end_date` (optional): ISO date, default=today

**Response** (200 OK):
```python
class UnifiedWeeklyTrend(BaseModel):
    week_start: date  # Monday of the week (ISO week)
    mcq_accuracy: Optional[float]  # % correct (0-100)
    osce_avg_score: Optional[float]  # Average score (0-100)
    emr_avg_score: Optional[float]  # Average validation score (0-100)

    # Counts (for tooltips)
    mcq_attempts: int
    osce_completions: int
    emr_sessions: int

class UnifiedWeeklyTrendsResponse(BaseModel):
    trends: List[UnifiedWeeklyTrend]
    summary: TrendSummary

    class TrendSummary(BaseModel):
        total_weeks: int
        mcq_improvement: float  # First week vs last week
        osce_improvement: float
        emr_improvement: float
        best_practice_mode: str  # "mcq", "osce", or "emr"

# Example Response:
{
  "trends": [
    {
      "week_start": "2026-01-13",
      "mcq_accuracy": 72.5,
      "osce_avg_score": 68.0,
      "emr_avg_score": 65.3,
      "mcq_attempts": 45,
      "osce_completions": 3,
      "emr_sessions": 5
    },
    {
      "week_start": "2026-01-20",
      "mcq_accuracy": 75.2,
      "osce_avg_score": 70.5,
      "emr_avg_score": 68.7,
      "mcq_attempts": 52,
      "osce_completions": 4,
      "emr_sessions": 6
    }
  ],
  "summary": {
    "total_weeks": 12,
    "mcq_improvement": 12.5,
    "osce_improvement": 8.3,
    "emr_improvement": 15.2,
    "best_practice_mode": "emr"
  }
}
```

**Business Logic**:
1. Check cache: `trends:unified:{user_id}:{weeks}` (Redis)
2. If cache miss:
   a. Query MCQ sessions (GROUP BY week, calculate avg accuracy)
   b. Query OSCE sessions (GROUP BY week, calculate avg score)
   c. Query EMR sessions (GROUP BY week, calculate avg validation score)
   d. Merge results (OUTER JOIN on week_start)
   e. Fill gaps with null (weeks with no activity)
   f. Calculate summary (improvement, best mode)
   g. Cache result (10min TTL)
3. Return trends

**SQL Query Example**:
```sql
-- Generate week series
WITH week_series AS (
  SELECT
    date_trunc('week', CURRENT_DATE - interval '1 week' * generate_series(0, :weeks - 1))::date as week_start
),

-- MCQ data by week
mcq_weekly AS (
  SELECT
    date_trunc('week', completed_at)::date as week_start,
    AVG(CASE WHEN is_correct THEN 100.0 ELSE 0.0 END) as mcq_accuracy,
    COUNT(*) as mcq_attempts
  FROM mcq_sessions
  WHERE user_id = :user_id
    AND completed_at IS NOT NULL
    AND completed_at >= CURRENT_DATE - interval '1 week' * :weeks
  GROUP BY date_trunc('week', completed_at)
),

-- OSCE data by week
osce_weekly AS (
  SELECT
    date_trunc('week', completed_at)::date as week_start,
    AVG(final_score) as osce_avg_score,
    COUNT(*) as osce_completions
  FROM osce_sessions
  WHERE user_id = :user_id
    AND completed_at IS NOT NULL
    AND completed_at >= CURRENT_DATE - interval '1 week' * :weeks
  GROUP BY date_trunc('week', completed_at)
),

-- EMR data by week
emr_weekly AS (
  SELECT
    date_trunc('week', s.completed_at)::date as week_start,
    AVG(v.total_amc_score) as emr_avg_score,
    COUNT(s.id) as emr_sessions
  FROM emr_sessions s
  LEFT JOIN emr_validations v ON s.id = v.session_id
  WHERE s.user_id = :user_id
    AND s.completed_at IS NOT NULL
    AND s.completed_at >= CURRENT_DATE - interval '1 week' * :weeks
  GROUP BY date_trunc('week', s.completed_at)
)

-- Merge all data
SELECT
  ws.week_start,
  COALESCE(mcq.mcq_accuracy, NULL) as mcq_accuracy,
  COALESCE(osce.osce_avg_score, NULL) as osce_avg_score,
  COALESCE(emr.emr_avg_score, NULL) as emr_avg_score,
  COALESCE(mcq.mcq_attempts, 0) as mcq_attempts,
  COALESCE(osce.osce_completions, 0) as osce_completions,
  COALESCE(emr.emr_sessions, 0) as emr_sessions
FROM week_series ws
LEFT JOIN mcq_weekly mcq ON ws.week_start = mcq.week_start
LEFT JOIN osce_weekly osce ON ws.week_start = osce.week_start
LEFT JOIN emr_weekly emr ON ws.week_start = emr.week_start
ORDER BY ws.week_start ASC;
```

**Error Responses**:
- 400 Bad Request: weeks > 52 or invalid date range
- 401 Unauthorized: Missing/invalid JWT
- 500 Internal Server Error: Database/cache error

**Performance Target**: <500ms (with cache miss), <50ms (with cache hit)

---

#### Endpoint 3: EMR Weak Areas

```python
GET /api/v1/progress/weak-areas/emr?limit=5
```

**Purpose**: Get top 5 weak specialties in EMR practice (avg score <70%) for targeted improvement

**Authentication**: JWT required

**Query Parameters**:
- `limit` (optional, default=5, max=10): Number of weak areas to return
- `threshold` (optional, default=70.0): Score threshold (specialties below this are "weak")

**Response** (200 OK):
```python
class WeakArea(BaseModel):
    specialty: str
    session_count: int
    avg_score: float
    gap_to_target: float  # How far below 80% target
    recommended_practice_count: int  # # of additional sessions needed

class EMRWeakAreasResponse(BaseModel):
    weak_areas: List[WeakArea]
    total_weak_areas: int
    has_more: bool  # True if more than limit weak areas exist

# Example Response:
{
  "weak_areas": [
    {
      "specialty": "Neurology",
      "session_count": 8,
      "avg_score": 62.5,
      "gap_to_target": 17.5,
      "recommended_practice_count": 5
    },
    {
      "specialty": "Psychiatry",
      "session_count": 5,
      "avg_score": 65.0,
      "gap_to_target": 15.0,
      "recommended_practice_count": 4
    },
    {
      "specialty": "Obstetrics",
      "session_count": 6,
      "avg_score": 68.2,
      "gap_to_target": 11.8,
      "recommended_practice_count": 3
    }
  ],
  "total_weak_areas": 3,
  "has_more": false
}
```

**Business Logic**:
1. Check cache: `weak-areas:emr:{user_id}` (Redis)
2. If cache miss:
   a. Query emr_sessions grouped by specialty
   b. Calculate avg validation score per specialty
   c. Filter specialties with avg_score < threshold
   d. Calculate gap_to_target (80% - avg_score)
   e. Estimate recommended_practice_count (gap_to_target / 5 sessions)
   f. Order by gap_to_target DESC (worst first)
   g. Limit results
   h. Cache result (5min TTL)
3. Return weak areas

**SQL Query Example**:
```sql
WITH specialty_performance AS (
  SELECT
    p.specialty,
    COUNT(s.id) as session_count,
    AVG(v.total_amc_score) as avg_score,
    (80.0 - AVG(v.total_amc_score)) as gap_to_target
  FROM emr_sessions s
  JOIN mock_patients p ON s.patient_id = p.id
  LEFT JOIN emr_validations v ON s.id = v.session_id
  WHERE s.user_id = :user_id
    AND s.completed_at IS NOT NULL
    AND v.total_amc_score IS NOT NULL
  GROUP BY p.specialty
  HAVING AVG(v.total_amc_score) < :threshold
)
SELECT
  specialty,
  session_count,
  ROUND(avg_score, 1) as avg_score,
  ROUND(gap_to_target, 1) as gap_to_target,
  GREATEST(3, CEIL(gap_to_target / 5.0)) as recommended_practice_count
FROM specialty_performance
ORDER BY gap_to_target DESC
LIMIT :limit;

-- Count total weak areas (for has_more flag)
SELECT COUNT(*) as total
FROM specialty_performance;
```

**Error Responses**:
- 400 Bad Request: limit > 10 or invalid threshold
- 401 Unauthorized: Missing/invalid JWT
- 500 Internal Server Error: Database/cache error

**Performance Target**: <200ms (with cache miss), <50ms (with cache hit)

---

### Service Layer Architecture

```python
# File: backend/src/services/emr_analytics.py

from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import EMRSession, EMRValidation, MockPatient, MCQSession, OSCESession
from ..cache import cache_manager  # Redis caching utility

class EMRAnalyticsService:
    """Service for EMR dashboard analytics"""

    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def get_dashboard_metrics(self) -> dict:
        """Get EMR dashboard metrics (cached 5min)"""
        cache_key = f"dashboard:emr:{self.user_id}"

        # Try cache first
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached

        # Calculate metrics
        metrics = {
            **await self._get_session_counts(),
            **await self._get_performance_metrics(),
            **await self._get_specialty_breakdown(),
        }

        # Cache for 5 minutes
        await cache_manager.set(cache_key, metrics, ttl=300)

        return metrics

    async def _get_session_counts(self) -> dict:
        """Query: total, completed, in_progress, system breakdown"""
        result = await self.db.execute(
            select(
                func.count(EMRSession.id).label("total_sessions"),
                func.count(EMRSession.id).filter(EMRSession.is_active == False).label("completed_sessions"),
                func.count(EMRSession.id).filter(EMRSession.is_active == True).label("in_progress_sessions"),
                func.count(EMRSession.id).filter(EMRSession.emr_system == "epic").label("epic_sessions"),
                func.count(EMRSession.id).filter(EMRSession.emr_system == "cerner").label("cerner_sessions"),
            )
            .where(EMRSession.user_id == self.user_id)
        )
        row = result.one()

        return {
            "total_sessions": row.total_sessions or 0,
            "completed_sessions": row.completed_sessions or 0,
            "in_progress_sessions": row.in_progress_sessions or 0,
            "epic_sessions": row.epic_sessions or 0,
            "cerner_sessions": row.cerner_sessions or 0,
        }

    async def _get_performance_metrics(self) -> dict:
        """Query: avg score, typing WPM, AHPRA compliance, improvement"""
        result = await self.db.execute(
            select(
                func.avg(EMRValidation.total_amc_score).label("avg_score"),
                func.avg(EMRValidation.typing_wpm).label("avg_wpm"),
                func.sum(
                    func.cast(EMRValidation.ahpra_compliant, Integer)
                ).label("compliant_count"),
                func.count(EMRValidation.id).label("total_validated"),
                func.sum(
                    func.extract('epoch', EMRSession.completed_at - EMRSession.started_at)
                ).label("total_seconds"),
            )
            .select_from(EMRSession)
            .outerjoin(EMRValidation, EMRSession.id == EMRValidation.session_id)
            .where(
                EMRSession.user_id == self.user_id,
                EMRSession.completed_at.isnot(None),
            )
        )
        row = result.one()

        improvement_pct = await self._calculate_improvement()

        return {
            "avg_validation_score": float(row.avg_score) if row.avg_score else 0.0,
            "avg_typing_wpm": float(row.avg_wpm) if row.avg_wpm else 0.0,
            "ahpra_compliance_rate": (
                float(row.compliant_count / row.total_validated * 100)
                if row.total_validated
                else 0.0
            ),
            "improvement_percentage": improvement_pct,
            "total_time_spent_seconds": int(row.total_seconds) if row.total_seconds else 0,
        }

    async def _calculate_improvement(self) -> float:
        """Calculate improvement: last 5 sessions vs previous 5"""
        # Subquery for last 10 sessions with scores
        subq = (
            select(
                EMRValidation.total_amc_score,
                func.row_number()
                .over(order_by=EMRSession.completed_at.desc())
                .label("rn"),
            )
            .select_from(EMRSession)
            .join(EMRValidation, EMRSession.id == EMRValidation.session_id)
            .where(
                EMRSession.user_id == self.user_id,
                EMRSession.completed_at.isnot(None),
            )
            .limit(10)
            .subquery()
        )

        result = await self.db.execute(
            select(
                func.avg(subq.c.total_amc_score)
                .filter(subq.c.rn <= 5)
                .label("recent_avg"),
                func.avg(subq.c.total_amc_score)
                .filter(subq.c.rn > 5)
                .label("previous_avg"),
            )
        )
        row = result.one()

        if row.recent_avg and row.previous_avg:
            return float((row.recent_avg - row.previous_avg) / row.previous_avg * 100)
        return 0.0

    async def _get_specialty_breakdown(self) -> dict:
        """Query: top 5 specialties by session count"""
        result = await self.db.execute(
            select(
                MockPatient.specialty,
                func.count(EMRSession.id).label("session_count"),
                func.avg(EMRValidation.total_amc_score).label("avg_score"),
            )
            .select_from(EMRSession)
            .join(MockPatient, EMRSession.patient_id == MockPatient.id)
            .outerjoin(EMRValidation, EMRSession.id == EMRValidation.session_id)
            .where(
                EMRSession.user_id == self.user_id,
                EMRSession.completed_at.isnot(None),
            )
            .group_by(MockPatient.specialty)
            .order_by(func.count(EMRSession.id).desc())
            .limit(5)
        )

        specialty_stats = [
            {
                "specialty": row.specialty,
                "session_count": row.session_count,
                "avg_score": float(row.avg_score) if row.avg_score else 0.0,
            }
            for row in result
        ]

        return {"specialty_stats": specialty_stats}


class UnifiedTrendsService:
    """Service for unified MCQ + OSCE + EMR weekly trends"""

    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def get_weekly_trends(self, weeks: int = 12) -> dict:
        """Get unified weekly trends (cached 10min)"""
        cache_key = f"trends:unified:{self.user_id}:{weeks}"

        # Try cache
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached

        # Generate week series
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)

        # Query MCQ, OSCE, EMR data in parallel
        mcq_data = await self._get_mcq_weekly(start_date, end_date)
        osce_data = await self._get_osce_weekly(start_date, end_date)
        emr_data = await self._get_emr_weekly(start_date, end_date)

        # Merge data by week_start
        trends = self._merge_trends(mcq_data, osce_data, emr_data, start_date, weeks)

        # Calculate summary
        summary = self._calculate_summary(trends)

        result = {"trends": trends, "summary": summary}

        # Cache for 10 minutes
        await cache_manager.set(cache_key, result, ttl=600)

        return result

    async def _get_mcq_weekly(self, start_date: date, end_date: date) -> dict:
        """Query MCQ sessions grouped by week"""
        result = await self.db.execute(
            select(
                func.date_trunc("week", MCQSession.completed_at).label("week_start"),
                func.avg(
                    func.cast(MCQSession.is_correct, Integer) * 100.0
                ).label("mcq_accuracy"),
                func.count(MCQSession.id).label("mcq_attempts"),
            )
            .where(
                MCQSession.user_id == self.user_id,
                MCQSession.completed_at.isnot(None),
                MCQSession.completed_at >= start_date,
                MCQSession.completed_at <= end_date,
            )
            .group_by(func.date_trunc("week", MCQSession.completed_at))
        )

        return {row.week_start.date(): row for row in result}

    async def _get_osce_weekly(self, start_date: date, end_date: date) -> dict:
        """Query OSCE sessions grouped by week"""
        result = await self.db.execute(
            select(
                func.date_trunc("week", OSCESession.completed_at).label("week_start"),
                func.avg(OSCESession.final_score).label("osce_avg_score"),
                func.count(OSCESession.id).label("osce_completions"),
            )
            .where(
                OSCESession.user_id == self.user_id,
                OSCESession.completed_at.isnot(None),
                OSCESession.completed_at >= start_date,
                OSCESession.completed_at <= end_date,
            )
            .group_by(func.date_trunc("week", OSCESession.completed_at))
        )

        return {row.week_start.date(): row for row in result}

    async def _get_emr_weekly(self, start_date: date, end_date: date) -> dict:
        """Query EMR sessions grouped by week"""
        result = await self.db.execute(
            select(
                func.date_trunc("week", EMRSession.completed_at).label("week_start"),
                func.avg(EMRValidation.total_amc_score).label("emr_avg_score"),
                func.count(EMRSession.id).label("emr_sessions"),
            )
            .select_from(EMRSession)
            .outerjoin(EMRValidation, EMRSession.id == EMRValidation.session_id)
            .where(
                EMRSession.user_id == self.user_id,
                EMRSession.completed_at.isnot(None),
                EMRSession.completed_at >= start_date,
                EMRSession.completed_at <= end_date,
            )
            .group_by(func.date_trunc("week", EMRSession.completed_at))
        )

        return {row.week_start.date(): row for row in result}

    def _merge_trends(
        self,
        mcq_data: dict,
        osce_data: dict,
        emr_data: dict,
        start_date: date,
        weeks: int,
    ) -> List[dict]:
        """Merge MCQ, OSCE, EMR data by week_start"""
        trends = []

        # Generate all week_starts
        for i in range(weeks):
            week_start = start_date + timedelta(weeks=i)
            week_start = week_start - timedelta(days=week_start.weekday())  # Monday

            mcq_row = mcq_data.get(week_start)
            osce_row = osce_data.get(week_start)
            emr_row = emr_data.get(week_start)

            trends.append({
                "week_start": week_start.isoformat(),
                "mcq_accuracy": float(mcq_row.mcq_accuracy) if mcq_row else None,
                "osce_avg_score": float(osce_row.osce_avg_score) if osce_row else None,
                "emr_avg_score": float(emr_row.emr_avg_score) if emr_row else None,
                "mcq_attempts": int(mcq_row.mcq_attempts) if mcq_row else 0,
                "osce_completions": int(osce_row.osce_completions) if osce_row else 0,
                "emr_sessions": int(emr_row.emr_sessions) if emr_row else 0,
            })

        return trends

    def _calculate_summary(self, trends: List[dict]) -> dict:
        """Calculate improvement and best practice mode"""
        # First and last non-null values
        mcq_first = next((t["mcq_accuracy"] for t in trends if t["mcq_accuracy"]), None)
        mcq_last = next((t["mcq_accuracy"] for t in reversed(trends) if t["mcq_accuracy"]), None)

        osce_first = next((t["osce_avg_score"] for t in trends if t["osce_avg_score"]), None)
        osce_last = next((t["osce_avg_score"] for t in reversed(trends) if t["osce_avg_score"]), None)

        emr_first = next((t["emr_avg_score"] for t in trends if t["emr_avg_score"]), None)
        emr_last = next((t["emr_avg_score"] for t in reversed(trends) if t["emr_avg_score"]), None)

        mcq_improvement = ((mcq_last - mcq_first) / mcq_first * 100) if mcq_first and mcq_last else 0.0
        osce_improvement = ((osce_last - osce_first) / osce_first * 100) if osce_first and osce_last else 0.0
        emr_improvement = ((emr_last - emr_first) / emr_first * 100) if emr_first and emr_last else 0.0

        # Best mode = highest improvement
        improvements = {
            "mcq": mcq_improvement,
            "osce": osce_improvement,
            "emr": emr_improvement,
        }
        best_mode = max(improvements, key=improvements.get)

        return {
            "total_weeks": len(trends),
            "mcq_improvement": round(mcq_improvement, 1),
            "osce_improvement": round(osce_improvement, 1),
            "emr_improvement": round(emr_improvement, 1),
            "best_practice_mode": best_mode,
        }


class WeakAreasService:
    """Service for identifying weak EMR specialties"""

    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def get_weak_areas(self, limit: int = 5, threshold: float = 70.0) -> dict:
        """Get weak EMR specialties (cached 5min)"""
        cache_key = f"weak-areas:emr:{self.user_id}"

        # Try cache
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached

        # Query weak specialties
        result = await self.db.execute(
            select(
                MockPatient.specialty,
                func.count(EMRSession.id).label("session_count"),
                func.avg(EMRValidation.total_amc_score).label("avg_score"),
            )
            .select_from(EMRSession)
            .join(MockPatient, EMRSession.patient_id == MockPatient.id)
            .join(EMRValidation, EMRSession.id == EMRValidation.session_id)
            .where(
                EMRSession.user_id == self.user_id,
                EMRSession.completed_at.isnot(None),
            )
            .group_by(MockPatient.specialty)
            .having(func.avg(EMRValidation.total_amc_score) < threshold)
            .order_by(func.avg(EMRValidation.total_amc_score).asc())
            .limit(limit)
        )

        weak_areas = [
            {
                "specialty": row.specialty,
                "session_count": row.session_count,
                "avg_score": round(row.avg_score, 1),
                "gap_to_target": round(80.0 - row.avg_score, 1),
                "recommended_practice_count": max(3, int((80.0 - row.avg_score) / 5)),
            }
            for row in result
        ]

        # Count total weak areas
        total_result = await self.db.execute(
            select(func.count().label("total"))
            .select_from(
                select(MockPatient.specialty)
                .select_from(EMRSession)
                .join(MockPatient, EMRSession.patient_id == MockPatient.id)
                .join(EMRValidation, EMRSession.id == EMRValidation.session_id)
                .where(
                    EMRSession.user_id == self.user_id,
                    EMRSession.completed_at.isnot(None),
                )
                .group_by(MockPatient.specialty)
                .having(func.avg(EMRValidation.total_amc_score) < threshold)
                .subquery()
            )
        )
        total = total_result.scalar() or 0

        response = {
            "weak_areas": weak_areas,
            "total_weak_areas": total,
            "has_more": total > limit,
        }

        # Cache for 5 minutes
        await cache_manager.set(cache_key, response, ttl=300)

        return response
```

---

## L - LOOP (Implementation Phases)

### Phase 1: Foundation (3-4 hours)

**Goal**: Set up API router, Pydantic schemas, database indexes

**Tasks**:
1. Create `/backend/src/api/v1/progress.py` router
2. Define Pydantic schemas (EMRDashboardMetrics, UnifiedWeeklyTrend, WeakArea)
3. Add database indexes:
   ```sql
   CREATE INDEX idx_emr_sessions_user_completed
   ON emr_sessions(user_id, completed_at)
   WHERE completed_at IS NOT NULL;

   CREATE INDEX idx_emr_validations_session
   ON emr_validations(session_id);
   ```
4. Set up Redis caching utility (`cache_manager.py`)

**Verification**:
- API router registered in `main.py`
- Schemas pass Pydantic validation tests
- Database indexes created (check `EXPLAIN ANALYZE`)
- Redis connection works (pytest test)

---

### Phase 2: Core Implementation (4-5 hours)

**Goal**: Implement 3 endpoints + service layer

**Tasks**:
1. Implement `EMRAnalyticsService` (dashboard metrics)
2. Implement `UnifiedTrendsService` (weekly trends)
3. Implement `WeakAreasService` (weak areas)
4. Create FastAPI endpoints (call services)
5. Add JWT authentication middleware
6. Add error handling (try/except, 500 responses)

**Verification**:
- All 3 endpoints return valid JSON
- Services return correct data structure
- JWT auth blocks unauthorized requests
- Error responses have proper status codes

---

### Phase 3: Testing & Optimization (1-2 hours)

**Goal**: Achieve ≥70% test coverage, <500ms response time

**Tasks**:
1. Write pytest tests:
   - Unit tests for services (mock database)
   - Integration tests for endpoints (test database)
   - Cache hit/miss tests
2. Load testing (100 concurrent users with `locust`)
3. Query optimization (check `EXPLAIN ANALYZE`, add indexes if needed)
4. Cache tuning (adjust TTL based on load test results)

**Verification**:
- `pytest --cov` shows ≥70% coverage
- All tests pass (100% pass rate)
- Load test: p95 <500ms for all endpoints
- Cache hit rate >80% in load test

---

## P - PLAN (Task Breakdown)

### Task 1.1: API Router Setup (30min)
- [ ] Create `backend/src/api/v1/progress.py`
- [ ] Register router in `main.py`
- [ ] Add APIRouter with JWT dependency
- [ ] Test: `curl localhost:8001/api/v1/progress/health` → 200 OK

### Task 1.2: Pydantic Schemas (45min)
- [ ] Create `backend/src/schemas/progress.py`
- [ ] Define `EMRDashboardMetrics` schema
- [ ] Define `UnifiedWeeklyTrend` schema
- [ ] Define `WeakArea` schema
- [ ] Write schema validation tests
- [ ] Test: `pytest tests/test_schemas/test_progress.py` → 100% pass

### Task 1.3: Database Indexes (30min)
- [ ] Create Alembic migration `011_add_progress_indexes.py`
- [ ] Add indexes for (user_id, completed_at)
- [ ] Run migration on dev database
- [ ] Test: `EXPLAIN ANALYZE` shows index usage
- [ ] Verify: Query time <100ms with indexes

### Task 1.4: Redis Caching (45min)
- [ ] Create `backend/src/cache/manager.py`
- [ ] Implement `cache_manager.get()`, `cache_manager.set()`
- [ ] Add connection pooling
- [ ] Write cache tests (set, get, expire)
- [ ] Test: `pytest tests/test_cache/` → 100% pass

### Task 2.1: EMRAnalyticsService (90min)
- [ ] Create `backend/src/services/emr_analytics.py`
- [ ] Implement `get_dashboard_metrics()`
- [ ] Implement `_get_session_counts()` query
- [ ] Implement `_get_performance_metrics()` query
- [ ] Implement `_calculate_improvement()` subquery
- [ ] Implement `_get_specialty_breakdown()` query
- [ ] Add caching (5min TTL)
- [ ] Test: Service returns correct structure

### Task 2.2: UnifiedTrendsService (90min)
- [ ] Implement `UnifiedTrendsService` class
- [ ] Implement `get_weekly_trends(weeks=12)`
- [ ] Implement `_get_mcq_weekly()` query
- [ ] Implement `_get_osce_weekly()` query
- [ ] Implement `_get_emr_weekly()` query
- [ ] Implement `_merge_trends()` logic
- [ ] Implement `_calculate_summary()` logic
- [ ] Add caching (10min TTL)
- [ ] Test: Service merges data correctly

### Task 2.3: WeakAreasService (60min)
- [ ] Implement `WeakAreasService` class
- [ ] Implement `get_weak_areas(limit=5, threshold=70.0)`
- [ ] Implement weak specialty query
- [ ] Calculate gap_to_target and recommended_practice_count
- [ ] Add caching (5min TTL)
- [ ] Test: Service identifies weak areas correctly

### Task 2.4: FastAPI Endpoints (60min)
- [ ] Implement `GET /progress/dashboard/emr`
- [ ] Implement `GET /progress/weekly-trends/unified`
- [ ] Implement `GET /progress/weak-areas/emr`
- [ ] Add JWT authentication to all endpoints
- [ ] Add error handling (try/except, 500 responses)
- [ ] Test: `curl` requests return valid JSON

### Task 3.1: Unit Tests (60min)
- [ ] Write tests for `EMRAnalyticsService` (mock DB)
- [ ] Write tests for `UnifiedTrendsService` (mock DB)
- [ ] Write tests for `WeakAreasService` (mock DB)
- [ ] Test cache hit/miss scenarios
- [ ] Test: `pytest --cov` → ≥70% coverage

### Task 3.2: Integration Tests (30min)
- [ ] Write endpoint tests (TestClient)
- [ ] Test JWT auth (401 on missing token)
- [ ] Test query parameters (weeks, limit, threshold)
- [ ] Test: All integration tests pass

### Task 3.3: Load Testing (30min)
- [ ] Create `locustfile.py` for 100 concurrent users
- [ ] Run load test (5min duration)
- [ ] Measure p95 response time
- [ ] Check cache hit rate (Redis metrics)
- [ ] Verify: p95 <500ms, cache hit >80%

---

## H - HANDOFF (Acceptance Criteria)

### API Functionality
- [ ] **3 endpoints implemented**: `/dashboard/emr`, `/weekly-trends/unified`, `/weak-areas/emr`
- [ ] **JWT auth works**: 401 response on missing/invalid token
- [ ] **Query parameters validated**: Bad requests return 400
- [ ] **Error handling**: 500 errors caught, logged, returned as JSON

### Performance
- [ ] **Response time <500ms** (p95) for all endpoints
- [ ] **Cache hit rate >80%** in load test
- [ ] **Database queries <100ms** (indexed queries)
- [ ] **Concurrent users: 100+** without degradation

### Data Quality
- [ ] **Dashboard metrics accurate**: Matches manual SQL query
- [ ] **Weekly trends correct**: Data merges properly across MCQ/OSCE/EMR
- [ ] **Weak areas valid**: Only specialties <70% threshold returned
- [ ] **Caching works**: Subsequent requests hit cache (measured)

### Testing
- [ ] **Test coverage ≥70%**: Pytest coverage report
- [ ] **100% test pass rate**: Zero failures
- [ ] **Load test passed**: 100 concurrent users, <500ms p95
- [ ] **Integration tests pass**: All endpoints return valid JSON

### Documentation
- [ ] **API docs updated**: Swagger UI shows 3 new endpoints
- [ ] **Schema examples added**: Request/response examples in docs
- [ ] **Cache strategy documented**: TTL values, invalidation logic
- [ ] **Performance benchmarks**: Response times, cache hit rates

### Code Quality
- [ ] **Follows FastAPI patterns**: Consistent with osces.py, mcqs.py
- [ ] **Type hints added**: All functions have type annotations
- [ ] **Error messages clear**: No stack traces leaked to client
- [ ] **Logging added**: Info logs for cache hits, warning logs for slow queries

---

## Success Criteria

**MUST HAVE**:
1. All 3 endpoints return valid JSON matching Pydantic schemas
2. JWT authentication blocks unauthorized requests (401)
3. Response time <500ms (p95) under 100 concurrent users
4. Cache hit rate >80% in load test
5. Test coverage ≥70%, 100% pass rate
6. Database queries use indexes (<100ms)

**SHOULD HAVE**:
7. Error responses include helpful messages (not just status codes)
8. API docs (Swagger UI) updated with examples
9. Load test results documented (p95, cache metrics)
10. Code follows project conventions (same as osces.py)

**NICE TO HAVE**:
11. Cache invalidation hooks (clear cache on session completion)
12. Query result pagination (limit 1000 rows max)
13. Monitoring metrics (Prometheus/Grafana integration)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Complex SQL queries slow** | Medium | High | Add indexes first, profile queries, use EXPLAIN ANALYZE |
| **Cache stampede** | Low | Medium | Use lock-based caching (only 1 request recalculates) |
| **Missing data** (no MCQ/OSCE sessions) | Medium | Low | Return null/empty arrays gracefully |
| **Redis connection failure** | Low | High | Fallback to no caching (direct DB query) |
| **Timezone issues** (week_start calculation) | Medium | Medium | Use UTC consistently, test with different timezones |

---

## Dependencies

**Required Before Starting**:
- ✅ PRD_BACKEND_001 complete (emr_sessions, user_progress tables exist)
- ✅ PRD_BACKEND_002 complete (session data populated)
- ✅ Redis installed and running (localhost:6379)
- ✅ PostgreSQL indexes tuned (connection pooling configured)

**Blocks**:
- ❌ PRD_FRONTEND_003 (EMR Dashboard Integration - needs these APIs)
- ❌ PRD_INTEGRATION_002 (Unified Progress Tracking - depends on trends API)

---

## Testing Strategy

### Unit Tests (Services)
```python
# tests/services/test_emr_analytics.py

import pytest
from backend.src.services.emr_analytics import EMRAnalyticsService

@pytest.mark.asyncio
async def test_get_dashboard_metrics(mock_db, sample_user_id):
    service = EMRAnalyticsService(db=mock_db, user_id=sample_user_id)

    # Mock database to return 10 sessions, 8 completed
    mock_db.execute.return_value.one.return_value = {
        "total_sessions": 10,
        "completed_sessions": 8,
        "avg_score": 75.5,
        # ...
    }

    metrics = await service.get_dashboard_metrics()

    assert metrics["total_sessions"] == 10
    assert metrics["completed_sessions"] == 8
    assert metrics["avg_validation_score"] == 75.5
    assert "specialty_stats" in metrics
```

### Integration Tests (Endpoints)
```python
# tests/api/test_progress.py

from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)

def test_get_emr_dashboard_metrics_unauthorized():
    response = client.get("/api/v1/progress/dashboard/emr")
    assert response.status_code == 401

def test_get_emr_dashboard_metrics_success(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/progress/dashboard/emr", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "avg_validation_score" in data
    assert isinstance(data["specialty_stats"], list)
```

### Load Tests (Locust)
```python
# locustfile.py

from locust import HttpUser, task, between

class DashboardUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login to get JWT token
        response = self.client.post("/api/v1/auth/login", json={
            "username": "student@example.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def get_emr_metrics(self):
        self.client.get(
            "/api/v1/progress/dashboard/emr",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(2)
    def get_weekly_trends(self):
        self.client.get(
            "/api/v1/progress/weekly-trends/unified?weeks=12",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def get_weak_areas(self):
        self.client.get(
            "/api/v1/progress/weak-areas/emr",
            headers={"Authorization": f"Bearer {self.token}"}
        )

# Run: locust -f locustfile.py --users 100 --spawn-rate 10
```

---

## Deployment Checklist

**Before Deploying**:
- [ ] All tests pass (pytest, integration, load)
- [ ] Database migrations applied (011_add_progress_indexes)
- [ ] Redis configured and running
- [ ] Environment variables set (REDIS_URL, DATABASE_URL)
- [ ] API docs reviewed (Swagger UI)

**After Deploying**:
- [ ] Smoke test all 3 endpoints (production)
- [ ] Monitor response times (Grafana dashboard)
- [ ] Check cache hit rate (Redis INFO stats)
- [ ] Monitor error logs (Sentry/CloudWatch)
- [ ] Notify frontend team (endpoints ready for integration)

---

## Appendix: API Response Examples

### Dashboard Metrics Response
```json
{
  "total_sessions": 45,
  "completed_sessions": 42,
  "in_progress_sessions": 3,
  "avg_validation_score": 78.5,
  "avg_typing_wpm": 42.3,
  "improvement_percentage": 12.5,
  "ahpra_compliance_rate": 85.7,
  "total_time_spent_seconds": 18000,
  "epic_sessions": 25,
  "cerner_sessions": 20,
  "specialty_stats": [
    {
      "specialty": "Cardiology",
      "session_count": 12,
      "avg_score": 82.0
    },
    {
      "specialty": "Respiratory",
      "session_count": 10,
      "avg_score": 75.5
    }
  ]
}
```

### Weekly Trends Response
```json
{
  "trends": [
    {
      "week_start": "2026-01-13",
      "mcq_accuracy": 72.5,
      "osce_avg_score": 68.0,
      "emr_avg_score": 65.3,
      "mcq_attempts": 45,
      "osce_completions": 3,
      "emr_sessions": 5
    }
  ],
  "summary": {
    "total_weeks": 12,
    "mcq_improvement": 12.5,
    "osce_improvement": 8.3,
    "emr_improvement": 15.2,
    "best_practice_mode": "emr"
  }
}
```

### Weak Areas Response
```json
{
  "weak_areas": [
    {
      "specialty": "Neurology",
      "session_count": 8,
      "avg_score": 62.5,
      "gap_to_target": 17.5,
      "recommended_practice_count": 5
    }
  ],
  "total_weak_areas": 3,
  "has_more": false
}
```

---

**END OF PRD_BACKEND_005**
