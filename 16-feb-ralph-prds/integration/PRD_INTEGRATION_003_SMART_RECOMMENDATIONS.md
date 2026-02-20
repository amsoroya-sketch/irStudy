# PRD: Claude AI-Powered Smart Study Recommendations

**PRD ID**: PRD_INTEGRATION_003_SMART_RECOMMENDATIONS
**Category**: Integration
**Priority**: P1-High (critical for personalized learning optimization)
**Estimated Effort**: 12-15 hours
**Dependencies**:
- PRD_INTEGRATION_002 (Unified Progress Tracking - user_analytics schema required)
- PRD_BACKEND_001 (EMR Database Migration - EMR metrics)
- PRD_FRONTEND_003 (EMR Dashboard Integration - existing UI patterns)

**Blocks**:
- PRD_FRONTEND_006 (Advanced Study Planning - uses recommendation data)
- PRD_INTEGRATION_004 (Peer Learning Features - social recommendations)

**Status**: Ready for Implementation

---

## R - REQUEST (What & Why)

### User Story

**As a** medical student preparing for AMC Clinical Examination
**I want** personalized, AI-powered study recommendations based on my cross-module performance patterns
**So that** I can focus my limited study time on high-impact areas, address knowledge/skill gaps systematically, and improve my overall AMC readiness score by 5-15 marks within 2 weeks

### Business Context

**Current State**:
- Students have access to unified progress analytics (PRD_INTEGRATION_002: overall_score, specialty_heatmap, learning_velocity)
- Students can see they have weaknesses (e.g., "55% in Cardiology MCQ, 60% in Cardiology OSCE, 58% in Cardiology EMR")
- **BUT**: No actionable guidance on *what to do next*
- **BUT**: No pattern detection across modules (knowledge gap vs skill gap vs documentation gap)
- **BUT**: No prioritization (which specialty to focus on first?)
- **BUT**: No resource linking (which OSCE videos, MCQ topics, EMR patients to practice?)
- **BUT**: No impact estimation (how many AMC marks can I gain by addressing this?)

**Problem - Generic Study Planning Without Intelligence**:
1. **No Cross-Module Pattern Detection**:
   - Student sees: MCQ Cardiology 85%, OSCE Cardiology 55% → What does this mean?
   - Missing insight: "Knowledge gap" (strong theory, weak clinical skills) → Practice OSCE stations

