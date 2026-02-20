# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: face_to_face_clinical_amc_blueprint_710

## Clinical Context
- Differentials detected: PE, cancer, COPD
- Investigations mentioned: 

## Transcript Excerpt
misrun and what is the thinking process behind these cases that they designed for you. I think it's one of the first things that I'll understand about the exam before I proceed to cases, look at the scoring system and look at the outcome of the exam. Now let's go step by step together. AMC in their specification handbook day mentioned that this exam is at the level of an intern year of Australian local graduate, although I don't totally agree with that. To be honest, I don't totally disagree with that. The cases that they use are cases that they use at their intern level. Maybe the only difference is like the scoring system that they use is not the scoring system that they use at the intern level. Because obviously at the intern level, I might be a little bit more flexible in the scoring, but AMC obviously has a high threshold and standard in the scoring system. But it is an osuke exam. We'll talk about osuke exam later on about what is the concept and everything, but they do mention this word a few times that will kind of dissect it and talk about it a little bit more in the scoring system video to the satisfaction of the examinus. So your performance will be always judged by your examinus to pass off a illustration and apparently your threshold to silver alarm for you to pass is the satisfaction of your examiner. We'll give them a mark sheet. We'll make it objective, but it is at the level of satisfaction of your examinus, but even in their 2025 session that AMC run for providers, they still do agree that the exam is at an intern year level. That anyway, they are the people doing the exam and we can really argue about that. You already know that in the face to face exam, we'll have 16 stations. So your overall exam will be 20 stations. When you walk into your exam hallway, you also have 20 rooms out of those 20 rooms, you'll have four rest stations. We'll talk about them later. I'll talk about the exact thing about what is going to happen on the exam day and you will be performing 16 stations or 16 cases with your role players and your examinus. Each of your stations will be at 10 minute duration in total. That 10 minute duration will be divided into eight minute performance. By the time you step foot into that room, the clock starts running, you'll have eight minutes and you'll have two minutes to read the stem outside. So that's essentially when the exam starts, they give you two minutes to read your stem outside, walk in, you have eight minutes to perform, you hear the bell, your two minutes are already started for the next station and you have to run out. But understanding the blueprint, we have already talked about our topics and how do we kind of divide them? We'll talk about them later on in your study planning too. Overall out of your 16 stations, if I want to divide it into five areas, we'll divide it into physical examination. You have medicine and surgery, so I'll put medicine surgery together. I see them as one topic because they do

## Task

You are an expert clinical educator aligned with AMC Clinical Examination standards.

Generate comprehensive AMC-standard clinical notes for this OSCE station.

### REQUIRED SECTIONS:

1. **Station Overview**
   - Station type, presenting complaint, time allocation (8 minutes typical)

2. **SOCRATES Assessment** (for history stations)
   - Each component with clinical examples and what to ask

3. **Systematic History Framework**
   - HPC, PMHx, Medications (include H. pylori therapy where relevant), Allergies, FHx, SHx, Systems Review

4. **Differential Diagnoses** (top 3–5)
   - Each with distinguishing clinical features and likelihood

5. **Red Flags**
   - Full list with clinical significance and immediate actions

6. **Relevant Investigations**
   - Ordered by priority (bedside → bloods → imaging → endoscopy)

7. **Management Principles**
   - Initial, definitive, and safety-net

8. **AMC Marking Criteria Alignment**
   - What examiners specifically assess

9. **Key Facts for AMC Exam** (10 bullet points)
   - High-yield, exam-relevant facts

### CRITICAL CONSTRAINTS:
- Australian AMC standards ONLY
- NEVER mention "video", "recording", "the video says", "missing"
- Present all content as authoritative clinical reference
- Use Australian drug names and guidelines
- Include specific examples and clinical pearls

### OUTPUT FORMAT:
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/face_to_face_clinical_amc_blueprint_710/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/face_to_face_clinical_amc_blueprint_710/key_facts.json

### key_facts.json must contain:
```json
{
  "station_type": "history_taking",
  "main_diagnosis": "",
  "differential_diagnoses": [],
  "red_flags": [],
  "investigations": [],
  "management_steps": [],
  "amc_criteria": [],
  "domain_scores": {
    "history_structure": 8,
    "clinical_reasoning": 8,
    "communication": 7,
    "differential_diagnosis": 8,
    "red_flags": 7,
    "investigations": 8,
    "management": 7,
    "patient_education": 7
  }
}
```
