# Project Constraints & Standards - Quick Reference

**Project**: irStudy - ICRP Medical Education AI System
**Version**: 3.0.0 (Modular Structure)
**Last Updated**: 2026-01-26
**Format**: Lightweight index + detailed constraint modules

---

## 🚨 CRITICAL: Read Before Starting Work

**ALL agents MUST read relevant constraints before starting ANY work.**

This file provides a quick reference. For detailed requirements, see individual constraint files in `/constraints/` folder.

---

## Top 10 Critical Constraints (Must Know)

| # | Constraint | Details | File |
|---|------------|---------|------|
| 1 | **Australian Medical Context** | Use eTG, PBS, AHPRA, Australian spelling (paracetamol not acetaminophen) | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 2 | **NO Placeholder Content** | 100% real content - NO templates, NO "Option A", NO "Clinical scenario for..." | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 3 | **Python venv REQUIRED** | ALWAYS `source venv/bin/activate` before running Python scripts | [constraints/4-llm-integration.md](constraints/4-llm-integration.md) |
| 4 | **Local LLMs CANNOT generate MCQs** | Use Claude (Anthropic API) for ALL MCQ/OSCE generation | [constraints/4-llm-integration.md](constraints/4-llm-integration.md#42-claude-vs-local-llms-for-medical-content-critical) |
| 5 | **RAG citations REQUIRED** | Exactly 3 citations per MCQ, >0.70 confidence, with page numbers | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 6 | **NO hardcoded credentials** | Use `ref.read(databaseConfigProvider)` - NEVER mock IDs | [constraints/3-security.md](constraints/3-security.md) |
| 7 | **100% test pass rate** | ALL tests must pass before commit - NO exceptions | [constraints/6-testing.md](constraints/6-testing.md) |
| 8 | **UTF-8 encoding** | ALWAYS `open(file, 'r', encoding='utf-8')` for JSON/text files | [constraints/5-data-processing.md](constraints/5-data-processing.md) |
| 9 | **No PHI in logs** | Hash/truncate patient identifiers - NEVER log MRN, DOB, email | [constraints/3-security.md](constraints/3-security.md) |
| 10 | **Australian drug names** | paracetamol, salbutamol, adrenaline (NOT acetaminophen, albuterol, epinephrine) | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 11 | **Ralph PROMPT.md Directives** | Use "EXECUTE NOW", NOT "Would you like..." - Prevents premature Ralph exits | [constraints/13-ralph-execution.md](constraints/13-ralph-execution.md) |
| 12 | **Medical Content Quality Gates** | ALL medical content MUST pass 13-gate QA + FRACP validation, 100% RAG citations | [constraints/14-ralph-medical-content-standards.md](constraints/14-ralph-medical-content-standards.md) |
| 13 | **Ponytail/Code Reuse FIRST** | ALWAYS search for existing code before creating new - See Section 0 Discovery requirements | [.claude/CLAUDE.md](.claude/CLAUDE.md#0---discovery--code-reuse-ponytail-strategy) |

---

## 0 - DISCOVERY & CODE REUSE (Ponytail Strategy)

**Ponytail Principle**: Every line of code that doesn't need to exist saves tokens, time, and errors.

### Section 0 in PRDs (MANDATORY as of 2026-07-01)

All PRDs executed by Ralph MUST include **Section 0: DISCOVERY** that documents:
- Existing code search results (Python backend, TypeScript frontend, Flutter mobile)
- Reusable components identified (FastAPI routers, React components, medical content)
- Python/TypeScript/Flutter packages considered
- RAG content evaluated (Qdrant search for existing medical content)
- Decision to reuse vs. create new

**Example Section 0 for irStudy** (Medical Education Platform - EMR + OSCE):
```markdown
## 0 - DISCOVERY

### Existing Code Search

**Python/FastAPI Backend**:
- ✅ FOUND: FastAPI router pattern in `backend/src/api/routers/patient_router.py`
- ✅ FOUND: SQLAlchemy models in `backend/src/models/`
- ❌ NOT FOUND: OSCE scenario evaluation logic (new domain)

**TypeScript/React Frontend**:
- ✅ FOUND: PatientCard component in `frontend/src/components/PatientCard.tsx`
- ✅ FOUND: usePatient hook in `frontend/src/hooks/usePatient.ts`
- ❌ NOT FOUND: OSCE timer component (new feature)

**Medical Content/RAG**:
- ✅ FOUND: Existing peptic ulcer disease content in Qdrant (qdrant_point_id: 550e8400-...)
- ✅ FOUND: 47 AMC blueprint conditions with 100% citations
- ❌ NOT FOUND: Communication skills rubrics (new content type)

### Reuse Decisions

1. **FastAPI Router Pattern**: Reuse `patient_router.py` structure
   - SQLAlchemy + dependency injection + error handling
   - Reference: `backend/src/api/routers/patient_router.py:12-45`

2. **React Component Pattern**: Reuse `PatientCard.tsx` structure
   - TypeScript typing + useState/useEffect hooks + error states
   - Reference: `frontend/src/components/PatientCard.tsx:15-60`

3. **Medical Content**: Extend existing Qdrant content, don't recreate
   - Search Qdrant FIRST before generating new medical content
   - Reuse existing citations (eTG, AMH, Talley & O'Connor)

4. **Flutter Mobile**: Check for existing Riverpod providers before creating new
   - Reference: `mobile/lib/features/*/providers/*_provider.dart`

### Packages Considered

**Python Backend**:
- `fastapi: ^0.115.0` ✅ ALREADY INSTALLED
- `sqlalchemy: ^2.0.0` ✅ ALREADY INSTALLED
- `alembic: ^1.13.0` ✅ ALREADY INSTALLED
- `anthropic: ^0.39.0` ✅ ALREADY INSTALLED (for medical content generation)

**TypeScript Frontend**:
- `react: ^18.2.0` ✅ ALREADY INSTALLED
- `axios: ^1.7.0` ✅ ALREADY INSTALLED
- `react-router-dom: ^6.26.0` ✅ ALREADY INSTALLED

**Flutter Mobile**:
- `flutter_riverpod: ^2.6.0` ✅ ALREADY INSTALLED
- `intl: ^0.19.0` ✅ ALREADY INSTALLED
```

### Discovery Commands (Run BEFORE Creating Code)

**Python/FastAPI Backend Search**:
```bash
# Search for existing routers
find backend/src/api/routers -name "*.py"

# Search for existing models
find backend/src/models -name "*.py"

# Check for similar endpoints
grep -r "@router\." backend/src/api/

# Check for existing Alembic migrations
ls backend/alembic/versions/*.py | sort

# Check for existing database operations
grep -r "session.query\|session.add\|session.commit" backend/src/

# Check installed Python packages
cat backend/requirements.txt | grep [package-name]

# Check for existing medical content processing
grep -r "qdrant_point_id\|citations" backend/src/
```

**TypeScript/React Frontend Search**:
```bash
# Search for existing components
find frontend/src/components -name "*.tsx"

# Search for existing hooks
find frontend/src/hooks -name "*.ts"

# Check for similar API calls
grep -r "axios.get\|axios.post" frontend/src/

# Check for existing state management
grep -r "useState\|useContext\|useReducer" frontend/src/

# Check installed npm packages
cat frontend/package.json | grep [package-name]

# Check for existing types
find frontend/src/types -name "*.ts"
```

**Flutter Mobile Search**:
```bash
# Search for existing providers
find mobile/lib -name "*_provider.dart"

# Search for existing repositories
find mobile/lib -name "*_repository.dart"

# Check for existing FFI calls
grep -r "ffi\." mobile/lib/

# Check for existing widgets
find mobile/lib/features -name "*_screen.dart" -o -name "*_widget.dart"

# Check for existing database patterns
grep -r "databaseConfigProvider" mobile/lib/
```

**Medical Content/RAG Search** (CRITICAL for irStudy):
```bash
# Search Qdrant for existing medical content (prevents duplication)
curl -X POST "http://localhost:6333/collections/amc_blueprints/points/search" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, ...],
    "limit": 10,
    "with_payload": true
  }'

# Check existing AMC blueprint conditions
find backend/data/amc_blueprints -name "*.json" | wc -l

# Check for existing citations (don't recreate)
grep -r "qdrant_point_id\|citation.*eTG\|citation.*AMH" backend/data/

# Check for similar clinical scenarios
grep -r "presenting_complaint\|differential_diagnosis" backend/data/

# Search for existing red flags by condition
grep -r "red_flags" backend/data/amc_blueprints/
```

### Code Reuse Checklist (Complete BEFORE Creating New Code)

**Python/FastAPI Backend**:
- [ ] Does this router exist? → Search `backend/src/api/routers/`
- [ ] Does this model exist? → Search `backend/src/models/`
- [ ] Does this endpoint exist? → Grep for `@router.get`, `@router.post`
- [ ] Does this Alembic migration exist? → Check `backend/alembic/versions/`
- [ ] Is there a Python package? → Check requirements.txt, PyPI
- [ ] Can I extend existing code? → Prefer extension over duplication

**TypeScript/React Frontend**:
- [ ] Does this component exist? → Search `frontend/src/components/`
- [ ] Does this hook exist? → Search `frontend/src/hooks/`
- [ ] Does this API call exist? → Grep for axios/fetch calls
- [ ] Does this type exist? → Search `frontend/src/types/`
- [ ] Is there an npm package? → Check package.json, npmjs.com
- [ ] Can I reuse existing state management? → Check context/hooks

**Flutter Mobile** (if applicable):
- [ ] Does this provider exist? → Search `mobile/lib/**/*_provider.dart`
- [ ] Does this repository exist? → Search `mobile/lib/**/*_repository.dart`
- [ ] Does this FFI call exist? → Grep for `ffi.` calls
- [ ] Does this widget exist? → Search `mobile/lib/**/*_screen.dart`
- [ ] Can I reuse DatabaseConfig pattern? → Grep for `databaseConfigProvider`

**Medical Content/RAG** (CRITICAL - irStudy specific):
- [ ] Does this clinical scenario exist in Qdrant? → Search RAG database
- [ ] Does this AMC blueprint condition exist? → Check `backend/data/amc_blueprints/`
- [ ] Do these citations exist? → Grep for `qdrant_point_id`, eTG/AMH references
- [ ] Can I extend existing medical content? → Prefer augmentation over recreation
- [ ] Are red flags already documented? → Check existing condition files

### Anti-Patterns (NEVER DO THIS)

❌ **Creating new FastAPI router without discovery**:
```python
# WRONG: Creating new router without checking if similar exists
@router.post("/my-new-endpoint")
async def my_endpoint(db: Session = Depends(get_db)):
    ...
```

✅ **Correct approach**:
```bash
# FIRST: Search for existing routers and endpoints
find backend/src/api/routers -name "*.py"
grep -r "@router.post" backend/src/api/

# THEN: Reuse pattern if found, or create new with justification in Section 0
```

❌ **Duplicating React components**:
```tsx
// WRONG: Creating new PatientCard when one exists
export function MyCustomPatientCard() { ... }
```

✅ **Correct approach**:
```bash
# FIRST: Search for existing components
find frontend/src/components -name "*Patient*.tsx"

# THEN: Reuse or extend existing implementation
```

❌ **Recreating medical content that already exists**:
```python
# WRONG: Generating new peptic ulcer content without checking Qdrant
new_content = generate_peptic_ulcer_scenario()
```

✅ **Correct approach**:
```bash
# FIRST: Search Qdrant for existing content
curl -X POST "http://localhost:6333/collections/amc_blueprints/points/search" ...

# THEN: If found (>0.70 confidence), reuse existing content
# ONLY generate new content if truly missing from RAG database
```

### Integration with Ralph PRDs

**All PRDs executed by Ralph MUST**:
1. Include Section 0 (DISCOVERY) documenting search results across all systems:
   - Python/FastAPI backend
   - TypeScript/React frontend
   - Flutter mobile (if applicable)
   - Medical content/RAG (Qdrant)
   - Cross-system shared infrastructure (Vault, Redis)

2. Justify new code creation:
   - Explain why existing code couldn't be reused
   - Document searches performed (include grep/find commands used)
   - Reference similar patterns that informed new implementation

3. Reference existing patterns:
   - FastAPI routers, SQLAlchemy models, Alembic migrations
   - React components, custom hooks, API clients
   - Flutter providers, repositories, widgets
   - Medical content citations, RAG entries

4. Follow cross-system coordination:
   - Check SHARED_INFRASTRUCTURE_SPEC.md before creating infrastructure
   - Coordinate with other system (EMR vs OSCE) to prevent conflicts
   - Reference COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md

### Token Optimization Impact (irStudy-specific)

**Before Ponytail** (creating everything new):
- FastAPI router: 200 lines (new implementation + tests)
- React component: 150 lines (new structure + state management)
- Medical content: 500 lines (regenerate existing AMC blueprint)
- **Total**: 850 lines, ~17,000 tokens

**After Ponytail** (reuse existing patterns + extend RAG content):
- FastAPI router: 50 lines (reuse patient_router.py pattern)
- React component: 40 lines (reuse PatientCard.tsx pattern)
- Medical content: 100 lines (extend existing Qdrant entry, add new sections)
- **Total**: 190 lines, ~3,800 tokens

**Savings**: 78% fewer lines, 78% fewer tokens, 35% faster execution

**Medical Content Savings** (Unique to irStudy):
- Searching Qdrant FIRST prevents regenerating existing AMC blueprint conditions
- Reusing existing citations (eTG, AMH, Talley) saves ~500 tokens per condition
- Extending existing content maintains consistency and citation quality

### References

- **Global Ponytail Standards**: `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/PONYTAIL_INTEGRATION.md`
- **T-RALPH v2.2 Standards**: `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/PRD_STANDARDS_V2_T-RALPH.md`
- **Project-Specific Patterns**: `/home/dev/Development/irStudy/.claude/CLAUDE.md`
- **Cross-System Coordination**: `/home/dev/Development/irStudy/COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md`

---

## Constraint Modules (Detailed)

### 1. Medical Accuracy Standards
**File**: [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md)
**Status**: MANDATORY
**Key Topics**: Australian context, spelling, citations, clinical accuracy

**Critical Rules**:
- ✅ Use: eTG, PBS, AHPRA, AMH, Australian spelling
- ❌ Never: American sources without context, placeholder content
- 📊 Quality: 100% citation validation, 3 citations per MCQ

### 2. Code Architecture & Patterns
**File**: [constraints/2-code-architecture.md](constraints/2-code-architecture.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Agent patterns, project structure, naming conventions

### 3. Security & Configuration
**File**: [constraints/3-security.md](constraints/3-security.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: No hardcoded credentials, PHI protection, HIPAA compliance

**Critical Rules**:
- ❌ NEVER: Hardcode database paths, mock user IDs, log PHI
- ✅ ALWAYS: Use config providers, hash identifiers, sanitize logs

### 4. LLM Integration Patterns ⚠️ NEW
**File**: [constraints/4-llm-integration.md](constraints/4-llm-integration.md)
**Status**: CRITICAL - Read before ANY LLM work
**Last Updated**: 2026-01-26 (Added Section 4.2)

**Sections**:
- 4.0: Python Environment & LLM Requirements
- 4.1: Ollama Client Usage
- 4.2: **Claude vs Local LLMs for Medical Content** (NEW)

**Critical Discovery (2026-01-26)**:
- ❌ Local LLMs (Ollama 7B models) **CANNOT** generate complex MCQs
- ✅ **MUST** use Claude (Anthropic API) for MCQ/OSCE generation
- 📊 Evidence: 200 MCQs failed with local LLMs → all placeholders
- 💰 Cost: ~$0.02/MCQ (acceptable vs quality compromise)

**Task Complexity Matrix**:
| Task | Local LLMs (Ollama) | Claude (Anthropic API) |
|------|---------------------|------------------------|
| MCQ generation | ❌ FAILS | ✅ REQUIRED |
| OSCE generation | ❌ FAILS | ✅ REQUIRED |
| Simple validation | ✅ OK | ✅ OK |

### 5. Data Processing Standards
**File**: [constraints/5-data-processing.md](constraints/5-data-processing.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: JSON handling, UTF-8 encoding, large file processing

### 6. Testing Requirements
**File**: [constraints/6-testing.md](constraints/6-testing.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: 100% pass rate, test coverage, quality gates

### 7. Documentation Standards
**File**: [constraints/7-documentation.md](constraints/7-documentation.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Code comments, API docs, constraint documentation

### 8. Agent-Specific Requirements
**File**: [constraints/8-agent-requirements.md](constraints/8-agent-requirements.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Medical agents (MED-001-046), QA agents, specialist requirements

### 9. Project-Specific Context
**File**: [constraints/9-project-context.md](constraints/9-project-context.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: ICRP exam preparation, AMC standards, 46-agent system

### 10. Anti-Patterns (What NOT to Do)
**File**: [constraints/10-anti-patterns.md](constraints/10-anti-patterns.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Common mistakes, violations discovered, historical lessons

### 11. ICRP Clinical Training Standards
**File**: [constraints/11-icrp-standards.md](constraints/11-icrp-standards.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: AMC Clinical Exam, OSCE requirements, Australian medical training

### 12. RAG Citation Requirements
**File**: [constraints/12-rag-citation.md](constraints/12-rag-citation.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Citation format, confidence scores, verification badges

### 13. Ralph Execution Requirements ⚠️ NEW
**File**: [constraints/13-ralph-execution.md](constraints/13-ralph-execution.md)
**Status**: MANDATORY - Read before creating PROMPT.md or PRD files
**Last Updated**: 2026-02-07

**Critical Rules**:
- ✅ ALWAYS: Use "AUTONOMOUS EXECUTION MODE" header, "EXECUTE NOW" commands
- ❌ NEVER: Use "Would you like...", "Should I...", "Please..." phrasing
- 📊 Requirements: Exact bash commands (no placeholders), verification commands, success criteria

**Problem Solved**: Prevents Ralph loop premature exits caused by question-based prompts

**Sections**:
- 13.1: AUTONOMOUS EXECUTION MODE Header (required)
- 13.2: Directive Language Only (no questions)
- 13.3: Exact Commands (no placeholders)
- 13.4: Success Criteria with Verification
- 13.5: PRD Template Structure
- 13.6: Quality Checks Before Running Ralph

### 14. Ralph Medical Content Quality Standards ⚠️ NEW
**File**: [constraints/14-ralph-medical-content-standards.md](constraints/14-ralph-medical-content-standards.md)
**Status**: **MANDATORY** - Auto-enforced in all medical content PRDs
**Last Updated**: 2026-03-21

**Critical Rules**:
- ✅ ALWAYS: Use clinical expert agents (clinical-documentation-expert, history-taking-expert, physical-examination-expert)
- ✅ ALWAYS: Include 3 required skills (rag-citation-verification, australian-medical-terminology, fracp-clinical-validation)
- ✅ ALWAYS: Include 5 required validations (QA 13-gate, FRACP clinical, security scan, RAG coverage, database)
- ❌ NEVER: Generate medical content without RAG citations (100% coverage required)
- ❌ NEVER: Use placeholder content ("Clinical scenario for...", "Option A/B/C/D")
- 📊 Quality Gates: 13-gate QA validation + FRACP clinical validation (≥8.0/10)

**Problem Solved**: Prevents medical content generation without proper quality gates

**Sections**:
- 14.1: Overview - Automatic Quality Enforcement
- 14.2: Mandatory PRD Components for Medical Content
- 14.3: Quality Gate Enforcement Flow
- 14.4: RAG System Requirements
- 14.5: 13-Gate QA Validation System
- 14.6: FRACP Clinical Validation
- 14.7: Auto-Fix Common Errors
- 14.8: Enforcement Checklist for PRD Authors
- 14.9: Example Medical Content PRD Template
- 14.10: Monitoring and Metrics

**Current Metrics (Batch 1 - 207 Personas)**:
- ✅ 100% RAG citation coverage (3,726 citations with qdrant_point_id)
- ✅ 96.5% deployment readiness (200/207 approved)
- ✅ 0 hallucinated citations (100% verified)
- ✅ 66.1% Australian sources (exceeds 60% target)

---

## Quick Start Guide

### Before Writing Code
1. Read Top 10 Critical Constraints (above)
2. Identify your task type (MCQ generation? Testing? Security?)
3. Read relevant constraint module(s)
4. Follow implementation checklist in constraint file

### Before Committing Code
- [ ] All tests pass (100% pass rate)
- [ ] No hardcoded credentials
- [ ] No placeholder content
- [ ] Australian spelling used
- [ ] Citations validated (if MCQ/OSCE)
- [ ] UTF-8 encoding specified
- [ ] No PHI in logs

---

## Recent Changes

### v3.0.0 (2026-01-26) - Modular Structure
- **Restructured**: Split 30,000+ token file into modular constraint files
- **Added**: `constraints/4-llm-integration.md` with Section 4.2 (LLM Capabilities)
- **Created**: Lightweight quick reference (this file)
- **Benefit**: Easier to read, navigate, and maintain

### v2.1.0 (2026-01-26) - LLM Capabilities Constraint
- **Added**: Section 4.2 documenting that local 7B models cannot generate complex MCQs
- **Mandated**: Claude Code client for all MCQ/OSCE generation
- **Evidence**: 200 placeholder MCQs from failed local model generation
- **Impact**: Prevents future quality compromises

---

## File Structure

```
/home/dev/Development/irStudy/
├── PROJECT_CONSTRAINTS_V3.md (this file - quick reference)
├── PROJECT_CONSTRAINTS.md (legacy - 30,000+ tokens)
└── constraints/
    ├── README.md (constraint system overview)
    ├── 4-llm-integration.md (✅ created 2026-01-26)
    └── (other constraint files - to be created)
```

---

## Need Help?

1. **Can't find a constraint?** Check the detailed file in `/constraints/` folder
2. **Constraint unclear?** Ask PM to clarify or update constraint file
3. **Discovered new constraint?** Document it and add to relevant constraint file
4. **File too large?** Consider splitting into sub-sections

---

## For Agents

**CRITICAL**: Before starting ANY work:
1. Identify task type (MCQ generation, testing, security, etc.)
2. Read relevant constraint file(s) from `/constraints/` folder
3. Follow implementation checklist
4. Validate work against constraints before returning

**If constraint file doesn't exist yet**: Read legacy `PROJECT_CONSTRAINTS.md` and extract relevant section.

---

**Status**: ✅ ACTIVE (v3.0.0 Modular Structure)
**Maintenance**: Update constraint files as new requirements discovered
**Legacy File**: `PROJECT_CONSTRAINTS.md` (kept for reference until all modules created)

---

## MCQ Data Quality Constraints (CRITICAL - MANDATORY)

### 15. MCQ Content Validation (Zero-Tolerance Policy)

**Status**: MANDATORY - Auto-enforced in all MCQ generation and data loading
**Last Updated**: 2026-05-27
**Incident**: 1,046/1,613 MCQs (64.8%) were placeholder content (CRITICAL DATA QUALITY FAILURE)

#### 15.1 Placeholder Content Detection (ZERO TOLERANCE)

**ALL MCQ generation, data loading, and database insertion scripts MUST reject placeholder content.**

**Forbidden Placeholder Patterns** (auto-reject):

```python
PLACEHOLDER_PATTERNS = [
    # Question text placeholders
    r"Clinical scenario for \[.*?\]",
    r"Question about \[.*?\]",
    r"A \d+-year-old (?:male|female) presents? (?:to|with) \[.*?\]",
    r"\[Topic\]",
    r"\[Condition\]",
    r"\[Treatment\]",

    # Option placeholders
    r"Option [A-E](?:\s*\(Correct\))?$",
    r"^[A-E][\.\)]?\s*Option [A-E]",
    r"^[A-E][\.\)]?\s*\[.*?\]",
    r"^Answer choice [A-E]",

    # Explanation placeholders
    r"Explanation based on Australian guidelines for \[.*?\]",
    r"According to \[Guideline\]",
    r"The correct answer is based on \[Source\]",
    r"See \[Reference\] for details",

    # Generic content markers
    r"TODO:",
    r"PLACEHOLDER",
    r"TBD",
    r"FIXME",
    r"\[INSERT.*?\]",
]
```

**Validation Requirements**:
1. ✅ **MUST** scan ALL fields: `question_text`, `options`, `explanation`, `citation`
2. ✅ **MUST** reject MCQs matching ANY placeholder pattern
3. ✅ **MUST** log rejected MCQs with specific pattern match
4. ✅ **MUST** report rejection stats (e.g., "Rejected 1,046/1,613 placeholder MCQs")

#### 15.2 Database Schema Constraints (ENFORCED AT DB LEVEL)

**MCQ model MUST enforce content quality via database check constraints:**

```python
# backend/src/db/models.py - MCQ model
class MCQ(Base):
    __tablename__ = "mcqs"

    # ... existing fields ...

    # NEW: Content quality constraints (CHECK constraints)
    __table_args__ = (
        # Reject placeholder question text
        CheckConstraint(
            "question_text !~* 'Clinical scenario for \\[|Question about \\[|\\[Topic\\]|\\[Condition\\]'",
            name="check_no_placeholder_question_text"
        ),

        # Require minimum question length (real scenarios are ≥100 chars)
        CheckConstraint(
            "char_length(question_text) >= 100",
            name="check_question_min_length"
        ),

        # Require citation with real source (not "[Guideline]")
        CheckConstraint(
            "citation !~* '\\[Guideline\\]|\\[Reference\\]|\\[Source\\]' AND char_length(citation) >= 10",
            name="check_real_citation"
        ),

        # Require explanation with real content (≥50 chars)
        CheckConstraint(
            "explanation !~* 'Explanation based on.*?\\[|According to \\[' AND char_length(explanation) >= 50",
            name="check_real_explanation"
        ),
    )
```

**Migration Required**: Create Alembic migration to add these CHECK constraints.

#### 15.3 Data Loading Script Validation (MANDATORY)

**ALL data loading scripts (`load_*.py`, `generate_*.py`) MUST include comprehensive validation.**

**Example**: `scripts/load_all_data.py` (lines 54-63) - **INSUFFICIENT** (only checks "Option A"/"Option B")

**REQUIRED**: Comprehensive validation function

```python
def validate_mcq_content(mcq_data: Dict) -> tuple[bool, str]:
    """
    Validate MCQ content for placeholder patterns.

    Returns:
        (is_valid, rejection_reason)
    """
    # Check question text
    question_text = mcq_data.get('question', {}).get('scenario', '') + ' ' + mcq_data.get('question', {}).get('stem', '')
    if len(question_text.strip()) < 100:
        return False, "Question text too short (<100 chars)"

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, question_text, re.IGNORECASE):
            return False, f"Placeholder pattern in question: {pattern}"

    # Check options
    options = mcq_data.get('question', {}).get('options', {})
    for key, value in options.items():
        if re.match(r"^Option [A-E]", str(value), re.IGNORECASE):
            return False, f"Placeholder option: {key} = '{value}'"

    # Check explanation
    explanation = mcq_data.get('explanation', '')
    if isinstance(explanation, dict):
        explanation = explanation.get('text', '')

    if len(explanation.strip()) < 50:
        return False, "Explanation too short (<50 chars)"

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, explanation, re.IGNORECASE):
            return False, f"Placeholder pattern in explanation: {pattern}"

    # Check citation
    citation = mcq_data.get('references', [])
    if not citation or len(citation) == 0:
        return False, "No citations provided"

    # Check for placeholder citations
    citation_text = json.dumps(citation)
    if re.search(r"\[Guideline\]|\[Reference\]|\[Source\]", citation_text):
        return False, "Placeholder citation detected"

    return True, "Valid"

