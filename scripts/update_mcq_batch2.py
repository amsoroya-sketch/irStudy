#!/usr/bin/env python3
"""
Update MCQ Batch 2 - ENDO-MCQ-0004 to 0010
Claude Code Generated Content - Hyperthyroidism (varied scenarios)
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


# Batch 2: ENDO-MCQ-0004 to 0010
batch2_generated = {
    "ENDO-MCQ-0004": {
        "subtopic": "Thyroid Storm",
        "scenario": "A 52-year-old woman with known but poorly controlled Graves' disease presents to ED with fever (39.2°C), confusion, agitation, and profuse sweating. She had stopped taking her carbimazole 2 weeks ago. On examination, her heart rate is 145 bpm with atrial fibrillation, blood pressure is 160/95 mmHg, and she has a large goitre. She appears dehydrated and tremulous.",
        "stem": "What is the most appropriate immediate management?",
        "options": {
            "A": "Carbimazole 40 mg orally and propranolol 40 mg orally",
            "B": "Propylthiouracil 200 mg orally, propranolol 40 mg orally, hydrocortisone 100 mg IV, and supportive care",
            "C": "Urgent radioactive iodine ablation",
            "D": "Emergency thyroidectomy"
        },
        "correct_answer": "B",
        "explanation": "This patient has thyroid storm (thyrotoxic crisis), a life-threatening endocrine emergency. Management requires: (1) High-dose antithyroid medication - propylthiouracil is preferred as it blocks peripheral T4 to T3 conversion; (2) Beta-blockade (propranolol) for cardiovascular symptoms; (3) Corticosteroids (hydrocortisone) to block peripheral T4 conversion and treat potential relative adrenal insufficiency; (4) Supportive care (IV fluids, cooling, treatment of precipitating factors). Iodine can be given 1 hour after antithyroid drugs. This is a medical emergency requiring ICU admission. Surgery is not appropriate in the acute setting."
    },

    "ENDO-MCQ-0005": {
        "subtopic": "Subclinical Hyperthyroidism",
        "scenario": "A 68-year-old woman is found to have a suppressed TSH of <0.1 mIU/L on routine blood tests. Free T4 and T3 levels are within normal range. She is asymptomatic with no palpitations, weight loss, or tremor. She has a history of osteoporosis and atrial fibrillation (on warfarin). On examination, pulse is 72 bpm and regular, with no goitre palpable.",
        "stem": "What is the most appropriate next step in management?",
        "options": {
            "A": "Reassure and repeat thyroid function tests in 6 months",
            "B": "Start carbimazole 10 mg daily",
            "C": "Arrange thyroid ultrasound and repeat TFTs in 3 months",
            "D": "Refer for radioactive iodine ablation"
        },
        "correct_answer": "C",
        "explanation": "This patient has subclinical hyperthyroidism (suppressed TSH with normal free T4/T3). Given her risk factors (age >65, osteoporosis, atrial fibrillation), treatment may be beneficial. However, first steps are to: (1) Exclude non-thyroidal causes (medications, recent illness); (2) Repeat TFTs in 3 months to confirm persistence; (3) Investigate the cause with thyroid ultrasound. Persistent subclinical hyperthyroidism in patients with risk factors (AF, osteoporosis, cardiac disease, age >65) warrants treatment. Immediate treatment is not indicated without confirming persistence and identifying the cause."
    },

    "ENDO-MCQ-0006": {
        "subtopic": "Toxic Multinodular Goitre",
        "scenario": "A 65-year-old man presents with a 6-month history of weight loss, palpitations, and heat intolerance. On examination, he has a large, irregular, multinodular goitre. Thyroid function tests show TSH <0.01 mIU/L and free T4 32 pmol/L. Thyroid autoantibodies (TSH receptor antibodies and anti-TPO) are negative. A thyroid uptake scan shows multiple areas of increased and decreased uptake.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Graves' disease",
            "B": "Toxic multinodular goitre",
            "C": "Thyroiditis",
            "D": "Factitious hyperthyroidism"
        },
        "correct_answer": "B",
        "explanation": "This patient has toxic multinodular goitre (Plummer's disease). Key features distinguishing it from Graves' disease are: (1) Older age (typically >50 years vs younger in Graves'); (2) Multinodular goitre on examination; (3) Negative TSH receptor antibodies; (4) Patchy uptake on scan (vs diffuse increased uptake in Graves'). Thyroiditis typically presents with painful/tender thyroid and biphasic pattern. Factitious hyperthyroidism would show low/absent uptake on scan. Treatment options include radioactive iodine (first-line if no compressive symptoms) or surgery if large goitre with compression."
    },

    "ENDO-MCQ-0007": {
        "subtopic": "Solitary Toxic Adenoma",
        "scenario": "A 42-year-old woman presents with symptoms of hyperthyroidism. Examination reveals a 3 cm smooth, mobile nodule in the right thyroid lobe. TSH is suppressed at <0.01 mIU/L, free T4 is 28 pmol/L. Thyroid uptake scan shows a single 'hot' nodule in the right lobe with suppression of the remaining thyroid tissue.",
        "stem": "What is the most appropriate definitive treatment?",
        "options": {
            "A": "Long-term carbimazole therapy",
            "B": "Radioactive iodine ablation",
            "C": "Thyroid lobectomy",
            "D": "Total thyroidectomy"
        },
        "correct_answer": "B",
        "explanation": "This patient has a solitary toxic adenoma (autonomous functioning nodule). Definitive treatment options are radioactive iodine ablation or surgery (hemithyroidectomy/lobectomy). Radioactive iodine is generally preferred as it is non-invasive, highly effective (90% cure rate), and the 'cold' suppressed tissue protects against whole gland ablation. Surgery (thyroid lobectomy) is appropriate if patient preference, large nodule (>4 cm), or contraindications to RAI. Total thyroidectomy is unnecessary. Long-term antithyroid drugs are not curative and inappropriate for solitary toxic adenoma - definitive treatment is required."
    },

    "ENDO-MCQ-0008": {
        "subtopic": "Amiodarone-Induced Thyrotoxicosis",
        "scenario": "A 70-year-old man with chronic atrial fibrillation on amiodarone 200 mg daily for 18 months presents with weight loss and palpitations. Thyroid function shows TSH <0.01 mIU/L and free T4 38 pmol/L. He has no previous thyroid disease. Thyroid is non-tender and not enlarged. Thyroid uptake scan shows low uptake.",
        "stem": "What is the most appropriate initial management?",
        "options": {
            "A": "Stop amiodarone immediately and start carbimazole",
            "B": "Continue amiodarone, start prednisolone 40 mg daily",
            "C": "Continue amiodarone, start carbimazole 40 mg daily",
            "D": "Stop amiodarone and monitor thyroid function"
        },
        "correct_answer": "B",
        "explanation": "This is amiodarone-induced thyrotoxicosis type 2 (AIT-2) - destructive thyroiditis causing thyroid hormone release, indicated by low uptake on scan. Type 1 (iodine-induced hyperthyroidism) shows normal/high uptake. For AIT-2: (1) Continue amiodarone if treating life-threatening arrhythmia (stop only if possible); (2) Start corticosteroids (prednisolone 40 mg daily for 1-3 months). Antithyroid drugs (carbimazole) are not effective in AIT-2 as it's destructive not hyperfunctioning. If type uncertain, combination therapy (carbimazole + prednisolone) may be used. Cardiology consultation is essential for arrhythmia management."
    },

    "ENDO-MCQ-0009": {
        "subtopic": "Hyperthyroidism in Pregnancy",
        "scenario": "A 26-year-old woman at 8 weeks gestation presents with hyperemesis gravidarum. Blood tests show TSH <0.01 mIU/L, free T4 26 pmol/L, and negative TSH receptor antibodies. Beta-hCG is elevated at 180,000 IU/L. She has no goitre and no previous thyroid disease. Symptoms improve with antiemetics and IV fluids.",
        "stem": "What is the most appropriate management of her thyroid status?",
        "options": {
            "A": "Start propylthiouracil immediately",
            "B": "Start carbimazole 20 mg daily",
            "C": "Reassure and repeat thyroid function in 4 weeks",
            "D": "Urgent endocrinology referral for radioactive iodine"
        },
        "correct_answer": "C",
        "explanation": "This is gestational transient thyrotoxicosis (GTT), caused by hCG-mediated thyroid stimulation in early pregnancy (hCG has weak TSH-like activity). Key features: (1) First trimester; (2) Associated with hyperemesis gravidarum; (3) Negative TSH receptor antibodies (excludes Graves'); (4) Self-limiting (resolves by 14-18 weeks). Management is supportive - antiemetics, IV fluids, beta-blockers if needed for symptoms. Antithyroid drugs are NOT indicated as it's self-limiting and medications carry fetal risks. Repeat TFTs in 4 weeks to confirm resolution. If TSH receptor antibodies positive or thyrotoxicosis persists beyond 18 weeks, consider Graves' disease and may need propylthiouracil (preferred in first trimester over carbimazole due to lower teratogenic risk)."
    },

    "ENDO-MCQ-0010": {
        "subtopic": "Graves' Ophthalmopathy",
        "scenario": "A 35-year-old woman with recently diagnosed Graves' disease (on carbimazole 30 mg daily) presents with worsening eye symptoms. She reports grittiness, excessive tearing, and her partner has noticed her eyes appear more prominent. On examination, she has bilateral proptosis, lid retraction, and conjunctival injection. Visual acuity is normal and she has full extraocular movements.",
        "stem": "What is the most appropriate initial management for her eye disease?",
        "options": {
            "A": "Increase carbimazole dose to 40 mg daily",
            "B": "Urgent orbital decompression surgery",
            "C": "Artificial tears, smoking cessation advice, and ophthalmology referral",
            "D": "Immediate high-dose IV methylprednisolone"
        },
        "correct_answer": "C",
        "explanation": "This patient has mild-moderate Graves' ophthalmopathy (GO). Initial management for mild GO includes: (1) Artificial tears/lubricants for symptom relief; (2) Smoking cessation (smoking worsens GO); (3) Optimize thyroid control (achieve euthyroid state); (4) Ophthalmology referral for monitoring and assessment. Severe sight-threatening GO (optic neuropathy, severe proptosis with exposure keratopathy) requires urgent high-dose IV corticosteroids. Orbital decompression is reserved for severe cases or compressive optic neuropathy not responding to medical therapy. Radioactive iodine can worsen GO and may be relatively contraindicated. Selenium supplementation may provide mild benefit in mild GO."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 2 UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 2: ENDO-MCQ-0004 to 0010 (Hyperthyroidism - Varied)")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch2_generated)

    print(f"\n✅ Batch 2 Complete: {updated}/7 MCQs updated")
    print(f"✅ Total Progress: 10/658 MCQs (1.5%)")
    print(f"\nNext: Continue with remaining 648 MCQs (different topics)")
