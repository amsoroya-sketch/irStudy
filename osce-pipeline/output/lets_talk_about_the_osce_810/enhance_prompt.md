# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: lets_talk_about_the_osce_810

## Clinical Context
- Differentials detected: cancer, meningitis
- Investigations mentioned: ECG, MRI

## Transcript Excerpt
Hi everyone, hope all of you guys are well and welcome to this video. Now we've been talking together for a couple of hours so far talking about the exam, the blue, green and about the exam day and all of these topics have to prepare for the exam. But now we want to start looking at our osuke exam in a more professional way just to get a bit of understanding about how can we prepare for it a little bit better. As all of you know, AIMC, the best example of osuke exam, the OSC and E stand for objective structured clinical examination. So we already know that we are doing a clinical examination that's out of the way. But we want to focus a little bit more on the objective word and the structured word. Now what do they mean when they say like osuke is structured, the way that they designed the osuke is extremely specific. Why is it specific? Because I cannot give you a general case of, okay, your patient has come to you with headache, tell me what you want to do. That is a little bit too general. In eight minutes someone might talk more on examination, someone might talk more on management and at that point I have a little bit of difficulty on who I want to pass. In terms of being structured, it is specific meaning that you have tasks. So I will be giving you cases because of the time limitation we have. In each case, I'm going to focus on a certain area, on a certain task, very specific task. That your task is kind of the predominant assessment area. For example, in eight minutes I want to assess your history, taking skills, I'll give you headache case, you take history for me and tell me diagnosis and differentials. I want to look at your diagnostic formulation. I'll give you a chest pain case, take history, I'll give you an ECG formula, your diagnosis based on the findings of your history and your ECG. This is the way that we are kind of looking into this together. So an osuke exam will be extremely structured, extremely specific. You have very specific tasks because that specific task needs to come over here and give you an exam in a marksheet. Now, no one can ignore and deny the subjective nature of an osuke exam because if I'm a nice person, I'm on a good mood, I've had my coffee, obviously I have a high chance of passing you compared to my bad day. When I'm a little bit grumpy, I haven't had my coffee, I haven't slept well, I might be a little bit more tough on passing you. And when I use the nice guy, Alex is the hard, tough guy. Obviously, these guys have different passing rates. There is a little bit of a subjective nature in an osuke exam, but to kind of counter that, we need to make it as objective as possible. And the only way to make it objective for a mirror and Alex to score the candidate, preferably similar or quite similar is to give him a marksheet. Now when you give him a marksheet, you have to make that marksheet so specific and by specific, I mean, I have to write down boxes. Did Emir and Alex have to tick off box one tick off? 

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/lets_talk_about_the_osce_810/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/lets_talk_about_the_osce_810/key_facts.json

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