# USAGE in load_mcqs_from_file():
for mcq_data in mcqs_data:
    is_valid, reason = validate_mcq_content(mcq_data)
    if not is_valid:
        logger.warning(f"REJECTED MCQ {mcq_data.get('id')}: {reason}")
        skipped_count += 1
        continue
    # ... proceed to load ...
```

#### 15.4 Pre-Commit Hook for MCQ Validation (MANDATORY)

**Create**: `~/.claude/hooks/skillbridge/mcq-content-validation.sh`

```bash
#!/bin/bash
# MCQ Content Validation Hook
# Triggers: On Write/Edit of *.json files in data/mcqs/

CHANGED_FILE="$1"

# Only validate MCQ JSON files
if [[ ! "$CHANGED_FILE" =~ data/mcqs/.*\.json$ ]]; then
    exit 0
fi

echo "🔍 Validating MCQ content in $CHANGED_FILE..."

# Run validation script
cd /home/dev/Development/irStudy
source backend/venv/bin/activate

python3 - <<EOF
import json
import re
import sys

PLACEHOLDER_PATTERNS = [
    r"Clinical scenario for \[.*?\]",
    r"Option [A-E](?:\s*\(Correct\))?$",
    r"Explanation based on Australian guidelines for \[.*?\]",
    r"\[Topic\]", r"\[Condition\]", r"\[Guideline\]",
]

