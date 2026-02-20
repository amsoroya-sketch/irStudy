# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: pid_216

## Clinical Context
- Differentials detected: appendicitis, ectopic, cancer, hepatitis
- Investigations mentioned: ESR, CRP

## Transcript Excerpt
This one is interesting. So your next version is a 19 year old lady who presents the complaining of abdominal pain. This case will give you a very good idea about predominant assessment areas. Your task in this case is take a history for six minutes. Explain diagnosis and differential to the patient. Now you read this case. This is more of the online exam version. This case is a new case in this cluster that started around two years ago in the online exam back then we just had online exams. A very young lady, abdominal pain. You don't have any further information and disturb about duration, location, nothing. So apparently you're black. So in that blankness of this case, you have to think about your history taking. Now in your brainstorming, you quickly think about your critical differentials. You know how to do that by now. You quickly think about your structure. Okay, when I go in intro, the few things that are important. Remember to add rest of concern, explore the pain, I'll re-know my differentials. These are the things that I'm not gonna forget. Squeeze it in six minutes. And in six minutes you have a lot of time. So if I wanna just quickly run through the case and what is the difference of this case that I have six minutes, this is how I'm gonna go. I'm just re-writing down the structure one for the reason of repetition, second for probing further. So you go in, that I did check you sanitize your hand, you sanitize your hand. So that is, let's say, marry your patient. You go sit down, introduce yourself. You ask him a dynamic stability from the examiner. The examiner tells you the patient is stable. Just proceed, don't even ask me, okay? Your grumpy examiner, but thank you for confirming that he's stable, she's stable. So, marry, my name is Amir, I'm your doctor for today. Tell me, how can I help you? You wanna do it a little bit differently. From the notes I can see, you've been having some pain. Tell me more about your pain. This patient starts selling your opening statement that yet, I've had this pain in the right lower side of my stomach. This has been going on for a couple of days. And it is getting worse, which has made me a little bit worried and I want you to check it out for me. Okay, so same statement as usual. Now, have a slide now, have a little bit of understanding about the timing and obviously as usual, your concern as any patient will be. I'll add rest and respond to your statement. I'll acknowledge it. Yes, that is stressful. And the stand you've been having a tough time in the last couple of days. I'm here to help you. And I'm really sorry that you've been experiencing this pain. But to better get a bit of understanding about the pain, we will need to go through a few questions together to figure out what's happening. Is that okay with you? Yes. Now, are you in any pain now? Yes, I am, doctor. Do you want a painkiller? Let's say Mary says, yes, I want some. I'll arrange the nurse to give you some painkillers by the time 

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/pid_216/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/pid_216/key_facts.json

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
