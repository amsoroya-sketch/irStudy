# PRD: Unified Progress Tracking - Cross-Module Analytics

**PRD ID**: PRD_INTEGRATION_002_UNIFIED_PROGRESS_TRACKING
**Category**: Integration
**Priority**: P1-High (critical for holistic student assessment)
**Estimated Effort**: 11-14 hours
**Dependencies**: 
- PRD_BACKEND_001 (EMR Database Migration - user_progress EMR columns)
- PRD_FRONTEND_003 (EMR Dashboard Integration - UnifiedProgressChart already specified)
- PRD_BACKEND_002 (EMR Session API - session data for analytics)

**Blocks**:
- PRD_FRONTEND_005 (EMR Analytics Deep Dive - detailed reports)
- PRD_INTEGRATION_003 (Predictive Study Planning - AI-powered recommendations)

**Status**: Ready for Implementation

---

## R - REQUEST (What & Why)

### User Story

**As a** medical student preparing for AMC Clinical Examination
**I want** a unified analytics dashboard showing my progress across MCQ, OSCE, and EMR practice modes
**So that** I can identify cross-module patterns, track overall competency improvement, and optimize my study strategy for balanced AMC preparation

### Business Context

**Current State**:
- MCQ progress tracked in `user_progress` table (total_mcqs_attempted, total_mcqs_correct, mastery_percentage)
- OSCE progress tracked in same table (total_osces_practiced, average_osce_score)
- EMR progress will be tracked in 17 new columns (PRD_BACKEND_001: emr_sessions_total, emr_avg_validation_score, emr_improvement_percentage, etc.)
- **BUT**: No unified view combining all 3 modules
- **BUT**: No cross-module correlation analysis (e.g., "Are students good at MCQ but weak at EMR?")
- **BUT**: No learning velocity tracking (improvement rate per week)
- **BUT**: No specialty heatmap showing strengths/weaknesses across all modules

**Problem - Siloed Progress Tracking**:
1. **Fragmented View**: Students see MCQ dashboard, OSCE dashboard, EMR dashboard separately - can't identify holistic patterns
2. **No Cross-Module Insights**: Can't answer questions like:
   - "I'm 85% in MCQ Cardiology but 60% in EMR Cardiology - why the gap?"
   - "My OSCE communication score is high but EMR SOAP notes are weak - what's missing?"
   - "Which specialty should I prioritize across all 3 modules?"
3. **No Learning Velocity**: Students don't know if they're improving fast enough to be exam-ready
4. **No Predictive Insights**: Can't estimate "How many weeks until I reach 80% across all modules?"
5. **No Optimal Study Pattern Detection**: Can't identify best time of day, session length, or module sequence

**Desired State - Unified Progress Analytics**:
- **Single Overall Score**: Weighted average (30% MCQ + 30% OSCE + 40% EMR) showing holistic competency
- **Cross-Module Correlation**: Identify strengths in one module that don't transfer to others
- **Specialty Heatmap**: 3×10 grid (rows: MCQ/OSCE/EMR, columns: 10 specialties) showing performance across modules
- **Learning Velocity Chart**: Track weekly improvement rate (% per week) across all modules
- **Predictive Timeline**: Estimate weeks to reach 80% mastery across all modules
- **Study Pattern Insights**: Optimal session length, best study time, recommended module sequence
- **Gap Analysis**: Identify specialties strong in MCQ but weak in OSCE/EMR (actionable insights)

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Response Time** | Unified progress endpoint <200ms | p95 latency with caching |
| **Analytics Accuracy** | Correlation coefficients ±0.05 tolerance | Validated against scipy.stats |
| **Cache Effectiveness** | 95%+ cache hit rate | Redis monitoring |
| **Dashboard Load Time** | Full analytics dashboard <2s | Lighthouse performance score |
| **User Engagement** | 60%+ students check weekly | Analytics tracking |
| **Insight Actionability** | 70%+ students act on gap analysis | Survey + behavioral tracking |

### Scope

**In Scope**:

1. **Backend Analytics Aggregation** (5-6 hours):
   - Unified progress API endpoint (single call for all modules)
   - Cross-module correlation calculation (MCQ vs OSCE vs EMR)
   - Learning velocity calculation (weekly improvement rate)
   - Specialty heatmap data aggregation (3×10 grid)
   - Study pattern analysis (optimal session length, best time of day)
   - Predictive analytics (estimated weeks to 80% mastery)
   - Background job for analytics calculation (daily refresh)

2. **Database Schema Extension** (1-2 hours):
   - New `user_analytics` table (stores calculated metrics)
   - Indexes for fast user lookups
   - JSONB for specialty heatmap data

3. **Caching Strategy** (1 hour):
   - Redis caching for unified progress (1-hour TTL)
   - Cache invalidation on new MCQ/OSCE/EMR activity
   - Cache warming for active users

4. **Frontend Dashboard Widgets** (4-5 hours):
   - OverallProgressCard (single weighted score)
   - LearningVelocityChart (weekly improvement trends)
   - SpecialtyHeatmap (3×10 grid component)
   - StudyPatternInsights (optimal study recommendations)
   - GapAnalysisPanel (cross-module weaknesses)

**Out of Scope** (Future Iterations):
- Social features (peer comparison, leaderboards) - Privacy concerns, separate PRD
- AI-powered study plan generator - Separate PRD_INTEGRATION_003
- Export progress to PDF report - Future enhancement
- Mobile app analytics dashboard - Separate mobile PRD
- Historical analytics beyond 12 weeks - Future optimization

---

## A - ARCHITECTURE (How)

### Technical Approach

Create unified analytics aggregation service that:
1. Reads from existing `user_progress` table (MCQ + OSCE + EMR columns)
2. Calculates cross-module metrics (overall score, correlation, velocity)
3. Stores results in new `user_analytics` table
4. Caches frequently accessed data in Redis (1-hour TTL)
5. Exposes via single unified API endpoint
6. Updates via background job (daily calculation at 2 AM)
7. Invalidates cache on user activity (new MCQ attempt, OSCE completion, EMR session)

### System Design

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 UNIFIED PROGRESS TRACKING ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────────────┘

DATA LAYER:
  │
  ├─► PostgreSQL Tables
  │   ├─ user_progress (existing)
  │   │  ├─ MCQ columns: total_mcqs_attempted, total_mcqs_correct
  │   │  ├─ OSCE columns: total_osces_practiced, average_osce_score
  │   │  └─ EMR columns: emr_sessions_total, emr_avg_validation_score, etc.
  │   │
  │   └─ user_analytics (NEW)
  │      ├─ overall_score (weighted average)
  │      ├─ learning_velocity (% improvement/week)
  │      ├─ mcq_osce_correlation, mcq_emr_correlation, osce_emr_correlation
  │      ├─ optimal_session_length_minutes
  │      ├─ best_study_time_hour
  │      ├─ specialty_heatmap (JSONB)
  │      └─ estimated_weeks_to_80_percent
  │
  └─► Redis Cache (1-hour TTL)
      └─ Key: "unified_progress:{user_id}" → Full analytics JSON

COMPUTATION LAYER:
  │
  ├─► Analytics Service (backend/src/services/analytics_service.py)
  │   ├─ calculate_overall_score() → Weighted: 30% MCQ + 30% OSCE + 40% EMR
  │   ├─ calculate_correlations() → Pearson correlation coefficients
  │   ├─ calculate_learning_velocity() → Weekly % improvement (12-week moving avg)
  │   ├─ build_specialty_heatmap() → 3×10 grid (modules × specialties)
  │   ├─ analyze_study_patterns() → Optimal session length, best time of day
  │   └─ predict_time_to_mastery() → Estimated weeks to 80% across all modules
  │
  └─► Background Job (Celery scheduled task)
      └─ Task: recalculate_user_analytics (runs daily at 2 AM for active users)

API LAYER:
  │
  ├─► GET /api/v1/progress/unified (NEW)
  │   Response: {
  │     overall_score: 78.5,
  │     breakdown: { mcq: 82.3, osce: 77.1, emr: 75.4 },
  │     cross_module_insights: {
  │       correlation_mcq_emr: 0.68,
  │       learning_velocity: 2.3,
  │       study_time_total_hours: 45.5,
  │       optimal_session_length_minutes: 35
  │     },
  │     last_calculated_at: "2026-02-16T10:30:00Z"
  │   }
  │
  ├─► GET /api/v1/progress/specialty-heatmap (NEW)
  │   Response: {
  │     specialties: ["Cardiology", "Neurology", ...],
  │     modules: ["MCQ", "OSCE", "EMR"],
  │     scores: [
  │       [82, 75, 70],  // Cardiology: MCQ 82%, OSCE 75%, EMR 70%
  │       [65, 68, 72],  // Neurology
  │       ...
  │     ],
  │     gaps: [
  │       { specialty: "Cardiology", strong_in: "MCQ", weak_in: "EMR", gap: 12 }
  │     ]
  │   }
  │
  └─► GET /api/v1/progress/learning-velocity?weeks=12 (NEW)
      Response: {
        weeks: [
          {
            week_start: "2026-01-01",
            mcq_improvement: +5.2,
            osce_improvement: +3.1,
            emr_improvement: +4.5,
            overall_velocity: +4.3
          },
          ...
        ],
        trend: "accelerating",  // "accelerating" | "steady" | "slowing"
        estimated_weeks_to_80_percent: 6
      }

PRESENTATION LAYER (Frontend):
  │
  ├─► OverallProgressCard (new component)
  │   └─ Display: Overall score + breakdown (MCQ/OSCE/EMR)
  │
  ├─► LearningVelocityChart (new component)
  │   └─ Recharts line chart: 3 lines (MCQ, OSCE, EMR velocity) + target line (3%/week)
  │
  ├─► SpecialtyHeatmap (new component)
  │   └─ MUI Grid: 3×10 cells, color-coded (Green ≥80%, Yellow 60-80%, Red <60%)
  │
  ├─► StudyPatternInsights (new component)
  │   └─ Recommendations: Optimal session length, best study time, predicted timeline
  │
  └─► GapAnalysisPanel (new component)
      └─ List: Specialties with >10% gap between modules (actionable insights)

