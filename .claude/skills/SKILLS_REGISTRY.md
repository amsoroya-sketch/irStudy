# Skills Registry - irStudy Medical Education AI

**Project**: irStudy - ICRP Medical Education AI System
**Skills Structure**: Progressive (YAML frontmatter + on-demand references)
**Total Skills**: 2
**Optimization Date**: 2026-04-13

---

## Active Skills

### 1. Medical Content Quality
**Path**: `.claude/skills/medical-content-quality/`
**Description**: Australian medical education content quality assurance for OSCE/MCQ generation
**Effort**: High
**User-Invocable**: Yes

**Triggers**:
- Medical content generation
- Clinical scenario validation
- OSCE case review
- Quality gate validation

**Key Capabilities**:
- 13-gate QA validation enforcement
- RAG citation compliance (100% coverage, ≥0.65 confidence)
- Australian medical context validation (no US drug names)
- FRACP review criteria (≥8.0/10 target)
- No placeholder content detection
- UTF-8 encoding verification

**Files**:
- `SKILL.md` - Progressive skill definition (YAML + core patterns)
- `reference/quality-gates-checklist.md` - Detailed 13-gate requirements
- `scripts/validate-medical-content.sh` - Automated validation

---

### 2. Python + LLM Integration
**Path**: `.claude/skills/python-llm-integration/`
**Description**: Python venv + LLM integration patterns for medical content generation
**Effort**: Medium
**User-Invocable**: Yes

**Triggers**:
- Running Python scripts
- LLM integration work
- Medical content generation
- Batch processing tasks

**Key Capabilities**:
- Python venv activation enforcement
- Claude API usage for medical content (CRITICAL - no local LLMs)
- UTF-8 encoding validation
- Environment setup validation
- Checkpoint/resume patterns
- Cost-quality tradeoff guidance

**Files**:
- `SKILL.md` - Progressive skill definition (YAML + patterns)
- `scripts/validate-python-setup.sh` - Environment validation

---

## Skill Usage Statistics

| Skill | Invocations | Success Rate | Avg Effort |
|-------|-------------|--------------|------------|
| medical-content-quality | TBD | TBD | High |
| python-llm-integration | TBD | TBD | Medium |

**Note**: Statistics tracked by `skill-evolution-tracker.py` (installed at project root)

---

## Optimization Metrics

### Before Optimization
- Skills: 0 (empty directory)
- Context per invocation: No skill context
- Ralph iterations: Limited by lack of validation patterns

### After Optimization
- Skills: 2 progressive skills
- Context savings: ~40% (reference docs loaded on demand)
- Ralph iterations: Enhanced with validation patterns
- Validation automation: 2 executable scripts

---

## Integration with PROJECT_CONSTRAINTS.md

All skills reference specific constraint modules:
- `medical-content-quality` → `constraints/14-ralph-medical-content-standards.md`
- `python-llm-integration` → `constraints/4-llm-integration.md`

**Duplication eliminated**: Skills contain ONLY triggers and quick-reference patterns, detailed rules stay in constraints.

---

## Maintenance Notes

### Monthly Review
- Update RAG citation confidence thresholds based on deployment metrics
- Review FRACP validation scores and adjust criteria if needed
- Update Python package requirements

### Quarterly Backfill
- Run `ralph-learning-filler.py` to analyze Ralph logs
- Extract new medical content patterns
- Update skill descriptions based on usage analytics

### Skill Evolution
- Track with: `python skill-evolution-tracker.py report --days 30`
- Auto-optimize descriptions if over/under-applied
- Create new skills when distinct patterns emerge

---

## Quick Reference Commands

### Validate Medical Content
```bash
bash .claude/skills/medical-content-quality/scripts/validate-medical-content.sh
```

### Validate Python Setup
```bash
bash .claude/skills/python-llm-integration/scripts/validate-python-setup.sh
```

### Track Skill Usage
```bash
python skill-evolution-tracker.py report
```

### Backfill Learning Templates
```bash
python ralph-learning-filler.py --backfill
```

---

**Last Updated**: 2026-04-13
**Optimization Status**: ✅ Complete
**Ralph Context Tracking**: ✅ Enabled (ralph-enhanced.sh)
