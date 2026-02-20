# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: physical_examination_form_examiner_structure_23

## Clinical Context
- Differentials detected: ectopic, appendicitis, pneumonia
- Investigations mentioned: colonoscopy, ECG

## Transcript Excerpt
Now let's get to the second component of a PC. Now for those of you who are hearing this word for the first time, from now on this will stand for Ask, Ask Physical Examination from your examiner. Now this is the famous task. I will say the most problematic task of the face-to-face example. If you ask me is the online exam easier or face-to-face, I'll say online was easier because you didn't have a PC desk. Now when you want to start asking physical examination from examiner, there's a lot of things that go wrong. There's a lot of points that kind of come in the way no one really knows what they want. There's a lot of versions of what to do at this point, and we have a lot of problems over here. But we want to talk about the concept together, just to kind of make a good understanding together. Let's go slow guys. So we want to kind of make a logical understanding rather than just listening to what I tell you. AMC usually in the history taking labels and scores you with this task. That they labeled this part as a Peefias. We want to look at their choice technique, organization and sequence. It is a long statement, but there is a few clear things over here. Organization and sequence. And the second thing is choice. If you look at it into the description of this task, they tell you that we want to see a relevant physical examination. That is relevant to the patient complaint. We want to see logical and efficient sequencing of actions. So sequence and organization is important for us. And it needs to include all the required elements. What does it mean elements like physical examination elements? If you're doing an abdominal examination, I will not pass you if you just asked me, Paul, patient for the end of this. Because it is abdominal examination. I want to hear all the elements of your abdominal examination. So you have to kind of be a little bit clever on how you do this. I'll use this. This is the only mark sheet that AMC has formally provided you. Also in the Peef, if nothing weird, is on the website later on in the specification handbook. At the end, they have appendix that they kind of at this only mark sheet of a shortness of breath. I just want you to read these two sentences with me. In terms of the examination finding, this is what they instruct the examinate. That the candidate must ask for each specific component of the examination. And findings should not be given to them where they do not specifically ask for it. What does it mean? Examiner, I want to do an abdominal examination. The examiner tells you what are you looking for. What does the examiner tell you that? Because they told me not to provide findings if they do not specifically ask for it. No examiner in the exam is going to go like, examiner, I want an abdominal examination. Okay, good. You have a tenderness on the right lower quadrant with rebound tenderness. We present bowel sounds with a normal DR. You have to ask it one by one from your examiner. And if you just look at t

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/physical_examination_form_examiner_structure_23/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/physical_examination_form_examiner_structure_23/key_facts.json

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
