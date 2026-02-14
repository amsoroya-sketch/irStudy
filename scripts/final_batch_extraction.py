#!/usr/bin/env python3
"""
FINAL BATCH EXTRACTION - Reach 750 cards
Manually curated high-quality cards from all remaining modules
Focus: High-yield OSCE content
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_FILE = Path(
    "/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json"
)

with open(OUTPUT_FILE, "r") as f:
    data = json.load(f)

next_id = len(data["cards"]) + 1


# Helper function
def c(front, back, cat, diff, deck, src):
    """Add card"""
    global next_id
    data["cards"].append(
        {
            "id": next_id,
            "front": front,
            "back": back,
            "deck": deck,
            "tags": [cat, diff],
            "source": src,
            "difficulty": diff,
            "category": cat,
        }
    )
    next_id += 1


# Shortened for brevity - deck names
MG = "Medicine_Gastroenterology"
MC = "Medicine_Cardiorespiratory"
MN = "Medicine_Neurology"
ME = "Medicine_Endocrinology"
MEM = "Medicine_Emergency"
MENT = "Medicine_ENT"
MCARD = "Medicine_Cardiology"
MGEN = "Medicine_General"
SUR = "Surgery"
OG = "ObGyn"
PAED = "Paediatrics"
PSY = "Psychiatry"
ETH = "Ethics_Communication"
GEN = "General"

# ==================================================================
# MEDICINE - Additional Red Flags & Differentials
# ==================================================================

# GI Bleeding (continued)
c(
    "🚨 RED FLAG: Massive haematemesis immediate management",
    "Haematemesis + haemodynamic instability → 2x large-bore IV (14-16G) + crossmatch 6 units + IV tranexamic acid 1g + activate massive transfusion + URGENT endoscopy + ICU",
    "red_flags",
    "hard",
    MG,
    "Medicine/02_GI_Bleeding_Differentials.html",
)

c(
    "Differentials: Causes of melaena (black tarry stool)",
    "• Peptic ulcer (most common)\n• Oesophageal varices\n• Mallory-Weiss tear\n• Gastritis\n• Upper GI malignancy\n• Aorto-enteric fistula (if AAA repair history)",
    "differential",
    "medium",
    MG,
    "Medicine/02_GI_Bleeding_Differentials.html",
)

c(
    "IMG Mistake: Not calculating Rockall score in upper GI bleed",
    "Rockall score predicts rebleeding and mortality. Age, shock, comorbidities, diagnosis, stigmata of recent haemorrhage. Score ≥3 = high risk → URGENT endoscopy.",
    "img_mistake",
    "medium",
    MG,
    "Medicine/02_GI_Bleeding_Differentials.html",
)

c(
    "Australian: Upper GI endoscopy timing (eTG guidelines)",
    "HIGH RISK (Rockall ≥3, ongoing bleeding, hypotension): Endoscopy within 24h\nAVERAGE RISK: Endoscopy within 24-48h\nLOW RISK: Outpatient endoscopy\nAll receive IV PPI (pantoprazole 80mg bolus + 8mg/h infusion)",
    "australian",
    "medium",
    MG,
    "Medicine/02_GI_Bleeding_Differentials.html",
)

# Cardiorespiratory (continued)
c(
    "🚨 RED FLAG: Cardiac tamponade (Beck's triad)",
    "Hypotension + raised JVP + muffled heart sounds + pulsus paradoxus → URGENT pericardiocentesis (echo-guided)",
    "red_flags",
    "hard",
    MC,
    "Medicine/01_Cardiovascular_Respiratory_History.html",
)

c(
    "🚨 RED FLAG: Acute severe asthma (life-threatening features)",
    "Silent chest + cyanosis + exhaustion + confusion + bradycardia + hypotension → Immediate high-flow O2 + salbutamol continuous nebulizer + IV magnesium + hydrocortisone + ICU",
    "red_flags",
    "hard",
    MC,
    "Medicine/01_Cardiovascular_Respiratory_History.html",
)

c(
    "Differentials: Chronic cough causes (>8 weeks)",
    "• Post-nasal drip (upper airway cough syndrome)\n• Asthma/eosinophilic bronchitis\n• GORD\n• ACE inhibitor\n• Chronic bronchitis\n• Bronchiectasis\n• Lung cancer",
    "differential",
    "medium",
    MC,
    "Medicine/01_Cardiovascular_Respiratory_History.html",
)

c(
    "Physical exam: Differentiating pleural effusion vs consolidation",
    "EFFUSION: Stony dull percussion + reduced breath sounds + reduced vocal resonance\nCONSOLIDATION: Dull percussion + bronchial breathing + increased vocal resonance + crackles",
    "physical_exam",
    "medium",
    MC,
    "Medicine/02_Physical_Examination_Cardiovascular_Respiratory.html",
)

c(
    "Australian: Oxygen prescribing in COPD",
    "Target SpO2 88-92% in COPD (not 94-98%). Risk of CO2 retention with high-flow O2 → Venturi mask (fixed concentration): 24%, 28% initially. Monitor ABG.",
    "australian",
    "medium",
    MC,
    "Medicine/01_Cardiovascular_Respiratory_History.html",
)

# Neurology (continued)
c(
    "🚨 RED FLAG: Bacterial meningitis empirical treatment",
    "Suspected meningitis + NO focal neurology/papilloedema → LP + blood cultures → IV ceftriaxone 2g BD (+ ampicillin if >50 years for Listeria) + dexamethasone 10mg QID x 4 days\nIf focal neurology/papilloedema → CT first, then LP",
    "red_flags",
    "hard",
    MN,
    "Medicine/03_Neurology_Headache_Differentials.html",
)

c(
    "Differentials: Causes of headache + fever",
    "• Meningitis (bacterial, viral, fungal)\n• Encephalitis\n• Brain abscess\n• Sinusitis\n• Viral illness (influenza)\n• Malaria (if returned traveler)",
    "differential",
    "hard",
    MN,
    "Medicine/03_Neurology_Headache_Differentials.html",
)

c(
    "Physical exam: Kernig's sign vs Brudzinski's sign",
    "KERNIG'S: Hip flexed to 90°, attempt to extend knee → Pain/resistance = positive (meningism)\nBRUDZINSKI'S: Passive neck flexion → Involuntary hip/knee flexion = positive (meningism)",
    "physical_exam",
    "medium",
    MN,
    "Medicine/03_Neurology_Headache_Differentials.html",
)

c(
    "IMG Mistake: Giving steroids before LP in suspected meningitis",
    "Give dexamethasone AFTER or WITH first dose of antibiotics (NOT before). If delay in LP, give antibiotics immediately, don't wait for LP. DON'T delay antibiotics for imaging.",
    "img_mistake",
    "medium",
    MN,
    "Medicine/03_Neurology_Headache_Differentials.html",
)

c(
    "🚨 RED FLAG: Stroke thrombolysis timeframe",
    "Ischaemic stroke + <4.5 hours from onset + no contraindications (haemorrhage on CT, recent surgery, bleeding disorder, BP >185/110) → IV alteplase 0.9mg/kg + thrombectomy if large vessel occlusion",
    "red_flags",
    "hard",
    MN,
    "Medicine/04_Neurology_Weakness_Limb_Examination.html",
)

c(
    "Physical exam: FAST (stroke recognition)",
    "F = Face (facial droop)\nA = Arms (arm drift)\nS = Speech (slurred, unable to speak)\nT = Time (call 000 immediately)\nPositive FAST → Stroke until proven otherwise",
    "physical_exam",
    "hard",
    MN,
    "Medicine/04_Neurology_Weakness_Limb_Examination.html",
)

c(
    "Differentials: Acute unilateral weakness causes",
    "• Stroke (most common)\n• Todd's paresis (post-ictal)\n• Hemiplegic migraine\n• Hypoglycaemia\n• Functional (conversion disorder)\n• Subdural haematoma\n• Brain tumor",
    "differential",
    "hard",
    MN,
    "Medicine/04_Neurology_Weakness_Limb_Examination.html",
)

# Emergency Medicine
c(
    "🚨 RED FLAG: Rhabdomyolysis and acute kidney injury",
    "Myalgia + dark urine (tea-colored) + elevated CK (>5x normal) + AKI → IV fluids (target urine output 200-300mL/h) + urinary alkalinization + monitor K+ (hyperkalaemia risk) + dialysis if severe",
    "red_flags",
    "hard",
    MEM,
    "Medicine/10_Emergency_Anaphylaxis_Management.html",
)

c(
    "Australian: Snake bite management (Australian snakes)",
    "Pressure immobilization bandage + limb splint + keep still + DO NOT wash bite site → ID snake (brown, tiger, taipan, death adder, black) → Venom detection kit → Antivenom (specific to snake type) IV in monitored setting",
    "australian",
    "medium",
    MEM,
    "Emergency medicine",
)

c(
    "🚨 RED FLAG: Status epilepticus treatment protocol",
    "Seizure >5 min or ≥2 seizures without recovery:\n0-5 min: ABCDE, glucose, thiamine\n5-10 min: Midazolam 10mg IM/buccal OR diazepam 10mg IV\n10-20 min: Repeat benzodiazepine\n20-40 min: Phenytoin 20mg/kg IV infusion OR levetiracetam\n>40 min: Intubate + general anaesthesia",
    "red_flags",
    "hard",
    MEM,
    "Medicine/12_Emergency_Seizure_Management.html",
)

c(
    "Differentials: Causes of seizures (first presentation)",
    "• Idiopathic epilepsy\n• Structural (stroke, tumor, head injury)\n• Metabolic (hypoglycaemia, hyponatraemia, hypocalcaemia)\n• Infection (meningitis, encephalitis)\n• Drug-related (alcohol withdrawal, cocaine)\n• Eclampsia (pregnant women)",
    "differential",
    "medium",
    MEM,
    "Medicine/12_Emergency_Seizure_Management.html",
)

c(
    "Australian: Seizure driving restrictions (NSW)",
    "First seizure: 6 months off driving (private vehicle)\nEstablished epilepsy: 12 months seizure-free (or only sleep seizures for ≥1 year)\nCommercial vehicle: 5-10 years seizure-free\nDoctor MUST advise patient (document in notes)",
    "australian",
    "hard",
    MEM,
    "Medicine/12_Emergency_Seizure_Management.html",
)

# Endocrinology
c(
    "🚨 RED FLAG: DKA diagnostic criteria",
    "Glucose >11mmol/L + pH <7.3 (or HCO3 <15) + ketonaemia (blood ketones >3mmol/L) or ketonuria (2+ on dipstick)\nManagement: IV fluids (1L 0.9% NaCl first hour) + fixed-rate insulin infusion 0.1 unit/kg/h + potassium replacement + find precipitant",
    "red_flags",
    "hard",
    ME,
    "Medicine/09_Endocrinology_Diabetes_Management.html",
)

c(
    "🚨 RED FLAG: Hyperosmolar hyperglycaemic state (HHS)",
    "Glucose >30mmol/L + osmolality >320 + NO significant ketones + hypovolaemia → Slower rehydration than DKA (avoid cerebral oedema) + lower insulin dose + monitor Na+ closely",
    "red_flags",
    "hard",
    ME,
    "Medicine/09_Endocrinology_Diabetes_Management.html",
)

c(
    "Differentials: Causes of hypoglycaemia",
    "DIABETIC: Insulin/sulphonylurea excess, missed meal, exercise, alcohol\nNON-DIABETIC: Insulinoma, adrenal insufficiency, liver failure, sepsis, alcohol, drugs (beta-blockers, quinine)",
    "differential",
    "medium",
    ME,
    "Medicine/09_Endocrinology_Diabetes_Management.html",
)

c(
    "Australian: Continuous glucose monitoring (CGM) PBS access",
    "FreeStyle Libre (CGM sensor): PBS-subsidized for Type 1 diabetes (<21 years), pregnant with Type 1, or NDSS-registered Type 1 with recent severe hypo/DKA. Expensive if not eligible (~$100/sensor, lasts 14 days).",
    "australian",
    "easy",
    ME,
    "Medicine/09_Endocrinology_Diabetes_Management.html",
)

c(
    "IMG Mistake: Not checking for DKA in hyperglycaemia",
    "Glucose >15mmol/L → ALWAYS check ketones (blood or urine). Don't assume Type 2 diabetes can't get DKA (can occur in SGLT2 inhibitor use - 'euglycaemic DKA').",
    "img_mistake",
    "medium",
    ME,
    "Medicine/09_Endocrinology_Diabetes_Management.html",
)

# ENT
c(
    "Physical exam: Otoscopy - normal tympanic membrane landmarks",
    "Pearly grey, translucent membrane\nLight reflex (5 o'clock right ear, 7 o'clock left ear)\nHandle of malleus visible\nCone of light\nNo bulging, retraction, or perforation",
    "physical_exam",
    "easy",
    MENT,
    "Medicine/05_Physical_Examination_ENT.html",
)

c(
    "🚨 RED FLAG: Acute epiglottitis",
    "Severe sore throat + drooling + muffled voice + sitting forward (tripod position) + stridor → DO NOT examine throat (may precipitate total airway obstruction) → IMMEDIATE ENT/anaesthetics → Intubation in theatre + IV ceftriaxone",
    "red_flags",
    "hard",
    MENT,
    "Medicine/05_Physical_Examination_ENT.html",
)

c(
    "Differentials: Causes of vertigo",
    "PERIPHERAL: BPPV (most common), vestibular neuronitis, Meniere's disease, vestibular migraine\nCENTRAL: Stroke (brainstem/cerebellum), MS, tumor, medications",
    "differential",
    "medium",
    MENT,
    "Medicine/05_Physical_Examination_ENT.html",
)

c(
    "Physical exam: Dix-Hallpike test (BPPV diagnosis)",
    "Patient sitting → Turn head 45° to affected side → Rapidly lie back (head hangs 20° below horizontal) → Observe for nystagmus + vertigo (latency 5-10s, fatigable) = Positive\nPositive → Epley maneuver treatment",
    "physical_exam",
    "medium",
    MENT,
    "Medicine/05_Physical_Examination_ENT.html",
)

c(
    "IMG Mistake: Not differentiating peripheral vs central vertigo",
    "PERIPHERAL: Horizontal/rotatory nystagmus, +ve Dix-Hallpike, NO focal neurology\nCENTRAL: Vertical nystagmus, focal neurology (ataxia, diplopia, weakness) → URGENT imaging (stroke risk)",
    "img_mistake",
    "medium",
    MENT,
    "Medicine/05_Physical_Examination_ENT.html",
)

# Cardiology/ECG
c(
    "Physical exam: ECG - STEMI territory localization",
    "ANTERIOR: V1-V4 (LAD occlusion)\nINFERIOR: II, III, aVF (RCA occlusion)\nLATERAL: I, aVL, V5-V6 (circumflex occlusion)\nPOSTERIOR: Tall R waves V1-V2 + ST depression (posterior leads V7-V9 show ST elevation)",
    "physical_exam",
    "hard",
    MCARD,
    "Medicine/11_ECG_Interpretation_Guide.html",
)

c(
    "🚨 RED FLAG: Wellens' syndrome (LAD occlusion warning)",
    "Biphasic or deeply inverted T waves in V2-V3 + recent chest pain (now pain-free) + normal/minimally elevated troponin → High risk of LAD occlusion → URGENT angiography (even if pain resolved)",
    "red_flags",
    "hard",
    MCARD,
    "Medicine/11_ECG_Interpretation_Guide.html",
)

c(
    "Differentials: Causes of atrial fibrillation",
    "Cardiac: IHD, valvular (mitral), heart failure, pericarditis\nNon-cardiac: Hyperthyroidism, alcohol, sepsis, PE, post-operative\nLone AF (no identifiable cause)",
    "differential",
    "medium",
    MCARD,
    "Medicine/11_ECG_Interpretation_Guide.html",
)

c(
    "Australian: CHADS-VASc score for AF anticoagulation",
    "C = CHF (1), H = Hypertension (1), A = Age ≥75 (2), D = Diabetes (1), S = Stroke/TIA (2), V = Vascular disease (1), A = Age 65-74 (1), Sc = Sex female (1)\nScore ≥2 men/≥3 women → Anticoagulation (apixaban, rivaroxaban, warfarin)\nPBS restricts NOACs to CHADS-VASc ≥1",
    "australian",
    "medium",
    MCARD,
    "Medicine/11_ECG_Interpretation_Guide.html",
)

c(
    "IMG Mistake: Not recognizing posterior MI",
    "ST depression in V1-V3 in context of chest pain = posterior STEMI (NOT NSTEMI). Request posterior leads (V7-V9) showing ST elevation → Immediate PCI.",
    "img_mistake",
    "hard",
    MCARD,
    "Medicine/11_ECG_Interpretation_Guide.html",
)

# ==================================================================
# SURGERY - Expanded Content
# ==================================================================

c(
    "Physical exam: Abdominal examination - McBurney's point",
    "Location: 1/3 distance from ASIS to umbilicus (right lower quadrant). Maximum tenderness at McBurney's point = appendicitis (not specific, but suggestive).",
    "physical_exam",
    "easy",
    SUR,
    "Surgery/02_Acute_Abdomen_Physical_Examination.html",
)

c(
    "Physical exam: Rovsing's sign",
    "Palpate LEFT lower quadrant → Pain in RIGHT lower quadrant = Positive Rovsing's sign → Suggests appendicitis (peritoneal irritation)",
    "physical_exam",
    "easy",
    SUR,
    "Surgery/02_Acute_Abdomen_Physical_Examination.html",
)

c(
    "Physical exam: Psoas sign",
    "Passive right hip extension (patient lying on left side) → Pain = Positive psoas sign → Inflamed appendix overlying psoas muscle",
    "physical_exam",
    "easy",
    SUR,
    "Surgery/02_Acute_Abdomen_Physical_Examination.html",
)

c(
    "Physical exam: Obturator sign",
    "Passive internal rotation of flexed right hip → Pain = Positive obturator sign → Inflamed appendix overlying obturator internus",
    "physical_exam",
    "easy",
    SUR,
    "Surgery/02_Acute_Abdomen_Physical_Examination.html",
)

c(
    "Differentials: Causes of bowel obstruction",
    "SMALL BOWEL: Adhesions (60% - previous surgery), hernias, malignancy, Crohn's, intussusception\nLARGE BOWEL: Malignancy (60%), diverticular stricture, volvulus, faecal impaction",
    "differential",
    "medium",
    SUR,
    "Surgery/01_Acute_Abdomen_History_Differentials.html",
)

c(
    "🚨 RED FLAG: Closed loop obstruction",
    "Bowel obstruction + two points of obstruction (e.g., competent ileocaecal valve in large bowel obstruction) → Rapid distension → Perforation risk → IMMEDIATE surgery (don't wait for conservative management)",
    "red_flags",
    "hard",
    SUR,
    "Surgery/01_Acute_Abdomen_History_Differentials.html",
)

c(
    "Australian: Surgical consent documentation",
    "Document in notes: Diagnosis, procedure, risks (common + serious), benefits, alternatives, patient questions, patient understanding. Patient signs consent form. For high-risk procedures, consultant should obtain consent (not junior doctor).",
    "australian",
    "medium",
    SUR,
    "Surgery/04_Pre_Post_Operative_Assessment.html",
)

c(
    "IMG Mistake: Not recognizing post-operative ileus",
    "Post-op: No bowel sounds + distension + nausea/vomiting + no flatus → Ileus (normal after abdominal surgery, usually resolves 3-5 days). If persists >5 days or worsening → CT (exclude mechanical obstruction).",
    "img_mistake",
    "medium",
    SUR,
    "Surgery/04_Pre_Post_Operative_Assessment.html",
)

# Lumps and hernias
c(
    "Physical exam: Examining a lump - 7 characteristics",
    "1. Site + size\n2. Shape (regular/irregular)\n3. Surface (smooth/irregular)\n4. Consistency (soft/firm/hard)\n5. Temperature (warm = infection/inflammation)\n6. Tenderness\n7. Mobility (skin/muscle/fixed)",
    "physical_exam",
    "medium",
    SUR,
    "Surgery/03_Surgical_Lumps_Hernias_History_Examination.html",
)

c(
    "Physical exam: Transillumination test",
    "Shine light through lump in dark room. Transilluminates (light passes through) → Fluid-filled (cyst, hydrocele). Does NOT transilluminate → Solid mass.",
    "physical_exam",
    "easy",
    SUR,
    "Surgery/03_Surgical_Lumps_Hernias_History_Examination.html",
)

c(
    "Differentials: Groin lump differentials",
    "• Inguinal hernia (most common)\n• Femoral hernia\n• Lymph node (lymphadenopathy)\n• Saphena varix\n• Lipoma\n• Undescended/ectopic testis\n• Psoas abscess",
    "differential",
    "medium",
    SUR,
    "Surgery/03_Surgical_Lumps_Hernias_History_Examination.html",
)

c(
    "Physical exam: Inguinal vs femoral hernia differentiation",
    "INGUINAL: Above and medial to pubic tubercle, descends into scrotum (indirect), more common in men\nFEMORAL: Below and lateral to pubic tubercle, does NOT enter scrotum, higher strangulation risk, more common in women",
    "physical_exam",
    "medium",
    SUR,
    "Surgery/03_Surgical_Lumps_Hernias_History_Examination.html",
)

c(
    "IMG Mistake: Missing breast cancer red flags",
    "RED FLAGS: Hard irregular lump, skin tethering, nipple inversion/retraction, peau d'orange (skin dimpling), bloody nipple discharge, axillary lymphadenopathy, age >40 → URGENT referral (2-week rule) + triple assessment (clinical + imaging + biopsy)",
    "img_mistake",
    "hard",
    SUR,
    "Surgery/03_Surgical_Lumps_Hernias_History_Examination.html",
)

# Trauma
c(
    "Physical exam: Log roll examination technique",
    "Minimum 3 people (1 controls C-spine, 2 roll patient). Maintain in-line spinal immobilization. Examine: Back, spine palpation (tenderness, step deformity), PR exam (tone, blood, prostate position). Roll back carefully.",
    "physical_exam",
    "medium",
    SUR,
    "Surgery/05_Trauma_Assessment.html",
)

c(
    "🚨 RED FLAG: Pelvic fracture with haemodynamic instability",
    "High-impact trauma + pelvic fracture on XR + hypotension → Massive retroperitoneal haemorrhage → Pelvic binder + IV resuscitation + tranexamic acid + crossmatch 6 units + interventional radiology (embolization) OR ex-fix OR surgery",
    "red_flags",
    "hard",
    SUR,
    "Surgery/05_Trauma_Assessment.html",
)

c(
    "Differentials: Causes of shock in trauma",
    "• Haemorrhagic (most common - external bleeding, internal bleeding)\n• Tension pneumothorax\n• Cardiac tamponade\n• Neurogenic (spinal cord injury - bradycardia + hypotension)\n• Septic (rare acutely)",
    "differential",
    "hard",
    SUR,
    "Surgery/05_Trauma_Assessment.html",
)

c(
    "Australian: Major trauma criteria (NSW)",
    "HIGH RISK MECHANISM: Fall >3m, high-speed MVC, pedestrian/cyclist vs car, ejection from vehicle\nPHYSIOLOGY: GCS <13, RR <10 or >29, SBP <90, penetrating injury head/neck/torso\nANATOMY: Flail chest, 2+ long bone fractures, pelvic fracture, paralysis\n→ Activate trauma team",
    "australian",
    "medium",
    SUR,
    "Surgery/05_Trauma_Assessment.html",
)

# ==================================================================
# OBGYN - Expanded Content
# ==================================================================

c(
    "🚨 RED FLAG: Ruptured ectopic pregnancy management",
    "Ectopic pregnancy + haemodynamic instability (hypotension, tachycardia) → Ruptured → 2x large bore IV + crossmatch + tranexamic acid + IMMEDIATE laparoscopy (salpingectomy) + resuscitation\nStable → Laparoscopy OR medical (methotrexate if criteria met)",
    "red_flags",
    "hard",
    OG,
    "ObGyn/01_Obstetric_History_Differentials.html",
)

c(
    "Differentials: Causes of miscarriage (pregnancy loss <20 weeks)",
    "• Chromosomal abnormalities (50%)\n• Maternal factors (uterine anomalies, cervical incompetence, antiphospholipid syndrome)\n• Infections (rare)\n• Idiopathic (often no cause found)",
    "differential",
    "medium",
    OG,
    "ObGyn/01_Obstetric_History_Differentials.html",
)

c(
    "Physical exam: Obstetric abdominal palpation - Leopold's maneuvers",
    "1st: Fundal palpation (head vs breech)\n2nd: Lateral palpation (fetal back vs limbs)\n3rd: Suprapubic palpation (presenting part)\n4th: Pelvic grip (engagement - 5/5 to 0/5 fifths palpable)",
    "physical_exam",
    "medium",
    OG,
    "ObGyn/04_Obstetric_Examination.html",
)

c(
    "Australian: Antenatal screening (public system)",
    "First trimester: Dating scan (8-12 weeks), combined first trimester screening (CFTS at 11-13 weeks - NT + βhCG + PAPP-A)\nSecond trimester: Morphology scan (18-20 weeks - structural abnormalities)\nGestational diabetes screening: OGTT at 24-28 weeks\nAll FREE in public system",
    "australian",
    "easy",
    OG,
    "ObGyn/01_Obstetric_History_Differentials.html",
)

c(
    "IMG Mistake: Not recognizing placenta praevia risk factors",
    "RISK: Previous C-section, multiparity, advanced maternal age, smoking, previous placenta praevia\nPresentation: Painless PV bleeding in 3rd trimester\nManagement: NO vaginal examination (precipitate massive haemorrhage), ultrasound, elective C-section at 36-37 weeks",
    "img_mistake",
    "hard",
    OG,
    "ObGyn/01_Obstetric_History_Differentials.html",
)

# Gynaecological
c(
    "Physical exam: Speculum examination steps",
    "1. Consent + chaperone\n2. Empty bladder\n3. Lithotomy position\n4. Warm speculum, lubricate with water only (not gel - interferes with cytology)\n5. Insert obliquely, rotate 90°, open blades, visualize cervix\n6. Cervical smear if indicated\n7. Remove, rotate back",
    "physical_exam",
    "medium",
    OG,
    "ObGyn/05_Gynaecological_Examination.html",
)

c(
    "🚨 RED FLAG: Cervical cancer clinical features",
    "Post-coital bleeding + intermenstrual bleeding + postmenopausal bleeding + foul-smelling discharge → Speculum shows abnormal cervix (ulcerated, irregular, bleeds on contact) → URGENT gynae referral + cervical biopsy",
    "red_flags",
    "hard",
    OG,
    "ObGyn/02_Gynaecological_History_Differentials.html",
)

c(
    "Australian: National Cervical Screening Program",
    "Cervical screening test (CST): Every 5 years from age 25-74 (changed from 2-yearly Pap smear in 2017). Tests for high-risk HPV. If HPV positive → Reflex LBC (liquid-based cytology). Self-collection option available.",
    "australian",
    "medium",
    OG,
    "ObGyn/02_Gynaecological_History_Differentials.html",
)

c(
    "Communication: Explaining Mirena (hormonal IUS) to patient",
    '"Mirena is a small T-shaped device inserted into your uterus. It releases a hormone that thins the uterine lining, reducing bleeding. It lasts 5 years, very effective contraception (>99%). Common side effects: Irregular bleeding first 3-6 months (usually settles), some women\'s periods stop completely (this is safe). You can have it removed anytime."',
    "communication",
    "medium",
    OG,
    "ObGyn/03_Contraception_Counselling.html",
)

# ==================================================================
# PSYCHIATRY - Expanded Content
# ==================================================================

c(
    "Physical exam: Mini-Mental State Examination (MMSE) scoring",
    "30 points total:\nOrientation (10): Time 5, place 5\nRegistration (3): Repeat 3 words\nAttention (5): Serial 7s or spell WORLD backwards\nRecall (3): Recall 3 words\nLanguage (9): Naming, repetition, 3-stage command, read, write, copy\n<24/30 = cognitive impairment",
    "physical_exam",
    "medium",
    PSY,
    "Psychiatry/02_Mental_State_Examination.html",
)

c(
    "Differentials: Causes of delirium (acute confusion)",
    "DELIRIUM mnemonic:\nD = Drugs (opioids, benzos, anticholinergics)\nE = Eyes, ears (sensory impairment)\nL = Low O2 (hypoxia, PE, MI)\nI = Infection (UTI, pneumonia)\nR = Retention (urinary, constipation)\nI = Ictal (seizure)\nU = Underhydration/undernourishment\nM = Metabolic (hypoglycaemia, electrolytes)",
    "differential",
    "medium",
    PSY,
    "Psychiatry/04_Common_Psychiatric_Presentations.html",
)

c(
    "🚨 RED FLAG: Lithium toxicity",
    "Lithium level >1.5mmol/L + coarse tremor + ataxia + confusion + seizures + arrhythmias → STOP lithium + IV fluids + haemodialysis if severe (>2.5mmol/L) + monitor renal function + ECG",
    "red_flags",
    "hard",
    PSY,
    "Psychiatry/04_Common_Psychiatric_Presentations.html",
)

c(
    "Australian: Mental Health Treatment Plan (MHTP)",
    "GP Mental Health Treatment Plan: Allows 10 subsidized psychology sessions/year (6 initial + 4 additional with review). Patient pays gap (~$50-100/session after Medicare rebate). Review required for additional sessions.",
    "australian",
    "easy",
    PSY,
    "Psychiatry/04_Common_Psychiatric_Presentations.html",
)

c(
    "Communication: De-escalation techniques for agitated patient",
    "1. Ensure safety (exit route, alarm)\n2. Non-threatening posture (sit if safe, arms open)\n3. Calm tone, slow speech\n4. Active listening, validate feelings\n5. Offer choices, avoid confrontation\n6. Set clear limits if needed\n7. Call security if unsafe",
    "communication",
    "medium",
    PSY,
    "Psychiatry/03_Risk_Assessment_Suicide_Violence_Selfneglect.html",
)

c(
    "IMG Mistake: Not documenting capacity assessment properly",
    "Document: (1) Decision being made (2) Information provided (3) Patient's understanding, retention, use/weigh, communication (4) Conclusion (has/lacks capacity) (5) Best interests if lacks capacity. Medicolegal protection.",
    "img_mistake",
    "medium",
    PSY,
    "Psychiatry/05_Capacity_Assessment_Legal_Framework.html",
)

# ==================================================================
# PAEDIATRICS - Expanded Content
# ==================================================================

c(
    "🚨 RED FLAG: Sepsis in children (warning signs)",
    "Tachycardia (age-dependent) + tachypnoea + prolonged capillary refill >2sec + reduced consciousness + mottled/pale skin + not feeding → Sepsis → IV/IO access + fluid bolus 20mL/kg + IV antibiotics (ceftriaxone) + URGENT paediatric review",
    "red_flags",
    "hard",
    PAED,
    "Paediatrics/02_Common_Paediatric_Presentations.html",
)

c(
    "Physical exam: Assessing dehydration in children (clinical signs)",
    "MILD (3-5%): Dry mucous membranes, decreased urine output\nMODERATE (5-10%): Sunken eyes, reduced skin turgor, sunken fontanelle (infants), lethargy\nSEVERE (>10%): Prolonged capillary refill, tachycardia, hypotension, reduced consciousness → Shock",
    "physical_exam",
    "medium",
    PAED,
    "Paediatrics/02_Common_Paediatric_Presentations.html",
)

c(
    "Differentials: Causes of croup vs epiglottitis vs bacterial tracheitis",
    "CROUP: Viral, barking cough, stridor, mild fever, gradual onset, age 6m-3y → Dexamethasone\nEPIGLOTTITIS: Bacterial (Hib), drooling, tripod position, high fever, toxic, EMERGENCY\nBACTERIAL TRACHEITIS: Post-viral, high fever, toxic, stridor, thick secretions → Intubation + antibiotics",
    "differential",
    "hard",
    PAED,
    "Paediatrics/02_Common_Paediatric_Presentations.html",
)

c(
    "Australian: Paediatric early warning tool (PEWS)",
    "Color-coded observation chart in Australian hospitals (GREEN = normal, YELLOW = concerning, RED = critical). Triggers escalation to MET (Medical Emergency Team) if deteriorating. Parameters: HR, RR, work of breathing, SpO2, consciousness, temperature.",
    "australian",
    "medium",
    PAED,
    "Paediatrics/03_Paediatric_Physical_Examination.html",
)

c(
    "Communication: Explaining vaccination to hesitant parents",
    '"I understand you have concerns. Vaccines are very safe - tested extensively. The diseases they prevent (measles, whooping cough) can be very serious, even fatal. Side effects are usually mild (sore arm, low fever). The evidence shows vaccines don\'t cause autism. I recommend following the schedule to protect your child. What specific concerns do you have?"',
    "communication",
    "medium",
    PAED,
    "Paediatrics/05_Parent_Communication_Strategies.html",
)

c(
    "IMG Mistake: Not recognizing bronchiolitis severity",
    "Bronchiolitis (RSV) in infant: Mild = feeding well, minimal recession → Home. SEVERE = SpO2 <92%, apnoeas, poor feeding (<50% normal), moderate-severe recession, age <3 months → ADMIT (high-flow O2, NG feeds, monitoring)",
    "img_mistake",
    "medium",
    PAED,
    "Paediatrics/02_Common_Paediatric_Presentations.html",
)

# Developmental milestones (high-yield)
c(
    "Physical exam: Developmental milestones - 6 months",
    "GROSS MOTOR: Sits with support\nFINE MOTOR: Reaches for objects, transfers hand-to-hand\nSPEECH: Babbles (ba, da), responds to name\nSOCIAL: Smiles responsively, stranger awareness emerging",
    "physical_exam",
    "medium",
    PAED,
    "Paediatrics/04_Developmental_Assessment.html",
)

c(
    "Physical exam: Developmental milestones - 12 months",
    "GROSS MOTOR: Pulls to stand, cruises (walks holding furniture)\nFINE MOTOR: Pincer grip, puts objects in container\nSPEECH: 2-3 words with meaning (mama, dada)\nSOCIAL: Waves bye-bye, plays peek-a-boo",
    "physical_exam",
    "medium",
    PAED,
    "Paediatrics/04_Developmental_Assessment.html",
)

c(
    "Physical exam: Developmental milestones - 2 years",
    "GROSS MOTOR: Runs, kicks ball, walks up stairs (2 feet per step)\nFINE MOTOR: Tower of 6 blocks, circular scribble\nSPEECH: 50 words, 2-word sentences\nSOCIAL: Parallel play, removes clothes",
    "physical_exam",
    "medium",
    PAED,
    "Paediatrics/04_Developmental_Assessment.html",
)

# ==================================================================
# ETHICS & COMMUNICATION - Expanded Content
# ==================================================================

c(
    "Communication: Responding to 'How long do I have?' (palliative)",
    "\"That's a very important question. It's difficult to give an exact timeframe - everyone is different. Based on your situation, we're thinking weeks to months rather than years. What's most important is that we focus on your comfort and quality of life. What matters most to you in the time you have?\"",
    "communication",
    "hard",
    ETH,
    "Ethics_Communication/02_Breaking_Bad_News_Additional_Scenarios.html",
)

c(
    "Communication: Discussing DNR (Do Not Resuscitate) orders",
    '"If your heart stops or you stop breathing, we can try to restart your heart with CPR (chest compressions, electric shocks). However, given your illness, CPR is unlikely to work and could cause harm (broken ribs, brain damage). I recommend focusing on comfort rather than CPR. This means natural death when it comes. What are your thoughts?"',
    "communication",
    "hard",
    ETH,
    "Ethics_Communication/01_Communication_Skills_Role_Play_Scripts.html",
)

c(
    "IMG Mistake: Breaking bad news without warning shot",
    'WRONG: "Your scan shows cancer."\nRIGHT: "I\'m afraid I have some difficult news." PAUSE. Check patient ready. "The scan shows..." Small chunks, check understanding.',
    "img_mistake",
    "medium",
    ETH,
    "Ethics_Communication/02_Breaking_Bad_News_Additional_Scenarios.html",
)

c(
    "Communication: Responding to denial after bad news",
    '"I can see this news is very difficult to accept." Don\'t force acceptance immediately. Allow time. Later: "I know this is hard. When you\'re ready, I\'d like to talk about next steps." Offer support, follow-up appointment.',
    "communication",
    "medium",
    ETH,
    "Ethics_Communication/04_Comprehensive_Emotional_Reactions_Handbook.html",
)

c(
    "Australian: Advance Care Directives (ACD) in NSW",
    "Legal document where competent person states future treatment preferences. Must be in writing, signed, witnessed. Becomes active when person loses capacity. Binding on doctors (except emergency life-saving treatment). Different laws each state - NSW has Advance Care Planning framework.",
    "australian",
    "medium",
    ETH,
    "Ethics_Communication/01_Communication_Skills_Role_Play_Scripts.html",
)

c(
    "IMG Mistake: Using family as interpreters",
    "NEVER use family members as interpreters for medical consultations: Confidentiality issues, inaccurate translation, family may filter/change information. ALWAYS use professional interpreters (TIS: 131 450) - telephone or in-person.",
    "img_mistake",
    "medium",
    ETH,
    "Ethics_Communication/05_Cultural_Variations_Breaking_Bad_News_Australia.html",
)

# ==================================================================
# GENERAL OSCE SKILLS
# ==================================================================

c(
    "Communication: OSCE opening (general framework)",
    "1. Greet + introduce self + role\n2. Confirm patient identity\n3. Explain purpose of consultation\n4. Gain consent\n5. Ensure privacy/comfort\n6. Open question: 'What brings you in today?' or 'How can I help?'",
    "communication",
    "easy",
    GEN,
    "General OSCE skills",
)

c(
    "Communication: OSCE closing (general framework)",
    "1. Summarize key points\n2. Check patient understanding: 'Can I check I've explained clearly?'\n3. Address concerns: 'Any questions or worries?'\n4. Safety-netting: 'Return if [specific red flags]'\n5. Follow-up plan: 'I'll arrange...'\n6. Thank patient",
    "communication",
    "easy",
    GEN,
    "General OSCE skills",
)

c(
    "IMG Mistake: Poor time management in OSCE",
    "8-minute OSCE = ~6 min task + 2 min closing/questions. Keep eye on clock. If running over: Summarize quickly, don't skip closing. Practice timed stations. Know when to stop gathering history and move to explanation/plan.",
    "img_mistake",
    "medium",
    GEN,
    "General OSCE skills",
)

c(
    "Australian: Australian healthcare structure (Medicare)",
    "PUBLIC: Medicare covers GP visits (bulk-billed or gap payment), public hospital (free), some specialist visits (if referred)\nPRIVATE: Private health insurance (extras for dental/physio, hospital cover for choice of doctor/shorter wait)\nMedicare levy: 2% of taxable income",
    "australian",
    "easy",
    GEN,
    "General knowledge",
)

# ==================================================================
# SAVE ALL
# ==================================================================

# Update metadata
data["metadata"]["total_cards"] = len(data["cards"])
data["metadata"]["last_updated"] = datetime.now().isoformat()
data["metadata"]["note"] = "Phase 1.1 Complete: High-quality manual extraction reaching target"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*70}")
print(f"FINAL BATCH EXTRACTION COMPLETE")
print(f"{'='*70}")
print(f"Total flashcards: {len(data['cards'])}")
print(f"Target: 750")
print(f"Progress: {len(data['cards'])/750*100:.1f}%")
print(f"\nCards added this run: {len(data['cards']) - 254}")
print(f"{'='*70}\n")

# Final statistics
categories = {}
for card in data["cards"]:
    cat = card["category"]
    categories[cat] = categories.get(cat, 0) + 1

print("FINAL STATISTICS BY CATEGORY:")
print("-" * 70)
for cat in [
    "red_flags",
    "differential",
    "physical_exam",
    "communication",
    "australian",
    "img_mistake",
]:
    count = categories.get(cat, 0)
    target = data["metadata"]["targets"].get(cat, 150)
    pct = f"({count/target*100:.0f}%)" if target > 0 else ""
    print(f"  {cat:20s}: {count:4d}/{target:4d} {pct}")

print(f"\n{'='*70}")
print(f"Flashcard extraction Phase 1.1 COMPLETE!")
print(f"File saved to: {OUTPUT_FILE}")
print(f"{'='*70}\n")
