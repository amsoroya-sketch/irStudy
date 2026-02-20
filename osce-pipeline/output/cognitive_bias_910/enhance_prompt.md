# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: cognitive_bias_910

## Clinical Context
- Differentials detected: hepatitis
- Investigations mentioned: 

## Transcript Excerpt
So well and welcome to this video. So in this video, we want to talk about a new topic that I've decided to add to my strategic preparation videos. It's been something that has been around for a long time. I started getting a idea a little bit about this when I was studying for my fellowship exams for RACGP. And then when I started working as a more of a formal medical educator and started being trained for that, I realized like these are things that they train their examiners for. So all of your oscuxemps, you know, Australia, before they allow anyone to be an examiner, they usually train them for that examiner position. And it's interesting that part of this training, they always go over the cognitive biases, that cognitive biases are very important, especially in an oscuxem, because in an oscuxem, you're kind of showing off your thinking process and that kind of affects everything that you're doing and also the marking and the scoring of the stations. So let's go step by step. As I told you, these cognitive biases are part of the training of the examiner. So they kind of train the examiners that not to pass the people who clearly have cognitive biases. And today we wanna just see like what are the most famous examples of cognitive biases in an oscuxem, like AMC clinical. Again, having worked with you guys for the last few years have given me enough experience to kind of talk about this and do examples with you guys, because I'm sure many of you guys see this in your role, please, with your friends. So what is a cognitive bias? A cognitive bias is kind of a systematic thought process. So it's interesting that it's still a systematic thought process. But the main reason of it is the tendency of your brain trying to simplify things, trying to go for shortcuts. So the brain wants to simplify the information processing through a filter of either personal experience or preferences. So the way that you wanna do our oscuxem, like AMC clinical, that I wanna do it my way. And I need AMC to pass me on my way, that doesn't happen. That's when I tell you that you have to play AMC by the rules, not your rules. And by personal experience that you do know that personal experience in our storyline is recalls. So essentially a cognitive bias is that thinking process that you develop, that your brain wants to simplify is looking for shortcuts. I don't wanna know a structure. I don't wanna know differentials. I just wanna know the diagnosis and the recall and I wanna simplify it working towards a diagnosis. If I get to the diagnosis, I expect to pass. And hopefully by now, after seeing the strategic preparation videos, you do know that that doesn't happen. Well, let's look at a few famous versions of it. We have already talked about premature closing as being one of the most famous ones. I kinda got introduced to this a little bit early into my journey. I actually learned it from my Oscar exam of the fellowship exams. But what is a premature closing? It's a tende

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/cognitive_bias_910/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/cognitive_bias_910/key_facts.json

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