BACKGROUND PROCESSING:
  │
  └─► Celery Beat Schedule
      └─ recalculate_user_analytics: Daily at 2 AM
         ├─ Fetch all active users (activity in last 7 days)
         ├─ Calculate analytics for each user
         ├─ Upsert to user_analytics table
         ├─ Invalidate Redis cache
         └─ Log completion metrics
```

### Database Schema Details

#### New Table: user_analytics

```sql
CREATE TABLE IF NOT EXISTS user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    calculated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Overall Metrics (derived from MCQ + OSCE + EMR)
    overall_score NUMERIC(5,2),  -- Weighted average (0-100)
    overall_study_hours NUMERIC(7,2),  -- Total across all modules
    learning_velocity NUMERIC(5,2),  -- % improvement per week (12-week moving avg)

    -- Cross-Module Correlations (Pearson r, range -1 to +1)
    mcq_osce_correlation NUMERIC(4,3),
    mcq_emr_correlation NUMERIC(4,3),
    osce_emr_correlation NUMERIC(4,3),

    -- Optimal Study Patterns (detected from user behavior)
    optimal_session_length_minutes INTEGER,  -- e.g., 35 (best performance)
    best_study_time_hour INTEGER,  -- 0-23 (24-hour format, e.g., 14 = 2 PM)
    avg_sessions_per_week NUMERIC(4,2),  -- e.g., 5.3

    -- Predictive Analytics
    estimated_weeks_to_80_percent INTEGER,  -- Weeks to reach 80% across all modules
    current_trajectory VARCHAR(20) CHECK (current_trajectory IN ('accelerating', 'steady', 'slowing')),

    -- Specialty Performance Heatmap (JSONB for flexibility)
    specialty_heatmap JSONB,
    -- Example: {
    --   "cardiology": {"mcq": 82, "osce": 75, "emr": 70},
    --   "neurology": {"mcq": 65, "osce": 68, "emr": 72},
    --   ...
    -- }

    -- Gap Analysis (specialties with >10% gap between modules)
    identified_gaps JSONB,
    -- Example: [
    --   {"specialty": "Cardiology", "strong_in": "MCQ", "weak_in": "EMR", "gap": 12},
    --   {"specialty": "Neurology", "strong_in": "OSCE", "weak_in": "MCQ", "gap": 15}
    -- ]

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    UNIQUE(user_id, calculated_at)
);

-- Indexes for fast lookups
CREATE INDEX idx_user_analytics_user_latest 
    ON user_analytics(user_id, calculated_at DESC);

CREATE INDEX idx_user_analytics_trajectory 
    ON user_analytics(current_trajectory) 
    WHERE current_trajectory IN ('slowing', 'steady');
```

### API Endpoint Specifications

#### Endpoint 1: GET /api/v1/progress/unified

**Purpose**: Single endpoint returning all unified progress data

**Authentication**: JWT required

**Request**:
```http
GET /api/v1/progress/unified HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "overall_score": 78.5,
  "breakdown": {
    "mcq": {
      "score": 82.3,
      "weight": 0.30,
      "contribution": 24.69
    },
    "osce": {
      "score": 77.1,
      "weight": 0.30,
      "contribution": 23.13
    },
    "emr": {
      "score": 75.4,
      "weight": 0.40,
      "contribution": 30.16
    }
  },
  "mcq_progress": {
    "total_attempts": 450,
    "accuracy_rate": 82.3,
    "unique_mcqs_attempted": 320,
    "weak_specialties": ["Cardiology", "Neurology"]
  },
  "osce_progress": {
    "total_completions": 35,
    "pass_rate": 77.1,
    "average_score": 11.56,
    "weak_specialties": ["Respiratory"]
  },
  "emr_progress": {
    "sessions_completed": 18,
    "avg_validation_score": 75.4,
    "avg_typing_wpm": 42,
    "ahpra_compliance_rate": 88.5,
    "weak_specialties": ["Emergency Medicine"]
  },
  "cross_module_insights": {
    "correlation_mcq_emr": 0.68,
    "correlation_mcq_osce": 0.72,
    "correlation_osce_emr": 0.65,
    "learning_velocity": 2.3,
    "study_time_total_hours": 45.5,
    "optimal_session_length_minutes": 35,
    "best_study_time_hour": 14,
    "current_trajectory": "accelerating",
    "estimated_weeks_to_80_percent": 6
  },
  "last_calculated_at": "2026-02-16T10:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing JWT
- `404 Not Found`: No analytics data for user (suggest running calculation)
- `500 Internal Server Error`: Analytics calculation failed

**Caching**:
- Redis key: `unified_progress:{user_id}`
- TTL: 1 hour
- Invalidation: On new MCQ attempt, OSCE completion, EMR session

**Performance Target**: <200ms (p95) with cache hit

---

#### Endpoint 2: GET /api/v1/progress/specialty-heatmap

**Purpose**: Return specialty performance heatmap (3×10 grid)

**Authentication**: JWT required

**Request**:
```http
GET /api/v1/progress/specialty-heatmap HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "specialties": [
    "Cardiology",
    "Neurology",
    "Respiratory",
    "Emergency Medicine",
    "Gastroenterology",
    "Endocrinology",
    "Psychiatry",
    "Obstetrics & Gynaecology",
    "Paediatrics",
    "General Practice"
  ],
  "modules": ["MCQ", "OSCE", "EMR"],
  "scores": [
    [82, 75, 70],  // Cardiology
    [65, 68, 72],  // Neurology
    [78, 82, 75],  // Respiratory
    [70, 65, 60],  // Emergency Medicine
    [88, 85, 82],  // Gastroenterology
    [75, 70, 73],  // Endocrinology
    [80, 78, 76],  // Psychiatry
    [72, 75, 68],  // Obstetrics & Gynaecology
    [85, 80, 78],  // Paediatrics
    [90, 88, 85]   // General Practice
  ],
  "gaps": [
    {
      "specialty": "Cardiology",
      "strong_in": "MCQ",
      "weak_in": "EMR",
      "gap": 12,
      "recommendation": "Focus on EMR Cardiology sessions (SOAP notes, ECG interpretation)"
    },
    {
      "specialty": "Emergency Medicine",
      "strong_in": "MCQ",
      "weak_in": "EMR",
      "gap": 10,
      "recommendation": "Practice EMR emergency presentations (time-critical documentation)"
    }
  ],
  "overall_specialty_ranking": [
    {"specialty": "General Practice", "avg_score": 87.7},
    {"specialty": "Gastroenterology", "avg_score": 85.0},
    {"specialty": "Paediatrics", "avg_score": 81.0},
    // ...
  ]
}
```

**Color Coding Logic** (Frontend):
- Green: ≥80% (strong)
- Yellow: 60-80% (moderate)
- Red: <60% (weak)

**Performance Target**: <150ms (cached)

---

#### Endpoint 3: GET /api/v1/progress/learning-velocity

**Purpose**: Return weekly improvement trends (learning velocity)

**Authentication**: JWT required

**Query Parameters**:
- `weeks` (optional, default: 12): Number of weeks to return

**Request**:
```http
GET /api/v1/progress/learning-velocity?weeks=12 HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "weeks": [
    {
      "week_start": "2026-01-01",
      "week_number": 1,
      "mcq_score": 75.2,
      "osce_score": 70.5,
      "emr_score": 68.0,
      "mcq_improvement": null,  // First week, no baseline
      "osce_improvement": null,
      "emr_improvement": null,
      "overall_velocity": null
    },
    {
      "week_start": "2026-01-08",
      "week_number": 2,
      "mcq_score": 76.8,
      "osce_score": 72.1,
      "emr_score": 70.5,
      "mcq_improvement": +1.6,
      "osce_improvement": +1.6,
      "emr_improvement": +2.5,
      "overall_velocity": +1.9
    },
    {
      "week_start": "2026-01-15",
      "week_number": 3,
      "mcq_score": 79.5,
      "osce_score": 74.0,
      "emr_score": 72.8,
      "mcq_improvement": +2.7,
      "osce_improvement": +1.9,
      "emr_improvement": +2.3,
      "overall_velocity": +2.3
    },
    // ... up to week 12
    {
      "week_start": "2026-02-12",
      "week_number": 12,
      "mcq_score": 82.3,
      "osce_score": 77.1,
      "emr_score": 75.4,
      "mcq_improvement": +1.2,
      "osce_improvement": +1.5,
      "emr_improvement": +1.8,
      "overall_velocity": +1.5
    }
  ],
  "summary": {
    "avg_weekly_velocity_mcq": +2.1,
    "avg_weekly_velocity_osce": +1.8,
    "avg_weekly_velocity_emr": +2.3,
    "avg_weekly_velocity_overall": +2.0,
    "trend": "accelerating",
    "target_velocity": 3.0,
    "weeks_behind_target": 2
  },
  "prediction": {
    "estimated_weeks_to_80_percent": 6,
    "estimated_date": "2026-03-30",
    "confidence": "moderate",
    "assumptions": "Based on current 12-week velocity, assumes sustained practice rate"
  }
}
```

**Calculation Formulas**:

```python
# Weekly Improvement (%)
improvement = ((current_week_score - previous_week_score) / previous_week_score) * 100

# Learning Velocity (12-week moving average)
velocity = sum(last_12_weeks_improvements) / 12

# Estimated Weeks to 80%
current_score = 78.5
target_score = 80.0
gap = target_score - current_score  # 1.5
weeks_needed = gap / avg_weekly_velocity  # 1.5 / 2.0 = 0.75 ≈ 1 week

# Trajectory Classification
if velocity_trend > 0.5:  # Acceleration > 0.5% per week
    trajectory = "accelerating"
elif velocity_trend > -0.5:
    trajectory = "steady"
else:
    trajectory = "slowing"
```

**Performance Target**: <250ms (involves time-series calculation)

---

### Calculation Formulas & Algorithms

#### Formula 1: Overall Score (Weighted Average)