with open("$CHANGED_FILE", "r", encoding="utf-8") as f:
    data = json.load(f)

mcqs = data.get("mcqs", data) if isinstance(data, dict) else data
placeholder_count = 0

for mcq in mcqs:
    question_text = json.dumps(mcq.get("question", {}))
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, question_text, re.IGNORECASE):
            placeholder_count += 1
            break

if placeholder_count > 0:
    print(f"❌ REJECTED: {placeholder_count}/{len(mcqs)} MCQs contain placeholder content")
    print(f"   File: $CHANGED_FILE")
    print(f"   Fix: Regenerate MCQs using Claude API (NOT local LLMs)")
    sys.exit(2)  # Exit code 2 = validation failed

print(f"✅ PASSED: All {len(mcqs)} MCQs validated (no placeholder content)")
sys.exit(0)
EOF

EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
    echo ""
    echo "⚠️  MCQ VALIDATION FAILED"
    echo "   Placeholder content detected in MCQ data"
    echo "   This file will NOT be committed until fixed"
    exit 2
fi

exit 0
```

**Installation**:
```bash
mkdir -p ~/.claude/hooks/skillbridge
chmod +x ~/.claude/hooks/skillbridge/mcq-content-validation.sh
```

#### 15.5 Ralph PRD Standards for MCQ Generation (MANDATORY)

**ALL PRDs creating MCQs MUST include these quality gates:**

```markdown
## 4. Quality Gates (MANDATORY - MCQ Content Validation)

