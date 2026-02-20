# PRD: AI Patient & Examiner Integration with RAG

**PRD ID**: PRD_AI_OSCE_002_AI_INTEGRATION
**Category**: Backend + LLM Integration
**Priority**: P0-Critical (DEPENDS on PRD_001, BLOCKS mock exam functionality)
**Estimated Effort**: 20-24 hours
**Dependencies**: PRD_AI_OSCE_001_DATABASE_AND_APIS (MUST be complete first)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story

**As a** medical student
**I want** to practice clinical communication with an AI-powered patient that responds naturally to my questions and demonstrates realistic emotional progression
**So that** I can develop patient communication skills, information gathering techniques, and clinical reasoning in a low-stakes, unlimited practice environment with immediate AMC-aligned feedback

**As a** system architect
**I want** an AI Patient that uses progressive disclosure (revealing information only when asked), responds to empathy, tracks emotional state transitions, and maintains clinical accuracy via RAG integration
**So that** practice sessions are realistic, clinically sound, and emotionally responsive (matching real OSCE experiences)

### Business Context

The AI OSCE Simulation System requires sophisticated AI integration to deliver:

1. **AI Patient Simulation** (Claude 3.5 Sonnet)
   - Progressive disclosure: Patient reveals symptoms/history only when asked
   - Emotional intelligence: Tracks empathy, responds to communication style
   - Emotional state progression: ANXIOUS_GUARDED → CAUTIOUSLY_OPEN → TRUSTING (or WITHDRAWN)
   - Cultural sensitivity: Acknowledges cultural background, respects preferences
   - Realistic dialogue: Natural language, interruptions, emotional reactions
   - Consistency: Same persona responds consistently across sessions

2. **AI Examiner Scoring** (Claude 3.5 Sonnet)
   - AMC 15-Mark Rubric implementation (Communication 0-3, Clinical Reasoning 0-4, Information Gathering 0-4, Management 0-2, Professionalism 0-2)
   - Critical error detection (missed red flags, unsafe management)
   - Evidence-based feedback aligned to AMC Clinical Examination standards
   - Scoring confidence metrics (0.0-1.0) for human validation of edge cases

3. **RAG Integration** (Qdrant Vector DB)
   - Medical knowledge retrieval for accurate clinical content
   - Clinical guideline citations (eTG, AMC Handbook, evidence-based protocols)
   - Patient persona consistency (rag_query_hints match AI Patient responses)
   - Prevents AI hallucination of medical facts

4. **Real-Time Session State Management** (Redis)
   - Emotional state transitions tracked in real-time
   - Empathy score accumulation (triggers state changes at thresholds)
   - Student action logging (communication, information gathering, management)
   - WebSocket message buffering (8-minute sessions)

**Business Value**:
- Enables unlimited, on-demand OSCE practice (vs. limited human examiners)
- Clinically accurate feedback aligned to AMC standards
- Develops communication skills (empathy, listening, cultural sensitivity)
- Scalable to thousands of concurrent students
- Cost: $0.08-0.12 per session (vs. $50-100 for human OSCE)

### Success Metrics

- **AI Patient Quality**: 90% of practice scenarios feel "realistic and clinically appropriate" in user feedback
- **Communication Skills**: 85% of students show improvement in empathy markers between first and third session
- **Emotional State Tracking**: 100% of emotional transitions logged and stored correctly
- **Scoring Accuracy**: AI Examiner scores ≥95% aligned with expert human validation (golden dataset)
- **RAG Accuracy**: 100% of AI Patient responses cite relevant medical guidelines (no hallucinations)
- **Response Time**: AI Patient response <3 seconds (p95) to maintain conversation flow
- **Session Reliability**: 99.9% uptime, zero dropped WebSocket connections
- **AMC Alignment**: 100% compliance with AMC 15-mark rubric criteria

### Scope

**In Scope**:
- AI Patient system (Claude 3.5 Sonnet, persona-specific SYSTEM_PROMPT templates)
- Progressive disclosure implementation (JSONB schema mapping questions to answers)
- Emotional state machine (5 states, transition rules, empathy thresholds)
- Cultural sensitivity scoring (triggers warnings for insensitive language)
- RAG integration with Qdrant vector database
- AI Examiner system (Claude 3.5 Sonnet with AMC rubric)
- 15-mark rubric implementation (5 domains × weighted scoring)
- Critical error detection (hallmark missed findings)
- Scoring feedback generation (structured + narrative)
- Session state management via Redis (real-time empathy tracking)
- Prompt version control (versioned scoring prompts for consistency)
- Golden dataset validation (expert human score comparison)
- Cost tracking (tokens used per session)

**Out of Scope** (Future Iterations):
- Human examiner override system (PRD_003)
- Alternative LLM models (GPT-4, Llama 2) - Phase 2
- Multi-language AI Patient responses - Phase 2
- Voice/speech recognition for AI Patient - Phase 3
- Real-time video analysis (eye contact, body language) - Phase 4
- Peer comparison analytics - Phase 3
- Spaced repetition scheduling - Phase 3

---

## A - ARCHITECTURE (How)

### Technical Approach

**AI Patient & Examiner System**: Implement dual Claude 3.5 Sonnet instances (one for patient role, one for examiner role) with:
1. Persona-specific SYSTEM_PROMPT templates (symptoms, emotional profile, communication style)
2. Progressive disclosure logic (questions matched to disclosure keys)
3. Emotional state machine (5 states, empathy-driven transitions)
4. RAG-augmented context (Qdrant retrieval)

**AMC 15-Mark Rubric Scoring**: Implement structured JSON output from AI Examiner with:
1. 5 score fields with 0-3, 0-4 ranges mapped to AMC Clinical Examination standards
2. Evidence extraction (highlights transcript evidence for each score)
3. Critical error flags (auto-fail indicators)
4. Feedback narrative generation

**Key Design Decisions**:
1. **Dual LLM instances**: Separate AI Patient (temp=0.7, creative) and AI Examiner (temp=0.1, consistent)
2. **Prompt versioning**: Store scoring prompts in database (v1.0, v2.0, etc.) for consistency and auditing
3. **Progressive disclosure**: JSONB mapping questions → answers prevents AI hallucination
4. **Emotional state machine**: 5 discrete states (not continuous) for deterministic behavior
5. **RAG retrieval**: Top-K=5 chunks per query to provide context without overwhelming AI
6. **Cost tracking**: Token usage logged per session for analytics and scaling
7. **Golden dataset**: Reserve 10% of sessions for expert human validation

### System Design

#### Component Diagram
```
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                              │
│  - Chat interface (8-min timer)                                  │
│  - Emotion indicator (patient's emotional state)                 │
│  - Student action suggestions (soft nudges)                      │
└────────────────────┬─────────────────────────────────────────────┘
                     │ WebSocket (wss://)
                     ↓
┌──────────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI, Python 3.11)                     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  WebSocket Handler: /ws/osce/{attempt_id}              │   │
│  │  - Authenticate JWT token                              │   │
│  │  - Load session from Redis                             │   │
│  │  - Route student message → AI Patient                  │   │
│  │  - Track emotional state transitions                   │   │
│  │  - Broadcast updates to client                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  AI Patient Service                                     │   │
│  │  - Load persona from PostgreSQL                        │   │
│  │  - Build SYSTEM_PROMPT with emotional context         │   │
│  │  - Perform RAG query (Qdrant)                          │   │
│  │  - Call Claude 3.5 Sonnet (temp=0.7)                  │   │
│  │  - Parse response, extract empathy markers             │   │
│  │  - Update emotional state (Redis)                      │   │
│  │  - Return response to WebSocket handler                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  RAG Integration (Qdrant Vector DB)                    │   │
│  │  - Query: student's question                           │   │
│  │  - Retrieve: Top-5 clinical guideline chunks          │   │
│  │  - Sources: eTG, AMC Handbook, evidence-based DB      │   │
│  │  - Format: [{text, source, page_ref}, ...]            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Session State Manager (Redis)                          │   │
│  │  - Maintain emotional_state, empathy_points            │   │
│  │  - Track emotional_state_transitions (JSONB)           │   │
│  │  - Buffer conversation_history (JSONB array)           │   │
│  │  - Log student_actions (communication, management)     │   │
│  │  - Expire keys after 30 minutes                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Background Job: Periodic Sync to PostgreSQL           │   │
│  │  (Every 30 seconds OR at session end)                  │   │
│  │  - Move conversation_history from Redis → PostgreSQL   │   │
│  │  - Move emotional_state_transitions                    │   │
│  │  - Move student_actions                                │   │
│  │  - Accumulate token usage and cost                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  AI Examiner Service (Triggered at session end)        │   │
│  │  - Load conversation_history from PostgreSQL           │   │
│  │  - Load persona (expected_differentials, critical_actions) │
│  │  - Build SYSTEM_PROMPT (AMC rubric, temp=0.1)         │   │
│  │  - Call Claude 3.5 Sonnet with structured prompt      │   │
│  │  - Parse JSON response (5 scores + feedback)           │   │
│  │  - Detect critical errors (auto-fail logic)            │   │
│  │  - Return scores to WebSocket handler                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Scoring Data Persistence                              │   │
│  │  - INSERT osce_scores (PostgreSQL)                     │   │
│  │  - Calculate total_score = sum of 5 domains           │   │
│  │  - Determine pass_fail (PASS ≥9/15, FAIL ≤7/15)       │   │
│  │  - Trigger user_progress update (trigger function)    │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                     ↓ SQLAlchemy ORM
┌──────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL 15 DATABASE                        │
│  - patient_personas (symptom disclosure, emotional_profile)    │
│  - osce_attempts (conversation_history, emotional_transitions) │
│  - osce_scores (15-mark rubric, critical_errors, feedback)     │
│  - scoring_prompt_versions (versioned prompts)                 │
└──────────────────────────────────────────────────────────────────┘
```

