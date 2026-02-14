#!/usr/bin/env python3
"""
Update MCQ Batch 3 - ENDO-MCQ-0011 to 0020
Claude Code Generated Content - Hyperthyroidism (5) + Hypothyroidism (5)
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


# Batch 3: ENDO-MCQ-0011 to 0020 (5 Hyperthyroid + 5 Hypothyroid)
batch3_generated = {
    "ENDO-MCQ-0011": {
        "subtopic": "Post-Partum Thyroiditis",
        "scenario": "A 28-year-old woman presents 4 months post-partum with fatigue, palpitations, and weight loss. She is breastfeeding. Thyroid function shows TSH <0.01 mIU/L and free T4 32 pmol/L. TPO antibodies are positive. She has no goitre and her thyroid is non-tender.",
        "stem": "What is the most likely diagnosis and appropriate management?",
        "options": {
            "A": "Graves' disease - start carbimazole",
            "B": "Post-partum thyroiditis - symptomatic treatment and monitor",
            "C": "Toxic adenoma - refer for radioactive iodine",
            "D": "Subacute thyroiditis - start NSAIDs"
        },
        "correct_answer": "B",
        "explanation": "Post-partum thyroiditis occurs in 5-10% of women in the first year post-partum, typically 1-6 months after delivery. It follows a triphasic pattern: (1) Thyrotoxic phase (1-3 months) - treated symptomatically with beta-blockers; (2) Hypothyroid phase (4-8 months) - may need thyroxine if symptomatic; (3) Recovery (usually by 12 months). Positive TPO antibodies support the diagnosis. The thyrotoxic phase is due to thyroid destruction/hormone release, not overproduction, so antithyroid drugs are not indicated. Most women recover completely, but 20-30% develop permanent hypothyroidism. Avoid radioactive iodine (contraindicated in breastfeeding)."
    },

    "ENDO-MCQ-0012": {
        "subtopic": "Sick Euthyroid Syndrome",
        "scenario": "A 75-year-old man is admitted to ICU with severe community-acquired pneumonia and septic shock. Thyroid function tests ordered as part of workup show TSH 0.2 mIU/L (low-normal), free T4 8 pmol/L (low), and free T3 2.0 pmol/L (low). He has no previous thyroid disease and is not on amiodarone.",
        "stem": "What is the most appropriate management of his thyroid results?",
        "options": {
            "A": "Start levothyroxine 100 mcg daily immediately",
            "B": "Reassure - this is sick euthyroid syndrome, treat underlying illness",
            "C": "Request urgent endocrinology review for myxoedema coma",
            "D": "Check cortisol and start hydrocortisone for possible adrenal insufficiency"
        },
        "correct_answer": "B",
        "explanation": "This is sick euthyroid syndrome (non-thyroidal illness syndrome), a common finding in critically ill patients. Changes reflect adaptive response to severe illness: decreased T3 (reduced peripheral conversion), low/normal TSH, and low T4 in severe illness. Key features: (1) Acute severe illness; (2) No previous thyroid disease; (3) Low T3 with low-normal TSH. Management is to treat the underlying illness - thyroid function normalizes with recovery. Levothyroxine replacement is NOT indicated and may be harmful. Repeat TFTs after recovery to confirm resolution. Myxoedema coma would present with severe hypothermia, reduced consciousness, and very high TSH."
    },

    "ENDO-MCQ-0013": {
        "subtopic": "Thyroid Nodule Management",
        "scenario": "A 50-year-old woman has a 2.5 cm thyroid nodule discovered incidentally on carotid Doppler. She is clinically euthyroid. TSH is normal at 2.1 mIU/L. Thyroid ultrasound shows a solid, hypoechoic nodule with irregular margins and microcalcifications. No cervical lymphadenopathy.",
        "stem": "What is the most appropriate next investigation?",
        "options": {
            "A": "Repeat ultrasound in 6 months",
            "B": "Fine needle aspiration (FNA) biopsy",
            "C": "Thyroid uptake scan",
            "D": "CT neck with contrast"
        },
        "correct_answer": "B",
        "explanation": "This nodule has suspicious ultrasound features (hypoechoic, irregular margins, microcalcifications) requiring FNA biopsy. Indications for FNA in euthyroid patients: (1) Nodule >1 cm with suspicious features; (2) Any nodule >1.5 cm; (3) Any size nodule with suspicious lymph nodes or high-risk history. Normal TSH rules out functional nodule. FNA is the diagnostic test of choice - results guide management (benign: observe; indeterminate: repeat FNA or molecular testing; malignant: surgery). Thyroid uptake scan is only useful if TSH is suppressed (to identify hot nodule). CT is not first-line but may be needed for large goitres or retrosternal extension."
    },

    "ENDO-MCQ-0014": {
        "subtopic": "Papillary Thyroid Cancer",
        "scenario": "A 35-year-old woman undergoes total thyroidectomy for a 3 cm papillary thyroid carcinoma with no lymph node involvement. Histology confirms papillary carcinoma, confined to thyroid, clear margins. Post-operative calcium and PTH are normal.",
        "stem": "What is the most appropriate post-operative management?",
        "options": {
            "A": "No further treatment - discharge to GP",
            "B": "Levothyroxine to achieve TSH <0.1 mIU/L, then radioactive iodine ablation",
            "C": "Levothyroxine replacement dose to maintain TSH 0.5-2.0 mIU/L only",
            "D": "External beam radiotherapy"
        },
        "correct_answer": "B",
        "explanation": "Post-thyroidectomy management for papillary thyroid cancer includes: (1) Levothyroxine for TSH suppression (<0.1 mIU/L for high-risk, 0.1-0.5 for low-intermediate risk) - suppresses any residual thyroid tissue and micrometastases; (2) Radioactive iodine (RAI) ablation for most patients - destroys residual thyroid tissue and treats occult metastases; (3) Lifelong monitoring with thyroglobulin and anti-Tg antibodies. RAI is typically given for tumours >1 cm, lymph node involvement, or adverse features. Simple replacement dosing is insufficient. External beam radiotherapy is rarely used in differentiated thyroid cancer. Follow-up includes ultrasound neck, thyroglobulin monitoring, and RAI scans if indicated."
    },

    "ENDO-MCQ-0015": {
        "subtopic": "Levothyroxine Drug Interactions",
        "scenario": "A 55-year-old woman with well-controlled primary hypothyroidism on levothyroxine 100 mcg daily presents with recurrent symptoms of hypothyroidism (fatigue, weight gain, constipation) over the past 2 months. TSH is now 12 mIU/L (previously 2.5 mIU/L). Medication review reveals she started taking omeprazole 20 mg daily for reflux 3 months ago. She takes levothyroxine in the morning with her other medications.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Increase levothyroxine dose to 125 mcg daily",
            "B": "Advise taking levothyroxine 30-60 minutes before breakfast, separate from omeprazole",
            "C": "Stop omeprazole immediately",
            "D": "Switch from levothyroxine to liothyronine (T3)"
        },
        "correct_answer": "B",
        "explanation": "Levothyroxine absorption is impaired by proton pump inhibitors (PPIs), iron, calcium, antacids, and some foods. Optimal absorption occurs on empty stomach. Management: (1) Take levothyroxine 30-60 minutes before breakfast or at bedtime (at least 4 hours after last meal); (2) Separate from interfering medications by at least 4 hours; (3) Consider dose increase only if optimizing timing doesn't correct TSH. Other common interactions: iron/calcium supplements (separate by 4 hours), bile acid sequestrants, sucralfate. Patient education on timing is crucial. Stopping omeprazole may be unnecessary if used for valid indication. Liothyronine is not standard therapy."
    },

    "ENDO-MCQ-0016": {
        "subtopic": "Primary Hypothyroidism Diagnosis",
        "scenario": "A 42-year-old woman presents with 6-month history of progressive fatigue, weight gain (5 kg), cold intolerance, constipation, and heavy menstrual periods. On examination, she has a slow relaxing ankle reflex, dry skin, and periorbital puffiness. Her pulse is 58 bpm and regular.",
        "stem": "Which initial investigation will confirm the diagnosis?",
        "options": {
            "A": "Free T4 level only",
            "B": "TSH and free T4 levels",
            "C": "Thyroid autoantibodies (TPO and thyroglobulin)",
            "D": "Thyroid ultrasound"
        },
        "correct_answer": "B",
        "explanation": "The clinical features suggest primary hypothyroidism. Initial investigation is TSH and free T4. In primary hypothyroidism: TSH is elevated (>4 mIU/L) and free T4 is low. TSH alone may miss central (secondary) hypothyroidism, though this is rare. Thyroid antibodies (anti-TPO, anti-thyroglobulin) help identify autoimmune cause (Hashimoto's thyroiditis) but are not needed for diagnosis. Ultrasound is not required for diagnosis but may show features of Hashimoto's (heterogeneous, hypoechoic gland). Once diagnosis confirmed, check for other autoimmune conditions and start levothyroxine replacement."
    },

    "ENDO-MCQ-0017": {
        "subtopic": "Hypothyroidism in Cardiac Disease",
        "scenario": "A 65-year-old woman is newly diagnosed with primary hypothyroidism (TSH 28 mIU/L, free T4 6 pmol/L). She has a history of ischaemic heart disease with previous myocardial infarction 2 years ago. She is clinically stable on aspirin, atorvastatin, and bisoprolol.",
        "stem": "What is the most appropriate starting dose of levothyroxine?",
        "options": {
            "A": "Levothyroxine 100 mcg daily",
            "B": "Levothyroxine 25 mcg daily, increase by 25 mcg every 4 weeks",
            "C": "Levothyroxine 50 mcg daily",
            "D": "Levothyroxine 1.6 mcg/kg daily"
        },
        "correct_answer": "B",
        "explanation": "In patients with cardiac disease (IHD, angina, heart failure), start levothyroxine at LOW dose (25 mcg daily) and titrate slowly (increase by 25 mcg every 3-4 weeks) to avoid precipitating angina, arrhythmias, or MI. Rapid replacement increases cardiac oxygen demand. Young, healthy patients can start at full replacement dose (1.6 mcg/kg = ~100-125 mcg). Elderly patients without cardiac disease: start 50 mcg. Check TSH 6-8 weeks after each dose change. Target TSH: 0.5-2.5 mIU/L in most patients. Once stable, check TSH annually. Patient should be warned about cardiac symptoms and told to seek review if chest pain develops."
    },

    "ENDO-MCQ-0018": {
        "subtopic": "Subclinical Hypothyroidism",
        "scenario": "A 50-year-old asymptomatic woman has routine blood tests showing TSH 6.2 mIU/L (reference 0.5-4.0) with normal free T4 16 pmol/L. She has no symptoms of hypothyroidism. Anti-TPO antibodies are positive. She has no other medical conditions and is not trying to conceive.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Start levothyroxine 50 mcg daily immediately",
            "B": "Reassure and repeat TSH in 3 months",
            "C": "Start levothyroxine only if TSH >10 mIU/L on repeat testing",
            "D": "No treatment needed - reassure and discharge"
        },
        "correct_answer": "B",
        "explanation": "This is subclinical hypothyroidism (elevated TSH with normal free T4). Management depends on TSH level, symptoms, and risk factors. For TSH 4-10 mIU/L: (1) Repeat in 3 months to confirm (exclude transient causes); (2) Consider treatment if: TSH persistently >10 mIU/L, symptomatic, positive antibodies with progressively rising TSH, pregnancy/trying to conceive, or cardiovascular risk factors. Positive anti-TPO suggests Hashimoto's and increased risk of progression (4-5% per year). If TSH remains 6-10 mIU/L and asymptomatic, trial of levothyroxine may be considered or ongoing monitoring (repeat TSH 6-12 monthly). Immediate treatment not indicated without confirmation of persistent elevation."
    },

    "ENDO-MCQ-0019": {
        "subtopic": "Myxoedema Coma",
        "scenario": "An 80-year-old woman is brought to ED in winter, found confused at home. Temperature is 32°C, GCS 10/15, BP 90/60 mmHg, HR 45 bpm, RR 8/min with shallow breathing. She has non-pitting oedema, very dry skin, and delayed tendon reflexes. Her daughter reports she stopped taking 'thyroid tablets' months ago. Blood gas shows pH 7.25, pCO2 65 mmHg, pO2 55 mmHg.",
        "stem": "What is the most appropriate immediate management?",
        "options": {
            "A": "Levothyroxine 100 mcg oral daily only",
            "B": "Levothyroxine 200-400 mcg IV loading dose, hydrocortisone 100 mg IV, supportive care including ventilation",
            "C": "Urgent haemodialysis for metabolic acidosis",
            "D": "Passive rewarming only, delay levothyroxine until thyroid function results available"
        },
        "correct_answer": "B",
        "explanation": "This is myxoedema coma, an endocrine emergency (mortality 20-50%). Features: profound hypothermia, reduced consciousness, hypoventilation (CO2 retention), hypotension, bradycardia, hyponatraemia. Immediate management: (1) Levothyroxine IV loading dose 200-400 mcg (some add liothyronine); (2) Hydrocortisone 100 mg IV (treat possible adrenal insufficiency); (3) Supportive care (warming, mechanical ventilation, IV fluids, vasopressors if needed); (4) Treat precipitants (infection, MI, cold exposure). Do NOT wait for thyroid results - this is a clinical diagnosis requiring immediate treatment. Oral levothyroxine is inadequate. Active rewarming may cause vasodilation and worsen hypotension. Requires ICU admission."
    },

    "ENDO-MCQ-0020": {
        "subtopic": "Hashimoto's Thyroiditis",
        "scenario": "A 35-year-old woman presents with a painless, diffusely enlarged thyroid gland. She reports fatigue and weight gain. Thyroid function shows TSH 45 mIU/L and free T4 5 pmol/L. Anti-TPO antibodies are strongly positive (>1000 IU/mL). Ultrasound shows a diffusely enlarged, heterogeneous hypoechoic thyroid.",
        "stem": "What is the most likely diagnosis and appropriate initial treatment?",
        "options": {
            "A": "Subacute thyroiditis - NSAIDs and observation",
            "B": "Hashimoto's thyroiditis - levothyroxine replacement",
            "C": "Thyroid lymphoma - urgent biopsy",
            "D": "Riedel's thyroiditis - corticosteroids"
        },
        "correct_answer": "B",
        "explanation": "This is Hashimoto's thyroiditis (chronic autoimmune thyroiditis), the most common cause of hypothyroidism in iodine-sufficient areas. Key features: (1) Diffuse painless goitre; (2) Primary hypothyroidism (high TSH, low T4); (3) Positive anti-TPO antibodies (90%) and/or anti-thyroglobulin (80%); (4) Ultrasound shows heterogeneous hypoechoic gland. Treatment is levothyroxine replacement (starting dose depends on age/cardiac status). The goitre may shrink with treatment. Screen for other autoimmune conditions (type 1 diabetes, coeliac disease, Addison's disease). Subacute thyroiditis is painful and typically follows viral illness. Thyroid lymphoma presents with rapidly enlarging hard mass. Riedel's is rare, presents with rock-hard fixed thyroid."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 3 UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 3: ENDO-MCQ-0011 to 0020")
    print(f"  - Hyperthyroidism (5): Post-partum, Sick euthyroid, Nodules, Cancer, Interactions")
    print(f"  - Hypothyroidism (5): Diagnosis, Dosing, Subclinical, Myxoedema, Hashimoto's")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch3_generated)

    print(f"\n✅ Batch 3 Complete: {updated}/10 MCQs updated")
    print(f"✅ Total Progress: 20/658 MCQs (3.0%)")
    print(f"\nNext: Batch 4 (ENDO-MCQ-0021 to 0030 - DKA)")
