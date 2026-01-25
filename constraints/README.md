# Project Constraints & Standards

**Project**: irStudy - ICRP Medical Education AI System
**Version**: 2.0.0
**Last Updated**: 2025-12-18
**Purpose**: Standards and constraints for implementing 46 medical AI agents + ICRP clinical preparation
**Critical**: ALL agents MUST read this file BEFORE starting any work

---

## About This Directory

This directory contains the modular project constraints and standards documentation. The original monolithic `PROJECT_CONSTRAINTS.md` (2,908 lines) has been split into focused, topic-specific files for easier navigation and maintenance.

---

## Quick Navigation

### Core Standards

1. **[Medical Accuracy Standards](01-medical-accuracy.md)** (218 lines)
   - Australian medical context (eTG, PBS, AHPRA standards)
   - Australian spelling & terminology (paediatric, anaesthesia)
   - Clinical accuracy requirements (drug dosages, red flags)
   - Citation requirements with RAG verification

2. **[Code Architecture & Patterns](02-code-architecture.md)** (334 lines)
   - BaseAgent inheritance pattern (MANDATORY)
   - Project structure & file organization
   - Multi-agent communication patterns
   - Workflow orchestration examples

3. **[Security & Configuration](03-security-configuration.md)** (152 lines)
   - Environment variables (ZERO hardcoded secrets)
   - Configuration management patterns
   - Security best practices
   - Sensitive data handling

### Integration & Processing

4. **[LLM Integration Patterns](04-llm-integration.md)** (287 lines)
   - OllamaClient usage (MANDATORY)
   - Prompt engineering standards
   - Token management (4K-8K limits)
   - Fallback strategies & error handling

5. **[Data Processing Standards](05-data-processing.md)** (283 lines)
   - JSON file handling (UTF-8 encoding)
   - Progress tracking (tqdm)
   - Batch processing patterns
   - File path management (pathlib.Path)

### Quality Assurance

6. **[Testing Requirements](06-testing-requirements.md)** (466 lines)
   - Unit testing (80%+ coverage target)
   - Integration testing
   - Medical accuracy validation
   - Performance benchmarking

7. **[Documentation Standards](07-documentation-standards.md)** (361 lines)
   - Docstring format (Google-style)
   - Type hints (MANDATORY)
   - README templates
   - API documentation (OpenAPI/Swagger)

### Agent & Domain Specific

8. **[Agent-Specific Requirements](08-agent-requirements.md)** (158 lines)
   - Medical Expert Agents (MED-XXX)
   - Development Agents (DEV-XXX)
   - AI/Data Science Agents (AI-XXX)
   - Testing & QA Agents (QA-XXX)
   - Documentation Agents (DOC-XXX)
   - Project Management Agents (PM-XXX)

9. **[ICRP Clinical Training Standards](09-icrp-clinical-training.md)** (151 lines)
   - History taking structure (9-step system)
   - Physical examination protocols
   - OSCE station requirements
   - Australian clinical context

### Anti-Patterns & Warnings

10. **[Anti-Patterns (What NOT to Do)](10-anti-patterns.md)** (169 lines)
    - Security anti-patterns (hardcoded credentials)
    - Medical accuracy violations
    - Code quality issues
    - Common mistakes to avoid

### RAG & Validation Systems

11. **[RAG Citation Requirements](11-rag-citation-requirements.md)** (MANDATORY before content generation)
    - Pre-flight validation checklist (ZERO TOLERANCE for "Unknown" citations)
    - RAG database metadata standards (title, author, year, page)
    - Data pipeline quality gates (PDF → Chunking → Embedding → Qdrant)
    - Incremental validation (fail-fast on first invalid citation)
    - Week 1 mistake documentation & prevention system
    - Remediation process & QA-003 integration

---

## Project Context

### Target Audience

**ICRP Candidates (International Medical Graduates)**

- **Background**: Qualified doctors from overseas seeking Australian medical registration
- **Goal**: Pass AMC Clinical Exam (OSCE format) to practice medicine in Australia
- **Timeline**: March 2 - May 22, 2026 (Young District Hospital ICRP program)
- **Location**: NSW, Australia
- **Exam Type**: AMC Clinical Exam - 16 OSCE stations × 8 minutes each

**Key Needs:**
- Australian medical practice standards and terminology
- NSW Health protocols and guidelines
- Clinical examination techniques (Australian context)
- Case-based scenario practice
- Red flag recognition and emergency management
- Communication skills for Australian healthcare system