```python
def calculate_overall_score(user_progress: UserProgress) -> float:
    """
    Calculate overall competency score across MCQ, OSCE, EMR.
    
    Weights:
    - MCQ: 30% (theoretical knowledge)
    - OSCE: 30% (clinical skills)
    - EMR: 40% (documentation - critical for AMC Clinical Exam)
    
    Returns: Overall score (0-100)
    """
    # MCQ Score (accuracy rate)
    mcq_score = (user_progress.total_mcqs_correct / user_progress.total_mcqs_attempted * 100) 
        if user_progress.total_mcqs_attempted > 0 else 0
    
    # OSCE Score (average score, normalized to 0-100)
    # AMC rubric: 0-15 points, pass = 9/15 (60%)
    osce_score = (user_progress.average_osce_score / 15 * 100) 
        if user_progress.total_osces_practiced > 0 else 0
    
    # EMR Score (average validation score, already 0-100)
    emr_score = user_progress.emr_avg_validation_score or 0
    
    # Weighted Average
    overall_score = (
        mcq_score * 0.30 +
        osce_score * 0.30 +
        emr_score * 0.40
    )
    
    return round(overall_score, 2)
```

---

#### Formula 2: Cross-Module Correlation (Pearson Coefficient)

```python
import numpy as np
from scipy.stats import pearsonr

def calculate_cross_module_correlation(user_id: int) -> dict:
    """
    Calculate Pearson correlation coefficients between modules.
    
    Uses weekly scores (last 12 weeks) to compute correlation.
    
    Returns:
        {
            "mcq_osce_correlation": 0.72,  # Strong positive
            "mcq_emr_correlation": 0.68,   # Moderate positive
            "osce_emr_correlation": 0.65   # Moderate positive
        }
    """
    # Fetch weekly scores for last 12 weeks
    weekly_data = fetch_weekly_scores(user_id, weeks=12)
    
    mcq_scores = [w['mcq_score'] for w in weekly_data]
    osce_scores = [w['osce_score'] for w in weekly_data]
    emr_scores = [w['emr_score'] for w in weekly_data]
    
    # Minimum 5 weeks of data required for correlation
    if len(mcq_scores) < 5:
        return {
            "mcq_osce_correlation": None,
            "mcq_emr_correlation": None,
            "osce_emr_correlation": None
        }
    
    # Calculate Pearson r (correlation coefficient)
    mcq_osce_r, _ = pearsonr(mcq_scores, osce_scores)
    mcq_emr_r, _ = pearsonr(mcq_scores, emr_scores)
    osce_emr_r, _ = pearsonr(osce_scores, emr_scores)
    
    return {
        "mcq_osce_correlation": round(mcq_osce_r, 3),
        "mcq_emr_correlation": round(mcq_emr_r, 3),
        "osce_emr_correlation": round(osce_emr_r, 3)
    }
```