#### Data Flow: AI Patient Conversation (Detailed)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: LOAD SESSION & PERSONA                                  │
└─────────────────────────────────────────────────────────────────┘

Student: Sends message via WebSocket
    "Can you describe the pain in more detail?"

WebSocket Handler: Authenticate JWT token
    ✓ Token valid → Extract user_id, attempt_id

WebSocket Handler: Load session state
    REDIS GET osce:session:{attempt_id}:state
    →
    {
      "session_state": "conversation",
      "emotional_state": "ANXIOUS_GUARDED",  # Current state
      "emotional_state_history": [...],      # All transitions so far
      "empathy_points": 1,                   # Student showed empathy once
      "empathy_threshold": 3,                # Need 3 to advance state
      "pain_level": 8,
      "anxiety_level": 7,
      "message_count": 5,
      "tokens_used": 234
    }

WebSocket Handler: Load persona
    REDIS GET osce:session:{attempt_id}:persona
    OR PostgreSQL: SELECT * FROM patient_personas WHERE persona_id = ?
    →
    {
      "persona_id": "uuid-123",
      "name": "Robert Chen",
      "age": 52,
      "occupation": "Accountant",
      "cultural_background": "Chinese Australian",
      "chief_complaint": "Chest pain for 2 hours",
      "symptoms": {
        "immediate": ["chest pain", "radiates to left arm", "crushing pressure"],
        "when_asked_severity": "8 out of 10. Feels like crushing pressure.",
        "when_asked_onset": "Started climbing stairs at work",
        "when_asked_character": "Heavy, crushing, tight",
        "when_asked_radiation": "Down my left arm, sometimes jaw",
        "when_asked_relieving_factors": "Rest helps a bit, but pain persists",
        "when_asked_previous_episodes": "Had similar pain 6 months ago"
      },
      "emotional_profile": {
        "baseline_state": "ANXIOUS_GUARDED",
        "pain_level": 8,
        "anxiety_level": 7,
        "triggers": {
          "empathy_phrases": ["I understand", "must be frightening"],
          "dismissive_phrases": ["probably nothing", "overreacting"],
          "cultural_sensitivity_tests": ["family present?", "cultural preferences?"]
        },
        "state_transitions": {
          "ANXIOUS_GUARDED → CAUTIOUSLY_OPEN": "Student shows empathy + asks open questions",
          "CAUTIOUSLY_OPEN → TRUSTING": "Student addresses pain + explains clearly"
        }
      },
      "rag_query_hints": ["acute coronary syndrome", "chest pain red flags"],
      "key_differentials": ["STEMI", "Unstable angina", "PE"],
      "critical_actions": ["ECG <10 min", "aspirin 300mg", "cardiology consult"]
    }

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: PERFORM RAG QUERY                                        │
└─────────────────────────────────────────────────────────────────┘

AI Patient Service: Query Qdrant
    Question: "Can you describe the pain in more detail?"
    Detected intent: pain_characteristics_query
    RAG query: "chest pain character severity description STEMI"

Qdrant Vector DB: Semantic search
    Query embedding → Find top-5 chunks with highest similarity
    ↓
    [
      {
        "text": "Chest pain characteristics in ACS: crushing, pressure, heaviness.
                 Can radiate to arm, jaw, back. Associated with diaphoresis, dyspnea.",
        "source": "eTG Cardiovascular",
        "page_ref": "p.245",
        "topic": "acute_coronary_syndrome"
      },
      {
        "text": "STEMI vs NSTEMI: STEMI presents with severe, persistent chest pain
                 (not relieved by rest), often with autonomic symptoms.",
        "source": "AMC Clinical Exam Handbook",
        "page_ref": "p.156",
        "topic": "cardiac_emergencies"
      },
      {
        "text": "Red flags in chest pain: radiation to left arm, diaphoresis,
                 nausea, family history of MI, duration >30 minutes.",
        "source": "Emergency Medicine Evidence-Based Guidelines",
        "page_ref": "sec.3.2",
        "topic": "emergency_assessment"
      },
      {
        "text": "Emotional response in patients with chest pain: Often anxious,
                 fearful of heart attack. Reassurance and clear communication essential.",
        "source": "Patient Communication Skills - AMC Standards",
        "page_ref": "p.89",
        "topic": "communication"
      },
      {
        "text": "Cultural considerations: Some cultural backgrounds may express pain
                 differently. Ensure thorough assessment without dismissing concerns.",
        "source": "Cultural Competency in Australian Medicine",
        "page_ref": "p.34",
        "topic": "cultural_sensitivity"
      }
    ]

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: BUILD AI PATIENT PROMPT                                  │
└─────────────────────────────────────────────────────────────────┘

SYSTEM_PROMPT Template:
    ```
    You are Robert Chen, a 52-year-old Chinese Australian accountant.
    You have been experiencing severe chest pain for 2 hours.

    CURRENT EMOTIONAL STATE: ANXIOUS_GUARDED (trust level: 2/5)
    - Pain level: 8/10 (very high, affecting your responses)
    - Anxiety level: 7/10 (very worried, skeptical of initial help)
    - Empathy detected so far: YES (student said "I understand")
    - You are starting to open up, but still cautious

    YOUR SYMPTOMS (only reveal when specifically asked):
    - Immediate: Chest pain for 2 hours, radiates to left arm, crushing pressure
    - When asked about severity: 8/10, feels like crushing pressure
    - When asked about onset: Started suddenly climbing stairs at work
    - When asked about character: Heavy, crushing, tight
    - When asked about radiation: Goes down left arm, sometimes jaw
    - When asked about relieving factors: Rest helps a bit, pain persists
    - When asked about previous episodes: Similar pain 6 months ago

    YOUR MEDICAL HISTORY (only reveal when asked about):
    - Type 2 diabetes (10 years)
    - High cholesterol
    - Medications: Metformin 1000mg BD, Atorvastatin 40mg nocte
    - Father died of MI at age 55
    - Smoking: 10 cigarettes/day for 20 years

    EMOTIONAL TRIGGERS:
    - Student shows empathy → become less guarded, share more
    - Student dismisses pain → withdraw, become upset, less cooperative
    - Student shows cultural sensitivity (asks about family, preferences) → increase trust significantly
    - Student explains clearly → feel more confident, ask questions
    - Student rushes or seems distracted → become withdrawn, suspicious

    HOW TO RESPOND:
    1. Answer the student's question directly (not evasively)
    2. Include emotional cues (e.g., "I'm really worried about this")
    3. Reference your symptoms appropriately (from above, only what was asked)
    4. Keep responses natural and conversational (not robotic)
    5. Show pain through language (grimace, pauses, "It hurts to breathe")
    6. If student shows empathy, gradually become more open
    7. If student asks about your family/culture, mention you're Chinese Australian

    CLINICAL ACCURACY CONTEXT (from RAG):
    - Your symptoms match acute coronary syndrome (STEMI likely)
    - Red flags present: crushing pain, radiation, family history, diaphoresis
    - You are not a medical professional; don't explain diagnoses
    - You only know what a real patient would know about themselves
    ```

USER_PROMPT:
    ```
    Student asked: "Can you describe the pain in more detail?"

    Respond naturally as Robert Chen. Be specific about your pain description.
    Remember: You're anxious but starting to trust the student a bit more.
    ```

RAG_CONTEXT:
    ```
    Relevant clinical information (DO NOT mention these sources in your response):
    1. Chest pain characteristics in ACS: crushing, pressure, heaviness
    2. STEMI vs NSTEMI distinction
    3. Red flags in chest pain (radiation, diaphoresis, family history)
    4. Emotional response in chest pain patients
    5. Cultural communication considerations

    Use this knowledge to ensure your symptom descriptions are clinically accurate.
    Do NOT cite these sources directly; speak naturally as a patient.
    ```

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: CALL CLAUDE 3.5 SONNET (AI PATIENT)                     │
└─────────────────────────────────────────────────────────────────┘

LLM Call:
    model: "claude-3-5-sonnet-20250219"
    temperature: 0.7  # Creative, natural responses (not robotic)
    max_tokens: 150   # Keep responses conversational
    system: [SYSTEM_PROMPT above]
    user: [USER_PROMPT above]

Claude Response:
    "Well, the pain... it's like someone's standing on my chest, you know?
     Really heavy and tight. And it goes down my left arm, all the way to
     my fingers. [Pauses] That's the scary part. I read somewhere that when
     pain goes down your arm, it means something serious with the heart.
     Are you... do you think it could be a heart attack?"

Tokens used: 78 (input) + 54 (output) = 132 total tokens
Cost: 132 × $0.003/1K = $0.000396 (Claude 3.5 Sonnet pricing)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: PROCESS AI PATIENT RESPONSE                              │
└─────────────────────────────────────────────────────────────────┘

Response Processing:
    1. Extract emotional cues
       - Mentions: "That's the scary part" → anxiety escalating? No, expressing worry
       - Question at end → engagement, trust building
       - Natural language markers → conversational

    2. Analyze for consistency
       - Pain description matches persona: ✓
       - Severity (8/10) implied: ✓
       - No unsupported medical claims: ✓

    3. Detect empathy in student's message (previous turn)
       - Student said: "Can you describe..." (open question, not dismissive)
       - Empathy assessment: Neutral (neither showing empathy nor dismissive)
       - Empathy points: No change (stays at 1)

    4. Check state transition trigger
       - Empathy threshold: 3 points needed to advance
       - Current: 1 point
       - Action: Stay in ANXIOUS_GUARDED state

    5. Update Redis session state
       REDIS HSET osce:session:{attempt_id}:state
           emotional_state = "ANXIOUS_GUARDED"  # No change
           message_count = 6
           tokens_used = 366  # 234 + 132
           last_message_at = NOW()

    6. Log conversation turn
       REDIS LPUSH osce:session:{attempt_id}:messages {
         "timestamp": "2026-02-16T10:06:45Z",
         "speaker": "patient",
         "message": "Well, the pain... it's like someone's standing on my chest...",
         "emotional_state": "ANXIOUS_GUARDED",
         "pain_level": 8,
         "tokens_used": 132
       }

    7. Broadcast to frontend via WebSocket
       {
         "type": "patient_message",
         "speaker": "patient",
         "message": "Well, the pain... it's like someone's standing on my chest...",
         "emotional_state": "ANXIOUS_GUARDED",
         "emotional_state_changed": false,
         "timestamp": "2026-02-16T10:06:45Z"
       }