2. **No Root Cause Analysis**:
   - Student sees: Low EMR score (55%) → Why is it low?
   - Missing insight: Strong MCQ/OSCE (70%+) + Weak EMR → "Documentation gap" (knows medicine, can't write SOAP notes)

3. **No Prioritization Algorithm**:
   - Student has 5 weak specialties → Which one first?
   - Missing: Priority based on AMC exam weighting, severity, improvement potential

4. **No Resource Discovery**:
   - Student knows they need to practice Respiratory OSCE → Which video?
   - Missing: Smart linking to relevant OSCE videos, MCQ topics, EMR patients

5. **No Impact Quantification**:
   - Student doesn't know if addressing Cardiology weakness will gain them 2 marks or 10 marks
   - Missing: Estimated AMC score improvement (motivates action)

6. **No Australian Contextualization**:
   - Generic study advice doesn't reference eTG, AMH, PBS, MBS, AHPRA
   - Missing: "Review eTG Cardiovascular section 3.2 (STEMI management), PBS aspirin 100mg code 1234"

**Desired State - Claude AI-Powered Smart Recommendations**:

**Core Capabilities**:
1. **Weak Area Aggregator**: Analyzes user_analytics data to detect 4 pattern types:
   - **Knowledge Gap**: Weak MCQ + Weak OSCE in same specialty (root cause: insufficient theory)
   - **Skill Gap**: Strong MCQ (≥80%) + Weak OSCE (<60%) (root cause: knowledge not applied clinically)
   - **Documentation Gap**: Strong MCQ/OSCE (≥70%) + Weak EMR (<60%) (root cause: poor SOAP note writing)
   - **Comprehensive Weakness**: All 3 modules <60% in same specialty (root cause: complete gap)

2. **Claude AI Recommendation Engine**:
   - Model: `claude-sonnet-4-5-20250929` (NOT local 7B models - per Constraint 4.2)
   - Input: User analytics + weak patterns + specialty scores
   - Output: 5 prioritized recommendations with:
     - Title (50 chars, actionable)
     - Description (200 chars, specific advice)
     - Root cause (knowledge_gap|skill_gap|documentation_gap|comprehensive_weakness)
     - Priority (high|medium|low)
     - Estimated impact (0-15 AMC marks)
     - Resources (OSCE videos, MCQ topics, EMR patients)
     - Australian context (eTG/AMH/PBS/MBS references)

3. **Smart Resource Linking**:
   - Maps recommendations to existing database resources:
     - OSCE videos (osce_videos table: ID, specialty, station_type, duration)
     - MCQ topics (mcq_questions table: topic, subtopic, difficulty)
     - EMR patients (emr_patient_scenarios table: specialty, complexity, conditions)
   - Validates resource IDs exist before returning (no broken links)

4. **Impact Scoring Algorithm**:
   - Calculates potential AMC score improvement based on:
     - Current score in specialty (gap to 80% threshold)
     - AMC exam weighting by specialty (Cardiology 15%, Neurology 10%, etc.)
     - Learning velocity (faster learners → higher impact estimates)
   - Example: Cardiology gap of 20% × 15% exam weight = 3 AMC marks potential

5. **User Interaction & Feedback Loop**:
   - Students can mark recommendations as "Completed" or "Skipped"
   - Completed recommendations tracked (completion_rate metric)
   - Next generation considers completed items (don't recommend what's already done)

**User Workflow Example**:

```
1. Student logs in → Dashboard shows unified progress (75% overall)
2. System detects patterns:
   - Cardiology: MCQ 85%, OSCE 60%, EMR 70% → SKILL GAP (strong theory, weak clinical)
   - Neurology: MCQ 55%, OSCE 58%, EMR 50% → COMPREHENSIVE WEAKNESS (all weak)
   - Respiratory: MCQ 80%, OSCE 75%, EMR 55% → DOCUMENTATION GAP (poor EMR notes)

3. Claude AI generates 5 recommendations:

   RECOMMENDATION #1 (HIGH PRIORITY):
   Title: "Practice Cardiology OSCE History Taking"
   Description: "Your MCQ knowledge is strong (85%) but OSCE performance lags (60%). Focus on translating theory to clinical skills through structured history taking practice."
   Root Cause: Skill Gap
   Estimated Impact: +3.5 AMC marks
   Resources:
   - OSCE Video: "Chest Pain History Taking (Cardiology)" [12 min]
   - OSCE Video: "Cardiovascular Examination Technique" [15 min]
   - Practice Station: "OSCE Cardiology Chest Pain Station" [Moderate]
   Australian Context: "Review eTG Cardiovascular 3.2 (Acute Coronary Syndrome). Familiarize with PBS aspirin 100mg (code 1234), GTN spray (code 5678). Practice MBS ECG item 11700 documentation."

   RECOMMENDATION #2 (HIGH PRIORITY):
   Title: "Build Neurology Foundation with MCQ Bank"
   Description: "All modules weak in Neurology (50-58%). Start with MCQ foundation before OSCE/EMR. Focus on stroke, seizures, headache (high AMC yield)."
   Root Cause: Comprehensive Weakness
   Estimated Impact: +4.2 AMC marks
   Resources:
   - MCQ Topic: "Neurology - Stroke & TIA" [30 questions]
   - MCQ Topic: "Neurology - Seizure Disorders" [25 questions]
   - MCQ Topic: "Neurology - Headache Classification" [20 questions]
   Australian Context: "Review AMC Part 1 Neurology blueprint (12% exam weight). Study eTG Neurology section 8 (Stroke). Familiarize with PBS alteplase criteria."

   RECOMMENDATION #3 (MEDIUM PRIORITY):
   Title: "Improve Respiratory EMR SOAP Note Writing"
   Description: "Strong MCQ/OSCE (75-80%) but weak EMR (55%). Focus on structured SOAP notes, differential diagnosis documentation, and management plans."
   Root Cause: Documentation Gap
   Estimated Impact: +2.1 AMC marks
   Resources:
   - EMR Patient: "Acute Asthma Exacerbation" [Moderate complexity]
   - EMR Patient: "COPD with Infective Exacerbation" [Moderate complexity]
   - EMR Training: "SOAP Note Structure & Rubric" [Guide]
   Australian Context: "Practice eTG Respiratory section 5 (Asthma) documentation. Include PBS salbutamol inhaler (code 3456), prednisolone 25mg (code 7890). Use MBS spirometry item 11503."

4. Student clicks "Practice Cardiology OSCE History Taking" → Navigates to OSCE video player
5. Student watches video, practices station → Marks recommendation as "Completed"
6. Next day: New recommendations generated (excludes completed Cardiology OSCE, focuses on next priority)
7. Two weeks later: Student's overall score improves from 75% → 80% (+5% = 5 AMC marks)
```

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Recommendation Relevance** | 80%+ students rate as "Very Helpful" | In-app survey after completing recommendation |
| **Completion Rate** | 50%+ recommendations completed within 7 days | Track `completed_at` timestamp in user_recommendations |
| **Score Improvement** | 5%+ overall score increase within 2 weeks for active users | Compare analytics.overall_score before/after |
| **Resource Click-Through** | 70%+ recommendations result in resource access | Track navigation to linked OSCE videos, MCQ topics, EMR patients |
| **API Generation Time** | <2 seconds for 5 recommendations (Claude API <5s) | p95 latency monitoring |
| **Australian Compliance** | 100% recommendations include eTG/AMH/PBS/MBS context | Automated validation in prompt |
| **No Broken Links** | 100% resource IDs validated before display | Pre-submission resource existence check |

### Scope

**In Scope**:

1. **Backend - Weak Area Aggregator Service** (3-4 hours):
   - `WeakAreaAggregator` class: Analyzes user_analytics data
   - 4 pattern detection algorithms (knowledge_gap, skill_gap, documentation_gap, comprehensive_weakness)
   - Severity ranking (critical > high > medium > low)
   - Specialty prioritization (AMC exam weighting × gap severity)

2. **Backend - Claude AI Recommendation Engine** (4-5 hours):
   - `RecommendationService` class: Generates recommendations via Claude API
   - 400+ line prompt template with:
     - Pattern detection rules
     - Australian context requirements (eTG/AMH/PBS/MBS)
     - Structured JSON output format
     - Resource linking instructions
     - Impact estimation algorithm
   - Claude API integration (model: `claude-sonnet-4-5-20250929`)
   - Anthropic client with "claud" key from Vault (NOT "anthropic" - security constraint)
   - Response parsing & validation (ensure no malformed JSON)

3. **Backend - Resource Linking & Validation** (1-2 hours):
   - Validate OSCE video IDs exist in `osce_videos` table
   - Validate MCQ topics exist in `mcq_questions` table
   - Validate EMR patient scenario IDs exist in `emr_patient_scenarios` table
   - Return 404 error if resource not found (don't recommend non-existent resources)

4. **Backend - API Endpoints** (2-3 hours):
   - `POST /api/v1/recommendations/generate` - Generate 5 new recommendations
   - `GET /api/v1/recommendations/{user_id}` - Retrieve all recommendations (filter: active/completed/skipped)
   - `POST /api/v1/recommendations/{id}/complete` - Mark recommendation as completed
   - `POST /api/v1/recommendations/{id}/skip` - Mark recommendation as skipped
   - JWT authentication on all endpoints
   - Pydantic input validation

5. **Database Schema - user_recommendations Table** (1 hour):
   - Table: `user_recommendations`
   - Columns: id, user_id, recommendation_type, title, description, priority, estimated_impact, resources (JSONB), australian_context, completed_at, skipped_at, created_at
   - Indexes: user_id, priority, completed_at
   - Foreign key: user_id → users(id)

6. **Frontend - Recommendation UI Components** (3-4 hours):
   - `RecommendationCard` component: Display single recommendation with priority badge, impact chip, resource links, action buttons
   - `RecommendationsPanel` component: List of 5 recommendations, filter by priority, sort by impact
   - `ResourceChip` component: Clickable chip linking to OSCE video, MCQ topic, or EMR patient
   - Navigation integration: Click resource → Navigate to `/osce/videos/{id}`, `/mcq/topics/{topic}`, `/emr/patients/{id}`

**Out of Scope** (Future Iterations):

- AI-generated study schedules (separate PRD_INTEGRATION_004)
- Peer comparison ("Students like you focused on...") - privacy concerns
- Adaptive recommendation refresh (real-time vs daily batch)
- Mobile app recommendation notifications (separate mobile PRD)
- Recommendation effectiveness tracking (A/B testing different prompts)
- Multi-week study plan generator (separate PRD)
- Integration with external study tools (Anki flashcards, etc.)

---

## A - ARCHITECTURE (How)

### Technical Approach

**High-Level Strategy**:
1. **Pattern Detection First**: Analyze user_analytics data (from PRD_INTEGRATION_002) to identify cross-module patterns
2. **Claude AI Generation**: Send patterns + user data to Claude API with structured prompt (400+ lines)
3. **Resource Validation**: Verify all recommended resource IDs exist in database before saving
4. **Store & Serve**: Save recommendations to `user_recommendations` table, expose via REST API
5. **Frontend Display**: React components fetch recommendations, display with priority/impact, link to resources
6. **Feedback Loop**: Track completion/skip actions, use in next generation cycle

**Why Claude AI Instead of Local Models**:
- Per Constraint 4.2: Local 7B models (Ollama) CANNOT handle complex medical reasoning + structured JSON output
- Evidence: 200 MCQs failed with local models (all placeholders)
- Claude API required for:
  - Complex multi-step reasoning (analyze patterns → prioritize → estimate impact → link resources)
  - Medical domain knowledge depth (Australian guidelines, AMC exam structure)
  - Long-form structured JSON generation (500-1000 tokens per recommendation)
- Model: `claude-sonnet-4-5-20250929` (Anthropic's latest medical-capable model)

### System Design

#### Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│           CLAUDE AI-POWERED SMART RECOMMENDATIONS ARCHITECTURE             │
└───────────────────────────────────────────────────────────────────────────┘

DATA SOURCES:
  │
  ├─► PostgreSQL Tables
  │   ├─ user_analytics (FROM PRD_INTEGRATION_002)
  │   │  ├─ overall_score (weighted: 30% MCQ + 30% OSCE + 40% EMR)
  │   │  ├─ specialty_heatmap (JSONB: 3×10 grid of scores)
  │   │  ├─ learning_velocity (% improvement/week)
  │   │  ├─ mcq_osce_correlation, mcq_emr_correlation, osce_emr_correlation
  │   │  └─ optimal_session_length_minutes, best_study_time_hour
  │   │
  │   ├─ user_progress (existing MCQ/OSCE/EMR raw data)
  │   │
  │   ├─ osce_videos (resource validation)
  │   │  └─ Columns: id, specialty, station_type, title, duration_minutes
  │   │
  │   ├─ mcq_questions (resource validation)
  │   │  └─ Columns: id, topic, subtopic, difficulty, question_text
  │   │
  │   ├─ emr_patient_scenarios (resource validation)
  │   │  └─ Columns: id, specialty, complexity, conditions, soap_template
  │   │
  │   └─ user_recommendations (NEW - stores generated recommendations)
  │      ├─ id UUID PRIMARY KEY
  │      ├─ user_id UUID REFERENCES users(id)
  │      ├─ recommendation_type VARCHAR(50) -- 'knowledge_gap', 'skill_gap', etc.
  │      ├─ title VARCHAR(200)
  │      ├─ description TEXT
  │      ├─ priority VARCHAR(20) -- 'high', 'medium', 'low'
  │      ├─ estimated_impact NUMERIC(4,2) -- 0-15 AMC marks
  │      ├─ resources JSONB -- [{"type": "osce_video", "id": "uuid", "title": "..."}]
  │      ├─ australian_context TEXT -- eTG/AMH/PBS/MBS references
  │      ├─ completed_at TIMESTAMP
  │      ├─ skipped_at TIMESTAMP
  │      ├─ created_at TIMESTAMP DEFAULT NOW()
  │      └─ INDEX: (user_id, priority, completed_at)

PROCESSING PIPELINE:
  │
  ├─► STAGE 1: Weak Area Aggregator
  │   File: backend/src/services/weak_area_aggregator.py
  │
  │   class WeakAreaAggregator:
  │       async def identify_patterns(user_id: UUID) -> List[WeakPattern]:
  │           analytics = await get_user_analytics(user_id)
  │           patterns = []
  │
  │           for specialty in SPECIALTIES:
  │               mcq_score = analytics.specialty_heatmap[specialty]['mcq']
  │               osce_score = analytics.specialty_heatmap[specialty]['osce']
  │               emr_score = analytics.specialty_heatmap[specialty]['emr']
  │
  │               # Pattern 1: Knowledge Gap
  │               if mcq_score < 70 and osce_score < 70:
  │                   patterns.append({
  │                       "type": "knowledge_gap",
  │                       "specialty": specialty,
  │                       "severity": "high" if mcq_score < 60 else "medium",
  │                       "scores": {"mcq": mcq_score, "osce": osce_score, "emr": emr_score}
  │                   })
  │
  │               # Pattern 2: Skill Gap
  │               elif mcq_score >= 80 and osce_score < 60:
  │                   patterns.append({
  │                       "type": "skill_gap",
  │                       "specialty": specialty,
  │                       "severity": "high",
  │                       "scores": {"mcq": mcq_score, "osce": osce_score, "emr": emr_score}
  │                   })
  │
  │               # Pattern 3: Documentation Gap
  │               elif mcq_score >= 70 and osce_score >= 70 and emr_score < 60:
  │                   patterns.append({
  │                       "type": "documentation_gap",
  │                       "specialty": specialty,
  │                       "severity": "medium",
  │                       "scores": {"mcq": mcq_score, "osce": osce_score, "emr": emr_score}
  │                   })
  │
  │               # Pattern 4: Comprehensive Weakness
  │               elif mcq_score < 60 and osce_score < 60 and emr_score < 60:
  │                   patterns.append({
  │                       "type": "comprehensive_weakness",
  │                       "specialty": specialty,
  │                       "severity": "critical",
  │                       "scores": {"mcq": mcq_score, "osce": osce_score, "emr": emr_score}
  │                   })
  │
  │           # Sort by severity: critical → high → medium
  │           patterns.sort(key=lambda p: {"critical": 0, "high": 1, "medium": 2}[p["severity"]])
  │           return patterns[:5]  # Top 5 patterns
  │
  ├─► STAGE 2: Claude AI Recommendation Engine
  │   File: backend/src/services/recommendation_service.py
  │
  │   class RecommendationService:
  │       def __init__(self):
  │           # CRITICAL: Use Claude API, NOT local Ollama (Constraint 4.2)
  │           from anthropic import Anthropic
  │           self.anthropic = Anthropic(api_key=get_vault_secret("claud"))
  │           self.model = "claude-sonnet-4-5-20250929"
  │
  │       async def generate_recommendations(user_id: UUID) -> List[Recommendation]:
  │           # Step 1: Get analytics
  │           analytics = await get_user_analytics(user_id)
  │
  │           # Step 2: Identify patterns
  │           aggregator = WeakAreaAggregator()
  │           patterns = await aggregator.identify_patterns(user_id)
  │
  │           # Step 3: Build Claude prompt (400+ lines - see below)
  │           prompt = self._build_prompt(analytics, patterns)
  │
  │           # Step 4: Call Claude API
  │           response = self.anthropic.messages.create(
  │               model=self.model,
  │               max_tokens=4000,
  │               messages=[{"role": "user", "content": prompt}]
  │           )
  │
  │           # Step 5: Parse JSON response
  │           recommendations = json.loads(response.content[0].text)
  │
  │           # Step 6: Validate resources exist
  │           validated_recs = await self._validate_resources(recommendations)
  │
  │           # Step 7: Save to database
  │           await self._save_recommendations(user_id, validated_recs)
  │
  │           return validated_recs
  │
  ├─► STAGE 3: Resource Validation
  │   File: backend/src/services/resource_validator.py
  │
  │   class ResourceValidator:
  │       async def validate_resources(recommendations: List[dict]) -> List[dict]:
  │           for rec in recommendations:
  │               validated_resources = []
  │               for resource in rec['resources']:
  │                   exists = await self._check_resource_exists(
  │                       resource['type'],
  │                       resource['id']
  │                   )
  │                   if exists:
  │                       validated_resources.append(resource)
  │                   else:
  │                       logger.warning(f"Resource {resource['id']} not found, omitted")
  │
  │               rec['resources'] = validated_resources
  │
  │           return recommendations
  │
  │       async def _check_resource_exists(resource_type: str, resource_id: str) -> bool:
  │           if resource_type == "osce_video":
  │               return await db.exists(OsceVideo, id=resource_id)
  │           elif resource_type == "mcq_topic":
  │               return await db.exists(McqQuestion, topic=resource_id)
  │           elif resource_type == "emr_patient":
  │               return await db.exists(EmrPatientScenario, id=resource_id)
  │           return False
  │
  └─► STAGE 4: API Layer
      File: backend/src/api/v1/recommendations.py

      Endpoints:
      1. POST /api/v1/recommendations/generate
         - Triggers recommendation generation
         - Returns 5 recommendations (sorted by priority)

      2. GET /api/v1/recommendations/{user_id}
         - Query params: status=[all|active|completed|skipped]
         - Returns filtered recommendations

      3. POST /api/v1/recommendations/{id}/complete
         - Marks recommendation as completed (sets completed_at timestamp)
         - Returns updated recommendation

      4. POST /api/v1/recommendations/{id}/skip
         - Marks recommendation as skipped (sets skipped_at timestamp)
         - Returns updated recommendation

FRONTEND LAYER:
  │
  ├─► React Components
  │   File: frontend/src/components/recommendations/
  │
  │   1. RecommendationsPanel.tsx (Container)
  │      - Fetches recommendations via TanStack Query
  │      - Filters by priority (high/medium/low)
  │      - Sorts by estimated_impact
  │      - Displays list of RecommendationCard components
  │
  │   2. RecommendationCard.tsx (Display)
  │      - Shows title, description, priority badge, impact chip
  │      - Displays resource chips (clickable links)
  │      - Shows Australian context (eTG/AMH references)
  │      - Action buttons: "Mark Complete", "Skip"
  │
  │   3. ResourceChip.tsx (Navigation)
  │      - Clickable chip for each resource
  │      - Icon varies by type: VideoIcon, BookIcon, PatientIcon
  │      - onClick → navigate(`/${resource.type}/${resource.id}`)
  │
  │   4. ImpactBadge.tsx (Visual)
  │      - Displays "+X.X marks" in success color
  │      - Tooltip: "Estimated AMC score improvement"
  │
  └─► API Integration
      File: frontend/src/api/recommendations.ts

      export const recommendationsApi = {
          generate: () => api.post('/recommendations/generate'),
          getAll: (userId, status) => api.get(`/recommendations/${userId}?status=${status}`),
          complete: (id) => api.post(`/recommendations/${id}/complete`),
          skip: (id) => api.post(`/recommendations/${id}/skip`)
      };
```

#### Data Flow

```
USER ACTION: Student logs in → Dashboard loads
    ↓
STEP 1: Frontend requests recommendations
    GET /api/v1/recommendations/{user_id}?status=active
    ↓
STEP 2: Backend checks if fresh recommendations exist (created within 24 hours)
    - If yes → Return cached recommendations
    - If no → Trigger generation (continue to Step 3)
    ↓
STEP 3: WeakAreaAggregator analyzes user_analytics
    - Fetch user_analytics (overall_score, specialty_heatmap, learning_velocity)
    - Detect patterns (knowledge_gap, skill_gap, documentation_gap, comprehensive_weakness)
    - Rank by severity (critical > high > medium)
    - Return top 5 patterns
    ↓
STEP 4: RecommendationService builds Claude prompt
    - Include analytics data (overall score, specialty scores, weak patterns)
    - Include pattern detection rules (see prompt template below)
    - Include Australian context requirements (eTG/AMH/PBS/MBS)
    - Include resource linking instructions (validate IDs exist)
    - Include impact estimation algorithm (gap × specialty weight)
    ↓
STEP 5: Claude API generates recommendations
    - Model: claude-sonnet-4-5-20250929
    - Input: 400+ line prompt with user data
    - Output: JSON array of 5 recommendations
    - Processing time: 3-5 seconds
    ↓
STEP 6: ResourceValidator checks resource IDs
    - For each recommendation resource:
        - Query database (osce_videos, mcq_questions, emr_patient_scenarios)
        - If exists → Keep resource
        - If not found → Remove resource (don't recommend non-existent content)
    ↓
STEP 7: Save to user_recommendations table
    - Insert 5 recommendations
    - Set created_at = NOW()
    - Set completed_at = NULL, skipped_at = NULL (active state)
    ↓
STEP 8: Return to frontend
    Response: {
        recommendations: [
            {
                id: "uuid",
                title: "Practice Cardiology OSCE History Taking",
                description: "Your MCQ knowledge is strong (85%) but...",
                recommendation_type: "skill_gap",
                priority: "high",
                estimated_impact: 3.5,
                resources: [
                    {type: "osce_video", id: "uuid", title: "Chest Pain History Taking"},
                    {type: "osce_video", id: "uuid", title: "Cardiovascular Examination"}
                ],
                australian_context: "Review eTG Cardiovascular 3.2...",
                created_at: "2026-02-16T10:00:00Z"
            },
            // ... 4 more recommendations
        ]
    }
    ↓
STEP 9: Frontend displays RecommendationsPanel
    - Render 5 RecommendationCard components
    - Display priority badges (high=red, medium=orange, low=blue)
    - Display impact chips ("+3.5 marks")
    - Display resource chips (clickable links to OSCE videos, MCQ topics, EMR patients)
    ↓
USER ACTION: Student clicks "Practice Cardiology OSCE History Taking" resource
    ↓
STEP 10: Navigate to resource
    onClick → navigate('/osce/videos/uuid')
    ↓
USER ACTION: Student watches video, practices station
    ↓
USER ACTION: Student clicks "Mark Complete"
    ↓
STEP 11: Update recommendation
    POST /api/v1/recommendations/{id}/complete
    UPDATE user_recommendations SET completed_at = NOW() WHERE id = {id}
    ↓
STEP 12: Frontend updates UI
    - Remove from active recommendations list
    - Show in "Completed" filter
    - Trigger confetti animation (celebration)
    ↓
NEXT DAY: Student returns
    - Fresh recommendations generated (exclude completed Cardiology OSCE)
    - Focus on next priority (e.g., Neurology comprehensive weakness)
    - Cycle continues...
```

### Database Schema Changes

#### New Table: user_recommendations

```sql
-- Table: user_recommendations
-- Purpose: Store Claude AI-generated study recommendations
-- Updated: Daily (new recommendations generated at 2 AM or on-demand)

CREATE TABLE user_recommendations (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key to users
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Recommendation metadata
    recommendation_type VARCHAR(50) NOT NULL, -- 'knowledge_gap', 'skill_gap', 'documentation_gap', 'comprehensive_weakness'
    title VARCHAR(200) NOT NULL, -- "Practice Cardiology OSCE History Taking"
    description TEXT NOT NULL, -- Detailed advice (200 chars)

    -- Prioritization
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
    estimated_impact NUMERIC(4,2) NOT NULL CHECK (estimated_impact >= 0 AND estimated_impact <= 15), -- 0-15 AMC marks

    -- Resources (JSONB array of objects)
    resources JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example:
    -- [
    --   {"type": "osce_video", "id": "uuid", "title": "Chest Pain History Taking", "duration_minutes": 12},
    --   {"type": "mcq_topic", "topic": "Cardiology", "subtopic": "Acute Coronary Syndrome", "question_count": 30},
    --   {"type": "emr_patient", "id": "uuid", "specialty": "Cardiology", "complexity": "Moderate"}
    -- ]

    -- Australian medical context
    australian_context TEXT NOT NULL, -- eTG/AMH/PBS/MBS references

    -- Tracking
    completed_at TIMESTAMP NULL, -- User marked as completed
    skipped_at TIMESTAMP NULL, -- User marked as skipped
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Indexes for fast queries
    CONSTRAINT user_recommendations_user_id_idx INDEX (user_id),
    CONSTRAINT user_recommendations_priority_idx INDEX (priority),
    CONSTRAINT user_recommendations_completed_at_idx INDEX (completed_at),
    CONSTRAINT user_recommendations_created_at_idx INDEX (created_at),

    -- Composite index for common query pattern
    CONSTRAINT user_recommendations_user_priority_idx INDEX (user_id, priority, completed_at)
);

-- Comments
COMMENT ON TABLE user_recommendations IS 'Claude AI-generated personalized study recommendations based on cross-module analytics';
COMMENT ON COLUMN user_recommendations.recommendation_type IS 'Pattern type: knowledge_gap (weak MCQ+OSCE), skill_gap (strong MCQ, weak OSCE), documentation_gap (strong MCQ/OSCE, weak EMR), comprehensive_weakness (all weak)';
COMMENT ON COLUMN user_recommendations.estimated_impact IS 'Estimated AMC score improvement in marks (0-15 scale based on gap × specialty weighting)';
COMMENT ON COLUMN user_recommendations.resources IS 'JSONB array of linked resources (OSCE videos, MCQ topics, EMR patients) with validated IDs';
COMMENT ON COLUMN user_recommendations.australian_context IS 'Australian-specific guidance referencing eTG, AMH, PBS medication codes, MBS item numbers, AHPRA standards';

-- Migration script (Alembic)
-- File: backend/alembic/versions/20260216_1200_011_add_user_recommendations_table.py
```

#### Sample Data

```sql
-- Sample recommendation for user with skill gap in Cardiology
INSERT INTO user_recommendations (
    user_id,
    recommendation_type,
    title,
    description,
    priority,
    estimated_impact,
    resources,
    australian_context
) VALUES (
    '123e4567-e89b-12d3-a456-426614174000', -- Sample user ID
    'skill_gap',
    'Practice Cardiology OSCE History Taking',
    'Your MCQ knowledge is strong (85%) but OSCE performance lags (60%). Focus on translating theory to clinical skills through structured history taking practice.',
    'high',
    3.50,
    '[
        {
            "type": "osce_video",
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Chest Pain History Taking (Cardiology)",
            "duration_minutes": 12
        },
        {
            "type": "osce_video",
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "title": "Cardiovascular Examination Technique",
            "duration_minutes": 15
        },
        {
            "type": "mcq_topic",
            "topic": "Cardiology",
            "subtopic": "Acute Coronary Syndrome",
            "question_count": 30
        }
    ]'::jsonb,
    'Review eTG Cardiovascular section 3.2 (Acute Coronary Syndrome management). Familiarize with PBS aspirin 100mg dispersible (code 1234), GTN sublingual spray (code 5678). Practice documentation of MBS ECG item 11700. Ensure STEMI/NSTEMI pathway knowledge aligns with ANZACS-QI guidelines.'
);
```

### API Endpoints

#### 1. POST /api/v1/recommendations/generate

**Purpose**: Generate 5 new AI-powered recommendations for user

**Authentication**: JWT required

**Request**:
```http
POST /api/v1/recommendations/generate
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "force_regenerate": false  // Optional: true = ignore 24-hour cache
}
```

**Response** (200 OK):
```json
{
    "status": "success",
    "data": {
        "recommendations": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "recommendation_type": "skill_gap",
                "title": "Practice Cardiology OSCE History Taking",
                "description": "Your MCQ knowledge is strong (85%) but OSCE performance lags (60%). Focus on translating theory to clinical skills through structured history taking practice.",
                "priority": "high",
                "estimated_impact": 3.5,
                "resources": [
                    {
                        "type": "osce_video",
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "title": "Chest Pain History Taking (Cardiology)",
                        "duration_minutes": 12,
                        "url": "/osce/videos/550e8400-e29b-41d4-a716-446655440001"
                    },
                    {
                        "type": "osce_video",
                        "id": "550e8400-e29b-41d4-a716-446655440002",
                        "title": "Cardiovascular Examination Technique",
                        "duration_minutes": 15,
                        "url": "/osce/videos/550e8400-e29b-41d4-a716-446655440002"
                    }
                ],
                "australian_context": "Review eTG Cardiovascular section 3.2...",
                "completed_at": null,
                "skipped_at": null,
                "created_at": "2026-02-16T10:00:00Z"
            },
            // ... 4 more recommendations
        ],
        "generation_metadata": {
            "analytics_snapshot": {
                "overall_score": 75.2,
                "mcq_score": 78.5,
                "osce_score": 72.1,
                "emr_score": 70.8
            },
            "patterns_detected": [
                {
                    "type": "skill_gap",
                    "specialty": "Cardiology",
                    "severity": "high"
                },
                {
                    "type": "comprehensive_weakness",
                    "specialty": "Neurology",
                    "severity": "critical"
                }
            ],
            "model_used": "claude-sonnet-4-5-20250929",
            "generation_time_seconds": 4.2
        }
    }
}
```

**Error Responses**:
- `400 Bad Request`: User has no analytics data (must complete at least 1 MCQ/OSCE/EMR session)
- `401 Unauthorized`: Invalid or expired JWT
- `429 Too Many Requests`: Rate limit exceeded (max 5 generations per day per user)
- `500 Internal Server Error`: Claude API failure
- `503 Service Unavailable`: Claude API timeout

**Business Logic**:
1. Check if recommendations exist created within 24 hours
   - If yes AND force_regenerate=false → Return cached recommendations
   - If no OR force_regenerate=true → Generate new recommendations
2. Fetch user_analytics (from PRD_INTEGRATION_002)
3. Run WeakAreaAggregator to detect patterns
4. Build Claude prompt (400+ lines)
5. Call Claude API (model: claude-sonnet-4-5-20250929)
6. Parse JSON response
7. Validate resource IDs exist in database
8. Save to user_recommendations table
9. Return recommendations

**Code Example**:
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])

class GenerateRequest(BaseModel):
    force_regenerate: bool = False

@router.post("/generate")
async def generate_recommendations(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate 5 AI-powered study recommendations"""

    # Check rate limit (5 per day)
    if await rate_limiter.check(current_user.id, limit=5, window=86400):
        raise HTTPException(status_code=429, detail="Daily generation limit reached (5/day)")

    # Check if fresh recommendations exist
    if not request.force_regenerate:
        existing = await db.query(UserRecommendation).filter(
            UserRecommendation.user_id == current_user.id,
            UserRecommendation.created_at > datetime.now() - timedelta(hours=24)
        ).all()

        if existing:
            return {
                "status": "success",
                "data": {"recommendations": [rec.to_dict() for rec in existing]}
            }

    # Generate new recommendations
    service = RecommendationService()
    try:
        recommendations = await service.generate_recommendations(current_user.id)

        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "generation_metadata": service.get_metadata()
            }
        }
    except AnthropicAPIError as e:
        logger.error(f"Claude API error: {e}")
        raise HTTPException(status_code=500, detail="AI service unavailable")
    except ValueError as e:
        logger.error(f"Insufficient data: {e}")
        raise HTTPException(status_code=400, detail="Insufficient analytics data")
```

