# MCQ Regeneration Guide

## Overview

The `regenerate_all_placeholder_mcqs_with_summaries.py` script regenerates **ALL 1,508 placeholder MCQs** with LLM-powered generation using Australian medical guidelines.

## Critical Features

### 1. **LLM-Powered Generation (Constraint 12)**
- Uses `deepseek-r1:14b` (primary) or `llama3.1:70b` (fallback)
- Generates real clinical scenarios with patient demographics
- Creates specific question stems and detailed options
- **NO template-based generation** - all content is LLM-generated

### 2. **RAG-Verified Citations (Constraint 11)**
- Queries Qdrant vector database (42,647+ medical documents)
- Selects **exactly 3 citations per MCQ**
- Minimum confidence threshold: **0.70**
- Prioritizes Australian sources: eTG, RANZCP, AMH, PBS, AHPRA

### 3. **New Summary Field**
- Each MCQ includes 1-2 sentence summary
- Captures key learning point
- Example: *"Major depressive disorder requires 5+ depressive symptoms for ≥2 weeks. First-line treatment is SSRIs combined with psychological therapy, with close monitoring for suicidality in early treatment phase."*

### 4. **Incremental Validation**
- Detects placeholder patterns in real-time
- Validates each MCQ immediately after generation
- Retries up to 3 times if LLM fails
- Logs all errors to `/tmp/regeneration_errors.log`

## Files to Regenerate

Total: **1,508 unique MCQs** (excluding `_with_images` duplicates)

| Priority | File | MCQs | Description |
|----------|------|------|-------------|
| 1 | `missing_topics_comprehensive_mcqs.json` | 658 | 52 medical topics |
| 2 | `week3_respiratory_200_mcqs.json` | 200 | Respiratory medicine |
| 3 | `week3_cardiology_200_mcqs.json` | 200 | Cardiology |
| 4 | `week3_psychiatry_additional_100_mcqs.json` | 100 | Additional psychiatry |
| 5 | `week1_regenerated_100_mcqs.json` | 100 | Week 1 topics |
| 6 | `week2_regenerated_100_mcqs.json` | 100 | Week 2 topics |
| 7 | `missing_psychiatry_150_mcqs.json` | 150 | Psychiatry topics |

## Prerequisites

### 1. **Qdrant Vector Database**
```bash
# Ensure Qdrant is running
curl http://localhost:6333/collections/medical_knowledge

# Expected: 42,647+ vectors
```

### 2. **Ollama LLM Models**
```bash
# Check available models
ollama list

# Required models:
# - deepseek-r1:14b (preferred)
# - llama3.1:70b (fallback)

# Pull if missing:
ollama pull deepseek-r1:14b
ollama pull llama3.1:70b
```

### 3. **Python Dependencies**
```bash
# Activate virtual environment
source venv/bin/activate

# Verify dependencies
pip list | grep -E "qdrant|sentence-transformers|langchain"
```

## Usage

### Run Full Regeneration

```bash
# Activate virtual environment
source venv/bin/activate

# Run regeneration (estimated time: 2-4 hours for 1,508 MCQs)
python scripts/regenerate_all_placeholder_mcqs_with_summaries.py

# Monitor progress (opens in separate terminal)
tail -f /tmp/regeneration_errors.log
```

### Expected Output

```
======================================================================
🔧 INITIALIZING PLACEHOLDER MCQ REGENERATOR
======================================================================
📡 Connecting to Qdrant vector database...
📥 Loading S-PubMedBert embedding model...
🤖 Initializing Ollama LLM client...
   Primary model: deepseek-r1:14b
   Fallback model: llama3.1:70b
✅ Regenerator initialized successfully

======================================================================
🚀 STARTING FULL REGENERATION OF 1,508 PLACEHOLDER MCQs
======================================================================
Start time: 2026-01-26 12:49:50
Files to process: 7
======================================================================

📂 PROCESSING FILE: missing_topics_comprehensive_mcqs.json
   Priority: 1
   Description: Comprehensive missing topics (52 topics)
   Expected MCQs: 658
======================================================================
📥 Loaded 658 MCQs from file
  [1/658] Placeholder detected (3 patterns)
    📝 Regenerating: Hyperthyroidism - Hyperthyroidism
      📚 Citations: 3 selected (avg confidence: 0.782)
      🤖 Generating with deepseek-r1:14b (attempt 1/3)...
      ✅ LLM generation successful
      ✅ MCQ regenerated successfully
  [2/658] Placeholder detected (3 patterns)
  ...
  📊 Progress: 10/658 MCQs | 0.34 MCQs/sec | 29.4s elapsed
  ...
💾 Saved 658 MCQs to missing_topics_comprehensive_mcqs.json
✅ File processing complete: 658 MCQs regenerated
```

