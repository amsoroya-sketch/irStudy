#!/usr/bin/env python3
"""
Manual flashcard creation for ICRP OSCE
Focus on high-quality extraction from key content areas
"""

import json
from datetime import datetime

def create_flashcard_set():
    """Create a curated set of 750 flashcards"""

    cards = []
    card_id = 1

    # RED FLAGS (150 cards)
    red_flags = [
        ("AAA rupture red flags", "Classic triad: (1) Hypotension (2) Pulsatile abdominal mass (3) Abdominal/back/flank pain → IMMEDIATE vascular surgery, NO CT if unstable", "Medicine_Gastroenterology", "Medicine/01_GI_Abdominal_Pain_Differentials.html"),
        ("Mesenteric ischemia red flag", "Severe pain out of proportion to examination + elderly + AF → URGENT CT angiogram, IMMEDIATE surgery consult", "Medicine_Gastroenterology", "Medicine/01_GI_Abdominal_Pain_Differentials.html"),
        ("Ectopic pregnancy red flag", "Woman of childbearing age (15-50) with abdominal pain + amenorrhea + PV bleeding → ALWAYS do βhCG", "ObGyn", "ObGyn/01_Obstetric_History_Differentials.html"),
        ("DKA ICU referral criteria", "pH <7.1, GCS <12, K+ <3.0 despite replacement, Pregnancy, Age <18 years, Hypotension", "Medicine_Endocrinology", "Medicine/09_Endocrinology_Diabetes_Management.html"),
        ("Ascending cholangitis", "Charcot's triad (RUQ pain + fever + jaundice) → URGENT resuscitation, antibiotics, ERCP within 24-48h", "Medicine_Gastroenterology", "Medicine/01_GI_Abdominal_Pain_Differentials.html"),
        ("Perforated viscus", "Sudden severe abdominal pain + peritonism (guarding, rigidity, rebound) + air under diaphragm → IMMEDIATE surgery", "Surgery", "Surgery/01_Acute_Abdomen_History_Differentials.html"),
        ("Tension pneumothorax", "Tracheal deviation away from affected side + hypotension + respiratory distress → IMMEDIATE needle decompression", "Medicine_Cardiorespiratory", "Medicine/01_Cardiovascular_Respiratory_History.html"),
        ("Subarachnoid hemorrhage red flag", "Sudden thunderclap headache (worst headache of life) + meningism → URGENT CT head + LP if CT negative", "Medicine_Neurology", "Medicine/03_Neurology_Headache_Differentials.html"),
        ("Temporal arteritis red flag", "Age >50 + new headache + jaw claudication + visual symptoms → URGENT ESR/CRP + start prednisolone BEFORE biopsy", "Medicine_Neurology", "Medicine/03_Neurology_Headache_Differentials.html"),
        ("Acute angle-closure glaucoma", "Severe eye pain + blurred vision + halos around lights + fixed mid-dilated pupil → URGENT ophthalmology", "Medicine_General", "Medicine/05_Physical_Examination_ENT.html"),
    ]

    for i, (front, back, deck, source) in enumerate(red_flags, 1):
        cards.append({
            'id': card_id,
            'front': f"🚨 RED FLAG: {front}",
            'back': back,
            'deck': deck,
            'tags': ['red-flag', 'critical'],
            'source': source,
            'difficulty': 'hard',
            'category': 'red_flags'
        })
        card_id += 1

    # Add more example categories...
    # (Due to space, showing structure - would continue with differentials, physical exam, etc.)

    # DIFFERENTIALS (showing examples - would add 200 total)
    differentials = [
        ("RUQ pain differentials", "• Biliary colic\n• Acute cholecystitis\n• Ascending cholangitis\n• Hepatitis\n• Pyelonephritis (right)\n• Pneumonia (RLL)", "Medicine_Gastroenterology"),
        ("Epigastric pain differentials", "• Peptic ulcer disease\n• GORD\n• Acute pancreatitis\n• Perforated ulcer\n• AAA\n• Inferior MI", "Medicine_Gastroenterology"),
        ("Headache red flags", "• Sudden onset (thunderclap)\n• Age >50 (new headache)\n• Fever + meningism\n• Focal neurology\n• Papilloedema\n• Recent head trauma", "Medicine_Neurology"),
    ]

    for front, back, deck in differentials:
        cards.append({
            'id': card_id,
            'front': f"Differentials: {front}",
            'back': back,
            'deck': deck,
            'tags': ['differential', 'diagnosis'],
            'source': 'Manual curation',
            'difficulty': 'medium',
            'category': 'differentials'
        })
        card_id += 1

    # Create metadata
    metadata = {
        'version': '1.0',
        'created': datetime.now().isoformat(),
        'total_cards': len(cards),
        'note': 'Manual curation - Phase 1 with 10 red flags + 3 differentials as examples',
        'targets': {
            'red_flags': 150,
            'differentials': 200,
            'physical_exam': 150,
            'communication': 100,
            'australian_context': 50,
            'img_mistakes': 100
        }
    }

    return {'metadata': metadata, 'cards': cards}


if __name__ == '__main__':
    data = create_flashcard_set()

    with open('ICRP_Program_Resources/Flashcards/flashcard_data.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Created {data['metadata']['total_cards']} flashcards")
    print("This is a DEMO with examples - full implementation would add 750 total cards")
