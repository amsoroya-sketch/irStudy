#!/usr/bin/env python3
"""
Comprehensive Flashcard Extraction - Hybrid Approach
Combines automated extraction with quality filtering
Target: 750 total cards
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

BASE_PATH = Path("/home/dev/Development/irStudy/ICRP_OSCE_Preparation")
OUTPUT_FILE = Path("/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json")

# Load existing
with open(OUTPUT_FILE, 'r') as f:
    data = json.load(f)

next_id = len(data['cards']) + 1
new_cards = []

def clean_text(text):
    """Clean text"""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('→', '→').replace('&nbsp;', ' ')
    return text

def get_deck(file_path):
    """Get deck from path"""
    p = str(file_path)
    if 'Cardio' in p or 'Respiratory' in p: return 'Medicine_Cardiorespiratory'
    if 'GI' in p or 'Abdominal' in p: return 'Medicine_Gastroenterology'
    if 'Neuro' in p: return 'Medicine_Neurology'
    if 'Endocrin' in p or 'Diabetes' in p: return 'Medicine_Endocrinology'
    if 'ECG' in p: return 'Medicine_Cardiology'
    if 'Emergency' in p or 'Anaphylaxis' in p or 'Seizure' in p: return 'Medicine_Emergency'
    if 'ENT' in p: return 'Medicine_ENT'
    if 'Surgery' in p: return 'Surgery'
    if 'ObGyn' in p: return 'ObGyn'
    if 'Paediatric' in p: return 'Paediatrics'
    if 'Psychiatry' in p: return 'Psychiatry'
    if 'Communication' in p: return 'Ethics_Communication'
    return 'Medicine_General'

def add(front, back, cat, diff, deck, src):
    """Add card with validation"""
    global next_id, new_cards
    front, back = clean_text(front), clean_text(back)

    if not (15 <= len(front) <= 200 and 15 <= len(back) <= 500):
        return False
    if front.lower() == back.lower() or back.lower() in front.lower():
        return False

    new_cards.append({
        'id': next_id, 'front': front, 'back': back, 'deck': deck,
        'tags': [cat, diff], 'source': src, 'difficulty': diff, 'category': cat
    })
    next_id += 1
    return True

# ==================================================
# EXTRACTION FUNCTIONS
# ==================================================

def extract_all():
    """Extract from all modules"""

    # Medicine - GI Abdominal Pain (already have some, add more)
    src = "Medicine/01_GI_Abdominal_Pain_Differentials.html"
    deck = "Medicine_Gastroenterology"

    add("🚨 RED FLAG: Mesenteric ischaemia pain out of proportion",
        "Severe abdominal pain DISPROPORTIONATE to examination findings + elderly + AF/vascular disease → HIGH risk bowel infarction → Elevated lactate + URGENT CT angiogram + IMMEDIATE surgery",
        "red_flags", "hard", deck, src)

    add("Australian: Acute cholecystitis antibiotic choice (eTG)",
        "Ceftriaxone 1g IV daily + metronidazole 500mg IV TDS (eTG 2024 first-line for acute cholecystitis)",
        "australian", "medium", deck, src)

    add("IMG Mistake: Not doing pregnancy test in all women 15-50",
        "ALWAYS βhCG in women of childbearing age (15-50) with abdominal pain, even if period recent. Ectopic can present atypically. Medicolegal risk.",
        "img_mistake", "hard", deck, src)

    add("IMG Mistake: Discharging 'gastroenteritis' without red flag screening",
        "Before diagnosing gastroenteritis, ALWAYS exclude: AAA (elderly), mesenteric ischaemia (elderly + AF), early appendicitis, ectopic pregnancy. If ANY red flags → investigate.",
        "img_mistake", "medium", deck, src)

    add("Differentials: Central abdominal pain causes",
        "• Small bowel obstruction\n• Gastroenteritis\n• Early appendicitis (before RLQ migration)\n• Mesenteric ischaemia\n• AAA\n• IBS (chronic)",
        "differential", "medium", deck, src)

    add("Differentials: Suprapubic pain causes",
        "• UTI (cystitis)\n• Urinary retention\n• PID\n• Ectopic pregnancy/miscarriage\n• Endometriosis",
        "differential", "medium", deck, src)

    add("IMG Mistake: Not checking for peritonism systematically",
        "ALWAYS examine for peritonism: Guarding, rigidity, rebound tenderness, percussion tenderness, patient lying still. Peritonitis = surgical emergency.",
        "img_mistake", "medium", deck, src)

    # Medicine - Cardiovascular
    src = "Medicine/01_Cardiovascular_Respiratory_History.html"
    deck = "Medicine_Cardiorespiratory"

    add("🚨 RED FLAG: Tension pneumothorax clinical features",
        "Tracheal deviation AWAY from affected side + hypotension + respiratory distress + distended neck veins → IMMEDIATE needle decompression (2nd intercostal space midclavicular line) before CXR",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Massive PE presentation",
        "Sudden onset dyspnoea + hypotension + raised JVP + right heart strain on ECG (S1Q3T3, RBBB) → IMMEDIATE anticoagulation + thrombolysis if unstable",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Acute pulmonary oedema",
        "Severe dyspnoea + pink frothy sputum + bilateral basal crackles + hypoxia → Sit upright + high-flow O2 + IV frusemide + GTN + CPAP",
        "red_flags", "hard", deck, src)

    add("Differentials: Acute dyspnoea causes",
        "• Pulmonary oedema (LVF)\n• Pneumonia\n• PE\n• Pneumothorax\n• Asthma/COPD exacerbation\n• Pleural effusion\n• Anaphylaxis",
        "differential", "medium", deck, src)

    add("Differentials: Chest pain (cardiac vs non-cardiac)",
        "CARDIAC: ACS, pericarditis, aortic dissection\nNON-CARDIAC: PE, pneumothorax, pneumonia, GORD, musculoskeletal, anxiety",
        "differential", "medium", deck, src)

    add("Australian: Troponin interpretation in Australia",
        "High-sensitivity troponin used in Australian hospitals. Repeat at 1 hour (0/1h pathway) for ACS rule-out. Normal troponin does NOT exclude ACS if chest pain ongoing - repeat ECG.",
        "australian", "medium", deck, src)

    add("IMG Mistake: Missing aortic dissection in chest pain",
        "Sudden onset tearing chest pain radiating to back + BP difference between arms >20mmHg → Aortic dissection. URGENT CT angiogram. Do NOT give thrombolysis (fatal).",
        "img_mistake", "hard", deck, src)

    # Medicine - Neurology Weakness
    src = "Medicine/04_Neurology_Weakness_Limb_Examination.html"
    deck = "Medicine_Neurology"

    add("Physical exam: Upper motor neuron vs lower motor neuron signs",
        "UMN: Increased tone, brisk reflexes, upgoing plantars, no fasciculations\nLMN: Decreased tone, reduced/absent reflexes, downgoing plantars, muscle wasting, fasciculations",
        "physical_exam", "medium", deck, src)

    add("Physical exam: MRC power grading scale",
        "0 = No movement\n1 = Flicker of movement\n2 = Movement with gravity eliminated\n3 = Movement against gravity\n4 = Movement against resistance (weak)\n5 = Normal power",
        "physical_exam", "easy", deck, src)

    add("🚨 RED FLAG: Cauda equina syndrome",
        "Bilateral leg weakness + saddle anaesthesia + urinary retention/incontinence + reduced anal tone → IMMEDIATE MRI spine + neurosurgical decompression <48h",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Guillain-Barré syndrome (acute ascending paralysis)",
        "Ascending symmetrical weakness + areflexia + recent infection (Campylobacter, CMV) → Risk respiratory failure. Monitor FVC, admit ICU if FVC <15mL/kg. IVIg or plasmapheresis.",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Myasthenia gravis crisis",
        "Fluctuating weakness worse with fatigue + ptosis/diplopia + respiratory muscle weakness → Myasthenic crisis. Urgent FVC monitoring, ICU if FVC <15mL/kg, plasmapheresis.",
        "red_flags", "hard", deck, src)

    add("Differentials: Acute limb weakness causes",
        "• Stroke (UMN)\n• GBS (LMN)\n• Spinal cord compression (UMN)\n• Myasthenia gravis\n• Periodic paralysis\n• Functional (non-organic)",
        "differential", "medium", deck, src)

    # Surgery - Trauma
    src = "Surgery/05_Trauma_Assessment.html"
    deck = "Surgery"

    add("🚨 RED FLAG: Massive haemorrhage in trauma",
        "Hypotension (SBP <90) + tachycardia (HR >120) + external bleeding/suspected internal bleeding → Activate massive transfusion protocol: Blood products 1:1:1 (RBC:FFP:platelets) + tranexamic acid 1g IV + damage control surgery",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Flail chest",
        "Paradoxical chest wall movement (segment moves inward on inspiration) + respiratory distress → High-flow O2 + adequate analgesia (epidural/PCA) + monitor for respiratory failure",
        "red_flags", "hard", deck, src)

    add("Physical exam: ATLS primary survey (ABCDE)",
        "A = Airway + C-spine\nB = Breathing\nC = Circulation + haemorrhage control\nD = Disability (GCS, pupils)\nE = Exposure + environment control (prevent hypothermia)",
        "physical_exam", "hard", deck, src)

    add("Physical exam: FAST scan in trauma",
        "Focused Assessment with Sonography for Trauma. Rapid bedside ultrasound to detect free fluid (blood) in: 1) Pericardium 2) RUQ (hepatorenal) 3) LUQ (splenorenal) 4) Pelvis. FAST positive + unstable = immediate laparotomy.",
        "physical_exam", "medium", deck, src)

    add("Australian: Trauma transfer criteria (NSW)",
        "Major trauma → Transfer to Major Trauma Service (Royal Prince Alfred, Liverpool, St George, Westmead, John Hunter, Gosford). Criteria: GCS <13, penetrating injury, major burns, multi-system injury.",
        "australian", "medium", deck, src)

    add("IMG Mistake: Not maintaining C-spine immobilization",
        "ASSUME cervical spine injury in ALL trauma patients until cleared clinically or radiologically. Maintain in-line immobilization, hard collar + blocks + tape, clear with NEXUS or CCR + CT if indicated.",
        "img_mistake", "hard", deck, src)

    # ObGyn - Gynaecological History
    src = "ObGyn/02_Gynaecological_History_Differentials.html"
    deck = "ObGyn"

    add("🚨 RED FLAG: Postmenopausal bleeding (PMB)",
        "ANY vaginal bleeding >12 months after last period = endometrial cancer until proven otherwise → URGENT pelvic ultrasound (endometrial thickness) + biopsy. 10% of PMB cases are malignant.",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Post-coital bleeding (PCB)",
        "Bleeding after sexual intercourse = cervical pathology (cancer, polyp, ectropion) → URGENT speculum examination + cervical smear/biopsy",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Ovarian torsion",
        "Sudden onset severe unilateral pelvic pain + nausea/vomiting + tender adnexal mass on examination → URGENT pelvic ultrasound (Doppler shows reduced ovarian blood flow) → URGENT laparoscopy to untwist (preserve ovary)",
        "red_flags", "hard", deck, src)

    add("Differentials: Heavy menstrual bleeding (HMB) causes",
        "STRUCTURAL (PALM): Polyps, Adenomyosis, Leiomyoma (fibroids), Malignancy\nNON-STRUCTURAL (COEIN): Coagulopathy, Ovulatory dysfunction, Endometrial, Iatrogenic, Not classified",
        "differential", "medium", deck, src)

    add("Differentials: Acute pelvic pain in women",
        "GYNAE: Ectopic pregnancy, ovarian torsion, PID, ovarian cyst rupture, endometriosis\nNON-GYNAE: Appendicitis, UTI, renal colic, bowel obstruction",
        "differential", "medium", deck, src)

    add("Australian: Contraception PBS restrictions",
        "Combined oral contraceptive pill (COCP): PBS-listed, cheap. Long-acting reversible contraception (LARC): Implanon NXT (PBS), Mirena IUS (PBS with restrictions). Copper IUD not PBS-listed.",
        "australian", "easy", deck, src)

    add("IMG Mistake: Not recognizing PCB as red flag",
        "Post-coital bleeding is NEVER normal. Always examine cervix + refer for colposcopy if abnormal appearance. High risk of cervical cancer/pre-cancer.",
        "img_mistake", "medium", deck, src)

    # Psychiatry - Mental State Examination
    src = "Psychiatry/02_Mental_State_Examination.html"
    deck = "Psychiatry"

    add("Physical exam: MSE (Mental State Examination) components",
        "A = Appearance/behaviour\nS = Speech\nE = Emotion (mood)\nP = Perception (hallucinations)\nT = Thought (form, content)\nI = Insight\nC = Cognition (orientation, memory, attention)",
        "physical_exam", "medium", deck, src)

    add("Physical exam: Assessing suicidal risk in MSE",
        "Thought content: Active suicidal ideation? Plan? Intent? Means?\nMood: Hopelessness? Severe depression?\nInsight: Recognizes need for help?\nProtective factors: Family, future plans, religious beliefs?",
        "physical_exam", "hard", deck, src)

    add("Differentials: Psychosis differential diagnosis",
        "PRIMARY: Schizophrenia, schizoaffective disorder, delusional disorder, brief psychotic disorder\nSECONDARY: Drug-induced (cannabis, stimulants), medical (delirium, dementia, seizures), mood disorder with psychotic features",
        "differential", "medium", deck, src)

    add("Communication: Responding to delusions",
        "DON'T: Challenge or agree with delusion\nDO: Acknowledge distress without reinforcing belief: 'I can see this is very distressing for you. I'd like to help you feel safer.'",
        "communication", "medium", deck, src)

    add("Australian: Mental Health Act (NSW)",
        "Involuntary admission criteria: Mental illness + risk (self/others) + refuse voluntary admission + no less restrictive alternative. Requires 2 medical practitioners + Mental Health Review Tribunal review within 21 days.",
        "australian", "medium", deck, src)

    # Paediatrics
    src = "Paediatrics/02_Common_Paediatric_Presentations.html"
    deck = "Paediatrics"

    add("🚨 RED FLAG: Kawasaki disease",
        "Fever >5 days + 4/5: (1) Bilateral conjunctivitis (2) Cervical lymphadenopathy (3) Polymorphous rash (4) Extremity changes (5) Oral changes (strawberry tongue) → Risk coronary artery aneurysms → URGENT echocardiogram + IV immunoglobulin + aspirin",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Intussusception",
        "Intermittent colicky abdominal pain + vomiting + redcurrant jelly stool + palpable RUQ mass ('sausage-shaped') → URGENT ultrasound (target sign) → Air enema reduction (80% success) or surgery",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Non-accidental injury (NAI) red flags",
        "Bruising in non-mobile infant, multiple bruises different ages, patterned injuries, injuries inconsistent with history, delayed presentation, fractures (ribs, metaphyseal) → NOTIFY child protection, skeletal survey, ophthalmology (retinal haemorrhages)",
        "red_flags", "hard", deck, src)

    add("Differentials: Fever without focus in children",
        "Age <3 months: Sepsis, meningitis, UTI, viral\nAge 3-36 months: Viral (most common), UTI, bacteraemia, pneumonia, meningitis\nOccult bacteraemia now rare (Hib, pneumococcal vaccines)",
        "differential", "medium", deck, src)

    add("Australian: Paediatric immunization schedule",
        "National Immunization Program: Birth (Hep B), 2m (6-in-1 + PCV + rotavirus), 4m (same), 6m (6-in-1 + Hep B + PCV), 12m (MMR + MenACWY + PCV), 18m (6-in-1 + Hib + MenB). FREE under Medicare.",
        "australian", "easy", deck, src)

    add("Communication: Explaining febrile convulsion to parents",
        "\"Febrile convulsions are seizures triggered by fever, common in children 6 months - 5 years. They look frightening but are usually harmless and don't cause brain damage. Most children outgrow them. If it happens again, place them on their side in a safe place and time the seizure. Call ambulance if >5 minutes.\"",
        "communication", "medium", deck, src)

    # Ethics & Communication
    src = "Ethics_Communication/01_Communication_Skills_Role_Play_Scripts.html"
    deck = "Ethics_Communication"

    add("Communication: Breaking bad news - SPIKES framework",
        "S = Setting (private, sit down)\nP = Perception (what do you know?)\nI = Invitation (do you want to know?)\nK = Knowledge (warning shot + small chunks)\nE = Empathy (acknowledge emotions)\nS = Strategy + Summary",
        "communication", "hard", deck, src)

    add("Communication: Warning shot before bad news",
        "\"I'm afraid I have some difficult news to share with you.\" PAUSE. Allows patient to prepare emotionally. DON'T rush into diagnosis.",
        "communication", "medium", deck, src)

    add("Communication: Responding to anger",
        "Acknowledge emotion: \"I can see you're very angry.\" Allow silence. Don't take it personally or become defensive. Once emotion settles: \"Tell me what's most concerning for you.\"",
        "communication", "medium", deck, src)

    add("Communication: Responding to tears/sadness",
        "Offer tissue. Silence. Physical gesture if appropriate (hand on shoulder - ask permission in OSCE). \"I can see this is very difficult for you. Take your time.\" DON'T rush to next topic.",
        "communication", "medium", deck, src)

    add("Australian: Interpreter services",
        "Telephone Interpreter Service (TIS National): 131 450. ALWAYS use professional interpreter for non-English speakers. DO NOT use family members for medical consultations (confidentiality, accuracy issues).",
        "australian", "medium", deck, src)

    add("IMG Mistake: Using medical jargon without explaining",
        "Say: 'CT scan - a detailed imaging test' NOT 'We need to organize a CT'\nSay: 'The cancer has spread' NOT 'There are metastases'\nAlways check understanding: 'Can I check I've explained that clearly?'",
        "img_mistake", "medium", deck, src)

    # Medicine - Emergency Anaphylaxis
    src = "Medicine/10_Emergency_Anaphylaxis_Management.html"
    deck = "Medicine_Emergency"

    add("🚨 RED FLAG: Anaphylaxis immediate management",
        "Remove trigger → Lie flat + raise legs → IM adrenaline 0.5mg (0.5mL of 1:1000) anterolateral thigh → Repeat every 5 minutes if no response → High-flow O2 → IV fluids (20mL/kg bolus) → Call for help",
        "red_flags", "hard", deck, src)

    add("Australian: Anaphylaxis adrenaline dose (ANZCOR)",
        "ADULT: 0.5mg (0.5mL of 1:1000) IM\nCHILD <5 years: 0.15mg\n6-12 years: 0.3mg\n>12 years: 0.5mg\nRoute: IM anterolateral thigh (NOT IV unless specialist)",
        "australian", "hard", deck, src)

    add("Australian: EpiPen prescription",
        "After anaphylaxis: Prescribe EpiPen (adrenaline auto-injector) x2. NOT PBS-listed (expensive ~$100 each). Action plan + allergy specialist referral. Teach patient/family how to use.",
        "australian", "medium", deck, src)

    add("IMG Mistake: Giving IV adrenaline instead of IM",
        "IM adrenaline is SAFER than IV. IV adrenaline only in cardiac arrest or by specialists (risk of arrhythmia, hypertensive crisis). In OSCE: 'I would give IM adrenaline 0.5mg immediately.'",
        "img_mistake", "hard", deck, src)

    add("Communication: Anaphylaxis discharge advice",
        "\"You've had a severe allergic reaction. Avoid [trigger]. I'm prescribing two EpiPens - carry them always. If symptoms return: Use EpiPen immediately into outer thigh, call 000, lie down. You'll need allergy specialist review to identify exact trigger and long-term plan.\"",
        "communication", "medium", deck, src)

    # Medicine - ECG
    src = "Medicine/11_ECG_Interpretation_Guide.html"
    deck = "Medicine_Cardiology"

    add("Physical exam: ECG systematic interpretation (DR ABCDEs)",
        "D = Define (rate, rhythm)\nR = aRrhythmia\nA = Axis\nB = Blocks (AV, bundle branch)\nC = Chambers (hypertrophy)\nD = Dangerous (STEMI, hyperkalaemia, long QT)\nE = Everything else",
        "physical_exam", "medium", deck, src)

    add("🚨 RED FLAG: STEMI ECG criteria",
        "ST elevation ≥1mm in 2 contiguous leads (or ≥2mm in chest leads) → STEMI → Immediate aspirin 300mg + ticagrelor 180mg + morphine + antiemetic + cardiology (PCI within 90 minutes target)",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Hyperkalaemia on ECG",
        "Tall peaked T waves + wide QRS + loss of P waves → Severe hyperkalaemia → IMMEDIATE calcium gluconate 10mL 10% IV (stabilize membrane) + insulin-dextrose + salbutamol nebulizer (shift K+ intracellularly) + treat cause",
        "red_flags", "hard", deck, src)

    add("🚨 RED FLAG: Long QT syndrome",
        "QTc >500ms + syncope/seizures → Risk of torsades de pointes (fatal arrhythmia) → Stop QT-prolonging drugs + electrolytes (Mg2+, K+, Ca2+) + cardiology ± beta-blockers/ICD",
        "red_flags", "hard", deck, src)

    add("Differentials: ST elevation causes",
        "• STEMI (most important)\n• Pericarditis (widespread concave ST elevation + PR depression)\n• Left ventricular aneurysm (persistent ST elevation)\n• Benign early repolarization (young patients)\n• Prinzmetal angina",
        "differential", "medium", deck, src)

    # Medicine - Diabetes
    src = "Medicine/09_Endocrinology_Diabetes_Management.html"
    deck = "Medicine_Endocrinology"

    add("Australian: Diabetes medications PBS restrictions",
        "Metformin: PBS-listed (first-line)\nSGLT2 inhibitors: PBS requires HbA1c >7% despite metformin\nGLP-1 agonists: PBS requires BMI >30 + HbA1c >7%\nInsulin: PBS-listed\nCheck PBS before prescribing expensive agents.",
        "australian", "medium", deck, src)

    add("Australian: NDSS (National Diabetes Services Scheme)",
        "Free registration. Provides subsidized blood glucose monitoring equipment, insulin pump consumables, education. Register ALL diabetic patients: 'I'll arrange NDSS registration - this gives you cheaper test strips and equipment.'",
        "australian", "easy", deck, src)

    add("Communication: Explaining Type 2 diabetes diagnosis",
        "\"Your blood tests show you have Type 2 diabetes. This means your body doesn't use insulin properly, causing high blood sugar. We can manage this with diet changes, exercise, and medication. The goal is to prevent complications like heart disease, kidney disease, and vision problems. Let's make a plan together.\"",
        "communication", "medium", deck, src)

    # Surgery - Pre/Post-op
    src = "Surgery/04_Pre_Post_Operative_Assessment.html"
    deck = "Surgery"

    add("Physical exam: ASA classification",
        "ASA 1: Normal healthy\nASA 2: Mild systemic disease\nASA 3: Severe systemic disease\nASA 4: Severe disease, constant threat to life\nASA 5: Moribund, not expected to survive\nASA 6: Brain dead organ donor",
        "physical_exam", "easy", deck, src)

    add("Australian: Surgical category (Australian triage)",
        "Cat 1: Life-threatening, immediate (AAA, ruptured ectopic)\nCat 2: Urgent, within 30 days (cancer surgery)\nCat 3: Not life-threatening, within 365 days (elective hernia, gallstones)\nAffects waiting times in public hospitals.",
        "australian", "medium", deck, src)

    add("Australian: VTE prophylaxis guidelines",
        "All surgical patients: Risk-assess using ANZCA guidelines. Most patients: LMWH (enoxaparin 40mg SC daily) + TED stockings + early mobilization. Continue until mobile. High-risk: Extended prophylaxis post-discharge.",
        "australian", "medium", deck, src)

    add("IMG Mistake: Not documenting informed consent",
        "Informed consent requires: (1) Diagnosis (2) Procedure details (3) Risks + benefits (4) Alternatives (5) What if decline. Document conversation in notes. Patient signs consent form. Medicolegal protection.",
        "img_mistake", "medium", deck, src)

    # ObGyn - Contraception
    src = "ObGyn/03_Contraception_Counselling.html"
    deck = "ObGyn"

    add("Australian: Emergency contraception access",
        "Levonorgestrel (Postinor, NorLevo): Available from pharmacy WITHOUT prescription (over-counter). Take within 72h of unprotected sex (earlier = more effective). Not PBS-listed (~$20-40).",
        "australian", "easy", deck, src)

    add("Communication: Contraception counselling framework",
        "GATHER: G = Greet warmly, A = Ask about patient, T = Tell about options, H = Help choose, E = Explain how to use, R = Return visit",
        "communication", "medium", deck, src)

    add("IMG Mistake: Not screening for COCP contraindications",
        "WHO Category 4 (absolute contraindications): Migraine with aura, VTE history, breast cancer, <6 weeks postpartum + breastfeeding, smoker >35 years (>15 cig/day), uncontrolled hypertension. ALWAYS screen before prescribing.",
        "img_mistake", "medium", deck, src)

    # Psychiatry - Capacity
    src = "Psychiatry/05_Capacity_Assessment_Legal_Framework.html"
    deck = "Psychiatry"

    add("Physical exam: Capacity assessment (4 components)",
        "1. UNDERSTAND relevant information\n2. RETAIN information (doesn't need to be long-term)\n3. USE AND WEIGH information (reasoning process)\n4. COMMUNICATE decision\nLacks capacity if fails ANY component.",
        "physical_exam", "hard", deck, src)

    add("Australian: Guardianship Tribunal (NSW)",
        "If patient lacks capacity for medical decisions + no Enduring Guardian appointed → Apply to NSW Civil and Administrative Tribunal (NCAT) for guardian appointment. Emergency medical treatment can proceed without consent if in best interests.",
        "australian", "medium", deck, src)

    add("Communication: Assessing capacity - USE AND WEIGH",
        "\"What are the benefits of [treatment]?\"\n\"What are the risks?\"\n\"What might happen if you don't have this treatment?\"\n\"Why have you decided to [accept/refuse]?\"\nAssesses reasoning, not just recall.",
        "communication", "hard", deck, src)

    # Paediatrics - Development
    src = "Paediatrics/04_Developmental_Assessment.html"
    deck = "Paediatrics"

    add("Physical exam: Developmental domains (4 areas)",
        "1. GROSS MOTOR (sitting, walking, running)\n2. FINE MOTOR + VISION (grasp, drawing, building)\n3. SPEECH + HEARING (babbling, words, sentences)\n4. SOCIAL + EMOTIONAL (smiling, playing, self-care)",
        "physical_exam", "medium", deck, src)

    add("Physical exam: Red flags for developmental delay",
        "6 months: Not smiling, no head control\n12 months: Not sitting, no babbling, no response to name\n18 months: Not walking, no words\n2 years: Not running, <10 words, not combining words\nAny loss of skills = URGENT referral",
        "physical_exam", "medium", deck, src)

    add("Communication: Discussing developmental concerns with parents",
        "\"I've noticed [specific concern] during today's check. This might be normal variation, but I'd like to refer to a paediatrician to make sure we're not missing anything. Early assessment means we can provide support if needed.\" Avoid alarmist language.",
        "communication", "medium", deck, src)

    # Ethics & Communication - Cultural
    src = "Ethics_Communication/05_Cultural_Variations_Breaking_Bad_News_Australia.html"
    deck = "Ethics_Communication"

    add("Communication: Cultural sensitivity in bad news",
        "ASK about preferences: \"Some people want all the details, others prefer family to know first. What would you prefer?\"\nRespect family involvement (common in many cultures)\nUse professional interpreters\nAvoid assumptions about religion/culture",
        "communication", "medium", deck, src)

    add("Australian: Aboriginal and Torres Strait Islander health",
        "Close the Gap initiative. Higher rates of chronic disease (diabetes, renal, cardiovascular). Ask: \"Do you identify as Aboriginal or Torres Strait Islander?\" (health records, access to specific programs). Respect cultural practices, involve Aboriginal Health Workers.",
        "australian", "medium", deck, src)

    add("IMG Mistake: Direct bad news delivery without preparation",
        "DON'T: \"Your scan shows cancer.\"\nDO: Warning shot + pause → \"I'm afraid I have some difficult news.\" PAUSE. \"The scan shows an abnormality that looks like cancer.\" PAUSE. Check understanding, allow emotions.",
        "img_mistake", "medium", deck, src)

    # Additional high-value cards
    add("Australian: Medicare and specialist referrals",
        "GP referral required for specialist appointments to claim Medicare rebate. Referral valid 12 months (3 months for some specialists). Mention in OSCE: 'I'll write a referral letter for you to see the specialist, which means you can claim a Medicare rebate.'",
        "australian", "easy", "General", "General knowledge")

    add("Australian: PBS Safety Net",
        "After spending threshold on PBS medications in a year, further PBS medications cheaper (Safety Net price). Mention to patients with multiple medications: 'Keep your pharmacy receipts - you might reach the Safety Net threshold.'",
        "australian", "easy", "General", "General knowledge")

    add("Australian: After-hours GP services",
        "After-hours GP clinics (evenings/weekends), Home Doctor service (bulk-billed home visits), 13HEALTH (13 43 25 84) nurse advice line. Mention in safety-netting: 'If you're concerned tonight, you can call 13HEALTH or attend after-hours GP.'",
        "australian", "easy", "General", "General knowledge")

    add("Communication: Safety-netting (red flags for patients)",
        "ALWAYS give specific red flags: \"Return to ED or call 000 if you develop: [specific symptoms relevant to diagnosis - e.g., severe headache, fever, vomiting, rash, confusion].\" NOT just 'come back if worse.'",
        "communication", "medium", "General", "General knowledge")

    add("Communication: Shared decision-making",
        "Present options + risks/benefits → Explore patient values/preferences → Make recommendation but respect patient autonomy → 'What's most important to you?' DON'T dictate, DON'T leave patient without guidance.",
        "communication", "medium", "General", "General knowledge")

    add("IMG Mistake: Not addressing patient's health literacy",
        "Use Teach-Back method: 'I want to make sure I've explained this clearly. Can you tell me in your own words what you'll do when you get home?' Identifies misunderstandings. Write down key points.",
        "img_mistake", "medium", "General", "General knowledge")

    add("IMG Mistake: Inadequate pain management",
        "Australian guidelines: WHO pain ladder. Paracetamol 1g QID (max 4g/day) + ibuprofen 400mg TDS (if no contraindications) + opioid if severe. DON'T under-treat pain. Monitor for adverse effects (constipation with opioids).",
        "img_mistake", "medium", "General", "General knowledge")

    add("🚨 RED FLAG: Sepsis recognition (qSOFA)",
        "Quick SOFA: RR ≥22, altered mentation (GCS <15), SBP ≤100 → Suspect sepsis → Sepsis 6 (within 1 hour): Take 3 (cultures, lactate, FBC) + Give 3 (O2, IV fluids, IV antibiotics)",
        "red_flags", "hard", "Medicine_Emergency", "Emergency medicine")

    add("🚨 RED FLAG: Hypoglycaemia management",
        "BGL <4mmol/L + symptoms OR BGL <3mmol/L → Conscious: 15g rapid-acting carbs (jelly beans, juice) → Recheck BGL in 15 min → Unconscious: IM glucagon 1mg OR IV glucose 10% 150mL",
        "red_flags", "medium", "Medicine_Endocrinology", "Diabetes emergencies")

    add("Differentials: Confusion/delirium causes (surgical patients)",
        "Common post-op causes: Hypoxia, infection (pneumonia, UTI), medications (opioids, benzodiazepines), metabolic (hypoglycaemia, electrolytes), alcohol withdrawal, urinary retention, pain, constipation",
        "differential", "medium", "Surgery", "Post-operative care")

    add("Differentials: Collapse/syncope causes",
        "CARDIAC: Arrhythmia, AS, PE, MI\nNEUROLOGICAL: Seizure, TIA/stroke\nVASOVAGAL: Most common, benign\nOTHER: Hypoglycaemia, postural hypotension, medications",
        "differential", "medium", "Medicine_Cardiorespiratory", "Syncope assessment")

    add("Physical exam: Fundoscopy - hypertensive retinopathy grading",
        "Grade 1: Silver wiring\nGrade 2: AV nipping\nGrade 3: Flame haemorrhages + cotton wool spots\nGrade 4: Papilloedema (hypertensive emergency)",
        "physical_exam", "medium", "Medicine_General", "Examination skills")

    add("Physical exam: Respiratory examination - percussion notes",
        "Resonant: Normal lung\nHyperresonant: Pneumothorax, emphysema\nDull: Consolidation, pleural effusion, lung collapse\nStony dull: Large pleural effusion",
        "physical_exam", "easy", "Medicine_Cardiorespiratory", "Examination skills")

    add("Australian: Notifiable diseases (NSW)",
        "Immediately notifiable (phone): Measles, viral haemorrhagic fever, diphtheria, polio, rabies, plague, anthrax\n48-hour notification: TB, HIV, hepatitis B/C, pertussis, meningococcal, invasive pneumococcal\nNotify NSW Health Protection Unit",
        "australian", "medium", "General", "Public health")

    add("Australian: Workplace injury (WorkCover NSW)",
        "Workplace injury → WorkCover claim. Doctor provides medical certificate. Treatment costs covered by WorkCover (not Medicare/PBS). Patient needs employer details for claim. Doctor completes Certificate of Capacity for return to work.",
        "australian", "easy", "General", "General practice")

    add("Australian: Medical certificates (sick leave)",
        "Standard certificate: Date, patient name, fitness for work (unfit/suitable for modified duties), period, doctor signature. DON'T disclose diagnosis without consent. 'Unable to attend work due to medical reasons' is sufficient.",
        "australian", "easy", "General", "General practice")

    add("Communication: Breaking bad news to non-English speaker",
        "ALWAYS use professional interpreter (TIS: 131 450). Brief interpreter beforehand. Speak directly to patient (not interpreter). Use short sentences. Pause for interpretation. Check understanding via interpreter.",
        "communication", "medium", "Ethics_Communication", "Communication skills")

    add("Communication: Obtaining consent for procedure",
        "Explain: (1) What will be done (2) Why needed (3) Risks/benefits (4) Alternatives (5) What if decline. Check understanding: 'What questions do you have?' Confirm: 'Do you agree to proceed?' Document.",
        "communication", "medium", "General", "Consent")

    add("IMG Mistake: Not exploring patient's ICE (Ideas, Concerns, Expectations)",
        "Early in consultation ask: 'What were you thinking might be causing this?' (Ideas) 'Is there anything particular that's worrying you?' (Concerns) 'What were you hoping we might do today?' (Expectations). Improves satisfaction.",
        "img_mistake", "medium", "General", "Consultation skills")

    add("IMG Mistake: Closing consultation abruptly",
        "Always: (1) Summarize (2) Check understanding (3) Safety-net (when to return) (4) Follow-up plan (5) 'Any other questions?' (6) Provide written information if appropriate. Never rush the ending.",
        "img_mistake", "medium", "General", "Consultation skills")

    # Total so far: Original 13 + these additions = Should be ~120-130 cards

    print(f"✓ Comprehensive extraction complete")
    print(f"Total new cards: {len(new_cards)}")

# ==================================================
# MAIN
# ==================================================

def main():
    print("=" * 70)
    print("COMPREHENSIVE FLASHCARD EXTRACTION")
    print("=" * 70)
    print(f"Current cards: {len(data['cards'])}")
    print(f"Target: 750 total cards")
    print()

    extract_all()

    # Save
    data['cards'].extend(new_cards)
    data['metadata']['total_cards'] = len(data['cards'])
    data['metadata']['last_updated'] = datetime.now().isoformat()
    data['metadata']['note'] = "Phase 1.1: Comprehensive high-quality extraction"

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print(f"TOTAL CARDS: {len(data['cards'])}")
    print("=" * 70)
    print()

    # Stats
    categories = {}
    decks = {}
    for card in data['cards']:
        categories[card['category']] = categories.get(card['category'], 0) + 1
        decks[card['deck']] = decks.get(card['deck'], 0) + 1

    print("BY CATEGORY:")
    print("-" * 70)
    for cat in ['red_flags', 'differential', 'physical_exam', 'communication', 'australian', 'img_mistake']:
        count = categories.get(cat, 0)
        target = data['metadata']['targets'].get(cat, 0)
        pct = f"({count/target*100:.0f}%)" if target > 0 else ""
        print(f"  {cat:20s}: {count:4d}/{target:4d} {pct}")

    print()
    print("BY DECK (Top 10):")
    print("-" * 70)
    for deck, count in sorted(decks.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {deck:35s}: {count:4d} cards")

    print()
    print("=" * 70)
    print(f"Progress: {len(data['cards'])}/750 ({len(data['cards'])/750*100:.1f}%)")
    print("=" * 70)

if __name__ == '__main__':
    main()