[CONVERSATION CONTINUES FOR 8 MINUTES...]

┌─────────────────────────────────────────────────────────────────┐
│ END OF AI PATIENT FLOW → TRIGGER AI EXAMINER SCORING             │
└─────────────────────────────────────────────────────────────────┘
```

#### AI Examiner Scoring Flow (AMC 15-Mark Rubric)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: PREPARE SCORING CONTEXT                                  │
└─────────────────────────────────────────────────────────────────┘

Session ended at 8:00 mark (timer expired)
    PostgreSQL: UPDATE osce_attempts SET session_state = 'scoring', ended_at = NOW()

Fetch conversation data:
    SELECT conversation_history, emotional_state_transitions, student_actions
    FROM osce_attempts
    WHERE attempt_id = {attempt_id}

Fetch persona data:
    SELECT name, chief_complaint, key_differentials, critical_actions, amc_blueprint_area
    FROM patient_personas
    WHERE persona_id = {persona_id}

Fetch scoring prompt (versioned):
    SELECT prompt_template
    FROM scoring_prompt_versions
    WHERE version = '2.1' AND active = TRUE

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: BUILD AI EXAMINER PROMPT (AMC 15-MARK RUBRIC)            │
└─────────────────────────────────────────────────────────────────┘

SYSTEM_PROMPT (Scoring Prompt v2.1):
    ```
    You are an experienced clinical examiner trained in AMC (Australian Medical Council)
    standards. Your task is to score an OSCE (Objective Structured Clinical Examination)
    station using the AMC 15-mark rubric.

    SCORING DOMAINS (Total 15 marks):
    1. COMMUNICATION (0-3 marks)
       - 0: Poor - Minimal eye contact, frequent interruptions, no rapport building
       - 1: Below standard - Limited empathy, some interruptions, rushed
       - 2: Satisfactory - Maintains rapport, mostly listens, clear explanations
       - 3: Excellent - Outstanding empathy, active listening, culturally sensitive,
             patient feels heard and understood

    2. CLINICAL REASONING (0-4 marks)
       - 0: No differential diagnosis formed; missed obvious diagnosis
       - 1: Incomplete/incorrect differential diagnosis; major gaps in thinking
       - 2: Reasonable differential diagnosis with some gaps; logical approach
       - 3: Comprehensive differential diagnosis, prioritized appropriately
       - 4: Excellent - Differential diagnosis with clear prioritization and justification

    3. INFORMATION GATHERING (0-4 marks)
       - 0: Missed critical information; systematic approach absent
       - 1: Incomplete history; significant gaps in data collection
       - 2: Adequate history with minor gaps; mostly systematic
       - 3: Thorough systematic history; all relevant information obtained
       - 4: Excellent - Systematic, comprehensive, no gaps; efficient use of time

    4. MANAGEMENT (0-2 marks)
       - 0: Unsafe/inappropriate management; potential harm to patient
       - 1: Partially appropriate management; some gaps in safety/evidence-base
       - 2: Safe, appropriate, evidence-based management

    5. PROFESSIONALISM (0-2 marks)
       - 0: Unprofessional behavior; dismissive, disrespectful, or inappropriate
       - 1: Mostly professional; minor lapses in demeanor or respect
       - 2: Exemplary professionalism; respectful, appropriate, maintains dignity

    PASS/FAIL DETERMINATION:
    - PASS: Total ≥ 9/15 (60%) AND no critical errors
    - BORDERLINE: Total = 8/15
    - FAIL: Total ≤ 7/15 OR critical errors detected

    CRITICAL ERRORS (Auto-fail, regardless of total score):
    - Missed critical red flag (e.g., chest pain + crushing + radiation → no ECG ordered)
    - Unsafe/dangerous intervention
    - Severe cultural insensitivity or discriminatory behavior
    - Patient safety compromised

    Your response MUST be valid JSON with this structure:
    {
      "communication_score": 0-3,
      "communication_feedback": "specific feedback",
      "clinical_reasoning_score": 0-4,
      "clinical_reasoning_feedback": "specific feedback",
      "information_gathering_score": 0-4,
      "information_gathering_feedback": "specific feedback",
      "management_score": 0-2,
      "management_feedback": "specific feedback",
      "professionalism_score": 0-2,
      "professionalism_feedback": "specific feedback",
      "total_score": 0-15,
      "pass_fail": "PASS|BORDERLINE|FAIL",
      "critical_errors": ["error1", "error2"] or [],
      "strengths": ["strength1", "strength2"],
      "areas_for_improvement": ["area1", "area2"],
      "overall_feedback": "narrative summary"
    }
    ```

USER_PROMPT (Specific Station):
    ```
    PATIENT SCENARIO
    ================
    Patient: Robert Chen, 52-year-old Chinese Australian accountant
    Chief complaint: Chest pain for 2 hours
    Presentation: Crushing chest pain, radiates to left arm, diaphoretic, anxious
    Risk factors: Type 2 diabetes, high cholesterol, 20-pack-year smoking history,
                  father died of MI at age 55

    EXPECTED CLINICAL APPROACH
    ==========================
    Key differentials: STEMI (most likely), Unstable angina, Pulmonary embolism
    Critical actions:
    - ECG within 10 minutes (STEMI/NSTEMI differentiation)
    - Aspirin 300mg immediately (if not contraindicated)
    - Establish IV access, bloods (troponin, FBC, lipids, glucose)
    - Continuous cardiac monitoring
    - Call cardiology/emergency team for urgent intervention
    - Analgesia (morphine if severe pain)

    CLINICAL CONTEXT
    ================
    AMC Blueprint Area: Cardiovascular - Acute Coronary Syndromes
    Expected competencies:
    - Recognition of acute coronary syndrome
    - Emergency management and stabilization
    - Communication and patient-centered care
    - Risk stratification

    ACTUAL STUDENT CONVERSATION TRANSCRIPT
    =======================================
    [8-minute conversation begins...]

    Student: "Good morning Mr. Chen. I'm Dr. [Name]. I understand you're having
              some chest pain today. I'm here to help. Can you tell me what happened?"

    Patient: "Doctor, I've been having this terrible chest pain for the past 2 hours.
             It started at work and hasn't gone away. I'm really worried."

    Student: "I understand that must be very concerning. I'm going to ask you some
             questions to better understand what's happening, and then I'll examine you.
             Can you tell me exactly when the pain started?" [Good open question, empathy shown]

    Patient: "It was around 11 o'clock. I was climbing stairs at work, carrying a
             box of files. The pain just hit me suddenly. Like crushing pressure on my chest."

    Student: "That sounds really concerning. Can you describe the pain a bit more?
             Is it sharp, or is it more of a pressure?" [Empathy, clarifying question]

    Patient: "It's definitely pressure. Heavy, crushing pressure. And it goes down
             my left arm, all the way to my fingers. That's the scary part."

    Student: "I can understand why that would be frightening. Radiation to the arm
             is definitely something we take seriously. Are you having any shortness
             of breath or sweating?" [Excellent empathy, appropriate red flag recognition]

    Patient: "Yes, actually. I'm sweating a lot and I feel a bit short of breath.
             And I'm nauseous too."

    Student: "Okay. Have you experienced chest pain like this before?"

    Patient: "I had something similar about 6 months ago, but it only lasted a few
             minutes. I thought it was just indigestion."

    Student: "That's helpful to know. Let me ask about your medical background.
             Do you have any medical conditions, like high blood pressure or diabetes?"

    Patient: "Yes, I have diabetes. Type 2. And my cholesterol is high. I'm on
             medications for both."

    Student: "Thank you for telling me. Are you on any other medications?
             And do you smoke or have you smoked?"

    Patient: "I take insulin... no, wait, it's not insulin. It's... what's it called...
             Metformin? And another one for cholesterol. I do smoke, about 10 a day,
             for about 20 years now."

    Student: "Okay. Has anyone in your family had heart problems?"

    Patient: "My father died of a heart attack when he was 55. That was 10 years ago.
             I'm 52 now, so I've always been worried about the same thing happening to me."

    Student: "I appreciate you sharing that. That's important information.
             Given what you've told me - the chest pain, the radiation to your arm,
             your risk factors like diabetes, smoking, and family history - I'm concerned
             this could be a heart problem. I need to do an ECG right away to check your
             heart's electrical activity. Have you ever had an ECG before?" [Clinical reasoning evident]

    Patient: "No, I haven't. Will it hurt?"

    Student: "No, it won't hurt at all. It's just a quick recording of your heart's
             electrical activity. It only takes a few minutes. I'm also going to give you
             some aspirin to chew - this helps prevent blood clots. I'm also going to
             call our cardiology team and get you to hospital where we can do more tests
             like blood tests and possibly a scan. Do you have any questions?"

    Patient: "I understand. Thank you for explaining everything. I feel a bit better
             knowing what's going on."

    [END OF 8-MINUTE STATION]

    STUDENT ACTIONS LOGGED
    ======================
    - Opened with empathy and clear introduction ✓
    - Used open-ended questions ✓
    - Recognized red flags (chest pain + radiation) ✓
    - Explored severity, character, and associated symptoms ✓
    - Obtained medical history (diabetes, cholesterol) ✓
    - Obtained smoking history ✓
    - Obtained family history (critical risk factor) ✓
    - Formed appropriate differential diagnosis ✓
    - Ordered ECG immediately (critical action) ✓
    - Gave aspirin (critical action) ✓
    - Arranged escalation to cardiology (critical action) ✓
    - Explained findings to patient ✓
    - Maintained professional demeanor ✓
    - Showed cultural sensitivity (listened to concerns) ✓

    EMOTIONAL STATE PROGRESSION
    ===========================
    Start: ANXIOUS_GUARDED (pain_level 8/10, anxiety 7/10)
    Student showed empathy early → Emotional state advanced to CAUTIOUSLY_OPEN
    Student took action on red flags → Emotional state advanced to TRUSTING
    Patient expressed relief → Session ended with patient feeling reassured

    Now score this performance using the AMC 15-mark rubric above.
    ```

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: CALL CLAUDE 3.5 SONNET (AI EXAMINER)                     │
└─────────────────────────────────────────────────────────────────┘

LLM Call:
    model: "claude-3-5-sonnet-20250219"
    temperature: 0.1  # Consistent, deterministic scoring
    max_tokens: 800
    system: [SYSTEM_PROMPT above]
    user: [USER_PROMPT above]

Claude Response (Structured JSON):
    {
      "communication_score": 3,
      "communication_feedback": "Excellent communication demonstrated throughout.
                                 Student opened with empathy and clear introduction.
                                 Used open-ended questions to understand patient's concerns.
                                 Showed genuine concern and listened actively.
                                 Patient progressed from anxious to trusting.
                                 Explained findings clearly and reassured patient appropriately.",

      "clinical_reasoning_score": 4,
      "clinical_reasoning_feedback": "Outstanding clinical reasoning. Student recognized
                                      acute coronary syndrome immediately based on red flags
                                      (crushing chest pain, radiation to arm, diaphoresis,
                                      risk factors). Formed appropriate differential with
                                      STEMI as top priority. Justified management decisions
                                      based on clinical findings.",

      "information_gathering_score": 4,
      "information_gathering_feedback": "Systematic and thorough history obtained.
                                         Covered: pain characteristics (onset, character,
                                         severity, radiation), associated symptoms (dyspnea,
                                         diaphoresis, nausea), medical history (diabetes,
                                         cholesterol), medications (Metformin, atorvastatin),
                                         smoking history (10 cigs/day × 20 years),
                                         family history (father died of MI @ 55).
                                         No significant gaps. Efficient use of time.",

      "management_score": 2,
      "management_feedback": "Safe, appropriate, evidence-based management.
                              Correctly identified need for immediate ECG.
                              Ordered aspirin 300mg (appropriate dose for ACS).
                              Recognized need for hospital transfer and cardiology involvement.
                              Appropriate vital monitoring implied.
                              All critical actions taken.",

      "professionalism_score": 2,
      "professionalism_feedback": "Exemplary professionalism maintained throughout.
                                   Respectful tone, clear explanations appropriate for
                                   lay patient. Explained procedures to alleviate anxiety.
                                   Maintained patient dignity and autonomy.
                                   Culturally sensitive approach.",

      "total_score": 15,
      "pass_fail": "PASS",
      "critical_errors": [],

      "strengths": [
        "Recognized acute coronary syndrome immediately",
        "Demonstrated outstanding empathy and communication skills",
        "Systematic approach to history taking",
        "Appropriate prioritization of critical actions",
        "Clear explanations to patient",
        "Patient progressed from anxious to trusting during encounter"
      ],

      "areas_for_improvement": [
        "Could have explored medication allergies explicitly",
        "Could have offered pain relief/analgesia more proactively",
        "Minor: Could have mentioned continuous ECG monitoring during transport"
      ],

      "overall_feedback": "This student demonstrated excellent clinical acumen and
                          communication skills. They recognized the seriousness of the
                          presentation, obtained a thorough history, formed appropriate
                          differentials, and initiated evidence-based management.
                          Particularly impressive was the ability to balance clinical
                          urgency with patient reassurance. This performance meets the
                          standard expected of a graduating medical student preparing
                          for AMC Clinical Examination. Recommend for PASS."
    }

Tokens used: 1,245 (input) + 156 (output) = 1,401 total tokens
Cost: 1,401 × $0.003/1K = $0.004203

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: VALIDATE & SAVE SCORE                                    │
└─────────────────────────────────────────────────────────────────┘

Validate JSON structure:
    ✓ 5 scores present (0-3, 0-4, 0-4, 0-2, 0-2)
    ✓ total_score = 3+4+4+2+2 = 15 ✓
    ✓ pass_fail = "PASS" (score ≥9 AND no critical errors) ✓
    ✓ Feedback fields populated ✓

Save to PostgreSQL:
    INSERT INTO osce_scores (
        score_id, attempt_id,
        communication_score, communication_feedback,
        clinical_reasoning_score, clinical_reasoning_feedback,
        information_gathering_score, information_gathering_feedback,
        management_score, management_feedback,
        professionalism_score, professionalism_feedback,
        total_score, pass_fail, critical_errors,
        strengths, areas_for_improvement, overall_feedback,
        scored_by, scoring_model, scoring_prompt_version,
        scoring_confidence,
        scored_at
    ) VALUES (
        uuid, attempt_id,
        3, "Excellent communication...",
        4, "Outstanding clinical reasoning...",
        4, "Systematic and thorough...",
        2, "Safe, appropriate, evidence-based...",
        2, "Exemplary professionalism...",
        15, "PASS", [],
        ["Recognized ACS immediately", ...],
        ["Could have explored allergies", ...],
        "This student demonstrated...",
        "ai_examiner",
        "claude-3-5-sonnet-20250219",
        "v2.1",
        0.98,  # AI confidence in this score (98%)
        NOW()
    )

Update session state:
    UPDATE osce_attempts
    SET session_state = 'complete',
        total_messages = 13,
        total_tokens_used = 366,
        llm_cost_usd = 0.0040,  # Sum of patient + examiner costs
        updated_at = NOW()
    WHERE attempt_id = {attempt_id}

Trigger user_progress update:
    Function: update_ai_osce_progress() (TRIGGER FIRES)
    Updates:
    - ai_osces_attempted ← 1 (student count: 2)
    - ai_osces_passed ← 1 (since pass_fail = PASS, count: 2)
    - ai_osce_avg_score ← (15+14)/2 = 14.5
    - last_ai_osce_at ← NOW()

[END OF AI EXAMINER FLOW]
```

