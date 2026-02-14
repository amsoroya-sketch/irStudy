# Agent OS Regeneration - Quick Reference Card

**Print this page for desk reference during execution**

---

## Pre-Flight Checklist

```bash
# 1. RAG System
curl -s http://localhost:6333/collections/medical_knowledge | jq '.result.vectors_count'
# Expect: 9,672+

# 2. Ollama LLM
ollama list | grep llama3.2:latest
# Expect: llama3.2:latest found

# 3. Agent OS Imports
python3 -c "from src.agents.medical.med_001_cardiology import CardiologyExpert; from src.agents.medical.med_002_respiratory import RespiratoryExpert; from src.agents.medical.med_009_psychiatry import PsychiatryExpert"
# Expect: No errors

# 4. Output Directories
ls -ld data-jan-26/mcqs/{respiratory,cardiology,psychiatry}/
# Expect: All directories exist and writable
```

---

## Execution Commands

### Day 1-2: Respiratory (MED-002)
```bash
# Pre-check
./scripts-jan-26/pre_generation_check.sh

# Generate (Terminal 1)
python3 scripts-jan-26/generate_respiratory_mcqs.py | tee logs/respiratory_$(date +%Y%m%d).log

# Monitor (Terminal 2)
watch -n 10 'jq ". | length" data-jan-26/mcqs/respiratory/respiratory_mcqs.json'

# Post-check
./scripts-jan-26/post_generation_check.sh respiratory

# Commit (if PASS)
git add data-jan-26/mcqs/respiratory/
git commit -m "feat: Add 200 respiratory MCQs via Agent OS MED-002"
```

### Day 2-3: Cardiology (MED-001)
```bash
python3 scripts-jan-26/generate_cardiology_mcqs.py | tee logs/cardiology_$(date +%Y%m%d).log
./scripts-jan-26/post_generation_check.sh cardiology
git add data-jan-26/mcqs/cardiology/
git commit -m "feat: Add 200 cardiology MCQs via Agent OS MED-001"
```

### Day 3-4: Psychiatry (MED-009)
```bash
python3 scripts-jan-26/generate_psychiatry_mcqs.py | tee logs/psychiatry_$(date +%Y%m%d).log
./scripts-jan-26/post_generation_check.sh psychiatry
git add data-jan-26/mcqs/psychiatry/
git commit -m "feat: Add 200 psychiatry MCQs via Agent OS MED-009"
```

---

## Validation Gates (Fail-Fast)

### Gate 1: Pre-Generation (BLOCKS start)
- RAG operational (9,672+ chunks)
- Ollama operational (llama3.2:latest)
- Agent OS imports successful

### Gate 2: Incremental (BLOCKS each MCQ)
- No placeholder patterns (6 patterns checked)
- Exactly 3 citations (confidence >0.70)
- Summary present (50-200 chars)
- Patient demographics (age + gender)
- Australian context (eTG/RANZCP)

### Gate 3: Post-Generation (BLOCKS next specialty)
- 0 placeholder patterns
- >70% QA-003 Tier 1 approval
- 100% Australian compliance
- 100% summary compliance

### Gate 4: Pre-Commit Hook (BLOCKS git commit)
- Final placeholder scan (must be 0)

---

## Success Metrics (Target)

| Metric | Target | How to Check |
|--------|--------|--------------|
| MCQs Generated | 600 | `jq '. | length' combined_600_mcqs.json` |
| Placeholder Patterns | 0 | `./scripts/validate_content_substance.sh <file>` |
| Citation Count | 3/MCQ | `jq '[.[] | .references | length] | add / length' <file>` |
| Summary Compliance | 100% | `jq '[.[] | select(.summary != null)] | length' <file>` |
| QA-003 Tier 1 | >70% | Check `reports/*_qa003.json` |
| Australian Compliance | 100% | `python3 scripts/validate_australian_compliance.py` |

---

## Troubleshooting

### Issue: "RAG system not responding"
```bash
# Restart Qdrant
docker compose restart qdrant

# Verify collection
curl http://localhost:6333/collections/medical_knowledge

# Re-index if needed
python3 scripts/index_qdrant.py
```