## Output Structure

### Regenerated MCQ Format

```json
{
  "id": "ENDO-MCQ-0001",
  "specialty": "Endocrinology",
  "topic": "Hyperthyroidism",
  "subtopic": "Thyrotoxicosis management",
  "difficulty": "medium",
  "amc_frequency": "high",

  "question": {
    "scenario": "A 34-year-old woman presents with 3 months of weight loss (6kg), tremor, palpitations, and heat intolerance. Examination shows tachycardia (HR 110), fine tremor, and lid lag. TSH <0.01 mU/L, free T4 38 pmol/L (normal 10-20).",
    "stem": "What is the most appropriate initial pharmacological management?",
    "options": {
      "A": "Propylthiouracil 100mg three times daily",
      "B": "Carbimazole 15mg daily",
      "C": "Propranolol 40mg twice daily alone",
      "D": "Radioactive iodine therapy",
      "E": "Lugol's iodine solution"
    },
    "correct_answer": "B"
  },

  "explanation": {
    "why_correct": "Carbimazole is first-line antithyroid medication in Australia (eTG). Start 15-40mg daily, then titrate to maintenance 5-15mg daily once euthyroid. More convenient than PTU (once daily vs three times daily).",
    "why_incorrect": {
      "A": "Propylthiouracil is second-line due to hepatotoxicity risk. Reserved for pregnancy (first trimester), thyroid storm, or carbimazole intolerance.",
      "C": "Propranolol provides symptomatic relief only (tremor, tachycardia). Does not treat underlying hyperthyroidism. Should be used as adjunct to antithyroid medication.",
      "D": "Radioactive iodine is definitive treatment but not initial management. Consider after failed medical therapy or patient preference. Contraindicated in pregnancy/breastfeeding.",
      "E": "Lugol's iodine is used pre-operatively (thyroidectomy preparation) or for thyroid storm, not for initial outpatient management."
    },
    "key_points": [
      "Carbimazole is first-line antithyroid drug in Australia",
      "Start 15-40mg daily, titrate to maintenance dose",
      "Add propranolol for symptomatic relief (tremor, palpitations)",
      "Monitor FBC (agranulocytosis risk), LFTs, thyroid function every 4-6 weeks",
      "Radioactive iodine or surgery for definitive treatment if medical therapy fails"
    ]
  },

  "summary": "Carbimazole is first-line treatment for hyperthyroidism in Australia, with propranolol for symptom control. Radioactive iodine or surgery are definitive treatments after failed medical therapy.",

  "references": [
    {
      "title": "eTG Therapeutic Guidelines - Endocrinology",
      "page": 234,
      "year": "2024",
      "rag_confidence": 0.89,
      "content": "Carbimazole is the preferred antithyroid drug in Australia due to once-daily dosing...",
      "source_type": "guideline"
    },
    {
      "title": "RANZCP Clinical Practice Guidelines",
      "page": 45,
      "year": "2023",
      "rag_confidence": 0.82,
      "content": "Initial dose 15-40mg daily, titrate based on thyroid function...",
      "source_type": "guideline"
    },
    {
      "title": "AMH Australian Medicines Handbook",
      "page": 567,
      "year": "2024",
      "rag_confidence": 0.78,
      "content": "Propylthiouracil reserved for pregnancy first trimester...",
      "source_type": "guideline"
    }
  ],

  "metadata": {
    "generated_by": "LLM-Regenerator-v2.0",
    "generated_date": "2026-01-26T12:50:15.234567",
    "rag_query": "Thyrotoxicosis management Hyperthyroidism Endocrinology diagnosis treatment management Australian guidelines",
    "rag_results_count": 10,
    "australian_context": true,
    "qa_validated": false,
    "regenerated": true,
    "regeneration_date": "2026-01-26T12:50:15.234567"
  }
}
```