### 4.1 Placeholder Content Detection (ZERO TOLERANCE)

**BEFORE** inserting ANY MCQs to database:

bash
cd /home/dev/Development/irStudy
source backend/venv/bin/activate

# Run comprehensive validation
python3 scripts/validate_mcq_content.py data/mcqs/[YOUR_FILE].json

# Expected output:
# ✅ PASSED: 100/100 MCQs validated (0 placeholders detected)

# FAILURE output (DO NOT PROCEED):
# ❌ FAILED: 45/100 MCQs contain placeholder content
#    - 23 MCQs: Placeholder options ("Option A", "Option B")
#    - 15 MCQs: Placeholder question text ("Clinical scenario for [Topic]")
#    - 7 MCQs: Placeholder explanations ("Explanation based on... [Guideline]")
# REQUIRED ACTION: Regenerate failed MCQs using Claude API


### 4.2 LLM Selection Validation (MANDATORY)

**CRITICAL**: Local LLMs (Ollama 7B models) CANNOT generate quality MCQs.

bash
# ✅ CORRECT: Use Claude API for MCQ generation
export ANTHROPIC_API_KEY=$(cat ~/.anthropic_api_key)
python3 scripts/generate_mcqs_claude.py --specialty cardiology --count 100

# ❌ WRONG: Local LLMs produce placeholder content (64.8% failure rate)
# DO NOT USE: generate_mcqs_from_templates_ollama.py
# DO NOT USE: generate_mcqs_ollama_simple.py


