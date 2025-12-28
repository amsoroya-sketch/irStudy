#!/usr/bin/env python3
"""
Flashcard Extraction Script V2 - Manual High-Quality Extraction
Focuses on extracting high-quality, well-structured flashcards
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# Base path
BASE_PATH = Path("/home/dev/Development/irStudy/ICRP_OSCE_Preparation")
OUTPUT_FILE = Path("/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json")

# Load existing flashcards
with open(OUTPUT_FILE, 'r') as f:
    data = json.load(f)

# Reset to manual cards only (first 13)
data['cards'] = data['cards'][:13]
next_id = 14
new_cards = []

def clean_text(text):
    """Clean and normalize text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove HTML entities
    text = text.replace('→', '→').replace('&nbsp;', ' ')
    # Remove extra markers
    text = re.sub(r'🚨+', '🚨', text)
    return text.strip()

def determine_deck(file_path):
    """Determine deck based on file path"""
    path_str = str(file_path)
    if 'Cardio' in path_str or 'Respiratory' in path_str:
        return 'Medicine_Cardiorespiratory'
    elif 'GI' in path_str or 'Abdominal' in path_str or 'Gastro' in path_str:
        return 'Medicine_Gastroenterology'
    elif 'Neuro' in path_str:
        return 'Medicine_Neurology'
    elif 'Endocrin' in path_str or 'Diabetes' in path_str:
        return 'Medicine_Endocrinology'
    elif 'ECG' in path_str:
        return 'Medicine_Cardiology'
    elif 'Emergency' in path_str or 'Anaphylaxis' in path_str or 'Seizure' in path_str:
        return 'Medicine_Emergency'
    elif 'ENT' in path_str:
        return 'Medicine_ENT'
    elif 'Surgery' in path_str:
        return 'Surgery'
    elif 'ObGyn' in path_str:
        return 'ObGyn'
    elif 'Paediatric' in path_str:
        return 'Paediatrics'
    elif 'Psychiatry' in path_str:
        return 'Psychiatry'
    elif 'Ethics' in path_str or 'Communication' in path_str:
        return 'Ethics_Communication'
    return 'Medicine_General'

def add_card(front, back, category, difficulty, deck, source):
    """Add a card with validation"""
    global next_id, new_cards

    front = clean_text(front)
    back = clean_text(back)

    # Validation
    if len(front) < 10 or len(back) < 10:
        return False
    if len(front) > 200 or len(back) > 500:
        return False
    if front.lower() == back.lower():
        return False

    new_cards.append({
        'id': next_id,
        'front': front,
        'back': back,
        'deck': deck,
        'tags': [category, difficulty],
        'source': source,
        'difficulty': difficulty,
        'category': category
    })
    next_id += 1
    return True

# ============================================================================
# MEDICINE - GI ABDOMINAL PAIN
# ============================================================================

