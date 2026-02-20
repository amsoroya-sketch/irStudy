# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: why_do_we_fail_310

## Clinical Context
- Differentials detected: 
- Investigations mentioned: 

## Transcript Excerpt
But why do we fail? So this is the important part that we want to talk about. Two components that we need to figure out together. On, let's talk about the first part before I go forward. Look guys, it is very normal to form emotions. Yeah, there is this osc.y examination deconstructing an osc.y written by a English, British psychiatrist. She says like one of the first emotional responses to failing osc.y exam, especially if you are IMG. is to stop blaming that college, that organization, that they are unfair, they want to fail us, they want to make money, racism, this, that. This is just an emotional response because you're still in denial. You don't take any part of the blame that maybe I didn't perform well. It's all their problem. I don't understand what, why didn't it pass me? I have to pass. I'm overconfident that I'm on a passing level. That's a normal emotional response. I don't know. I don't blame anyone for me. That kind of, that kind of emotion and that kind of feeling. But I usually tell these kind of people who start developing that kind of emotions around this, that before you step foot into this path, you know that this exam has a passing rate of 25%. Hopefully you knew, if you knew that if I walk into this exam, I already understand that chances, the odds of me failing are way more than the odds of me passing this exam. So there's something wrong there. But going forward, AMC on further March 2025, did this kind of workshop or session for course providers that I was in that session two and that was part of their talking about the exam to course providers. I was expecting someone to talk about it anyway. I think everything that was told to us in that session was kind of intended for you guys to hear. So I've kind of put a summary of why AMC thinks you fail. The first interesting thing is like AMC claims that they have around 7,000 examiners. That was, I was quite surprised. I was like, wow, that's a large number of examiners. As much as you think being a AMC examiner is a very big thing and a cool thing. Everyone has been an examiner in AMC and a consultant, the registrar, whoever you have in Australia, GP has been in that exam room once. They have a big cohort of simulated patients. So again, you do get the understanding that it does get a little bit subjective anyway because we're dealing with a large number of people. And they do like training sessions for the simulated patients and examiners. So the good thing is they have been doing a little bit more training on their role players in 2025. I've been hearing less problems with the role players compared to all the stores that I used to hear in 2019, 2020. The cases are very tightly scripted now. So you get better answers. Previously, we used to have a little bit of problems. And they usually do training and rehearsals for the cases that again makes it a little bit nicer. They are training their examiners that we are going to give you defined specific expectations. That means we'r

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/why_do_we_fail_310/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/why_do_we_fail_310/key_facts.json

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
