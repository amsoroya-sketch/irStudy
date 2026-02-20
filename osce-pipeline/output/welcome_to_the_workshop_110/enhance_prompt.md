# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: welcome_to_the_workshop_110

## Clinical Context
- Differentials detected: 
- Investigations mentioned: 

## Transcript Excerpt
Hi everyone, hope all of you are well and welcome to this workshop. First of all, thank you for enrolling for this workshop and hopefully you'll find it helpful. I thought to take a few minutes just to introduce you to the workshop, talk about the different components and for those of you who are meeting me for the first time, just introduce myself. Although I know for a large group of you guys you've already heard about me, you know me, but I thought it's nice to just introduce myself properly. As you know already, my name is Emir, so I'm an IMG and I'm a GP in Melbourne. I'm a fellow of RACGP and I've been involved in teaching for AMC clinical since 2018 and I've held like multiple medical education roles in Australia with RACGP, with Melbourne University and so on. Now about this workshop guys, it kind of has two components just to give you a heads up about what's going to happen. We have the first component that is called the strategic preparation for AMC clinical and you're going to find a pack of videos. That in the next few days is just going to get a little bit more complete until it becomes the entire bundle and later on we're going to start our live sessions of Medicine Masterclass Chapter 1. Regarding the first component of strategic preparation for AMC clinical, this is just the evolution of a class that I used to do a long time ago and I used to call it let's talk about delivery. So I used to talk about the exam itself, the scoring system, what does the exam contain and what does it want from you and I always find that one very important component of preparation for AMC clinical because I can always get you in my class and from day one, second one, start doing cases, recall number one, recall number two, but if you don't have a good understanding about what AMC clinical is doing, how's it been designed, how is it scoring you and what you need to do to pass it. It's really not about recalls notes or cases. You have to understand what you're dealing with and I promise you as much as the videos will be a little bit longer and I'll take you a few days to see them. Once you finish them, you'll kind of be noting and thinking that I have a better understanding about AMC clinical now and what they need from me. I want you to see that video in your spare time whenever you have time. They are not videos designed for you to have your notebooks in front of you to write down the entire theme, but you might need to jot down a few key points for yourself just to understanding about the exam itself. Make it make it one piece of paper, have it at the beginning of your notes just to remind you what you're going to do in your entire preparation. It does contain a few videos so I go through the basic of AMC clinical, I go through the scoring system, I go through the reasons why you fail or talk about how to have a strategic preparation. So there is one video on preparation planning that is an interesting video and I want you to definitely see that one. 

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/welcome_to_the_workshop_110/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/welcome_to_the_workshop_110/key_facts.json

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
