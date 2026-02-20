# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: the_typical_candidate_510

## Clinical Context
- Differentials detected: 
- Investigations mentioned: 

## Transcript Excerpt
is we're going to look into a typical candidate. I decided to start it like this. And usually in this video and in the next few videos, many of you will tell me like, this was exactly me in my first attempt. Oh, this is exactly me now. But let's look at a typical candidate. Let's look at what they do. And let's look at what the result of that is. So a typical candidate starts the journey. Hope usually with booking the exam three, four, five months in advance. Yeah. And they start the journey with, okay. So they told me told about recalls. Yeah. Where can I find the recalls? And you start joining Facebook groups, telegram groups nowadays. And you start getting the recalls that people have made, the files that they've made. Then you start getting the notes that focus on the recalls at the end of the day. Yeah. Your M notes, your K notes, L notes, you put all those together. So you start with a ton of notes. The way that you usually start studying is you say like let's start studying backwards. So for example, I'm starting today, November 2023. And I'm preparing for February next year. So I'll start studying November recalls first, October recalls, September recalls. And I'll move back depending on how much time I have. And this is where the funny question starts coming up that. And me, how much recalls should I study? That is the moment that when you ask me this question deep down inside, I get a feeling of sadness thinking to myself that you're not definitely going to pass this exam. If you're still thinking about this exam as how much recalls I should study, you're not going to pass the exam. It's really not about recalls. So this candidate goes on. So start studying November starts studying October. After a few weeks of studying, she realizes like these recalls are super confusing. Yeah. So the way that people have recalled that incomplete stem, just two words like their recall, like my green case, what should I study about it? Yeah. What is the stem? What is the task? Where should I study? And that starts building a little bit of stress and anxiety deep down inside you that I'm trying to study, but what they told me the notes and the recalls are not helping. The problem with the recalls are the best thing you have I had to blur this by purpose because I don't want to be spreading recalls or stuff. The best thing that you can get is to go and get the past feedback that you do have a limited number of them. But again, the very problem with a past feedback is it is more helpful than the only two word that recall that they put on the groups. The guy usually writes you are very small stem and usually writes you free to four lines. And you want to study four lines and you want to learn the case. Yes, you do learn the diagnosis. Yes, you do learn the positive points, but what are you going to go? What are you going to do when you go into a eight-minute station of this case? You know four questions that are positive. You ask it. Then you'll start askin

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/the_typical_candidate_510/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/the_typical_candidate_510/key_facts.json

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
