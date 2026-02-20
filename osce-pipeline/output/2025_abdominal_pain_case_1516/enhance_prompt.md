# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: 2025_abdominal_pain_case_1516

## Clinical Context
- Differentials detected: cancer
- Investigations mentioned: 

## Transcript Excerpt
the 2025 case, let me just check it. So I'm going to say one year. I'm just going to talk about the diagnosis. Nothing with it is new. But when I started seeing the recalls, everyone started calling this case. I've got a strange case. OK, let's look at your strange case. So I mean, 60-year-old guy abdominal discomfort. So nothing strange so far. History for six minutes. Expand diagnosis and your differentials. OK, I went and did a structure. I laid out my structure. So abdominal discomfort went to you. And explored the pain. General GI questions. Red flags went in. These are your findings. Now, really guys, tell me your diagnosis. Pain in the lower abdomen. How bad is your pain? 1, 2, 10. One is your least pain. 10 is your worst pain. One. OK. How long? One month. The patient, the moment you ask him about constipation and diarrhea, gives you this. The doctor, I have constipation and diarrhea. And they change. Yeah, I have about constipation and diarrhea alternating. Oh, is it a virtual biosinter? You have loss of weight. How much? 5 kilos? How long? Last month? Intentional? Not intentional. Any blood in your shoes? Yes, blood? They have bowel cancer in your family? Yes, in my aunt? Have you done your screening? Yeah, I did my screening and it's normal. 60-year-old man guys choose diagnosis. Someone asked me at the beginning of today. I might not pass you if you don't get the right diagnosis. Hey, good job. Rest of you. No matter what the age is, the first thing top of your list, bowel cancer. So I asked all the people who recalled this. What was strange with this guy? I mean, here, the guy had IVS findings. And I told them, I'll shoot myself in the head. I told you, red flags, no IVS. Any red flag, no IVS. Don't even talk about it. But I got more confused. The moment he said he's done a bowel cancer screening last year and it's normal, I still go more confused. Like, can this be bowel cancer? What do you think? Still bowel cancer. I am very concerned of you having bowel cancer. Why changes of your bowel habits? Loss of weight, blood, family history, what else do you need? A typical easy case of bowel cancer. This is not IVS. Definitely not IVS. Even if you have other criteria of stress or whatever, I will not care about this. You did it last year, it's 12 months ago. Now it's now. Yeah, doesn't mean if it last year was fine, it's fine now. I still want to consider the fact that the most likely diagnosis of you will be bowel cancer. Everyone agrees that it's not strange. Yeah. So we kind of clarified IVS a little bit more this year.

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/2025_abdominal_pain_case_1516/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/2025_abdominal_pain_case_1516/key_facts.json

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
