# Medical Expert Agents - Agent OS Specifications

**Created**: 2026-03-15
**Purpose**: FRACP-equivalent medical expert agents for clinical content creation
**Framework**: Agent OS + Claude Skills
**Total Agents**: 13 (10 specialty experts + 1 physical exam + 1 cultural safety + 1 QA validator)

---

## Overview

This folder contains **13 agent specification files** that define FRACP-equivalent (Fellow of the Royal Australasian College of Physicians) expertise for generating 360 AI Patient Personas.

### Why Agent OS Framework?

**Agent OS** provides:
- **Structured expertise**: Each agent has specialty-specific knowledge (eTG sections, AMC competencies)
- **Learning loops**: Agents improve based on FRACP clinician feedback
- **Quality checklists**: Automated validation before returning work
- **RAG integration**: Citations from eTG/AMH medical guidelines
- **Critical error detection**: Agents flag unsafe clinical scenarios

**vs Traditional LLM prompting**:
- ❌ Generic medical knowledge → ✅ Specialty-specific eTG guidelines
- ❌ No quality control → ✅ Mandatory validation checklist
- ❌ No learning → ✅ Feedback loop from expert reviews
- ❌ Hallucination risk → ✅ RAG-grounded citations (>0.65 confidence)

---

## Agent Directory

