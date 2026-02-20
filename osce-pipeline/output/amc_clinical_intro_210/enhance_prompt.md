# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: amc_clinical_intro_210

## Clinical Context
- Differentials detected: cancer
- Investigations mentioned: 

## Transcript Excerpt
Hi everyone, hope all of you guys are well and welcome to this discussion. Now this will be our first video that we're talking about the AMC clinical exam and I'm sure somewhere in your mind you're thinking about why are we having this discussion, why are we not rushing to recalls and doing cases and you know, doing structures. This is a very important discussion that we have to have with each other. Why is this discussion so important? Because I need you guys to know what you're dealing with. What is the exam? How is it designed? Who is the typical candidate? What are the problems in the preparation and having an understanding about overall what you're dealing with? Because when you look at the passing rates and I want to look at a few years ago, so we look at the last year, the last annual report that we have was still waiting on the 2025 passing rate. The 2022 to free and even before that. We are dealing with something around 25% of passing rates. So that means like one in every four of you pass this exam. That is a little bit strange because I'm sure out of those four people, three of them prepared very well, three of them are competing doctors, three of them have a lot of experience, they have a lot of knowledge, but they're still fed two of them are failing the exam. Only one is passing. Let's say one of them didn't prepare properly. Let's say one of them has been out of practice for a while and didn't study too much for the exam. And one of the reasons that we have been having such a low passing rate because we've been rushing for a shortcut, we've been rushing to tell me the recall, tell me the diagnosis, I want to study three months of recalls and I'm done with the exam and I want to go pass it. We kind of forgot that we have to understand the concept of the exam, how is the exam designed, what is the exam's purpose, what does it want to do and how does it do it? If you understand how the exam has been designed and if you understand how the exam is being scored and what the exam is looking for, you'll be way better prepared to pass this exam. So if you ask me again, why is this discussion important, please take the time to see these videos once and that's why we're doing it at the first medicine chapter because you have to understand what you are dealing with, what is the exam, what is the concept, whoever designed it on the first day and all the changes that happened later on. What is the sequence structure of this exam? As long as you understand it, it'll give you a way better preparation and I can promise you you'll be way better prepared for the exam and you'll have a way higher passing rate compared to the other people. Now we need to understand that this exam has two separate components, you have a knowledge component, you have a delivery component, why does this come in play because you have to go into the basics of a design of an oscary exam, the basics are based on the Miller's pyramid. So if you go and read medical education li

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/amc_clinical_intro_210/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/amc_clinical_intro_210/key_facts.json

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
