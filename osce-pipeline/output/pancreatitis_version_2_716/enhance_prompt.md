# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: pancreatitis_version_2_716

## Clinical Context
- Differentials detected: cancer, hepatitis, pneumonia, pancreatitis, reflux
- Investigations mentioned: lipase

## Transcript Excerpt
story, just a slight difference that you have a patient 25 year old with upper abdominal pain. The only difference is we're giving you investigations in the stem. That makes the case a little bit stupid, yeah? Your task is still to take a history. You need to explain the results to the patient and you need to tell him the diagnosis and the differentials. I don't like this case because when I tell you the lipase is high, everything becomes pancreatitis, makes it a little bit hard to do a nice history taking. But the reason that this case becomes a little bit harder, the stem has made it very specific its pancreatitis. So you will only pass in one situation. That is if you rule our causes of pancreatitis. I will do the same structure that we did in the previous case, but what you need to pass this very super specific case that I told you in the stem its pancreatitis is causes of pancreatitis. When I get extra time, I will still look into ruling out my other differentials, but I'll say in such a case, your priority is not differentials. Does everyone get the point? The way that the case has been designed. I'm checking your knowledge specifically about pancreatitis. So you stick to the same structure, same structure, ticks off your boxes. The reason that it ticks off your boxes is after we did the secura, we came back to the conclusion that pancreatitis is the most common probable thing we ruled out the causes. Although this I really wouldn't worry about. I will still continue ruling out the differentials, but wherever I run out of time, I don't care because I've done my job. Let's just get to the investigation and explain the investigation. With the investigation, let's keep it simple and stupid. If I roleplay this with anyone and anyone starts like, yeah, we have free lines up cells in our blood. That's the moment that I know we're not going well. You want to quickly tell me, what is that high white blood cell? What is happening? What is that light paste? What is happening to the liver? This is a slight issue over here. Question. We're sure this is pancreatitis. The question for you guys to answer here before you go into the exam is, is a mildly raised ASD and ALT okay to see in pancreatitis? Or is this hepatitis or colocystitis? I don't know, colanitis? What do you think? So my question is it okay to see a certain amount of raised liver enzymes? Yeah. Because once you have pancreatitis, again, sticking to the liver, ducts are connected to each other. It is normal, okay, common to see a slight mild change in your liver enzymes. You do know in terms of the liver enzymes, whenever we want to look at a hepatocelular pattern, we usually say four, five, more than 10 times eight times the normal limit. So if you see, like for example, the ASD, ALT, your upper limit that you have in the exam is 40 or 50. And it's less than two to three times. I'm not concerned about that. I'm not going to call this, this is pancreatitis because colocystitis or pancreatiti

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/pancreatitis_version_2_716/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/pancreatitis_version_2_716/key_facts.json

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
