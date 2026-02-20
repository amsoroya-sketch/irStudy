# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: upper_abdominal_pain_pud_15

## Clinical Context
- Differentials detected: cancer, pancreatitis, reflux, peptic ulcer, hepatitis, pneumonia, carcinoma, gastritis
- Investigations mentioned: 

## Transcript Excerpt
So let's start with the first case that we want to do in this cluster, again, upper GI problems. This will be just a continuation of our acute abdomen cases. Now, we'll start with this case together. You have a 32 year old man who presents your general practice. He has the very famous complaint of upper abdomen opane. Now he's a truck driver. I'm not sure what the significance in this case is, but anyway, he's a truck driver just tell you the occupation and you have a history taking for six minutes, diagnosed and differentials. So when you see such a case, you clearly know the predominant assessment area of this case is history taking. I will be mainly deciding if I want to pass or fail you on the structure sequence of your history taking the way that you do it and also the list of differentials that you kind of integrate into your structure. Let's just have a quick review about this case. Just go step by step doing it as more of a natural form. Then I'll show you the findings. So we already have a structure just for the purpose of reviewing it one last time. It's a abdominal pain case. I'll jump in. I still will have hemodynamic stability on my mind. We'll ask the examiner just so that the patient is stable, tell me the vital sons will get over quickly, sit down, introduce yourself. Your regular open ended question by now. You know how you want to ask it. What if the way you've decided to do it, how can I help you today? Tell me more about your pain. Now, this pain usually starts with this story line that, yeah, I have a pain in my left upper side of my stomach. And now this is a new area that we're covering together. Okay, so I've been having a pain in the left upper side of my stomach. It's been going on for some time now. And sometimes it's not exactly a very acute pain. And as usual, I'm a little bit worried about it or I need help. And you want to add risk to concern of your patient. You want to build that initial conversation, bridge the case into your questions. What are the words you've decided to do that? I'm really sorry to hear that. I understand your concern. Let's go through this together. I'll figure out what's going on and I'll try to help you out as best as I can. Now, let's go forward. Is that okay with you James? James is happy. Let's get to the pain. We want to explore the pain. We've already done this together. So the site is already clear, but I might ask the patient, can you just clarify one more time? Where do you feel the pain? Who tells you in the left upper side? Just as a heads up, there have been a few cases that the patient has shown his epic gastric area. To be honest, we wouldn't change my structure. See it in the left upper side, doctor. It's in the middle upper side of my stomach. Okay. You asked the intensity. Please scale it for me. One to 10. 10 is your worst pain. How about is your pain today? Tell me the quality. The patient describes this pain that I have a dull ache. And so this might be a little bit criti

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/upper_abdominal_pain_pud_15/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/upper_abdominal_pain_pud_15/key_facts.json

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