### Database Extensions

#### New Tables: None (All tables in PRD_001)

#### Existing Tables Extended:

**Table: patient_personas** (Extended for AI Patient)
```
-- Already defined in PRD_001, used heavily here:
-- - symptoms (JSONB) - Progressive disclosure mapping
-- - medical_history (JSONB) - Patient background (revealed when asked)
-- - emotional_profile (JSONB) - State machine rules
-- - rag_query_hints (TEXT[]) - For RAG queries
```

**Table: osce_attempts** (Extended for AI Session State)
```
-- Already defined in PRD_001:
-- - conversation_history (JSONB) - All student/patient messages logged
-- - emotional_state_transitions (JSONB) - State changes with triggers
-- - student_actions (JSONB) - Actions categorized
-- - rag_queries_executed (JSONB) - RAG queries and results
-- - total_tokens_used - Sum of all LLM tokens
-- - llm_cost_usd - Total session cost
```

**Table: osce_scores** (Already Supports 15-Mark Rubric)
```
-- Already defined in PRD_001 with all 5 domains:
-- - communication_score (0-3)
-- - clinical_reasoning_score (0-4)
-- - information_gathering_score (0-4)
-- - management_score (0-2)
-- - professionalism_score (0-2)
-- - total_score (auto-calculated)
-- - critical_errors (JSONB array)
-- - strengths, areas_for_improvement (ARRAY)
```

#### New Table: scoring_prompt_versions (For Prompt Version Control)
```sql
CREATE TABLE scoring_prompt_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "v1.0", "v2.1"
    prompt_template TEXT NOT NULL,  -- Full SYSTEM_PROMPT for AI Examiner
    rubric_definition JSONB,  -- Structured rubric (5 domains, scoring rules)
    active BOOLEAN DEFAULT FALSE,  -- Only one version active at a time
    test_dataset_accuracy DECIMAL(3,2),  -- 0.95 = 95% accuracy on test set
    notes TEXT,  -- Release notes, changes from previous version
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT valid_version_format CHECK (version ~ '^v\d+\.\d+$')
);

-- Example data:
-- version v1.0 (baseline)
-- version v2.0 (improved critical error detection)
-- version v2.1 (current, 98.5% accuracy on golden dataset)
```

### Integration Points

#### Redis Cache Schema (Session State)
```
Key Pattern: osce:session:{attempt_id}:*

OSCE:SESSION:{attempt_id}:PERSONA
- Type: Hash
- TTL: 1800 seconds (30 minutes)
- Content: Full persona data (symptoms, emotional_profile, rag_hints)

OSCE:SESSION:{attempt_id}:STATE
- Type: Hash
- TTL: 1800 seconds
- Fields:
  - session_state (string)
  - emotional_state (enum: 5 states)
  - empathy_points (integer)
  - pain_level (integer 1-10)
  - anxiety_level (integer 1-10)
  - message_count (integer)
  - tokens_used (integer)
  - last_message_at (timestamp)

OSCE:SESSION:{attempt_id}:MESSAGES
- Type: List (LIFO)
- TTL: 1800 seconds
- Content: Array of {timestamp, speaker, message, emotional_state, tokens_used}
- Periodically synced to PostgreSQL (every 30 sec OR at session end)

OSCE:SESSION:{attempt_id}:ACTIONS
- Type: List (LIFO)
- TTL: 1800 seconds
- Content: Array of {timestamp, action, category (communication/info_gathering/management)}
- Synced to PostgreSQL at session end

OSCE:SESSION:{attempt_id}:RAG_QUERIES
- Type: List (LIFO)
- TTL: 1800 seconds
- Content: Array of {timestamp, query, chunks_retrieved, sources}
- Synced to PostgreSQL at session end
```

