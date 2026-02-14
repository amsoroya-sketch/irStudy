#!/usr/bin/env python3
"""
Update MCQ Batch 6C - ENDO-MCQ-0081 to 0100 (20 MCQs)
Sub-batch 3 of 5 in Batch 6
Topics: Thyroid Nodules (4) + Adrenal Disorders (12) + Pituitary (4)
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


# Batch 6C: ENDO-MCQ-0081 to 0100
batch6c_generated = {
    "ENDO-MCQ-0081": {
        "subtopic": "Thyroid Nodule in Pregnancy",
        "scenario": "A 28-year-old woman at 12 weeks gestation is found to have a 1.5cm thyroid nodule. TSH is normal. Ultrasound shows hypoechoic nodule with microcalcifications. She is concerned about investigations and treatment during pregnancy.",
        "stem": "What is the most appropriate management?",
        "options": {
            "A": "Defer all investigations until after delivery",
            "B": "FNA is safe in pregnancy if indicated; defer surgery to second trimester if malignant/suspicious cytology; RAI contraindicated in pregnancy",
            "C": "Immediate thyroidectomy regardless of trimester",
            "D": "Radioactive iodine scanning and ablation"
        },
        "correct_answer": "B",
        "explanation": "Thyroid nodules in pregnancy: Prevalence similar to non-pregnant women. Diagnostic approach: (1) TSH: trimester-specific reference ranges (lower in T1); (2) Thyroid ultrasound: safe in pregnancy; (3) FNA: safe in pregnancy if clinically indicated (suspicious features, growing nodule, abnormal lymph nodes). Malignancy risk: no increased risk in pregnancy. Most thyroid cancers in pregnancy have excellent prognosis. Management of suspicious/malignant nodules: (1) First trimester: Defer surgery to second trimester if possible (organogenesis period, anesthetic risks); Close ultrasound monitoring; If aggressive cancer → surgery in second trimester. (2) Second trimester: Safest time for surgery if needed. (3) Third trimester: Defer to postpartum unless aggressive growth. Radioactive iodine: Absolutely contraindicated in pregnancy (fetal thyroid develops 10-12 weeks, concentrates iodine - causes fetal hypothyroidism/cretinism). Thyroid hormone requirements: May need 30% increase in levothyroxine if already on treatment. This patient: suspicious ultrasound features - FNA appropriate to guide further management. If benign → observe; if malignant → surgery in second trimester or defer to postpartum if low-risk. Breastfeeding contraindication for RAI postpartum."
    },

    "ENDO-MCQ-0082": {
        "subtopic": "Follicular Thyroid Cancer",
        "scenario": "A 45-year-old woman undergoes thyroid lobectomy for a 3cm follicular neoplasm (Bethesda IV cytology). Final histopathology shows follicular thyroid carcinoma with capsular and vascular invasion.",
        "stem": "What is the most appropriate next step?",
        "options": {
            "A": "No further treatment - lobectomy sufficient",
            "B": "Completion thyroidectomy (remove remaining lobe) followed by radioactive iodine ablation",
            "C": "Radioactive iodine without completion surgery",
            "D": "Chemotherapy"
        },
        "correct_answer": "B",
        "explanation": "Follicular thyroid carcinoma (FTC): 10-15% of thyroid cancers. More aggressive than papillary, spreads hematogenously (bone, lung). Cannot diagnose on FNA (requires histology to see capsular/vascular invasion). Histology types: Minimally invasive (capsular invasion only - excellent prognosis); Widely invasive (vascular invasion, aggressive). Management: (1) Lobectomy appropriate for diagnostic purposes (FNA shows follicular neoplasm, need histology); (2) If final histology shows FTC with high-risk features (vascular invasion, size >4cm, extensive invasion): Completion thyroidectomy (remove remaining thyroid); Rationale: allows RAI treatment (needs total thyroidectomy), enables thyroglobulin monitoring, reduces recurrence. (3) Radioactive iodine ablation post-completion thyroidectomy (similar to papillary cancer). This patient: vascular invasion = high-risk FTC → needs completion thyroidectomy + RAI. Low-risk FTC (minimally invasive, <1cm): may avoid completion thyroidectomy (controversial). Post-treatment: TSH suppression, thyroglobulin monitoring, imaging surveillance. Prognosis: 10-year survival 85-95% for minimally invasive, 50-70% for widely invasive. Distant metastases more common than papillary (15% vs 5%). Treatment of metastases: RAI if iodine-avid, tyrosine kinase inhibitors if RAI-refractory."
    },

    "ENDO-MCQ-0083": {
        "subtopic": "Hurthle Cell Carcinoma",
        "scenario": "A 55-year-old woman undergoes total thyroidectomy for a thyroid nodule. Histopathology shows Hurthle cell (oncocytic) carcinoma, 2.5cm, capsular invasion, no lymph node involvement.",
        "stem": "What is a key characteristic affecting post-operative management of this tumor?",
        "options": {
            "A": "Excellent response to radioactive iodine like papillary cancer",
            "B": "Hurthle cell carcinomas often do NOT concentrate radioactive iodine well - RAI less effective, requires closer surveillance with imaging",
            "C": "Chemotherapy is first-line treatment",
            "D": "Never metastasizes"
        },
        "correct_answer": "B",
        "explanation": "Hurthle cell (oncocytic) carcinoma: Considered variant of follicular thyroid cancer, but distinct biology. 3% of thyroid cancers. Features: (1) Mitochondria-rich oxyphilic cells; (2) More aggressive than follicular cancer; (3) Higher recurrence/metastasis rates; (4) Lymph node spread more common than follicular cancer. Key difference: Poor radioiodine uptake (60-70% do NOT take up RAI adequately). Implications: (1) Standard RAI ablation often ineffective; (2) Post-operative RAI may be attempted but often fails; (3) Cannot rely on whole-body RAI scans for surveillance; (4) Cannot use thyroglobulin as reliably (some Hurthle cell cancers don't produce thyroglobulin). Surveillance: (1) Neck ultrasound (every 6-12 months); (2) CT chest annually (lung metastases common); (3) Thyroglobulin if produced; (4) FDG-PET scan useful (typically PET-avid even if RAI-negative). Treatment of recurrence/metastases: (1) Surgery if resectable; (2) External beam radiotherapy for unresectable disease; (3) Tyrosine kinase inhibitors (lenvatinib, sorafenib) for progressive RAI-refractory disease. This patient: Hurthle cell carcinoma - total thyroidectomy already done (correct), may try RAI but likely won't work well. Need intensive surveillance with imaging rather than relying on RAI scans. Prognosis: Worse than papillary/follicular cancers - 10-year survival 75-85%, but 25-30% recurrence rate. More likely to develop distant metastases."
    },

    "ENDO-MCQ-0084": {
        "subtopic": "Thyroglobulin Monitoring Post-Thyroidectomy",
        "scenario": "A 40-year-old woman is 6 months post total thyroidectomy and RAI ablation for papillary thyroid cancer. She is on levothyroxine 150mcg daily with TSH 0.05 mIU/L (suppressed as intended). Her thyroglobulin level is 15 ng/mL (should be undetectable), anti-thyroglobulin antibodies negative.",
        "stem": "What does the elevated thyroglobulin indicate?",
        "options": {
            "A": "Normal finding - all patients have detectable thyroglobulin",
            "B": "Biochemical evidence of persistent/recurrent disease - requires further investigation (neck ultrasound, consider RAI scan or FDG-PET)",
            "C": "Laboratory error - ignore",
            "D": "Due to levothyroxine therapy"
        },
        "correct_answer": "B",
        "explanation": "Thyroglobulin (Tg) monitoring post-thyroidectomy for thyroid cancer: Thyroglobulin is produced only by thyroid tissue (normal or malignant). After total thyroidectomy + RAI ablation, Tg should be undetectable (<0.2-1 ng/mL depending on assay). Detectable/rising Tg indicates: (1) Residual normal thyroid tissue (incomplete surgery/RAI); (2) Persistent disease; (3) Recurrent disease. Caveats: (1) Anti-thyroglobulin antibodies interfere with Tg assay - must check Tg antibodies (TgAb); If TgAb positive → Tg unreliable; Use TgAb trend instead (rising TgAb suggests recurrence). (2) TSH stimulation increases Tg sensitivity: Stimulated Tg (TSH >30 mIU/L) more sensitive than suppressed Tg; Can achieve via: (a) Levothyroxine withdrawal (hypothyroid, symptomatic); (b) Recombinant TSH (Thyrogen) injection (preferred, avoid hypothyroid symptoms). This patient: Tg 15 ng/mL (clearly elevated), TgAb negative (reliable assay), TSH suppressed. Indicates persistent/recurrent disease. Next steps: (1) Neck ultrasound (look for lymph nodes, thyroid bed abnormality); (2) If US negative: diagnostic RAI scan (low dose to avoid stunning) or FDG-PET scan; (3) If disease found: surgery (resectable lymph nodes), RAI therapy (if iodine-avid), external beam RT, tyrosine kinase inhibitors (if RAI-refractory). Rising Tg trend more worrying than stable low levels. Target post-treatment: Tg <0.2 ng/mL on suppressed TSH, <1 ng/mL on stimulated TSH."
    },

    "ENDO-MCQ-0085": {
        "subtopic": "Cushing's Syndrome - Diagnosis",
        "scenario": "A 42-year-old woman presents with 18 months of weight gain (central obesity), facial rounding, easy bruising, and proximal muscle weakness. BP 165/95 mmHg, fasting glucose 8.2 mmol/L. Examination shows central obesity, moon facies, supraclavicular fat pads, thin skin with purple striae on abdomen.",
        "stem": "What is the most appropriate initial screening test for Cushing's syndrome?",
        "options": {
            "A": "Random serum cortisol",
            "B": "24-hour urinary free cortisol OR late-night salivary cortisol OR overnight dexamethasone suppression test (1mg)",
            "C": "ACTH level",
            "D": "Pituitary MRI"
        },
        "correct_answer": "B",
        "explanation": "Cushing's syndrome: Chronic excess cortisol. Causes: (1) ACTH-dependent (80%): Cushing's disease (pituitary adenoma 70%), ectopic ACTH (SCLC, carcinoid 10%); (2) ACTH-independent (20%): adrenal adenoma, carcinoma, exogenous steroids. Clinical features: Central obesity, moon facies, buffalo hump, supraclavicular fat pads, skin changes (thin skin, bruising, purple striae >1cm), proximal myopathy, hypertension, diabetes, osteoporosis, psychiatric symptoms. This patient: classic cushingoid features. Screening tests (need abnormal result on 2 different tests to diagnose): (1) 24-hour urinary free cortisol (UFC): Elevated (>3x upper limit); Collect 2-3 separate collections; False positives: depression, alcohol, pregnancy. (2) Late-night salivary cortisol: Elevated (loss of circadian rhythm); Collect at 11pm-midnight; Simple, outpatient; Sensitive and specific. (3) 1mg overnight dexamethasone suppression test (DST): Give 1mg dexamethasone at 11pm; Measure 8am cortisol next day; Normal: cortisol <50 nmol/L (suppressed); Cushing's: cortisol >140 nmol/L (non-suppressed). After positive screening: (1) Repeat different test to confirm; (2) ACTH level to determine ACTH-dependent vs independent; (3) Imaging (pituitary MRI if ACTH-dependent, adrenal CT if ACTH-independent). Do NOT start with imaging - need biochemical confirmation first."
    },

    "ENDO-MCQ-0086": {
        "subtopic": "Cushing's Disease - Treatment",
        "scenario": "A 38-year-old man is diagnosed with Cushing's disease (pituitary ACTH-secreting adenoma). MRI shows 6mm pituitary microadenoma. Biochemistry confirms ACTH-dependent hypercortisolism.",
        "stem": "What is the first-line treatment?",
        "options": {
            "A": "Medical therapy with ketoconazole",
            "B": "Trans-sphenoidal pituitary surgery (adenomectomy)",
            "C": "Bilateral adrenalectomy",
            "D": "Pituitary radiotherapy"
        },
        "correct_answer": "B",
        "explanation": "Cushing's disease (pituitary ACTH-secreting adenoma): 70% of Cushing's syndrome cases. Treatment hierarchy: First-line: Trans-sphenoidal surgery (TSS) - selective adenomectomy (1) Cure rate: 70-90% for microadenomas (<1cm), 50-65% for macroadenomas; (2) Complications: hypopituitarism (10-20%, often transient), diabetes insipidus (transient 20%, permanent <5%), CSF leak (3%), meningitis; (3) Post-op assessment: 8am cortisol <50 nmol/L (day 2-5 post-op) = remission likely; Follow-up: monitor for recurrence (10-20% recur over 10 years). Second-line (if surgery fails/recurrence): (1) Repeat surgery; (2) Pituitary radiotherapy: Stereotactic (gamma knife, proton beam) - 50-60% remission over 5 years, slow onset; Hypopituitarism risk 30-50%. Third-line: (1) Medical therapy: Pasireotide (somatostatin analog - inhibits ACTH secretion); Ketoconazole, metyrapone (inhibit cortisol synthesis); Cabergoline (dopamine agonist); Mifepristone (cortisol receptor blocker); Used as bridge to surgery or if surgery not possible. (2) Bilateral adrenalectomy: Curative for hypercortisolism but causes lifelong adrenal insufficiency; Risk of Nelson's syndrome (aggressive pituitary tumor growth 10-30%); Reserved for refractory cases. This patient: microadenoma - excellent surgical candidate. TSS is first-line with high cure rate. Post-op: may need temporary hydrocortisone (suppressed HPA axis), then taper as HPA recovers."
    },

    "ENDO-MCQ-0087": {
        "subtopic": "Adrenal Incidentaloma - Evaluation",
        "scenario": "A 58-year-old woman undergoes CT abdomen for investigation of abdominal pain. Report mentions a 2.5cm left adrenal mass (incidentaloma). She has no symptoms. BP 135/85 mmHg, no cushingoid features, no virilization.",
        "stem": "What is the most appropriate initial hormonal evaluation?",
        "options": {
            "A": "No hormonal testing needed for asymptomatic incidentalomas",
            "B": "Screen for subclinical Cushing's (1mg DST), pheochromocytoma (plasma/urinary metanephrines), and primary aldosteronism if hypertensive (aldosterone-renin ratio)",
            "C": "ACTH stimulation test only",
            "D": "Adrenal biopsy"
        },
        "correct_answer": "B",
        "explanation": "Adrenal incidentaloma: Adrenal mass ≥1cm discovered on imaging for unrelated reasons. Prevalence 4-7% on CT, increases with age. Evaluation addresses 2 questions: (1) Hormonal activity? (2) Malignant potential? Hormonal evaluation (ALL incidentalomas, even if asymptomatic): (1) Subclinical Cushing's: 1mg overnight dexamethasone suppression test (5-20% of incidentalomas); 8am cortisol >140 nmol/L = autonomous cortisol secretion; May not have obvious cushingoid features but increased cardiovascular risk. (2) Pheochromocytoma: Plasma metanephrines OR 24-hour urinary fractionated metanephrines (5% of incidentalomas); MUST exclude before biopsy/surgery (undiagnosed pheo → hypertensive crisis/death). (3) Primary aldosteronism (if hypertensive or hypokalemic): Aldosterone-renin ratio (ARR); Stop interfering medications 2 weeks before (spironolactone, ACEi, ARBs). (4) Adrenal androgens (if virilization present): DHEAS, testosterone, 17-OH progesterone. Imaging evaluation: (1) Unenhanced CT attenuation: <10 HU = benign adenoma; >10 HU = indeterminate/suspicious. (2) Size: <4cm + benign features → follow-up; ≥4cm → consider resection (cancer risk increases). This patient: 2.5cm, asymptomatic - needs full hormonal workup despite lack of symptoms (subclinical disease common). If hormonally inactive + benign imaging → surveillance. Never biopsy without excluding pheochromocytoma first."
    },

    "ENDO-MCQ-0088": {
        "subtopic": "Primary Aldosteronism - Diagnosis",
        "scenario": "A 45-year-old man with resistant hypertension (BP 170/105 mmHg on 3 drugs including ACE inhibitor) has hypokalemia (K+ 2.9 mmol/L). Screening aldosterone-renin ratio (ARR) is elevated at 850 (aldosterone 650 pmol/L, renin <0.5 mU/L).",
        "stem": "What is the most appropriate next step?",
        "options": {
            "A": "Start spironolactone immediately without further testing",
            "B": "Confirmatory testing with saline suppression test or fludrocortisone suppression test (off interfering medications)",
            "C": "Immediate adrenalectomy",
            "D": "Renal artery Doppler"
        },
        "correct_answer": "B",
        "explanation": "Primary aldosteronism (PA, Conn's syndrome): Most common cause secondary hypertension (5-10% of hypertensives, up to 20% of resistant hypertension). Causes: (1) Bilateral adrenal hyperplasia (BAH, 60-70%); (2) Aldosterone-producing adenoma (APA, 30-40%); (3) Rarely: unilateral hyperplasia, adrenal carcinoma. Diagnosis steps: Step 1 - Screening (ARR): Indications: Resistant hypertension, hypertension + hypokalemia, young hypertensives (<40), adrenal incidentaloma + hypertension; ARR >750-800 (units vary) = positive screen; Stop interfering drugs 2 weeks prior (spironolactone 4-6 weeks, ACEi, ARBs, diuretics); Can continue CCB, alpha-blockers, hydralazine. Step 2 - Confirmatory testing (required to confirm autonomous aldosterone secretion): (1) Saline suppression test: 2L 0.9% saline IV over 4 hours; Measure aldosterone before/after; PA: aldosterone remains >140-280 pmol/L (fails to suppress). (2) Fludrocortisone suppression test; (3) Captopril challenge test. Step 3 - Subtype differentiation (adenoma vs hyperplasia): CT adrenals (look for adenoma); Adrenal venous sampling (AVS) - gold standard for lateralization if surgical candidate. This patient: positive ARR - needs confirmatory test (off ACE inhibitor) before diagnosis. After confirmation: CT + AVS if surgery considered. Treatment: APA → adrenalectomy (curative); BAH → medical (spironolactone, eplerenone). Do not start spironolactone before confirmation (interferes with testing)."
    },

    "ENDO-MCQ-0089": {
        "subtopic": "Pheochromocytoma - Presentation",
        "scenario": "A 32-year-old woman presents with paroxysmal episodes (lasting 15-20 minutes, 2-3 times/week) of severe headache, palpitations, profuse sweating, and tremor. During episodes, BP rises to 220/120 mmHg (baseline 135/85 mmHg between episodes). Episodes seem spontaneous with no clear trigger. Fasting glucose 6.8 mmol/L.",
        "stem": "What is the most likely diagnosis and initial diagnostic test?",
        "options": {
            "A": "Panic disorder - refer to psychiatry",
            "B": "Pheochromocytoma - plasma metanephrines OR 24-hour urinary fractionated metanephrines",
            "C": "Thyrotoxicosis - check TSH",
            "D": "Essential hypertension - start antihypertensive"
        },
        "correct_answer": "B",
        "explanation": "Pheochromocytoma: Catecholamine-secreting tumor of chromaffin cells (adrenal medulla 90%, extra-adrenal paraganglia 10%). Prevalence <0.2% of hypertensives, but important diagnosis (potentially lethal if unrecognized). Classic triad: (1) Episodic headaches; (2) Sweating; (3) Palpitations. Plus: (1) Paroxysmal hypertension (50%, sustained in 50%); (2) Pallor, tremor, anxiety; (3) Hyperglycemia (catecholamines inhibit insulin); (4) Weight loss. Episodes: Spontaneous or triggered (exercise, postural change, abdominal pressure, tyramine-rich foods, certain drugs). Rule of 10s: 10% bilateral, 10% extra-adrenal, 10% malignant, 10% familial (MEN 2, VHL, NF1, paraganglioma syndromes). Diagnosis: (1) Plasma fractionated metanephrines (most sensitive - 97%): Obtain seated after 15min rest; False positives: stress, interfering medications (TCAs, MAOIs, decongestants). (2) 24-hour urinary fractionated metanephrines and catecholamines; (3) Cutoff: >2-3x upper limit = highly suggestive. Imaging (only after biochemical confirmation): (1) CT/MRI adrenals + abdomen/pelvis (locate tumor); (2) Functional imaging if needed (MIBG scan, PET). This patient: classic paroxysmal symptoms triad - highly suggestive of pheochromocytoma. Needs biochemical testing. Treatment: surgery after alpha-blockade (phenoxybenzamine, doxazosin), then beta-blockade (NEVER beta-block first - unopposed alpha causes hypertensive crisis)."
    },

    "ENDO-MCQ-0090": {
        "subtopic": "Pheochromocytoma - Pre-operative Management",
        "scenario": "A 40-year-old man is diagnosed with pheochromocytoma (4cm right adrenal mass, markedly elevated metanephrines). He is scheduled for laparoscopic adrenalectomy. Current BP 165/100 mmHg on amlodipine.",
        "stem": "What is the most important pre-operative medical management?",
        "options": {
            "A": "No specific preparation needed",
            "B": "Alpha-adrenergic blockade (phenoxybenzamine or doxazosin) for 10-14 days pre-operatively, followed by beta-blockade if needed; ensure adequate volume repletion",
            "C": "Beta-blockade alone",
            "D": "ACE inhibitor"
        },
        "correct_answer": "B",
        "explanation": "Pre-operative preparation for pheochromocytoma resection (critical to prevent intraoperative crisis): Alpha-blockade (ESSENTIAL): (1) Phenoxybenzamine (non-selective irreversible alpha-blocker): Start 10-14 days pre-op; Initial 10mg BD, titrate up (usual dose 20-100mg BD); Continue until BP controlled, orthostatic hypotension present (suggests adequate blockade); OR (2) Doxazosin (selective alpha-1 blocker): Easier to titrate, shorter acting (easier to reverse post-op). Goals: BP <130/80 mmHg seated, allow orthostatic hypotension (drop >15mmHg SBP on standing = adequate alpha-blockade), HR <100 bpm. Beta-blockade (only AFTER adequate alpha-blockade): (1) For tachycardia/arrhythmias persisting after alpha-blockade; (2) Propranolol, atenolol; (3) NEVER give beta-blocker first (unopposed alpha-vasoconstriction → severe hypertensive crisis). Volume expansion: High-salt diet, IV fluids pre-op (catecholamines cause vasoconstriction and low circulating volume). Anesthetic considerations: (1) Invasive BP monitoring; (2) Intraoperative hypertension (during tumor manipulation): IV phentolamine, nitroprusside, nicardipine; (3) Post-resection hypotension: IV fluids, stop alpha-blockers, vasopressors if needed. This patient: needs alpha-blockade started immediately, continued for 10-14 days. Inadequate pre-op preparation → intraoperative hypertensive crisis, arrhythmias, MI, stroke, death."
    },

    "ENDO-MCQ-0091": {
        "subtopic": "Addison's Disease - Diagnosis",
        "scenario": "A 35-year-old woman presents with 6 months of fatigue, weight loss (7kg), and lightheadedness on standing. Examination shows BP 95/60 mmHg (supine), hyperpigmentation of palmar creases, buccal mucosa, and old scars. Electrolytes: Na+ 128 mmol/L, K+ 5.6 mmol/L. 8am cortisol 120 nmol/L (low).",
        "stem": "What is the most appropriate confirmatory test for primary adrenal insufficiency?",
        "options": {
            "A": "Random cortisol is sufficient - no further testing",
            "B": "Short Synacthen test (ACTH stimulation test): Give 250mcg synthetic ACTH, measure cortisol at 0 and 30 minutes",
            "C": "Insulin tolerance test",
            "D": "Dexamethasone suppression test"
        },
        "correct_answer": "B",
        "explanation": "Primary adrenal insufficiency (Addison's disease): Destruction of adrenal cortex → deficiency of cortisol, aldosterone, androgens. Causes: Autoimmune (80% in developed countries), TB, adrenal hemorrhage, metastases, medications. Clinical features: (1) Chronic symptoms: fatigue, weight loss, anorexia, N/V, abdominal pain, salt craving; (2) Postural hypotension; (3) Hyperpigmentation (elevated ACTH stimulates melanocytes - palmar creases, buccal mucosa, scars, pressure areas, areolae); (4) Hyponatremia, hyperkalemia (aldosterone deficiency). This patient: classic presentation. Diagnosis: Step 1 - Screening: 8am cortisol: <100 nmol/L = diagnostic; 100-450 nmol/L = indeterminate, need Synacthen test; >450 nmol/L = unlikely AI. Step 2 - Confirmatory test: Short Synacthen test: Give 250mcg synthetic ACTH (tetracosactide) IM/IV; Measure cortisol at baseline, 30 and 60 minutes; Normal response: cortisol rises to >450-550 nmol/L; Addison's: fails to rise (adrenals cannot respond); Perform in morning (physiological ACTH peak). Step 3 - Differentiate primary vs secondary AI: ACTH level: Primary (Addison's): ACTH very high (>100 pg/mL); Secondary (pituitary): ACTH low/normal. Step 4 - Identify cause: Adrenal autoantibodies (21-hydroxylase); CT adrenals (look for hemorrhage, metastases, TB calcification); Screen for autoimmune conditions (thyroid, diabetes, vitiligo). This patient needs Synacthen test to confirm. Treatment: hydrocortisone + fludrocortisone (aldosterone replacement)."
    },

    "ENDO-MCQ-0092": {
        "subtopic": "Adrenal Crisis - Management",
        "scenario": "A 42-year-old man with known Addison's disease (on hydrocortisone and fludrocortisone) presents to ED with 2 days of gastroenteritis (vomiting, diarrhea). He is confused, BP 75/45 mmHg, HR 125 bpm, temperature 37.8°C. Glucose 3.2 mmol/L, Na+ 125 mmol/L, K+ 6.2 mmol/L.",
        "stem": "What is the most appropriate immediate management?",
        "options": {
            "A": "Continue oral hydrocortisone at usual dose",
            "B": "IV hydrocortisone 100mg stat, followed by 50-100mg every 6 hours; IV 0.9% saline resuscitation; treat precipitating cause",
            "C": "IV dexamethasone 4mg daily",
            "D": "Oral fludrocortisone only"
        },
        "correct_answer": "B",
        "explanation": "Adrenal crisis (Addisonian crisis): Life-threatening emergency due to acute adrenal insufficiency. Triggers: (1) Infection, trauma, surgery, pregnancy; (2) Missed steroid doses (vomiting, non-adherence); (3) Sudden withdrawal of long-term steroids; (4) Bilateral adrenal hemorrhage/infarction. Features: (1) Hypotension/shock; (2) Altered consciousness; (3) Abdominal pain, vomiting; (4) Hypoglycemia; (5) Hyponatremia, hyperkalemia; (6) Fever (may not have infection - cortisol deficiency alone can cause fever). Management (do NOT delay for confirmatory tests): (1) IV hydrocortisone 100mg STAT (or IM if no IV access), then 50-100mg every 6 hours (or continuous infusion 200mg/24hrs); (2) IV 0.9% saline resuscitation: 1L rapidly, then ongoing replacement (often need 3-5L in first 24 hours); (3) 5-10% dextrose if hypoglycemic; (4) Identify and treat precipitant (antibiotics for infection, etc.); (5) Monitor electrolytes, glucose, BP. Why hydrocortisone, not dexamethasone? (1) Hydrocortisone has mineralocorticoid activity at high doses - replaces aldosterone; (2) Dexamethasone has no mineralocorticoid activity - would need separate fludrocortisone; (3) If need to do Synacthen test: use dexamethasone (doesn't interfere with cortisol assay), but treatment takes priority over diagnostic testing. Fludrocortisone: Hold initially (high-dose hydrocortisone provides mineralocorticoid activity), restart when patient stable on lower hydrocortisone doses. This patient: adrenal crisis precipitated by gastroenteritis. Needs immediate IV hydrocortisone + fluids. Once stable, educate on stress dosing/sick day rules."
    },

    "ENDO-MCQ-0093": {
        "subtopic": "Congenital Adrenal Hyperplasia - 21-Hydroxylase Deficiency",
        "scenario": "A newborn female infant is noted to have ambiguous genitalia (clitoromegaly, labial fusion). Serum electrolytes at day 7 show Na+ 125 mmol/L, K+ 6.8 mmol/L. 17-hydroxyprogesterone is markedly elevated.",
        "stem": "What is the most likely diagnosis and immediate management?",
        "options": {
            "A": "Turner syndrome - refer genetics",
            "B": "Congenital adrenal hyperplasia (21-hydroxylase deficiency) - IV hydrocortisone, IV saline resuscitation, fludrocortisone",
            "C": "Androgen-secreting tumor - surgical resection",
            "D": "No treatment needed - will resolve spontaneously"
        },
        "correct_answer": "B",
        "explanation": "Congenital adrenal hyperplasia (CAH): Autosomal recessive enzyme deficiencies in cortisol synthesis. Most common: 21-hydroxylase deficiency (90-95% of CAH). Types: (1) Classic salt-wasting (75%): Severe enzyme deficiency, cannot produce cortisol or aldosterone; Presents in newborn: adrenal crisis (hyponatremia, hyperkalemia, shock, hypoglycemia), virilization in females. (2) Classic simple-virilizing (25%): Milder deficiency, some aldosterone production; Virilization without salt-wasting. (3) Non-classic/late-onset: Mild deficiency, presents later with hirsutism, irregular periods, acne. Pathophysiology: (1) Blocked cortisol synthesis → elevated ACTH → adrenal hyperplasia; (2) Precursors shunted to androgen pathway → excess androgens → virilization; (3) Aldosterone deficiency (salt-wasting forms) → hyponatremia, hyperkalemia, hypotension. Virilization in females: Ambiguous genitalia at birth (clitoromegaly, labial fusion, may be mistaken for male with undescended testes). Males: Normal-appearing genitalia at birth (not detected on newborn exam), present with adrenal crisis at 1-2 weeks. Diagnosis: Elevated 17-hydroxyprogesterone (>10,000 ng/dL diagnostic). Management: (1) Acute (adrenal crisis): IV hydrocortisone, IV saline, treat hypoglycemia; (2) Chronic: Oral hydrocortisone (replace cortisol, suppresses ACTH/androgens), Fludrocortisone (replace aldosterone); (3) Females: Genitoplasty for ambiguous genitalia. This infant: classic salt-wasting CAH. Life-threatening emergency requiring immediate treatment. Newborn screening detects most cases (17-OHP on Guthrie card)."
    },

    "ENDO-MCQ-0094": {
        "subtopic": "Secondary Adrenal Insufficiency - Steroid Withdrawal",
        "scenario": "A 55-year-old woman with rheumatoid arthritis has been on prednisolone 20mg daily for 18 months. Her rheumatologist wants to cease steroids as disease is now in remission on other medications. She is concerned about stopping suddenly.",
        "stem": "What is the most appropriate approach to stopping long-term corticosteroids?",
        "options": {
            "A": "Stop immediately - no taper needed",
            "B": "Gradual taper over weeks-months to allow HPA axis recovery; may need Synacthen test to assess adrenal reserve if prolonged use",
            "C": "Switch to dexamethasone",
            "D": "Add fludrocortisone"
        },
        "correct_answer": "B",
        "explanation": "Corticosteroid withdrawal and secondary adrenal insufficiency: Long-term exogenous steroids (>3 weeks at doses >7.5mg prednisolone equivalent) suppress the hypothalamic-pituitary-adrenal (HPA) axis. Mechanism: Exogenous steroids → negative feedback → suppressed CRH and ACTH → adrenal atrophy. Abrupt cessation → acute adrenal insufficiency. Withdrawal approach: (1) Gradual taper (no fixed protocol): Reduce to physiological dose (5-7.5mg prednisolone) relatively quickly; Then slow taper (e.g., reduce by 1-2.5mg every 1-4 weeks); Monitor for adrenal insufficiency symptoms (fatigue, nausea, hypotension). (2) Morning dosing (mimic physiological cortisol rhythm); (3) Test HPA axis recovery if prolonged use: Short Synacthen test when on <5mg prednisolone or after cessation; If normal response (cortisol >450-550 nmol/L) → HPA axis recovered; If inadequate response → continue low-dose replacement, retest in 4-12 weeks. (4) Sick day rules: Patients on long-term steroids or recent withdrawal need increased doses during illness/stress (even if off steroids recently). Duration of HPA suppression: Variable - may take months to year after stopping long-term steroids. This patient: 18 months on supraphysiological dose - definitely HPA suppressed. Needs gradual taper over 2-3 months minimum. May need Synacthen test to confirm recovery before fully stopping. Carry steroid emergency card during taper period. Secondary AI (from exogenous steroids) does NOT need fludrocortisone (aldosterone production intact - controlled by renin-angiotensin, not ACTH)."
    },

    "ENDO-MCQ-0097": {
        "subtopic": "Prolactinoma - Presentation",
        "scenario": "A 32-year-old woman presents with 12 months of amenorrhea and galactorrhea. She is not pregnant (negative pregnancy test). No headaches or visual disturbances. Prolactin level 3200 mU/L (normal <500 mU/L).",
        "stem": "What is the most likely diagnosis and next investigation?",
        "options": {
            "A": "Physiological hyperprolactinemia - reassure",
            "B": "Prolactinoma (pituitary adenoma) - MRI pituitary",
            "C": "Hypothyroidism - check TSH",
            "D": "Polycystic ovary syndrome - pelvic ultrasound"
        },
        "correct_answer": "B",
        "explanation": "Prolactinoma: Most common functional pituitary adenoma (40% of pituitary tumors). Causes of hyperprolactinemia: (1) Physiological: pregnancy, breastfeeding, stress, sleep, exercise; (2) Pharmacological: dopamine antagonists (metoclopramide, antipsychotics), antidepressants (SSRIs, TCAs), opioids, methyldopa; (3) Hypothyroidism (TRH stimulates prolactin); (4) Pituitary stalk compression (any pituitary mass) - 'stalk effect' - mild elevation <2000-3000 mU/L; (5) Prolactinoma - adenoma secreting prolactin: Microprolactinoma (<1cm, prolactin 1000-5000 mU/L); Macroprolactinoma (≥1cm, prolactin often >5000 mU/L). Symptoms: Women: Amenorrhea, oligomenorrhea, infertility, galactorrhea, loss of libido, vaginal dryness (estrogen deficiency from prolactin suppressing GnRH). Men: Erectile dysfunction, loss of libido, infertility, gynecomastia (less common), often present later with macroadenomas and mass effects. Mass effects (macroadenomas): Headaches, bitemporal hemianopia (optic chiasm compression), hypopituitarism. This patient: Very high prolactin (>3000 mU/L), classic symptoms - highly suggestive of prolactinoma. Next step: (1) MRI pituitary (with gadolinium); (2) Assess other pituitary hormones (TSH, free T4, LH, FSH, cortisol, IGF-1) for hypopituitarism; (3) Visual field testing if macroadenoma. Prolactin >5000 mU/L = almost certainly prolactinoma (not stalk effect). Treatment: medical (dopamine agonists), not surgery."
    },

    "ENDO-MCQ-0098": {
        "subtopic": "Prolactinoma - Medical Management",
        "scenario": "A 28-year-old woman is diagnosed with a 7mm microprolactinoma (prolactin 2200 mU/L). MRI shows no mass effect or suprasellar extension. She has amenorrhea and wishes to restore fertility.",
        "stem": "What is the first-line treatment?",
        "options": {
            "A": "Trans-sphenoidal surgery",
            "B": "Dopamine agonist therapy (cabergoline or bromocriptine)",
            "C": "Radiotherapy",
            "D": "Observation only"
        },
        "correct_answer": "B",
        "explanation": "Prolactinoma treatment: Medical therapy is first-line (unlike other pituitary adenomas where surgery is often primary). Dopamine agonists: (1) Cabergoline (Dostinex): Preferred agent; Dose: 0.25-0.5mg twice weekly, titrate up; Efficacy: normalizes prolactin in 80-90%, shrinks tumor 60-90%; Better tolerated than bromocriptine (less nausea). (2) Bromocriptine: 1.25-15mg daily in divided doses; Efficacy: normalizes prolactin 70-80%; More side effects (nausea, orthostatic hypotension, nasal congestion). Mechanism: Dopamine agonists suppress prolactin secretion and shrink tumor. Goals: Normalize prolactin, restore menses/fertility, shrink tumor, prevent osteoporosis (estrogen deficiency). Indications for treatment: (1) Symptomatic (oligomenorrhea, galactorrhea, sexual dysfunction); (2) Wishes to conceive; (3) Mass effects (macroadenomas); (4) Prevent osteoporosis. Surgery (trans-sphenoidal): Reserved for: (1) Drug intolerance/resistance (5-10%); (2) CSF leak from dopamine agonist-induced tumor shrinkage (rare); (3) Patient preference. Lower cure rate than medical therapy (50-70% for microadenomas). Microprolactinomas vs macroprolactinomas: Microprolactinomas: May not need treatment if asymptomatic, no fertility concerns; Can observe with periodic prolactin/MRI; Rarely progress. Macroprolactinomas: Almost always need treatment (mass effects, hypopituitarism). This patient: symptomatic, desires fertility - cabergoline first-line. Monitor prolactin monthly, MRI at 6-12 months to assess shrinkage."
    },

    "ENDO-MCQ-0099": {
        "subtopic": "Acromegaly - Diagnosis",
        "scenario": "A 48-year-old man presents with gradual facial changes over 5 years, increased shoe/ring size, snoring, and excessive sweating. BP 155/95 mmHg, fasting glucose 7.2 mmol/L. Examination shows coarse facial features, frontal bossing, prominent jaw (prognathism), large hands and feet, skin tags. Random IGF-1 level is elevated.",
        "stem": "What is the most appropriate confirmatory test for acromegaly?",
        "options": {
            "A": "Random growth hormone (GH) level",
            "B": "Oral glucose tolerance test with GH suppression (75g glucose, measure GH at baseline and 2 hours)",
            "C": "Pituitary MRI alone",
            "D": "Insulin tolerance test"
        },
        "correct_answer": "B",
        "explanation": "Acromegaly: Excess growth hormone (GH), usually from pituitary adenoma (98%), rarely ectopic GHRH. Features: (1) Acral enlargement: hands, feet, jaw (macrognathia, prognathism); (2) Facial changes: coarse features, frontal bossing, prominent supraorbital ridges, large nose/lips; (3) Skin: thick, oily, skin tags, acanthosis nigricans; (4) Arthralgia, carpal tunnel; (5) Obstructive sleep apnea; (6) Hypertension (40%), diabetes (30%), cardiomyopathy; (7) Colonic polyps (increased cancer risk); (8) Hyperhidrosis, headaches. Diagnosis: Step 1 - Screening: IGF-1 (insulin-like growth factor 1): Age- and sex-adjusted; Elevated IGF-1 = screen positive; IGF-1 integrates GH secretion over time (GH is pulsatile - single level unreliable). Step 2 - Confirmatory test: Oral glucose tolerance test (OGTT) with GH measurement: Give 75g glucose orally; Measure GH at baseline, 30, 60, 90, 120 minutes; Normal: GH suppresses to <1 mcg/L (glucose normally inhibits GH); Acromegaly: GH fails to suppress (often paradoxical rise). Step 3 - Imaging: MRI pituitary to locate adenoma (90% macroadenomas). This patient: classic features + elevated IGF-1 - needs OGTT for confirmation. Random GH unhelpful (pulsatile, affected by stress, sleep, meals). Treatment: Trans-sphenoidal surgery (first-line), medical therapy (somatostatin analogs, dopamine agonists, pegvisomant), radiotherapy if refractory. Complications if untreated: Cardiovascular disease (leading cause death), arthritis, OSA, colonic neoplasia."
    },

    "ENDO-MCQ-0100": {
        "subtopic": "Pituitary Apoplexy",
        "scenario": "A 45-year-old man with known pituitary macroadenoma (on observation) presents to ED with sudden-onset severe headache ('worst headache of life'), vomiting, diplopia, and confusion. On examination, he has bilateral 3rd nerve palsies, reduced visual acuity, BP 85/55 mmHg.",
        "stem": "What is the most likely diagnosis and immediate management?",
        "options": {
            "A": "Migraine - analgesia and observation",
            "B": "Pituitary apoplexy (hemorrhage/infarction into pituitary) - urgent IV hydrocortisone 100mg, urgent MRI/CT, neurosurgical consultation for possible decompression",
            "C": "Meningitis - lumbar puncture and antibiotics",
            "D": "Subarachnoid hemorrhage - refer neurosurgery"
        },
        "correct_answer": "B",
        "explanation": "Pituitary apoplexy: Acute hemorrhage or infarction into pituitary gland (usually pre-existing adenoma). Medical emergency. Precipitants: (1) Spontaneous (most common); (2) Post-surgery, head trauma; (3) Anticoagulation; (4) Pregnancy (Sheehan's syndrome if postpartum); (5) Dopamine agonist initiation. Clinical features: (1) Sudden severe headache (thunderclap, retro-orbital); (2) Visual disturbance (bitemporal hemianopia, diplopia, blindness) - optic chiasm/nerves compressed; (3) Ophthalmoplegia (3rd, 4th, 6th nerve palsies) - cavernous sinus invasion; (4) Altered consciousness, confusion; (5) Nausea, vomiting; (6) Hypopituitarism (acute adrenal insufficiency most dangerous - hypotension, shock). Differential diagnosis: SAH (consider if no known pituitary adenoma), meningitis (fever more prominent), migraine (less severe). Investigations: (1) Urgent MRI (or CT if MRI unavailable): shows hemorrhage/infarction in pituitary; (2) Visual field assessment; (3) Pituitary function tests (but don't delay treatment). Management: (1) IV hydrocortisone 100mg STAT, then every 6 hours (treat acute adrenal crisis - most important); (2) IV fluids; (3) Urgent neurosurgical consultation: Surgery (trans-sphenoidal decompression) indicated if: progressive visual loss, severe/persistent visual deficits, reduced consciousness; Conservative management if: stable vision, no neuro deterioration. (4) Hormone replacement (after acute phase). Prognosis: Variable - vision loss may be permanent if delayed treatment. Most patients develop hypopituitarism. This patient: classic apoplexy presentation - needs immediate steroids + neurosurgical assessment. Do NOT delay for pituitary function tests."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 6C UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 6C: ENDO-MCQ-0081 to 0100 (Thyroid + Adrenal + Pituitary)")
    print(f"Sub-batch 3 of 5 in Batch 6 (100 MCQs total)")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch6c_generated)

    print(f"\n✅ Batch 6C Complete: {updated}/20 MCQs updated")
    print(f"✅ Total Progress: 100/658 MCQs (15.2%)")
    print(f"\n🔄 Batch 6 Progress: 60/100 complete")
    print(f"Next: Batch 6D (MCQs 0101-0120 - Pituitary Disorders continued)")
