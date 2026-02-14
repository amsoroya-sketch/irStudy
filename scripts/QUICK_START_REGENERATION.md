# Quick Start: MCQ Regeneration

## TL;DR

Regenerate **1,508 placeholder MCQs** with LLM-powered generation in 3 commands.

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run regeneration (2-4 hours)
python scripts/regenerate_all_placeholder_mcqs_with_summaries.py

# 3. Validate results
python scripts/validate_mcqs_qa003.py
```

---

## Pre-Flight Checklist

### ✅ Prerequisites

```bash
# Check Qdrant is running
curl http://localhost:6333/collections/medical_knowledge
# Expected: {"result":{"name":"medical_knowledge",...}}

# Check Ollama models
ollama list | grep -E "deepseek-r1:14b|llama3.1:70b"
# Expected: Both models listed

# Activate virtual environment
source venv/bin/activate
```

### ✅ What It Does

- Regenerates **1,508 MCQs** across 7 files
- Uses **LLM generation** (deepseek-r1:14b or llama3.1:70b)
- Adds **3 RAG-verified citations** per MCQ (confidence >0.70)
- Generates **summary field** (1-2 sentences) for each MCQ
- Validates **no placeholder patterns** remain
- Prefers **Australian guidelines** (eTG, RANZCP, AMH, PBS)

---

## Run Regeneration

```bash
# Full regeneration (estimated: 2-4 hours)
python scripts/regenerate_all_placeholder_mcqs_with_summaries.py

# Monitor progress in separate terminal
tail -f /tmp/regeneration_errors.log
```

### Expected Output

```
======================================================================
🚀 STARTING FULL REGENERATION OF 1,508 PLACEHOLDER MCQs
======================================================================

📂 PROCESSING FILE: missing_topics_comprehensive_mcqs.json (658 MCQs)
  [1/658] ✅ MCQ regenerated successfully
  [10/658] 📊 Progress: 0.34 MCQs/sec | 29.4s elapsed
  ...
💾 Saved 658 MCQs to missing_topics_comprehensive_mcqs.json

📂 PROCESSING FILE: week3_respiratory_200_mcqs.json (200 MCQs)
  ...

📊 FINAL SUMMARY:
  Total MCQs Regenerated: 1,508
  Total Citations Validated: 4,524 (3 per MCQ)
  Total Time: 180.5 minutes
  Success Rate: 98.7%
```

---

## Validate Results

```bash
# Run QA-003 validation
python scripts/validate_mcqs_qa003.py

# Check for remaining placeholders (should be 0)
grep -l "Clinical scenario for" data/mcqs/*.json | wc -l

# Verify summary fields (should be 1,508)
grep -o '"summary"' data/mcqs/*.json | wc -l

# Check Australian citations (should be 1,508+)
grep -i "etg\|ranzcp\|amh" data/mcqs/*.json | wc -l
```

---

## Files Regenerated

| File | MCQs | Status |
|------|------|--------|
| `missing_topics_comprehensive_mcqs.json` | 658 | ⏳ Pending |
| `week3_respiratory_200_mcqs.json` | 200 | ⏳ Pending |
| `week3_cardiology_200_mcqs.json` | 200 | ⏳ Pending |
| `week3_psychiatry_additional_100_mcqs.json` | 100 | ⏳ Pending |
| `week1_regenerated_100_mcqs.json` | 100 | ⏳ Pending |
| `week2_regenerated_100_mcqs.json` | 100 | ⏳ Pending |
| `missing_psychiatry_150_mcqs.json` | 150 | ⏳ Pending |

**Total:** 1,508 MCQs

---

## Troubleshooting

### Issue: Qdrant Connection Failed
```bash
docker-compose up -d qdrant
curl http://localhost:6333
```

### Issue: Ollama Model Not Found
```bash
ollama pull deepseek-r1:14b
ollama pull llama3.1:70b
```

### Issue: LLM Generation Slow
```bash
# Check Ollama status
ollama ps

# Expected: Models running, no errors
```

### Issue: Placeholder Patterns Still Detected
```bash
# Check error log
tail -100 /tmp/regeneration_errors.log

# Review failed MCQs
grep "validation_warning" data/mcqs/*.json
```

---

## Success Criteria

After regeneration completes:

- ✅ All 7 files processed
- ✅ 1,508 MCQs regenerated
- ✅ 4,524 citations validated (3 per MCQ)
- ✅ No placeholder patterns remain
- ✅ All MCQs have summary field
- ✅ QA-003 validation passes

---

## Next Steps

1. ✅ Review error log: `/tmp/regeneration_errors.log`
2. ✅ Check summary report: `planning/regeneration_summary.json`
3. ✅ Run QA-003 validation
4. ✅ Commit regenerated MCQs to git

---

## Documentation

- **Full Guide:** `scripts/REGENERATION_GUIDE.md`
- **Complete Summary:** `MCQ_REGENERATION_COMPLETE.md`
- **Script:** `scripts/regenerate_all_placeholder_mcqs_with_summaries.py`

---

**Estimated Runtime:** 2-4 hours
**Created:** 2026-01-26