---

#### 2. GET /api/v1/recommendations/{user_id}

**Purpose**: Retrieve all recommendations for user (filterable by status)

**Authentication**: JWT required (must match user_id or be admin)

**Request**:
```http
GET /api/v1/recommendations/123e4567-e89b-12d3-a456-426614174000?status=active
Authorization: Bearer <jwt_token>
```

**Query Parameters**:
- `status` (optional): `all` | `active` | `completed` | `skipped` (default: `active`)
- `priority` (optional): `high` | `medium` | `low` (filter by priority)
- `limit` (optional): integer (default: 50, max: 100)

**Response** (200 OK):
```json
{
    "status": "success",
    "data": {
        "recommendations": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "title": "Practice Cardiology OSCE History Taking",
                "priority": "high",
                "estimated_impact": 3.5,
                // ... full recommendation object
            }
        ],
        "pagination": {
            "total": 15,
            "returned": 5,
            "active": 5,
            "completed": 8,
            "skipped": 2
        }
    }
}
```

**Code Example**:
```python
@router.get("/{user_id}")
async def get_recommendations(
    user_id: UUID,
    status: str = "active",
    priority: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Retrieve recommendations with filtering"""

    # Authorization: user can only see own recommendations (unless admin)
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Build query
    query = db.query(UserRecommendation).filter(UserRecommendation.user_id == user_id)

    # Filter by status
    if status == "active":
        query = query.filter(
            UserRecommendation.completed_at.is_(None),
            UserRecommendation.skipped_at.is_(None)
        )
    elif status == "completed":
        query = query.filter(UserRecommendation.completed_at.isnot(None))
    elif status == "skipped":
        query = query.filter(UserRecommendation.skipped_at.isnot(None))

    # Filter by priority
    if priority:
        query = query.filter(UserRecommendation.priority == priority)

    # Order by priority (high → medium → low), then by estimated_impact (descending)
    query = query.order_by(
        case(
            (UserRecommendation.priority == "high", 1),
            (UserRecommendation.priority == "medium", 2),
            (UserRecommendation.priority == "low", 3)
        ),
        UserRecommendation.estimated_impact.desc()
    ).limit(limit)

    recommendations = await query.all()

    # Count totals
    total = await db.query(UserRecommendation).filter(UserRecommendation.user_id == user_id).count()
    active = await db.query(UserRecommendation).filter(
        UserRecommendation.user_id == user_id,
        UserRecommendation.completed_at.is_(None),
        UserRecommendation.skipped_at.is_(None)
    ).count()
    completed = await db.query(UserRecommendation).filter(
        UserRecommendation.user_id == user_id,
        UserRecommendation.completed_at.isnot(None)
    ).count()
    skipped = await db.query(UserRecommendation).filter(
        UserRecommendation.user_id == user_id,
        UserRecommendation.skipped_at.isnot(None)
    ).count()

    return {
        "status": "success",
        "data": {
            "recommendations": [rec.to_dict() for rec in recommendations],
            "pagination": {
                "total": total,
                "returned": len(recommendations),
                "active": active,
                "completed": completed,
                "skipped": skipped
            }
        }
    }
```