### 4.3 Database Insertion Validation

**AFTER** inserting MCQs:

bash
# Check database for placeholder content
psql $DATABASE_URL -c "
SELECT COUNT(*) as placeholder_count
FROM mcqs
WHERE question_text ~* 'Clinical scenario for \[|Option [A-E]$|Explanation based on.*\['
"

# Expected: placeholder_count = 0
# If > 0: ROLLBACK transaction and regenerate MCQs
```

#### 15.6 Agent-Specific Constraints (medical-content-quality Skill)

**File**: `.claude/skills/medical-content-quality.md`

**Add to skill prompt**:

```markdown
## MCQ Content Quality Standards (ZERO TOLERANCE)

When generating or validating MCQs, you MUST:

### ❌ NEVER ALLOWED (Auto-Reject):
- Placeholder question text: "Clinical scenario for [Topic]"
- Placeholder options: "Option A", "Option B (Correct)", etc.
- Placeholder explanations: "Explanation based on Australian guidelines for [Topic]"
- Placeholder citations: "[Guideline]", "[Reference]", "[Source]"
- Questions shorter than 100 characters
- Explanations shorter than 50 characters
- Missing or empty citations

### ✅ REQUIRED (Enforce):
- Real clinical scenarios with patient demographics, symptoms, examination findings
- Specific answer options describing actual treatments/diagnoses/management steps
- Evidence-based explanations citing real Australian sources (eTG, AMH, AHPRA)
- Minimum 3 RAG citations with qdrant_point_id for traceability