### Exam Context - AMC Clinical Exam (OSCE)

**Format**: 16 stations × 8 minutes each

**Content Distribution:**
- History taking (40%)
- Physical examination (30%)
- Diagnosis & management (20%)
- Communication skills (10%)

**Key Skills Tested:**
- Clinical reasoning with Australian context
- Physical examination techniques (proper consent, draping)
- Red flag recognition (emergency identification)
- Patient communication (Australian cultural norms)
- Australian medical system navigation (GP referrals, Medicare, PBS)

**Common Station Types:**
- History taking (chest pain, abdominal pain, shortness of breath)
- Cardiovascular examination
- Respiratory examination
- Abdominal examination
- Neurological examination
- Breaking bad news
- Informed consent discussions
- Medication counseling (PBS medications)

### Clinical Context - Young Hospital ICRP Program

**Program Details:**
- **Location**: Young District Hospital, NSW, Australia
- **Duration**: 12 weeks (March 2 - May 22, 2026)
- **Supervision**: Senior medical staff (registrars, consultants)
- **Rotations**: Emergency Department, General Medicine, Surgery, GP clinics
- **Goal**: Prepare candidates for AMC Clinical Exam through supervised practice

**Clinical Focus:**
- Common presentations: chest pain, abdominal pain, SOB, headache, fever
- Emergency medicine scenarios: sepsis, ACS, stroke, trauma
- Chronic disease management: diabetes, hypertension, COPD, heart failure
- Preventive health: cancer screening, cardiovascular risk assessment, immunization
- Aboriginal & Torres Strait Islander health considerations

### Geographic Context - NSW Health System

**Healthcare Structure:**

**Primary Care:**
- GP clinics (bulk-billed or private)
- Aboriginal Medical Services (AMS)
- Community health centers

**Emergency Care:**
- Emergency Departments (public hospitals)
- Triage system (categories 1-5)
- Ambulance service (call 000)

**Specialty Care:**
- Referral via GP (gatekeeping model)
- Public hospital outpatient clinics
- Private specialists

**Medications:**
- PBS (Pharmaceutical Benefits Scheme) - subsidized medications
- Authority prescriptions for restricted PBS medications
- TGA (Therapeutic Goods Administration) approval required

**Guidelines:**
- NSW Health Clinical Practice Guidelines
- Therapeutic Guidelines (eTG) - national standards
- AMH (Australian Medicines Handbook)

### Timeline & Milestones

**Current Phase**: Development (December 2025)

**Preparation Phase** (December 2025 - February 2026):
- Develop 46-agent AI system
- Create MCQ question bank (1000+ questions)
- Build OSCE practice platform
- Generate clinical vignettes and flashcards

**ICRP Phase** (March 2 - May 22, 2026):
- Candidates use platform for study
- Practice OSCE stations
- Review clinical guidelines
- Prepare for AMC Clinical Exam

**Target Outcomes:**
- 90%+ pass rate for AMC Clinical Exam
- Confident in Australian medical practice
- Ready for PGY1/resident positions in Australia

---

## How to Use This Documentation

### For New Agents

1. **Start here**: Read this README first
2. **Read your domain**: Navigate to relevant constraint files for your specialty
3. **Follow patterns**: Review example code in reference files
4. **Validate**: Use the validation checklist before submitting work

### For Existing Agents

1. **Quick reference**: Jump directly to specific constraint files
2. **Updates**: Check version history for recent changes
3. **Clarification**: Search for specific patterns or examples

### Finding What You Need

| What You Need | Where to Look |
|---------------|---------------|
| Australian medical standards | [01-medical-accuracy.md](01-medical-accuracy.md) |
| How to create an agent | [02-code-architecture.md](02-code-architecture.md) |
| Environment variables | [03-security-configuration.md](03-security-configuration.md) |
| LLM/AI model usage | [04-llm-integration.md](04-llm-integration.md) |
| File processing patterns | [05-data-processing.md](05-data-processing.md) |
| Testing strategies | [06-testing-requirements.md](06-testing-requirements.md) |
| Documentation format | [07-documentation-standards.md](07-documentation-standards.md) |
| Agent role requirements | [08-agent-requirements.md](08-agent-requirements.md) |
| OSCE/clinical exam prep | [09-icrp-clinical-training.md](09-icrp-clinical-training.md) |
| Common mistakes | [10-anti-patterns.md](10-anti-patterns.md) |

---

## Validation Checklist

**Before submitting ANY code, verify:**