---

#### 3. POST /api/v1/recommendations/{id}/complete

**Purpose**: Mark recommendation as completed

**Authentication**: JWT required (must own recommendation)

**Request**:
```http
POST /api/v1/recommendations/550e8400-e29b-41d4-a716-446655440003/complete
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
    "status": "success",
    "data": {
        "recommendation": {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "title": "Practice Cardiology OSCE History Taking",
            "completed_at": "2026-02-16T14:30:00Z",
            // ... full recommendation object
        },
        "message": "Great job! 🎉 You've completed this recommendation. Keep up the excellent work!"
    }
}
```

**Code Example**:
```python
@router.post("/{id}/complete")
async def complete_recommendation(
    id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Mark recommendation as completed"""

    # Fetch recommendation
    rec = await db.query(UserRecommendation).filter(UserRecommendation.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Authorization
    if rec.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check not already completed
    if rec.completed_at:
        raise HTTPException(status_code=400, detail="Already completed")

    # Mark as completed
    rec.completed_at = datetime.now()
    rec.skipped_at = None  # Clear skip if previously skipped
    await db.commit()

    # Track analytics event
    await analytics.track(
        user_id=current_user.id,
        event="recommendation_completed",
        properties={
            "recommendation_id": str(id),
            "recommendation_type": rec.recommendation_type,
            "priority": rec.priority,
            "estimated_impact": float(rec.estimated_impact)
        }
    )

    return {
        "status": "success",
        "data": {
            "recommendation": rec.to_dict(),
            "message": "Great job! 🎉 You've completed this recommendation."
        }
    }
```

---

#### 4. POST /api/v1/recommendations/{id}/skip

**Purpose**: Mark recommendation as skipped (user chooses not to follow)

**Authentication**: JWT required (must own recommendation)

**Request**:
```http
POST /api/v1/recommendations/550e8400-e29b-41d4-a716-446655440003/skip
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
    "status": "success",
    "data": {
        "recommendation": {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "title": "Practice Cardiology OSCE History Taking",
            "skipped_at": "2026-02-16T14:30:00Z",
            // ... full recommendation object
        },
        "message": "Recommendation skipped. We'll focus on other priorities."
    }
}
```

**Code Example**:
```python
@router.post("/{id}/skip")
async def skip_recommendation(
    id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Mark recommendation as skipped"""

    # Similar logic to complete, but sets skipped_at instead
    rec = await db.query(UserRecommendation).filter(UserRecommendation.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    rec.skipped_at = datetime.now()
    rec.completed_at = None  # Clear completion if previously completed
    await db.commit()

    await analytics.track(
        user_id=current_user.id,
        event="recommendation_skipped",
        properties={
            "recommendation_id": str(id),
            "recommendation_type": rec.recommendation_type,
            "priority": rec.priority
        }
    )

    return {
        "status": "success",
        "data": {
            "recommendation": rec.to_dict(),
            "message": "Recommendation skipped. We'll focus on other priorities."
        }
    }
```

### Claude AI Prompt Template (400+ Lines)

**File**: `backend/src/services/prompts/recommendation_prompt.py`

