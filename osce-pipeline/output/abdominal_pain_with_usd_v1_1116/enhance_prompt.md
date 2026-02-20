# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: abdominal_pain_with_usd_v1_1116

## Clinical Context
- Differentials detected: reflux
- Investigations mentioned: ultrasound

## Transcript Excerpt
Now you have got this case a few times throughout the year, so let's read it out together. Your next patient is a 40-year-old man who presents your general practice complaining of ongoing abdominal pain. He has done a recent ultrasound and it shows gallstones in the gallbladder, but there is no inflammation in the gallbladder. There is no inflammation, there is no thick wall, there is no features of colesis thitis in this case. Now I'll label this as one of the two cases that you have ultrasounds in abdominal pain cases. So you do have overall two cases, this is the 20-25 case. I'll add the other cases as a recording after class, you can see that one. That one is a lady with a right lower quadrant pain. With an ultrasound that goes towards being a middle spurs, but it's a very interesting design of a case that they give you an ultrasound, they leave a few points in the ultrasound. In that case you also have a gallstone with no inflammation in the gallbladder, no features of thickness in the wall and whatever inflammation there. The lady is very concerned about colesis thitis because her mother had colesis thitis. This is the newer version, so we're going to do this together and see how we go. Take a history from the patient for six minutes, obviously your diagnosis, your predominant as a scenario is going to be history taking, expand your diagnosis and your differentials. I'll just ask you a question. Do you think this case can be a colesis thitis or biliracolic? The question that I'm asking, do you think the designer is so stupid to give you a case that understands you have abdominal pain, you have gallstones, please come in and make the diagnosis of colesis thitis for me? Funny enough, some people are still made the diagnosis or biliracolic in this case. I'm not just talking about a few people. Let's go in. These are the features that you get. Let's go in and do a structure together. Have a lot of stability first. I'm going to just tell me if I want to know if it's stable or not vital signs. An open-ended question, yeah, doctor, so I've been having this pain. I recently did a scan. They told me I have gallstones. The pain is ongoing, not getting better. Let's go through a pain assessment together. Tell me more about your pain. There is the pain in the upper abdomen. Now, tell me specifically where is it? It's in the middle, upper middle. Okay, good. Tell me the intensity, scale of one to the end. Tell me the quality, is it double-shot? Tell me the timing. How long have you had this? Is it on and off? I'm just doing a basic secore or nothing weird. Is it getting worse? It's just staying the same doctor and not getting better. Is there any radiation? Is there anything that makes it better or worse? Doctor, I've noticed when I eat, it gets worse. Okay, so let's probe this a little bit further. Is there any specific food that makes it worse? Yeah. And how soon after eating, do you get the pain? Now, with this secore, your next step is general GR qu

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_with_usd_v1_1116/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_with_usd_v1_1116/key_facts.json

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