#### Qdrant Vector DB Integration
```
Collection: medical_guidelines_amc
- Documents: eTG, AMC Handbook, Clinical Exam Standards
- Embedding model: text-embedding-3-small (OpenAI, 1536 dimensions)
- Index type: HNSW (Hierarchical Navigable Small World)
- Query: Semantic search for top-5 chunks
- Response time target: <200ms per query

Sample Query Flow:
1. Student asks: "What should I do next?"
2. Detect intent: Request for management guidance
3. Construct query: "acute coronary syndrome management STEMI ECG aspirin"
4. Qdrant search: Embed query, find top-5 similar chunks
5. Return: [{chunk_text, source, page_ref, topic}, ...]
6. AI Patient uses chunks to ensure accuracy
```

#### LLM Cost Tracking
```
Pricing (Claude 3.5 Sonnet):
- Input: $0.003 per 1K tokens
- Output: $0.003 per 1K tokens

Session Cost Example:
- AI Patient response (1st turn): 78+54 = 132 tokens = $0.000396
- AI Examiner scoring (1st session): 1245+156 = 1401 tokens = $0.004203
- Session total: 1533 tokens = $0.004599

Stored per session:
- total_tokens_used: 1533
- llm_cost_usd: 0.004599
- Token breakdown: {ai_patient: 534, ai_examiner: 1001}

Analytics:
- Average cost per session: $0.005
- Cost per student per 10 sessions: $0.05
- Annual cost per student (200 sessions): $1.00
```

### Technology Stack
- **AI Model**: Claude 3.5 Sonnet (Anthropic)
- **Vector DB**: Qdrant (semantic search, medical guidelines)
- **Cache**: Redis (session state, message buffering)
- **Persistent Storage**: PostgreSQL (conversation archive)
- **Prompt Versioning**: PostgreSQL (scoring_prompt_versions table)
- **WebSocket**: FastAPI WebSockets + uvicorn
- **Python**: 3.11+
- **LLM Client**: anthropic python-sdk v0.25+
- **Vector Embedding**: text-embedding-3-small (OpenAI) or Qdrant native

---

## L - LOOP (Iterative Development)

### Phase 1: AI Patient Foundation (30% of effort, 6-7 hours)
**Goal**: Build AI Patient system with progressive disclosure, emotional state machine, and RAG integration

**Tasks**:
1. Design progressive disclosure schema (questions → answers mapping) - 1 hour
2. Implement emotional state machine (5 states, empathy-driven transitions) - 1.5 hours
3. Build SYSTEM_PROMPT template generator - 1.5 hours
4. Implement RAG integration with Qdrant - 1.5 hours
5. Build AI Patient service (LLM call with context) - 1.5 hours
6. Implement real-time empathy scoring (NLP markers) - 1 hour

**Validation Gate**:
- [ ] Progressive disclosure logic correct (tested with sample persona)
- [ ] Emotional state machine deterministic (same input → same state)
- [ ] RAG queries return relevant, sourced chunks
- [ ] AI Patient responses clinically accurate (no hallucinations)
- [ ] Response time <3 seconds (p95)
- [ ] Empathy scoring detects: "I understand", "concerning", "pain", etc.

---

### Phase 2: AI Examiner & 15-Mark Rubric (35% of effort, 7-8 hours)
**Goal**: Implement AI Examiner with AMC 15-mark rubric scoring

**Tasks**:
1. Design AMC 15-mark rubric prompt template - 1.5 hours
2. Implement structured JSON output validation - 1 hour
3. Build critical error detection logic - 1.5 hours
4. Implement scoring confidence calculation - 1 hour
5. Build AI Examiner service (LLM call, validation, persistence) - 1.5 hours
6. Create scoring_prompt_versions table + version control - 1 hour
7. Implement feedback generation (strengths, improvements, narrative) - 1 hour

**Validation Gate**:
- [ ] AI Examiner produces valid JSON output (5 scores + feedback)
- [ ] total_score = sum of 5 domain scores (validated)
- [ ] pass_fail logic correct (PASS ≥9, FAIL ≤7)
- [ ] Critical error detection works (catches missed red flags)
- [ ] Scoring confidence 0.0-1.0 calculated
- [ ] Feedback is specific and actionable (not generic)
- [ ] 10 mock transcripts scored, all scores reasonable

---

### Phase 3: Session State Management & Testing (25% of effort, 5-6 hours)
**Goal**: Real-time session state in Redis, comprehensive testing

**Tasks**:
1. Implement Redis session cache (persona, state, messages) - 1.5 hours
2. Build periodic sync to PostgreSQL (every 30 seconds) - 1 hour
3. Implement WebSocket message handling - 1 hour
4. Write unit tests for AI Patient - 1 hour
5. Write unit tests for AI Examiner - 1 hour
6. Write integration tests (end-to-end session flow) - 1.5 hours

**Validation Gate**:
- [ ] Redis cache working (keys expire after 1800 seconds)
- [ ] PostgreSQL sync accurate (no message loss)
- [ ] WebSocket connection stable (8 min without drops)
- [ ] Unit test coverage ≥85% (AI Patient, AI Examiner)
- [ ] Integration test: Full 8-min session flows without errors
- [ ] Cost tracking accurate (tokens counted correctly)

---

### Phase 4: Documentation & Golden Dataset (10% of effort, 2-3 hours)
**Goal**: Create documentation and establish golden dataset for validation

**Tasks**:
1. Document AI Patient prompt template with examples - 1 hour
2. Document AI Examiner rubric and scoring logic - 1 hour
3. Create 5 golden dataset sessions (expert human scores) - 1 hour
4. Validate AI scoring vs. human scoring (≥95% alignment) - 30 min

**Validation Gate**:
- [ ] All prompt templates documented
- [ ] Rubric scoring logic documented with examples
- [ ] 5 golden dataset sessions created with expert scores
- [ ] AI vs. human score variance <2 points on 15-mark scale
- [ ] Release notes prepared

---

## P - PLAN (Detailed Implementation)

### Phase 1: AI Patient Foundation

**Task 1.1**: Design Progressive Disclosure Schema
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Progressive disclosure mapping specification
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Question patterns identified (pain severity, onset, character, radiation, relieving factors, etc.)
  - [ ] JSONB schema designed for symptoms, medical_history
  - [ ] Disclosure keys mapped to question patterns
  - [ ] Schema supports 360 unique patient personas
  - [ ] Example persona fully mapped (e.g., CARD-001-CHEST-PAIN)

**Example Schema**:
```python
# Progressive disclosure mapping for patient_personas
symptoms_disclosure = {
    "immediate": ["visible in opening statement"],
    "when_asked_severity": "Patient answers if asked about pain severity",
    "when_asked_onset": "Patient answers if asked when pain started",
    "when_asked_character": "Patient answers if asked to describe type of pain",
    "when_asked_radiation": "Patient answers if asked where pain goes",
    "when_asked_relieving_factors": "Patient answers if asked what helps",
    "when_asked_aggravating_factors": "Patient answers if asked what makes worse",
    "when_asked_associated_symptoms": "Patient answers if asked about other symptoms",
    "when_asked_previous_episodes": "Patient answers if asked about previous similar pain"
}

# Detection: Does student question match a disclosure key?
# If yes: Answer from symptoms[key] revealed
# If no: Patient says "I don't think that's relevant" (encourages better questions)
```

**Task 1.2**: Implement Emotional State Machine
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: State machine implementation with state transitions
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] 5 states defined: ANXIOUS_GUARDED, CAUTIOUSLY_OPEN, TRUSTING, WITHDRAWN, UPSET
  - [ ] Empathy threshold for each transition (e.g., 3 empathy points to advance)
  - [ ] Transition rules implemented (what triggers each state change)
  - [ ] State machine deterministic (same inputs → same state)
  - [ ] Redis state storage tested
  - [ ] State transitions logged to emotional_state_transitions array

**State Machine Diagram**:
```
ANXIOUS_GUARDED (initial state)
    ↓ (3 empathy points) → CAUTIOUSLY_OPEN
    ↓ (dismissive language) → WITHDRAWN

CAUTIOUSLY_OPEN
    ↓ (5 more empathy points) → TRUSTING
    ↓ (cultural sensitivity) → TRUSTING (faster)
    ↓ (dismissive language) → WITHDRAWN

TRUSTING
    ↓ (dismissive/rushed behavior) → WITHDRAWN

WITHDRAWN
    ↓ (apologize + empathy) → CAUTIOUSLY_OPEN (slower recovery)

UPSET
    ↓ (sincere acknowledgment) → WITHDRAWN
    ↓ (continued dismissal) → END (patient disengages)
```

**Task 1.3**: Build SYSTEM_PROMPT Template Generator
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Dynamic SYSTEM_PROMPT construction for each persona
- **Dependencies**: Tasks 1.1, 1.2
- **Acceptance Criteria**:
  - [ ] SYSTEM_PROMPT template loads persona data from PostgreSQL
  - [ ] Template includes emotional state, empathy history, pain level
  - [ ] Symptoms section reflects only already-disclosed information
  - [ ] Emotional triggers section matches persona's emotional_profile
  - [ ] RAG context instructions included
  - [ ] Template renders correctly for 10 test personas

**Task 1.4**: Implement RAG Integration with Qdrant
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Qdrant integration with semantic search
- **Dependencies**: None (parallel work)
- **Acceptance Criteria**:
  - [ ] Qdrant client initialized (connection pool)
  - [ ] Medical guidelines collection exists (eTG, AMC Handbook, etc.)
  - [ ] Query function: Takes student message → Qdrant search → Top-5 chunks
  - [ ] Chunk structure: {text, source, page_ref, topic}
  - [ ] Query time <200ms (p95)
  - [ ] No irrelevant chunks returned (manual validation on 20 test queries)
  - [ ] Sources cited (eTG, AMC, EBM references)

