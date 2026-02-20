# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: studying_plan_2026_610

## Clinical Context
- Differentials detected: 
- Investigations mentioned: 

## Transcript Excerpt
Hope all of you are well. And let's get to one of our last videos on strategic preparation for AMC clinical. So in this video, I'll be talking about study planning. And I'll be doing it in three separate parts, initially talking about why I want you to have study planning and make a plan for yourself. Secondly, talking about what are the concepts that you have to think about and apply to your plan. And at the end, I'll tell you like, if I was to make a plan again to study for AMC clinical, how would I do that based on the experience of the last three, four years of working with you guys, seeing what you do, the common trends. And I know most of you know by now that the common trends are not working for this exam, you can just look at the passing rate and just realize that things that people are doing over and over again, obviously are not working for this exam. So hopefully please trust my experience on this. Again, what I'll be telling you is partly the experiences that I've had with many people looking at the past candidates and at the same time looking at the failed candidates. And I have also been a candidate of this exam up in through the entire emotions, the stages, the thoughts that you go through. I have tried to pass this exam with a short cut, just coming down to the conclusion that there is no short cut in passing this exam. So you really have to be clever. And I don't call it a good study planning or someone who studied more is just about being clever, being clever using the time you have in the best way possible. But what is our goal out of this discussion? The thing that I want you to do after you finish listening to this video, you have to really sit down with yourself and sort this out. Because most of you have exams coming up in two or three months time and this is the point that you really have to have a plan in front of you. You have to have a step by step plan just to help you manage your time and manage all those unexpected events that are going to happen in the next few months that will interfere with your regular planning that you've done. I want you to avoid wasting time. Unfortunately, it's not that all people who are failing this exam don't study but many of you study and prepare in an incorrect way that I've already talked about the typical candidate who role plays 12 hours based on your notes just the recalls with their study partner. They've actually put a lot of time and energy into it but they've wasted time because just close to the exam, they realize that memorizing those recalls is not going to help them. And the reality is that I want you to use that time in the best way possible. So we are going to focus on the key word, the best way possible. And this is the point that becomes a little bit important whatever amount of time you have. Each and every one of you will be different. And this is one thing that I need to tell you at the beginning of this video. I know you guys expect me to give you a structure, a plan

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/studying_plan_2026_610/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/studying_plan_2026_610/key_facts.json

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