def extract_medicine_gi_abdominal_pain():
    """Extract from Medicine/01_GI_Abdominal_Pain_Differentials.html"""
    file_path = BASE_PATH / "Medicine" / "01_GI_Abdominal_Pain_Differentials.html"
    deck = determine_deck(file_path)
    source = "Medicine/01_GI_Abdominal_Pain_Differentials.html"

    # RED FLAGS - The Deadly Six
    add_card(
        "🚨 RED FLAG: Perforated viscus clinical features",
        "Sudden severe abdominal pain + peritonism (guarding, rigidity, rebound) + air under diaphragm → IMMEDIATE surgery",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Bowel obstruction red flags",
        "Colicky pain → constant + vomiting + absolute constipation (no flatus/feces) + distension + previous surgery → URGENT surgery consult",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Acute pancreatitis severe presentation",
        "Severe epigastric pain radiating to back + vomiting + alcohol/gallstones + tachycardia + hypotension → ICU if severe",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Ascending cholangitis (Charcot's triad)",
        "RUQ pain + fever + jaundice → URGENT resuscitation, antibiotics, ERCP within 24-48h",
        "red_flags", "hard", deck, source
    )

    # DIFFERENTIALS
    add_card(
        "Differentials: RUQ pain differentials",
        "• Biliary colic\n• Acute cholecystitis\n• Ascending cholangitis\n• Hepatitis\n• Pyelonephritis (right)\n• Pneumonia (RLL)\n• Peptic ulcer",
        "differential", "medium", deck, source
    )

    add_card(
        "Differentials: Epigastric pain differentials",
        "• Peptic ulcer disease\n• GORD\n• Acute pancreatitis\n• Perforated ulcer\n• AAA\n• Inferior MI\n• Gastritis",
        "differential", "medium", deck, source
    )

    add_card(
        "Differentials: RLQ pain differentials",
        "• Acute appendicitis\n• Ectopic pregnancy\n• Ovarian torsion\n• PID\n• Renal colic\n• Crohn's disease\n• Cecal pathology",
        "differential", "medium", deck, source
    )

    add_card(
        "Differentials: LLQ pain differentials",
        "• Acute diverticulitis\n• Ectopic pregnancy\n• Ovarian torsion\n• PID\n• Renal colic\n• Ulcerative colitis\n• Colorectal cancer",
        "differential", "medium", deck, source
    )

    # IMG MISTAKES
    add_card(
        "IMG Mistake: Withholding analgesia before surgical review",
        "GIVE adequate analgesia - does NOT mask signs, improves patient comfort and cooperation with examination",
        "img_mistake", "medium", deck, source
    )

    add_card(
        "IMG Mistake: Missing AAA in elderly with abdominal pain",
        "ALWAYS consider AAA in patients >60 with abdominal/back pain. Palpate for pulsatile mass. URGENT CT angiogram if suspected.",
        "img_mistake", "hard", deck, source
    )

    add_card(
        "IMG Mistake: Not recognising mesenteric ischaemia",
        "'Pain out of proportion to examination' = CRITICAL red flag. Elderly + AF + severe abdominal pain → Check lactate, URGENT CT angiogram, IMMEDIATE surgery.",
        "img_mistake", "hard", deck, source
    )

    print(f"✓ {source}: Added cards")

# ============================================================================
# MEDICINE - GI BLEEDING
# ============================================================================

def extract_medicine_gi_bleeding():
    """Extract from Medicine/02_GI_Bleeding_Differentials.html"""
    file_path = BASE_PATH / "Medicine" / "02_GI_Bleeding_Differentials.html"
    deck = determine_deck(file_path)
    source = "Medicine/02_GI_Bleeding_Differentials.html"

    # RED FLAGS
    add_card(
        "🚨 RED FLAG: Upper GI bleeding red flags (urgent endoscopy)",
        "Haematemesis + hypotension (SBP <100) OR tachycardia (HR >100) OR Hb <70 → URGENT endoscopy within 24h",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Variceal bleeding management",
        "Known cirrhosis + haematemesis → Terlipressin + antibiotics (ceftriaxone) + URGENT endoscopy (variceal banding) + octreotide",
        "red_flags", "hard", deck, source
    )

    # DIFFERENTIALS
    add_card(
        "Differentials: Upper GI bleeding causes",
        "• Peptic ulcer (50%)\n• Oesophageal varices (15%)\n• Mallory-Weiss tear\n• Gastritis/erosions\n• Oesophagitis\n• Malignancy",
        "differential", "medium", deck, source
    )

    add_card(
        "Differentials: Lower GI bleeding causes",
        "• Diverticulosis\n• Angiodysplasia\n• Haemorrhoids\n• Anal fissure\n• IBD\n• Colorectal cancer\n• Ischaemic colitis",
        "differential", "medium", deck, source
    )

    print(f"✓ {source}: Added cards")

# ============================================================================
# MEDICINE - NEUROLOGY HEADACHE
# ============================================================================

def extract_medicine_neurology_headache():
    """Extract from Medicine/03_Neurology_Headache_Differentials.html"""
    file_path = BASE_PATH / "Medicine" / "03_Neurology_Headache_Differentials.html"
    deck = "Medicine_Neurology"
    source = "Medicine/03_Neurology_Headache_Differentials.html"

    # RED FLAGS
    add_card(
        "🚨 RED FLAG: Thunderclap headache (worst headache of life)",
        "Sudden onset severe headache reaching peak <1 minute → URGENT CT head + LP if CT negative (subarachnoid haemorrhage until proven otherwise)",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Headache with fever and neck stiffness",
        "Headache + fever + neck stiffness + photophobia → Meningitis. URGENT LP + blood cultures + IV ceftriaxone",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Headache with focal neurology",
        "Headache + focal neurology (weakness, sensory loss, visual field defect, speech disturbance) → Space-occupying lesion, stroke. URGENT CT/MRI",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Headache with papilloedema",
        "Headache + papilloedema + visual obscurations → Raised ICP. URGENT CT head + LP (measure opening pressure)",
        "red_flags", "hard", deck, source
    )

    # DIFFERENTIALS
    add_card(
        "Differentials: Primary headaches",
        "• Migraine (with/without aura)\n• Tension-type headache\n• Cluster headache\n• Medication overuse headache",
        "differential", "medium", deck, source
    )

    add_card(
        "Differentials: Secondary headaches (life-threatening)",
        "• Subarachnoid haemorrhage\n• Meningitis\n• Encephalitis\n• Space-occupying lesion\n• Temporal arteritis\n• Acute angle-closure glaucoma",
        "differential", "hard", deck, source
    )

    print(f"✓ {source}: Added cards")

# ============================================================================
# SURGERY - ACUTE ABDOMEN
# ============================================================================

def extract_surgery_acute_abdomen():
    """Extract from Surgery/01_Acute_Abdomen_History_Differentials.html"""
    deck = "Surgery"
    source = "Surgery/01_Acute_Abdomen_History_Differentials.html"

    # RED FLAGS
    add_card(
        "🚨 RED FLAG: Peritonitis clinical features",
        "Guarding (involuntary muscle spasm) + rigidity (board-like abdomen) + rebound tenderness + percussion tenderness + lying still → IMMEDIATE surgery",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Strangulated hernia",
        "Irreducible tender hernia + overlying skin changes (erythema) + systemic upset (fever, tachycardia) → IMMEDIATE surgery (bowel ischaemia risk)",
        "red_flags", "hard", deck, source
    )

    # PHYSICAL EXAM
    add_card(
        "Physical exam: Acute abdomen examination sequence",
        "1. Inspection (scars, distension, masses)\n2. Palpation (start away from pain, assess peritonism)\n3. Percussion (liver span, shifting dullness, rebound)\n4. Auscultation (bowel sounds)\n5. Special tests (Murphy's, McBurney's, Rovsing's)",
        "physical_exam", "medium", deck, source
    )

    add_card(
        "Physical exam: Murphy's sign (positive finding)",
        "Palpate RUQ whilst patient takes deep breath → Sudden cessation of inspiration due to pain = Positive Murphy's sign → Acute cholecystitis",
        "physical_exam", "medium", deck, source
    )

    print(f"✓ {source}: Added cards")

# ============================================================================
# OBGYN - OBSTETRIC HISTORY
# ============================================================================

def extract_obgyn_obstetric():
    """Extract from ObGyn/01_Obstetric_History_Differentials.html"""
    deck = "ObGyn"
    source = "ObGyn/01_Obstetric_History_Differentials.html"

    # RED FLAGS
    add_card(
        "🚨 RED FLAG: Pre-eclampsia severe features",
        "BP ≥160/110 + proteinuria + (severe headache OR visual disturbance OR epigastric pain OR elevated LFTs OR platelets <100) → URGENT MgSO4 + delivery",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Placental abruption",
        "Constant severe abdominal pain + woody hard uterus + vaginal bleeding + fetal distress → IMMEDIATE delivery (Category 1 C-section if fetus alive)",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Reduced fetal movements",
        "Maternal perception of reduced fetal movements ≥28 weeks → URGENT CTG + ultrasound (up to 50% of stillbirths preceded by reduced movements)",
        "red_flags", "hard", deck, source
    )

    # DIFFERENTIALS
    add_card(
        "Differentials: First trimester bleeding causes",
        "• Miscarriage (threatened, inevitable, incomplete, complete)\n• Ectopic pregnancy\n• Molar pregnancy\n• Cervical causes (polyp, ectropion, cancer)\n• Implantation bleeding",
        "differential", "medium", deck, source
    )

    add_card(
        "Differentials: Third trimester bleeding causes",
        "• Placenta praevia\n• Placental abruption\n• Vasa praevia\n• Show (bloody mucous plug)\n• Local causes (cervical, vaginal)",
        "differential", "hard", deck, source
    )

    print(f"✓ {source}: Added cards")

# ============================================================================
# PSYCHIATRY - RISK ASSESSMENT
# ============================================================================

def extract_psychiatry_risk():
    """Extract from Psychiatry/03_Risk_Assessment_Suicide_Violence_Selfneglect.html"""
    deck = "Psychiatry"
    source = "Psychiatry/03_Risk_Assessment_Suicide_Violence_Selfneglect.html"

    # RED FLAGS
    add_card(
        "🚨 RED FLAG: High suicide risk features",
        "Specific plan + means available + intent + no protective factors + previous attempts + hopelessness + psychosis with command hallucinations → Admit involuntarily if refuses",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Acute violence risk",
        "Recent violence + threats + psychosis with paranoid delusions + agitation + weapons access + substance intoxication → IMMEDIATE safety measures (security, de-escalation, sedation)",
        "red_flags", "hard", deck, source
    )

    # COMMUNICATION
    add_card(
        "Communication: Asking about suicidal ideation",
        "\"Have you been feeling so low that you've had thoughts of harming yourself or ending your life?\" (Direct, non-judgmental, shows concern)",
        "communication", "medium", deck, source
    )

    add_card(
        "Communication: Assessing suicide plan",
        "\"Have you thought about how you might do it?\" then \"Do you have access to [means]?\" and \"When were you thinking of doing this?\"",
        "communication", "medium", deck, source
    )

    print(f"✓ {source}: Added cards")

# ============================================================================
# PAEDIATRICS
# ============================================================================

def extract_paediatrics():
    """Extract from Paediatrics files"""
    deck = "Paediatrics"
    source = "Paediatrics/01_Paediatric_History_Differentials.html"

    # RED FLAGS
    add_card(
        "🚨 RED FLAG: Meningococcal septicaemia",
        "Non-blanching purpuric rash + fever + unwell child → IMMEDIATE IM/IV benzylpenicillin + hospital transfer (DON'T delay for LP)",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Febrile child <3 months",
        "Any fever in infant <3 months → High risk of serious bacterial infection. Admit + full septic screen + IV antibiotics",
        "red_flags", "hard", deck, source
    )

    add_card(
        "🚨 RED FLAG: Respiratory distress in children",
        "Grunting + nasal flaring + subcostal/intercostal recession + tracheal tug + SpO2 <92% → High-flow O2 + URGENT paediatric review",
        "red_flags", "hard", deck, source
    )

    print(f"✓ {source}: Added cards")

# ============================================================================
# AUSTRALIAN CONTEXT
# ============================================================================

def extract_australian_context():
    """Extract Australian-specific content"""

    # eTG references
    add_card(
        "Australian context: eTG (Therapeutic Guidelines)",
        "Australian evidence-based guidelines for medication and management. FREE access via NPS MedicineWise app. ALWAYS reference eTG in AMC OSCE for antibiotic choices, dosing.",
        "australian", "medium", "General", "Multiple sources"
    )

    add_card(
        "Australian context: PBS (Pharmaceutical Benefits Scheme)",
        "Australian government subsidy for medications. Check PBS restrictions before prescribing expensive medications (e.g., biologics require authority approval).",
        "australian", "medium", "General", "Multiple sources"
    )

    add_card(
        "Australian context: ANZCOR (resuscitation guidelines)",
        "Australian and New Zealand Committee on Resuscitation. Use ANZCOR protocols for CPR, anaphylaxis (adrenaline doses), ALS algorithms.",
        "australian", "medium", "Medicine_Emergency", "Multiple sources"
    )

    add_card(
        "Australian context: Community pharmacy access",
        "Australian pharmacies provide emergency contraception (without prescription), nicotine replacement therapy, some antibiotics (UTI - pharmacist-only). Mention in safety-netting.",
        "australian", "easy", "General", "Multiple sources"
    )

    add_card(
        "Australian context: Bulk billing and costs",
        "Mention costs in counselling: 'This medication is PBS-listed, so it will cost you $XX at the pharmacy.' Shows cultural awareness of Australian healthcare system.",
        "australian", "easy", "General", "Multiple sources"
    )

    add_card(
        "Australian spelling: Key medical terms",
        "Use -ise not -ize (e.g., hospitalise, organise), -our not -or (e.g., labour, tumour), -ae not -e (e.g., paediatric, anaesthesia), -re not -er (e.g., centre, litre)",
        "australian", "easy", "General", "Multiple sources"
    )

    print("✓ Australian context: Added cards")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("FLASHCARD EXTRACTION V2 - High-Quality Manual Extraction")
    print("=" * 60)
    print()

    # Extract from each module
    extract_medicine_gi_abdominal_pain()
    extract_medicine_gi_bleeding()
    extract_medicine_neurology_headache()
    extract_surgery_acute_abdomen()
    extract_obgyn_obstetric()
    extract_psychiatry_risk()
    extract_paediatrics()
    extract_australian_context()

    # TODO: Add more extraction functions for other modules
    # This is a foundation - need to manually add more cards

    print()
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"New cards extracted: {len(new_cards)}")
    print(f"Total cards: {len(data['cards']) + len(new_cards)}")
    print()

    # Save
    data['cards'].extend(new_cards)
    data['metadata']['total_cards'] = len(data['cards'])
    data['metadata']['last_updated'] = datetime.now().isoformat()
    data['metadata']['note'] = "Phase 1.1: High-quality manual extraction with proper categorization"

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved to {OUTPUT_FILE}")

    # Statistics
    print()
    print("STATISTICS BY CATEGORY:")
    print("-" * 60)
    categories = {}
    for card in new_cards:
        cat = card['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        target = data['metadata']['targets'].get(cat, '?')
        print(f"  {cat:20s}: {count:4d}/{target} cards")

    print()
    print("STATISTICS BY DECK:")
    print("-" * 60)
    decks = {}
    for card in new_cards:
        deck = card['deck']
        decks[deck] = decks.get(deck, 0) + 1

    for deck, count in sorted(decks.items(), key=lambda x: x[1], reverse=True):
        print(f"  {deck:30s}: {count:4d} cards")

    print()
    print("=" * 60)
    print("NOTE: This is a foundation with ~50 high-quality cards.")
    print("To reach 750 cards, continue adding extraction functions")
    print("for remaining modules following the same pattern.")
    print("=" * 60)

if __name__ == '__main__':
    main()