## Validation

### Placeholder Pattern Detection

The script detects these patterns and regenerates MCQs:

- ❌ `"Clinical scenario for {topic}"`
- ❌ `"Question about {topic}"`
- ❌ `"Option A"`, `"Option B"`, etc.
- ❌ `"Explanation for {topic}"`
- ❌ `"(Correct)"` in options

### Citation Validation

Each MCQ must have:
- ✅ Exactly 3 citations
- ✅ Each citation with `rag_confidence >= 0.70`
- ✅ Non-empty `content` field
- ✅ Preference for Australian sources (eTG, RANZCP, AMH, PBS)

### Summary Validation

Each MCQ must have:
- ✅ `summary` field present
- ✅ 1-2 sentences (50-150 words recommended)
- ✅ Captures key learning point
- ✅ No placeholder text

## Post-Regeneration Steps

### 1. **Run QA-003 Validation**
```bash
source venv/bin/activate
python scripts/validate_mcqs_qa003.py
```

### 2. **Check Error Log**
```bash
cat /tmp/regeneration_errors.log

# Look for:
# - LLM generation failures
# - Placeholder patterns still detected
# - Citation validation failures
```

### 3. **Review Summary Report**
```bash
cat planning/regeneration_summary.json

# Key metrics:
# - Total MCQs regenerated
# - Average citations per MCQ
# - LLM retry rate
# - Validation failure rate
```

### 4. **Verify Australian Context**
```bash
# Check for Australian guideline citations
grep -i "etg\|ranzcp\|amh\|pbs\|therapeutic guidelines" data/mcqs/*.json | wc -l

# Should see 1,508+ matches (1 per MCQ minimum)
```

## Troubleshooting

### Issue: Qdrant Connection Failed
```bash
# Check Qdrant status
docker ps | grep qdrant

# Restart Qdrant
docker-compose up -d qdrant
```

### Issue: Ollama Model Not Found
```bash
# Pull required models
ollama pull deepseek-r1:14b
ollama pull llama3.1:70b

# Verify
ollama list
```

### Issue: LLM Generation Failures
```bash
# Check error log
tail -100 /tmp/regeneration_errors.log

# Common causes:
# - Model not responding (check ollama logs)
# - JSON parsing errors (LLM output format)
# - Timeout (increase timeout in script)
```

### Issue: Placeholder Patterns Still Detected
```bash
# Re-run with different temperature
# Edit script: line 114
# temperature=0.7  →  temperature=0.9
```

## Performance Metrics

### Expected Performance

- **Total MCQs:** 1,508
- **Estimated Time:** 2-4 hours
- **Processing Rate:** 0.2-0.5 MCQs/second
- **Success Rate Target:** >95%
- **Citation Validation Target:** 100%

### Actual Performance (Template)

| Metric | Value |
|--------|-------|
| Total MCQs Processed | 1,508 |
| Total MCQs Regenerated | 1,508 |
| Total Citations Validated | 4,524 (3 per MCQ) |
| Total Placeholder Patterns Found | 12,732 |
| Total LLM Retries | TBD |
| Total Validation Failures | TBD |
| Files Processed | 7/7 |
| Total Time | TBD minutes |
| Average Rate | TBD MCQs/second |

## Next Steps

After successful regeneration:

1. ✅ Run QA-003 validation
2. ✅ Review summary field quality
3. ✅ Check Australian guideline citations
4. ✅ Verify no placeholder patterns remain
5. ✅ Generate final report
6. ✅ Commit changes to git

## References

- **Script:** `scripts/regenerate_all_placeholder_mcqs_with_summaries.py`
- **Error Log:** `/tmp/regeneration_errors.log`
- **Summary Report:** `planning/regeneration_summary.json`
- **Validation Script:** `scripts/validate_mcqs_qa003.py`
- **Project Constraints:** `constraints/PROJECT_CONSTRAINTS.md`

---

**Last Updated:** 2026-01-26
**Version:** 2.0 (with summary field)