### Code Quality
- [ ] Extended BaseAgent (if creating new agent)
- [ ] Used correct agent_id format (PREFIX-XXX)
- [ ] Type hints on all functions
- [ ] Docstrings (Google-style) on all functions
- [ ] Error handling (try-except with specific exceptions)
- [ ] Logging with self.logger (not print statements)

### Security
- [ ] NO hardcoded credentials or secrets
- [ ] NO sensitive data in logs
- [ ] Used environment variables for configuration
- [ ] Used pathlib.Path (not string paths)

### Medical Accuracy
- [ ] Australian spelling for medical terms (paediatric, anaesthesia)
- [ ] Australian drug names (paracetamol, adrenaline)
- [ ] Citations for all medical claims (Therapeutic Guidelines)
- [ ] Dosage units specified (mg, mcg, mL)
- [ ] Red flags identified for emergencies
- [ ] SI units used (mmol/L, not mg/dL)
- [ ] Australian emergency number (000, not 911)

### Testing
- [ ] Unit tests written (80%+ coverage target)
- [ ] Integration tests for multi-agent workflows
- [ ] Medical accuracy validation tests
- [ ] Performance benchmarks met
- [ ] All tests passing

### Data Processing
- [ ] JSON files use encoding='utf-8'
- [ ] Progress bars for long operations (tqdm)
- [ ] Batch processing for large datasets
- [ ] Proper error handling for file operations

### LLM Integration
- [ ] Used OllamaClient (not direct API calls)
- [ ] Handled token limits (4K-8K tokens)
- [ ] Implemented fallback strategy
- [ ] Used appropriate temperature for task type
- [ ] Structured prompts with clear requirements

### Documentation
- [ ] README.md created/updated
- [ ] Module docstring present
- [ ] Usage examples provided
- [ ] Performance metrics documented
- [ ] Dependencies listed

---

## References

### Key Project Files

**Agent Framework:**
- `/home/dev/Development/irStudy/src/agents/base_agent.py` - BaseAgent class (MUST READ)
- `/home/dev/Development/irStudy/src/agents/pm_001_project_manager.py` - PM example
- `/home/dev/Development/irStudy/src/agents/workflows/orchestration.py` - Multi-agent workflows

**LLM Integration:**
- `/home/dev/Development/irStudy/src/models/ollama_client.py` - LLM client (MUST READ)

**Data Processing:**
- `/home/dev/Development/irStudy/scripts/extract_pdfs.py` - PDF extraction example
- `/home/dev/Development/irStudy/scripts/chunk_medical_texts.py` - Text chunking example
- `/home/dev/Development/irStudy/scripts/generate_embeddings.py` - Embedding generation
- `/home/dev/Development/irStudy/scripts/index_qdrant.py` - Vector database indexing

**Documentation:**
- `/home/dev/Development/irStudy/docs/AGENT_SPECIFICATIONS.md` - Agent architecture
- `/home/dev/Development/irStudy/00_PROJECT_OVERVIEW.md` - Project overview

### External Australian Medical Standards