| Agent ID | Agent Name | Specialty | Personas | eTG Sections | Batch |
|----------|------------|-----------|----------|--------------|-------|
| **MED-001** | cardiology-expert | Cardiology | 45 | 2.1-2.8 (CVS) | 1 |
| **MED-002** | emergency-expert | Emergency Medicine | 45 | Multiple (ACS, Stroke, Trauma) | 1 |
| **MED-003** | gp-expert | General Practice | 54 | Multiple (Chronic disease) | 1 |
| **MED-004** | pediatrics-expert | Pediatrics | 36 | 14.1-14.6 (Child health) | 2 |
| **MED-005** | obgyn-expert | Obstetrics & Gynaecology | 27 | 15.1-15.5 (Women's health) | 2 |
| **MED-006** | surgery-expert | Surgery | 27 | Multiple (Pre/post-op) | 2 |
| **MED-007** | psychiatry-expert | Psychiatry | 36 | 16.1-16.9 (Mental health) | 2 |
| **MED-008** | respiratory-expert | Respiratory Medicine | 36 | 3.1-3.7 (Respiratory) | 1 |
| **MED-009** | neurology-expert | Neurology | 27 | 12.1-12.5 (Neurology) | 1 |
| **MED-010** | infectious-diseases-expert | Infectious Diseases | 27 | 5.1-5.12 (Infections) | 2 |
| **MED-011** | cultural-safety-expert | Cultural Safety | 92 (integrated) | Aboriginal health guidelines | 4 |
| **MED-012** | physical-exam-expert | Physical Examination | 60 | AMC Clinical Examination | 3 |
| **QA-001** | medical-qa-validator | Quality Assurance | Reviews all 360 | All eTG sections | Final |

---

## Agent Specification Structure

Each agent file contains:

### 1. Expertise Profile
- FRACP-equivalent specialty training
- eTG sections with page numbers
- AMC competency domains covered
- Australian medical context (PBS, MBS)

### 2. Persona Creation Workflow
```
Step 1: RAG Retrieval (eTG/AMH guidelines)
  ↓
Step 2: LLM Generation (Claude 3.5 Sonnet, temp=0.7)
  ↓
Step 3: Validation (9-step history, RAG citations, clinical accuracy)
  ↓
Step 4: FRACP Review (≥2 clinicians)
  ↓
Step 5: Iteration (incorporate feedback)
```

### 3. Critical Error Detection Rules
- Wrong diagnosis (e.g., ACS as heartburn)
- Dangerous advice (e.g., NSAIDs in acute kidney injury)
- Contraindicated medications (e.g., beta-blockers in severe asthma)
- Missed red flags (e.g., anaphylaxis signs)

### 4. Quality Checklist
- [ ] Follows JSON template
- [ ] RAG citations >0.65 confidence
- [ ] 9-step history structure present
- [ ] Difficulty level appropriate (Easy/Medium/Hard)
- [ ] Australian medications (paracetamol, salbutamol, adrenaline)
- [ ] ≥2 FRACP clinician reviews

### 5. Learning Loop Structure
- Initial persona created
- FRACP feedback collected
- Patterns identified (e.g., "History questions too closed-ended")
- Agent updates system prompt
- Next persona incorporates learning

### 6. Anti-Patterns to Avoid
- ❌ Generic symptoms (e.g., "chest pain" without SOCRATES)
- ❌ US medical context (ER instead of ED, acetaminophen instead of paracetamol)
- ❌ Missing cultural context (e.g., Aboriginal health without NACCHO protocols)
- ❌ Stereotypical personas (e.g., Aboriginal patients only with diabetes)

---

## How to Use Agent Specifications

### For Project Managers

**When delegating PRD_CC_003 (History-Taking Personas)**:
```markdown
Task: Create 240 history-taking personas across 10 specialties

AGENTS TO USE:
- Read: clinical-content-prds/agents/MED-001-cardiology-expert.md
- Read: clinical-content-prds/agents/MED-002-emergency-expert.md
- Read: clinical-content-prds/agents/MED-003-gp-expert.md
- (... all 10 specialty agents)

DELEGATION STRATEGY:
1. Batch 1: Launch MED-001, MED-002, MED-003, MED-008, MED-009 in parallel
2. Wait for all 5 to complete
3. Run quality gate (scripts/quality-gate-clinical-content.sh 1)
4. Batch 2: Launch MED-004, MED-005, MED-006, MED-007, MED-010 in parallel
5. Wait for all 5 to complete
6. Run quality gate (scripts/quality-gate-clinical-content.sh 2)

VALIDATION:
- All agents MUST read agent spec file FIRST
- All agents MUST follow validation checklist
- PM runs quality gate after each batch
```

### For Agent Developers

**When creating new agent specification**:
1. Copy template from existing agent (e.g., MED-001-cardiology-expert.md)
2. Update expertise profile (eTG sections, AMC competencies)
3. Define critical error detection rules (specialty-specific)
4. Add learning loop examples (feedback → updated system prompt)
5. Document anti-patterns to avoid

### For Clinical Educators (FRACP Clinicians)

**When reviewing personas**:
1. Check clinical accuracy (diagnosis, management, red flags)
2. Check Australian medical context (PBS medications, MBS billing)
3. Check cultural safety (Aboriginal health protocols if applicable)
4. Provide feedback in structured format:
   - ✅ Clinically accurate? (Yes/No)
   - ✅ Appropriate difficulty? (Easy/Medium/Hard)
   - ✅ RAG citations correct? (Check eTG page numbers)
   - 📝 Feedback: (What to improve)

---

## Agent Coordination

### Batch 1 Execution (5 Agents Parallel)

**Agents**: MED-001, MED-002, MED-003, MED-008, MED-009
**Target**: 207 personas (45+45+54+36+27)
**Duration**: ~42 hours total (8-10 hours actual)

**Coordination**:
- All agents read constraints/4-llm-integration.md FIRST
- All agents use same RAG service (Qdrant vector DB)
- All agents follow same JSON template
- PM runs quality gate when all complete

### Batch 2 Execution (5 Agents Parallel)

**Agents**: MED-004, MED-005, MED-006, MED-007, MED-010
**Target**: 153 personas (36+27+27+36+27)
**Duration**: ~31 hours total (6-8 hours actual)

**Coordination**:
- Agents learn from Batch 1 FRACP feedback
- Updated system prompts based on patterns
- Same quality gate checklist

### Batch 3 Execution (1 Agent)

**Agent**: MED-012 (physical-exam-expert)
**Target**: 60 personas (CVS, Resp, Abdo, Neuro, MSK)
**Duration**: ~12 hours total

**Coordination**:
- Follows 5 Ps framework (Preparation, Position, Permission, Perform, Present)
- Creates examination findings (e.g., "Pansystolic murmur grade 3/6 at apex")

### Batch 4 Execution (1 Agent)

**Agent**: MED-011 (cultural-safety-expert)
**Target**: 92 cultural personas (integrated into 360)
**Duration**: ~28 hours total

**Coordination**:
- Cultural liaison review BEFORE deployment
- LGBTQIA+ educator review BEFORE deployment
- No stereotypical personas

---

## Quality Assurance (QA-001)

**medical-qa-validator** agent reviews all 360 personas after creation:

**Checklist**:
- [ ] All 360 personas follow JSON template
- [ ] All RAG citations >0.65 confidence
- [ ] All have ≥2 FRACP clinician reviews
- [ ] Zero hardcoded credentials
- [ ] Zero clinical inaccuracies (no wrong diagnoses, dangerous advice)
- [ ] Cultural safety validated (12 Aboriginal/TSI, 40 LGBTQIA+, 40 CALD)
- [ ] Difficulty distribution correct (125 Easy, 148 Medium, 87 Hard)
- [ ] Specialty distribution correct (10 specialties as per MASTER_PLAN.md)

**QA Report Output**:
```json
{
  "total_personas_reviewed": 360,
  "total_personas_passed": 360,
  "total_personas_failed": 0,
  "quality_issues": [],
  "clinical_inaccuracies": 0,
  "cultural_safety_violations": 0,
  "avg_rag_citation_confidence": 0.73,
  "avg_fracp_reviews_per_persona": 2.1,
  "recommendation": "APPROVED FOR DEPLOYMENT"
}
```

---

## Next Steps

1. **Read individual agent specs**: Start with MED-001-cardiology-expert.md
2. **Understand learning loop**: How agents improve based on FRACP feedback
3. **Execute PRD_CC_001**: Create all 13 agent specification files
4. **Validate with test persona**: Create 1 cardiology persona and validate with 2 FRACP clinicians before scaling to 360

---

**Status**: ✅ ALL 13 AGENT SPECIFICATIONS COMPLETE (8,909 lines)
**Files Created**: MED-001 through MED-012 + QA-001 (13 agent specs)
**Total Lines**: 8,909 lines across 13 files (avg 685 lines/agent)
**Next**: Convert to Claude Skills format → Test with pilot personas
**Last Updated**: 2026-03-15
**Version**: 1.0 (COMPLETE)
