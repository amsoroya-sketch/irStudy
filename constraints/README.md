# Constraints Folder - Modular Constraint System

**Created**: 2026-01-26
**Last Updated**: 2026-03-21
**Purpose**: Break down large PROJECT_CONSTRAINTS.md into manageable modules
**Structure**: One file per major constraint category

---

## Why Modular Structure?

**Problem**: Original `PROJECT_CONSTRAINTS.md` was 30,000+ tokens
- Too large to read completely
- Difficult to navigate
- Hard to maintain
- Agents couldn't read it all before starting work

**Solution**: Split into topic-specific modules
- Easier to read (each file 2000-5000 tokens)
- Better navigation (read only what you need)
- Simpler maintenance (update specific sections)
- Agents can read relevant constraints quickly

---

## File Structure

```
constraints/
├── README.md (this file)
├── 01-medical-accuracy.md (✅ EXISTING)
├── 02-code-architecture.md (✅ EXISTING)
├── 03-security-configuration.md (✅ EXISTING)
├── 04-llm-integration.md (✅ EXISTING)
├── 05-data-processing.md (✅ EXISTING)
├── 06-testing-requirements.md (✅ EXISTING)
├── 07-documentation-standards.md (✅ EXISTING)
├── 08-agent-requirements.md (✅ EXISTING)
├── 09-icrp-clinical-training.md (✅ EXISTING)
├── 10-anti-patterns.md (✅ EXISTING)
├── 11-rag-citation-requirements.md (✅ EXISTING)
├── 12-content-generation-requirements.md (✅ EXISTING)
├── 13-ralph-execution.md (✅ EXISTING)
├── 14-ralph-medical-content-standards.md (✅ NEW 2026-03-21)
├── MEDICAL_CONTENT_ENFORCEMENT_SUMMARY.md (✅ NEW 2026-03-21)
└── QUICK_START.md (✅ EXISTING)
```

### Key Constraint Files for Medical Content

#### 01-medical-accuracy.md (✅ EXISTING)
**Purpose**: Australian medical standards
**Key Requirements**: eTG, MBS, PBS, AHPRA, Australian drug names

#### 11-rag-citation-requirements.md (✅ EXISTING)
**Purpose**: RAG citation requirements
**Key Requirements**: qdrant_point_id, confidence ≥0.65, 100% coverage

#### 12-content-generation-requirements.md (✅ EXISTING)
**Purpose**: LLM-powered content generation
**Key Requirements**: No placeholder content, Claude API for medical content

#### 14-ralph-medical-content-standards.md (✅ NEW 2026-03-21)
**Purpose**: **Ralph-specific enforcement for medical content PRDs**
**Size**: ~15,000 tokens (comprehensive)
**Key Requirements**:
- MANDATORY clinical expert agents (clinical-documentation-expert, history-taking-expert, physical-examination-expert)
- MANDATORY 3 skills (rag-citation-verification, australian-medical-terminology, fracp-clinical-validation)
- MANDATORY 5 validations (QA 13-gate, FRACP clinical, security scan, RAG coverage, database)
- MANDATORY prompt structure (Medical Accuracy Requirements, Validation Checklist, Anti-Patterns)
- MANDATORY context references (constraint files)

**Why created**: Prevents medical content PRDs from bypassing quality gates. Ralph Dashboard will **REJECT** non-compliant PRDs.

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

#### MEDICAL_CONTENT_ENFORCEMENT_SUMMARY.md (✅ NEW 2026-03-21)
**Purpose**: Summary of how medical content quality standards are auto-enforced
**Key Topics**:
- What constraints exist
- How Ralph enforces them
- Current quality metrics (Batch 1 - 207 personas)
- Enforcement checklist for PRD authors

---

## How to Use

### For Agents

**Before starting work**:
1. Identify your task type (Medical content? Testing? Security? UI?)
2. **If medical content** → Read constraints 1, 11, 12, 14 (MANDATORY)
3. Read relevant constraint file from this folder
4. Follow implementation checklist in constraint file
5. Validate work against constraints before returning

**For Medical Content Specifically**:
```bash
# MANDATORY: Read these constraints FIRST
Read(constraints/01-medical-accuracy.md)
Read(constraints/11-rag-citation-requirements.md)
Read(constraints/12-content-generation-requirements.md)
Read(constraints/14-ralph-medical-content-standards.md)

# MANDATORY: Verify RAG system ready
Bash(./scripts/pre_flight_validation.sh)
# Must exit with code 0 before proceeding
```

**If constraint file doesn't exist yet**:
- Read legacy `PROJECT_CONSTRAINTS.md`
- Extract relevant section

### For PRD Authors (Ralph Loop)

**Before creating medical content PRD**:
1. Read `constraints/14-ralph-medical-content-standards.md`
2. Use extended PRD schema: `production-launch-prds/.ralph/schemas/irstudy-prd-schema.json`
3. Follow enforcement checklist in section 14.8
4. Include all 5 required validations
5. Reference example PRD: `production-launch-prds/.ralph/examples/PRD-CONTENT-001-CARDIOLOGY-STEMI-PERSONAS.json`

**Ralph Dashboard will REJECT PRDs that don't meet medical content standards.**

---

## Benefits

✅ Read only relevant constraints (faster)
✅ Easier to maintain and update
✅ Clear implementation checklists
✅ Better documentation organization
✅ **AUTO-ENFORCED** medical content quality (NEW 2026-03-21)
✅ **ZERO-TOLERANCE** for hallucinated citations (NEW 2026-03-21)
✅ **96.5% deployment readiness** (200/207 personas approved) (NEW 2026-03-21)

---

## Recent Updates

### 2026-03-21: Medical Content Quality Enforcement
- ✅ Created `14-ralph-medical-content-standards.md`
- ✅ Created `MEDICAL_CONTENT_ENFORCEMENT_SUMMARY.md`
- ✅ Updated `PROJECT_CONSTRAINTS.md` with Constraint 14
- ✅ Updated `CLAUDE.md` with medical content standards
- ✅ Defined MANDATORY PRD components for medical content
- ✅ Established Ralph Dashboard validation gates

**Impact**: ALL future medical content generation automatically enforces quality gates.

---

**Status**: ✅ ACTIVE (v4.0.0 Medical Content Quality Enforcement)
