# Expert Enhancement Request

## Agent: history-taking-expert
## Station Type: history_taking
## Slug: abdominal_pain_young_cluster_916

## Clinical Context
- Differentials detected: peptic ulcer, cancer, Crohn, reflux, IBD, hepatitis, appendicitis, colitis
- Investigations mentioned: 

## Transcript Excerpt
cases of the online exam, quite recent, 2023 and 2024, they have happened a number of times. The big difference of this cluster compared to the other abdominal pains that we've done so far is you will have them in young patients. So if you look at all of the previous cases that we've done together, most of them were mid-age to elderly group of patients and most of them 95% of your cases where I acute cases now we're going to talk about chronic cases. Cases that tell you I've had abdominal pain for a number of months and it's not getting better. So we'll start looking at this together. I'll call this the young cluster and we'll just have a chat about it. Now let's do case number one. You have a 16 year old boy. He's presented to your general practice, his complaining of abdominal pain. So you have abdominal pain in a very young patient and the idea is the fact that you don't know the acuteness or the chronic nature of this pain. You have to take a history when it came out in the online exam and if it comes out in the face-to-face exam obviously it's going to be for six minutes. Physical examination happened in the online exam. On a card you may still get a puffy. So in the online exam they used to put it on a screen. If they want to just drag that structure to a face-to-face exam they'll give it to you on a card. At this point when you hit your prompt time the exam gives you a piece of paper that all your examination findings are written on it. I'll show you what came up in the online exam. You need to expand your diagnosis and your two frontials. Now the way that I'm going to do this one I might ask you one question. By now you have a great structure. You don't want to change anything on that. You do have a great list of differentials. You don't want to change the concept of that. Imagine you start asking me general GI questions and you start getting a lot of GI symptoms in this case. So let's say this is how the case goes. In the Cicora you find out it's chronic, number of months. When you go into GI symptoms you find weird stuff. You find diarrhea, you find maybe constipation, maybe bloating. That kind of signifies the fact that okay the intensity of GI symptoms in this case. Maybe I want to expand my GI group. I want to expand my GI group. The first thing that you have to answer the first question are you going to skip red flag questions because this is a young patient and we don't expect the cancer? Their red flag questions are here because they are red flag questions not necessary for cancer. And again I'll say you're like I'll agree a 16 year old can I have a cancer but if you tell me 20 30s I still can be a cancer. But it's the questions that you ask the blood in the stool is the loss of weight appetite, problem tightness that also happens in other conditions. The second question that I want to ask you is in our structure we had cancers. We just did medications and surgery. So if you look at our previous cases that we've done our structure

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
Structured Markdown saved to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_young_cluster_916/clinical_notes.md
Also save structured JSON to: /home/dev/Development/irStudy/osce-pipeline/output/abdominal_pain_young_cluster_916/key_facts.json

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
