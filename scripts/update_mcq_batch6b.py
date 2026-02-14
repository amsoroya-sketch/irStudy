#!/usr/bin/env python3
"""
Update MCQ Batch 6B - ENDO-MCQ-0061 to 0080 (20 MCQs)
Sub-batch 2 of 5 in Batch 6
Topics: Diabetic Neuropathy (12) + Thyroid Nodules (8)
"""

import json
from pathlib import Path
from datetime import datetime


def update_mcq_batch(file_path, generated_mcqs):
    """Update MCQ file with generated content"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    updated_count = 0

    for i, mcq in enumerate(data['mcqs']):
        mcq_id = mcq['id']

        if mcq_id in generated_mcqs:
            gen = generated_mcqs[mcq_id]

            mcq['question']['scenario'] = gen['scenario']
            mcq['question']['stem'] = gen['stem']
            mcq['question']['options'] = gen['options']
            mcq['correct_answer'] = gen['correct_answer']
            mcq['explanation'] = gen['explanation']
            mcq['generated_by'] = "claude_code"
            mcq['generated_at'] = datetime.now().isoformat()

            updated_count += 1
            print(f"✅ Updated {mcq_id}: {gen['subtopic']}")

    data['metadata']['claude_code_generated'] = data['metadata'].get('claude_code_generated', 0) + updated_count
    data['metadata']['last_updated'] = datetime.now().isoformat()

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Saved {updated_count} updated MCQs")
    return updated_count


# Batch 6B: ENDO-MCQ-0061 to 0080
batch6b_generated = {
    "ENDO-MCQ-0061": {
        "subtopic": "Diabetic Peripheral Neuropathy - Presentation",
        "scenario": "A 58-year-old man with type 2 diabetes for 12 years (HbA1c 8.9%) presents with 6 months of burning pain and tingling in both feet, worse at night, affecting sleep. On examination: reduced sensation to light touch and pinprick in both feet in stocking distribution, absent ankle reflexes, normal foot pulses.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Peripheral vascular disease",
            "B": "Diabetic peripheral neuropathy (sensory polyneuropathy)",
            "C": "Vitamin B12 deficiency",
            "D": "Lumbar spinal stenosis"
        },
        "correct_answer": "B",
        "explanation": "Diabetic peripheral neuropathy (DPN) is the most common complication of diabetes (30-50% prevalence). Presentation: (1) Sensory symptoms: numbness, tingling, burning pain (hyperalgesia), allodynia, worse at night; (2) Distribution: symmetrical, 'glove and stocking' (distal to proximal); (3) Loss of sensation (pain, temperature, vibration, proprioception); (4) Reduced/absent ankle reflexes. Types: (1) Sensory (most common - 80%); (2) Motor (foot drop, hand weakness); (3) Mixed. Risk factors: poor glycemic control, duration of diabetes, age, smoking, hypertension, dyslipidemia. Examination findings: (1) 10g monofilament (protective sensation - inability to feel = high ulcer risk); (2) 128Hz tuning fork (vibration sense); (3) Pinprick, temperature discrimination; (4) Ankle reflexes. This patient: classic DPN - distal symmetrical sensory loss, burning pain, reduced reflexes, preserved pulses (not vascular). Investigations: Clinical diagnosis usually; exclude other causes (B12, TSH, serum protein electrophoresis if atypical). Management: (1) Optimize glucose control (prevents progression); (2) Neuropathic pain management; (3) Foot care education."
    },

    "ENDO-MCQ-0062": {
        "subtopic": "Neuropathic Pain Management in Diabetes",
        "scenario": "A 62-year-old woman with diabetic peripheral neuropathy has severe burning pain in both feet (pain score 8/10), interfering with sleep and daily activities. Her HbA1c is 7.2%. She has tried paracetamol without benefit. eGFR 55 mL/min.",
        "stem": "What is the most appropriate first-line pharmacological treatment for neuropathic pain?",
        "options": {
            "A": "Tramadol 50mg as needed",
            "B": "Pregabalin 75mg twice daily OR Duloxetine 60mg daily",
            "C": "Amitriptyline 10mg at night",
            "D": "Morphine controlled release"
        },
        "correct_answer": "B",
        "explanation": "Neuropathic pain management in DPN (stepwise approach): First-line: (1) Pregabalin (start 75mg BD, increase to 150-300mg BD based on response/tolerance); OR (2) Duloxetine (start 30mg daily for 1 week, increase to 60mg daily); OR (3) Gabapentin (start 300mg, titrate to 900-3600mg/day in divided doses). Second-line: (1) Tricyclic antidepressants (amitriptyline 10-75mg nocte, nortriptyline) - avoid in elderly/cardiac disease; (2) Venlafaxine; (3) Tramadol. Third-line: (1) Capsaicin cream 0.075%; (2) Opioids (if other options failed/contraindicated) - last resort due to dependency risk. This patient: CKD 3A (eGFR 55), significant pain - pregabalin or duloxetine appropriate first-line. Pregabalin requires dose adjustment in CKD (75mg BD appropriate for eGFR 50-60). Duloxetine preferred if concurrent depression. Amitriptyline effective but second-line (cardiac/cognitive side effects in elderly). Opioids reserved for refractory cases. Non-pharmacological: (1) Optimize glycemic control; (2) Physiotherapy; (3) Psychological support. Many patients require combination therapy. Assess response at 4-8 weeks, titrate dose, switch if inadequate response/intolerance."
    },

    "ENDO-MCQ-0063": {
        "subtopic": "Diabetic Autonomic Neuropathy - Cardiovascular",
        "scenario": "A 65-year-old man with type 1 diabetes for 30 years reports dizziness on standing. On examination: BP supine 145/85 mmHg, BP standing after 3 minutes 100/60 mmHg (drop of 45mmHg systolic). Resting heart rate 88 bpm with minimal variation.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Postural hypotension due to antihypertensive medication",
            "B": "Diabetic autonomic neuropathy with orthostatic hypotension and cardiac autonomic dysfunction",
            "C": "Dehydration",
            "D": "Addison's disease"
        },
        "correct_answer": "B",
        "explanation": "Diabetic autonomic neuropathy (DAN) affects multiple organ systems: Cardiovascular: (1) Resting tachycardia (parasympathetic denervation); (2) Fixed heart rate (loss of HR variability); (3) Orthostatic hypotension (>20mmHg systolic or >10mmHg diastolic drop on standing); (4) Silent MI (loss of cardiac pain sensation). Gastrointestinal: gastroparesis, diabetic diarrhea, constipation. Genitourinary: erectile dysfunction, bladder dysfunction, neurogenic bladder. Sudomotor: anhidrosis, gustatory sweating. Pupillary: impaired dark adaptation. This patient: orthostatic hypotension (45mmHg drop - marked) + fixed HR (minimal variation suggests impaired HR response). Investigations: (1) Heart rate variability (HRV) with deep breathing (gold standard for cardiac DAN); (2) Valsalva maneuver response; (3) Standing HR response (30:15 ratio); (4) Ambulatory BP monitoring. Management: (1) Non-pharmacological: gradual position changes, compression stockings, increase salt/fluid intake, elevate head of bed, avoid alcohol/hot showers; (2) Pharmacological: fludrocortisone (mineralocorticoid), midodrine (alpha-agonist), droxidopa. Prognosis: DAN associated with increased cardiovascular mortality. Regular screening indicated."
    },

    "ENDO-MCQ-0064": {
        "subtopic": "Gastroparesis in Diabetes",
        "scenario": "A 45-year-old woman with type 1 diabetes for 18 years presents with early satiety, nausea, vomiting (particularly of undigested food eaten hours earlier), and bloating. Her glucose control is erratic despite consistent insulin doses. Examination shows mild epigastric tenderness. Upper endoscopy and CT abdomen are normal.",
        "stem": "What is the most likely diagnosis and diagnostic test?",
        "options": {
            "A": "Peptic ulcer disease - repeat endoscopy with biopsies",
            "B": "Gastroparesis - gastric emptying scintigraphy (gold standard diagnostic test)",
            "C": "Celiac disease - TTG antibodies",
            "D": "Pancreatic insufficiency - fecal elastase"
        },
        "correct_answer": "B",
        "explanation": "Diabetic gastroparesis: delayed gastric emptying due to autonomic neuropathy affecting gastric motility. Prevalence 30-50% in long-standing diabetes. Symptoms: (1) Early satiety; (2) Nausea, vomiting (undigested food, often hours after eating); (3) Postprandial fullness, bloating; (4) Abdominal pain; (5) Erratic glucose control (unpredictable carbohydrate absorption). Diagnosis: (1) Gastric emptying scintigraphy (gold standard): radiolabeled meal, measure retention at 1, 2, 4 hours (>10% retention at 4 hours = delayed emptying); (2) Wireless motility capsule; (3) C13 breath test. Exclude: mechanical obstruction (endoscopy/CT), peptic ulcer, celiac disease. Management: (1) Dietary: small frequent meals (6 meals/day), low fat, low fiber, liquid/soft foods, avoid alcohol; (2) Optimize glucose control (paradoxically, hyperglycemia worsens gastroparesis); (3) Prokinetics: metoclopramide (first-line, but long-term risk tardive dyskinesia), domperidone (cardiac risk), erythromycin (tachyphylaxis); (4) Antiemetics: ondansetron, prochlorperazine; (5) Severe cases: gastric electrical stimulation, feeding jejunostomy. Insulin timing: adjust based on eating/symptoms (may need post-meal dosing). This patient: classic features + normal endoscopy/CT - gastroparesis likely."
    },

    "ENDO-MCQ-0065": {
        "subtopic": "Diabetic Foot Ulcer - Assessment",
        "scenario": "A 68-year-old man with type 2 diabetes presents with a painless ulcer on the plantar surface of his right great toe (1cm diameter, shallow, clean base). He has reduced sensation to monofilament testing. Foot pulses present bilaterally. Surrounding skin is warm, no erythema or discharge.",
        "stem": "What is the most appropriate classification and immediate management?",
        "options": {
            "A": "Acute gout - start colchicine",
            "B": "Neuropathic ulcer - offload pressure (total contact cast/offloading boot), wound care, assess vascular status, glucose optimization",
            "C": "Ischemic ulcer - urgent vascular referral for revascularization",
            "D": "Infected ulcer - start oral antibiotics immediately"
        },
        "correct_answer": "B",
        "explanation": "Diabetic foot ulcers (DFU): Leading cause of lower limb amputation. Classification: (1) Neuropathic (60%): sensory loss, warm foot, palpable pulses, painless, pressure areas (metatarsal heads, heel), Wagner grade; (2) Ischemic (15%): absent pulses, cool foot, painful, atypical sites (toes, lateral foot); (3) Neuroischemic (25%): mixed features. This ulcer: painless (neuropathy), plantar pressure area, palpable pulses, no infection signs - neuropathic ulcer. Assessment: (1) Neuropathy: 10g monofilament, vibration, reflexes; (2) Vascular: pulses, ABI (ankle-brachial index), if abnormal → duplex/angiography; (3) Infection: IDSA/PEDIS criteria (erythema, purulence, warmth, systemic signs); (4) Wound characteristics: size, depth, probe to bone (osteomyelitis). Management: (1) Pressure offloading (most important): total contact cast (gold standard), offloading boot, felt padding - non-weight bearing essential; (2) Wound care: debridement, moisture balance, dressings; (3) Infection management (if present); (4) Optimize glucose control; (5) Address vascular insufficiency; (6) Multidisciplinary foot clinic. This patient needs urgent offloading + wound care. No antibiotics unless infection present (no erythema/discharge). Regular review essential. Prevention: daily foot checks, appropriate footwear, podiatry."
    },

    "ENDO-MCQ-0066": {
        "subtopic": "Diabetic Foot Infection",
        "scenario": "A 72-year-old man with diabetes presents with a foot ulcer (2cm, plantar surface) with surrounding erythema extending 3cm, purulent discharge, and foul odor. Temperature 38.2°C, HR 102 bpm. Probe-to-bone test positive. WCC 14 × 10⁹/L, CRP 145 mg/L. X-ray shows soft tissue swelling, no obvious bony changes.",
        "stem": "What is the most appropriate antibiotic regimen and investigation?",
        "options": {
            "A": "Oral cephalexin for 1 week, no further imaging needed",
            "B": "IV broad-spectrum antibiotics (piperacillin-tazobactam OR meropenem), MRI foot to assess osteomyelitis, wound culture, bone biopsy if osteomyelitis confirmed",
            "C": "Topical antibiotics only",
            "D": "Wait for culture results before starting antibiotics"
        },
        "correct_answer": "B",
        "explanation": "Diabetic foot infection classification (IDSA/PEDIS): Mild: Local infection, erythema 0.5-2cm, superficial. Moderate: Erythema >2cm OR deep tissue involvement OR systemic signs. Severe: Systemic toxicity (SIRS criteria) OR metabolic instability. This patient: moderate-severe infection (erythema >2cm, purulent discharge, fever, positive probe-to-bone suggesting osteomyelitis). Microbiology: Usually polymicrobial (Staph aureus, streptococci, gram-negatives, anaerobes). Antibiotic management: Mild: Oral (cephalexin, amoxicillin-clavulanate) for 1-2 weeks. Moderate-severe: IV broad-spectrum initially: (1) Piperacillin-tazobactam 4.5g TDS; OR (2) Meropenem 1g TDS (if MRSA/resistant organisms); OR (3) Flucloxacillin + metronidazole + gentamicin. Duration: 2-4 weeks (soft tissue), 6 weeks minimum (osteomyelitis). Investigations: (1) Wound swab/deep tissue culture (post-debridement); (2) Blood cultures if systemic infection; (3) MRI foot (best for osteomyelitis detection - 90% sensitivity/specificity); (4) Bone biopsy + culture (gold standard if OM suspected). Management: (1) IV antibiotics; (2) Surgical debridement; (3) Offloading; (4) Vascular assessment; (5) Glucose optimization. This patient needs immediate IV antibiotics, MRI to confirm osteomyelitis, deep wound cultures. May require prolonged antibiotics ± bone resection."
    },

    "ENDO-MCQ-0067": {
        "subtopic": "Charcot Arthropathy",
        "scenario": "A 55-year-old man with type 1 diabetes for 25 years presents with a warm, swollen, red right foot developed over 3 weeks. He reports no trauma or pain. Foot is visibly deformed with collapsed arch. Temperature difference of 3°C between feet. X-ray shows fractures and dislocations in midfoot.",
        "stem": "What is the most likely diagnosis and immediate management?",
        "options": {
            "A": "Cellulitis - IV antibiotics",
            "B": "Acute Charcot arthropathy - strict non-weight bearing, total contact cast, serial imaging",
            "C": "Gout - start colchicine",
            "D": "DVT - anticoagulation"
        },
        "correct_answer": "B",
        "explanation": "Charcot arthropathy (Charcot foot): Progressive destructive arthropathy in insensate foot. Pathophysiology: (1) Neuropathy → loss of protective sensation + autonomic dysfunction (increased blood flow); (2) Unrecognized microtrauma → inflammation → bone resorption → fractures/dislocations → deformity. Presentation: (1) Acute phase: warm, swollen, red foot (mimics infection); (2) Temperature difference >2°C between feet (key diagnostic clue); (3) Painless or minimal pain (due to neuropathy); (4) No preceding trauma recalled; (5) Develops over weeks-months. Stages (Eichenholtz): Stage 0: Prodromal (warm, swollen, no X-ray changes); Stage 1: Acute (fragmentation, debris); Stage 2: Coalescence (resorption, healing); Stage 3: Chronic (consolidation, deformity). Diagnosis: (1) Clinical suspicion essential; (2) X-ray (fractures, dislocations, subluxation, debris); (3) MRI (earlier detection, exclude OM). Management: Acute phase: (1) Strict non-weight bearing (critical - prevents further destruction); (2) Total contact cast immobilization for 3-6 months; (3) Serial X-rays to monitor healing; (4) Bisphosphonates may help. Chronic phase: (1) Accommodative footwear/orthotics; (2) Lifelong monitoring. Complications: recurrent ulceration, infection, amputation if untreated. Differential: infection (but CRP/WCC normal in Charcot), DVT. Early recognition and offloading prevent permanent deformity."
    },

    "ENDO-MCQ-0068": {
        "subtopic": "Diabetic Mononeuropathy",
        "scenario": "A 60-year-old man with type 2 diabetes wakes up with sudden-onset double vision. On examination, he has a left eye that cannot adduct past midline, with ptosis and a dilated pupil. Right eye movements normal. No other neurological deficits.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Diabetic third nerve (oculomotor) palsy - pupil-sparing would be typical but this has pupil involvement suggesting compressive cause (aneurysm) - needs urgent imaging",
            "B": "Posterior communicating artery aneurysm - urgent CTA/MRA required",
            "C": "Myasthenia gravis",
            "D": "Stroke"
        },
        "correct_answer": "B",
        "explanation": "Diabetic mononeuropathy: Isolated cranial or peripheral nerve lesions. Common: (1) Cranial nerves: III (oculomotor), VI (abducens), IV (trochlear), VII (facial); (2) Peripheral: median (carpal tunnel), ulnar, peroneal, femoral. Third nerve palsy: (1) Diabetic (microvascular): Pupil-sparing (>80% cases) - pupillary fibers run peripherally, spared by core ischemia; sudden onset, resolves over 3-6 months; (2) Compressive (aneurysm, tumor): Pupil-involving (dilated pupil) - pupillary fibers compressed; severe headache often present; NEUROSURGICAL EMERGENCY. This patient: ptosis + eye cannot adduct (medial rectus palsy) = third nerve involvement, BUT dilated pupil suggests compressive cause, not diabetic. Management: (1) Pupil-involving third nerve palsy = posterior communicating artery aneurysm until proven otherwise; (2) Urgent CT angiography (CTA) or MR angiography; (3) Neurosurgical consultation. Diabetic third nerve palsy: (1) Pupil-sparing (normal pupil size/reactivity); (2) Painful headache/eye pain common; (3) Conservative management (spontaneous recovery in 3-6 months); (4) MRI to exclude compressive lesion if atypical features. Other diabetic cranial neuropathies: Sixth nerve palsy (eye cannot abduct - horizontal diplopia), Fourth nerve (vertical diplopia on downward gaze), Facial nerve palsy (Bell's palsy, higher incidence in diabetes). Key point: pupil involvement = surgical emergency, not diabetic neuropathy."
    },

    "ENDO-MCQ-0069": {
        "subtopic": "Diabetic Amyotrophy",
        "scenario": "A 68-year-old man with recently diagnosed type 2 diabetes presents with 3 months of severe pain, weakness, and wasting of the right thigh. He has difficulty standing from a chair and climbing stairs. Examination shows right quadriceps wasting, reduced knee jerk, but normal sensation. EMG shows denervation in femoral nerve distribution.",
        "stem": "What is the most likely diagnosis and prognosis?",
        "options": {
            "A": "Lumbar radiculopathy - requires urgent MRI spine",
            "B": "Diabetic amyotrophy (lumbosacral plexopathy) - usually improves over 6-18 months with glucose optimization",
            "C": "Motor neuron disease",
            "D": "Polymyositis"
        },
        "correct_answer": "B",
        "explanation": "Diabetic amyotrophy (proximal diabetic neuropathy, lumbosacral radiculoplexus neuropathy): Uncommon, severe, asymmetric neuropathy affecting proximal lower limbs. Features: (1) Severe pain (thigh, hip) - often initial symptom, can be debilitating; (2) Asymmetric proximal leg weakness (quadriceps, iliopsoas); (3) Muscle wasting (thigh); (4) Weight loss common (5-20kg); (5) Reduced/absent knee jerk; (6) Usually sensory sparing or mild; (7) Often presents at diabetes diagnosis or with poor control. Pathophysiology: microvasculitis affecting lumbosacral plexus/nerve roots. Investigations: (1) EMG/NCS (denervation in femoral/obturator nerve territories); (2) MRI lumbar plexus (may show enhancement/thickening); (3) Exclude other causes (MRI spine for radiculopathy, CK for myopathy). Management: (1) Optimize glucose control aggressively; (2) Neuropathic pain management (gabapentinoids, duloxetine); (3) Physiotherapy (prevent contractures, strengthen unaffected muscles); (4) IV immunoglobulin or corticosteroids (controversial, may help in acute phase). Prognosis: (1) Gradual improvement over 6-18 months in most cases; (2) Residual weakness common; (3) Contralateral leg may become affected (30%). Differential: L2-L4 radiculopathy, vasculitis, CIDP. Good control + time usually leads to recovery."
    },

    "ENDO-MCQ-0070": {
        "subtopic": "Erectile Dysfunction in Diabetes",
        "scenario": "A 52-year-old man with type 2 diabetes for 8 years reports progressive erectile dysfunction over 2 years. He has gradual onset ED affecting all sexual encounters, preserved libido, normal morning erections absent. He has background diabetic retinopathy and microalbuminuria. Testosterone 12 nmol/L (normal 10-30).",
        "stem": "What is the most likely cause and first-line treatment?",
        "options": {
            "A": "Hypogonadism - testosterone replacement",
            "B": "Diabetic autonomic neuropathy ± vascular disease - phosphodiesterase-5 inhibitor (sildenafil, tadalafil)",
            "C": "Psychological ED - psychosexual counseling only",
            "D": "Depression - antidepressant therapy"
        },
        "correct_answer": "B",
        "explanation": "Erectile dysfunction in diabetes: Prevalence 35-75% (3 times higher than non-diabetics). Causes: (1) Autonomic neuropathy (impaired parasympathetic innervation); (2) Vascular disease (atherosclerosis, endothelial dysfunction); (3) Hormonal (hypogonadism - 30-40% of men with T2DM); (4) Medications (antihypertensives, antidepressants); (5) Psychological. This patient: gradual onset, affects all encounters, absent spontaneous erections, microvascular complications present - suggests organic cause (neuropathy/vascular). Assessment: (1) History: timing, consistency, libido, morning/spontaneous erections; (2) Medications review; (3) Hormonal: testosterone, LH, prolactin; (4) Screen for depression; (5) Cardiovascular risk assessment (ED often precedes CAD). Management: (1) Optimize glucose control, cardiovascular risk factors; (2) First-line: PDE-5 inhibitors (sildenafil 50-100mg, tadalafil 10-20mg, vardenafil) - effective in 60-70% diabetics; (3) If testosterone low (<8 nmol/L): replacement therapy; (4) Second-line: vacuum devices, intracavernosal injections, intraurethral alprostadil; (5) Third-line: penile prosthesis. PDE-5 contraindications: nitrates, unstable angina, recent MI/stroke. This patient: normal testosterone, microvascular complications - neuropathic/vascular ED, PDE-5 inhibitor appropriate first-line. Discuss expectations (may need higher doses/repeated attempts)."
    },

    "ENDO-MCQ-0071": {
        "subtopic": "Neurogenic Bladder in Diabetes",
        "scenario": "A 65-year-old woman with type 1 diabetes for 25 years reports difficulty emptying her bladder, needing to strain, poor stream, and frequent UTIs. Post-void residual ultrasound shows 350mL retained urine. Urinalysis shows no infection currently.",
        "stem": "What is the most likely diagnosis and management?",
        "options": {
            "A": "Stress incontinence - pelvic floor exercises",
            "B": "Diabetic neurogenic bladder (autonomic neuropathy affecting detrusor function) - timed voiding, double voiding, intermittent catheterization if severe",
            "C": "Bladder outlet obstruction - urological referral for surgery",
            "D": "Urinary tract infection - antibiotics"
        },
        "correct_answer": "B",
        "explanation": "Diabetic neurogenic bladder: Autonomic neuropathy affecting bladder innervation. Phases: (1) Early: Decreased bladder sensation (increased capacity, infrequent voiding); (2) Late: Detrusor weakness (poor contractility, incomplete emptying, high post-void residual). Symptoms: (1) Decreased urinary frequency; (2) Poor stream, straining; (3) Incomplete emptying sensation; (4) Overflow incontinence; (5) Recurrent UTIs (stagnant urine). Complications: (1) Recurrent UTIs/pyelonephritis; (2) Hydronephrosis (chronic high pressures); (3) Chronic kidney disease. Assessment: (1) Post-void residual volume (>150-200mL abnormal); (2) Bladder diary; (3) Urodynamic studies (if diagnosis unclear); (4) Exclude mechanical obstruction (BPH in men, prolapse in women); (5) Renal ultrasound to assess for hydronephrosis. Management: (1) Timed voiding (empty bladder every 3-4 hours even if no urge); (2) Double/triple voiding (attempt multiple times); (3) Crede maneuver (manual bladder compression); (4) Intermittent self-catheterization (if PVR >300mL or recurrent UTIs); (5) Bethanechol (cholinergic agonist - limited efficacy); (6) Treat UTIs promptly; (7) Avoid anticholinergics. This patient: high PVR (350mL), straining, recurrent UTIs, long diabetes duration - diabetic neurogenic bladder. Needs intermittent catheterization if conservative measures fail. Monitor renal function."
    },

    "ENDO-MCQ-0072": {
        "subtopic": "Diabetic Neuropathy Prevention",
        "scenario": "A 35-year-old woman with type 1 diabetes for 5 years (HbA1c 9.2%, persistently above target) asks what she can do to prevent diabetic complications, particularly neuropathy. She currently has no neuropathy symptoms and normal sensation on examination.",
        "stem": "What is the most important intervention to prevent diabetic neuropathy?",
        "options": {
            "A": "Annual foot checks are sufficient",
            "B": "Intensive glucose control to achieve HbA1c <7% (reduces neuropathy risk by 60-70% in type 1 diabetes)",
            "C": "Vitamin B12 supplementation",
            "D": "Gabapentin prophylaxis"
        },
        "correct_answer": "B",
        "explanation": "Prevention of diabetic neuropathy: Glycemic control is THE most important modifiable risk factor. Evidence: (1) DCCT trial (type 1 diabetes): intensive control (HbA1c 7% vs 9%) reduced neuropathy risk by 69%; (2) UKPDS (type 2 diabetes): 1% reduction in HbA1c associated with 25% reduction in microvascular complications. Other risk factors (some modifiable): (1) Duration of diabetes (non-modifiable); (2) Blood pressure control; (3) Lipid management; (4) Smoking cessation; (5) Weight management; (6) Foot care. Screening recommendations: (1) Type 1: screen annually starting 5 years after diagnosis; (2) Type 2: screen at diagnosis, then annually; (3) Earlier if symptoms present. Screening tests: (1) 10g monofilament (protective sensation); (2) 128Hz tuning fork (vibration); (3) Ankle reflexes; (4) Pain/temperature sensation. This patient: Poor control (HbA1c 9.2%), no neuropathy yet - opportunity for primary prevention. Intensive glucose optimization (target HbA1c <7% or individualized target) is critical. Multifactorial risk factor management also important. Once neuropathy develops, it's largely irreversible (glucose control may slow progression but doesn't reverse established neuropathy). Early intervention essential. Note: In established neuropathy, very rapid glucose improvement can temporarily worsen neuropathic pain ('treatment-induced neuropathy') - gradual HbA1c reduction preferred."
    },

    "ENDO-MCQ-0073": {
        "subtopic": "Thyroid Nodule Evaluation - Initial Assessment",
        "scenario": "A 42-year-old woman presents with a 2cm palpable nodule in the right thyroid lobe discovered incidentally. She is clinically euthyroid with no compressive symptoms. No family history of thyroid cancer. No history of neck irradiation.",
        "stem": "What is the most appropriate initial investigation?",
        "options": {
            "A": "Immediate thyroidectomy",
            "B": "Thyroid function tests (TSH) and thyroid ultrasound",
            "C": "Fine needle aspiration biopsy without imaging",
            "D": "Radioactive iodine scan"
        },
        "correct_answer": "B",
        "explanation": "Thyroid nodule evaluation (stepwise approach): Prevalence: 5-10% by palpation, 20-76% on ultrasound. Most are benign. Initial assessment: (1) History: duration, growth, compressive symptoms (dysphagia, dyspnea, voice change), hyperthyroid/hypothyroid symptoms; Risk factors for malignancy (age <20 or >70, male, family history thyroid cancer, MEN2/familial syndromes, childhood neck irradiation, rapid growth, hoarseness, cervical lymphadenopathy); (2) Examination: nodule size, consistency, fixation, lymphadenopathy; (3) TSH (first test): If suppressed (<0.1 mIU/L) → 'hot' nodule likely (autonomous, <5% malignant) → radionuclide scan; If normal/elevated → proceed to ultrasound. Ultrasound features (ACR TI-RADS classification): Benign features: purely cystic, spongiform, hyperechoic; Suspicious features: hypoechoic, microcalcifications, taller-than-wide, irregular margins, extrathyroidal extension. This patient: clinically euthyroid, palpable nodule - need TSH + ultrasound. If TSH normal and ultrasound shows suspicious features + size >1cm → FNA. If TSH suppressed → radioiodine scan. Do NOT biopsy before ultrasound (ultrasound guides FNA of suspicious nodules/features)."
    },

    "ENDO-MCQ-0074": {
        "subtopic": "Thyroid FNA - Bethesda Classification",
        "scenario": "A 50-year-old woman undergoes FNA of a 1.5cm thyroid nodule with suspicious ultrasound features. Cytology report: 'Bethesda Category III - Atypia of Undetermined Significance (AUS)'. TSH is normal.",
        "stem": "What is the most appropriate next step?",
        "options": {
            "A": "Immediate total thyroidectomy",
            "B": "Repeat FNA in 3-6 months OR molecular testing (Afirma, ThyroSeq) OR diagnostic hemithyroidectomy based on clinical context",
            "C": "Radioactive iodine ablation",
            "D": "Reassure and discharge"
        },
        "correct_answer": "B",
        "explanation": "Bethesda System for thyroid cytology: Category I: Non-diagnostic/Inadequate (repeat FNA with ultrasound guidance). Category II: Benign (malignancy risk <3%) - surveillance. Category III: AUS/FLUS (Atypia of Undetermined Significance/Follicular Lesion of Undetermined Significance) - malignancy risk 10-30%. Category IV: Follicular Neoplasm/Suspicious for Follicular Neoplasm - malignancy risk 25-40%. Category V: Suspicious for Malignancy - malignancy risk 50-75%. Category VI: Malignant - malignancy risk >97%. Bethesda III (AUS/FLUS) management options: (1) Repeat FNA (30-50% reclassified to benign or malignant); (2) Molecular testing (Afirma Gene Expression Classifier, ThyroSeq) - if benign molecular results, avoid surgery; (3) Diagnostic hemithyroidectomy (removes affected lobe for histology); (4) Observation if low clinical suspicion. Factors influencing decision: patient preference, clinical context, ultrasound features, molecular test availability. Bethesda IV: Usually diagnostic hemithyroidectomy (cannot distinguish follicular adenoma from carcinoma on cytology - needs capsular/vascular invasion assessment histologically). Bethesda V-VI: Total thyroidectomy (+ lymph node dissection if indicated). This patient: Bethesda III - indeterminate, needs further evaluation. Molecular testing increasingly used to avoid unnecessary surgery."
    },

    "ENDO-MCQ-0075": {
        "subtopic": "Thyroid Nodule - Hot vs Cold",
        "scenario": "A 38-year-old woman with suppressed TSH (<0.01 mIU/L) and free T4 26 pmol/L has a 2.5cm right thyroid nodule. Radioactive iodine uptake scan shows increased uptake in the nodule with suppression of the remaining thyroid tissue.",
        "stem": "What is the significance of this finding and management?",
        "options": {
            "A": "Cold nodule - high cancer risk - immediate surgery",
            "B": "Hot nodule (autonomous functioning nodule) - very low malignancy risk (<1%), FNA not routinely required, treat hyperthyroidism",
            "C": "Hot nodule - malignancy risk 50% - needs FNA",
            "D": "Indeterminate - requires PET scan"
        },
        "correct_answer": "B",
        "explanation": "Hot vs Cold thyroid nodules: Hot nodule (hyperfunctioning): (1) Autonomous function → suppresses TSH → increased radioiodine uptake in nodule; (2) Malignancy risk <1% (very rare); (3) FNA NOT routinely indicated; (4) Causes: toxic adenoma, early toxic multinodular goiter. Cold nodule (non-functioning): (1) Decreased/absent radioiodine uptake; (2) Malignancy risk 10-15% (higher than hot nodules); (3) Requires FNA if >1cm or suspicious features. This patient: suppressed TSH + increased uptake in nodule = hot nodule (autonomous functioning nodule causing hyperthyroidism). Management: (1) Treat hyperthyroidism: radioactive iodine ablation (preferred) OR surgery (thyroid lobectomy/total thyroidectomy) OR long-term antithyroid drugs (less ideal); (2) FNA not needed (malignancy extremely rare); (3) If choosing RAI: may need pre-treatment with antithyroid drugs if severely thyrotoxic. Note: (1) If TSH suppressed, ALWAYS do radioiodine scan before FNA (avoid unnecessary biopsies of hot nodules); (2) If TSH normal/elevated, skip scan and proceed to ultrasound + FNA based on ultrasound features; (3) Hot nodules in suppressed TSH = benign; (4) Cold nodules in normal TSH = need evaluation for cancer."
    },

    "ENDO-MCQ-0076": {
        "subtopic": "Papillary Thyroid Cancer - Management",
        "scenario": "A 35-year-old woman undergoes thyroidectomy for a 1.8cm right thyroid nodule. Histopathology confirms papillary thyroid carcinoma (classic variant), confined to thyroid, no lymphovascular invasion, no lymph node involvement. Margins clear.",
        "stem": "What is the most appropriate post-operative management?",
        "options": {
            "A": "No further treatment needed",
            "B": "Radioactive iodine (RAI) ablation followed by TSH suppression with levothyroxine and thyroglobulin monitoring",
            "C": "External beam radiotherapy",
            "D": "Chemotherapy"
        },
        "correct_answer": "B",
        "explanation": "Papillary thyroid carcinoma (PTC): Most common thyroid cancer (80-85%), excellent prognosis (10-year survival >95%). Risk stratification (ATA): Low risk: intrathyroidal, no metastases, complete resection, favorable histology, no aggressive features. Intermediate risk: microscopic extrathyroidal extension, cervical LN metastases, aggressive histology. High risk: macroscopic extrathyroidal extension, incomplete resection, distant metastases. This patient: 1.8cm, confined to thyroid, no LN involvement, clear margins = low-intermediate risk. Post-operative management: (1) Completion thyroidectomy if hemithyroidectomy performed (controversial for small low-risk tumors <1cm); (2) Radioactive iodine (RAI) ablation: Indications: tumor >4cm, extrathyroidal extension, LN/distant metastases, aggressive histology; Controversial for intermediate risk (this patient); May omit for low risk <1cm with favorable features. Dose: 30-150 mCi depending on risk. (3) TSH suppression with levothyroxine: High risk: TSH <0.1 mIU/L; Intermediate: TSH 0.1-0.5 mIU/L; Low risk: TSH 0.5-2.0 mIU/L after initial suppression. (4) Surveillance: Thyroglobulin (tumor marker) every 6-12 months; Neck ultrasound 6-12 monthly initially; Whole body radioiodine scan post-RAI. (5) Restaging after 9-12 months: If no evidence of disease → reduce TSH suppression. This patient: likely gets RAI (1.8cm, intermediate features) + TSH suppression + surveillance."
    },

    "ENDO-MCQ-0077": {
        "subtopic": "Thyroid Incidentaloma on Imaging",
        "scenario": "A 55-year-old man undergoes CT neck for carotid disease evaluation. Report mentions a 1.2cm incidental thyroid nodule in the left lobe. He is asymptomatic with no palpable nodule on examination.",
        "stem": "What is the most appropriate next step?",
        "options": {
            "A": "Ignore - too small to be significant",
            "B": "TSH and dedicated thyroid ultrasound (incidentalomas >1cm require evaluation)",
            "C": "Immediate FNA based on CT findings",
            "D": "Repeat CT in 12 months"
        },
        "correct_answer": "B",
        "explanation": "Thyroid incidentalomas: Nodules discovered on imaging performed for other reasons (CT, MRI, PET, carotid ultrasound). Prevalence: Very common (up to 67% on ultrasound, 16% on CT/MRI). Malignancy risk: Similar to palpable nodules (~7-15%). Management: Nodules ≥1cm: (1) Check TSH; (2) Dedicated thyroid ultrasound (CT/MRI not optimal for thyroid characterization); (3) Proceed with FNA if ultrasound shows suspicious features (based on ACR TI-RADS). Nodules <1cm: (1) Generally do not require further evaluation unless: High-risk features on imaging (suspicious lymph nodes, extrathyroidal extension); High-risk patient (family history, radiation exposure, symptoms); PET-avid nodule (SUV >2.5 associated with higher malignancy risk - 30-50%). PET incidentalomas: Focal PET uptake in thyroid = higher malignancy risk than other incidentalomas → lower threshold for FNA (often evaluate nodules >1cm even if <1cm if very PET-avid). This patient: 1.2cm incidentaloma on CT - meets size criterion for evaluation. Need TSH + dedicated thyroid ultrasound. If ultrasound suspicious → FNA. Do NOT biopsy based on CT alone (ultrasound better characterizes nodule features). Many incidentalomas turn out benign, but appropriate evaluation prevents missed cancers."
    },

    "ENDO-MCQ-0078": {
        "subtopic": "Anaplastic Thyroid Cancer",
        "scenario": "A 72-year-old woman presents with a rapidly growing neck mass over 6 weeks, dysphagia, and hoarseness. Examination shows a hard, fixed 5cm thyroid mass with cervical lymphadenopathy. FNA shows undifferentiated carcinoma consistent with anaplastic thyroid cancer.",
        "stem": "What is the prognosis and management approach?",
        "options": {
            "A": "Excellent prognosis - total thyroidectomy curative",
            "B": "Very poor prognosis (median survival 3-6 months) - palliative approach: airway assessment, consider palliative surgery/radiotherapy/chemotherapy, tracheostomy if airway compromise",
            "C": "Good response to radioactive iodine - standard treatment",
            "D": "Cure with chemotherapy alone"
        },
        "correct_answer": "B",
        "explanation": "Anaplastic thyroid carcinoma (ATC): Most aggressive thyroid cancer, <2% of thyroid cancers, but accounts for 50% thyroid cancer deaths. Features: (1) Rapid growth (weeks-months); (2) Elderly (peak age 60-70); (3) Rock-hard, fixed mass; (4) Compressive symptoms (dysphagia, dyspnea, hoarseness); (5) Often unresectable at presentation (local invasion); (6) Distant metastases common (lungs 50%, bone 25%). Prognosis: Dismal - median survival 3-6 months, 1-year survival <20%. Management (mainly palliative): (1) Airway assessment (critical - tracheostomy often needed); (2) Surgery: Only if resectable disease (rare) for local control/airway preservation; Debulking may palliate symptoms. (3) External beam radiotherapy (EBRT): Palliative for local control; Hyperfractionated regimens; Combined with chemotherapy. (4) Chemotherapy: Doxorubicin, taxanes, platinum agents; Limited efficacy. (5) Targeted therapy: BRAF inhibitors (dabrafenib + trametinib) if BRAF V600E mutation present (50% of ATCs) - improved outcomes in some patients; Clinical trials. (6) Supportive care: Pain management, nutrition, psychosocial support. This patient: classic ATC features. Needs immediate assessment for airway compromise, staging CT chest/abdomen (metastases), multidisciplinary discussion (oncology, ENT, palliative care), genetic testing for BRAF mutation. Prognosis discussion essential. Contrast with papillary/follicular thyroid cancers (excellent prognosis). Most patients receive palliative radiotherapy."
    },

    "ENDO-MCQ-0079": {
        "subtopic": "Medullary Thyroid Cancer - Screening",
        "scenario": "A 38-year-old man is diagnosed with medullary thyroid carcinoma (MTC). His calcitonin level is markedly elevated. Family history reveals his father died of 'thyroid cancer' at age 45, and his sister has a pheochromocytoma.",
        "stem": "What is the most important next step?",
        "options": {
            "A": "Immediate thyroidectomy without further testing",
            "B": "Screen for MEN 2 syndrome: genetic testing for RET mutation, screen for pheochromocytoma (plasma/urinary metanephrines) and hyperparathyroidism (calcium, PTH), screen first-degree relatives",
            "C": "Radioactive iodine ablation",
            "D": "Reassure - sporadic case, no further family evaluation needed"
        },
        "correct_answer": "B",
        "explanation": "Medullary thyroid carcinoma (MTC): Arises from parafollicular C-cells, secretes calcitonin. 75% sporadic, 25% hereditary (MEN 2A, MEN 2B, familial MTC). Red flags for hereditary MTC: (1) Family history thyroid cancer/MEN; (2) Young age; (3) Bilateral/multifocal MTC; (4) Associated features (pheochromocytoma, hyperparathyroidism, marfanoid habitus, mucosal neuromas). This patient: MTC + family history thyroid cancer + sister with pheochromocytoma = MEN 2A until proven otherwise. MEN 2 syndrome: Caused by germline RET proto-oncogene mutation. MEN 2A: MTC (95%), pheochromocytoma (50%), primary hyperparathyroidism (20-30%). MEN 2B: MTC (100%), pheochromocytoma (50%), marfanoid habitus, mucosal neuromas, no hyperparathyroidism. Urgent actions: (1) RET genetic testing (confirm hereditary MTC); (2) Screen for pheochromocytoma (MUST do BEFORE any surgery - undiagnosed pheochromocytoma → intraoperative hypertensive crisis/death): Plasma metanephrines (most sensitive); 24-hour urinary metanephrines; If positive → imaging (CT/MRI adrenals), treat pheochromocytoma first (alpha-blockade then surgery). (3) Screen for hyperparathyroidism: calcium, PTH. (4) Family screening: Offer RET testing to all first-degree relatives; If RET mutation positive → prophylactic thyroidectomy (timing depends on mutation aggressiveness - some mutations require thyroidectomy in early childhood). MTC surgery: Total thyroidectomy + central lymph node dissection. Post-op monitoring: Calcitonin levels (tumor marker), CEA. This patient needs urgent pheochromocytoma exclusion before thyroidectomy."
    },

    "ENDO-MCQ-0080": {
        "subtopic": "Multinodular Goiter - Management",
        "scenario": "A 58-year-old woman has a longstanding multinodular goiter. TSH is normal. Recent growth has caused visible neck swelling and mild dysphagia. CT shows large multinodular goiter with tracheal deviation and mild compression, extending substernally.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Observation - goiters never cause problems",
            "B": "Radioactive iodine shrinkage therapy",
            "C": "Total thyroidectomy (compressive symptoms + substernal extension are surgical indications)",
            "D": "Levothyroxine suppression therapy"
        },
        "correct_answer": "C",
        "explanation": "Multinodular goiter (MNG): Multiple nodules causing thyroid enlargement. Can be non-toxic (euthyroid) or toxic (hyperthyroid). Indications for surgery: (1) Compressive symptoms: Dysphagia, dyspnea, stridor; Tracheal deviation/compression; Venous obstruction (facial plethora, arm swelling - Pemberton's sign positive); (2) Substernal extension (below thoracic inlet); (3) Suspicious/malignant nodules on FNA; (4) Cosmetic concerns (large visible goiter); (5) Toxic MNG if RAI contraindicated/refused. This patient: compressive symptoms (dysphagia) + tracheal compression + substernal extension = surgical indications. Surgery: Total thyroidectomy preferred (vs subtotal) - lower recurrence, allows RAI if cancer found. Risks: (1) Recurrent laryngeal nerve injury (1-2%); (2) Hypoparathyroidism (transient 10-30%, permanent 1-3%); (3) Bleeding, infection; (4) Lifelong levothyroxine replacement. Alternative (non-surgical): Radioactive iodine: Can shrink goiter (30-50% reduction), but less effective than surgery for compressive symptoms; Contraindicated if substernal extension (may cause acute swelling/airway compromise); Requires hyperthyroid state (not useful in euthyroid MNG unless inducing hyperthyroidism first). Levothyroxine suppression: NOT effective for MNG shrinkage, may induce hyperthyroidism. This patient: surgery indicated due to compressive symptoms + substernal component. Pre-operative vocal cord assessment (laryngoscopy). Post-op calcium monitoring."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 6B UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 6B: ENDO-MCQ-0061 to 0080 (Diabetic Neuropathy + Thyroid Nodules)")
    print(f"Sub-batch 2 of 5 in Batch 6 (100 MCQs total)")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch6b_generated)

    print(f"\n✅ Batch 6B Complete: {updated}/20 MCQs updated")
    print(f"✅ Total Progress: 80/658 MCQs (12.2%)")
    print(f"\n🔄 Batch 6 Progress: 40/100 complete")
    print(f"Next: Batch 6C (MCQs 0081-0100 - Thyroid Nodules + Adrenal Disorders)")