### Issue: "Ollama LLM slow/crashed"
```bash
# Check GPU memory
nvidia-smi

# Restart Ollama
pkill ollama
ollama serve

# Test generation
ollama run llama3.2:latest "Test prompt"
```

### Issue: "Placeholder patterns detected"
```bash
# Find affected MCQs
grep -n "Clinical scenario for\|Question about" <file>

# Regenerate affected topics
python3 scripts-jan-26/generate_<specialty>_mcqs.py --topic <topic> --regenerate
```

### Issue: "QA-003 approval rate <70%"
```bash
# Review low-confidence citations
jq '.items[] | select(.confidence < 0.70)' reports/<specialty>_qa003.json

# Regenerate low-confidence MCQs
python3 scripts-jan-26/regenerate_low_confidence.py --file <file> --threshold 0.70
```

---

## Rollback Plan

### Failure Criteria
- Placeholder rate >5% after 100 MCQs
- QA-003 Tier 1 approval <50%
- Generation time >2 min per MCQ

### Rollback Steps
```bash
# 1. STOP generation
pkill -f generate_.*_mcqs.py

# 2. Do NOT commit
git reset --hard HEAD

# 3. Diagnose
# - Check Agent OS prompts
# - Check RAG connectivity
# - Check LLM response quality

# 4. Fix and retry
# - Update agent generation templates
# - Improve RAG citation extraction
# - Optimize LLM prompts

# 5. Document in LESSONS_LEARNED_AND_MISTAKES.md
```

---

## Agent OS Routing

| Specialty | Agent | Tools | Guidelines |
|-----------|-------|-------|------------|
| Respiratory | MED-002 | spirometry, CXR, Wells_PE, CURB65 | eTG Respiratory 4.x |
| Cardiology | MED-001 | ECG, GRACE, TIMI, CHA2DS2-VASc | eTG Cardiovascular 5.x |
| Psychiatry | MED-009 | PHQ9, GAD7, MSE, BPRS, suicide_risk | RANZCP Guidelines |

---

## Placeholder Patterns (NEVER ALLOW)

```
❌ "Clinical scenario for"
❌ "Question about"
❌ "Option A", "Option B", "Option C", "Option D"
❌ "Explanation for"
❌ "Brief summary of"
❌ "This MCQ tests"
```

**Detection**: `./scripts/validate_content_substance.sh <file>`
**Action**: Regenerate MCQ immediately (max 2 retries)

---

## Australian Compliance (ALWAYS REQUIRED)

### Spelling
```
✅ paediatric   ❌ pediatric
✅ anaesthesia  ❌ anesthesia
✅ oesophagus   ❌ esophagus
```

### Drug Names
```
✅ paracetamol  ❌ acetaminophen
✅ salbutamol   ❌ albuterol
✅ adrenaline   ❌ epinephrine
```

### Guidelines
```
✅ Therapeutic Guidelines (eTG)
✅ RANZCP Clinical Practice Guidelines
✅ PBS (Pharmaceutical Benefits Scheme)
✅ AMH (Australian Medicines Handbook)
```

---

## Monitoring Commands

```bash
# Real-time MCQ count
watch -n 5 'jq ". | length" data-jan-26/mcqs/<specialty>/<specialty>_mcqs.json'

# Placeholder pattern count
watch -n 30 './scripts/validate_content_substance.sh data-jan-26/mcqs/<specialty>/<specialty>_mcqs.json && echo "PASS" || echo "FAIL"'

# Generation speed
tail -f logs/<specialty>_*.log | grep "MCQ.*saved"

# Disk space
df -h | grep "/$"
```

---

## Contact Points

| Issue | Contact |
|-------|---------|
| Agent OS technical issues | PM (coordinator) |
| Medical accuracy concerns | Medical Expert (manual review) |
| RAG system issues | PM (Qdrant admin) |
| Validation script failures | testing-qa-expert |
| Australian compliance violations | QA-001 validator (automated) |

---

**Print Date**: 2026-01-26
**Version**: 1.0
**Status**: READY FOR EXECUTION
