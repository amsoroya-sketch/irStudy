# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: indigestion_25

## Clinical Context
- Differentials detected: reflux, cancer, pancreatitis, gastritis, peptic ulcer, IBD
- Investigations mentioned: biopsy, endoscopy, colonoscopy

## Transcript Excerpt
a famous little bit old case, the indigestion case. Now the indigestion case specifically hasn't happened in 2025, but if you look at last year, previous years, it's a lovely case. It is a very challenging case, and it wasn't designed in the online exam. It's been a case of AMC four of the, it's one of those cases that even if it hasn't happened this year, I'm sure it will happen next year. I'll always pull it out of my pocket. It's very nicely designed. Before I go into the topic, this one needs a little bit discussion because it's a very vague complaint, what we're talking about is super vague, and you need to get idea about what we're doing. Let me just quickly show you this time, so you'll get idea about where we're going together. You have a 50 year old man or a lady, comes to you complaining of indigestion for six months. So two problems. You have a vague complaint, one that kind of have problems defining indigestion, what does that mean? Ooh, and it is chronic. Now this is a very complex case. This is one of your famous four task cases of the face to face exam. Take a picture for four minutes. We're going to give you a first prompt time. You'll have to manage your time for the next four minutes for the next three tasks. Ask a physical examination from exam, and then not only tell us diagnosis and differentials, but do also tell us investigations. So it'll be a little bit challenging to manage your time with beyond your first prompt time, but that's something you have to do. Usually just give you a general rule, guys. If you are in the face to face exam, you get any case that has more than three tasks. You tell yourself, that is not a case that I want to waste on by anything. I'll do essential things. Essential, nothing extra move on. I need to complete my task before I run out of time. Because if you do the best pee fee over here for three minutes and run out of time for investigation, unfortunately I cannot pass you. No chance at all. No matter how good you have been in the previous task. Okay, so we're talking about indigestion. If I want to give you indigestion, a better name, a name for you guys is dyspepsia. And so we are talking about a topic of dyspepsia. The problem that we face in this case is a patient who has heartburn, reflock, tells you how you have indigestion. The patient who has a little bit of upper abdominal discomfort of peptic ulcer disease, he has a pancreatic chronic pancreatitis, he has pancreatic pseudosis, will tell you I have indigestion. The guy who feels a little bit acidity burning, again, reflocks will tell you this. The guy who is bloated will tell you I have indigestion. And again, the guy who gets the standard extension and the stomach will also tell you I have indigestion. Now you can see indigestion is not clear at all. Whenever we do a case together that you have a presentation that is vague, all of you know, inexploring that complaint, there is a critical question. What is that? Before you go, you ask t

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/indigestion_25/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/indigestion_25/key_facts.json

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
