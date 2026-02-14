#!/usr/bin/env python3
"""
Update MCQ Batch 6D - MCQ-0101 to 0120 (20 MCQs)
Sub-batch 4 of 5 in Batch 6
Topics: Pituitary Disorders (8) + Syncope Approach (12)
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


# Batch 6D: MCQ-0101 to 0120
batch6d_generated = {
    "ENDO-MCQ-0101": {
        "subtopic": "Central Diabetes Insipidus - Diagnosis",
        "scenario": "A 35-year-old man presents with 2 weeks of polyuria (8L/day) and polydipsia. He wakes multiple times at night to urinate. Serum sodium 148 mmol/L, plasma osmolality 302 mOsm/kg, urine osmolality 110 mOsm/kg (dilute), glucose normal. He had pituitary surgery 6 months ago for non-functional adenoma.",
        "stem": "What is the most likely diagnosis and confirmatory test?",
        "options": {
            "A": "Diabetes mellitus - check HbA1c",
            "B": "Central diabetes insipidus (post-surgical) - water deprivation test with desmopressin response",
            "C": "Psychogenic polydipsia - psychiatric referral",
            "D": "Chronic kidney disease - check eGFR"
        },
        "correct_answer": "B",
        "explanation": "Diabetes insipidus (DI): Polyuria (>3L/day) with dilute urine due to ADH deficiency/resistance. Types: (1) Central DI (CDI): ADH deficiency from pituitary/hypothalamus; Causes: pituitary surgery, trauma, tumors, infiltration, idiopathic; (2) Nephrogenic DI (NDI): Renal resistance to ADH; Causes: lithium, hypercalcemia, hypokalemia, chronic kidney disease, inherited. This patient: post-pituitary surgery, polyuria with dilute urine despite hypernatremia/high plasma osmolality - suggests CDI. Water deprivation test: (1) Baseline: weight, plasma osmolality, urine osmolality, sodium; (2) Fluid restriction with hourly monitoring; (3) Stop when: plasma osmolality >300 mOsm/kg OR 3% weight loss; (4) Measure urine osmolality; (5) Give desmopressin (synthetic ADH) 2mcg IM/SC; (6) Measure urine osmolality 2-4 hours later. Interpretation: Normal: Urine concentrates to >600 mOsm/kg during deprivation. CDI: Urine remains dilute (<300 mOsm/kg), but concentrates >50% after desmopressin. NDI: Urine remains dilute even after desmopressin (<300 mOsm/kg, <10% rise). Psychogenic polydipsia: Urine concentrates normally during deprivation, low-normal sodium. Treatment: CDI: desmopressin (DDAVP) nasal spray or tablets; NDI: treat underlying cause, thiazide diuretics, amiloride (if lithium-induced)."
    },

    "ENDO-MCQ-0102": {
        "subtopic": "SIADH - Diagnosis and Management",
        "scenario": "A 68-year-old man with small cell lung cancer presents with confusion and lethargy. Serum sodium 118 mmol/L, plasma osmolality 250 mOsm/kg, urine osmolality 420 mOsm/kg (inappropriately concentrated), urine sodium 45 mmol/L. He is clinically euvolemic. Renal, thyroid, and adrenal function normal.",
        "stem": "What is the most likely diagnosis and initial management?",
        "options": {
            "A": "Dehydration - IV 0.9% saline rapidly",
            "B": "SIADH (syndrome of inappropriate ADH secretion) - fluid restriction 800-1000mL/day, treat underlying cause",
            "C": "Addison's disease - hydrocortisone",
            "D": "Cerebral salt wasting - IV 3% hypertonic saline"
        },
        "correct_answer": "B",
        "explanation": "SIADH: Inappropriate ADH secretion causing water retention and hyponatremia. Causes: (1) Malignancy: SCLC (most common), pancreatic, bladder; (2) CNS: meningitis, encephalitis, stroke, SAH, trauma; (3) Pulmonary: pneumonia, TB, aspergillosis; (4) Drugs: SSRIs, carbamazepine, cyclophosphamide, PPIs; (5) Post-operative. Diagnostic criteria: (1) Hyponatremia (<135 mmol/L); (2) Low plasma osmolality (<275 mOsm/kg); (3) Inappropriately concentrated urine (urine osm >100 mOsm/kg when plasma osm low); (4) Urine sodium >40 mmol/L; (5) Euvolemia (no edema, not dehydrated); (6) Normal renal, thyroid, adrenal function. This patient: classic SIADH with SCLC (paraneoplastic syndrome). Management: Asymptomatic/Mild (Na+ 125-135 mmol/L): (1) Fluid restriction 800-1000mL/day (first-line); (2) Treat underlying cause. Moderate (Na+ 115-125, symptomatic): (1) Fluid restriction; (2) Consider salt tablets, urea, demeclocycline. Severe (Na+ <115, seizures, coma): (1) IV 3% hypertonic saline (cautiously - risk osmotic demyelination); (2) Correct slowly: 6-8 mmol/L in 24 hours, <12 mmol/L in 48 hours; (3) ICU monitoring. Tolvaptan (vasopressin antagonist): Reserved for refractory cases. Differential: Cerebral salt wasting (hypovolemic, post-SAH). This patient: moderate SIADH - fluid restriction + treat SCLC. Monitor sodium closely - too rapid correction → osmotic demyelination syndrome (locked-in syndrome, dysarthria, quadriparesis)."
    },

    "ENDO-MCQ-0103": {
        "subtopic": "Empty Sella Syndrome",
        "scenario": "A 52-year-old obese woman undergoes MRI brain for headaches. Report shows 'empty sella - pituitary gland flattened against floor of sella, cerebrospinal fluid filling sella turcica'. Pituitary function tests are normal. No visual field defects.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Urgent neurosurgery",
            "B": "Reassurance - empty sella syndrome is usually benign; monitor pituitary function annually if asymptomatic",
            "C": "Trans-sphenoidal pituitary surgery",
            "D": "High-dose corticosteroids"
        },
        "correct_answer": "B",
        "explanation": "Empty sella syndrome: CSF fills sella turcica, compressing pituitary against floor. Types: (1) Primary empty sella (90%): Congenital defect in diaphragma sellae; More common in obese, multiparous women; Usually asymptomatic, incidental finding. (2) Secondary empty sella: Following pituitary surgery, radiotherapy, apoplexy, Sheehan's syndrome. Clinical features: (1) Most asymptomatic (incidental MRI finding); (2) Headaches (20-30%, but often unrelated); (3) Rarely: visual disturbances (optic chiasm herniation), CSF rhinorrhea; (4) Pituitary dysfunction uncommon in primary (10-15%), more common in secondary. Investigations: (1) MRI confirms diagnosis; (2) Pituitary function tests (TSH, free T4, LH, FSH, prolactin, 8am cortisol, IGF-1); (3) Visual field testing if symptoms. Management: Primary empty sella with normal function: (1) Reassurance - benign condition; (2) Annual pituitary function monitoring (some develop hypopituitarism over time); (3) No treatment needed if asymptomatic. Indications for intervention: (1) Hypopituitarism → hormone replacement; (2) CSF rhinorrhea → surgical repair; (3) Visual disturbances → rarely needs surgery. This patient: primary empty sella, normal function, asymptomatic - reassure and monitor. Surgery not indicated. Differential: pituitary adenoma (enhances on MRI), craniopharyngioma, Rathke's cleft cyst."
    },

    "ENDO-MCQ-0104": {
        "subtopic": "Hypopituitarism - Diagnosis",
        "scenario": "A 42-year-old woman presents with 6 months of fatigue, cold intolerance, amenorrhea, and loss of libido. She has no galactorrhea. Blood tests show: TSH 1.8 mIU/L, free T4 8 pmol/L, 8am cortisol 180 nmol/L, prolactin 150 mU/L, LH <1 IU/L, FSH <1 IU/L. MRI shows 2cm pituitary macroadenoma.",
        "stem": "What is the diagnosis?",
        "options": {
            "A": "Primary hypothyroidism",
            "B": "Hypopituitarism (secondary hypothyroidism, secondary adrenal insufficiency, hypogonadotropic hypogonadism) due to pituitary macroadenoma",
            "C": "Prolactinoma",
            "D": "Normal variant"
        },
        "correct_answer": "B",
        "explanation": "Hypopituitarism: Deficiency of one or more pituitary hormones. Causes: (1) Pituitary adenomas (mass effect - non-functional or functional); (2) Pituitary surgery, radiotherapy; (3) Traumatic brain injury; (4) Sheehan's syndrome (postpartum hemorrhage); (5) Infiltrative (sarcoidosis, hemochromatosis, lymphocytic hypophysitis); (6) Genetic (eg PROP1 mutations). This patient has multiple deficiencies: Secondary hypothyroidism: Low free T4 + inappropriately normal/low TSH (TSH 1.8 - should be elevated in primary hypothyroidism). Secondary adrenal insufficiency: Low cortisol 180 nmol/L (should be >450 at 8am). Hypogonadotropic hypogonadism: Amenorrhea, low libido, very low LH/FSH. Assessment: (1) Thyroid axis: TSH + free T4 (as above); (2) Adrenal axis: 8am cortisol + ACTH, Synacthen test if cortisol 100-450 nmol/L; (3) Gonadal axis: LH, FSH, estradiol/testosterone; (4) Prolactin: Can be mildly elevated due to stalk effect (<2000 mU/L); (5) GH axis: IGF-1, GH stimulation test if clinically indicated. Treatment: (1) Hormone replacement: Hydrocortisone (start BEFORE levothyroxine - avoid precipitating adrenal crisis), Levothyroxine, Sex hormones (estrogen/testosterone); (2) Treat underlying cause (pituitary adenoma - surgery/medical therapy). Order of replacement: Always cortisol first (thyroxine increases cortisol metabolism). This patient: pituitary macroadenoma causing mass effect → hypopituitarism. Needs full pituitary assessment, urgent hydrocortisone replacement, then levothyroxine, then estrogen replacement. Prolactin mildly elevated due to stalk compression (not prolactinoma - prolactin would be >2000-3000 mU/L)."
    },

    "ENDO-MCQ-0105": {
        "subtopic": "Sheehan's Syndrome",
        "scenario": "A 32-year-old woman presents 6 months after difficult childbirth complicated by severe postpartum hemorrhage requiring blood transfusions. She reports inability to breastfeed, failure to resume menses, fatigue, cold intolerance, and lightheadedness on standing. Examination shows orthostatic hypotension. Investigations show low cortisol, low TSH/T4, low LH/FSH.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Postpartum depression",
            "B": "Sheehan's syndrome (postpartum pituitary infarction causing hypopituitarism)",
            "C": "Primary hypothyroidism",
            "D": "Chronic fatigue syndrome"
        },
        "correct_answer": "B",
        "explanation": "Sheehan's syndrome: Postpartum pituitary infarction/necrosis due to severe obstetric hemorrhage. Pathophysiology: (1) Pregnancy causes physiological pituitary enlargement (2-3x size); (2) Pituitary blood supply from low-pressure portal system; (3) Severe hypotension from PPH → pituitary ischemia/infarction. Risk factors: (1) Severe PPH; (2) Disseminated intravascular coagulation; (3) Prolonged hypotension; (4) Developing countries (better obstetric care has reduced incidence in developed countries). Presentation: (1) Acute (rare): Pituitary apoplexy immediately postpartum; (2) Chronic (most common): Insidious onset weeks-months postpartum; Inability to lactate (first sign - prolactin deficiency); Failure to resume menses (gonadotropin deficiency); Fatigue, cold intolerance (secondary hypothyroidism); Hypotension, hyponatremia (secondary adrenal insufficiency); Symptoms of multiple hormone deficiencies. Diagnosis: (1) Clinical history: PPH + failure to lactate + amenorrhea; (2) Pituitary function testing: confirms hypopituitarism; (3) MRI pituitary: may show empty sella, small pituitary. Treatment: Lifelong hormone replacement - hydrocortisone, levothyroxine, estrogen/progesterone, +/- GH. This patient: classic presentation - PPH followed by inability to lactate, amenorrhea, symptoms of hypothyroidism and adrenal insufficiency. Sheehan's syndrome until proven otherwise. Differential: Lymphocytic hypophysitis (can also present postpartum but less common, MRI shows enlarged pituitary rather than small)."
    },

    "ENDO-MCQ-0106": {
        "subtopic": "Growth Hormone Deficiency in Adults",
        "scenario": "A 38-year-old man with history of craniopharyngioma treated with surgery and radiotherapy 10 years ago presents with fatigue, reduced exercise tolerance, increased abdominal adiposity, and reduced quality of life. He is on replacement for hypothyroidism, adrenal insufficiency, and hypogonadism. IGF-1 is low.",
        "stem": "What additional treatment should be considered?",
        "options": {
            "A": "No further treatment needed - GH replacement not indicated in adults",
            "B": "Growth hormone replacement (after confirming GH deficiency with stimulation test) - improves body composition, bone density, cardiovascular risk, and quality of life",
            "C": "Increase levothyroxine dose",
            "D": "Antidepressants"
        },
        "correct_answer": "B",
        "explanation": "Adult growth hormone deficiency (AGHD): Often overlooked but causes significant morbidity. Causes: (1) Pituitary adenoma, surgery, radiotherapy (most common); (2) Traumatic brain injury; (3) Childhood-onset GH deficiency (transition to adult care). Features: (1) Increased body fat (visceral adiposity); (2) Reduced muscle mass, strength; (3) Reduced exercise capacity; (4) Reduced bone density → osteoporosis; (5) Dyslipidemia, insulin resistance → cardiovascular risk; (6) Impaired quality of life (fatigue, reduced energy, social isolation, depression). Diagnosis: (1) Low IGF-1 (suggestive but not diagnostic); (2) GH stimulation tests (insulin tolerance test or glucagon stimulation test); Peak GH <3-5 mcg/L = deficient. Benefits of GH replacement in adults: (1) Improved body composition (decreased fat, increased lean mass); (2) Increased bone density; (3) Improved lipid profile, reduced cardiovascular risk; (4) Improved exercise capacity; (5) Improved quality of life, mood, energy. Treatment: (1) Recombinant GH subcutaneous daily injections; (2) Start low, titrate based on IGF-1 levels; (3) More beneficial if started earlier; (4) Continue indefinitely if effective. Side effects: Fluid retention, arthralgias, carpal tunnel (usually transient), insulin resistance, increased cancer risk theoretical concern (but no evidence). Contraindications: Active malignancy. This patient: craniopharyngioma with radiotherapy → high risk AGHD, symptoms consistent. Low IGF-1 supports diagnosis. Needs GH stimulation test, then consider GH replacement (significantly improves quality of life)."
    },

    "ENDO-MCQ-0107": {
        "subtopic": "Kallmann Syndrome",
        "scenario": "An 18-year-old male presents with delayed puberty, absent facial hair, and high-pitched voice. He has anosmia (no sense of smell). Testes are small (2mL bilaterally). Blood tests show LH <1 IU/L, FSH <1 IU/L, testosterone 2 nmol/L (very low). MRI shows absent olfactory bulbs.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Constitutional delay of puberty",
            "B": "Kallmann syndrome (hypogonadotropic hypogonadism with anosmia)",
            "C": "Klinefelter syndrome",
            "D": "Primary testicular failure"
        },
        "correct_answer": "B",
        "explanation": "Kallmann syndrome: Congenital hypogonadotropic hypogonadism with anosmia/hyposmia. Genetics: X-linked, autosomal dominant, or recessive; mutations in KAL1, FGFR1, others. Pathophysiology: Defective migration of GnRH neurons and olfactory neurons from nasal placode to hypothalamus. Features: (1) Hypogonadotropic hypogonadism: Delayed/absent puberty; Low LH, FSH, testosterone/estradiol; Small testes (<4mL), micropenis; (2) Anosmia/hyposmia (50-80%); (3) Associated features: Renal agenesis (30%), cleft palate, cryptorchidism, hearing loss, synkinesia (mirror movements). Diagnosis: (1) Clinical: delayed puberty + anosmia; (2) Biochemistry: Low sex hormones, inappropriately normal/low gonadotropins; (3) MRI brain: Absent/hypoplastic olfactory bulbs (diagnostic). Differential: (1) Constitutional delay: Normal smell, spontaneous progression; (2) Functional hypogonadotropic hypogonadism: Stress, anorexia, excessive exercise - reversible; (3) Other causes hypopituitarism: Tumor, infiltration - usually other hormone deficiencies; (4) Klinefelter: Primary hypogonadism (high LH/FSH), normal smell. Treatment: (1) Testosterone replacement in males (induces secondary sex characteristics, virilization); (2) For fertility: pulsatile GnRH therapy OR gonadotropin injections (FSH + hCG); (3) Psychological support. This patient: classic Kallmann - absent puberty, anosmia, low gonadotropins, absent olfactory bulbs. Distinguish from primary hypogonadism (testes/ovaries dysfunction - high LH/FSH) vs secondary (pituitary/hypothalamus - low/normal LH/FSH)."
    },

    "ENDO-MCQ-0108": {
        "subtopic": "Pituitary Incidentaloma",
        "scenario": "A 45-year-old woman undergoes MRI brain for investigation of migraines. Report mentions 6mm pituitary lesion (microadenoma). She has no symptoms of hormone excess or deficiency. Visual fields normal.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Immediate trans-sphenoidal surgery",
            "B": "Assess pituitary function (TSH, free T4, prolactin, 8am cortisol, LH, FSH, IGF-1) and repeat MRI in 6-12 months",
            "C": "Radiotherapy",
            "D": "No follow-up needed"
        },
        "correct_answer": "B",
        "explanation": "Pituitary incidentaloma: Pituitary lesion discovered on imaging for unrelated reasons. Prevalence: 10% of population have pituitary adenomas; most asymptomatic. Management approach: Step 1 - Assess hormonal activity (even if asymptomatic): (1) Prolactin (prolactinoma screening); (2) IGF-1 (acromegaly screening); (3) 1mg dexamethasone suppression test OR late-night salivary cortisol (Cushing's screening); (4) TSH, free T4 (secondary hypothyroidism); (5) LH, FSH, testosterone/estradiol (hypogonadism). Step 2 - Assess mass effect (macroadenomas ≥10mm): (1) Visual field testing (formal perimetry); (2) MRI if not already done. Step 3 - Management based on findings: Non-functional microadenoma (<10mm), asymptomatic: (1) Repeat MRI in 6-12 months (assess growth); (2) If stable: repeat MRI every 1-2 years for 3-5 years; (3) Repeat hormone testing if growth or new symptoms. Non-functional macroadenoma (≥10mm): (1) Neurosurgery referral; (2) Consider surgery if: growing, causing visual deficits, hypopituitarism, young patient; (3) If stable and asymptomatic: may observe with close monitoring. Functional adenoma: Treat underlying hormone excess (prolactinoma → cabergoline; acromegaly → surgery; Cushing's → surgery). This patient: 6mm microadenoma, asymptomatic - assess function + surveillance MRI. Most microadenomas remain stable. Surgery not indicated unless functional or growing. Caution: Some 'incidentalomas' are metastases, lymphoma, or other pathology - clinical context important."
    },

    "CARD-MCQ-0109": {
        "subtopic": "Syncope - Definition and Classification",
        "scenario": "A 28-year-old woman presents to ED after an episode of loss of consciousness while standing in a queue. She felt lightheaded and nauseated beforehand, then 'blacked out' for ~20 seconds. Witnesses report she 'went pale and slid to the ground', with brief jerking movements of limbs. She recovered quickly with no confusion. No tongue biting or incontinence.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Epileptic seizure",
            "B": "Reflex (vasovagal) syncope",
            "C": "Stroke",
            "D": "Cardiac arrhythmia"
        },
        "correct_answer": "B",
        "explanation": "Syncope: Transient loss of consciousness (TLOC) due to cerebral hypoperfusion, characterized by rapid onset, short duration, spontaneous complete recovery. Classification: (1) Reflex (neurally-mediated) syncope (60%): Vasovagal (common faint), Situational (cough, micturition, defecation), Carotid sinus hypersensitivity. (2) Orthostatic hypotension (15%): Autonomic failure, Volume depletion, Drugs. (3) Cardiac syncope (10-15%): Arrhythmias (VT, complete heart block, SVT), Structural (AS, HOCM, PE), High-risk. (4) Unexplained (15-20%). This patient: classic vasovagal syncope. Features: (1) Triggers: prolonged standing, crowded/hot environment, pain, fear, venepuncture; (2) Prodrome: lightheadedness, nausea, pallor, sweating, visual blurring (seconds to minutes); (3) Upright posture; (4) Witnesses: pale, diaphoretic, brief myoclonic jerks common ('convulsive syncope' - due to cerebral hypoxia, NOT epilepsy); (5) Rapid recovery (<1 min), no confusion. Distinguish from seizures: (1) Seizures: Aura (different from syncope prodrome), prolonged unconsciousness, tonic-clonic movements, tongue biting, incontinence, post-ictal confusion, elevated prolactin; (2) Syncope: Brief LOC (<30 sec), rapid recovery, no confusion. Initial assessment: History (80% diagnostic), examination, ECG, orthostatic BPs. This patient: benign vasovagal syncope, no further cardiac investigation needed if ECG normal and no red flags."
    },

    "CARD-MCQ-0110": {
        "subtopic": "Syncope Risk Stratification",
        "scenario": "A 72-year-old man presents to ED after syncope without warning while sitting. Past medical history includes ischemic heart disease (previous MI), heart failure (LVEF 35%). ECG shows left bundle branch block. He had similar episode 2 months ago.",
        "stem": "What is the risk level and appropriate management?",
        "options": {
            "A": "Low risk - discharge home",
            "B": "High risk - urgent admission, cardiac monitoring, cardiology consultation for investigation (echo, Holter, EP study, consider ICD)",
            "C": "Vasovagal syncope - reassure",
            "D": "Discharge with GP follow-up"
        },
        "correct_answer": "B",
        "explanation": "Syncope risk stratification (San Francisco Syncope Rule, Canadian Syncope Risk Score, ESC guidelines): High-risk features ('red flags'): History: (1) Syncope during exertion or supine (suggests cardiac); (2) No prodrome (sudden collapse - arrhythmia); (3) Chest pain, dyspnea (ACS, PE); (4) Family history sudden death <40 years; (5) Known heart disease (IHD, cardiomyopathy, valve disease). Examination: (1) Abnormal cardiovascular exam (murmurs, HF signs); (2) Persistent hypotension. ECG red flags: (1) Ischemia, infarction; (2) Conduction abnormalities (LBBB, RBBB, bifascicular block, AV block, prolonged PR); (3) Arrhythmias (VT, SVT, AF with RVR, bradycardia <40); (4) Channelopathies (long QT >460ms, Brugada pattern, short QT); (5) LVH with strain, Q waves. This patient: Multiple high-risk features - IHD, HF (LVEF 35%), LBBB, syncope without warning, recurrent. Suggests cardiac arrhythmia. Management: (1) Admit to monitored bed; (2) Continuous cardiac monitoring (telemetry); (3) Echocardiogram (structural assessment); (4) Prolonged ECG monitoring (Holter 24-48hr, event recorder, implantable loop recorder); (5) Electrophysiology study if suspect VT; (6) Consider ICD (low EF + concerning symptoms). Low-risk (can discharge): Young, no heart disease, typical vasovagal features, normal ECG. Intermediate risk: Admit for 24hr monitoring. Sudden cardiac death risk: Patients with structural heart disease + syncope have 5-10x increased SCD risk."
    },

    "CARD-MCQ-0111": {
        "subtopic": "Orthostatic Hypotension - Diagnosis",
        "scenario": "A 78-year-old woman with Parkinson's disease presents with recurrent falls and dizziness on standing. Lying BP 155/85 mmHg, standing BP (after 3 minutes) 95/60 mmHg. She reports symptoms worse in morning and after meals.",
        "stem": "What is the diagnosis and initial management?",
        "options": {
            "A": "Vasovagal syncope - reassure",
            "B": "Orthostatic hypotension (≥20mmHg systolic or ≥10mmHg diastolic drop) - non-pharmacological measures (slow position changes, compression stockings, increased salt/fluid), review medications, midodrine/fludrocortisone if refractory",
            "C": "Cardiac arrhythmia - pacemaker",
            "D": "Hypoglycemia - glucose monitoring"
        },
        "correct_answer": "B",
        "explanation": "Orthostatic hypotension (OH): Sustained BP drop within 3 minutes of standing: ≥20mmHg systolic OR ≥10mmHg diastolic. Causes: (1) Neurogenic: Autonomic failure (Parkinson's, MSA, pure autonomic failure, diabetic neuropathy), Age-related; (2) Non-neurogenic: Volume depletion, Drugs (antihypertensives, diuretics, vasodilators, alpha-blockers, TCAs, opioids), Prolonged bed rest, Anemia. This patient: Parkinson's disease (autonomic dysfunction) - neurogenic OH. Classic features: symptoms worse morning (nocturnal diuresis), post-prandial (splanchnic blood pooling). Diagnosis: (1) Measure BP lying (after 5min supine), then standing at 1 and 3 minutes; (2) Positive: ≥20/10 mmHg drop + symptoms (dizziness, lightheadedness, falls); (3) Tilt table testing if diagnosis unclear. Management: Non-pharmacological (first-line): (1) Education: rise slowly from lying → sitting → standing; (2) Avoid triggers: hot environment, large meals, alcohol, straining; (3) Physical countermaneuvers: leg crossing, muscle tensing; (4) Increase salt (6-10g/day if no contraindications), fluid intake (2-2.5L/day); (5) Compression stockings (waist-high); (6) Elevate head of bed 10-20° (reduces nocturnal diuresis); (7) Small frequent meals (reduce post-prandial OH). Pharmacological: (1) Fludrocortisone 0.1-0.2mg daily (mineralocorticoid - increases volume); (2) Midodrine 2.5-10mg TDS (alpha-agonist - vasoconstriction); (3) Droxidopa. Monitor for supine hypertension (common in neurogenic OH) - may need to avoid lying flat daytime. This patient needs medication review + non-pharmacological measures, consider pharmacotherapy if insufficient."
    },

    "CARD-MCQ-0112": {
        "subtopic": "Carotid Sinus Hypersensitivity",
        "scenario": "An 80-year-old man presents with recurrent unexplained syncope, often precipitated by turning his head or wearing tight collars. Carotid sinus massage (performed with ECG and BP monitoring) reproduces symptoms with 6-second asystole.",
        "stem": "What is the diagnosis and treatment?",
        "options": {
            "A": "Vasovagal syncope - reassure",
            "B": "Carotid sinus hypersensitivity with cardioinhibitory response - dual-chamber pacemaker indicated",
            "C": "Transient ischemic attack - antiplatelet therapy",
            "D": "Epilepsy - antiepileptic drugs"
        },
        "correct_answer": "B",
        "explanation": "Carotid sinus hypersensitivity (CSH): Exaggerated response to carotid sinus massage causing syncope/pre-syncope. Predominantly affects elderly (>60 years). Types: (1) Cardioinhibitory (70%): Bradycardia, AV block, asystole (≥3 seconds); (2) Vasodepressor (10%): Hypotension (≥50mmHg systolic drop) without significant bradycardia; (3) Mixed (20%): Both. Triggers: Head turning, tight collars, shaving, neck manipulation. Diagnosis: Carotid sinus massage (CSM): (1) Contraindications: Carotid bruit/stenosis (stroke risk), recent MI/stroke (<3 months), history VT/VF; (2) Technique: Firm pressure over carotid bifurcation for 5-10 seconds, one side at a time; (3) Monitoring: Continuous ECG, BP; (4) Positive: Asystole ≥3 seconds OR ≥50mmHg systolic BP drop + symptom reproduction. Treatment: Cardioinhibitory/Mixed: Dual-chamber pacemaker (prevents bradycardia/asystole, reduces syncope recurrence by 70-90%). Vasodepressor: More difficult - compression stockings, midodrine, education (avoid triggers); Pacing ineffective. This patient: classic CSH with cardioinhibitory response (6-second asystole with CSM). Pacemaker indicated (Class I recommendation if symptomatic + documented ≥3 second pause). Note: CSH without syncope (asymptomatic) does NOT require pacemaker - common incidental finding in elderly. Only treat if causing symptoms. Differential: Sick sinus syndrome (similar bradycardia but no trigger pattern)."
    },

    "CARD-MCQ-0113": {
        "subtopic": "Situational Syncope",
        "scenario": "A 45-year-old man reports two episodes of loss of consciousness immediately after urinating at night. He woke up on bathroom floor both times with no warning. No cardiac history, normal examination, normal ECG.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Cardiac arrhythmia requiring pacemaker",
            "B": "Micturition (post-voiding) syncope - situational reflex syncope, benign, advise sitting to urinate",
            "C": "Epilepsy",
            "D": "Prostate cancer"
        },
        "correct_answer": "B",
        "explanation": "Situational syncope: Subtype of reflex syncope triggered by specific situations. Types: (1) Micturition syncope: During/after urination (especially nocturnally in middle-aged/elderly men); Mechanism: Valsalva during voiding + rapid bladder decompression → vagal surge → bradycardia/vasodilatation; Exacerbated by: overnight diuresis, alcohol, standing to void. (2) Defecation syncope: During straining at stool; (3) Cough syncope: Prolonged vigorous coughing (COPD, pertussis); (4) Post-exercise syncope: Immediately after stopping intense exercise (peripheral vasodilatation); (5) Swallow syncope: Rare, esophageal pathology; (6) Laugh syncope: Gelastic syncope. This patient: classic micturition syncope - middle-aged male, nocturnal, immediately post-voiding. Diagnosis: Clinical history diagnostic, investigations normal (rule out cardiac causes). Management: (1) Reassurance - benign condition; (2) Avoid triggers: sit to urinate (especially at night), avoid alcohol before bed, adequate hydration; (3) Nocturnal urination: ensure lights on, wake up fully before voiding; (4) If recurrent despite measures: cardiology assessment to exclude cardiac causes. Prognosis: Excellent, no increased mortality. No pacemaker or other treatment needed. Differential: Cardiac syncope (but would be recurrent in various settings, ECG abnormalities). Situational syncope diagnosis requires: typical trigger, no cardiac history, normal cardiac evaluation."
    },

    "CARD-MCQ-0114": {
        "subtopic": "Syncope Investigation - Holter vs Event Recorder",
        "scenario": "A 58-year-old woman has had 3 episodes of syncope over past 6 months (unexplained after initial assessment). Episodes are infrequent and unpredictable. ECG shows occasional ectopy but no diagnostic abnormalities. 24-hour Holter monitor was normal.",
        "stem": "What is the most appropriate next investigation?",
        "options": {
            "A": "Repeat 24-hour Holter monthly",
            "B": "External event recorder (30-day) OR implantable loop recorder (up to 3 years) for long-term monitoring to capture infrequent events",
            "C": "No further investigation",
            "D": "Tilt table testing"
        },
        "correct_answer": "B",
        "explanation": "ECG monitoring strategies for syncope: 24-48 hour Holter monitor: (1) Continuous recording 24-48 hours; (2) Diagnostic yield 1-2% for syncope (most events don't occur during short monitoring); (3) Useful if: frequent symptoms (daily/every few days), baseline ECG abnormalities suggesting arrhythmia. External event recorder: (1) Patient-activated: symptoms too infrequent for Holter; (2) Auto-triggered: detects bradycardia/tachycardia automatically; (3) Duration: 2-4 weeks; (4) Diagnostic yield 10-20%; (5) Limitations: patient must activate device, may not capture presyncope if loses consciousness quickly. Implantable loop recorder (ILR): (1) Subcutaneous device (battery life 2-3 years); (2) Continuous monitoring, auto-activates for arrhythmias; (3) Patient can activate retrospectively; (4) Indications: Unexplained syncope after full evaluation, suspected arrhythmic cause, high-risk features but no diagnosis; (5) Diagnostic yield 50-70% over 1-2 years; (6) Invasive but highly effective for infrequent events. Tilt table testing: (1) Assesses vasovagal/neurogenic syncope; (2) Not for arrhythmia detection. This patient: Infrequent unpredictable syncope, normal Holter - needs prolonged monitoring. ILR is gold standard for unexplained syncope (Class I indication, ESC guidelines). External event recorder alternative if patient preference or cost constraints. Choice depends on: symptom frequency (very infrequent → ILR), patient preference, availability. ILR superior for capturing rare events but invasive. Modern ILRs detect AF, bradycardia, tachycardia automatically."
    },

    "CARD-MCQ-0115": {
        "subtopic": "Tilt Table Testing",
        "scenario": "A 25-year-old woman has recurrent episodes of syncope with typical vasovagal prodrome. Initial assessment (history, exam, ECG, orthostatic BPs) supports vasovagal syncope, but episodes are frequent and affecting quality of life. She wants definitive diagnosis.",
        "stem": "What is the role of tilt table testing in this case?",
        "options": {
            "A": "Tilt testing is mandatory for all syncope patients",
            "B": "Tilt testing can confirm vasovagal mechanism (70-80% sensitivity) and guide therapy, but diagnosis often clinical; consider if diagnosis uncertain or frequent recurrence despite measures",
            "C": "Tilt testing has no role - diagnosis already clear",
            "D": "Tilt testing for cardiac arrhythmia detection"
        },
        "correct_answer": "B",
        "explanation": "Tilt table testing: Provokes vasovagal syncope in controlled setting to confirm diagnosis and assess hemodynamic pattern. Indications: (1) Unexplained syncope after initial evaluation; (2) Recurrent syncope in high-risk occupations (pilots, drivers); (3) Syncope with atypical features; (4) Reassure patient/guide therapy for frequent vasovagal syncope. Technique: (1) Patient supine for 20 minutes (baseline); (2) Tilt to 60-70° for 20-45 minutes; (3) Monitor BP, HR, symptoms continuously; (4) Isoproterenol or nitrate provocation if initial tilt negative. Positive test: Reproduction of syncope/presyncope with: (1) Vasovagal response: Initially HR/BP rise, then sudden drop; Type 1: Mixed (HR and BP fall); Type 2A: Cardioinhibitory (HR falls >40bpm or <40bpm for >10 sec); Type 2B: Cardioinhibitory + asystole >3 sec; Type 3: Vasodepressor (BP falls, HR doesn't). (2) Orthostatic hypotension: Progressive BP fall without HR rise (autonomic failure). Sensitivity 70-80%, Specificity 90%. Limitations: (1) False positives (10% healthy people faint on tilt); (2) False negatives (vasovagal syncope can still occur if negative test); (3) Not useful for arrhythmia detection. This patient: Clinical diagnosis vasovagal syncope likely, but tilt testing reasonable if: wants confirmation, frequent episodes affecting life, considering pharmacotherapy (midodrine, fludrocortisone). Pattern on tilt table helps guide therapy (eg cardioinhibitory with asystole >3 sec → consider pacemaker, though rarely needed in young without structural heart disease)."
    },

    "CARD-MCQ-0116": {
        "subtopic": "Vasovagal Syncope - Management",
        "scenario": "A 22-year-old nursing student has recurrent vasovagal syncope (4 episodes in past year) triggered by prolonged standing, blood draws, and hot environments. Tilt table confirms vasovagal pattern. She is worried about fainting during clinical placements.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Beta-blockers",
            "B": "Education on triggers and prodrome recognition, physical counterpressure maneuvers (leg crossing, hand grip), increased salt/fluid intake, tilt training",
            "C": "Permanent pacemaker",
            "D": "Avoid all triggering situations permanently"
        },
        "correct_answer": "B",
        "explanation": "Vasovagal syncope management (stepwise): First-line (non-pharmacological): (1) Education: Explain benign nature, recognize prodrome (nausea, pallor, sweating, visual disturbances), lie/sit immediately when prodrome occurs; (2) Avoid/modify triggers: Prolonged standing, hot environments, dehydration, fasting, alcohol, sudden postural changes; (3) Physical counterpressure maneuvers (most effective): Leg crossing with muscle tensing, Hand grip, Arm tensing, Squatting; Performed during prodrome - abort 30-40% of episodes. (4) Increase salt (6-10g/day) and fluid intake (2-2.5L/day) - expand blood volume; (5) Tilt training: Daily head-up tilt at home (10-30 min/day) - progressive orthostatic training, desensitizes reflex. Second-line (pharmacological, limited efficacy): (1) Midodrine (alpha-agonist) - for refractory cases; (2) Fludrocortisone (volume expansion) - young patients; (3) Beta-blockers: Controversial, no consistent benefit in trials (previously used); (4) SSRIs - some benefit in refractory cases. Pacing: (1) Very limited role in vasovagal syncope; (2) Consider only if: Age >40, severe cardioinhibitory response (asystole >3 sec on tilt), recurrent injuries despite measures; (3) Benefit modest (30-40% reduction in syncope, doesn't prevent all episodes). This patient: Young, frequent vasovagal syncope - excellent candidate for non-pharmacological measures. Education + physical countermaneuvers most effective. Pharmacotherapy reserved for refractory cases. Prognosis: Benign, no increased mortality, but can cause injuries and affect quality of life."
    },

    "CARD-MCQ-0117": {
        "subtopic": "Syncope and Driving - Australian Guidelines",
        "scenario": "A 55-year-old truck driver (holds heavy vehicle license) has a single unexplained syncope episode while at rest. Initial investigations (ECG, echo, Holter) are normal.",
        "stem": "What are the Australian driving restrictions?",
        "options": {
            "A": "No restrictions - can return to driving immediately",
            "B": "Private license: No driving until cause identified/treated or 4 weeks symptom-free; Commercial license: Cannot drive until full investigation, cause identified/treated, 3 months symptom-free (may be longer)",
            "C": "Permanent ban from driving",
            "D": "Only restriction if syncope occurs while driving"
        },
        "correct_answer": "B",
        "explanation": "Australian driving standards (Austroads 2024) for syncope: Private (Class C) license: (1) Single syncope episode: No driving until: Cause identified and treated, OR 4 weeks symptom-free with full investigation; (2) Recurrent syncope: No driving until: Cause identified/treated AND 3 months symptom-free; (3) Vasovagal: Can drive if typical features, no syncope while driving, able to recognize prodrome. Commercial (Class HC, MC) license: More stringent: (1) Single unexplained syncope: Cannot drive commercial vehicle until: Full investigation (including prolonged ECG monitoring, EP study if indicated), Cause identified and treated, 3 months symptom-free; (2) Cardiac syncope: 6-12 months symptom-free after treatment; (3) Vasovagal: 3 months symptom-free. This patient: Truck driver with unexplained syncope - must not drive commercial vehicles until: (1) Complete investigation (may need ILR if no diagnosis), (2) Cause determined, (3) 3 months symptom-free after treatment. May be able to drive private vehicle earlier if cause identified/low risk. Legal obligation: Doctors must inform patients of driving restrictions; patients must notify licensing authority. High-risk situations: Syncope during exertion, while driving, with cardiac cause - higher SCD risk, longer restrictions. If ICD implanted: Cannot drive 6 months after implant or shock. Reporting requirements vary by state - check local guidelines."
    },

    "CARD-MCQ-0118": {
        "subtopic": "Neurocardiogenic Syncope vs Seizure",
        "scenario": "A 19-year-old woman is brought to ED by ambulance after 'seizure' at school. Witnesses report she was standing in assembly, became pale, collapsed, and had 'jerking movements of arms and legs for 10-15 seconds'. She recovered within 1 minute, oriented immediately, no confusion. No tongue biting, no incontinence. ECG normal.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Epileptic seizure - start antiepileptic drugs",
            "B": "Convulsive syncope (vasovagal syncope with myoclonic jerks due to cerebral hypoxia) - benign, not epilepsy",
            "C": "Cardiac arrhythmia - needs pacemaker",
            "D": "Stroke"
        },
        "correct_answer": "B",
        "explanation": "Convulsive syncope: Brief myoclonic jerking during syncope due to cerebral hypoxia, often misdiagnosed as epilepsy. Distinguishing syncope from seizures: Syncope (with convulsive features): (1) Trigger: Upright posture, prolonged standing, heat, pain; (2) Prodrome: Seconds-minutes of lightheadedness, nausea, pallor, visual dimming; (3) Posture: Usually upright; (4) LOC duration: <30 seconds; (5) Movements: Brief myoclonic jerks (<15 seconds), not rhythmic tonic-clonic; (6) Recovery: Immediate orientation, no confusion; (7) Injury: Rare (collapses gradually); (8) Tongue biting: Absent or tip only; (9) Incontinence: Rare; (10) Post-ictal: None. Epileptic seizures: (1) Trigger: None, or specific (flashing lights); (2) Aura: Seconds, often stereotyped (déjà vu, epigastric rising, unusual smells); (3) Posture: Any position (can occur lying down); (4) LOC duration: >1 minute typically; (5) Movements: Prolonged tonic-clonic (>30 seconds), rhythmic; (6) Recovery: Post-ictal confusion (minutes-hours); (7) Injury: Common (falls like 'tree trunk'); (8) Tongue biting: Lateral tongue (specific for seizures); (9) Incontinence: Common; (10) Post-ictal: Confusion, drowsiness, headache. This patient: Classic convulsive syncope - upright posture, pallor (witnessed), brief jerking, immediate recovery, no confusion. Cerebral hypoxia from syncope causes myoclonic jerks ('anoxic seizure'), but NOT epilepsy. Management: Treat as vasovagal syncope (education, avoid triggers). EEG not needed if clinical diagnosis clear. Antiepileptic drugs not indicated (ineffective, unnecessary side effects). Misdiagnosis as epilepsy common - leads to unnecessary AED treatment, driving restrictions. Clue: Syncope patients collapse gradually (slide to ground), seizure patients fall like 'tree trunk'."
    },

    "CARD-MCQ-0119": {
        "subtopic": "Unexplained Syncope - Long-term Prognosis",
        "scenario": "A 45-year-old woman has completed full syncope evaluation (history, exam, ECG, echo, Holter, tilt table, blood tests) with no abnormalities identified. She has had 2 episodes of unexplained syncope over past year. She is concerned about prognosis.",
        "stem": "What is the appropriate counseling regarding prognosis?",
        "options": {
            "A": "Very high mortality risk - needs aggressive intervention",
            "B": "Unexplained syncope after thorough evaluation has generally good prognosis if no structural heart disease; recurrence risk 30-40%, but low mortality; consider implantable loop recorder for diagnosis",
            "C": "Definitely epilepsy - start antiepileptics",
            "D": "100% recurrence rate"
        },
        "correct_answer": "B",
        "explanation": "Prognosis of syncope (depends on etiology): Cardiac syncope: (1) Highest risk: 1-year mortality 20-30%; (2) Sudden cardiac death risk 5-10%; (3) Arrhythmic/structural heart disease. Reflex/vasovagal syncope: (1) Benign: no increased mortality; (2) Recurrence 30-50% over 2-5 years; (3) Injury risk (~10% per episode - fractures, head trauma); (4) Quality of life impact. Orthostatic hypotension: (1) Moderate risk: increased falls, fractures; (2) Underlying cause determines prognosis. Unexplained syncope (after full evaluation): (1) Generally good prognosis IF: No structural heart disease, Normal ECG, Normal echo; (2) 1-year mortality similar to general population (~1-2%); (3) Recurrence risk 30-40% over 3-5 years; (4) Likely represents undiagnosed reflex syncope. This patient: Full negative evaluation - reassuring. Suggest: (1) Reassure: low mortality risk; (2) Implantable loop recorder: 50-70% diagnostic yield over 1-2 years - identifies arrhythmias or asystole if present, or documents sinus rhythm during symptoms (rules out arrhythmia); (3) Safety counseling: Avoid high-risk activities until diagnosis (driving restrictions, avoid heights, swimming alone); (4) Follow-up: repeat evaluation if symptoms change or new symptoms develop. ILR data: In unexplained syncope, ILR often shows: (1) Asystole/bradycardia (40%), (2) Tachycardia (5%), (3) Sinus rhythm during symptoms - excludes arrhythmia (40%). Decision for ILR depends on: syncope frequency, impact on quality of life, patient preference."
    },

    "CARD-MCQ-0120": {
        "subtopic": "Postural Orthostatic Tachycardia Syndrome (POTS)",
        "scenario": "A 24-year-old woman presents with 6 months of dizziness, palpitations, and near-syncope when standing. Symptoms improve lying down. BP lying 120/75 mmHg, standing 115/80 mmHg (no significant drop), but HR increases from 68 to 128 bpm. No other abnormalities on examination. ECG normal.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Orthostatic hypotension",
            "B": "Postural Orthostatic Tachycardia Syndrome (POTS) - sustained HR increase ≥30 bpm (or HR ≥120 bpm) on standing without orthostatic hypotension",
            "C": "Panic disorder",
            "D": "Hyperthyroidism"
        },
        "correct_answer": "B",
        "explanation": "POTS (Postural Orthostatic Tachycardia Syndrome): Autonomic disorder causing excessive HR increase on standing. Diagnostic criteria: (1) Sustained HR increase ≥30 bpm (or HR ≥120 bpm) within 10 minutes of standing; (2) WITHOUT orthostatic hypotension (BP drop <20/10 mmHg); (3) Symptoms of cerebral hypoperfusion (lightheadedness, palpitations, tremor, weakness) and/or sympathetic activation; (4) Duration ≥3 months. Epidemiology: (1) Young females predominantly (female:male 5:1); (2) Peak onset 15-25 years; (3) Often follows viral illness, trauma, pregnancy. Pathophysiology: (1) Hypovolemia (low blood volume); (2) Peripheral denervation (neuropathic subtype); (3) Hyperadrenergic (excessive sympathetic response). Symptoms: (1) Orthostatic intolerance (dizziness, lightheadedness, near-syncope on standing); (2) Palpitations, tremor; (3) Brain fog, fatigue; (4) Exercise intolerance; (5) GI symptoms (nausea, bloating). Diagnosis: (1) 10-minute stand test or tilt table: Document HR/BP response; (2) Exclude other causes: Anemia, hyperthyroidism, dehydration, medications; (3) Autonomic testing if available. Management: (1) Non-pharmacological: Increase fluid (2-3L/day) and salt (6-10g/day), Compression stockings, Exercise program (recumbent initially - rowing, swimming), Avoid triggers (heat, alcohol, prolonged standing); (2) Pharmacological: Beta-blockers (propranolol, low-dose), Ivabradine (pure HR reduction), Fludrocortisone, Midodrine. This patient: Classic POTS - young female, excessive HR rise (60 bpm) without BP drop, symptoms on standing. Differentiate from: Orthostatic hypotension (BP drops), anxiety (symptoms in all positions), deconditioning (improves with exercise program). Prognosis: Variable - 50% improve over 2-5 years, others chronic symptoms."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 6D UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 6D: MCQ-0101 to 0120 (Pituitary + Syncope)")
    print(f"Sub-batch 4 of 5 in Batch 6 (100 MCQs total)")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch6d_generated)

    print(f"\n✅ Batch 6D Complete: {updated}/20 MCQs updated")
    print(f"✅ Total Progress: 120/658 MCQs (18.2%)")
    print(f"\n🔄 Batch 6 Progress: 80/100 complete")
    print(f"Next: Batch 6E (MCQs 0121-0140 - Final 20 MCQs to complete Batch 6!)")
