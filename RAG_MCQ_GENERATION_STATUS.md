# RAG MCQ Generation - Status & Control

## Overview
- **Total MCQs:** 658
- **Batch Size:** 20 MCQs per batch
- **Total Batches:** 33 (32 full batches + 1 partial)
- **Generation Method:** RAG-integrated (Qdrant + Ollama + Medical Books)
- **Citations:** 3 per MCQ with page numbers and confidence scores

## Running Batches

### Active Sessions
Check active tmux sessions:
```bash
tmux list-sessions | grep mcq_rag
```

### Monitor Progress
```bash
bash scripts/monitor_rag_generation.sh
```

### View Specific Batch
```bash
# Attach to batch session
tmux attach -t mcq_rag_batch_1

# Detach: Press Ctrl+B then D

# View log file
tail -f logs/mcq_rag_generation/batch_1.log
```

## Launch All Batches

### Start Remaining Batches (4-33)
```bash
bash scripts/launch_all_rag_batches.sh 4 33
```

### Start Specific Range
```bash
# Example: Launch batches 10-20
bash scripts/launch_all_rag_batches.sh 10 20
```

## Batch Breakdown

| Batch | MCQs | Start Index | End Index | Status |
|-------|------|-------------|-----------|--------|
| 1 | 20 | 0 | 19 | Running |
| 2 | 20 | 20 | 39 | Running |
| 3 | 20 | 40 | 59 | Running |
| 4-32 | 20 each | 60-640 | - | Pending |
| 33 | 18 | 640 | 657 | Pending |

## Stop/Restart Batches

### Kill Specific Batch
```bash
tmux kill-session -t mcq_rag_batch_1
```

### Kill All RAG Batches
```bash
tmux list-sessions | grep mcq_rag | awk '{print $1}' | sed 's/://' | xargs -I {} tmux kill-session -t {}
```

### Restart Failed Batch
```bash
# Example: Restart batch 5
bash scripts/run_rag_mcq_batch.sh 5 80 20
```

## Progress Tracking

### Check JSON File
```bash
# Count generated MCQs
jq '[.mcqs[] | select(.generated_by == "rag_ollama")] | length' data/mcqs/missing_topics_comprehensive_mcqs.json
```

### Check Progress File
```bash
cat MCQ_RAG_GENERATION_PROGRESS.md
```

## Quality Check

### View Sample MCQ with Citations
```bash
jq '.mcqs[0] | {id, topic, scenario: .question.scenario, citations: .references | map({title, page, confidence: .rag_confidence})}' data/mcqs/missing_topics_comprehensive_mcqs.json
```

## Troubleshooting

### Model Loading Issues
- Each batch loads the S-PubMedBert model (takes ~30 seconds)
- Ollama must be running: `ollama list`

### RAG Connection Issues
- Qdrant must be running: `docker-compose up -d`
- Check collection: `curl http://localhost:6333/collections/medical_knowledge`

### Generation Failures
- Check log files: `logs/mcq_rag_generation/batch_*.log`
- Look for error messages
- Restart failed batches individually

## Expected Timeline

- **Per MCQ:** ~30-60 seconds (RAG query + Ollama generation)
- **Per Batch (20 MCQs):** ~10-20 minutes
- **Total (658 MCQs):** ~5-11 hours (if running sequentially)
- **With Parallel Execution:** Significantly faster

## Files Generated

- **Logs:** `logs/mcq_rag_generation/batch_*.log`
- **Progress:** `MCQ_RAG_GENERATION_PROGRESS.md`
- **Updated MCQs:** `data/mcqs/missing_topics_comprehensive_mcqs.json`

---

**Last Updated:** 2026-02-10 07:33
**Status:** Generation in progress