```python
from typing import Dict, List
import json

class RecommendationPromptBuilder:
    """
    Builds comprehensive Claude prompt for generating study recommendations.

    CRITICAL: This prompt is designed for claude-sonnet-4-5-20250929.
    DO NOT use with local 7B models (Ollama) - they cannot handle this complexity.
    Evidence: Constraint 4.2 - local models failed to generate 200 MCQs.
    """

    SPECIALTIES = [
        "Cardiology", "Neurology", "Respiratory", "Gastroenterology",
        "Endocrinology", "Nephrology", "Rheumatology", "Hematology",
        "Psychiatry", "Dermatology"
    ]

    AMC_SPECIALTY_WEIGHTS = {
        # AMC Clinical Exam specialty weightings (approximate)
        "Cardiology": 0.15,  # 15% of exam
        "Neurology": 0.10,
        "Respiratory": 0.12,
        "Gastroenterology": 0.08,
        "Endocrinology": 0.10,
        "Nephrology": 0.07,
        "Rheumatology": 0.05,
        "Hematology": 0.06,
        "Psychiatry": 0.12,
        "Dermatology": 0.05,
        "Other": 0.10
    }

    def build_prompt(
        self,
        analytics: Dict,
        weak_patterns: List[Dict]
    ) -> str:
        """
        Build comprehensive Claude prompt.

        Args:
            analytics: User analytics from PRD_INTEGRATION_002
                {
                    overall_score: 75.2,
                    breakdown: {mcq: 78.5, osce: 72.1, emr: 70.8},
                    specialty_heatmap: {
                        "Cardiology": {mcq: 85, osce: 60, emr: 70},
                        "Neurology": {mcq: 55, osce: 58, emr: 50},
                        ...
                    },
                    learning_velocity: 2.3,  # % improvement/week
                    mcq_weak_topics: ["Neurology - Stroke", ...],
                    osce_weak_stations: ["Cardiology - Chest Pain", ...],
                    emr_validation_failures: ["SOAP note structure", ...]
                }

            weak_patterns: List of detected patterns from WeakAreaAggregator
                [
                    {
                        type: "skill_gap",
                        specialty: "Cardiology",
                        severity: "high",
                        scores: {mcq: 85, osce: 60, emr: 70}
                    },
                    ...
                ]

        Returns:
            Complete Claude prompt (400+ lines)
        """

        prompt = f"""You are an expert medical educator specializing in Australian AMC Clinical Examination preparation.

Your task: Generate 5 personalized, high-impact study recommendations for a medical student based on their performance analytics.

═══════════════════════════════════════════════════════════════════════════════
SECTION 1: STUDENT PERFORMANCE DATA
═══════════════════════════════════════════════════════════════════════════════

OVERALL PERFORMANCE:
- Overall Score: {analytics['overall_score']:.1f}/100 (weighted: 30% MCQ + 30% OSCE + 40% EMR)
- MCQ Accuracy: {analytics['breakdown']['mcq']:.1f}%
- OSCE Pass Rate: {analytics['breakdown']['osce']:.1f}%
- EMR Validation Score: {analytics['breakdown']['emr']:.1f}%
- Learning Velocity: {analytics['learning_velocity']:.1f}% improvement per week

SPECIALTY PERFORMANCE (3×{len(self.SPECIALTIES)} grid):
{self._format_specialty_heatmap(analytics['specialty_heatmap'])}

DETECTED WEAK PATTERNS:
{self._format_weak_patterns(weak_patterns)}

RECENT PERFORMANCE ISSUES:
MCQ Weak Topics (Bottom 5):
{self._format_list(analytics.get('mcq_weak_topics', [])[:5])}

OSCE Weak Stations (Bottom 3):
{self._format_list(analytics.get('osce_weak_stations', [])[:3])}

EMR Validation Failures (Common Mistakes):
{self._format_list(analytics.get('emr_validation_failures', [])[:3])}

═══════════════════════════════════════════════════════════════════════════════
SECTION 2: PATTERN DETECTION RULES (CRITICAL - FOLLOW EXACTLY)
═══════════════════════════════════════════════════════════════════════════════

You MUST analyze the data above using these 4 pattern types:

1. KNOWLEDGE GAP
   Definition: Weak MCQ (<70%) + Weak OSCE (<70%) in same specialty
   Root Cause: Insufficient theoretical knowledge foundation
   Example: Neurology MCQ 55%, OSCE 58% → Student lacks basic neurology knowledge
   Recommendation Strategy:
   - Start with MCQ bank to build theoretical foundation
   - Review AMC Part 1 materials for specialty
   - Reference eTG/AMH guidelines for Australian context
   - THEN practice OSCE (after theory solidified)
   Resources to Link:
   - MCQ topics (same specialty, difficulty: Easy → Medium)
   - eTG/AMH guideline sections
   - AMC Part 1 blueprint references

   EXAMPLE OUTPUT:
   {{
     "title": "Build Neurology Foundation with MCQ Bank",
     "description": "Both MCQ (55%) and OSCE (58%) are weak in Neurology. Start with theoretical foundation through MCQ practice before attempting OSCE stations.",
     "recommendation_type": "knowledge_gap",
     "priority": "high",
     "estimated_impact": 4.2,
     "resources": [
       {{
         "type": "mcq_topic",
         "topic": "Neurology",
         "subtopic": "Stroke & TIA",
         "question_count": 30
       }},
       {{
         "type": "mcq_topic",
         "topic": "Neurology",
         "subtopic": "Seizure Disorders",
         "question_count": 25
       }}
     ],
     "australian_context": "Review AMC Part 1 Neurology blueprint (12% exam weight). Study eTG Neurology section 8 (Stroke management). Familiarize with PBS alteplase criteria for thrombolysis."
   }}

2. SKILL GAP
   Definition: Strong MCQ (≥80%) + Weak OSCE (<60%) in same specialty
   Root Cause: Knowledge not translated to clinical skills
   Example: Cardiology MCQ 85%, OSCE 60% → Student knows theory but struggles with patient interaction
   Recommendation Strategy:
   - Skip MCQ review (already strong)
   - Focus heavily on OSCE practice stations
   - Watch technique videos (history taking, physical examination)
   - Practice communication skills
   Resources to Link:
   - OSCE videos (same specialty, station type: History Taking, Physical Exam)
   - OSCE practice stations (same specialty, difficulty: Moderate)

   EXAMPLE OUTPUT:
   {{
     "title": "Practice Cardiology OSCE History Taking",
     "description": "Your MCQ knowledge is excellent (85%) but OSCE performance lags (60%). Focus on translating theory to clinical skills through structured history taking practice.",
     "recommendation_type": "skill_gap",
     "priority": "high",
     "estimated_impact": 3.5,
     "resources": [
       {{
         "type": "osce_video",
         "id": "validate-this-id",
         "title": "Chest Pain History Taking (Cardiology)",
         "duration_minutes": 12
       }},
       {{
         "type": "osce_video",
         "id": "validate-this-id",
         "title": "Cardiovascular Examination Technique",
         "duration_minutes": 15
       }}
     ],
     "australian_context": "Review eTG Cardiovascular section 3.2 (Acute Coronary Syndrome). Familiarize with PBS aspirin 100mg dispersible (code 1234), GTN sublingual spray (code 5678). Practice MBS ECG item 11700 documentation."
   }}

3. DOCUMENTATION GAP
   Definition: Strong MCQ (≥70%) + Strong OSCE (≥70%) + Weak EMR (<60%) in same specialty
   Root Cause: Poor SOAP note writing, documentation skills
   Example: Respiratory MCQ 80%, OSCE 75%, EMR 55% → Student knows medicine, can examine patients, but can't document properly
   Recommendation Strategy:
   - Skip MCQ/OSCE review (already strong)
   - Focus on EMR SOAP note practice
   - Review AMC documentation rubric
   - Practice differential diagnosis writing
   - Learn PBS medication codes, MBS item numbers
   Resources to Link:
   - EMR patient scenarios (same specialty, complexity: Moderate → High)
   - EMR training guides (SOAP note structure, rubric)

   EXAMPLE OUTPUT:
   {{
     "title": "Improve Respiratory EMR SOAP Note Writing",
     "description": "Strong clinical knowledge (MCQ 80%, OSCE 75%) but weak EMR documentation (55%). Focus on structured SOAP notes, differential diagnosis, and management plans.",
     "recommendation_type": "documentation_gap",
     "priority": "medium",
     "estimated_impact": 2.1,
     "resources": [
       {{
         "type": "emr_patient",
         "id": "validate-this-id",
         "specialty": "Respiratory",
         "complexity": "Moderate",
         "scenario_title": "Acute Asthma Exacerbation"
       }},
       {{
         "type": "emr_patient",
         "id": "validate-this-id",
         "specialty": "Respiratory",
         "complexity": "Moderate",
         "scenario_title": "COPD with Infective Exacerbation"
       }}
     ],
     "australian_context": "Practice eTG Respiratory section 5 (Asthma) documentation. Include PBS salbutamol inhaler (code 3456), prednisolone 25mg (code 7890). Use MBS spirometry item 11503. Follow AMC SOAP note rubric."
   }}

4. COMPREHENSIVE WEAKNESS
   Definition: All 3 modules <60% in same specialty
   Root Cause: Complete knowledge + skill gap (most severe)
   Example: Neurology MCQ 50%, OSCE 55%, EMR 50% → Student weak across all dimensions
   Recommendation Strategy:
   - Systematic learning path: MCQ foundation → OSCE practice → EMR documentation
   - Allocate more time (highest priority)
   - Break into smaller chunks (subtopics)
   Resources to Link:
   - MCQ topics (difficulty: Easy, foundational concepts)
   - OSCE videos (introductory, basic techniques)
   - EMR patients (difficulty: Easy, simple scenarios)

   EXAMPLE OUTPUT:
   {{
     "title": "Systematic Neurology Study Plan (MCQ → OSCE → EMR)",
     "description": "All modules weak in Neurology (50-55%). Start with MCQ foundation, then OSCE skills, then EMR documentation. Focus on stroke, seizures, headache (high AMC yield).",
     "recommendation_type": "comprehensive_weakness",
     "priority": "critical",
     "estimated_impact": 5.5,
     "resources": [
       {{
         "type": "mcq_topic",
         "topic": "Neurology",
         "subtopic": "Stroke & TIA Basics",
         "question_count": 20
       }},
       {{
         "type": "osce_video",
         "id": "validate-this-id",
         "title": "Neurological Examination Introduction",
         "duration_minutes": 18
       }},
       {{
         "type": "emr_patient",
         "id": "validate-this-id",
         "specialty": "Neurology",
         "complexity": "Easy",
         "scenario_title": "Simple Headache Assessment"
       }}
     ],
     "australian_context": "Review AMC Part 1 Neurology blueprint (12% exam weight). Start with eTG Neurology section 1 (Overview). Familiarize with PBS medication codes for common neurology drugs."
   }}

═══════════════════════════════════════════════════════════════════════════════
SECTION 3: PRIORITIZATION ALGORITHM
═══════════════════════════════════════════════════════════════════════════════

You MUST prioritize recommendations using this algorithm:

1. Severity Ranking:
   - Critical (comprehensive_weakness) → Highest priority
   - High (knowledge_gap, skill_gap with large gap >20%)
   - Medium (skill_gap with moderate gap 10-20%, documentation_gap)
   - Low (small gaps <10%)

2. AMC Exam Weighting:
   - Cardiology: 15% of exam → Higher priority
   - Neurology: 10% of exam
   - Respiratory: 12% of exam
   - Psychiatry: 12% of exam
   - Others: 5-8% of exam → Lower priority

3. Estimated Impact Calculation:
   Impact = (Gap to 80% threshold) × (AMC specialty weight) × (Learning velocity factor)

   Example:
   - Cardiology: Current 60%, Gap to 80% = 20%
   - AMC weight: 15%
   - Learning velocity: 2.3%/week → Factor 1.2 (fast learner)
   - Impact = 20 × 0.15 × 1.2 = 3.6 AMC marks

   Cap: Maximum 15 AMC marks per recommendation

4. Sorting:
   - Sort by severity (critical → high → medium → low)
   - Within same severity, sort by estimated_impact (descending)
   - Return top 5 recommendations

═══════════════════════════════════════════════════════════════════════════════
SECTION 4: RESOURCE LINKING INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

For each recommendation, you MUST link to specific resources:

RESOURCE TYPES:
1. OSCE Videos
   - Provide: {{"type": "osce_video", "id": "placeholder-uuid", "title": "...", "duration_minutes": X}}
   - NOTE: Backend will validate IDs exist before saving
   - Use descriptive titles that match specialty + station type
   - Prefer videos 10-20 minutes (optimal length)

2. MCQ Topics
   - Provide: {{"type": "mcq_topic", "topic": "Cardiology", "subtopic": "Acute Coronary Syndrome", "question_count": X}}
   - NOTE: Backend will validate topic exists in database
   - Focus on high-yield subtopics aligned with AMC blueprint
   - Suggest 20-40 questions per session

3. EMR Patient Scenarios
   - Provide: {{"type": "emr_patient", "id": "placeholder-uuid", "specialty": "...", "complexity": "Easy|Moderate|High", "scenario_title": "..."}}
   - NOTE: Backend will validate IDs exist
   - Match complexity to student's skill level
   - Focus on common presentations (high AMC yield)

LINKING RULES:
- Knowledge Gap → 2-3 MCQ topics
- Skill Gap → 2-3 OSCE videos
- Documentation Gap → 2-3 EMR patients
- Comprehensive Weakness → 1 MCQ topic + 1 OSCE video + 1 EMR patient

═══════════════════════════════════════════════════════════════════════════════
SECTION 5: AUSTRALIAN MEDICAL CONTEXT (MANDATORY)
═══════════════════════════════════════════════════════════════════════════════

EVERY recommendation MUST include australian_context with:

1. eTG/AMH Guidelines:
   - Reference specific eTG sections (e.g., "eTG Cardiovascular 3.2")
   - Mention AMH medication monographs where relevant
   - Link to AHPRA standards if applicable

2. PBS Medication Codes:
   - Include PBS codes for common medications (e.g., "aspirin 100mg code 1234")
   - Mention PBS restrictions/criteria (e.g., "PBS alteplase restricted to stroke within 4.5 hours")
   - Use Australian drug names (paracetamol NOT acetaminophen, salbutamol NOT albuterol, adrenaline NOT epinephrine)

3. MBS Item Numbers:
   - Include MBS item numbers for investigations (e.g., "ECG item 11700", "spirometry item 11503")
   - Mention Medicare rebate eligibility where relevant

4. Australian Terminology:
   - Use Australian spelling (organisation, programme, haemoglobin)
   - Reference Australian bodies (ANZACS-QI, RANZCP, RACP)
   - Use SI units (mmol/L NOT mg/dL, °C NOT °F)

EXAMPLES:
- Good: "Review eTG Cardiovascular 3.2 (STEMI). PBS aspirin 100mg (1234), GTN spray (5678). MBS ECG item 11700."
- Bad: "Review UpToDate for STEMI management. Consider acetaminophen." (❌ US resource, wrong drug name)

═══════════════════════════════════════════════════════════════════════════════
SECTION 6: OUTPUT FORMAT (JSON SCHEMA)
═══════════════════════════════════════════════════════════════════════════════

You MUST return a valid JSON array of exactly 5 recommendations.

SCHEMA:
[
  {{
    "title": "string (max 50 chars, actionable, specific)",
    "description": "string (max 200 chars, explain WHY this recommendation, reference scores)",
    "recommendation_type": "knowledge_gap|skill_gap|documentation_gap|comprehensive_weakness",
    "priority": "high|medium|low",
    "estimated_impact": 0.0-15.0,  // float, 2 decimal places
    "resources": [
      {{
        "type": "osce_video|mcq_topic|emr_patient",
        "id": "placeholder-uuid",  // Backend will validate
        "title": "string",
        "duration_minutes": integer,  // For OSCE videos
        "topic": "string",  // For MCQ topics
        "subtopic": "string",  // For MCQ topics
        "specialty": "string",  // For EMR patients
        "complexity": "Easy|Moderate|High"  // For EMR patients
      }}
    ],
    "australian_context": "string (eTG/AMH/PBS/MBS references, 100-200 chars)"
  }},
  // ... 4 more recommendations
]

VALIDATION RULES:
- MUST return exactly 5 recommendations
- MUST use only valid recommendation_type values
- MUST use only valid priority values
- estimated_impact MUST be 0.0-15.0
- resources MUST be non-empty array (1-3 resources per recommendation)
- australian_context MUST include at least one eTG/AMH/PBS/MBS reference
- All strings MUST be non-empty
- JSON MUST be valid (no trailing commas, proper escaping)

═══════════════════════════════════════════════════════════════════════════════
SECTION 7: QUALITY CHECKLIST (VALIDATE BEFORE RETURNING)
═══════════════════════════════════════════════════════════════════════════════

Before returning JSON, verify:

✅ Exactly 5 recommendations
✅ Sorted by severity/priority (critical/high first)
✅ Each recommendation addresses a detected weak pattern
✅ Estimated impacts are realistic (0-15 marks, based on gap × specialty weight)
✅ Resources are appropriate for recommendation type (MCQ for knowledge gaps, OSCE for skill gaps, etc.)
✅ Australian context includes eTG/AMH/PBS/MBS references
✅ Australian terminology used (paracetamol, salbutamol, adrenaline)
✅ No US resources mentioned (UpToDate, Medscape)
✅ Valid JSON (parseable, no syntax errors)
✅ Titles are actionable and specific (not generic like "Study more")
✅ Descriptions explain WHY (reference student's scores)

═══════════════════════════════════════════════════════════════════════════════
SECTION 8: CONSTRAINTS & EDGE CASES
═══════════════════════════════════════════════════════════════════════════════

EDGE CASES:

1. Student has no weak patterns (all scores >80%):
   - Generate "optimization" recommendations (fine-tuning, exam technique)
   - Priority: low
   - Focus on high-yield topics for last-minute review

2. Student is weak in everything (<50% overall):
   - Prioritize foundation-building (MCQ basics)
   - Break into smaller chunks (one specialty at a time)
   - Set realistic goals (reach 60% before aiming for 80%)

3. Student completed previous recommendations:
   - Exclude completed specialties/topics
   - Move to next priority area
   - Acknowledge progress in description ("Great job on Cardiology! Now let's tackle...")

4. Limited resources available for specialty:
   - Suggest general study strategies (textbooks, AMC blueprint review)
   - Link to related specialties (e.g., Cardiology → Respiratory for heart-lung interactions)

CONSTRAINTS:

- DO NOT recommend more than 2 recommendations per specialty (avoid overwhelming)
- DO NOT recommend same resource type 3+ times (vary: MCQ, OSCE, EMR)
- DO NOT suggest external paid resources (UpToDate, Medscape, AMBOSS) - only internal platform resources
- DO NOT exceed 15 AMC marks for estimated_impact (unrealistic)
- DO NOT use placeholder text in titles/descriptions (be specific)

═══════════════════════════════════════════════════════════════════════════════
BEGIN GENERATION
═══════════════════════════════════════════════════════════════════════════════

Based on the student performance data in SECTION 1 and following ALL rules in SECTIONS 2-8, generate 5 prioritized study recommendations.

Return ONLY the JSON array (no additional text, no markdown code blocks, no explanations).

JSON Array:
"""

        return prompt

    def _format_specialty_heatmap(self, heatmap: Dict) -> str:
        """Format specialty heatmap as ASCII table"""
        lines = []
        lines.append("┌────────────────┬─────────┬─────────┬─────────┐")
        lines.append("│ Specialty      │   MCQ   │  OSCE   │   EMR   │")
        lines.append("├────────────────┼─────────┼─────────┼─────────┤")

        for specialty in self.SPECIALTIES:
            scores = heatmap.get(specialty, {"mcq": 0, "osce": 0, "emr": 0})
            lines.append(
                f"│ {specialty:14s} │ {scores['mcq']:5.1f}%  │ {scores['osce']:5.1f}%  │ {scores['emr']:5.1f}%  │"
            )

        lines.append("└────────────────┴─────────┴─────────┴─────────┘")
        return "\n".join(lines)

    def _format_weak_patterns(self, patterns: List[Dict]) -> str:
        """Format detected patterns"""
        if not patterns:
            return "No significant weak patterns detected (all specialties >70%)"

        lines = []
        for i, pattern in enumerate(patterns, 1):
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(pattern['severity'], "⚪")

            lines.append(
                f"{i}. {severity_icon} {pattern['type'].upper()} - {pattern['specialty']}\n"
                f"   Scores: MCQ {pattern['scores']['mcq']:.1f}%, "
                f"OSCE {pattern['scores']['osce']:.1f}%, "
                f"EMR {pattern['scores']['emr']:.1f}%\n"
                f"   Severity: {pattern['severity']}"
            )

        return "\n".join(lines)

    def _format_list(self, items: List[str]) -> str:
        """Format list items"""
        if not items:
            return "- None (performing well across all areas)"
        return "\n".join([f"- {item}" for item in items])
```

