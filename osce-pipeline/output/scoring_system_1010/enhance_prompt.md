# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: scoring_system_1010

## Clinical Context
- Differentials detected: DVT, meningitis, stroke, MI, heart failure, cancer
- Investigations mentioned: ECG

## Transcript Excerpt
talking about the scoring system. Now, the scoring system is going to be an interesting topic to talk about, but at the end of the day it's going to be depressing because we're going to look at a lot of real feedbacks of real candidates who have gone into the exam for the last number of years and we're going to see that the scoring system is a little bit harsh and a little bit tough. But the importance of this discussion is when I run an OSCE and obviously I get you to perform a case that OSCE needs to have an outcome. Your outcome is your result, it's the idea that if you pass or fail. Essentially we have to think about what is the process of making that decision if I pass or fail and essentially the process that they are using is the scoring system. Now it's the scoring system that decides if you pass or fail, in case any if you understand the scoring system at least understand the parts that are understandable, not the subjective and unpredictable components. It might help you a little bit to deal with this exam and your preparation and your performance a little bit better. AMC has come in their annual reviews a number of times and they've kind of mentioned it formally that we are using a new scoring system and it's interesting that every time they come out and say we're using a new scoring system we're using a new mark sheet or scoring grid. What happens is you have a significant drop in the passing rates. I say the most significant one was in 2015 after they announced that we have relooked into our scoring system. That's when you're 60, 70% passing rate dropped down to 25% so obviously the scoring system did something to us because how did a 70% passing rate, 60% passing rate in the previous year suddenly end down to 25% 20% passing rate. So it's clearly the scoring system because I want to say IMG suddenly at 2015 were less knowledgeable. So that scoring system obviously wanted something new from us that it has taken us a number of years to realize what they really want and AMC obviously doesn't want to come out and talk about this. So in this video we're going to deep dive into the scoring system, try to talk about the things that AMC tells us and then look at real life experience. Now you already know that you're going to get 16 stations in the exam, 14 stations are going to be scored, two stations will be pilot stations, you do not know which stations are pilot stations. AMC keeps on saying that we're going to use new cases as our pilot stations. I actually made fun of that point in the AMC conference in September that go check your exams, 90% of your pilot stations are well known cases and it is a little bit unpredictable, unfortunately we've had new cases pop out in the exam for the first time and from day one they happen scored stations. So you really don't know which two stations are your pilot stations. So as we've discussed before you want to approach the exam as 16 stations and do your best on all 16 stations, you really don't kno

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/scoring_system_1010/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/scoring_system_1010/key_facts.json

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