**Primary Guidelines:**
- [Therapeutic Guidelines](https://tg.org.au/) - Primary Australian treatment guidelines
- [Australian Medicines Handbook (AMH)](https://amhonline.amh.net.au/) - Drug information
- [PBS](https://www.pbs.gov.au/) - Pharmaceutical Benefits Scheme
- [AHPRA](https://www.ahpra.gov.au/) - Australian Health Practitioner Regulation Agency
- [AMC](https://www.amc.org.au/) - Australian Medical Council
- [NSW Health](https://www.health.nsw.gov.au/) - NSW Health guidelines

**Clinical Resources:**
- Harrison's Principles of Internal Medicine (21st Edition)
- Talley & O'Connor's Clinical Examination (8th Edition)
- Murtagh's General Practice (8th Edition)
- Oxford Handbook of Emergency Medicine (5th Edition)

### Coding Standards

**Python:**
- [PEP 8](https://pep8.org/) - Python style guide
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints - PEP 484](https://www.python.org/dev/peps/pep-0484/)

**TypeScript:**
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)

**Testing:**
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Playwright](https://playwright.dev/)

---

## Version History

- **2.0.0** (2025-12-18): Comprehensive multi-agent system standards
  - Added 10 sections covering all aspects of agent development
  - Medical accuracy standards (Australian context)
  - Code architecture patterns (BaseAgent)
  - Security & configuration (zero tolerance for hardcoded secrets)
  - LLM integration patterns (OllamaClient)
  - Data processing standards (JSON, tqdm, Path)
  - Testing requirements (80%+ coverage)
  - Documentation standards (Google-style docstrings)
  - Agent-specific requirements (46 agents across 6 categories)
  - Project-specific context (ICRP program details)
  - Anti-patterns (what NOT to do)
  - ICRP clinical training standards (preserved from v1.1)

- **1.1** (2025-12-14): Added AMC Clinical / OSCE Standards
- **1.0** (2025-12-13): Initial version (ICRP clinical training focus)

---

## Critical Reminders

### For ALL Agents:
1. **READ THIS FILE FIRST** before starting ANY work
2. **Follow Australian medical standards** - no exceptions
3. **Extend BaseAgent** - don't create agents from scratch
4. **NO hardcoded secrets** - zero tolerance policy
5. **Use OllamaClient** for LLM access - no direct API calls
6. **Write tests** - 80%+ coverage required
7. **Document everything** - docstrings, type hints, READMEs

### For Medical Agents (MED-XXX):
1. **Australian spelling** - paediatric, anaesthesia, anaemia
2. **Australian drug names** - paracetamol, adrenaline, salbutamol
3. **Cite Therapeutic Guidelines** - every medical claim
4. **Include dosage units** - mg, mcg, mL
5. **Identify red flags** - life-threatening conditions
6. **Use SI units** - mmol/L, not mg/dL
7. **Call 000 for emergencies** - not 911

### For Development Agents (DEV-XXX):
1. **Type hints** - on all functions
2. **Error handling** - specific exceptions, no bare except
3. **Logging** - structured logging, not print()
4. **Testing** - unit + integration tests
5. **Security** - follow OWASP Top 10
6. **Performance** - optimize for speed and memory
7. **Documentation** - OpenAPI for APIs, READMEs for modules

### For AI/Data Agents (AI-XXX):
1. **OllamaClient** - always use the client
2. **Token limits** - chunk if needed (4K-8K tokens)
3. **Fallback strategy** - multiple model attempts
4. **Progress bars** - tqdm for long operations
5. **Batch processing** - manage memory usage
6. **Performance tracking** - log metrics
7. **Quality validation** - test search relevance

### Questions?
If ANY constraint is unclear:
1. Read the relevant reference files listed above
2. Search for similar existing code in the project
3. Ask the Project Manager (PM-001) BEFORE proceeding
4. DO NOT guess or assume - clarity prevents mistakes

### Updates
This document will be updated as new patterns emerge. **Always use the latest version.**

---

**Last Updated**: 2025-12-18
**Version**: 2.0.0
**Maintained By**: PM-001 (Project Manager)
**Status**: **MANDATORY READING FOR ALL AGENTS**


## 12. Content Generation Requirements ✨ NEW
**File**: [`12-content-generation-requirements.md`](./12-content-generation-requirements.md)
**Added**: 2026-01-26
**Status**: ⚠️ **BLOCKING CONSTRAINT**

**Critical issue identified**: Commit `0d7de50` generated 938 items with placeholder text only.

**Mandatory**: ALL content generation MUST use LLM to create actual clinical content from RAG citations.

### Key Requirements
- LLM-powered generation (NOT template-only)
- Content substance validation (fail-fast)
- Pre-commit validation hooks
- Patient demographics required
- Australian guidelines integration

### Files Affected
- 938 items require regeneration (774 MCQs + 65 OSCEs + 65 Study Cards)

### Prevention Measures
- `scripts/validate_content_substance.sh` - validation script
- Pre-commit hook installation
- Quality gates (pre + post generation)

**See file for**: Complete implementation guide, validation checklist, prevention command prompts

---

## Agent OS Integration

### Medical Content Generator Agent

**File**: [`AGENT_MEDICAL_CONTENT_GENERATOR.md`](./AGENT_MEDICAL_CONTENT_GENERATOR.md)
**Agent Type**: `medical-content-generator`
**Status**: ✅ **ACTIVE**

Specialized expert agent for generating clinically accurate medical educational content using LLM-powered generation from RAG citations.

**Capabilities**:
- RAG citation retrieval and validation
- LLM-powered clinical content generation
- Content substance validation (anti-placeholder)
- Australian medical standards compliance
- Quality gates integration (pre + post generation)

**When to Use**:
- Generating MCQs, OSCEs, Study Cards
- Creating clinical vignettes
- Building medical quiz banks

**Prevents**: Placeholder content issue (commit 0d7de50 - 938 items)

**Integration**: Works with QA-003 and security-compliance-expert agents in multi-agent workflow