### Technology Stack

**Backend**:
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **AI Integration**: Anthropic Python SDK
- **LLM Model**: claude-sonnet-4-5-20250929 (NOT local Ollama - per Constraint 4.2)
- **Authentication**: JWT (existing system)
- **Testing**: pytest, pytest-asyncio
- **Secrets**: Vault (key: "claud")

**Frontend**:
- **Language**: TypeScript
- **Framework**: React 18
- **UI Library**: Material-UI (MUI)
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Testing**: Vitest, React Testing Library

**Infrastructure**:
- **Database Migration**: Alembic
- **API Documentation**: OpenAPI/Swagger
- **Logging**: Python logging module
- **Monitoring**: (existing system)

### Integration Points

**Integrates With**:
- PRD_INTEGRATION_002 (Unified Progress Tracking): Consumes user_analytics data
- PRD_BACKEND_002 (EMR Session API): Uses EMR metrics
- Existing MCQ system: Links to MCQ topics
- Existing OSCE system: Links to OSCE videos
- Existing EMR system: Links to EMR patient scenarios
- Vault: Retrieves "claud" API key for Anthropic

**Consumed By**:
- Frontend Dashboard (displays recommendations)
- Frontend OSCE Video Player (receives clicks from resource links)
- Frontend MCQ Practice Interface (receives clicks from resource links)
- Frontend EMR Practice System (receives clicks from resource links)

**Depends On**:
- Anthropic Claude API: claude-sonnet-4-5-20250929
- PostgreSQL database (user_analytics, osce_videos, mcq_questions, emr_patient_scenarios tables)
- Vault secrets management ("claud" key)

### Security Considerations

- [x] **Input Validation**: Pydantic schemas for all API requests
- [x] **Authentication**: JWT required on all endpoints (verify user_id matches JWT)
- [x] **Authorization**: Users can only access own recommendations (except admins)
- [x] **Encryption**: HTTPS for API calls, TLS for database connections
- [x] **No Hardcoded Credentials**: Use Vault secret "claud" (NOT "anthropic")
- [x] **API Key Protection**: Claude API key stored in Vault, never logged
- [x] **Rate Limiting**: Max 5 recommendation generations per user per day (prevent abuse)
- [x] **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- [x] **XSS Prevention**: React auto-escapes all user-generated content
- [x] **CSRF Protection**: JWT-based auth (no cookies, no CSRF risk)

**Security Code Example**:
```python
from vault_client import get_vault_secret
from anthropic import Anthropic

class RecommendationService:
    def __init__(self):
        # CORRECT: Retrieve from Vault with key "claud"
        api_key = get_vault_secret("claud")
        self.anthropic = Anthropic(api_key=api_key)

        # ❌ WRONG: Hardcoded key
        # self.anthropic = Anthropic(api_key="sk-ant-...")

        # ❌ WRONG: Wrong Vault key
        # api_key = get_vault_secret("anthropic")
```

### Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Generation Time** | <2s (p95) | Claude API typically 3-5s, but acceptable |
| **API Retrieval Time** | <100ms (p95) | Simple SELECT query with index |
| **Database Query Time** | <50ms | user_recommendations table lookup |
| **Claude API Timeout** | 10s | Fail gracefully if timeout |
| **Concurrent Users** | 100+ | Standard FastAPI async support |
| **Resource Validation** | <200ms | Parallel validation of all resource IDs |

**Performance Optimization**:
1. **Caching**: Cache recommendations for 24 hours (avoid regenerating every request)
2. **Async Processing**: All database queries async (don't block event loop)
3. **Parallel Resource Validation**: Validate all resource IDs concurrently (asyncio.gather)
4. **Index Optimization**: Composite index on (user_id, priority, completed_at)
5. **Pagination**: Limit results to 50 recommendations per request

---

## L - LOOP (Iterative Development)

### Phase 1: Foundation (25% of effort, 3-4 hours)

**Goal**: Database schema, WeakAreaAggregator, basic API scaffolding

**Tasks**:
1. **Create database migration** (30 min)
   - Alembic migration for user_recommendations table
   - Indexes: user_id, priority, completed_at, composite (user_id, priority, completed_at)
   - Run migration in dev environment

2. **Implement WeakAreaAggregator** (1.5 hours)
   - File: backend/src/services/weak_area_aggregator.py
   - 4 pattern detection methods (knowledge_gap, skill_gap, documentation_gap, comprehensive_weakness)
   - Severity ranking algorithm
   - Integration with user_analytics (PRD_INTEGRATION_002)

3. **Create API skeleton** (1 hour)
   - File: backend/src/api/v1/recommendations.py
   - 4 endpoint stubs (generate, get, complete, skip)
   - Pydantic request/response models
   - JWT authentication decorators

4. **Unit tests for WeakAreaAggregator** (1 hour)
   - Test pattern detection (4 scenarios)
   - Test severity ranking
   - Test edge cases (no weak patterns, all weak)

**Validation Gate**:
- [ ] Database migration runs successfully (no errors)
- [ ] user_recommendations table created with all columns
- [ ] Indexes created (verify with \d+ user_recommendations in psql)
- [ ] WeakAreaAggregator detects all 4 pattern types correctly
- [ ] Unit tests pass (100% pass rate)
- [ ] No compilation errors (pytest runs without import errors)

---

### Phase 2: Core Functionality (50% of effort, 6-7 hours)

**Goal**: Claude AI integration, recommendation generation, resource validation

**Tasks**:
1. **Build Claude prompt template** (2 hours)
   - File: backend/src/services/prompts/recommendation_prompt.py
   - 400+ line prompt (all sections 1-8)
   - Australian context integration (eTG/AMH/PBS/MBS)
   - Pattern detection rules with examples
   - Impact estimation algorithm

2. **Implement RecommendationService** (2.5 hours)
   - File: backend/src/services/recommendation_service.py
   - Claude API integration (model: claude-sonnet-4-5-20250929)
   - Vault integration (retrieve "claud" key)
   - JSON parsing and validation
   - Error handling (API timeout, malformed JSON)

3. **Implement ResourceValidator** (1 hour)
   - File: backend/src/services/resource_validator.py
   - Validate OSCE video IDs (query osce_videos table)
   - Validate MCQ topics (query mcq_questions table)
   - Validate EMR patient IDs (query emr_patient_scenarios table)
   - Parallel validation (asyncio.gather)

4. **Complete API endpoints** (1.5 hours)
   - POST /api/v1/recommendations/generate (connect to RecommendationService)
   - GET /api/v1/recommendations/{user_id} (query with filters)
   - POST /api/v1/recommendations/{id}/complete (update completed_at)
   - POST /api/v1/recommendations/{id}/skip (update skipped_at)
   - Rate limiting (5 per day)

5. **Integration tests** (1 hour)
   - Test full generation flow (analytics → patterns → Claude → validation → save)
   - Test resource validation (valid IDs, invalid IDs)
   - Test API endpoints (happy path, error cases)
   - Mock Claude API (avoid API costs in tests)

**Validation Gate**:
- [ ] Claude API integration works (generate 1 test recommendation)
- [ ] Prompt template includes all 8 sections (verify line count ≥400)
- [ ] Resource validation correctly filters non-existent resources
- [ ] All API endpoints return valid responses
- [ ] Integration tests ≥70% coverage
- [ ] All tests pass (100% pass rate)
- [ ] Security scan (bandit): 0 HIGH/CRITICAL
- [ ] No hardcoded credentials (grep for "sk-ant-", "anthropic")

---

### Phase 3: Polish & Frontend (25% of effort, 3-4 hours)

**Goal**: Frontend UI, user testing, documentation

**Tasks**:
1. **Create React components** (2 hours)
   - RecommendationsPanel.tsx (container, fetch data, filter/sort)
   - RecommendationCard.tsx (display recommendation with badges, buttons)
   - ResourceChip.tsx (clickable resource links)
   - ImpactBadge.tsx ("+X.X marks" display)

2. **API integration in frontend** (30 min)
   - File: frontend/src/api/recommendations.ts
   - TanStack Query hooks (useRecommendations, useGenerateRecommendations, useCompleteRecommendation)
   - Error handling (toast notifications)

3. **Navigation integration** (30 min)
   - ResourceChip onClick → navigate to OSCE video, MCQ topic, or EMR patient
   - Test navigation from recommendation to resource pages

4. **User acceptance testing** (1 hour)
   - Generate recommendations for 3 test users (different patterns)
   - Verify recommendations are relevant and actionable
   - Verify Australian context includes eTG/AMH/PBS/MBS
   - Verify resource links work (no 404 errors)
   - Test complete/skip actions

5. **Documentation** (1 hour)
   - API documentation (OpenAPI schema)
   - Code comments (docstrings for all public functions)
   - README update (setup instructions for Claude API key)

**Validation Gate**:
- [ ] All React components render without errors
- [ ] Recommendations display correctly (priority badges, impact chips)
- [ ] Resource links navigate to correct pages
- [ ] Complete/skip actions update UI instantly
- [ ] Mobile responsive (test on 375px viewport)
- [ ] Performance: Dashboard loads in <2s
- [ ] E2E test: Generate → Display → Click resource → Navigate
- [ ] Documentation complete (API docs, code comments)

---

## P - PLAN (Detailed Implementation)

### Task Breakdown (1-2 hour chunks)

#### Phase 1 Tasks

**Task 1.1: Create Database Migration**
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Alembic migration file `backend/alembic/versions/20260216_1200_011_add_user_recommendations_table.py`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] user_recommendations table created with all columns (id, user_id, recommendation_type, title, description, priority, estimated_impact, resources, australian_context, completed_at, skipped_at, created_at)
  - [ ] Foreign key constraint on user_id → users(id)
  - [ ] Indexes created: user_id, priority, completed_at, (user_id, priority, completed_at)
  - [ ] Migration runs successfully: `alembic upgrade head`
  - [ ] Rollback works: `alembic downgrade -1`

**Task 1.2: Implement WeakAreaAggregator**
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: `backend/src/services/weak_area_aggregator.py`
- **Dependencies**: Task 1.1 (need user_analytics data schema)
- **Acceptance Criteria**:
  - [ ] `identify_patterns()` method detects 4 pattern types
  - [ ] Knowledge gap detection: MCQ <70% AND OSCE <70%
  - [ ] Skill gap detection: MCQ ≥80% AND OSCE <60%
  - [ ] Documentation gap detection: MCQ ≥70% AND OSCE ≥70% AND EMR <60%
  - [ ] Comprehensive weakness detection: All 3 modules <60%
  - [ ] Severity ranking: critical > high > medium
  - [ ] Returns top 5 patterns
  - [ ] Unit tests pass (test_identify_patterns_knowledge_gap, test_identify_patterns_skill_gap, test_severity_ranking)

**Task 1.3: Create API Skeleton**
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/src/api/v1/recommendations.py` (stubs)
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] 4 endpoint stubs created (generate, get, complete, skip)
  - [ ] Pydantic models: GenerateRequest, RecommendationResponse
  - [ ] JWT authentication decorator applied to all endpoints
  - [ ] OpenAPI docs auto-generated: http://localhost:8000/docs shows endpoints
  - [ ] Endpoints return 501 Not Implemented (stubs only)

**Task 1.4: Unit Tests for WeakAreaAggregator**
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/tests/test_services/test_weak_area_aggregator.py`
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Test knowledge gap pattern (MCQ 55%, OSCE 58% → knowledge_gap)
  - [ ] Test skill gap pattern (MCQ 85%, OSCE 60% → skill_gap)
  - [ ] Test documentation gap (MCQ 80%, OSCE 75%, EMR 55% → documentation_gap)
  - [ ] Test comprehensive weakness (MCQ 50%, OSCE 55%, EMR 50% → comprehensive_weakness)
  - [ ] Test severity ranking (critical before high before medium)
  - [ ] Test edge case: No weak patterns (all scores >80%)
  - [ ] Coverage ≥80% for weak_area_aggregator.py
  - [ ] All tests pass: `pytest backend/tests/test_services/test_weak_area_aggregator.py -v`

---

#### Phase 2 Tasks

