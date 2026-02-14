# RAG MCQ Generation - Restart Plan

## What Happened

**Problem:** Running 33 parallel Ollama processes overwhelmed the system
- Only batches 1-3 completed (58 MCQs total)
- Batches 4-33 failed with Ollama timeout errors
- Issue: Ollama can't handle 33 simultaneous generation requests

## Current Status

✅ **Completed:**
- Batch 1: 20/20 MCQs (ENDO-MCQ-0001 to 0020)
- Batch 2: 18/20 MCQs (ENDO-MCQ-0021 to 0040, 2 failures)
- Batch 3: 20/20 MCQs (ENDO-MCQ-0041 to 0060)
- **Total: 58 MCQs with proper RAG citations**

❌ **Remaining:**
- Batches 4-33: 600 MCQs (ENDO-MCQ-0061 to end)

## Solution: Sequential Generation

Instead of parallel, run batches one at a time:

```bash
# Run remaining batches sequentially
bash scripts/run_rag_sequential.sh 4 33
```

**Advantages:**
- No resource exhaustion
- Ollama handles one batch at a time
- More reliable
- Progress is trackable

**Timeline:**
- Per batch: ~20 minutes
- 30 remaining batches: ~10 hours total
- Can run overnight

## Alternative: Small Parallel Groups

Run 3-5 batches at a time instead of 33:

```bash
# Example: Run batches 4-8 in parallel
for i in 4 5 6 7 8; do
    bash scripts/run_rag_mcq_batch.sh $i $((($i-1)*20)) 20 &
done
wait

# Then batches 9-13, etc.
```

## Recommended Approach

**Option 1: Sequential (Safest)**
```bash
nohup bash scripts/run_rag_sequential.sh 4 33 > rag_sequential.log 2>&1 &
```

**Option 2: Small Groups (Faster)**
- Run 3 batches at a time
- Wait for completion
- Repeat

---

**Current File:** `data/mcqs/missing_topics_comprehensive_mcqs.json`
**Generated So Far:** 58/658 MCQs (8.8%)
**With Citations:** Yes (3 per MCQ with page numbers)
