# Workshop Case Assessment — Expert Agent Instructions

You are assessing Dr. Amir AMC workshop case notes for the irStudy platform.
For EACH case JSON file assigned to you:

## Input (read the staging JSON)
Each case file at `25-august-docs/staging/<TargetDir>/<case_id>.json` contains:
- `raw_text` — extracted case content (teaching notes for one OSCE case)
- `html_fragment` — clean HTML version (DOCX cases only; null for PDFs)
- `rag_context` — top textbook chunks from the irStudy medical RAG index
  (each with `qdrant_point_id`, `source`, `page`, `score`, `text`)
- `title`, `specialty`, `bundle`, `class`, `images`

## Your job
Fact-check the case content against `rag_context` (and your clinical knowledge),
then write `<case_id>.assessed.json` NEXT TO the input file with EXACTLY this schema:

```json
{
  "case_id": "<same as input>",
  "title": "<cleaned human title, e.g. 'Primary Amenorrhoea'>",
  "specialty": "<same as input>",
  "target_dir": "<same as input>",
  "use_fragment": true,
  "sections": [],
  "expert_review": {
    "reviewed_by": "<your persona, e.g. 'history-taking-expert (Australian clinical supervisor)'>",
    "corrections": [
      {"issue": "<what is wrong/outdated in the source>", "correction": "<the correct, current Australian guidance>"}
    ],
    "enhancements": [
      "<concrete suggestion: missing red flag, missing DDx, missing eTG/PBS/RACGP reference, structure improvement, metadata to add>"
    ],
    "metadata": {
      "station_type": "history_taking | physical_examination | counselling | communication | diagnosis_management | emergency_scenario",
      "difficulty": "easy | medium | hard",
      "amc_frequency": "<high/medium/low + one-line justification>",
      "tags": ["<3-8 lowercase tags>"],
      "related_topics": ["<related existing irStudy topics>"]
    },
    "citations": [
      {"claim": "<specific clinical claim from the case>",
       "source": "<source from rag_context>",
       "page": "<page or null>",
       "qdrant_point_id": "<id from rag_context>"}
    ]
  }
}
```

## Rules (validation gates will check these)
1. **DOCX cases** (`html_fragment` non-null): set `"use_fragment": true`, leave
   `"sections": []` — the renderer reuses the original HTML. Only add a section
   if content needs restructuring.
2. **PDF cases** (`html_fragment` null): set `"use_fragment": false` and build
   `sections` — an ordered list of `{"heading": str, "html": str}` structuring
   the raw_text into clean HTML (`<p>`, `<ul>`, `<table>`). Preserve ALL
   clinical content; fix OCR artifacts; do NOT invent content.
3. **≥3 citations per case**, each with a real `qdrant_point_id` copied from
   `rag_context`. Match citations to actual claims in the case. If rag_context
   is irrelevant to a claim, cite the most relevant chunk available and say so
   in the claim text.
4. **Corrections**: only list genuine errors/outdated guidance (empty list is
   fine if the source is correct). Australian context: eTG current, PBS, 000,
   paracetamol (not acetaminophen), mmol/L.
5. **Enhancements**: at least 2 concrete suggestions per case (the user
   explicitly wants corrections/enhancements/extra metadata surfaced in notes).
6. NO placeholder text ("Lorem", "TODO", "[insert...]", generic "Option A/B").
7. Output must be valid JSON — no trailing commas, no comments, no markdown fences.
8. After writing all files, re-read each .assessed.json you wrote to confirm it
   parses as JSON (visually check structure).