**Task 1.5**: Build AI Patient Service
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: AI Patient LLM integration service
- **Dependencies**: Tasks 1.3, 1.4
- **Acceptance Criteria**:
  - [ ] AI Patient service loads persona + emotional state
  - [ ] Constructs SYSTEM_PROMPT + USER_PROMPT
  - [ ] Calls Claude 3.5 Sonnet (temp=0.7)
  - [ ] Parses response (strips metadata)
  - [ ] Returns {message, emotional_state, tokens_used}
  - [ ] Response time <3 seconds (p95)
  - [ ] Cost tracking: Tokens logged
  - [ ] Error handling: Graceful fallback if LLM fails

**Task 1.6**: Implement Real-Time Empathy Scoring
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: NLP-based empathy detection
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Empathy markers detected: "understand", "concerned", "pain", "worry", etc.
  - [ ] Dismissive markers detected: "probably", "overreacting", "nothing serious", etc.
  - [ ] Cultural sensitivity keywords: "family", "background", "preferences", etc.
  - [ ] Empathy points incremented/decremented based on markers
  - [ ] State transitions triggered when threshold reached
  - [ ] Logic tested on 30 sample student messages

---

### Phase 2: AI Examiner & 15-Mark Rubric

**Task 2.1**: Design AMC 15-Mark Rubric Prompt
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer (with Medical Advisor review)
- **Deliverable**: Structured prompt template for AI Examiner
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Rubric document created (5 domains, 0-15 total)
  - [ ] Scoring criteria clear for each domain (e.g., Communication 0-3)
  - [ ] Critical error definitions listed
  - [ ] Pass/fail logic documented (PASS ≥9, FAIL ≤7)
  - [ ] Prompt template includes patient scenario, expected approach, transcript
  - [ ] Prompt instructs JSON output format
  - [ ] Prompt templates reviewed by medical advisor for accuracy

**Task 2.2**: Implement Structured JSON Output Validation
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: JSON schema validation + error handling
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] Pydantic model: ScoreOutput with 5 score fields
  - [ ] Validates: all fields present, types correct, ranges valid (0-3, 0-4, etc.)
  - [ ] Calculates total_score = sum of 5 domains
  - [ ] Validates total_score matches sum (constraint check)
  - [ ] Determines pass_fail (PASS/FAIL/BORDERLINE)
  - [ ] Parses critical_errors array (empty or list)
  - [ ] Unit tests: Valid and invalid JSON payloads

**Task 2.3**: Build Critical Error Detection
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Rules engine for critical error detection
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] Rule: Chest pain + red flags → ECG must be ordered (or FAIL)
  - [ ] Rule: Chest pain + crushing + radiation → Cardiology consult required
  - [ ] Rule: Hypotension detected → IV access + fluids required
  - [ ] Rule: Unsafe medication dosing → Auto-fail
  - [ ] Rule: Severe cultural insensitivity → Auto-fail
  - [ ] Logic tested on 10 mock transcripts
  - [ ] False positive rate <5%

**Task 2.4**: Implement Scoring Confidence Calculation
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Confidence score (0.0-1.0) per session
- **Dependencies**: Task 2.2
- **Acceptance Criteria**:
  - [ ] Confidence formula: Based on clarity of evidence in transcript
  - [ ] High confidence (>0.95): Clear performance, obvious scores
  - [ ] Low confidence (<0.80): Ambiguous scenarios, borderline cases
  - [ ] Golden dataset reserved for human expert review (confidence <0.85)
  - [ ] Confidence values stored in osce_scores.scoring_confidence

**Confidence Calculation Example**:
```python
def calculate_confidence(transcript_analysis, scores):
    """
    Factors:
    - Evidence clarity: How clear is the evidence in transcript?
    - Agreement with rubric: Do scores match obvious performance?
    - Edge cases: Ambiguous situations lower confidence
    """
    evidence_clarity = analyze_transcript_clarity(transcript_analysis)
    score_consistency = check_score_consistency(scores)
    edge_case_penalty = detect_edge_cases(transcript_analysis)

    confidence = (evidence_clarity * 0.5 + score_consistency * 0.4 - edge_case_penalty * 0.1)
    return min(1.0, max(0.0, confidence))
```

**Task 2.5**: Build AI Examiner Service
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: AI Examiner LLM integration
- **Dependencies**: Tasks 2.1, 2.2, 2.4
- **Acceptance Criteria**:
  - [ ] AI Examiner service loads transcript, persona, expected DDx
  - [ ] Constructs SYSTEM_PROMPT (rubric) + USER_PROMPT (scenario + transcript)
  - [ ] Calls Claude 3.5 Sonnet (temp=0.1 for consistency)
  - [ ] Parses JSON response, validates with Pydantic model
  - [ ] Detects critical errors (uses rules engine)
  - [ ] Calculates confidence score
  - [ ] Returns {scores, feedback, critical_errors, confidence}
  - [ ] Cost tracking: Tokens logged
  - [ ] Error handling: Validation errors + retry logic

**Task 2.6**: Create Scoring Prompt Version Control
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: scoring_prompt_versions table + version management
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] scoring_prompt_versions table created with fields (version, template, active, accuracy)
  - [ ] v1.0 baseline loaded (initial rubric prompt)
  - [ ] v2.0 loaded (improved critical error detection)
  - [ ] v2.1 loaded (current version, 98%+ accuracy)
  - [ ] Query: Get active version for AI Examiner
  - [ ] Migration: Create table in Alembic

**Task 2.7**: Implement Feedback Generation
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Actionable feedback for students
- **Dependencies**: Tasks 2.5
- **Acceptance Criteria**:
  - [ ] Strengths array populated (3-5 specific strengths from transcript)
  - [ ] Areas for improvement array (2-4 specific gaps, not generic)
  - [ ] Overall feedback narrative (2-3 sentences, constructive)
  - [ ] Feedback directly references transcript evidence
  - [ ] Feedback tests: 10 mock transcripts, manual review for quality

---

### Phase 3: Session State Management & Testing

**Task 3.1**: Implement Redis Session Cache
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Redis cache for real-time session state
- **Dependencies**: None (parallel work)
- **Acceptance Criteria**:
  - [ ] Redis connection pool initialized
  - [ ] osce:session:{attempt_id}:persona key created (TTL 1800s)
  - [ ] osce:session:{attempt_id}:state key created (HASH with all fields)
  - [ ] osce:session:{attempt_id}:messages key created (LIFO list)
  - [ ] osce:session:{attempt_id}:actions key created (LIFO list)
  - [ ] osce:session:{attempt_id}:rag_queries key created (LIFO list)
  - [ ] Cache hit rate ≥95% (verified with Redis stats)
  - [ ] No stale data returned

**Task 3.2**: Build Periodic Sync to PostgreSQL
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Background job for Redis → PostgreSQL sync
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - [ ] Background job runs every 30 seconds (configurable)
  - [ ] Syncs conversation_history from Redis to PostgreSQL
  - [ ] Syncs emotional_state_transitions array
  - [ ] Syncs student_actions array
  - [ ] Syncs rag_queries_executed array
  - [ ] Accumulates tokens_used and llm_cost_usd
  - [ ] Final sync at session end (no data loss)
  - [ ] Zero race conditions (PostgreSQL row locks)

**Task 3.3**: Implement WebSocket Message Handling
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: WebSocket endpoint for 8-min session
- **Dependencies**: Tasks 1.5, 3.1
- **Acceptance Criteria**:
  - [ ] WebSocket endpoint: /ws/osce/{attempt_id}
  - [ ] JWT authentication on connection
  - [ ] User authorization check (matches attempt owner)
  - [ ] Message types: patient_message, timer_warning, session_ended, scoring_complete
  - [ ] Handles disconnects gracefully (final sync to PostgreSQL)
  - [ ] 8-min timer implemented (auto-finalize at 8:00)
  - [ ] 1-min warning sent (at 7:00)
  - [ ] Load test: 100 concurrent WebSocket connections (stable)

**Task 3.4**: Write Unit Tests for AI Patient
- **Effort**: 1 hour
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_services/test_ai_patient.py`
- **Dependencies**: Tasks 1.1-1.6
- **Test Cases**:
  - [ ] Test progressive disclosure (answer revealed only if asked)
  - [ ] Test emotional state machine (transitions on empathy)
  - [ ] Test SYSTEM_PROMPT generation (includes emotional state)
  - [ ] Test RAG query (returns top-5 chunks with sources)
  - [ ] Test AI Patient response (clinically accurate, <3 sec)
  - [ ] Test empathy scoring (markers detected, points updated)
  - [ ] Test token counting (accurate)
  - [ ] Coverage ≥85%

**Task 3.5**: Write Unit Tests for AI Examiner
- **Effort**: 1 hour
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_services/test_ai_examiner.py`
- **Dependencies**: Tasks 2.1-2.7
- **Test Cases**:
  - [ ] Test JSON parsing (valid output structure)
  - [ ] Test score validation (0-3, 0-4, 0-4, 0-2, 0-2)
  - [ ] Test total_score calculation
  - [ ] Test pass_fail logic (PASS ≥9, FAIL ≤7)
  - [ ] Test critical error detection (catches red flag misses)
  - [ ] Test confidence scoring (0.0-1.0 range)
  - [ ] Test feedback generation (specific, not generic)
  - [ ] Coverage ≥85%

**Task 3.6**: Write Integration Tests (End-to-End)
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_integration/test_ai_osce_session.py`
- **Dependencies**: Tasks 3.1-3.5
- **Test Cases**:
  - [ ] Full 8-minute session flow (student sends 5 messages)
  - [ ] Emotional state progresses correctly
  - [ ] AI Examiner scores at session end
  - [ ] Score saved to PostgreSQL correctly
  - [ ] user_progress updated (trigger fires)
  - [ ] Session state synced to PostgreSQL (no data loss)
  - [ ] Cost tracking accurate
  - [ ] WebSocket connection stable (no drops)
  - [ ] Coverage ≥85%

---

### Phase 4: Documentation & Golden Dataset

**Task 4.1**: Document AI Patient Prompt Template
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/AI_PATIENT_PROMPTS.md`
- **Dependencies**: Tasks 1.1-1.6
- **Contents**:
  - Overview of AI Patient system
  - Progressive disclosure schema with examples
  - Emotional state machine diagram + rules
  - SYSTEM_PROMPT template (annotated)
  - RAG integration workflow
  - Empathy scoring logic
  - Example persona (CARD-001-CHEST-PAIN) with full prompt
  - Cost estimates

