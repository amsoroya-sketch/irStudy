# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: traumatic_abdominal_pain_1316

## Clinical Context
- Differentials detected: 
- Investigations mentioned: ultrasound, CT

## Transcript Excerpt
a total another concept. So let's look at the case. Your patient is a 16-year-old boy. He's come to the emergency department after he fell from his bike. So now this is a traumatic abdominal pain. He's complaining of pain at the very famous site that you have a physical examination, case buffing the online exam and the face-to-face exam in the left upper quadrant. You're asking us to take a five-minute history taking. We don't have any task of physical examination over here. Tell us your diagnosis and differentials and tell us the weird management. It's a little bit hard if you don't want to tell us what exactly the condition is but I think the management obviously is pointing towards the immediate urgent investigations that you're going to run for this patient in the emergency department. So let's do a practice with this case together. As you know this case is not a new case as such because we always have an physical examination, quite a famous case. In the face-to-face exam they used to have blood in the urine. So used to be a kidney injury. In the online exam used to go more towards a kind of a splenic injury. But I want you to think about this and just to prepare for new cases. Let's say you have a case of this in your exam and it's a new case. Try to think about what structure you want to apply. And I want you to do this on purpose. I want you to feel that let's say you have a case that you don't have any idea about. But you have a structure. Yeah. Just think about okay I know that structure. Let me put it in the context of this case. What I want to ask this guy. So I'll give you 30 seconds. Write it down for yourself at the end. I'll ask you to look at it. Yeah 30 seconds. Exactly. Yeah. So even if you don't have any idea about this case, still have a problem with no pain. And even if you just stick to your structure, you're still going to rule out everything that is important for me. Let's do this together. So you have a traumatic patient. Definitely want to do hemodynamic stability, even if you didn't have a problem with no pain. Yeah. Just want to make sure you're all good. I'll start with an open-ended question. You know what the patient is going to answer that yes, just how to fall. I was riding my bike. I nearly hit a car. You know, I tried to kind of stare away and I fell and I have pain in my stomach. You're going to be nice to that little teenager that I understand I can be concerning. I know you're stressed. I know you're scared, but let me ask you a few questions. We'll do some investigations. I'll find out what's happening and we'll make sure everything is okay. Once you do that, we step forward into our complaint. Our complaint is still an abdomen open. Easy. You want to do a secora. In terms of the secora, everything's going to stay the same. Where's the pain? Where do you feel the pain? Where's the side? Tell me the intensity. The quality is still important for you. In terms of the onset, you have a very super acute case that

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/traumatic_abdominal_pain_1316/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/traumatic_abdominal_pain_1316/key_facts.json

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
