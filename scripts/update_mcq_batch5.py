#!/usr/bin/env python3
"""
Update MCQ Batch 5 - ENDO-MCQ-0031 to 0040
Claude Code Generated Content - DKA (Diabetic Ketoacidosis)
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

    print(f"\n💾 Saved {updated_count} updated MCQs to {file_path}")
    return updated_count


# Batch 5: ENDO-MCQ-0031 to 0040
batch5_generated = {
    "ENDO-MCQ-0031": {
        "subtopic": "DKA Diagnosis Criteria",
        "scenario": "A 24-year-old man with known type 1 diabetes presents to ED with 2 days of nausea, vomiting, and abdominal pain. He ran out of insulin 3 days ago. He appears dehydrated with Kussmaul breathing. Vital signs: BP 95/60 mmHg, HR 118 bpm, RR 28/min. Capillary glucose 28.5 mmol/L. Venous blood gas shows: pH 7.18, bicarbonate 9 mmol/L, pCO2 24 mmHg. Urinalysis shows 3+ ketones.",
        "stem": "Which biochemical criteria confirm the diagnosis of diabetic ketoacidosis?",
        "options": {
            "A": "Hyperglycaemia (>11 mmol/L) alone",
            "B": "Hyperglycaemia (>11 mmol/L), metabolic acidosis (pH <7.3, bicarbonate <15 mmol/L), and ketonaemia/ketonuria",
            "C": "Hyperglycaemia (>20 mmol/L) and vomiting",
            "D": "Ketones in urine alone"
        },
        "correct_answer": "B",
        "explanation": "DKA diagnostic criteria (all three required): (1) Hyperglycaemia: blood glucose >11 mmol/L (or known diabetes); (2) Metabolic acidosis: pH <7.3 and/or bicarbonate <15 mmol/L; (3) Ketonaemia (blood ketones >3 mmol/L) or ketonuria (2+ or more on urinalysis). Severity classification: Mild (pH 7.25-7.30), Moderate (pH 7.0-7.24), Severe (pH <7.0). This patient has all criteria: glucose 28.5 mmol/L, pH 7.18, bicarbonate 9 mmol/L, urine ketones 3+. Note: Euglycemic DKA (glucose <14 mmol/L with acidosis and ketosis) can occur with SGLT2 inhibitors, pregnancy, or starvation - diagnosis relies on acidosis and ketones. Clinical features include dehydration, Kussmaul breathing (deep rapid respirations), abdominal pain, fruity breath odor, altered consciousness."
    },

    "ENDO-MCQ-0032": {
        "subtopic": "DKA Initial Fluid Resuscitation",
        "scenario": "A 32-year-old woman with type 1 diabetes presents in DKA. BP 88/55 mmHg, HR 125 bpm, capillary refill 4 seconds. Weight 60 kg. Blood glucose 32 mmol/L, pH 7.12, bicarbonate 8 mmol/L, sodium 138 mmol/L, potassium 5.2 mmol/L. She is being prepared for IV fluid resuscitation.",
        "stem": "What is the most appropriate initial fluid management?",
        "options": {
            "A": "0.9% sodium chloride 1 litre over 1 hour, then reassess",
            "B": "5% dextrose 1 litre over 4 hours",
            "C": "0.45% sodium chloride 500 mL/hour",
            "D": "Colloid solution 500 mL stat"
        },
        "correct_answer": "A",
        "explanation": "Initial fluid resuscitation in DKA: (1) 0.9% sodium chloride (normal saline) is first-line fluid; (2) If hypotensive/shocked: 1 litre over 1 hour (500 mL over 15 minutes if severe shock), reassess, repeat if needed; (3) Once BP stable: typical regimen is 1 L over 1st hour, 1 L over next 2 hours, 1 L over next 2 hours, then 1 L over 4 hours (total ~4-6 L in first 12 hours). Fluid deficit in DKA is typically 100 mL/kg (6 litres for 60 kg patient). After initial resuscitation, when glucose falls to 14-15 mmol/L, add 5% or 10% dextrose to prevent hypoglycaemia while continuing insulin to clear ketosis. Avoid hypotonic saline (0.45%) initially due to risk of cerebral oedema. Aim for gradual correction - too rapid fluid replacement increases cerebral oedema risk, especially in children."
    },

    "ENDO-MCQ-0033": {
        "subtopic": "DKA Insulin Therapy Protocol",
        "scenario": "A 28-year-old man with DKA (glucose 26 mmol/L, pH 7.15, bicarbonate 10 mmol/L, potassium 4.2 mmol/L) has received initial fluid resuscitation with 1 litre normal saline. His BP is now 105/70 mmHg. He is ready to commence insulin therapy.",
        "stem": "What is the most appropriate insulin regimen for DKA management?",
        "options": {
            "A": "Fixed-rate IV insulin infusion at 0.1 units/kg/hour (approximately 6-8 units/hour for average adult)",
            "B": "Subcutaneous rapid-acting insulin every 2 hours",
            "C": "IV insulin bolus 0.1 units/kg, then infusion at 0.05 units/kg/hour",
            "D": "Withhold insulin until potassium <5.5 mmol/L"
        },
        "correct_answer": "A",
        "explanation": "DKA insulin management: (1) Fixed-rate IV insulin infusion: 0.1 units/kg/hour (approximately 6-8 units/hour for 60-80 kg adult) via infusion pump; (2) Do NOT give insulin bolus initially (no longer recommended in most protocols); (3) Start insulin only after potassium >3.3 mmol/L (risk of life-threatening hypokalaemia if started earlier); (4) Continue insulin infusion until ketones clear (pH >7.3, bicarbonate >15 mmol/L, blood ketones <0.6 mmol/L), NOT just until glucose normalizes; (5) When glucose falls to 14-15 mmol/L, add dextrose infusion and continue insulin to clear ketosis. Aim for glucose fall of 3 mmol/L/hour. If glucose not falling adequately, increase insulin rate by 1 unit/hour increments. Subcutaneous insulin is NOT appropriate in acute DKA due to poor absorption from dehydration/hypoperfusion."
    },

    "ENDO-MCQ-0034": {
        "subtopic": "Potassium Replacement in DKA",
        "scenario": "A 35-year-old woman with DKA has commenced IV fluids and insulin. Initial potassium was 5.8 mmol/L. After 2 hours of treatment, repeat electrolytes show: potassium 3.2 mmol/L, glucose 18 mmol/L, pH 7.22. The insulin infusion is currently running at 7 units/hour.",
        "stem": "What is the most appropriate immediate action?",
        "options": {
            "A": "Continue current treatment without modification",
            "B": "Stop insulin infusion until potassium >5.5 mmol/L",
            "C": "Stop insulin infusion, give 40 mmol potassium chloride over 1 hour, then restart insulin when potassium >3.5 mmol/L",
            "D": "Reduce insulin infusion rate by 50%"
        },
        "correct_answer": "C",
        "explanation": "Potassium management in DKA is critical. Despite often presenting with hyperkalaemia (due to acidosis and insulin deficiency causing K+ shift from cells), total body potassium is depleted (losses via osmotic diuresis). With insulin and fluid treatment, potassium rapidly falls. Management: (1) Do NOT start insulin if K+ <3.3 mmol/L (risk cardiac arrhythmias); (2) If K+ 3.3-5.5 mmol/L: add 40 mmol/L KCl to each litre of IV fluid; (3) If K+ falls below 3.3 mmol/L during treatment: STOP insulin, give concentrated potassium replacement (10-20 mmol/hour via central line or 40 mmol over 1 hour peripherally), restart insulin when K+ >3.5 mmol/L; (4) Monitor K+ hourly initially, then 2-4 hourly. Target potassium 4-5 mmol/L during DKA treatment. Life-threatening hypokalaemia can occur if insulin given without adequate potassium replacement."
    },

    "ENDO-MCQ-0035": {
        "subtopic": "Bicarbonate Use in DKA",
        "scenario": "A 42-year-old man with severe DKA presents with pH 6.95, bicarbonate 4 mmol/L, glucose 34 mmol/L, potassium 5.5 mmol/L. He is conscious but drowsy. BP 90/60 mmHg after 1 litre fluid. The ED team is considering bicarbonate administration.",
        "stem": "What is the most appropriate management regarding bicarbonate therapy?",
        "options": {
            "A": "Give IV sodium bicarbonate 100 mmol immediately",
            "B": "Bicarbonate is NOT routinely recommended; only consider if pH <6.9 with cardiovascular compromise, and give cautiously (50 mmol over 1 hour with close monitoring)",
            "C": "Give oral sodium bicarbonate 1 g every hour",
            "D": "Bicarbonate is mandatory for all DKA patients with pH <7.0"
        },
        "correct_answer": "B",
        "explanation": "Bicarbonate use in DKA is controversial and generally NOT recommended. Evidence shows no benefit and potential harm. Current guidelines: (1) Do NOT routinely give bicarbonate in DKA; (2) Consider only if pH <6.9 (some say <7.0) AND cardiovascular instability/life-threatening hyperkalaemia; (3) If given: 50 mmol sodium bicarbonate in 200 mL water over 1 hour, with close monitoring; (4) Risks of bicarbonate include: paradoxical CNS acidosis (CO2 crosses blood-brain barrier faster than bicarbonate), hypokalaemia (worsened by alkalosis), sodium overload, rebound alkalosis. The acidosis in DKA resolves with insulin therapy (stops ketone production) and fluid resuscitation. Giving bicarbonate does not improve clinical outcomes and may increase cerebral oedema risk, particularly in children. Focus on insulin, fluids, and potassium replacement."
    },

    "ENDO-MCQ-0036": {
        "subtopic": "Cerebral Oedema in DKA",
        "scenario": "A 12-year-old boy with new-onset type 1 diabetes is being treated for severe DKA (pH 6.98). After 6 hours of treatment, his glucose has fallen from 38 to 12 mmol/L and pH improved to 7.15. He suddenly becomes drowsy with headache, then rapidly loses consciousness. BP 150/95 mmHg, HR 58 bpm, pupils unequal.",
        "stem": "What is the most likely diagnosis and immediate management?",
        "options": {
            "A": "Hypoglycaemia - give IV dextrose 50%",
            "B": "Cerebral oedema - give IV mannitol or hypertonic saline immediately, reduce fluid rate, notify ICU",
            "C": "Hypernatraemia - increase fluid rate",
            "D": "Hypokalaemia - give potassium replacement"
        },
        "correct_answer": "B",
        "explanation": "This is cerebral oedema, the most serious complication of DKA, occurring in 0.5-1% of cases (higher in children, new-onset diabetes, severe DKA). Mortality 20-40%. Clinical features: headache, altered consciousness, hypertension, bradycardia (Cushing's reflex), papilloedema, unequal pupils. Risk factors: younger age, new-onset diabetes, severe acidosis, rapid fall in glucose, excessive fluid administration, bicarbonate use. Immediate management: (1) IV mannitol 0.25-1 g/kg over 10-15 minutes OR hypertonic (3%) saline 2.5-5 mL/kg over 10-15 minutes; (2) Reduce IV fluid rate by one-third; (3) Elevate head of bed 30°; (4) Urgent CT brain (but do NOT delay treatment); (5) Notify ICU for intubation if needed. Prevention: avoid excessive fluid rates (especially hypotonic fluids), gradual glucose correction (not >5 mmol/L/hour), avoid bicarbonate if possible. This scenario shows classic signs: sudden neurological deterioration during DKA treatment with hypertension and bradycardia."
    },

    "ENDO-MCQ-0037": {
        "subtopic": "DKA vs HHS Differentiation",
        "scenario": "A 68-year-old man with poorly controlled type 2 diabetes (on metformin and gliclazide) presents with 1 week of polyuria, polydipsia, and confusion. He appears severely dehydrated. Blood tests show: glucose 58 mmol/L, sodium 158 mmol/L, osmolality 385 mOsm/kg, pH 7.35, bicarbonate 22 mmol/L, urine ketones trace.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Diabetic ketoacidosis (DKA)",
            "B": "Hyperosmolar hyperglycaemic state (HHS)",
            "C": "Euglycaemic DKA",
            "D": "Lactic acidosis"
        },
        "correct_answer": "B",
        "explanation": "This is hyperosmolar hyperglycaemic state (HHS), not DKA. Key differences:\n\nDKA: Glucose usually 15-30 mmol/L, severe acidosis (pH <7.3), high ketones, normal/low osmolality, typically type 1 diabetes, acute onset (hours-days)\n\nHHS: Very high glucose (>30 mmol/L, often >50), mild/no acidosis (pH >7.3), minimal ketones, very high osmolality (>320 mOsm/kg), severe dehydration, altered consciousness common, typically type 2 diabetes/elderly, gradual onset (days-weeks)\n\nThis patient has: severe hyperglycaemia (58 mmol/L), normal pH (7.35), minimal ketones (trace), hyperosmolality (385), hypernatraemia (158), confusion - classic HHS. Pathophysiology: residual insulin prevents lipolysis/ketogenesis but insufficient to control glucose. More profound dehydration than DKA (typical deficit 8-10 L vs 4-6 L). Management similar to DKA but: slower fluid replacement, lower insulin rates (0.05 units/kg/hr), higher thromboembolism risk (prophylactic LMWH recommended). Mortality higher than DKA (10-20% vs 1-5%)."
    },

    "ENDO-MCQ-0038": {
        "subtopic": "DKA Precipitating Factors",
        "scenario": "A 26-year-old woman with type 1 diabetes for 10 years presents with her third episode of DKA in 6 months. She reports good adherence to her insulin regimen. Each episode has required hospital admission. Between episodes, her HbA1c has been 7.2% (target <7%). Investigations during current admission reveal normal thyroid function, no evidence of infection, and negative pregnancy test.",
        "stem": "What is the most important precipitating factor to explore in this case?",
        "options": {
            "A": "Insulin pump malfunction",
            "B": "Eating disorder (diabulimia) with insulin omission",
            "C": "Undiagnosed Addison's disease",
            "D": "Factitious disorder (deliberately inducing DKA)"
        },
        "correct_answer": "B",
        "explanation": "Common DKA precipitating factors (remember the 5 I's): (1) Infection (most common: 30-40%); (2) Inadequate insulin (non-adherence, pump failure, prescription errors); (3) Ischaemia/Infarction (MI, stroke); (4) Intoxication (alcohol, drugs); (5) Inaugural (new diagnosis - 20-30%). In this case: recurrent DKA, young woman, claims good adherence, reasonable HbA1c between episodes, no clear trigger. This suggests insulin omission, often related to eating disorders (\"diabulimia\"). Young women with type 1 diabetes have higher rates of eating disorders. Deliberate insulin omission causes weight loss (glucosuria) but leads to DKA. Red flags: recurrent DKA without clear cause, discrepancy between reported adherence and DKA frequency, weight concerns. Other causes to consider: alcohol excess (causes ketosis), SGLT2 inhibitors (euglycemic DKA), pregnancy. Management requires multidisciplinary approach: diabetes team, mental health, dietitian. Direct but non-judgmental questioning about eating behaviors and insulin use is essential."
    },

    "ENDO-MCQ-0039": {
        "subtopic": "DKA Resolution Criteria",
        "scenario": "A 30-year-old woman has been treated for DKA for 14 hours. Current values: glucose 11 mmol/L, pH 7.32, bicarbonate 16.5 mmol/L, blood ketones 0.8 mmol/L. She is feeling much better and tolerating oral fluids. The team is considering stopping IV insulin infusion.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Stop IV insulin immediately and resume usual subcutaneous insulin regimen",
            "B": "Continue IV insulin until all of the following are met: pH >7.3, bicarbonate >15 mmol/L, blood ketones <0.6 mmol/L, then overlap subcutaneous and IV insulin",
            "C": "Continue IV insulin for 24 hours regardless of biochemistry",
            "D": "Stop IV insulin and IV fluids immediately as glucose is normalized"
        },
        "correct_answer": "B",
        "explanation": "DKA resolution criteria (ALL must be met): (1) pH >7.3; (2) Bicarbonate >15 mmol/L; (3) Blood ketones <0.6 mmol/L (or <0.5 mmol/L in some protocols); (4) Patient able to eat and drink. This patient does not yet meet criteria: pH 7.32 (just above 7.3), bicarbonate 16.5 (above 15), but ketones still 0.8 (above 0.6 threshold). Continue IV insulin until ketones <0.6 mmol/L. Transition to subcutaneous insulin: (1) Give subcutaneous rapid-acting insulin with meal; (2) Continue IV insulin infusion for 30-60 minutes after subcutaneous dose (allows time for subcutaneous insulin to be absorbed); (3) Then stop IV insulin; (4) If patient is on established insulin regimen, resume it; if new diagnosis, start basal-bolus regimen. Do NOT stop IV insulin before subcutaneous insulin has been given and absorbed - this risks recurrent ketoacidosis. Monitor capillary glucose and ketones for 24 hours after transition. Common error: stopping IV insulin when glucose normalizes, but ketosis not fully resolved."
    },

    "ENDO-MCQ-0040": {
        "subtopic": "Euglycemic DKA and SGLT2 Inhibitors",
        "scenario": "A 52-year-old woman with type 2 diabetes (on metformin, empagliflozin, and sitagliptin) presents to ED after 3 days of vomiting and reduced oral intake due to gastroenteritis. She stopped her metformin but continued other medications. She feels unwell with abdominal pain. Capillary glucose 12.5 mmol/L. Venous gas shows pH 7.15, bicarbonate 8 mmol/L, blood ketones 5.2 mmol/L.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Viral gastroenteritis with dehydration",
            "B": "Euglycemic DKA secondary to SGLT2 inhibitor (empagliflozin)",
            "C": "Lactic acidosis from metformin",
            "D": "Starvation ketosis"
        },
        "correct_answer": "B",
        "explanation": "This is euglycemic DKA (eDKA) secondary to SGLT2 inhibitor. SGLT2 inhibitors (empagliflozin, dapagliflozin, canagliflozin) cause urinary glucose excretion, lowering blood glucose but promoting ketogenesis. Risk factors for eDKA with SGLT2 inhibitors: (1) Reduced oral intake/starvation; (2) Acute illness; (3) Surgery; (4) Low carbohydrate diets; (5) Insulin deficiency; (6) Alcohol. This patient has DKA (pH 7.15, bicarbonate 8, ketones 5.2) but glucose only mildly elevated (12.5 mmol/L, not >20 typical of DKA). Presentation often delayed as patients feel well initially despite developing ketoacidosis (glucose not high, so polyuria/polydipsia absent). Management: (1) Stop SGLT2 inhibitor; (2) Treat as DKA: IV fluids, IV insulin (may need higher rates as some insulin resistance), potassium replacement, dextrose early (as glucose not elevated); (3) Identify/treat precipitant. Prevention: patient education to stop SGLT2 inhibitor during illness/fasting/surgery. SGLT2 inhibitors contraindicated in type 1 diabetes (high eDKA risk). Regular DKA would show glucose >20 mmol/L. Starvation ketosis typically milder (pH >7.3, ketones <3 mmol/L)."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 5 UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 5: ENDO-MCQ-0031 to 0040 (DKA - Diabetic Ketoacidosis)")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch5_generated)

    print(f"\n✅ Batch 5 Complete: {updated}/10 MCQs updated")
    print(f"✅ Total Progress: 40/658 MCQs (6.1%)")
    print(f"\nNext: Continue with remaining 618 MCQs")