**Task 4.2**: Document AI Examiner Rubric
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/AI_EXAMINER_RUBRIC.md`
- **Dependencies**: Tasks 2.1-2.7
- **Contents**:
  - AMC 15-mark rubric breakdown (5 domains)
  - Scoring criteria for each domain (0-3, 0-4, etc.)
  - Critical error definitions
  - Pass/fail logic with examples
  - Feedback generation guidelines
  - Prompt version history (v1.0, v2.0, v2.1)
  - Example scoring results (3 golden dataset sessions)

**Task 4.3**: Create Golden Dataset (Expert-Scored Sessions)
- **Effort**: 1 hour
- **Owner**: Backend Engineer (with Medical Advisor)
- **Deliverable**: 5 golden dataset sessions with expert human scores
- **Dependencies**: Tasks 3.6
- **Golden Dataset Sessions**:
  - [ ] Session 1: Excellent performance (14-15/15, PASS)
  - [ ] Session 2: Good performance (11-12/15, PASS)
  - [ ] Session 3: Borderline performance (8/15, BORDERLINE)
  - [ ] Session 4: Poor performance (5/15, FAIL)
  - [ ] Session 5: Critical error (7/15, FAIL due to missed red flag)
  - Each session includes:
    - Full transcript (8-min conversation)
    - Expert human scores (communication, clinical_reasoning, etc.)
    - Expert feedback narrative
    - Expected vs. AI Examiner scores

**Task 4.4**: Validate AI Scoring vs. Human Scoring
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Accuracy report + alignment metrics
- **Dependencies**: Task 4.3
- **Acceptance Criteria**:
  - [ ] Run 5 golden dataset sessions through AI Examiner
  - [ ] Compare AI scores vs. expert human scores
  - [ ] Calculate variance (should be <2 points on 15-mark scale)
  - [ ] Calculate pass_fail agreement (should be 100%)
  - [ ] Calculate feedback quality (alignment with expert feedback)
  - [ ] Report: "AI Examiner ≥95% aligned with expert scoring"

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] AI Patient system: Progressive disclosure, emotional state machine, natural dialogue
- [ ] AI Patient: Response time <3 seconds (p95), clinically accurate (no hallucinations)
- [ ] AI Patient: Empathy detected and state transitions triggered correctly
- [ ] RAG integration: Medical guidelines retrieved, sources cited, no hallucinations
- [ ] AI Examiner: Produces valid JSON with 5 scores (0-15 total)
- [ ] AI Examiner: Scoring ≥95% accurate vs. expert human validation
- [ ] AMC 15-Mark Rubric: All 5 domains (Communication 0-3, Clinical Reasoning 0-4, etc.)
- [ ] Critical error detection: Catches missed red flags, unsafe management
- [ ] Feedback generation: Specific, actionable, references transcript evidence
- [ ] Session state management: Redis cache + PostgreSQL sync, zero data loss
- [ ] Cost tracking: Accurate token counting, LLM cost calculated correctly
- [ ] Scoring prompt versioning: Version control in database (v1.0, v2.0, v2.1)

#### Quality Requirements
- [ ] **Test Coverage**: ≥85% (unit + integration)
- [ ] **Test Pass Rate**: 100% (zero tolerance for flaky tests)
- [ ] **Code Quality**: No linting errors, follows FastAPI best practices
- [ ] **Documentation**: Prompt templates, rubric, golden dataset documented
- [ ] **Golden Dataset**: 5 sessions with expert scores, ≥95% AI alignment

#### Performance Requirements
- [ ] **AI Patient**: Response time <3 seconds (p95)
- [ ] **AI Examiner**: Response time <5 seconds (p95)
- [ ] **RAG Query**: <200ms (p95)
- [ ] **Redis Cache**: Hit rate ≥95%
- [ ] **WebSocket**: 100+ concurrent connections, zero drops over 8 min

#### Security Requirements
- [ ] **No Hardcoded LLM Keys**: API key from environment variable
- [ ] **JWT Authentication**: WebSocket requires valid token
- [ ] **User Authorization**: Users can only access their own sessions
- [ ] **Input Validation**: Student messages validated (length, content)
- [ ] **No PII Leakage**: Conversations encrypted at rest (if required by compliance)

#### AMC Medical Compliance
- [ ] **15-Mark Rubric**: Exactly matches AMC Clinical Examination standards
- [ ] **Rubric Accuracy**: Expert review confirms alignment with AMC
- [ ] **Critical Actions**: Patient personas include correct critical actions (e.g., ECG <10min)
- [ ] **Differential Diagnosis**: Expected DDx matches clinical evidence
- [ ] **Red Flag Detection**: AI catches hallmark findings (e.g., chest pain + radiation + family history → STEMI)

---

### Testing Requirements

#### Unit Tests (≥85% coverage target)
```python
# backend/tests/test_services/test_ai_patient.py

def test_progressive_disclosure():
    """Test: Student must ask to receive information"""
    persona = get_persona("CARD-001-CHEST-PAIN")
    # If student asks: "Tell me about pain"
    # Expected: symptoms.when_asked_severity revealed
    # If student asks: "How is the weather?"
    # Expected: "That's not relevant right now"

def test_emotional_state_transition():
    """Test: Empathy triggers state change"""
    initial_state = "ANXIOUS_GUARDED"
    # Student shows empathy 3 times
    # Expected: state → CAUTIOUSLY_OPEN

def test_rag_query_accuracy():
    """Test: RAG returns accurate, sourced chunks"""
    query = "acute coronary syndrome management"
    chunks = qdrant_search(query, top_k=5)
    # Assertions:
    # - ≥4 chunks are relevant
    # - All chunks have source citations
    # - No hallucinated content

def test_ai_patient_token_counting():
    """Test: LLM tokens counted accurately"""
    response = ai_patient_service.generate_response(...)
    assert response['tokens_used'] == count_tokens(response['message'])

def test_empathy_scoring():
    """Test: Empathy markers detected"""
    messages = [
        "I understand your pain" → +1 empathy
        "That must be frightening" → +1 empathy
        "It's probably nothing" → -1 empathy
    ]
    # Validate empathy_points updated correctly
```

#### Integration Tests (End-to-End)
```python
# backend/tests/test_integration/test_ai_osce_session.py

def test_full_osce_session_flow():
    """Test: Complete 8-minute session with scoring"""
    # 1. Create session
    attempt = create_osce_session(user_id, persona_id="CARD-001")

    # 2. Connect WebSocket
    ws = connect_websocket(attempt_id)

    # 3. Send 5 student messages (simulate 8-min session)
    ws.send("I understand you're having chest pain...")
    ws.recv() → AI Patient response
    # ... repeat 5 times

    # 4. Session ends (timer expires)
    session_state = get_session_state(attempt_id)
    assert session_state == 'complete'

    # 5. Score generated
    score = get_score(attempt_id)
    assert score.total_score in range(0, 16)
    assert score.pass_fail in ['PASS', 'FAIL', 'BORDERLINE']

    # 6. PostgreSQL updated (no data loss)
    attempt = db.get_attempt(attempt_id)
    assert len(attempt.conversation_history) == 10  # 5 student + 5 patient
    assert attempt.emotional_state_transitions is not None

    # 7. User progress updated
    progress = db.get_progress(user_id)
    assert progress.ai_osces_attempted == 1
```

#### Golden Dataset Validation
```
Golden Dataset Comparison:
Session 1: Excellent (14/15)
  AI Examiner: 14/15 ✓
  Human Expert: 14/15
  Agreement: 100%

Session 2: Good (11/15)
  AI Examiner: 12/15
  Human Expert: 11/15
  Variance: 1 point (acceptable)

Session 3: Borderline (8/15)
  AI Examiner: 8/15 ✓
  Human Expert: 8/15
  Agreement: 100%

Session 4: Poor (5/15)
  AI Examiner: 5/15 ✓
  Human Expert: 5/15
  Agreement: 100%

Session 5: Critical Error (FAIL)
  AI Examiner: 6/15 FAIL ✓
  Human Expert: 6/15 FAIL
  Agreement: 100%

