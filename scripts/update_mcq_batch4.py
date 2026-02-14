#!/usr/bin/env python3
"""
Update MCQ Batch 4 - ENDO-MCQ-0021 to 0030
Claude Code Generated Content - Hypothyroidism (advanced topics)
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


# Batch 4: ENDO-MCQ-0021 to 0030
batch4_generated = {
    "ENDO-MCQ-0021": {
        "subtopic": "Hypothyroidism in Pregnancy - Management",
        "scenario": "A 28-year-old woman with known hypothyroidism (on levothyroxine 100 mcg daily) presents at 6 weeks gestation for antenatal booking. Her pre-pregnancy TSH was 2.1 mIU/L (reference range 0.4-4.0). She asks about her thyroid medication during pregnancy. She is well with no symptoms.",
        "stem": "What is the most appropriate management of her levothyroxine therapy?",
        "options": {
            "A": "Continue current dose and check TSH at 12 weeks",
            "B": "Increase levothyroxine dose by 30% immediately and check TSH in 4 weeks",
            "C": "Cease levothyroxine as pregnancy increases thyroid hormone levels",
            "D": "Switch to liothyronine (T3) for pregnancy"
        },
        "correct_answer": "B",
        "explanation": "In pregnancy, levothyroxine requirements increase by 30-50% due to increased thyroxine-binding globulin, increased thyroid hormone metabolism, and fetal thyroid hormone requirements. Women with hypothyroidism should increase their dose by 30% as soon as pregnancy is confirmed (or 2 extra doses per week). Target TSH in pregnancy is lower: <2.5 mIU/L in first trimester, <3.0 mIU/L in second/third trimesters. Untreated or undertreated hypothyroidism in pregnancy risks maternal complications and fetal neurodevelopmental impairment. TSH should be checked every 4 weeks in first half of pregnancy, then at 30 weeks. After delivery, return to pre-pregnancy dose."
    },

    "ENDO-MCQ-0022": {
        "subtopic": "Central vs Primary Hypothyroidism",
        "scenario": "A 45-year-old woman presents with 6 months of fatigue, weight gain, and cold intolerance. Blood tests show TSH 1.8 mIU/L (reference range 0.4-4.0) and free T4 8 pmol/L (reference range 10-20). She also reports headaches and oligomenorrhoea. On examination, she has delayed relaxation of reflexes and mild periorbital oedema.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Primary hypothyroidism with assay interference",
            "B": "Subclinical hypothyroidism",
            "C": "Central (secondary) hypothyroidism",
            "D": "Euthyroid sick syndrome"
        },
        "correct_answer": "C",
        "explanation": "This patient has central (secondary or tertiary) hypothyroidism, caused by pituitary or hypothalamic dysfunction. Key features: (1) Low free T4 with inappropriately normal or low TSH (not elevated as in primary hypothyroidism); (2) Clinical hypothyroid symptoms; (3) Other features suggesting pituitary disease (headaches, menstrual disturbance). In primary hypothyroidism, TSH would be elevated (>4 mIU/L). Investigation should include pituitary MRI and assessment of other pituitary hormones (cortisol, prolactin, LH/FSH, IGF-1). Treatment is levothyroxine replacement, but must assess/treat adrenal insufficiency first if present, as thyroid hormone replacement can precipitate adrenal crisis."
    },

    "ENDO-MCQ-0023": {
        "subtopic": "Levothyroxine Absorption - Timing and Interactions",
        "scenario": "A 55-year-old woman with primary hypothyroidism has been taking levothyroxine 125 mcg daily for 5 years with good control (TSH 1.8 mIU/L). She now presents with TSH 8.5 mIU/L despite reporting good medication adherence. Review of her medications shows she recently started taking calcium carbonate 600 mg twice daily for osteoporosis prevention, which she takes with breakfast along with her levothyroxine.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Increase levothyroxine dose to 150 mcg daily",
            "B": "Advise taking levothyroxine 30-60 minutes before breakfast and calcium at least 4 hours apart",
            "C": "Switch to liothyronine (T3) therapy",
            "D": "Check for anti-TPO antibodies to assess disease progression"
        },
        "correct_answer": "B",
        "explanation": "Levothyroxine absorption is impaired by calcium supplements (also iron, proton pump inhibitors, aluminium antacids, bile acid sequestrants). Optimal levothyroxine absorption occurs on an empty stomach. Best practice: take levothyroxine 30-60 minutes before breakfast (or at bedtime at least 4 hours after evening meal), and separate from interfering medications by at least 4 hours. In this case, the calcium supplement is likely causing malabsorption. Correct timing will likely restore TSH to therapeutic range without dose increase. Other factors affecting absorption: coeliac disease, H. pylori, atrophic gastritis, inflammatory bowel disease. Simply increasing dose doesn't address the underlying absorption issue."
    },

    "ENDO-MCQ-0024": {
        "subtopic": "Hypothyroidism and Cardiovascular Risk",
        "scenario": "A 62-year-old man is found to have primary hypothyroidism on routine screening (TSH 18 mIU/L, free T4 7 pmol/L). He is asymptomatic but has hyperlipidaemia (total cholesterol 7.2 mmol/L, LDL 4.8 mmol/L). He has no cardiac history. His GP is considering starting a statin.",
        "stem": "What is the most appropriate initial management?",
        "options": {
            "A": "Start statin immediately and commence levothyroxine",
            "B": "Start levothyroxine and recheck lipids in 3 months before deciding on statin",
            "C": "Treat with levothyroxine only, as statins are contraindicated in hypothyroidism",
            "D": "Start dietary modification and delay levothyroxine until cholesterol improves"
        },
        "correct_answer": "B",
        "explanation": "Hypothyroidism commonly causes secondary hyperlipidaemia (elevated total cholesterol and LDL). Treatment of hypothyroidism with levothyroxine often improves or normalizes lipid levels within 2-3 months. Therefore, check fasting lipids after achieving euthyroid state before starting lipid-lowering therapy. Many patients will not require statins once thyroid function is corrected. Starting both simultaneously makes it difficult to assess the contribution of thyroid replacement. However, if the patient has established cardiovascular disease or very high cardiovascular risk, concurrent statin therapy may be appropriate. Statins are not contraindicated in hypothyroidism but myopathy risk may be slightly increased."
    },

    "ENDO-MCQ-0025": {
        "subtopic": "Drug-Induced Hypothyroidism - Lithium",
        "scenario": "A 38-year-old woman with bipolar disorder (stable on lithium carbonate for 3 years) presents with lethargy and weight gain over the past 4 months. Blood tests show TSH 12.5 mIU/L, free T4 9 pmol/L, and therapeutic lithium level. Her psychiatrist reports she is psychiatrically stable with good response to lithium.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Stop lithium and switch to sodium valproate",
            "B": "Reduce lithium dose by 50%",
            "C": "Start levothyroxine and continue lithium",
            "D": "Start carbimazole to balance lithium's thyroid effects"
        },
        "correct_answer": "C",
        "explanation": "Lithium commonly causes hypothyroidism (up to 20% of patients) by inhibiting thyroid hormone synthesis and release. Management: (1) Continue lithium if providing good psychiatric control - the psychiatric benefits usually outweigh the thyroid side effects; (2) Start levothyroxine replacement for hypothyroidism; (3) Monitor TSH every 3-6 months. Stopping or reducing lithium risks psychiatric relapse in a stable patient. Hypothyroidism is easily managed with replacement therapy. Patients on lithium should have thyroid function monitored at baseline, 6 months, then annually (or if symptoms develop). Other lithium-related endocrine effects include nephrogenic diabetes insipidus and hyperparathyroidism."
    },

    "ENDO-MCQ-0026": {
        "subtopic": "Congenital Hypothyroidism Screening",
        "scenario": "A newborn baby boy is noted to have a positive newborn screening test for congenital hypothyroidism at day 3 of life. The GP receives the result on day 7. The baby is breastfeeding well and appears well on examination. Parents are concerned about the implications.",
        "stem": "What is the most urgent management step?",
        "options": {
            "A": "Reassure parents and repeat screening test in 2 weeks",
            "B": "Urgent paediatric endocrinology referral and immediate confirmatory TSH/free T4 testing (same day)",
            "C": "Start levothyroxine 25 mcg daily and follow up in 4 weeks",
            "D": "Order thyroid ultrasound before any treatment"
        },
        "correct_answer": "B",
        "explanation": "Congenital hypothyroidism is a paediatric emergency requiring urgent confirmation and treatment. Delayed treatment (even by weeks) can result in permanent intellectual disability. Management: (1) Urgent confirmatory serum TSH and free T4 (same day as notification); (2) Immediate paediatric endocrinology referral; (3) If confirmed, start levothyroxine immediately (typically 10-15 mcg/kg/day for infants); (4) Do NOT wait for imaging before starting treatment. Newborn screening is highly sensitive but false positives occur, hence need for urgent confirmation. Once confirmed, treatment must start within first 2 weeks of life to prevent neurodevelopmental impairment. Later investigations (thyroid scan, ultrasound) can identify the cause (dysgenesis, dyshormonogenesis) but should not delay treatment."
    },

    "ENDO-MCQ-0027": {
        "subtopic": "Subclinical Hypothyroidism in Pregnancy",
        "scenario": "A 32-year-old woman at 10 weeks gestation has routine antenatal bloods showing TSH 4.2 mIU/L (reference range 0.4-4.0, pregnancy target <2.5) with free T4 15 pmol/L (normal range). She is asymptomatic. Anti-TPO antibodies are positive. She has no history of thyroid disease.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Reassure and monitor TSH in third trimester",
            "B": "Start levothyroxine 50 mcg daily and recheck TSH in 4 weeks",
            "C": "Wait until TSH rises above 10 mIU/L before treating",
            "D": "Refer to endocrinology as pregnancy is a contraindication to thyroid treatment"
        },
        "correct_answer": "B",
        "explanation": "This is subclinical hypothyroidism in pregnancy (elevated TSH, normal free T4) with positive thyroid antibodies. Treatment is indicated because: (1) Pregnancy TSH targets are lower than non-pregnant (<2.5 in T1, <3.0 in T2/T3); (2) Positive anti-TPO antibodies increase risk of progression to overt hypothyroidism and adverse pregnancy outcomes; (3) Untreated subclinical hypothyroidism with positive antibodies is associated with increased risk of miscarriage, preterm birth, and potential neurodevelopmental effects. Start levothyroxine 50 mcg daily, aiming for TSH <2.5 mIU/L. Recheck TSH every 4 weeks until stable, then at 30 weeks. After delivery, levothyroxine may be ceased or dose-reduced with TSH monitoring, as many women with subclinical hypothyroidism in pregnancy revert to normal thyroid function postpartum."
    },

    "ENDO-MCQ-0028": {
        "subtopic": "TSH Monitoring and Dose Titration",
        "scenario": "A 48-year-old woman was started on levothyroxine 50 mcg daily for primary hypothyroidism 8 weeks ago (initial TSH 32 mIU/L). She returns for follow-up feeling much better. Repeat blood tests show TSH 15 mIU/L and free T4 12 pmol/L (reference range 10-20).",
        "stem": "What is the most appropriate next step in management?",
        "options": {
            "A": "Continue current dose and recheck TSH in 6 months",
            "B": "Increase levothyroxine to 75 mcg daily and recheck TSH in 6-8 weeks",
            "C": "Increase levothyroxine to 100 mcg daily immediately for faster control",
            "D": "Add liothyronine (T3) 10 mcg twice daily to the regimen"
        },
        "correct_answer": "B",
        "explanation": "Levothyroxine dose should be titrated gradually to avoid over-treatment and achieve target TSH (typically 0.5-2.5 mIU/L, or normal reference range). TSH is still elevated at 15 mIU/L despite symptomatic improvement, indicating under-replacement. Management: (1) Increase dose by 25 mcg increments (50 to 75 mcg); (2) Recheck TSH 6-8 weeks after each dose change (TSH takes ~6 weeks to stabilize after dose adjustment); (3) Continue titrating until TSH in target range. Typical maintenance dose is 1.6 mcg/kg/day (~100-150 mcg for average adult). Avoid aggressive dose increases, especially in elderly or cardiac patients, as this can precipitate angina or arrhythmias. T3 (liothyronine) is not routinely used and reserved for rare cases of incomplete symptom resolution despite optimal TSH on T4 monotherapy."
    },

    "ENDO-MCQ-0029": {
        "subtopic": "Hypothyroidism in Elderly - Atypical Presentation",
        "scenario": "A 78-year-old man presents to ED with gradual onset confusion, constipation, and decreased mobility over 3 weeks. His family reports he has 'slowed down' and seems depressed. Temperature is 35.2°C, heart rate 48 bpm, blood pressure 140/85 mmHg. On examination, he has delayed relaxation of ankle reflexes, dry skin, and periorbital oedema. Blood tests show TSH 85 mIU/L, free T4 4 pmol/L, sodium 128 mmol/L.",
        "stem": "What is the most appropriate immediate management?",
        "options": {
            "A": "Start levothyroxine 100 mcg daily immediately for rapid correction",
            "B": "Hospital admission, start low-dose levothyroxine (25 mcg daily), IV T3 if available, supportive care, and assess adrenal function",
            "C": "Commence thyroid hormone replacement after correcting hyponatraemia with hypertonic saline",
            "D": "Arrange urgent thyroidectomy as the cause of severe hypothyroidism"
        },
        "correct_answer": "B",
        "explanation": "This patient has myxoedema coma, a life-threatening endocrine emergency (mortality 20-50%). Features: severe hypothyroidism with altered mental status, hypothermia, bradycardia, hyponatraemia, hypotension, hypoglycaemia. Management: (1) Hospital admission (ideally ICU); (2) Supportive care (warming, fluids, treat precipitants); (3) Thyroid hormone replacement - IV levothyroxine (loading dose then daily) or combination IV T3 + T4 (T3 preferred if available due to faster onset); (4) Hydrocortisone 100 mg IV (treat possible concomitant adrenal insufficiency before thyroid replacement); (5) Treat hyponatraemia cautiously (water restriction, avoid rapid correction). In elderly or cardiac patients, usual practice is low-dose levothyroxine (25 mcg starting dose), but myxoedema coma requires higher doses and more aggressive treatment. Identify and treat precipitants (infection, cold exposure, medications)."
    },

    "ENDO-MCQ-0030": {
        "subtopic": "Hypothyroidism and Coeliac Disease",
        "scenario": "A 35-year-old woman with coeliac disease (diagnosed 3 years ago, on gluten-free diet) is commenced on levothyroxine 100 mcg daily for newly diagnosed hypothyroidism (TSH 22 mIU/L). After 12 weeks, her TSH remains elevated at 18 mIU/L despite reporting excellent medication adherence. She takes her levothyroxine first thing in the morning on an empty stomach with no other medications.",
        "stem": "What is the most likely explanation for inadequate response to levothyroxine?",
        "options": {
            "A": "Levothyroxine dose is too low - increase to 150 mcg daily",
            "B": "Poor adherence despite patient's report",
            "C": "Malabsorption due to ongoing enteropathy from coeliac disease",
            "D": "Development of levothyroxine resistance requiring switch to T3"
        },
        "correct_answer": "C",
        "explanation": "Coeliac disease commonly causes levothyroxine malabsorption due to enteropathy affecting the small bowel (levothyroxine is absorbed in jejunum/ileum). Even on a gluten-free diet, villous atrophy may persist. Management: (1) Assess coeliac disease control (anti-TTG, coeliac serology, ensure strict gluten-free diet adherence); (2) Consider dietitian review for inadvertent gluten exposure; (3) If enteropathy persists, may need higher levothyroxine doses or consideration of liquid/soft gel levothyroxine preparations (better absorbed); (4) Rarely, switch to IV/IM levothyroxine. Coeliac disease is associated with autoimmune hypothyroidism (Hashimoto's thyroiditis) - prevalence 4-8 times higher than general population. Other causes of malabsorption: atrophic gastritis, H. pylori, inflammatory bowel disease, medications (PPI, calcium, iron). Before increasing dose significantly, confirm malabsorption is the issue rather than non-adherence."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 4 UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 4: ENDO-MCQ-0021 to 0030 (Hypothyroidism - Advanced)")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch4_generated)

    print(f"\n✅ Batch 4 Complete: {updated}/10 MCQs updated")
    print(f"✅ Total Progress: 30/658 MCQs (4.6%)")
    print(f"\nNext: Continue with remaining 628 MCQs")
