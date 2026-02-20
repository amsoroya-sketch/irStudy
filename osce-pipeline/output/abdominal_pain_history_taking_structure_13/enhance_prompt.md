# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: abdominal_pain_history_taking_structure_13

## Clinical Context
- Differentials detected: peptic ulcer, colitis, Reflux, appendicitis, IBS, reflux, IBD, hepatitis, cancer, pancreatitis
- Investigations mentioned: 

## Transcript Excerpt
Good, so first of all, welcome to our first medicine master class for 2026 exams. Usually, the first workshop is always a little bit of fun and depressing at the same time because we have to kind of set our structure for ourselves on the standing and kind of come to a agreement together how to be prepared for the exam. I see a lot of familiar cases. Most of you know me. For those of you who don't know me, my name is Amir. I'm a GP in Melbourne. I'm a pure 100% IMG. I've done this myself. I've went the wrong way. I've realized what I have to do to kind of do it properly and pass the exam. So today we're going to go a little bit slow. It's our first class. You want to get a good understanding about our structure. Now, throughout our discussions today on all the cases, the structure, I use a few references just to show you what I'm going to use. Usually, I like to refer to more to a lot. It's a lovely source of information. We're going to look at the useful pieces together for our management. The only person talking in the room is therapeutic guidelines, Australian therapeutic guidelines. There are occasional points that Australian guidelines ignore talking about a certain topic and we might look at up to date just to get a few pieces of information together. Now I know all of you guys have started your preparation and you hear this word a lot recalls and everyone is excited at the moment you hear the word recalls. Yay, we want to go find recalls and we're on a past exam with recalls. The only problem that we need to understand today guys, recalls will not pass you because all of you guys have recalls and everyone has recalls but you are dealing with a exam that has a 25% passing rate. Today, I'll be looking a lot at this tips from examiner document because it's going to give us a good idea about how AMC and the examiner's look at things. This is the only recent document that we have from AMC site that they told us to do this and avoid these things in the exam. The first thing that that document told you that please avoid premature closure. So I'm not sure if you've seen the cognitive biases video. We train our examiners that you should not pass the candidate who prematurely closes the case. Who is that person? The person who already knows the answer without obtaining sufficient data and information, which means you know the recall. I can clearly see you know the recall because you didn't ask the questions to come to that conclusion and we're not going to pass you. So at our first session, on our first discussion, we need to make agreement together. Either be the blue candidate or the red candidate. The red candidate is the person who wants to go, starts reading recalls, going to telegram groups, cry about what is the diagnosis of the case of abdominal pain that came out on 15th of March 25th. And then you know the recall, you know the diagnosis, you think you know something, you just go in the exam and let me do a few things about that diagnosis th

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_history_taking_structure_13/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_history_taking_structure_13/key_facts.json

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
