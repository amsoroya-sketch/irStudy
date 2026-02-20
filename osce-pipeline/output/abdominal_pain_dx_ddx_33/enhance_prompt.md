# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: abdominal_pain_dx_ddx_33

## Clinical Context
- Differentials detected: pneumonia, appendicitis, ectopic, cancer
- Investigations mentioned: ultrasound

## Transcript Excerpt
Step number three, or sometimes two, let's get to the diagnosis and differentials. Now if you ever asked me like, where do you think we fail in the exams, usually this component. So if you ask me now, if you ask me two weeks before your exam, what should I do? My answer is always the same differentials. First understanding is you have to come down to the conclusion that you're not good at differentials. When I say you're not good at differentials, not that I'm saying you don't have knowledge for differentials, but the way that I need the state that I need you to be is when I tell you differentials, you have to close your eyes, tell me 20 differentials in 20 seconds. If you're in this mode in the exam, that appendicitis, cancer, this, you already run out of time and I'll see in the next exam. It needs to be on the top of your mind. If your differentials are not solid in your mind, your history taking will never be good. Because it's a foundation of your case. If you don't know differential, it doesn't pop up in your mind. What do you want to do in your history taking step number three? So if you ask me, what do I have to do to pass this exam? I'll tell you, grab yourself a small notebook. In any case, we do any cluster. Please write out that differential, list and repeat it so many times. Read it out to yourself so many times when I tell you differentials for chest pain, you close your eyes and tell me 50 differentials. Sequence, groups, specific, nice differentials. Now, the way that AMC looks at this, this is what they say. That you need to integrate the history examination, finding and relevant investigation as appropriate. You need to consider the likely conditions that could explain the patient symptoms, that this is kind of telling you that you need to tell us the provisional diagnosis. Now, this one is very interesting for me. I will get this question a lot. We'll start the first case and someone asked me like, on the history, the lady says she doesn't have fever. So should I still bring the infections in my list of differentials? At that point, I tell you that your list of differentials is made towards your complaint of your case in the STEM, not towards your diagnosis of what you found inside of the history taking. So when you told me you have a patient lady with low abdominal pain, without asking any further questions, a list of peers in my mind, I start ruling them out one by one. So someone will say like, you know, bowel can't say in a 30-year-old man, should I ask that question? We need a sufficient, complete list that includes the unlikely, but important diagnosis. It's useful to answer. Yeah, I agree it's unlikely. Let's likely. But if you missed that one rare case, no one will agree. The coroner will say like, okay, I agree it was rare. Maybe you shouldn't have asked questions. That is one more that tells you serious disorders that you should not miss. Never miss. I don't care how rare they are. They are pitfalls, they are serious.

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_dx_ddx_33/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_dx_ddx_33/key_facts.json

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
