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

## Recent Issues & Fixes

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

---