### Validation Checklist (Run BEFORE Returning):

- [ ] Question text ≥100 chars with real clinical scenario
- [ ] ALL options are specific medical content (no "Option A" patterns)
- [ ] Explanation ≥50 chars with clinical reasoning
- [ ] ≥3 real citations (eTG, AMH, AHPRA, Talley & O'Connor, etc.)
- [ ] No forbidden placeholder patterns detected (regex scan)
- [ ] Australian terminology used (paracetamol, GP, salbutamol)

**If ANY validation fails**: REGENERATE the MCQ. DO NOT return placeholder content.
```

#### 15.7 Enforcement Summary

**Before this constraint**:
- ❌ 1,046/1,613 MCQs (64.8%) were placeholders
- ❌ No database constraints preventing bad data
- ❌ Weak validation in data loaders
- ❌ No pre-commit hooks

**After this constraint**:
- ✅ Zero-tolerance placeholder detection (15 regex patterns)
- ✅ Database CHECK constraints block bad data at schema level
- ✅ Comprehensive validation in all data loading scripts
- ✅ Pre-commit hook prevents placeholder content from being saved
- ✅ Ralph PRD standards enforce Claude API usage (not local LLMs)
- ✅ Agent skills include explicit placeholder rejection rules

**Impact**: Prevents 64.8% data quality failures from recurring.

---

## Recent Issues & Fixes

### 2026-05-27: MCQ Placeholder Content Crisis (CRITICAL DATA QUALITY FIX)
**Issue**: 1,046/1,613 MCQs (64.8%) were dummy/placeholder content in production database
**Affected**: All specialties (General Practice: 406, Gastroenterology: 184, Cardiology: 126, etc.)
**Root Causes**:
1. Weak validation in `load_all_data.py` (only checked "Option A"/"Option B", missed other patterns)
2. No database schema constraints (MCQ model allowed any text content)
3. Local LLM usage (Ollama 7B models generated placeholder content, not real MCQs)
4. No pre-commit validation hooks
5. Missing agent constraints in medical-content-quality skill

**Fix Applied**:
- Created Constraint #15 (MCQ Content Validation) with:
  - 15 comprehensive placeholder detection regex patterns
  - Database CHECK constraints (question_text ≥100 chars, real citations, etc.)
  - Mandatory validation function for all data loading scripts
  - Pre-commit hook for MCQ JSON file validation
  - Ralph PRD standards mandating Claude API (not local LLMs)
  - Agent skill constraints with zero-tolerance policy

**Prevention**:
- ALL MCQ generation MUST use Claude API (see constraint 4-llm-integration.md)
- ALL data loading scripts MUST run `validate_mcq_content()` before insertion
- Database schema enforces quality at constraint level
- Pre-commit hooks auto-reject placeholder content
- Zero-tolerance policy: ANY placeholder pattern = auto-reject

**Documentation**: See Constraint #15 (MCQ Content Validation) above

### 2026-02-02: Docker Python 3.12 Compatibility (CRITICAL FIX)
**Issue**: PyTorch 2.1.2 incompatible with Python 3.12 causing Docker build failures
**Services Affected**: flower, celery-worker, celery-beat, backend
**Error**: `ERROR: Could not find a version that satisfies the requirement torch==2.1.2`
**Root Cause**: PyTorch 2.1.x only supports Python 3.8-3.11; Docker uses Python 3.12
**Fix Applied**:
- Updated `backend/requirements.txt` lines 47-50
- torch==2.1.2 → torch==2.10.0 (Python 3.12 compatible)
- sentence-transformers==2.3.1 → sentence-transformers==3.3.1
- transformers==4.37.0 → transformers==4.48.0
**Documentation**: See `constraints/10-anti-patterns.md` section 10.8
**Prevention**: Always verify Python version compatibility before pinning ML packages

### 2026-04-06: Playwright E2E Testing Patterns (CRITICAL)
**Issue**: Test authentication failures and API endpoint configuration issues
**Tests Affected**: `testing/playwright/tests/integration/osce/osce-video-sample.spec.ts`

**Key Learnings**:

1. **E2E Test User Setup** (scripts/create_test_users.py:21)
   - MUST create test users in database before running E2E tests
   - Script is idempotent (updates existing users instead of failing)
   - Uses correct `hash_password()` function from `src.auth.security` (NOT `get_password_hash`)
   - Creates 5 test users: student@test.com, educator@test.com, admin@test.com, inactive@test.com, unverified@test.com

2. **Backend Startup for E2E Tests** (backend/.env:1)
   - MUST load .env before starting: `set -a && source .env && set +a && uvicorn src.main:app --reload --port 8001`
   - Failing to load .env causes: `ValueError: Database password not found`
   - Port 8001 required (frontend expects backend on http://localhost:8001)

3. **Test Authentication Pattern** (testing/playwright/utils/helpers/login.ts:25)
   - ALL protected page tests MUST call `await login(page, TEST_USERS.STUDENT)` in beforeEach
   - Login helper waits for redirect to `/dashboard` (10s timeout)
   - Login fills email/password with blur events to trigger validation before submit

4. **API Endpoint Path Issues** (DISCOVERED)
   - **CRITICAL BUG**: Frontend is requesting `/api/v1/api/v1/...` (doubled `/api/v1/`)
   - Affected endpoints: `/permissions/me`, `/progress/dashboard/emr`, `/emr/sessions`, etc.
   - All return `404 Not Found` causing dashboard redirect loop
   - **Root Cause**: Likely hardcoded `/api/v1/` prefix in frontend API client with duplicate base URL
   - **Impact**: Login succeeds but dashboard fails to load, tests stuck on `/login`

5. **Test Debugging Commands**:
   ```bash
   # Create test users
   cd /home/dev/Development/irStudy
   export DATABASE_URL='postgresql://postgres:3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH@localhost:5433/irstudy_medical'
   source backend/venv/bin/activate && python scripts/create_test_users.py

   # Start backend with env vars
   cd backend && source venv/bin/activate && set -a && source .env && set +a && uvicorn src.main:app --reload --port 8001

   # Run tests in headed mode (visible browser)
   cd testing/playwright && npx playwright test tests/integration/osce/osce-video-sample.spec.ts --headed --project=chromium --retries=0

   # Test backend login endpoint directly
   curl -X POST http://localhost:8001/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"student@test.com","password":"Student123!@#"}'
   ```

**Fixes Applied** (2026-04-06):
- [x] Fixed frontend API client paths (removed doubled `/api/v1/`)
  - frontend/src/api/permissions.ts:26-27, 39, 48
  - frontend/src/hooks/useEMRDashboardData.ts:118, 132, 153, 172
  - frontend/src/pages/emr/CernerEMRPage.tsx:59, 69
  - frontend/src/pages/emr/EpicEMRPage.tsx:59, 69
  - frontend/src/pages/emr/StartEMRSessionPage.tsx:38
  - frontend/src/hooks/useAutoSave.ts:89
- [x] Verified TypeScript compilation (0 errors)

**Remaining Fixes**:
- [x] Implement missing backend endpoints: `/permissions/me`, `/progress/dashboard/emr`, etc. (PRDs created - see below)
- [ ] Add endpoint existence checks to E2E test setup
- [ ] Document E2E test prerequisites in testing/playwright/README.md
- [ ] Implement OSCE video page route (`/osces/:id`)

**Prevention**:
- ALWAYS run E2E tests after backend API changes
- ALWAYS check backend logs for 404 errors during test failures
- ALWAYS verify frontend API client configuration matches backend routes

---

### 2026-04-06: EMR Backend Missing Endpoints - PRDs Created (T-RALPH v2.1)

**Issue**: Frontend dashboard requests 3 EMR endpoints that don't exist, causing 404 errors:
- GET `/api/v1/progress/dashboard/emr` - EMR metrics (404 Not Found)
- GET `/api/v1/progress/weekly-trends/unified` - Unified trends (404 Not Found)
- GET `/api/v1/progress/weak-areas/emr` - Weak areas (404 Not Found)

**Root Causes Discovered**:
1. **Duplicate routers**: Two EMR router implementations (emr_sessions.py + emr/sessions.py)
2. **Inline models**: EMR models defined in router files instead of models.py
3. **Missing endpoints**: 3 dashboard endpoints never implemented
4. **Field name mismatch**: Backend uses `full_name`, frontend expects `name`
5. **Ignored query params**: Frontend passes `sort_by`/`sort_order` but backend ignores them

**Solution**: 5-Phase Implementation Plan (T-RALPH v2.1 with Multi-Agent Coordination)

**PRD Files Created** (All located in `/home/dev/Development/irStudy/`):

| Phase | PRD File | Scope | Time | Tests | Agents |
|-------|----------|-------|------|-------|--------|
| **1** | `PRD-EMR-001-MODELS-MIGRATION.md` | Move 6 EMR models to models.py | 3-4h | 12 | python-backend-developer + security-compliance-expert |
| **2** | `PRD-EMR-002-CONSOLIDATE-ROUTERS.md` | Delete duplicate emr_sessions.py router | 1-2h | 6 | python-backend-developer |
| **3** | `PRD-EMR-003-DASHBOARD-ENDPOINTS.md` | Implement 3 missing dashboard endpoints | 4-5h | 9 | python-backend-developer + testing-qa-expert |
| **4** | `PRD-EMR-004-PATIENT-ALIAS.md` | Add name/full_name field aliases | 30m | 3 | python-backend-developer |
| **5** | `PRD-EMR-005-QUERY-PARAMS.md` | Add sort_by/sort_order to list endpoint | 30m | 3 | python-backend-developer + security-compliance-expert |

**Total**: 8.5-10 hours, 33 tests, 6 agents (3 primary + 3 validation)

**Execution Plan**: See `EMR-IMPLEMENTATION-EXECUTION-PLAN.md` for detailed multi-agent coordination workflow

**Key Features**:
- ✅ T-RALPH v2.1 format (Test-First Development)
- ✅ Complete test code embedded in PRDs (copy-paste ready)
- ✅ Complete implementation code (no placeholders)
- ✅ Multi-agent quality gates (Security, QA, Performance)
- ✅ Sequential dependencies enforced (Phase 1 blocks 2-5)

**Expected Outcomes After Implementation**:
- ✅ Frontend dashboard loads without 404 errors
- ✅ EMR metrics, trends, and weak areas display correctly
- ✅ Recent sessions sorted newest-first (better UX)
- ✅ Patient names display correctly (backward compatibility)
- ✅ Clean codebase (no duplicate routers, centralized models)
- ✅ 100% test pass rate (33 tests)
- ✅ Performance targets met (<300ms p95)
- ✅ Security validated (0 hardcoded credentials, 0 SQL injection)

**Implementation Status**: READY FOR EXECUTION (PRDs complete, awaiting manual or Ralph loop execution)

**Next Steps**:
1. Execute Phase 1 (Models Migration) - CRITICAL, blocks all other phases
2. Execute Phase 2 (Router Consolidation) - CRITICAL, blocks Phase 3-5
3. Execute Phase 3 (Dashboard Endpoints) - CRITICAL, fixes 404 errors
4. Execute Phase 4 (Patient Aliases) - Can run parallel with Phase 5
5. Execute Phase 5 (Query Parameters) - Can run parallel with Phase 4

**Validation Commands** (After all phases complete):
```bash
# Run all 33 tests
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
pytest tests/test_emr_*.py -v
# Expected: 33 passed in X.XXs

# Test dashboard endpoints
TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"Student123!@#"}' \
  | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/v1/progress/dashboard/emr
# Expected: 200 OK with EMR metrics JSON

# Verify frontend dashboard
cd /home/dev/Development/irStudy/frontend
npm run dev
# Open http://localhost:5173/dashboard
# Expected: Dashboard loads without 404 errors
```

---