**Task 2.1: Build Claude Prompt Template**
- **Effort**: 2 hours
- **Owner**: AI Engineer / Backend Engineer
- **Deliverable**: `backend/src/services/prompts/recommendation_prompt.py`
- **Dependencies**: Task 1.2 (need weak_patterns format)
- **Acceptance Criteria**:
  - [ ] Prompt template ≥400 lines
  - [ ] Section 1: Student performance data (analytics, heatmap, weak patterns)
  - [ ] Section 2: Pattern detection rules (4 types with examples)
  - [ ] Section 3: Prioritization algorithm (severity + AMC weighting)
  - [ ] Section 4: Resource linking instructions (OSCE/MCQ/EMR)
  - [ ] Section 5: Australian context requirements (eTG/AMH/PBS/MBS)
  - [ ] Section 6: JSON output schema
  - [ ] Section 7: Quality checklist
  - [ ] Section 8: Constraints & edge cases
  - [ ] Test prompt with sample analytics data → Valid JSON output
  - [ ] Australian terminology used (paracetamol, salbutamol, adrenaline)

**Task 2.2: Implement RecommendationService**
- **Effort**: 2.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: `backend/src/services/recommendation_service.py`
- **Dependencies**: Task 2.1 (prompt template)
- **Acceptance Criteria**:
  - [ ] Anthropic client initialized with Vault secret "claud"
  - [ ] Model: claude-sonnet-4-5-20250929
  - [ ] `generate_recommendations()` method:
    - Fetches user_analytics
    - Calls WeakAreaAggregator
    - Builds prompt using RecommendationPromptBuilder
    - Calls Claude API (max_tokens=4000)
    - Parses JSON response
    - Returns 5 recommendations
  - [ ] Error handling: Claude API timeout (10s), malformed JSON, API rate limit
  - [ ] Logging: Log API call duration, token usage
  - [ ] Test with sample user → 5 valid recommendations returned
  - [ ] No hardcoded API key (grep for "sk-ant-" returns 0 matches)

**Task 2.3: Implement ResourceValidator**
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/src/services/resource_validator.py`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `validate_resources()` method accepts list of recommendations
  - [ ] For each resource:
    - If type=osce_video → Query osce_videos table by ID
    - If type=mcq_topic → Query mcq_questions table by topic
    - If type=emr_patient → Query emr_patient_scenarios table by ID
    - If exists → Keep resource
    - If not found → Remove resource, log warning
  - [ ] Parallel validation (asyncio.gather for speed)
  - [ ] Unit test: 3 valid resources + 1 invalid → Returns 3 resources
  - [ ] Performance: <200ms for 15 resource validations (5 recs × 3 resources)

**Task 2.4: Complete API Endpoints**
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: `backend/src/api/v1/recommendations.py` (complete)
- **Dependencies**: Task 2.2, 2.3
- **Acceptance Criteria**:
  - [ ] POST /generate: Calls RecommendationService, returns 5 recommendations
  - [ ] GET /{user_id}: Queries user_recommendations table, filters by status/priority
  - [ ] POST /{id}/complete: Updates completed_at, returns updated recommendation
  - [ ] POST /{id}/skip: Updates skipped_at, returns updated recommendation
  - [ ] Rate limiting: 5 generations per user per day (429 error if exceeded)
  - [ ] Authorization: User can only access own recommendations
  - [ ] Manual test: curl all 4 endpoints → Valid responses
  - [ ] OpenAPI docs updated: http://localhost:8000/docs shows request/response examples

**Task 2.5: Integration Tests**
- **Effort**: 1 hour
- **Owner**: Backend Engineer / QA
- **Deliverable**: `backend/tests/test_api/test_recommendations.py`
- **Dependencies**: Task 2.4
- **Acceptance Criteria**:
  - [ ] Test full generation flow (mock Claude API to avoid costs)
  - [ ] Test resource validation (valid IDs pass, invalid IDs filtered)
  - [ ] Test API endpoints:
    - POST /generate → 201 Created, 5 recommendations returned
    - GET /{user_id}?status=active → 200 OK, active recommendations only
    - POST /{id}/complete → 200 OK, completed_at timestamp set
    - POST /{id}/skip → 200 OK, skipped_at timestamp set
  - [ ] Test error cases:
    - 400 Bad Request (no analytics data)
    - 401 Unauthorized (no JWT)
    - 403 Forbidden (access other user's recommendations)
    - 429 Too Many Requests (rate limit exceeded)
  - [ ] Coverage ≥70% for recommendations.py
  - [ ] All tests pass: `pytest backend/tests/test_api/test_recommendations.py -v`

---

#### Phase 3 Tasks

**Task 3.1: Create React Components**
- **Effort**: 2 hours
- **Owner**: Frontend Engineer
- **Deliverable**:
  - `frontend/src/components/recommendations/RecommendationsPanel.tsx`
  - `frontend/src/components/recommendations/RecommendationCard.tsx`
  - `frontend/src/components/recommendations/ResourceChip.tsx`
  - `frontend/src/components/recommendations/ImpactBadge.tsx`
- **Dependencies**: Task 2.4 (API endpoints working)
- **Acceptance Criteria**:
  - [ ] RecommendationsPanel: Fetches recommendations, filters by priority, sorts by impact
  - [ ] RecommendationCard: Displays title, description, priority badge (high=red, medium=orange, low=blue), impact chip ("+X.X marks"), resources, Australian context
  - [ ] ResourceChip: Clickable chip with icon (VideoIcon for OSCE, BookIcon for MCQ, PatientIcon for EMR)
  - [ ] ImpactBadge: Green chip showing "+X.X marks" with tooltip
  - [ ] Action buttons: "Mark Complete" (success color), "Skip" (outlined)
  - [ ] Component tests: Render without errors, display data correctly
  - [ ] Storybook stories created (optional but recommended)

**Task 3.2: API Integration in Frontend**
- **Effort**: 30 min
- **Owner**: Frontend Engineer
- **Deliverable**: `frontend/src/api/recommendations.ts`
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - [ ] TanStack Query hooks:
    - `useRecommendations(userId, status)` → GET /recommendations/{userId}
    - `useGenerateRecommendations()` → POST /recommendations/generate
    - `useCompleteRecommendation(id)` → POST /recommendations/{id}/complete
    - `useSkipRecommendation(id)` → POST /recommendations/{id}/skip
  - [ ] Error handling: Toast notifications for 400/401/429 errors
  - [ ] Loading states: Skeleton loaders while fetching
  - [ ] Cache invalidation: Invalidate recommendations query after complete/skip

**Task 3.3: Navigation Integration**
- **Effort**: 30 min
- **Owner**: Frontend Engineer
- **Deliverable**: Navigation logic in ResourceChip component
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - [ ] ResourceChip onClick:
    - type=osce_video → navigate(`/osce/videos/${resource.id}`)
    - type=mcq_topic → navigate(`/mcq/topics/${resource.topic}`)
    - type=emr_patient → navigate(`/emr/patients/${resource.id}`)
  - [ ] Test navigation: Click chip → Correct page loads
  - [ ] Back button works (React Router history)

**Task 3.4: User Acceptance Testing**
- **Effort**: 1 hour
- **Owner**: QA / PM
- **Deliverable**: UAT test report
- **Dependencies**: Task 3.3
- **Acceptance Criteria**:
  - [ ] Generate recommendations for 3 test users (knowledge gap, skill gap, documentation gap)
  - [ ] Verify recommendations match weak patterns
  - [ ] Verify Australian context includes eTG/AMH/PBS/MBS (100% of recommendations)
  - [ ] Verify resource links work (click → navigate → page loads)
  - [ ] Test complete action: Click "Mark Complete" → Recommendation removed from active list
  - [ ] Test skip action: Click "Skip" → Recommendation removed from active list
  - [ ] Test filters: Filter by priority → Only high/medium/low shown
  - [ ] Mobile test: 375px viewport → UI responsive, no overflow
  - [ ] UAT report: Document 10+ test scenarios, all pass

**Task 3.5: Documentation**
- **Effort**: 1 hour
- **Owner**: Backend Engineer / Technical Writer
- **Deliverable**:
  - API documentation (OpenAPI schema)
  - Code comments (docstrings)
  - README update
- **Dependencies**: All previous tasks
- **Acceptance Criteria**:
  - [ ] OpenAPI docs complete: http://localhost:8000/docs shows all endpoints with examples
  - [ ] Docstrings for all public functions (RecommendationService, WeakAreaAggregator, ResourceValidator)
  - [ ] README section: "Setting Up Claude API Key"
    - Instructions to add "claud" key to Vault
    - Test command: `curl /api/v1/recommendations/generate`
  - [ ] Architecture diagram (optional): Flow chart of generation pipeline
  - [ ] Code review: 0 linting errors, docstrings present

---

### Dependency Graph

```
PHASE 1 (Foundation):
Task 1.1 (Database Migration)
    ↓
Task 1.2 (WeakAreaAggregator) ←───┐
    ↓                              │
Task 1.4 (Unit Tests)              │
    ↓                              │
Task 1.3 (API Skeleton)            │
    ↓                              │
PHASE 2 (Core):                     │
Task 2.1 (Claude Prompt) ──────────┤
    ↓                              │
Task 2.2 (RecommendationService) ──┤
    ↓                              │
Task 2.3 (ResourceValidator)       │
    ↓                              │
Task 2.4 (API Endpoints) ←─────────┘
    ↓
Task 2.5 (Integration Tests)
    ↓
PHASE 3 (Frontend):
Task 3.1 (React Components)
    ↓
Task 3.2 (API Integration)
    ↓
Task 3.3 (Navigation)
    ↓
Task 3.4 (UAT)
    ↓
Task 3.5 (Documentation)
    ↓
COMPLETE
```

---

### Resource Allocation

| Role | Effort (hours) | Tasks |
|------|----------------|-------|
| Backend Engineer | 8-9 hours | 1.1, 1.2, 1.3, 1.4, 2.2, 2.3, 2.4, 2.5, 3.5 |
| AI Engineer | 2 hours | 2.1 (Claude prompt design) |
| Frontend Engineer | 3 hours | 3.1, 3.2, 3.3 |
| QA Engineer | 1 hour | 3.4 (UAT) |
| PM Coordinator | 1 hour | Review, validation gates |
| **TOTAL** | **12-15 hours** | |

---

### Timeline (Example)

| Day | Phase | Tasks | Deliverable |
|-----|-------|-------|-------------|
| Day 1 | Phase 1 | 1.1, 1.2 | Database schema, WeakAreaAggregator implemented |
| Day 2 | Phase 1 | 1.3, 1.4 | API skeleton, unit tests passing |
| Day 3 | Phase 2 | 2.1, 2.2 | Claude prompt designed, RecommendationService working |
| Day 4 | Phase 2 | 2.3, 2.4, 2.5 | Resource validation, API endpoints, integration tests passing |
| Day 5 | Phase 3 | 3.1, 3.2, 3.3, 3.4, 3.5 | Frontend UI complete, UAT passed, documentation done |

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements

- [ ] **Recommendation Generation**: POST /api/v1/recommendations/generate returns 5 recommendations sorted by priority (high → medium → low)
- [ ] **Pattern Detection**: WeakAreaAggregator correctly detects all 4 pattern types (knowledge_gap, skill_gap, documentation_gap, comprehensive_weakness)
- [ ] **Resource Linking**: All recommended resources have validated IDs (no broken links)
- [ ] **Australian Context**: 100% of recommendations include eTG/AMH/PBS/MBS references
- [ ] **Impact Estimation**: estimated_impact values are realistic (0-15 AMC marks, based on gap × specialty weight)
- [ ] **Complete/Skip Actions**: POST /{id}/complete and /{id}/skip correctly update timestamps
- [ ] **Filtering**: GET /{user_id}?status=active|completed|skipped correctly filters recommendations
- [ ] **Rate Limiting**: Users limited to 5 generations per day (429 error on 6th attempt)
- [ ] **Navigation**: ResourceChip onClick navigates to correct OSCE video, MCQ topic, or EMR patient page

#### Quality Requirements

- [ ] **Test Coverage**: ≥70% coverage (unit + integration tests)
- [ ] **Test Pass Rate**: 100% (zero tolerance for failures)
- [ ] **Code Quality**: No linting errors (flake8, pylint, ESLint)
- [ ] **Documentation**: All endpoints documented in OpenAPI schema, all functions have docstrings

#### Performance Requirements

- [ ] **API Generation Time**: <2s p95 (Claude API 3-5s is acceptable)
- [ ] **API Retrieval Time**: <100ms p95 (GET /{user_id})
- [ ] **Database Queries**: <50ms (user_recommendations lookup)
- [ ] **Resource Validation**: <200ms (parallel validation of 15 resources)
- [ ] **Dashboard Load Time**: <2s (full RecommendationsPanel render)

#### Security Requirements

- [ ] **No Hardcoded Credentials**: `grep -r "sk-ant-" backend/` returns 0 matches
- [ ] **Vault Integration**: Claude API key retrieved from Vault with key "claud" (NOT "anthropic")
- [ ] **Input Validation**: All API inputs validated with Pydantic (reject invalid JSON, missing fields)
- [ ] **Authentication**: JWT required on all endpoints (401 if missing/expired)
- [ ] **Authorization**: Users can only access own recommendations (403 if accessing other user's data)
- [ ] **Security Scan**: `bandit -r backend/src/` returns 0 HIGH/CRITICAL issues

#### Australian Medical Compliance

- [ ] **Terminology**: Australian drug names used (paracetamol, salbutamol, adrenaline) - NOT US names
- [ ] **Guidelines**: eTG/AMH/AHPRA references in 100% of recommendations
- [ ] **Standards**: PBS medication codes, MBS item numbers included where relevant
- [ ] **Units**: SI units only (mmol/L, g/L, °C)
- [ ] **No US Resources**: No mentions of UpToDate, Medscape, AMBOSS in recommendations

---

### Testing Requirements

#### Unit Tests (≥70% coverage target)

**File**: `backend/tests/test_services/test_weak_area_aggregator.py`
```python
def test_identify_patterns_knowledge_gap():
    """Test detection of knowledge gap pattern"""
    analytics = {
        "specialty_heatmap": {
            "Neurology": {"mcq": 55, "osce": 58, "emr": 50}
        }
    }
    aggregator = WeakAreaAggregator()
    patterns = aggregator.identify_patterns(user_id, analytics)

    assert len(patterns) == 1
    assert patterns[0]["type"] == "knowledge_gap"
    assert patterns[0]["specialty"] == "Neurology"
    assert patterns[0]["severity"] == "high"

