# OSCE Station Generation — Expert Agent Instructions

You convert already-expert-assessed workshop cases into full AMC-format OSCE
station scenarios for the irStudy platform's `osces` table.

## Input
For each case you are given a path to a `<case>.assessed.json` (expert review +
metadata) — read it AND its sibling `<case>.json` (full clinical text /
html_fragment + rag_context with qdrant_point_ids). The clinical facts are
already verified; your job is to format an 8-minute OSCE station.

## Output
Write ONE JSON file per case to `25-august-docs/osce_generated/<case_id>.osce.json`
(create the dir). Each file is a single JSON object with EXACTLY these keys:

```json
{
  "osce_id": "WS-OSCE-<CASE_ID>",
  "title": "<concise station title>",
  "specialty": "<copy from assessed.json: gastroenterology|obstetrics_gynaecology|musculoskeletal|neurology|urology|ophthalmology|general_practice>",
  "station_type": "<history_taking|physical_examination|counselling|communication|diagnosis_management|emergency_scenario>",
  "difficulty": "<easy|medium|hard>",
  "time_limit_minutes": 8,
  "patient_instructions": "<role-player script: demographics, presenting complaint, story, ICE (ideas/concerns/expectations), how to respond to questions, affect. 150-300 words.>",
  "candidate_instructions": "<what the candidate is told at the door: setting, patient one-liner, and the task(s) e.g. 'Take a focused history, explain your differential, outline initial management.' 60-120 words.>",
  "examiner_instructions": "<what the examiner looks for + how to use the rubric; any prompts to give. 80-150 words.>",
  "rubric": {
     "total_marks": 15,
     "domains": [
        {"domain": "History/Approach", "max_marks": 5, "criteria": ["...", "..."]},
        {"domain": "Diagnosis/Reasoning", "max_marks": 4, "criteria": ["..."]},
        {"domain": "Management/Safety", "max_marks": 4, "criteria": ["..."]},
        {"domain": "Communication", "max_marks": 2, "criteria": ["..."]}
     ]
  },
  "red_flags": ["<must-not-miss features relevant to this presentation>", "..."],
  "australian_guidelines": ["<eTG / RACGP / RANZCOG / RANZCO / SOMANZ / KEMH / PBS references with the specific point>", "..."],
  "learning_objectives": ["...", "..."],
  "key_points": ["<clinical pearls>", "..."],
  "tags": ["<from assessed metadata + presentation>"],
  "citations": [{"claim": "...", "source": "...", "qdrant_point_id": "<from the case's rag_context>"}]
}
```

## Rules (a validation gate checks these)
1. `rubric.domains` must sum `max_marks` to `rubric.total_marks` (15).
2. `red_flags` ≥ 2 items; `australian_guidelines` ≥ 2 items — populate these fully
   (existing platform OSCEs leave them empty; this station set must not).
3. `patient_instructions`, `candidate_instructions`, `examiner_instructions` all
   non-empty and role-appropriate (patient = the actor's script, candidate = door
   instructions, examiner = marking guidance).
4. Ground everything in the assessed case content — incorporate the expert
   corrections (don't reproduce the original errors) and enhancements.
5. ≥2 citations with qdrant_point_ids copied verbatim from the case's rag_context.
6. Australian standards throughout (eTG, PBS, 000, mmol/L, paracetamol).
7. Pure valid JSON, no markdown fences, no placeholders.
8. Re-read each file you write to confirm it parses and the rubric marks sum to 15.

Return one line per station: osce_id — station_type — total_marks — #red_flags/#guidelines.