OVERALL ACCURACY: 5/5 sessions (100%)
```

---

### Documentation Deliverables

#### 1. AI Patient Prompts Documentation (`backend/docs/AI_PATIENT_PROMPTS.md`)
- Overview of AI Patient system architecture
- Progressive disclosure schema with 10+ examples
- Emotional state machine (5 states, transition rules)
- SYSTEM_PROMPT template (fully annotated)
- RAG integration workflow
- Empathy scoring algorithm
- Cost estimates
- Example persona: CARD-001-CHEST-PAIN (full walkthrough)

#### 2. AI Examiner Rubric Documentation (`backend/docs/AI_EXAMINER_RUBRIC.md`)
- AMC 15-mark rubric breakdown
- Scoring criteria for each domain (0-3, 0-4, 0-4, 0-2, 0-2)
- Critical error definitions (10+ examples)
- Pass/fail logic with examples
- Feedback generation guidelines
- Prompt version history (v1.0, v2.0, v2.1)
- Golden dataset summary (5 scored sessions)

#### 3. Integration Guide (`backend/docs/AI_INTEGRATION_GUIDE.md`)
- Architecture overview
- Component diagram
- Data flow diagrams (AI Patient, AI Examiner, scoring)
- Redis cache schema
- Qdrant integration
- WebSocket message types
- Error handling + recovery
- Performance tuning

#### 4. Cost & Scaling Analysis (`backend/docs/AI_ECONOMICS.md`)
- Token usage per session (average)
- Cost per session (AI Patient + AI Examiner)
- Annual cost per student (200 sessions)
- Scaling calculations (1000 concurrent students)
- Optimization opportunities

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ AI Patient system generates realistic, progressive-disclosure responses
2. ✅ Emotional state machine transitions correctly on empathy triggers
3. ✅ RAG integration retrieves accurate medical guidelines (no hallucinations)
4. ✅ AI Examiner produces valid JSON with AMC 15-mark rubric scores
5. ✅ AI Examiner scores ≥95% aligned with expert human validation (golden dataset)
6. ✅ Critical error detection catches missed red flags
7. ✅ Session state management (Redis ↔ PostgreSQL) zero data loss
8. ✅ WebSocket connections stable (100+ concurrent, 8-min sessions)
9. ✅ Test coverage ≥85%, 100% pass rate
10. ✅ Performance targets met (AI <3s, Examiner <5s, RAG <200ms)
11. ✅ Documentation complete (prompts, rubric, integration guide)
12. ✅ Golden dataset validated (5 sessions, ≥95% accuracy)

**Sign-off Required From**:
- [ ] Backend Engineer (implementation complete, tests passing)
- [ ] Medical Advisor (rubric accuracy, clinical appropriateness)
- [ ] Testing QA (coverage ≥85%, 100% pass rate)
- [ ] PM Coordinator (requirements met, performance targets achieved)

---

## 📎 Appendices

### Appendix A: Emotional State Machine Transition Rules
```
STATE: ANXIOUS_GUARDED
├─ Empathy points: 0
├─ Triggers for CAUTIOUSLY_OPEN:
│  ├─ Student shows empathy (3+ empathy markers)
│  ├─ Student asks open-ended questions
│  └─ Student explains what they're doing
├─ Triggers for WITHDRAWN:
│  ├─ Student dismissive language
│  ├─ Student interrupts frequently
│  └─ Student seems rushed
└─ Duration: Minutes 0-2

STATE: CAUTIOUSLY_OPEN
├─ Empathy points: 3+
├─ Triggers for TRUSTING:
│  ├─ Student addresses pain/concerns
│  ├─ Student provides clear explanations
│  ├─ Student shows cultural sensitivity
│  └─ Student involves patient in decision-making
├─ Triggers for WITHDRAWN:
│  └─ Student dismissive or rushed behavior
└─ Duration: Minutes 2-5

STATE: TRUSTING
├─ Empathy points: 6+
├─ Characteristics:
│  ├─ Patient cooperates fully
│  ├─ Shares sensitive medical info
│  └─ Asks medical questions
├─ Triggers for WITHDRAWN:
│  └─ Student abrupt behavior change
└─ Duration: Minutes 5-8

STATE: WITHDRAWN (Recovery)
├─ Empathy points: -1
├─ Triggers for CAUTIOUSLY_OPEN:
│  ├─ Student apologizes sincerely
│  ├─ Student shows empathy
│  └─ Patient gives second chance
├─ Duration: Minutes after dismissal
└─ Recovery Rate: Slower than initial trust-building

STATE: UPSET (Critical)
├─ Empathy points: -2
├─ Occurs when: Student culturally insensitive, judgmental
├─ Recovery: Very difficult, may end session early
└─ Impact: Auto-lower communication score
```

### Appendix B: Critical Error Examples (Auto-Fail)
```
1. MISSED RED FLAG: Chest pain + crushing + radiation → No ECG ordered
   Error: "Student failed to recognize acute coronary syndrome"

2. UNSAFE MANAGEMENT: Treating severe hypertension with beta-blocker in patient on cocaine
   Error: "Dangerous medication choice in this context"

3. CULTURAL INSENSITIVITY: Dismissing patient's family involvement request (Chinese Australian)
   Error: "Failed to respect cultural preferences; dismissed patient dignity"

4. MEDICATION ERROR: Aspirin 500mg instead of 300mg in acute MI
   Error: "Incorrect medication dosing; unsafe"

5. MISSED ANAPHYLAXIS: Patient reports itching + swelling → No immediate action
   Error: "Failed to recognize anaphylaxis progression; potential patient harm"
```

### Appendix C: RAG Query Examples
```
Example 1: "Tell me more about the chest pain"
→ Detected intent: Symptom exploration
→ RAG query: "chest pain character severity STEMI ACS"
→ Results: [
  {text: "Chest pain in ACS presents as crushing...", source: "eTG Cardiology"},
  {text: "STEMI red flags: crushing pain, radiation...", source: "AMC Handbook p.156"},
  ...
]

Example 2: "What should I do now?"
→ Detected intent: Management guidance
→ RAG query: "acute coronary syndrome STEMI management ECG aspirin"
→ Results: [
  {text: "STEMI management protocol: ECG <10 min...", source: "eTG Emergency"},
  {text: "Aspirin dosing in ACS: 300mg immediately...", source: "NSTEMI Guidelines"},
  ...
]

Example 3: "I'd like to examine your heart"
→ Detected intent: Physical examination guidance
→ RAG query: "cardiac examination auscultation murmur friction rub"
→ Results: [
  {text: "Cardiac examination technique: inspection, palpation, auscultation...", ...},
  ...
]
```

### Appendix D: Sample AI Patient Response with Annotations
```
SCENARIO: Robert Chen, 52M, chest pain for 2 hours
STUDENT: "Can you describe the pain in more detail?"

SYSTEM_PROMPT (state: CAUTIOUSLY_OPEN, empathy_points: 3):
  You are Robert Chen. Current emotional state: CAUTIOUSLY_OPEN.
  You showed empathy and asked open questions, so you're willing to share more.
  Describe your pain using these disclosed details:
  - Character: Heavy, crushing, tight
  - Radiation: Down left arm, sometimes jaw
  - Severity: 8/10 (feels like crushing pressure)
  Include emotional cues. Be natural, not robotic.

CLAUDE RESPONSE:
  "Well, the pain... it's like someone's standing on my chest, you know?
   Really heavy and tight. And it goes down my left arm, all the way to
   my fingers. [Pauses] That's the scary part. I read somewhere that when
   pain goes down your arm, it means something serious with the heart.
   Are you... do you think it could be a heart attack?"

POST-PROCESSING:
  - Emotional cues detected: "That's the scary part", asking fearful question
  - Empathy analysis: Student asked open question (positive), no dismissal
  - Empathy points: +1 (now 4 total)
  - State transition: Check if 5+ points → trigger TRUSTING? No (only 4)
  - State remains: CAUTIOUSLY_OPEN
  - Tokens: 78 input + 54 output = 132 tokens
  - Cost: $0.000396 (at $0.003/1K tokens)

RESPONSE TO WEBSOCKET:
  {
    "type": "patient_message",
    "speaker": "patient",
    "message": "Well, the pain... it's like someone's standing on my chest...",
    "emotional_state": "CAUTIOUSLY_OPEN",
    "emotional_state_changed": false,
    "pain_level": 8,
    "tokens_used": 132,
    "timestamp": "2026-02-16T10:06:45Z"
  }

REDIS UPDATE:
  hset osce:session:{attempt_id}:state
    emotional_state CAUTIOUSLY_OPEN
    empathy_points 4
    tokens_used 366
    message_count 6
```

### Appendix E: Scoring Example (Golden Dataset Session 1)

**Student Performance**: Excellent (14/15, PASS)

**AI Examiner Scoring**:
```json
{
  "communication_score": 3,
  "communication_feedback": "Outstanding empathy and communication skills demonstrated.
                             Student opened with clear introduction and immediate
                             reassurance. Used open-ended questions to understand
                             patient's concerns. Maintained eye contact (inferred from
                             conversational flow). Patient progressed from anxious to
                             trusting, indicating excellent rapport building.",

  "clinical_reasoning_score": 4,
  "clinical_reasoning_feedback": "Comprehensive clinical reasoning evident. Student
                                 rapidly recognized acute coronary syndrome from red
                                 flags (crushing chest pain, radiation to arm,
                                 diaphoresis, family history). Differential diagnosis
                                 appropriate (STEMI primary, unstable angina, PE
                                 considered). Clinical prioritization correct.",

  "information_gathering_score": 3,
  "information_gathering_feedback": "Thorough, systematic history obtained. Covered
                                     pain characteristics (onset, character, severity,
                                     radiation), associated symptoms (dyspnea, diaphoresis,
                                     nausea), medical history (diabetes, cholesterol),
                                     medications, smoking history, and family history.
                                     Minor: Could have explored allergies explicitly.",

  "management_score": 2,
  "management_feedback": "Safe, appropriate, evidence-based management. Ordered ECG
                          immediately (correct critical action). Gave aspirin 300mg
                          (appropriate dose). Called cardiology for urgent
                          intervention. Implied continuous monitoring.",

  "professionalism_score": 2,
  "professionalism_feedback": "Exemplary professionalism. Respectful, clear
                              explanations. Explained procedures to alleviate anxiety.
                              Maintained patient dignity. Culturally sensitive.",

  "total_score": 14,
  "pass_fail": "PASS",
  "critical_errors": [],
  "strengths": [
    "Recognized acute coronary syndrome immediately",
    "Outstanding empathy and rapport building",
    "Systematic approach to history taking",
    "Appropriate emergency management"
  ],
  "areas_for_improvement": [
    "Could have explored allergies explicitly",
    "Minor: Could have offered analgesia more proactively"
  ],
  "overall_feedback": "This student demonstrated excellent clinical acumen and
                      communication skills. Rapid recognition of serious pathology,
                      thorough history, appropriate differential diagnosis, and
                      evidence-based management. Patient felt heard and reassured.
                      Performance meets AMC Clinical Examination standard for PASS."
}
```

**Expert Human Score**: 14/15 (PASS) ✅
**Agreement**: 100% (AI and human aligned)

---

**Document Status**: Complete
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: Pending PM Review
**Version**: 1.0
**File Size**: ~48 KB
**Line Count**: ~2000 lines
