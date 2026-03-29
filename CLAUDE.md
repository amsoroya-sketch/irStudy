## Medical Content Quality Standards (MANDATORY)

### Critical Requirements
- **100% citation and QA validation** - ALL medical content MUST pass 13-gate QA validation + FRACP clinical validation
- **RAG citations required** - Every clinical fact MUST have RAG citation with qdrant_point_id, confidence ≥0.65
- **Australian medical standards** - Use eTG, MBS, PBS, AHPRA (NOT US sources)
- **Zero hallucinations** - All citations verified against Qdrant database
- **No placeholder content** - 100% real clinical content generated via LLM (Claude API)

### Before Starting ANY Medical Content Work
1. **Read constraints FIRST**:
   - `constraints/01-medical-accuracy.md` - Australian medical standards
   - `constraints/11-rag-citation-requirements.md` - RAG citation requirements
   - `constraints/12-content-generation-requirements.md` - Content generation requirements
   - `constraints/14-ralph-medical-content-standards.md` - Ralph medical content standards

2. **Verify RAG system ready**:
   ```bash
   ./scripts/pre_flight_validation.sh
   # Must exit with code 0 before proceeding
   ```

3. **Use clinical expert agents** (NEVER use general-purpose):
   - `.claude/agents/clinical-documentation-expert.md`
   - `.claude/agents/history-taking-expert.md`
   - `.claude/agents/physical-examination-expert.md`

### Quality Gates (ALL MUST PASS)
- ✅ Gate 1: JSON Compliance (17 required fields)
- ✅ Gate 2: RAG Citations >0.65 (ZERO tolerance for hallucinations)
- ✅ Gate 3: FRACP Reviews ≥8.0/10 (specialist clinical validation)
- ✅ Gate 4: Clinical Accuracy (no dangerous medications, correct dosing)
- ✅ Gate 5: Australian Context (paracetamol NOT acetaminophen, MBS/PBS)
- ✅ Gate 6-7: Difficulty/Specialty Valid
- ✅ Gate 8-10: Cultural Safety (Aboriginal/TSI, LGBTQIA+, CALD)
- ✅ Gate 11-12: Security (zero credentials, zero PHI)
- ✅ Gate 13: Educational Alignment (9-step history, SOCRATES, red flags)

### Current Performance (Batch 1 - 207 Personas)
- ✅ 100% RAG citation coverage (3,726 citations with qdrant_point_id)
- ✅ 96.5% deployment readiness (200/207 approved without manual intervention)
- ✅ 0 hallucinated citations (100% verified against Qdrant)
- ✅ 66.1% Australian sources (exceeds 60% target)

---

## Ralph PRD Standards (CRITICAL - ALWAYS FOLLOW)

**Master Location**: `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/`

**ALWAYS Read Standards First Before Creating PRDs**:
- Read: `ralph-dashboard/docs/specifications/prd-standards/PRD_STANDARDS_V2_T-RALPH.md`
- Read: `ralph-dashboard/docs/specifications/prd-standards/README.md`
- Follow T-RALPH structure (Test-First Development)

**Structure**: T-RALPH v2.1 (MANDATORY for NEW PRDs)
- **T** - TESTS: ALL test code BEFORE implementation (embedded in PRD, not separate files)
- **R** - REQUEST: User story, problem statement, success criteria
- **A** - ARCHITECTURE: System design, database schema, API endpoints
- **L** - LOOP: Iterative development with TDD workflow (RED → GREEN → REFACTOR per phase)
- **P** - PLAN: File-by-file implementation with full code examples
- **H** - HANDOFF: Test results summary, coverage reports, validation

**Version**: 2.1 (includes PROJECT_CONSTRAINTS.md integration - MANDATORY)
**Date**: 2026-03-29

**Key Requirements**:
- All agents MUST read `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md` BEFORE starting work
- All agents MUST read T section tests BEFORE implementation
- TDD workflow enforced: RED (tests fail) → GREEN (tests pass) → REFACTOR (maintain 100% pass rate)
- Validation checklist required in L section for each phase

**Legacy PRDs**: PRD-P1-004, PRD-P1-006, PRD-P1-007 use R-A-L-P-H format (pre-v2.1) - kept for historical reference

---

## Project-Specific Rules

- Always use Agent OS expert agents with all constraints and framework
- Don't use ICRP references - use **AMC Clinical Examination** standards
- Read `constraints/README.md` for constraint system overview
- Our preference: **AMC Part 1 and Clinical Exam for Australia**
- Don't ask for permission in same folder in this project
- Don't ask for permission for scripts and tasks