def test_identify_patterns_skill_gap():
    """Test detection of skill gap pattern"""
    analytics = {
        "specialty_heatmap": {
            "Cardiology": {"mcq": 85, "osce": 60, "emr": 70}
        }
    }
    aggregator = WeakAreaAggregator()
    patterns = aggregator.identify_patterns(user_id, analytics)

    assert patterns[0]["type"] == "skill_gap"
    assert patterns[0]["specialty"] == "Cardiology"

def test_severity_ranking():
    """Test patterns sorted by severity: critical > high > medium"""
    analytics = {
        "specialty_heatmap": {
            "Neurology": {"mcq": 50, "osce": 55, "emr": 50},  # comprehensive_weakness (critical)
            "Cardiology": {"mcq": 85, "osce": 60, "emr": 70},  # skill_gap (high)
            "Respiratory": {"mcq": 80, "osce": 75, "emr": 55}  # documentation_gap (medium)
        }
    }
    aggregator = WeakAreaAggregator()
    patterns = aggregator.identify_patterns(user_id, analytics)

    assert patterns[0]["severity"] == "critical"
    assert patterns[1]["severity"] == "high"
    assert patterns[2]["severity"] == "medium"
```

**Minimum Test Cases**:
- [ ] Happy path (normal user with 2-3 weak patterns)
- [ ] Edge case: No weak patterns (all scores >80%)
- [ ] Edge case: All weak (all scores <50%)
- [ ] Error handling: Invalid analytics data (missing specialty_heatmap)
- [ ] Resource validation: Valid IDs pass, invalid IDs filtered

#### Integration Tests

**File**: `backend/tests/test_api/test_recommendations.py`
```python
@pytest.mark.asyncio
async def test_generate_recommendations_flow(client, mock_claude_api):
    """Test full generation flow: analytics → patterns → Claude → validation → save"""
    # Arrange
    user = await create_test_user()
    await create_test_analytics(user.id, overall_score=75.2)

    # Act
    response = await client.post(
        "/api/v1/recommendations/generate",
        headers={"Authorization": f"Bearer {user.jwt}"}
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert len(data["recommendations"]) == 5
    assert all(rec["priority"] in ["high", "medium", "low"] for rec in data["recommendations"])
    assert all(0 <= rec["estimated_impact"] <= 15 for rec in data["recommendations"])
    assert all("australian_context" in rec for rec in data["recommendations"])

@pytest.mark.asyncio
async def test_complete_recommendation(client):
    """Test marking recommendation as completed"""
    # Arrange
    user = await create_test_user()
    rec = await create_test_recommendation(user.id)

    # Act
    response = await client.post(
        f"/api/v1/recommendations/{rec.id}/complete",
        headers={"Authorization": f"Bearer {user.jwt}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["recommendation"]["completed_at"] is not None
```

#### E2E Tests (Playwright)

**File**: `testing/playwright/tests/integration/recommendations.spec.ts`
```typescript
test('Generate and complete recommendation flow', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid=email-input]', 'student@test.com');
    await page.fill('[data-testid=password-input]', 'password123');
    await page.click('[data-testid=login-button]');

    // Navigate to recommendations
    await page.click('[data-testid=nav-recommendations]');
    await expect(page).toHaveURL('/recommendations');

    // Generate recommendations
    await page.click('[data-testid=generate-button]');
    await page.waitForSelector('[data-testid=recommendation-card]');

    // Verify 5 recommendations displayed
    const cards = await page.$$('[data-testid=recommendation-card]');
    expect(cards.length).toBe(5);

    // Click first recommendation's resource
    await page.click('[data-testid=resource-chip-0]');
    await expect(page).toHaveURL(/\/(osce|mcq|emr)\//);

    // Navigate back
    await page.goBack();

    // Mark first recommendation as complete
    await page.click('[data-testid=complete-button-0]');
    await expect(page.locator('[data-testid=recommendation-card]')).toHaveCount(4);

    // Verify completion persists after refresh
    await page.reload();
    await expect(page.locator('[data-testid=recommendation-card]')).toHaveCount(4);
});
```

---

### Documentation Deliverables

#### Code Documentation

- [ ] **API Documentation**: OpenAPI schema complete at http://localhost:8000/docs
  - All 4 endpoints documented
  - Request/response examples included
  - Error codes documented (400, 401, 403, 429, 500)

- [ ] **Function Docstrings**: All public functions documented
  - RecommendationService.generate_recommendations()
  - WeakAreaAggregator.identify_patterns()
  - ResourceValidator.validate_resources()
  - All API endpoint handlers

- [ ] **Inline Comments**: Complex logic explained
  - Pattern detection algorithm (explain thresholds)
  - Impact estimation calculation (explain formula)
  - Claude prompt structure (section purposes)

#### Architecture Documentation

- [ ] **Architecture Decision Record (ADR)**: Why Claude API instead of local models
  - Document Constraint 4.2: Local 7B models cannot handle complexity
  - Evidence: 200 MCQ generation failures
  - Decision: Use claude-sonnet-4-5-20250929 for all complex medical content

- [ ] **Database Schema Diagram**: ER diagram showing user_recommendations relationships
  - user_recommendations → users (foreign key)
  - JSONB resources structure

- [ ] **API Flow Diagram**: Request/response flow for recommendation generation
  - User → API → WeakAreaAggregator → Claude → ResourceValidator → Database → Response

---

### Deployment Checklist

#### Pre-Deployment

- [ ] All tests passing (100% pass rate)
- [ ] Security audit complete (0 HIGH/CRITICAL issues)
- [ ] Performance benchmarks met (generation <2s, retrieval <100ms)
- [ ] Database migration tested in staging: `alembic upgrade head`
- [ ] Rollback plan documented: `alembic downgrade -1`
- [ ] Vault secret "claud" configured in production

#### Deployment

- [ ] Database migration executed: `alembic upgrade head`
- [ ] Environment variables configured (VAULT_ADDR, etc.)
- [ ] Backend deployed to staging
- [ ] Smoke tests in staging pass (generate 1 recommendation)
- [ ] Frontend deployed to staging
- [ ] E2E tests in staging pass
- [ ] Deploy to production (zero-downtime deployment)

#### Post-Deployment

- [ ] Production smoke tests pass (generate 1 recommendation)
- [ ] Monitoring dashboards show healthy metrics (API latency <2s)
- [ ] No error spikes in logs (check CloudWatch/Sentry)
- [ ] Claude API usage within budget (<$10/day)
- [ ] User analytics: Track completion rate (target 50%+ within 7 days)
- [ ] Stakeholders notified (PM, product owner, users)

---

### Success Validation

**This PRD is considered COMPLETE when**:

1. ✅ All acceptance criteria met (100%)
2. ✅ All tests passing (100% pass rate, ≥70% coverage)
3. ✅ Code reviewed and approved (0 linting errors, security scan passed)
4. ✅ Security scan passes (0 HIGH/CRITICAL issues, no hardcoded credentials)
5. ✅ Documentation complete (API docs, docstrings, README)
6. ✅ Production deployment successful (smoke tests pass, no error spikes)
7. ✅ Success metrics trending positive:
   - 80%+ students rate recommendations as "Very Helpful" (in-app survey)
   - 50%+ completion rate within 7 days
   - 5%+ overall score improvement within 2 weeks for active users
   - 70%+ resource click-through rate

**Sign-off Required From**:
- [ ] PM Coordinator (overall quality, success metrics met)
- [ ] Security Expert (security approval, Vault integration verified)
- [ ] Testing QA (test coverage ≥70%, 100% pass rate)
- [ ] Lead Engineer (code review, performance benchmarks met)
- [ ] Medical Content Expert (Australian compliance verified, eTG/AMH references correct)

---

## 📎 Appendices

### Appendix A: API Request/Response Examples

#### POST /api/v1/recommendations/generate

**Request**:
```json
{
    "force_regenerate": false
}
```

**Response** (201 Created):
```json
{
    "status": "success",
    "data": {
        "recommendations": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "recommendation_type": "skill_gap",
                "title": "Practice Cardiology OSCE History Taking",
                "description": "Your MCQ knowledge is excellent (85%) but OSCE performance lags (60%). Focus on translating theory to clinical skills through structured history taking practice.",
                "priority": "high",
                "estimated_impact": 3.5,
                "resources": [
                    {
                        "type": "osce_video",
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "title": "Chest Pain History Taking (Cardiology)",
                        "duration_minutes": 12
                    }
                ],
                "australian_context": "Review eTG Cardiovascular section 3.2 (Acute Coronary Syndrome). Familiarize with PBS aspirin 100mg dispersible (code 1234), GTN sublingual spray (code 5678). Practice MBS ECG item 11700 documentation.",
                "completed_at": null,
                "skipped_at": null,
                "created_at": "2026-02-16T10:00:00Z"
            }
            // ... 4 more recommendations
        ],
        "generation_metadata": {
            "analytics_snapshot": {
                "overall_score": 75.2,
                "mcq_score": 78.5,
                "osce_score": 72.1,
                "emr_score": 70.8
            },
            "patterns_detected": [
                {
                    "type": "skill_gap",
                    "specialty": "Cardiology",
                    "severity": "high"
                }
            ],
            "model_used": "claude-sonnet-4-5-20250929",
            "generation_time_seconds": 4.2
        }
    }
}
```

---

### Appendix B: Error Codes

| Code | Message | Description | User Action |
|------|---------|-------------|-------------|
| E001 | Insufficient analytics data | User has not completed enough MCQ/OSCE/EMR sessions | Complete at least 10 sessions in each module |
| E002 | Claude API timeout | AI service took too long to respond (>10s) | Retry generation after 1 minute |
| E003 | Malformed Claude response | AI returned invalid JSON | Contact support (backend will retry automatically) |
| E004 | Rate limit exceeded | User exceeded 5 generations per day | Wait until tomorrow to generate new recommendations |
| E005 | Recommendation not found | Invalid recommendation ID | Check ID or refresh recommendations list |
| E006 | Unauthorized access | JWT expired or invalid | Re-login to get new token |
| E007 | Access denied | User trying to access another user's recommendations | Can only access own recommendations |

---

### Appendix C: Related PRDs

**Depends On**:
- **PRD_INTEGRATION_002**: Unified Progress Tracking - Provides user_analytics data (overall_score, specialty_heatmap, learning_velocity)
- **PRD_BACKEND_001**: EMR Database Migration - Provides EMR metrics (emr_avg_validation_score, emr_sessions_total)
- **PRD_FRONTEND_003**: EMR Dashboard Integration - Provides UI patterns for analytics display

**Blocks**:
- **PRD_FRONTEND_006**: Advanced Study Planning - Will use recommendation data to build multi-week study schedules
- **PRD_INTEGRATION_004**: Peer Learning Features - Will use recommendation patterns to suggest study groups

**Related**:
- **Constraint 4.2**: LLM Integration - Claude API required for complex medical content generation
- **PRD_BACKEND_002**: EMR Session API - Provides EMR session data for analytics

---

**Document Status**: Draft → Ready for Review → Approved
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: [Pending]
**Version**: 1.0
