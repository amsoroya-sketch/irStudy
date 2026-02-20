# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: appendicitis_116

## Clinical Context
- Differentials detected: colitis, cancer, appendicitis, ectopic, IBD
- Investigations mentioned: ESR, CRP, CT, ultrasound

## Transcript Excerpt
Now, we've kind of done our structure together. You have your structure. We've talked about history, differential physical examination. We want to take that to the exam and see how we go. Let's start on case number one, an interesting group of questions that we want to do. We'll jump to this one, my apologies. It'll go this one. Now, case number one, your next patient is a 27-year-old lady who presents to the emergency department complaining of abdominal pain. So in the context, you have a 27-year-old young lady female and it's just telling you, abdominal pain, you don't have any sight in the stem, you don't have any duration in the stem. This is where the problem starts that you just want to have one structure. You read your task. Your task is to take a history for four minutes. We are going to give you a prompt time. So in the stem, it'll be very specifically mentioned that we are going to give you a prompt time at four minutes, prompt time at four minutes. The prompt time will mean that you get a bell, you hear a mini bell inside of the station and ask physical examination from the examiner. They usually label this beside that task that you will only be given findings if you ask specifically. They're gonna solve a lot of problems with people complaining that I asked the question that they didn't give me the findings. So they're kinda labeled it when you ask physical examination. We're already telling you you have to be very specific and then explain your diagnosis and your differentials to the patient. Okay, so what we want to do together is, we want to kind of brainstorm together and go into this case into the exam. What I want you to do is, we will practice a little bit of a brainstorming together in terms of brainstorming, the way that brainstorming works is, when you're in the exam center, you're reading the stem outside. You have two minutes to think. This needs to be practiced on your side. When you're reading that stem, you have to think about a few questions. What do I want to go inside and do in this station? What is my plan in the next eight minutes inside this station? I'll give you 30 seconds, guys. I'll grab a piece of scrap paper, although in the exam you're not able to write down, but we just want to review everything that we learned together. Ask yourself, what is the list of differentials for this patient that comes to your mind? Second thing is, please try to map your history taking. In terms of mapping your history taking, you should be able to write down four boxes of things that you want to do and then put that differential diagnosis list into it. So I'll give you a few seconds, please think, do the brainstorming for me, then we'll jump into the case together, we'll see how we go. You Okay guys good. So this is what I needed you guys to think about. I have the structure in your framework in your mind. This is what kind of goes in my mind. Okay, in terms of abdominal pain, I have a young lady. Things that I want to definite

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/appendicitis_116/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/appendicitis_116/key_facts.json

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