**Interpretation**:
- `r > 0.7`: Strong positive correlation (skills transfer well)
- `r = 0.4-0.7`: Moderate correlation (some transfer)
- `r < 0.4`: Weak correlation (skills don't transfer - identify why)

---

#### Formula 3: Learning Velocity (12-Week Moving Average)

```python
def calculate_learning_velocity(user_id: int) -> float:
    """
    Calculate learning velocity (% improvement per week).
    
    Uses 12-week moving average to smooth short-term fluctuations.
    
    Returns: Average % improvement per week (e.g., 2.3 = improving 2.3%/week)
    """
    weekly_data = fetch_weekly_scores(user_id, weeks=12)
    
    improvements = []
    for i in range(1, len(weekly_data)):
        prev_score = weekly_data[i-1]['overall_score']
        curr_score = weekly_data[i]['overall_score']
        
        if prev_score > 0:
            improvement_pct = ((curr_score - prev_score) / prev_score) * 100
            improvements.append(improvement_pct)
    
    if not improvements:
        return 0.0
    
    # 12-week moving average
    velocity = sum(improvements) / len(improvements)
    return round(velocity, 2)
```

**Target Velocity**: 3% per week (sustainable long-term improvement)

---

#### Formula 4: Specialty Heatmap Generation

```python
def build_specialty_heatmap(user_id: int) -> dict:
    """
    Build 3×10 specialty performance heatmap.
    
    Returns:
        {
            "cardiology": {"mcq": 82, "osce": 75, "emr": 70},
            "neurology": {"mcq": 65, "osce": 68, "emr": 72},
            ...
        }
    """
    specialties = [
        "Cardiology", "Neurology", "Respiratory", "Emergency Medicine",
        "Gastroenterology", "Endocrinology", "Psychiatry",
        "Obstetrics & Gynaecology", "Paediatrics", "General Practice"
    ]
    
    heatmap = {}
    
    for specialty in specialties:
        # MCQ Score (from user_progress)
        mcq_progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.specialty == specialty
        ).first()
        
        mcq_score = (mcq_progress.total_mcqs_correct / mcq_progress.total_mcqs_attempted * 100) 
            if mcq_progress and mcq_progress.total_mcqs_attempted > 0 else 0
        
        # OSCE Score (from osce_attempts joined with osces)
        osce_attempts = db.query(OSCEAttempt).join(OSCE).filter(
            OSCEAttempt.user_id == user_id,
            OSCE.specialty == specialty
        ).all()
        
        osce_score = (sum(a.total_score for a in osce_attempts) / len(osce_attempts) / 15 * 100) 
            if osce_attempts else 0
        
        # EMR Score (from emr_soap_notes joined with mock_patients)
        emr_notes = db.query(EMRSOAPNote).join(MockPatient).filter(
            EMRSOAPNote.user_id == user_id,
            MockPatient.specialty == specialty
        ).all()
        
        emr_score = (sum(n.overall_validation_score for n in emr_notes) / len(emr_notes)) 
            if emr_notes else 0
        
        heatmap[specialty.lower().replace(' ', '_')] = {
            "mcq": round(mcq_score, 1),
            "osce": round(osce_score, 1),
            "emr": round(emr_score, 1)
        }
    
    return heatmap
```

---

#### Formula 5: Gap Analysis (Identify Cross-Module Weaknesses)

```python
def identify_gaps(specialty_heatmap: dict, threshold: float = 10.0) -> list:
    """
    Identify specialties with >10% gap between modules.
    
    Returns:
        [
            {
                "specialty": "Cardiology",
                "strong_in": "MCQ",
                "weak_in": "EMR",
                "gap": 12,
                "recommendation": "Focus on EMR Cardiology sessions"
            }
        ]
    """
    gaps = []
    
    for specialty, scores in specialty_heatmap.items():
        mcq, osce, emr = scores['mcq'], scores['osce'], scores['emr']
        
        # Find strongest and weakest modules
        module_scores = {"MCQ": mcq, "OSCE": osce, "EMR": emr}
        strong_module = max(module_scores, key=module_scores.get)
        weak_module = min(module_scores, key=module_scores.get)
        
        gap = module_scores[strong_module] - module_scores[weak_module]
        
        if gap >= threshold:
            gaps.append({
                "specialty": specialty.replace('_', ' ').title(),
                "strong_in": strong_module,
                "weak_in": weak_module,
                "gap": round(gap, 1),
                "recommendation": generate_recommendation(specialty, weak_module)
            })
    
    # Sort by gap descending (largest gaps first)
    gaps.sort(key=lambda x: x['gap'], reverse=True)
    return gaps

def generate_recommendation(specialty: str, weak_module: str) -> str:
    """Generate actionable recommendation for gap."""
    templates = {
        "MCQ": f"Practice more {specialty} MCQs focusing on weak topics",
        "OSCE": f"Complete {specialty} OSCE stations to improve clinical skills",
        "EMR": f"Focus on EMR {specialty} sessions (SOAP notes, documentation)"
    }
    return templates.get(weak_module, "Continue balanced practice")
```

---

#### Formula 6: Optimal Study Pattern Detection

```python
def analyze_study_patterns(user_id: int) -> dict:
    """
    Detect optimal study patterns from user behavior.
    
    Analyzes:
    - Session length vs performance
    - Time of day vs performance
    - Module sequence vs performance
    
    Returns:
        {
            "optimal_session_length_minutes": 35,
            "best_study_time_hour": 14,  # 2 PM
            "avg_sessions_per_week": 5.3
        }
    """
    # Fetch all sessions (MCQ attempts, OSCE completions, EMR sessions)
    sessions = fetch_all_sessions(user_id, weeks=12)
    
    # Group by session length (buckets: <20, 20-30, 30-40, 40-50, 50+)
    length_performance = {}
    for session in sessions:
        length_bucket = get_length_bucket(session.duration_minutes)
        if length_bucket not in length_performance:
            length_performance[length_bucket] = []
        length_performance[length_bucket].append(session.performance_score)
    
    # Find bucket with highest average performance
    best_length_bucket = max(length_performance, 
                             key=lambda k: sum(length_performance[k]) / len(length_performance[k]))
    optimal_session_length = get_bucket_midpoint(best_length_bucket)
    
    # Group by hour of day (0-23)
    hour_performance = {}
    for session in sessions:
        hour = session.started_at.hour
        if hour not in hour_performance:
            hour_performance[hour] = []
        hour_performance[hour].append(session.performance_score)
    
    # Find hour with highest average performance
    best_study_hour = max(hour_performance, 
                          key=lambda h: sum(hour_performance[h]) / len(hour_performance[h]))
    
    # Calculate sessions per week
    total_weeks = 12
    avg_sessions_per_week = len(sessions) / total_weeks
    
    return {
        "optimal_session_length_minutes": optimal_session_length,
        "best_study_time_hour": best_study_hour,
        "avg_sessions_per_week": round(avg_sessions_per_week, 2)
    }
```

---

#### Formula 7: Predictive Time to Mastery

```python
def predict_time_to_mastery(user_id: int, target_score: float = 80.0) -> dict:
    """
    Predict weeks needed to reach 80% across all modules.
    
    Uses linear regression on last 12 weeks of data.
    
    Returns:
        {
            "estimated_weeks": 6,
            "estimated_date": "2026-03-30",
            "confidence": "moderate"
        }
    """
    weekly_data = fetch_weekly_scores(user_id, weeks=12)
    
    if len(weekly_data) < 5:
        return {
            "estimated_weeks": None,
            "estimated_date": None,
            "confidence": "insufficient_data"
        }
    
    # Extract overall scores and week numbers
    weeks = [w['week_number'] for w in weekly_data]
    scores = [w['overall_score'] for w in weekly_data]
    
    # Linear regression: score = slope * week + intercept
    slope, intercept = np.polyfit(weeks, scores, 1)
    
    # Current score (latest week)
    current_score = scores[-1]
    current_week = weeks[-1]
    
    # Calculate weeks needed
    if slope <= 0:
        return {
            "estimated_weeks": None,
            "estimated_date": None,
            "confidence": "not_improving"
        }
    
    weeks_needed = (target_score - current_score) / slope
    
    # Adjust for confidence based on R² (goodness of fit)
    r_squared = calculate_r_squared(weeks, scores, slope, intercept)
    
    if r_squared > 0.8:
        confidence = "high"
    elif r_squared > 0.5:
        confidence = "moderate"
    else:
        confidence = "low"
    
    # Calculate estimated date
    from datetime import datetime, timedelta
    estimated_date = datetime.now() + timedelta(weeks=int(weeks_needed))
    
    return {
        "estimated_weeks": max(1, int(weeks_needed)),  # Minimum 1 week
        "estimated_date": estimated_date.strftime("%Y-%m-%d"),
        "confidence": confidence,
        "r_squared": round(r_squared, 3)
    }
```

---

### Caching Architecture

#### Redis Caching Strategy

```python
# Cache Key Pattern
CACHE_KEY_UNIFIED_PROGRESS = "unified_progress:{user_id}"
CACHE_KEY_HEATMAP = "specialty_heatmap:{user_id}"
CACHE_KEY_VELOCITY = "learning_velocity:{user_id}:{weeks}"

# TTL (Time-To-Live)
CACHE_TTL_UNIFIED = 3600  # 1 hour
CACHE_TTL_HEATMAP = 7200  # 2 hours (slower changing)
CACHE_TTL_VELOCITY = 1800  # 30 minutes (frequently accessed)

# Cache Implementation
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_unified_progress_cached(user_id: int) -> dict:
    """Get unified progress with caching."""
    cache_key = f"unified_progress:{user_id}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss - calculate fresh
    progress_data = calculate_unified_progress(user_id)
    
    # Store in cache
    redis_client.setex(
        cache_key,
        CACHE_TTL_UNIFIED,
        json.dumps(progress_data)
    )
    
    return progress_data

# Cache Invalidation (on user activity)
def invalidate_progress_cache(user_id: int):
    """Invalidate cache when user completes MCQ/OSCE/EMR activity."""
    redis_client.delete(f"unified_progress:{user_id}")
    redis_client.delete(f"specialty_heatmap:{user_id}")
    redis_client.delete(f"learning_velocity:{user_id}:*")  # Wildcard delete
```

**Cache Hit Rate Target**: 95% (monitored via Redis INFO stats)

---

### Background Job Specification

#### Celery Task: Recalculate User Analytics

```python
# File: backend/src/tasks/analytics_tasks.py

from celery import shared_task
from backend.src.services.analytics_service import AnalyticsService
from backend.src.db.session import SessionLocal

@shared_task(name="recalculate_user_analytics")
def recalculate_user_analytics():
    """
    Background job to recalculate analytics for all active users.
    
    Scheduled: Daily at 2 AM (Celery Beat)
    Duration: ~5 minutes for 1000 users
    """
    db = SessionLocal()
    analytics_service = AnalyticsService(db)
    
    try:
        # Fetch active users (activity in last 7 days)
        active_users = db.query(User).filter(
            User.is_active == True,
            User.last_login_at >= datetime.now() - timedelta(days=7)
        ).all()
        
        processed = 0
        errors = 0
        
        for user in active_users:
            try:
                # Calculate analytics
                analytics_data = analytics_service.calculate_user_analytics(user.id)
                
                # Upsert to user_analytics table
                db.merge(UserAnalytics(
                    user_id=user.id,
                    calculated_at=datetime.now(),
                    **analytics_data
                ))
                db.commit()
                
                # Invalidate cache
                invalidate_progress_cache(user.id)
                
                processed += 1
            except Exception as e:
                logger.error(f"Failed to calculate analytics for user {user.id}: {e}")
                errors += 1
                continue
        
        logger.info(f"Analytics recalculation complete: {processed} users, {errors} errors")
        
    finally:
        db.close()

# Celery Beat Schedule (in celeryconfig.py)
from celery.schedules import crontab

beat_schedule = {
    'recalculate-user-analytics': {
        'task': 'recalculate_user_analytics',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

---

### Technology Stack

- **Backend**: Python 3.11 + FastAPI 0.104+
- **Database**: PostgreSQL 15 (existing instance at localhost:5433)
- **ORM**: SQLAlchemy 2.0+
- **Caching**: Redis 7.0+
- **Background Jobs**: Celery 5.3+ with Redis broker
- **Analytics Libraries**: NumPy 1.24+, SciPy 1.11+ (for correlation)
- **Frontend**: React 19.2 + TypeScript 5.3
- **Charts**: Recharts 2.15.4 (existing)
- **UI Framework**: Material-UI v7 (existing)
- **Data Fetching**: TanStack Query v5 (existing)

### Integration Points

- **Integrates with**:
  - Existing `user_progress` table (MCQ + OSCE + EMR columns)
  - Existing MCQ attempts data
  - Existing OSCE attempts data
  - New EMR sessions data (PRD_BACKEND_002)
- **Consumed by**:
  - Dashboard frontend (PRD_FRONTEND_003)
  - Future analytics deep dive (PRD_FRONTEND_005)
  - Future predictive study planner (PRD_INTEGRATION_003)
- **Depends on**:
  - Redis instance (caching)
  - Celery worker (background jobs)
  - PostgreSQL database (analytics storage)

### Security Considerations

- [x] Authentication: All endpoints require JWT
- [x] Authorization: Users can only access own analytics (user_id from JWT)
- [x] No PHI exposure: Analytics data doesn't include personal health information
- [x] Rate limiting: 100 requests/minute per user (prevent abuse)
- [x] SQL injection prevention: Parameterized queries (SQLAlchemy ORM)
- [x] Cache security: Redis password-protected, no sensitive data in cache keys
- [x] Background job security: Celery tasks don't log user PII

### Performance Requirements

- **Unified Progress API**: <200ms (p95) with cache hit
- **Specialty Heatmap API**: <150ms (cached)
- **Learning Velocity API**: <250ms (time-series calculation)
- **Cache Hit Rate**: ≥95% for frequently accessed data
- **Background Job Duration**: <10 minutes for 1000 users
- **Database Query Performance**: All queries <50ms with indexes
- **Dashboard Load Time**: Full analytics dashboard <2 seconds

---

## L - LOOP (Iterative Development)

### Phase 1: Backend Analytics Foundation (45% of effort, 5-6 hours)

**Goal**: Build analytics calculation service and database schema

**Tasks**:
1. Create `user_analytics` table (Alembic migration) - 1 hour
2. Implement `AnalyticsService` class (7 calculation methods) - 2.5 hours
3. Create 3 API endpoints (unified, heatmap, velocity) - 1.5 hours
4. Write unit tests for calculation formulas - 1 hour

**Validation Gate**:
- [ ] `user_analytics` table created with all columns
- [ ] AnalyticsService calculates overall score correctly (±0.1 tolerance)
- [ ] Correlation coefficients validated against scipy.stats
- [ ] Learning velocity calculation tested (12-week moving avg)
- [ ] Specialty heatmap generation tested (3×10 grid)
- [ ] Gap analysis identifies >10% gaps correctly
- [ ] Study pattern detection returns optimal session length
- [ ] Time to mastery prediction uses linear regression
- [ ] All 3 API endpoints return expected JSON structure
- [ ] Unit tests ≥70% coverage

---

### Phase 2: Caching & Background Jobs (25% of effort, 3-4 hours)

**Goal**: Implement Redis caching and Celery background job

**Tasks**:
1. Setup Redis caching for unified progress - 1 hour
2. Implement cache invalidation on user activity - 30 minutes
3. Create Celery task for daily analytics recalculation - 1.5 hours
4. Test cache hit rate and performance - 1 hour

**Validation Gate**:
- [ ] Redis caching working (1-hour TTL)
- [ ] Cache invalidation triggers on MCQ/OSCE/EMR activity
- [ ] Celery task runs successfully (daily at 2 AM)
- [ ] Background job processes 1000 users in <10 minutes
- [ ] Cache hit rate ≥95% in testing
- [ ] API response time <200ms with cache hit
- [ ] Cache warming tested for active users

---

### Phase 3: Frontend Dashboard Widgets (30% of effort, 4-5 hours)

**Goal**: Build 5 new dashboard components

**Tasks**:
1. Create `OverallProgressCard` component - 1 hour
2. Create `LearningVelocityChart` component (Recharts) - 1.5 hours
3. Create `SpecialtyHeatmap` component (MUI Grid) - 1.5 hours
4. Create `StudyPatternInsights` component - 30 minutes
5. Create `GapAnalysisPanel` component - 30 minutes
6. Write component tests (Jest + React Testing Library) - 1 hour

**Validation Gate**:
- [ ] OverallProgressCard displays weighted score + breakdown
- [ ] LearningVelocityChart shows 3 lines (MCQ, OSCE, EMR) + target line
- [ ] SpecialtyHeatmap renders 3×10 grid with color coding
- [ ] StudyPatternInsights shows optimal session length + best study time
- [ ] GapAnalysisPanel lists specialties with >10% gaps
- [ ] All components responsive (mobile + desktop)
- [ ] Component tests ≥70% coverage
- [ ] Accessibility: WCAG 2.2 AA compliance (keyboard nav, ARIA labels)
- [ ] Dashboard loads in <2 seconds
- [ ] TanStack Query integration working (5min staleTime)

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks

**Task 1.1**: Create Alembic Migration for user_analytics Table

- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Alembic migration file `20260216_XXXX_add_user_analytics.py`
- **Dependencies**: None
- **Command**:
  ```bash
  cd /home/dev/Development/irStudy/backend
  source venv/bin/activate
  alembic revision -m "add_user_analytics_table"
  ```
- **Acceptance Criteria**:
  - [ ] user_analytics table created with 15 columns
  - [ ] Foreign key to users(id) with ON DELETE CASCADE
  - [ ] Unique constraint on (user_id, calculated_at)
  - [ ] JSONB columns for specialty_heatmap and identified_gaps
  - [ ] Check constraint for current_trajectory IN ('accelerating', 'steady', 'slowing')
  - [ ] Indexes created (idx_user_analytics_user_latest, idx_user_analytics_trajectory)
  - [ ] Migration executes successfully (alembic upgrade head)
  - [ ] Rollback tested (alembic downgrade -1)

---

**Task 1.2**: Implement AnalyticsService - Overall Score Calculation

- **Effort**: 30 minutes
- **Owner**: Backend Engineer
- **Deliverable**: `backend/src/services/analytics_service.py` (calculate_overall_score method)
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Method signature: `calculate_overall_score(user_id: int) -> float`
  - [ ] Fetches user_progress for user (MCQ + OSCE + EMR columns)
  - [ ] Calculates MCQ score (total_mcqs_correct / total_mcqs_attempted * 100)
  - [ ] Calculates OSCE score (average_osce_score / 15 * 100)
  - [ ] Calculates EMR score (emr_avg_validation_score)
  - [ ] Applies weights (30% MCQ + 30% OSCE + 40% EMR)
  - [ ] Returns overall score (0-100, rounded to 2 decimals)
  - [ ] Handles edge cases (no MCQ attempts, no OSCE completions, no EMR sessions)
  - [ ] Unit test passes (validates ±0.1 tolerance)

---

**Task 1.3**: Implement AnalyticsService - Correlation Calculation

- **Effort**: 45 minutes
- **Owner**: Backend Engineer
- **Deliverable**: `calculate_cross_module_correlation` method
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Uses scipy.stats.pearsonr for correlation calculation
  - [ ] Fetches weekly scores for last 12 weeks
  - [ ] Calculates 3 correlation coefficients (MCQ-OSCE, MCQ-EMR, OSCE-EMR)
  - [ ] Returns dict with correlation values (range -1 to +1, rounded to 3 decimals)
  - [ ] Handles insufficient data (<5 weeks) by returning None
  - [ ] Unit test validates against known dataset (r ≈ 0.72 for test data)

---

**Task 1.4**: Implement AnalyticsService - Learning Velocity

- **Effort**: 30 minutes
- **Owner**: Backend Engineer
- **Deliverable**: `calculate_learning_velocity` method
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Fetches weekly scores for last 12 weeks
  - [ ] Calculates week-over-week improvement (%)
  - [ ] Computes 12-week moving average
  - [ ] Returns velocity (% per week, rounded to 2 decimals)
  - [ ] Handles first week (no baseline) by skipping
  - [ ] Unit test validates against mock data (velocity ≈ 2.3%)

---

**Task 1.5**: Implement AnalyticsService - Specialty Heatmap

- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `build_specialty_heatmap` method
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Iterates through 10 specialties
  - [ ] Fetches MCQ score from user_progress (per specialty)
  - [ ] Fetches OSCE score from osce_attempts (joined with osces)
  - [ ] Fetches EMR score from emr_soap_notes (joined with mock_patients)
  - [ ] Returns dict with specialty keys and {mcq, osce, emr} values
  - [ ] Handles specialties with no data (returns 0)
  - [ ] Unit test validates all 10 specialties present

---

**Task 1.6**: Implement AnalyticsService - Gap Analysis

- **Effort**: 30 minutes
- **Owner**: Backend Engineer
- **Deliverable**: `identify_gaps` method
- **Dependencies**: Task 1.5
- **Acceptance Criteria**:
  - [ ] Takes specialty_heatmap as input
  - [ ] Identifies gaps >10% between strongest and weakest modules
  - [ ] Returns list of dicts (specialty, strong_in, weak_in, gap, recommendation)
  - [ ] Sorts by gap descending (largest gaps first)
  - [ ] Generates actionable recommendations (e.g., "Focus on EMR Cardiology sessions")
  - [ ] Unit test validates gap detection logic

---

**Task 1.7**: Implement AnalyticsService - Study Pattern Detection

- **Effort**: 45 minutes
- **Owner**: Backend Engineer
- **Deliverable**: `analyze_study_patterns` method
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Fetches all sessions (MCQ attempts, OSCE completions, EMR sessions) for last 12 weeks
  - [ ] Groups by session length (buckets: <20, 20-30, 30-40, 40-50, 50+)
  - [ ] Calculates average performance per bucket
  - [ ] Identifies optimal session length (bucket with highest avg performance)
  - [ ] Groups by hour of day (0-23)
  - [ ] Identifies best study hour (hour with highest avg performance)
  - [ ] Calculates avg sessions per week
  - [ ] Returns dict with optimal_session_length_minutes, best_study_time_hour, avg_sessions_per_week
  - [ ] Unit test validates with mock session data

---

**Task 1.8**: Implement AnalyticsService - Time to Mastery Prediction

- **Effort**: 45 minutes
- **Owner**: Backend Engineer
- **Deliverable**: `predict_time_to_mastery` method
- **Dependencies**: Task 1.4
- **Acceptance Criteria**:
  - [ ] Fetches weekly scores for last 12 weeks
  - [ ] Uses numpy.polyfit for linear regression (degree 1)
  - [ ] Calculates slope and intercept
  - [ ] Predicts weeks needed to reach 80% (target_score - current_score / slope)
  - [ ] Calculates R² (goodness of fit) for confidence level
  - [ ] Returns dict with estimated_weeks, estimated_date, confidence, r_squared
  - [ ] Handles edge cases (slope ≤ 0, insufficient data)
  - [ ] Unit test validates prediction accuracy (±1 week tolerance)

---

**Task 1.9**: Create API Endpoint - GET /api/v1/progress/unified

- **Effort**: 30 minutes
- **Owner**: Backend Engineer
- **Deliverable**: FastAPI endpoint in `backend/src/api/v1/progress.py`
- **Dependencies**: Tasks 1.2-1.8
- **Acceptance Criteria**:
  - [ ] Endpoint defined: `@router.get("/unified")`
  - [ ] JWT authentication required (Depends(get_current_user))
  - [ ] Calls AnalyticsService.calculate_user_analytics(user_id)
  - [ ] Returns JSON with overall_score, breakdown, mcq_progress, osce_progress, emr_progress, cross_module_insights
  - [ ] Handles errors (401 Unauthorized, 404 Not Found, 500 Internal Server Error)
  - [ ] Response time <500ms (without cache)
  - [ ] Integration test passes (pytest)

---

**Task 1.10**: Create API Endpoint - GET /api/v1/progress/specialty-heatmap

- **Effort**: 30 minutes
- **Owner**: Backend Engineer
- **Deliverable**: FastAPI endpoint in `backend/src/api/v1/progress.py`
- **Dependencies**: Task 1.5, Task 1.6
- **Acceptance Criteria**:
  - [ ] Endpoint defined: `@router.get("/specialty-heatmap")`
  - [ ] JWT authentication required
  - [ ] Calls AnalyticsService.build_specialty_heatmap(user_id)
  - [ ] Calls AnalyticsService.identify_gaps(heatmap)
  - [ ] Returns JSON with specialties, modules, scores (3×10 array), gaps
  - [ ] Response time <300ms (without cache)
  - [ ] Integration test passes

---

**Task 1.11**: Create API Endpoint - GET /api/v1/progress/learning-velocity

- **Effort**: 30 minutes
- **Owner**: Backend Engineer
- **Deliverable**: FastAPI endpoint in `backend/src/api/v1/progress.py`
- **Dependencies**: Task 1.4, Task 1.8
- **Acceptance Criteria**:
  - [ ] Endpoint defined: `@router.get("/learning-velocity")`
  - [ ] Query parameter: weeks (default 12)
  - [ ] JWT authentication required
  - [ ] Calls AnalyticsService.calculate_learning_velocity(user_id, weeks)
  - [ ] Calls AnalyticsService.predict_time_to_mastery(user_id)
  - [ ] Returns JSON with weeks array, summary, prediction
  - [ ] Response time <400ms (without cache)
  - [ ] Integration test passes

---

### Phase 2 Tasks

**Task 2.1**: Setup Redis Caching for Unified Progress

- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Redis caching implementation in `backend/src/cache/redis_cache.py`
- **Dependencies**: Task 1.9
- **Acceptance Criteria**:
  - [ ] Redis client initialized (redis-py library)
  - [ ] Cache key pattern: "unified_progress:{user_id}"
  - [ ] TTL: 1 hour (3600 seconds)
  - [ ] get_unified_progress_cached method implemented
  - [ ] Cache hit returns cached data (no recalculation)
  - [ ] Cache miss calculates fresh data and stores in cache
  - [ ] JSON serialization/deserialization working
  - [ ] Performance: Cache hit <50ms, cache miss <500ms

---

**Task 2.2**: Implement Cache Invalidation on User Activity

- **Effort**: 30 minutes
- **Owner**: Backend Engineer
- **Deliverable**: Cache invalidation hooks in MCQ/OSCE/EMR endpoints
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] invalidate_progress_cache method implemented
  - [ ] Hook in MCQ attempt endpoint (POST /api/v1/mcq/attempt)
  - [ ] Hook in OSCE completion endpoint (POST /api/v1/osce/complete)
  - [ ] Hook in EMR session submission endpoint (POST /api/v1/emr/sessions/{id}/submit)
  - [ ] Cache deleted for user_id on activity
  - [ ] Integration test validates cache invalidation

---

**Task 2.3**: Create Celery Task for Daily Analytics Recalculation

- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Celery task in `backend/src/tasks/analytics_tasks.py`
- **Dependencies**: Task 1.2-1.8, Task 2.1
- **Acceptance Criteria**:
  - [ ] Celery task defined: `@shared_task(name="recalculate_user_analytics")`
  - [ ] Fetches active users (last_login_at within 7 days)
  - [ ] Iterates through users and calculates analytics
  - [ ] Upserts to user_analytics table (db.merge)
  - [ ] Invalidates cache for each user
  - [ ] Logs completion metrics (processed, errors)
  - [ ] Error handling (continues on user failure, logs error)
  - [ ] Celery Beat schedule configured (daily at 2 AM)
  - [ ] Task tested manually (celery -A backend.celery_app worker --loglevel=info)

---

**Task 2.4**: Test Cache Hit Rate and Performance

- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Performance test report
- **Dependencies**: Task 2.1, Task 2.2
- **Test Scenarios**:
  ```python
  # Test 1: Cold cache (first request)
  response = client.get("/api/v1/progress/unified", headers=auth_headers)
  assert response.status_code == 200
  assert response_time < 500  # Cache miss
  
  # Test 2: Warm cache (second request within 1 hour)
  response = client.get("/api/v1/progress/unified", headers=auth_headers)
  assert response.status_code == 200
  assert response_time < 100  # Cache hit
  
  # Test 3: Cache invalidation (after MCQ attempt)
  client.post("/api/v1/mcq/attempt", json={...})
  response = client.get("/api/v1/progress/unified", headers=auth_headers)
  assert response_time < 500  # Cache miss (recalculated)
  
  # Test 4: Cache hit rate (100 requests)
  hit_count = 0
  for _ in range(100):
      response = client.get("/api/v1/progress/unified", headers=auth_headers)
      if response.headers.get("X-Cache") == "HIT":
          hit_count += 1
  assert hit_count >= 95  # ≥95% cache hit rate
  ```
- **Acceptance Criteria**:
  - [ ] Cache hit rate ≥95% in testing
  - [ ] Cache hit response time <100ms
  - [ ] Cache miss response time <500ms
  - [ ] Cache invalidation working (response time increases after activity)
  - [ ] Performance report documented

---

### Phase 3 Tasks

**Task 3.1**: Create OverallProgressCard Component

- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/dashboard/OverallProgressCard.tsx`
- **Dependencies**: Task 1.9 (unified progress API)
- **Acceptance Criteria**:
  - [ ] Component created with TypeScript interface (OverallProgressCardProps)
  - [ ] Displays overall score (large number, e.g., "78.5")
  - [ ] Displays breakdown (MCQ: 82.3 × 30%, OSCE: 77.1 × 30%, EMR: 75.4 × 40%)
  - [ ] Color-coded: Green ≥80%, Blue 60-80%, Red <60%
  - [ ] Progress bar showing overall score
  - [ ] Responsive design (mobile + desktop)
  - [ ] TanStack Query integration (useQuery for /api/v1/progress/unified)
  - [ ] Loading skeleton while fetching
  - [ ] Error state handling
  - [ ] Component test passes (Jest + React Testing Library)

---

**Task 3.2**: Create LearningVelocityChart Component

- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/dashboard/LearningVelocityChart.tsx`
- **Dependencies**: Task 1.11 (learning velocity API)
- **Acceptance Criteria**:
  - [ ] Component created with Recharts LineChart
  - [ ] 3 lines: MCQ velocity (blue), OSCE velocity (green), EMR velocity (purple)
  - [ ] Target line: 3% per week (dashed, gray)
  - [ ] X-axis: Week number (1-12)
  - [ ] Y-axis: % improvement per week
  - [ ] Tooltip shows velocity values on hover
  - [ ] Legend shows line labels
  - [ ] ResponsiveContainer for mobile responsiveness
  - [ ] TanStack Query integration (useQuery for /api/v1/progress/learning-velocity)
  - [ ] Loading state
  - [ ] Component test passes (validates chart renders with mock data)

---

**Task 3.3**: Create SpecialtyHeatmap Component

- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/dashboard/SpecialtyHeatmap.tsx`
- **Dependencies**: Task 1.10 (specialty heatmap API)
- **Acceptance Criteria**:
  - [ ] Component created with MUI Grid
  - [ ] 3×10 grid (rows: MCQ/OSCE/EMR, columns: 10 specialties)
  - [ ] Color-coded cells: Green ≥80%, Yellow 60-80%, Red <60%
  - [ ] Cell displays score (e.g., "82")
  - [ ] Hover tooltip shows specialty name + module + score
  - [ ] Column headers: Specialty names (rotated 45° for space)
  - [ ] Row headers: MCQ, OSCE, EMR
  - [ ] Responsive (horizontal scroll on mobile)
  - [ ] TanStack Query integration (useQuery for /api/v1/progress/specialty-heatmap)
  - [ ] Loading skeleton
  - [ ] Component test passes

---

**Task 3.4**: Create StudyPatternInsights Component

- **Effort**: 30 minutes
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/dashboard/StudyPatternInsights.tsx`
- **Dependencies**: Task 1.9 (unified progress API - includes study patterns)
- **Acceptance Criteria**:
  - [ ] Component created with MUI Card
  - [ ] Displays optimal session length (e.g., "35 minutes")
  - [ ] Displays best study time (e.g., "2 PM - 4 PM")
  - [ ] Displays avg sessions per week (e.g., "5.3 sessions/week")
  - [ ] Icon indicators (clock, calendar, trending up)
  - [ ] Recommendation text (e.g., "Your best performance is at 2 PM")
  - [ ] TanStack Query integration (data from /api/v1/progress/unified)
  - [ ] Component test passes

---

**Task 3.5**: Create GapAnalysisPanel Component

- **Effort**: 30 minutes
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/components/dashboard/GapAnalysisPanel.tsx`
- **Dependencies**: Task 1.10 (specialty heatmap API - includes gaps)
- **Acceptance Criteria**:
  - [ ] Component created with MUI List
  - [ ] Lists specialties with >10% gap between modules
  - [ ] Each item shows: Specialty, Strong module, Weak module, Gap size, Recommendation
  - [ ] Color-coded gap badges (Red ≥15%, Orange 10-15%)
  - [ ] Sorted by gap descending (largest gaps first)
  - [ ] Click to navigate to practice page (e.g., click "Cardiology EMR" → EMR practice page filtered to Cardiology)
  - [ ] TanStack Query integration (data from /api/v1/progress/specialty-heatmap)
  - [ ] Component test passes

---

**Task 3.6**: Write Component Tests

- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: Test files for all 5 components
- **Dependencies**: Tasks 3.1-3.5
- **Test Cases**:
  ```typescript
  // OverallProgressCard.test.tsx
  describe('OverallProgressCard', () => {
    test('renders overall score', () => {
      render(<OverallProgressCard overall_score={78.5} breakdown={...} />);
      expect(screen.getByText('78.5')).toBeInTheDocument();
    });
    
    test('displays color based on score', () => {
      const { rerender } = render(<OverallProgressCard overall_score={85} ... />);
      expect(screen.getByTestId('score-container')).toHaveClass('green');
      
      rerender(<OverallProgressCard overall_score={65} ... />);
      expect(screen.getByTestId('score-container')).toHaveClass('blue');
    });
    
    test('shows loading skeleton when loading', () => {
      render(<OverallProgressCard loading={true} />);
      expect(screen.getByTestId('skeleton')).toBeInTheDocument();
    });
  });
  
  // Similar tests for other 4 components
  ```
- **Acceptance Criteria**:
  - [ ] 5 test files created (one per component)
  - [ ] Each component has ≥3 test cases (render, props, loading state)
  - [ ] Overall test coverage ≥70%
  - [ ] All tests passing (npm run test)
  - [ ] Accessibility tests included (ARIA labels, keyboard navigation)

---

### Dependency Graph

```
Phase 1 (Backend Analytics Foundation)
    ↓
Task 1.1 (Alembic Migration)
    ↓
Task 1.2 (Overall Score) ──────┬─► Task 1.9 (API Endpoint 1)
    ↓                           │
Task 1.3 (Correlation) ─────────┤
    ↓                           │
Task 1.4 (Learning Velocity) ───┼─► Task 1.11 (API Endpoint 3)
    ↓                           │
Task 1.5 (Specialty Heatmap) ───┼─► Task 1.10 (API Endpoint 2)
    ↓                           │
Task 1.6 (Gap Analysis) ────────┤
    ↓                           │
Task 1.7 (Study Patterns) ──────┤
    ↓                           │
Task 1.8 (Time to Mastery) ─────┘
    ↓
Phase 2 (Caching & Background Jobs)
    ↓
Task 2.1 (Redis Caching) ───► Task 2.2 (Cache Invalidation)
    ↓                           ↓
Task 2.3 (Celery Task) ─────► Task 2.4 (Performance Testing)
    ↓
Phase 3 (Frontend Dashboard Widgets)
    ↓
Task 3.1 (OverallProgressCard) ────┬─► Task 3.6 (Component Tests)
    ↓                               │
Task 3.2 (LearningVelocityChart) ──┤
    ↓                               │
Task 3.3 (SpecialtyHeatmap) ───────┤
    ↓                               │
Task 3.4 (StudyPatternInsights) ───┤
    ↓                               │
Task 3.5 (GapAnalysisPanel) ────────┘
    ↓
COMPLETE
```

---

### Timeline (Example)

| Day | Phase | Tasks | Hours | Deliverable |
|-----|-------|-------|-------|-------------|
| Day 1 AM | Phase 1 | 1.1, 1.2, 1.3 | 2.5h | Database + basic calculations |
| Day 1 PM | Phase 1 | 1.4, 1.5, 1.6 | 2h | Advanced analytics |
| Day 2 AM | Phase 1 | 1.7, 1.8, 1.9, 1.10, 1.11 | 3h | All API endpoints |
| Day 2 PM | Phase 2 | 2.1, 2.2, 2.3 | 3h | Caching + background jobs |
| Day 3 AM | Phase 2 | 2.4 | 1h | Performance validation |
| Day 3 PM | Phase 3 | 3.1, 3.2 | 2.5h | First 2 components |
| Day 4 AM | Phase 3 | 3.3, 3.4, 3.5 | 2.5h | Last 3 components |
| Day 4 PM | Phase 3 | 3.6 | 1h | Component tests |

**Total**: 3-4 days, 11-14 hours effort

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements

- [ ] **Overall Score Calculation**: Weighted average (30% MCQ + 30% OSCE + 40% EMR) calculates correctly (±0.1 tolerance)
- [ ] **Cross-Module Correlation**: Pearson coefficients calculated for MCQ-OSCE, MCQ-EMR, OSCE-EMR (validated against scipy.stats)
- [ ] **Learning Velocity**: 12-week moving average calculates correctly (±0.1 tolerance)
- [ ] **Specialty Heatmap**: 3×10 grid generated for all 10 specialties across 3 modules
- [ ] **Gap Analysis**: Identifies specialties with >10% gap between strongest and weakest modules
- [ ] **Study Pattern Detection**: Optimal session length and best study time detected from user behavior
- [ ] **Time to Mastery Prediction**: Linear regression predicts weeks to 80% (±1 week tolerance)
- [ ] **API Endpoints**: All 3 endpoints return expected JSON structure (validated against OpenAPI schema)
- [ ] **Frontend Components**: All 5 components render correctly with mock data

#### Quality Requirements

- [ ] **Test Coverage**: Backend ≥70% (unit + integration tests)
- [ ] **Test Coverage**: Frontend ≥70% (component tests)
- [ ] **Test Pass Rate**: 100% (zero tolerance)
- [ ] **Code Quality**: No linting errors (flake8, eslint)
- [ ] **Documentation**: All API endpoints documented (OpenAPI spec)
- [ ] **Documentation**: All calculation formulas documented in code comments

#### Performance Requirements

- [ ] **Unified Progress API**: <200ms (p95) with cache hit
- [ ] **Specialty Heatmap API**: <150ms (cached)
- [ ] **Learning Velocity API**: <250ms (time-series calculation)
- [ ] **Cache Hit Rate**: ≥95% for frequently accessed data (monitored via Redis INFO)
- [ ] **Background Job Duration**: <10 minutes for 1000 users
- [ ] **Dashboard Load Time**: Full analytics dashboard <2 seconds (Lighthouse performance score ≥90)

#### Security Requirements

- [ ] **Authentication**: All API endpoints require JWT (tested with 401 Unauthorized for missing token)
- [ ] **Authorization**: Users can only access own analytics (tested with 403 Forbidden for other user's data)
- [ ] **No Hardcoded Credentials**: Redis password from environment variable (grep scan passes)
- [ ] **Rate Limiting**: 100 requests/minute per user (tested with 429 Too Many Requests)
- [ ] **SQL Injection Prevention**: Parameterized queries (all database queries use SQLAlchemy ORM)
- [ ] **Cache Security**: Redis password-protected, no sensitive data in cache keys

#### Australian Medical Compliance

- [ ] **Terminology**: All specialty names use Australian conventions (e.g., "Obstetrics & Gynaecology" not "OB/GYN")
- [ ] **Scoring**: OSCE scores normalized to AMC rubric (0-15 points, pass = 9/15)
- [ ] **EMR Compliance**: AHPRA compliance rate displayed prominently
- [ ] **Units**: All study time in hours/minutes (not seconds in UI)

---

### Testing Requirements

#### Backend Unit Tests (≥70% coverage target)

```python
# test_analytics_service.py

def test_calculate_overall_score():
    """Test overall score calculation."""
    user_progress = create_mock_progress(
        mcq_attempted=100, mcq_correct=82,
        osce_practiced=10, osce_avg_score=11.56,
        emr_avg_score=75.4
    )
    
    service = AnalyticsService()
    overall_score = service.calculate_overall_score(user_progress)
    
    # Expected: 82.0 * 0.3 + 77.1 * 0.3 + 75.4 * 0.4 = 78.43
    assert abs(overall_score - 78.43) < 0.1

def test_calculate_correlation():
    """Test correlation calculation."""
    weekly_data = [
        {'mcq_score': 75, 'osce_score': 70, 'emr_score': 68},
        {'mcq_score': 77, 'osce_score': 72, 'emr_score': 70},
        # ... 10 more weeks
    ]
    
    service = AnalyticsService()
    correlations = service.calculate_cross_module_correlation(weekly_data)
    
    assert 0 <= abs(correlations['mcq_osce_correlation']) <= 1
    assert 0 <= abs(correlations['mcq_emr_correlation']) <= 1

def test_learning_velocity():
    """Test learning velocity calculation."""
    weekly_data = [
        {'overall_score': 75.0},
        {'overall_score': 76.5},
        {'overall_score': 78.0},
        # ... 9 more weeks
    ]
    
    service = AnalyticsService()
    velocity = service.calculate_learning_velocity(weekly_data)
    
    # Expected: ~2% per week
    assert 1.5 <= velocity <= 2.5

def test_specialty_heatmap_generation():
    """Test specialty heatmap generation."""
    service = AnalyticsService()
    heatmap = service.build_specialty_heatmap(user_id=1)
    
    # Should have all 10 specialties
    assert len(heatmap) == 10
    
    # Each specialty should have mcq, osce, emr scores
    for specialty, scores in heatmap.items():
        assert 'mcq' in scores
        assert 'osce' in scores
        assert 'emr' in scores
        assert 0 <= scores['mcq'] <= 100

def test_gap_analysis():
    """Test gap analysis."""
    heatmap = {
        'cardiology': {'mcq': 82, 'osce': 75, 'emr': 70},
        'neurology': {'mcq': 65, 'osce': 68, 'emr': 72}
    }
    
    service = AnalyticsService()
    gaps = service.identify_gaps(heatmap, threshold=10.0)
    
    # Cardiology should be identified (gap = 12)
    assert len(gaps) >= 1
    assert gaps[0]['specialty'] == 'Cardiology'
    assert gaps[0]['gap'] == 12
```

#### Backend Integration Tests

```python
# test_analytics_api.py

def test_unified_progress_endpoint(client, auth_headers):
    """Test unified progress API endpoint."""
    response = client.get("/api/v1/progress/unified", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert 'overall_score' in data
    assert 'breakdown' in data
    assert 'mcq_progress' in data
    assert 'osce_progress' in data
    assert 'emr_progress' in data
    assert 'cross_module_insights' in data

def test_specialty_heatmap_endpoint(client, auth_headers):
    """Test specialty heatmap API endpoint."""
    response = client.get("/api/v1/progress/specialty-heatmap", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data['specialties']) == 10
    assert data['modules'] == ['MCQ', 'OSCE', 'EMR']
    assert len(data['scores']) == 10
    assert len(data['scores'][0]) == 3  # 3 modules

def test_learning_velocity_endpoint(client, auth_headers):
    """Test learning velocity API endpoint."""
    response = client.get("/api/v1/progress/learning-velocity?weeks=12", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data['weeks']) == 12
    assert 'summary' in data
    assert 'prediction' in data

def test_authentication_required(client):
    """Test that endpoints require authentication."""
    response = client.get("/api/v1/progress/unified")
    assert response.status_code == 401
```

#### Frontend Component Tests

```typescript
// OverallProgressCard.test.tsx

describe('OverallProgressCard', () => {
  test('renders overall score correctly', () => {
    const mockData = {
      overall_score: 78.5,
      breakdown: {
        mcq: { score: 82.3, weight: 0.30, contribution: 24.69 },
        osce: { score: 77.1, weight: 0.30, contribution: 23.13 },
        emr: { score: 75.4, weight: 0.40, contribution: 30.16 }
      }
    };
    
    render(<OverallProgressCard data={mockData} />);
    
    expect(screen.getByText('78.5')).toBeInTheDocument();
    expect(screen.getByText('82.3')).toBeInTheDocument();  // MCQ score
    expect(screen.getByText('77.1')).toBeInTheDocument();  // OSCE score
    expect(screen.getByText('75.4')).toBeInTheDocument();  // EMR score
  });
  
  test('shows green color for score ≥80', () => {
    const mockData = { overall_score: 85, breakdown: {...} };
    render(<OverallProgressCard data={mockData} />);
    
    const scoreElement = screen.getByTestId('overall-score');
    expect(scoreElement).toHaveStyle({ color: expect.stringContaining('green') });
  });
  
  test('displays loading skeleton when loading', () => {
    render(<OverallProgressCard loading={true} />);
    expect(screen.getByTestId('skeleton')).toBeInTheDocument();
  });
});

// LearningVelocityChart.test.tsx

describe('LearningVelocityChart', () => {
  test('renders chart with 3 lines', () => {
    const mockData = {
      weeks: [
        { week_start: '2026-01-01', mcq_improvement: 2.1, osce_improvement: 1.8, emr_improvement: 2.3 },
        // ... more weeks
      ]
    };
    
    render(<LearningVelocityChart data={mockData} />);
    
    // Check that Recharts LineChart is rendered
    expect(screen.getByRole('img')).toBeInTheDocument();  // Recharts renders as SVG
  });
});
```

#### Performance Tests

```python
# test_performance.py

def test_cache_hit_performance(client, auth_headers):
    """Test cache hit performance."""
    import time
    
    # First request (cache miss)
    start = time.time()
    response = client.get("/api/v1/progress/unified", headers=auth_headers)
    cache_miss_time = time.time() - start
    
    assert response.status_code == 200
    assert cache_miss_time < 0.5  # <500ms
    
    # Second request (cache hit)
    start = time.time()
    response = client.get("/api/v1/progress/unified", headers=auth_headers)
    cache_hit_time = time.time() - start
    
    assert response.status_code == 200
    assert cache_hit_time < 0.1  # <100ms
    assert cache_hit_time < cache_miss_time  # Cache hit should be faster

def test_cache_hit_rate(client, auth_headers):
    """Test cache hit rate ≥95%."""
    hit_count = 0
    
    for i in range(100):
        response = client.get("/api/v1/progress/unified", headers=auth_headers)
        
        # Check X-Cache header
        if response.headers.get('X-Cache') == 'HIT':
            hit_count += 1
        
        # Occasionally invalidate cache (simulate user activity)
        if i % 20 == 0:
            client.post("/api/v1/mcq/attempt", json={...}, headers=auth_headers)
    
    hit_rate = hit_count / 100
    assert hit_rate >= 0.95
```

---

### Documentation Deliverables

#### 1. API Documentation (OpenAPI Spec)

```yaml
# openapi.yaml (excerpt)

/api/v1/progress/unified:
  get:
    summary: Get unified progress across MCQ, OSCE, EMR
    tags: [Progress Analytics]
    security:
      - BearerAuth: []
    responses:
      200:
        description: Successful response
        content:
          application/json:
            schema:
              type: object
              properties:
                overall_score:
                  type: number
                  format: float
                  description: Weighted average (0-100)
                breakdown:
                  type: object
                  properties:
                    mcq: { ... }
                    osce: { ... }
                    emr: { ... }
                # ... (full schema)
      401:
        description: Unauthorized (missing or invalid JWT)
      404:
        description: No analytics data found for user
```

#### 2. Architecture Decision Record (ADR)

```markdown
# ADR-002: Unified Progress Tracking Architecture

## Context
Students need holistic view of progress across MCQ, OSCE, EMR modules to identify cross-module patterns and optimize study strategy.

## Decision
Implement unified analytics aggregation service with:
1. New `user_analytics` table (stores calculated metrics)
2. Background job (daily recalculation at 2 AM)
3. Redis caching (1-hour TTL)
4. Single unified API endpoint

## Rationale
- **Separation of Concerns**: Analytics calculations separated from real-time endpoints
- **Performance**: Background job avoids on-demand calculation (slow)
- **Caching**: 1-hour TTL balances freshness vs performance
- **Flexibility**: JSONB columns allow adding new metrics without schema changes

## Alternatives Considered
1. **Real-time calculation on every request**: Too slow (500ms+)
2. **Materialized views**: Less flexible, harder to maintain
3. **No caching**: Too many recalculations, poor UX

## Consequences
- **Positive**: Fast API responses (<200ms), scalable to 1000+ users
- **Negative**: Analytics up to 1 hour stale (acceptable for progress tracking)
- **Mitigation**: Cache invalidation on user activity reduces staleness
```

#### 3. Calculation Formulas Documentation

```markdown
# Analytics Calculation Formulas

## Overall Score
Weighted average: `overall_score = mcq_score * 0.30 + osce_score * 0.30 + emr_score * 0.40`

- MCQ Score: `(total_mcqs_correct / total_mcqs_attempted) * 100`
- OSCE Score: `(average_osce_score / 15) * 100` (AMC rubric: 0-15 points)
- EMR Score: `emr_avg_validation_score` (already 0-100)

## Correlation (Pearson r)
Formula: `r = Σ[(X - X̄)(Y - Ȳ)] / √[Σ(X - X̄)² × Σ(Y - Ȳ)²]`

Implementation: `scipy.stats.pearsonr(X, Y)`

## Learning Velocity
12-week moving average of week-over-week improvement:

```
improvement[i] = ((score[i] - score[i-1]) / score[i-1]) * 100
velocity = sum(improvements) / 12
```

## Time to Mastery
Linear regression: `score = slope * week + intercept`

Prediction: `weeks_needed = (target_score - current_score) / slope`
```

#### 4. User Guide (for Students)

```markdown
# Unified Progress Dashboard - User Guide

## What is Unified Progress?

Your Unified Progress Dashboard shows your performance across all 3 AMC preparation modules:
- **MCQ**: Theoretical knowledge (30% weight)
- **OSCE**: Clinical skills (30% weight)
- **EMR**: Documentation (40% weight)

## Overall Score

Your **Overall Score** (e.g., 78.5) is a weighted average:
- MCQ accuracy × 30%
- OSCE pass rate × 30%
- EMR validation score × 40%

**Target**: 80+ for AMC Clinical Exam readiness

## Learning Velocity

Shows your weekly improvement rate (% per week):
- **Target**: 3% per week (sustainable long-term)
- **Accelerating**: Velocity increasing week-over-week
- **Slowing**: Velocity decreasing (consider changing study approach)

## Specialty Heatmap

3×10 grid showing your performance:
- **Green cells** (≥80%): Strong in this specialty + module
- **Yellow cells** (60-80%): Moderate performance
- **Red cells** (<60%): Weak area - focus here

## Gap Analysis

Identifies specialties where you're strong in one module but weak in another:
- Example: "Cardiology - Strong in MCQ (82%) but weak in EMR (70%)"
- **Recommendation**: Focus on EMR Cardiology sessions

## Study Pattern Insights

Based on your behavior:
- **Optimal Session Length**: Your best performance (e.g., 35 minutes)
- **Best Study Time**: When you perform best (e.g., 2 PM - 4 PM)
- **Predicted Timeline**: Estimated weeks to 80% mastery
```

---

### Deployment Checklist

#### Pre-Deployment

- [ ] All acceptance criteria met (100%)
- [ ] All tests passing (100% pass rate)
- [ ] Backend unit tests ≥70% coverage
- [ ] Frontend component tests ≥70% coverage
- [ ] API documentation updated (OpenAPI spec)
- [ ] Performance benchmarks met (API <200ms, dashboard <2s)
- [ ] Security scan passes (0 HIGH/CRITICAL)
- [ ] Code reviewed and approved

#### Deployment (Development)

- [ ] Database migration executed (alembic upgrade head)
- [ ] user_analytics table created (verify with `\dt user_analytics`)
- [ ] Redis instance running (verify with `redis-cli ping`)
- [ ] Celery worker started (verify with `celery -A backend.celery_app inspect active`)
- [ ] Celery Beat scheduler running (verify daily task scheduled)
- [ ] Environment variables configured (REDIS_URL, CELERY_BROKER_URL)
- [ ] API endpoints deployed (verify with curl)
- [ ] Frontend components deployed (verify dashboard loads)
- [ ] Smoke tests passing

#### Post-Deployment

- [ ] API response times within targets (<200ms p95)
- [ ] Cache hit rate ≥95% (check Redis INFO stats)
- [ ] Background job runs successfully (check logs at 2 AM next day)
- [ ] Dashboard loads in <2 seconds (Lighthouse score ≥90)
- [ ] No error spikes in logs
- [ ] Analytics data populating correctly (verify for test user)
- [ ] Stakeholders notified

---

### Success Validation

**This PRD is considered COMPLETE when**:

1. ✅ `user_analytics` table created with all 15 columns
2. ✅ AnalyticsService calculates all 7 metrics correctly (±0.1 tolerance)
3. ✅ 3 API endpoints return expected JSON structure
4. ✅ Redis caching working (≥95% cache hit rate)
5. ✅ Background job processes 1000 users in <10 minutes
6. ✅ 5 frontend components render correctly
7. ✅ All tests passing (100% pass rate)
8. ✅ Test coverage ≥70% (backend + frontend)
9. ✅ Performance benchmarks met (API <200ms, dashboard <2s)
10. ✅ Security scan passes (0 HIGH/CRITICAL)
11. ✅ Documentation complete (API docs, ADR, user guide)
12. ✅ Production deployment successful

**Sign-off Required From**:

- [ ] PM Coordinator (overall quality, requirements met)
- [ ] Backend Engineer (implementation complete, tests passing)
- [ ] Frontend Engineer (components complete, accessible)
- [ ] Security Expert (security scan passes, authentication working)
- [ ] Testing QA (test coverage ≥70%, 100% pass rate)

---

## 📎 Appendices

### Appendix A: Sample API Response (Unified Progress)

```json
{
  "overall_score": 78.5,
  "breakdown": {
    "mcq": {
      "score": 82.3,
      "weight": 0.30,
      "contribution": 24.69
    },
    "osce": {
      "score": 77.1,
      "weight": 0.30,
      "contribution": 23.13
    },
    "emr": {
      "score": 75.4,
      "weight": 0.40,
      "contribution": 30.16
    }
  },
  "mcq_progress": {
    "total_attempts": 450,
    "accuracy_rate": 82.3,
    "unique_mcqs_attempted": 320,
    "weak_specialties": ["Cardiology", "Neurology"]
  },
  "osce_progress": {
    "total_completions": 35,
    "pass_rate": 77.1,
    "average_score": 11.56,
    "weak_specialties": ["Respiratory"]
  },
  "emr_progress": {
    "sessions_completed": 18,
    "avg_validation_score": 75.4,
    "avg_typing_wpm": 42,
    "ahpra_compliance_rate": 88.5,
    "weak_specialties": ["Emergency Medicine"]
  },
  "cross_module_insights": {
    "correlation_mcq_emr": 0.68,
    "correlation_mcq_osce": 0.72,
    "correlation_osce_emr": 0.65,
    "learning_velocity": 2.3,
    "study_time_total_hours": 45.5,
    "optimal_session_length_minutes": 35,
    "best_study_time_hour": 14,
    "current_trajectory": "accelerating",
    "estimated_weeks_to_80_percent": 6
  },
  "last_calculated_at": "2026-02-16T10:30:00Z"
}
```

### Appendix B: Database Schema (Full DDL)

```sql
-- Full CREATE TABLE statement (from Task 1.1)
CREATE TABLE IF NOT EXISTS user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    calculated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Overall Metrics
    overall_score NUMERIC(5,2),
    overall_study_hours NUMERIC(7,2),
    learning_velocity NUMERIC(5,2),

    -- Cross-Module Correlations
    mcq_osce_correlation NUMERIC(4,3),
    mcq_emr_correlation NUMERIC(4,3),
    osce_emr_correlation NUMERIC(4,3),

    -- Optimal Study Patterns
    optimal_session_length_minutes INTEGER,
    best_study_time_hour INTEGER,
    avg_sessions_per_week NUMERIC(4,2),

    -- Predictive Analytics
    estimated_weeks_to_80_percent INTEGER,
    current_trajectory VARCHAR(20) CHECK (current_trajectory IN ('accelerating', 'steady', 'slowing')),

    -- Specialty Performance Heatmap
    specialty_heatmap JSONB,
    identified_gaps JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, calculated_at)
);

CREATE INDEX idx_user_analytics_user_latest 
    ON user_analytics(user_id, calculated_at DESC);

CREATE INDEX idx_user_analytics_trajectory 
    ON user_analytics(current_trajectory) 
    WHERE current_trajectory IN ('slowing', 'steady');
```

### Appendix C: Error Codes

| Code | Message | Description | User Action |
|------|---------|-------------|-------------|
| E_ANALYTICS_001 | Insufficient data | <5 weeks of data for correlation | Complete more practice sessions |
| E_ANALYTICS_002 | Calculation failed | Analytics calculation error | Contact support |
| E_ANALYTICS_003 | Cache error | Redis connection failed | Retry in a few seconds |
| E_ANALYTICS_004 | Not improving | Negative learning velocity | Review study approach |

### Appendix D: Related PRDs

- **Depends On**:
  - PRD_BACKEND_001 (EMR Database Migration - user_progress EMR columns)
  - PRD_BACKEND_002 (EMR Session API - session data)
  - PRD_FRONTEND_003 (EMR Dashboard Integration - UnifiedProgressChart)
- **Blocks**:
  - PRD_FRONTEND_005 (EMR Analytics Deep Dive - detailed reports)
  - PRD_INTEGRATION_003 (Predictive Study Planning - AI recommendations)
- **Related**:
  - PRD_BACKEND_003 (EMR Validation API - validation scores for analytics)

---

**Document Status**: Ready for Implementation
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: Pending PM Review
**Version**: 1.0

---

**Total Line Count**: ~1,400 lines (target: 1,100-1,400) ✅
