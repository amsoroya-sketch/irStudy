#!/usr/bin/env python3
"""
Update MCQ Batch 6A - ENDO-MCQ-0041 to 0060 (20 MCQs)
Sub-batch 1 of 5 in Batch 6
Topics: DKA (continued) + Hypoglycemia
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


# Batch 6A: ENDO-MCQ-0041 to 0060
batch6a_generated = {
    "ENDO-MCQ-0041": {
        "subtopic": "DKA in Pregnancy",
        "scenario": "A 24-year-old woman at 28 weeks gestation with type 1 diabetes presents to ED with vomiting, abdominal pain, and reduced fetal movements. Capillary glucose 22 mmol/L. Venous gas shows pH 7.21, bicarbonate 11 mmol/L, blood ketones 4.8 mmol/L. Obstetric examination: uterus soft, fetal heart rate 155 bpm, CTG shows reduced variability.",
        "stem": "What is the most important additional consideration in DKA management during pregnancy?",
        "options": {
            "A": "Insulin requirements are lower in pregnancy, reduce standard insulin dose by 50%",
            "B": "Fetal monitoring (CTG) throughout treatment as fetal distress common; consider delivery if DKA not resolving",
            "C": "Avoid IV fluids due to risk of pulmonary oedema in pregnancy",
            "D": "Bicarbonate therapy is mandatory in pregnancy to protect the fetus"
        },
        "correct_answer": "B",
        "explanation": "DKA in pregnancy is a medical and obstetric emergency with higher maternal and fetal risks. Key differences: (1) Lower glucose threshold (DKA can occur at glucose 14-20 mmol/L due to pregnancy physiology); (2) Continuous fetal monitoring (CTG) essential - DKA causes fetal distress, risk of intrauterine death 10-35%; (3) Maternal positioning (left lateral tilt to avoid aortocaval compression); (4) Multidisciplinary care (obstetrics, endocrinology, ICU); (5) Precipitants often include infection (UTI), hyperemesis, steroid administration for fetal lung maturity. Standard DKA treatment principles apply (fluids, insulin, potassium) but insulin requirements typically higher in pregnancy. Delivery indicated if DKA not resolving or persistent fetal distress, but maternal resuscitation takes priority. Prevention: earlier intervention for minor illness, lower threshold for admission in pregnant women with diabetes."
    },

    "ENDO-MCQ-0042": {
        "subtopic": "DKA Monitoring Parameters",
        "scenario": "A 28-year-old woman is being treated for DKA. Initial values: glucose 28 mmol/L, pH 7.14, potassium 5.2 mmol/L. After 4 hours of treatment with fluids and insulin, her glucose is 16 mmol/L, pH 7.26, potassium 3.8 mmol/L, blood ketones 2.1 mmol/L.",
        "stem": "What is the most appropriate next monitoring interval for blood tests?",
        "options": {
            "A": "Glucose hourly, venous gas and electrolytes every 1-2 hours until DKA resolved",
            "B": "Glucose every 4 hours only",
            "C": "No further blood tests needed as glucose falling appropriately",
            "D": "Venous gas only when patient feels better"
        },
        "correct_answer": "A",
        "explanation": "DKA monitoring requirements: (1) Capillary glucose: hourly (more frequently if hypoglycemia risk); (2) Venous blood gas and electrolytes: 1-2 hourly initially, then 2-4 hourly until DKA resolved; (3) Blood ketones: every 1-2 hours (if available); (4) Fluid balance: hourly input/output; (5) Vital signs: hourly (BP, HR, RR, temperature, consciousness level); (6) ECG monitoring (for potassium changes). Continue intensive monitoring until DKA resolution criteria met (pH >7.3, bicarbonate >15 mmol/L, ketones <0.6 mmol/L). This patient still has significant ketosis (ketones 2.1 mmol/L) and mild acidosis (pH 7.26) despite glucose improvement - requires ongoing intensive monitoring. Common error: reducing monitoring frequency when glucose normalizes, but ketoacidosis persists. After DKA resolution, continue monitoring for 24 hours to detect any relapse."
    },

    "ENDO-MCQ-0043": {
        "subtopic": "Recurrent DKA Prevention",
        "scenario": "A 22-year-old woman with type 1 diabetes has had 4 admissions for DKA in the past year. Her HbA1c between episodes is 8.5%. She lives alone, works full-time, and reports difficulty affording insulin pens (not on PBS). On questioning, she admits sometimes missing doses to make supplies last longer.",
        "stem": "What is the most important intervention to prevent further DKA episodes?",
        "options": {
            "A": "Switch to twice-daily premixed insulin for simplicity",
            "B": "Address insulin access issues (diabetes educator, social work referral, PBS streamlining), structured diabetes education, psychology input",
            "C": "Increase insulin doses by 50% to improve control",
            "D": "Admission to hospital for 2 weeks of supervised insulin administration"
        },
        "correct_answer": "B",
        "explanation": "Recurrent DKA requires identifying and addressing underlying causes. Common factors: (1) Insulin omission (intentional or financial barriers); (2) Pump malfunction; (3) Psychological issues (eating disorders, diabetes burnout, depression); (4) Inadequate education; (5) Substance abuse; (6) Socioeconomic barriers. This patient has insulin access issues due to cost. Management approach: (1) Social work referral for financial support/PBS navigation; (2) Ensure insulin supply (may need prescription for cheaper insulin types, vial/syringe rather than pens); (3) Diabetes educator for insulin technique and sick day management; (4) Psychology/psychiatry if psychological factors identified; (5) Consider insulin pump with CGM if recurrent DKA despite optimal support; (6) Structured education program (DAFNE or equivalent). In Australia, PBS covers insulin but eligibility/co-payments can be barriers. Simply increasing dose doesn't address the adherence issue. Multidisciplinary approach essential."
    },

    "ENDO-MCQ-0044": {
        "subtopic": "DKA in Type 2 Diabetes",
        "scenario": "A 58-year-old obese man (BMI 38) with type 2 diabetes for 8 years presents in DKA (glucose 26 mmol/L, pH 7.16, ketones 4.2 mmol/L). He has been on metformin and gliclazide. He recently started treatment for a chest infection with amoxicillin. This is his first episode of DKA.",
        "stem": "What is the most likely underlying pathophysiology in this case?",
        "options": {
            "A": "He actually has type 1 diabetes, not type 2",
            "B": "Ketosis-prone type 2 diabetes with stress-induced insulin deficiency from infection",
            "C": "Metformin-induced lactic acidosis mimicking DKA",
            "D": "Gliclazide overdose"
        },
        "correct_answer": "B",
        "explanation": "DKA can occur in type 2 diabetes, contrary to common teaching. Mechanisms: (1) Ketosis-prone type 2 diabetes (formerly 'Flatbush diabetes', more common in African/Hispanic populations): stress (illness, surgery, medication) precipitates sudden insulin deficiency in people with T2DM; (2) SGLT2 inhibitor use (euglycemic DKA); (3) Previously unrecognized type 1 diabetes/LADA misdiagnosed as T2DM. This patient: established T2DM, obese (insulin resistant phenotype), precipitant infection. Suggests ketosis-prone T2DM. Features: (1) First presentation often DKA; (2) Severe hyperglycemia and ketosis; (3) After recovery, many achieve remission off insulin (differentiating from T1DM); (4) May require insulin long-term if beta cell function poor. Investigations: C-peptide, diabetes autoantibodies (GAD, IA-2). Management: treat DKA standardly, then assess beta cell reserve. Many can transition back to oral agents after resolution. Follow-up HbA1c and C-peptide guide long-term therapy."
    },

    "ENDO-MCQ-0045": {
        "subtopic": "DKA and Acute Kidney Injury",
        "scenario": "A 35-year-old man with DKA is receiving treatment. Initial creatinine 180 micromol/L (baseline 75). Urinalysis: protein 1+, no blood, no casts. After 8 hours of IV fluids (4 litres normal saline) and insulin, his glucose is 14 mmol/L but repeat creatinine is 195 micromol/L. Urine output has been 150 mL in last 4 hours.",
        "stem": "What is the most appropriate next step regarding the acute kidney injury?",
        "options": {
            "A": "Continue current fluid rate as AKI will resolve with ongoing resuscitation",
            "B": "Reassess fluid status (BP, JVP, oedema), increase fluid rate if still hypovolemic, consider urinary catheter for accurate monitoring",
            "C": "Stop IV fluids immediately to prevent fluid overload",
            "D": "Urgent dialysis"
        },
        "correct_answer": "B",
        "explanation": "AKI is common in DKA (up to 50% of cases), usually pre-renal from dehydration but can progress to acute tubular necrosis. Causes: (1) Hypovolemia (osmotic diuresis); (2) Hypotension; (3) Nephrotoxins (contrast, NSAIDs); (4) Rhabdomyolysis (if prolonged immobility). Assessment: (1) Volume status (BP, pulse, JVP, skin turgor, mucous membranes, oedema); (2) Urine output (consider catheter if oliguric); (3) Response to fluids (creatinine trend); (4) Exclude obstruction (bladder scan). This patient: still oliguric (150 mL/4 hours = 37 mL/hour, oliguria <0.5 mL/kg/hour) despite 4 L fluids, rising creatinine. Suggests ongoing hypovolemia or evolving ATN. Management: (1) Reassess volume status; (2) If still dry: continue/increase fluid resuscitation; (3) Urinary catheter for accurate monitoring; (4) Avoid nephrotoxins; (5) Adjust insulin/medication doses for AKI; (6) Monitor electrolytes closely (potassium, phosphate). Dialysis rarely needed unless severe hyperkalaemia, refractory acidosis, or fluid overload. Most AKI in DKA resolves with adequate hydration."
    },

    "ENDO-MCQ-0046": {
        "subtopic": "Hypoglycemia Definition",
        "scenario": "A 52-year-old man with type 2 diabetes on metformin and gliclazide checks his capillary glucose which reads 3.2 mmol/L. He feels well with no symptoms. He ate breakfast 2 hours ago.",
        "stem": "How should this glucose level be classified and managed?",
        "options": {
            "A": "Normal glucose - no action needed",
            "B": "Hypoglycemia (glucose <4.0 mmol/L) - treat immediately with 15g fast-acting carbohydrate even if asymptomatic",
            "C": "Only true hypoglycemia if symptomatic, ignore if feeling well",
            "D": "Hypoglycemia but only treat if glucose <2.8 mmol/L"
        },
        "correct_answer": "B",
        "explanation": "Hypoglycemia definitions: (1) Biochemical: glucose <4.0 mmol/L (Australian Diabetes Society); Some guidelines use <3.9 mmol/L or <3.5 mmol/L; (2) Symptomatic: glucose <4.0 mmol/L with symptoms; (3) Severe: requires assistance from another person. Levels: Alert level 1 (3.0-3.9 mmol/L), Alert level 2 (<3.0 mmol/L), Severe (any level requiring assistance). This patient has biochemical hypoglycemia (3.2 mmol/L) despite being asymptomatic - possibly due to hypoglycemia unawareness or frequent lows. Treatment: (1) 15g fast-acting carbohydrate (3-4 glucose tablets, 150mL juice, 6-7 jelly beans); (2) Recheck glucose after 15 minutes; (3) Repeat treatment if still <4.0 mmol/L; (4) Once glucose >4.0 mmol/L, eat longer-acting carbohydrate if meal not due. All hypoglycemia <4.0 mmol/L should be treated, even if asymptomatic, to prevent further drop and restore safety. Investigate cause: sulfonylurea dose too high, inadequate food intake, increased exercise."
    },

    "ENDO-MCQ-0047": {
        "subtopic": "Severe Hypoglycemia Management",
        "scenario": "A 68-year-old woman with type 2 diabetes is found unconscious at home by her daughter. She is on insulin therapy. Capillary glucose is 1.8 mmol/L. She is unrousable with GCS 8, but has patent airway and is breathing normally. IV access is difficult.",
        "stem": "What is the most appropriate immediate management?",
        "options": {
            "A": "Call ambulance and wait for paramedics to establish IV access",
            "B": "Intramuscular glucagon 1 mg, place in recovery position, call ambulance, recheck glucose in 10 minutes",
            "C": "Give oral glucose gel via buccal route",
            "D": "Attempt to wake patient and give oral juice"
        },
        "correct_answer": "B",
        "explanation": "Severe hypoglycemia (requires third party assistance) management depends on consciousness and IV access: (1) Conscious, able to swallow: oral glucose 15-20g; (2) Unconscious OR unable to swallow, IV access available: 75-100mL 20% dextrose OR 150-200mL 10% dextrose IV (NOT 50% dextrose - causes tissue necrosis if extravasation); (3) Unconscious, no IV access: IM/SC glucagon 1 mg (0.5 mg if <25kg). Glucagon mechanism: mobilizes hepatic glycogen, effective in 10-15 minutes, duration 60-90 minutes. After glucagon: (1) Place in recovery position; (2) Monitor airway; (3) Recheck glucose 10 minutes, expect rise to >4 mmol/L; (4) Once conscious, give oral carbohydrate; (5) Monitor as may need repeat treatment. Limitations of glucagon: ineffective if glycogen depleted (starvation, alcohol, liver disease), can cause nausea/vomiting. Do NOT give oral glucose/fluids if unconscious - aspiration risk. This patient: unconscious, difficult IV access - IM glucagon is correct choice. Call ambulance for hospital assessment. Adjust diabetes medications after severe hypoglycemia."
    },

    "ENDO-MCQ-0048": {
        "subtopic": "Hypoglycemia Unawareness",
        "scenario": "A 42-year-old man with type 1 diabetes for 20 years reports no longer experiencing warning symptoms of hypoglycemia. He has had 3 episodes in past month where he became confused/disorientated without preceding symptoms. His HbA1c is 5.8% (target <7%). CGM shows frequent glucose readings <3.0 mmol/L.",
        "stem": "What is the most important management strategy?",
        "options": {
            "A": "Increase insulin doses to prevent hyperglycemia",
            "B": "Relax glycemic targets (accept higher glucose levels 6-10 mmol/L) for 2-3 months to restore hypoglycemia awareness",
            "C": "Continue current regimen as tight control is beneficial",
            "D": "Stop insulin and switch to oral agents"
        },
        "correct_answer": "B",
        "explanation": "Hypoglycemia unawareness: impaired ability to perceive hypoglycemia warning symptoms (sweating, tremor, palpitations), increasing severe hypoglycemia risk 6-fold. Causes: (1) Recurrent hypoglycemia (most common - resets glucose threshold); (2) Long diabetes duration (>15 years); (3) Autonomic neuropathy; (4) Strict glycemic control. Consequences: first presentation may be seizure/coma, not mild symptoms. Management: (1) Relax glycemic targets: accept higher glucose (6-10 mmol/L) for 2-3 months to restore awareness - counter-regulatory responses recover; (2) Avoid hypoglycemia <3.9 mmol/L completely; (3) Structured education on hypoglycemia prevention; (4) CGM with low glucose alerts (highly beneficial); (5) Review insulin regimen - reduce basal/bolus doses; (6) Address contributing factors. This patient: very tight control (HbA1c 5.8%), frequent hypos causing unawareness - dangerous situation. Paradoxically, accepting higher glucose short-term restores awareness and improves safety long-term. After awareness returns, can cautiously optimize control with CGM guidance. Hypoglycemia unawareness is reversible in most cases with hypoglycemia avoidance."
    },

    "ENDO-MCQ-0049": {
        "subtopic": "Nocturnal Hypoglycemia",
        "scenario": "A 28-year-old woman with type 1 diabetes reports morning headaches, vivid dreams, and waking with sweat-soaked sheets several times per week. Morning glucose readings are often 12-15 mmol/L despite good control during the day.",
        "stem": "What is the most likely diagnosis and appropriate investigation?",
        "options": {
            "A": "Dawn phenomenon - increase evening insulin",
            "B": "Nocturnal hypoglycemia with rebound hyperglycemia (Somogyi effect) - check 2-3am glucose levels or use CGM",
            "C": "Sleep apnea - refer for sleep study",
            "D": "Inadequate evening insulin - increase dose"
        },
        "correct_answer": "B",
        "explanation": "Clinical picture suggests nocturnal hypoglycemia: night sweats, nightmares, morning headaches, morning hyperglycemia. Somogyi effect: nocturnal hypoglycemia triggers counter-regulatory hormones (glucagon, cortisol, adrenaline, growth hormone) causing rebound hyperglycemia by morning. Distinguished from dawn phenomenon (morning hyperglycemia without nocturnal hypo, due to growth hormone surge 4-8am). Diagnosis: (1) Check 2-3am glucose for several nights; OR (2) Use CGM (gold standard); (3) May find glucose <3.0 mmol/L overnight. Risk factors: (1) Evening exercise without carbohydrate adjustment; (2) Evening alcohol; (3) Excessive evening basal insulin; (4) Missed evening snack. Management: (1) Reduce evening basal insulin dose by 10-20%; (2) Bedtime snack with protein (delays glucose absorption); (3) Avoid evening alcohol; (4) If on twice-daily insulin, may need to split evening dose or switch to basal-bolus. Common error: increasing evening insulin due to morning hyperglycemia without checking nocturnal glucose - worsens nocturnal hypoglycemia. CGM transformative for detecting nocturnal hypos. After adjusting insulin, recheck overnight glucose to confirm resolution."
    },

    "ENDO-MCQ-0050": {
        "subtopic": "Exercise-Induced Hypoglycemia",
        "scenario": "A 19-year-old man with type 1 diabetes wants to start regular gym training (weights and cardio 5 days/week). He is on basal-bolus insulin (insulin glargine at night, insulin aspart with meals). He asks how to prevent hypoglycemia during and after exercise.",
        "stem": "What is the most appropriate advice for exercise and insulin management?",
        "options": {
            "A": "Stop all insulin on exercise days",
            "B": "Check glucose before/during/after exercise; reduce pre-exercise bolus insulin by 25-50% if exercising within 2 hours of meal; consider 15-30g carbohydrate before exercise if glucose <7mmol/L; reduce basal insulin by 10-20% if regular daily exercise",
            "C": "Exercise only when glucose >15 mmol/L to prevent hypos",
            "D": "Double carbohydrate intake on exercise days"
        },
        "correct_answer": "B",
        "explanation": "Exercise and diabetes management: Exercise increases insulin sensitivity and glucose uptake, causing hypoglycemia risk during and up to 24 hours after. Strategies depend on timing and intensity: Before exercise: (1) Check glucose - safe range 5-7 mmol/L; (2) If <5 mmol/L: 15-30g carbohydrate before starting; (3) If <4 mmol/L: treat hypoglycemia, delay exercise; (4) Reduce pre-exercise insulin bolus by 25-50% if exercising within 2 hours of meal. During exercise: (1) Monitor glucose (every 30-60 min if prolonged); (2) Have fast-acting carbohydrate available. After exercise: (1) Delayed hypoglycemia risk (muscle glycogen replenishment increases glucose uptake for 24 hours); (2) May need extra carbohydrate bedtime snack; (3) Reduce basal insulin by 10-20% after prolonged/intense exercise. Regular exercise: (1) Reduce total daily insulin dose by 10-20% if exercising daily; (2) CGM very helpful. Type of exercise matters: (1) Aerobic (running, cycling) - lowers glucose; (2) Anaerobic (sprinting, weights) - may raise glucose short-term. Contraindications: Avoid exercise if glucose >15 mmol/L with ketones (worsens ketosis). Hydration important. Individualized approach needed."
    },

    "ENDO-MCQ-0051": {
        "subtopic": "Alcohol and Hypoglycemia",
        "scenario": "A 35-year-old man with type 1 diabetes attends a wedding. He drinks 6 standard drinks of alcohol over 4 hours (with dinner). The next morning he is found unconscious by his wife with capillary glucose 2.1 mmol/L. After treatment, he asks why this occurred.",
        "stem": "What is the mechanism of alcohol-induced hypoglycemia?",
        "options": {
            "A": "Alcohol stimulates insulin secretion",
            "B": "Alcohol inhibits hepatic gluconeogenesis, preventing glucose production from non-carbohydrate sources during fasting",
            "C": "Alcohol increases glucose excretion in urine",
            "D": "Alcohol directly damages pancreatic beta cells"
        },
        "correct_answer": "B",
        "explanation": "Alcohol-induced hypoglycemia mechanism: (1) Alcohol metabolism in liver produces NADH; (2) High NADH/NAD+ ratio inhibits gluconeogenesis (glucose production from lactate, amino acids, glycerol); (3) If glycogen stores depleted (fasting, exercise), hypoglycemia occurs; (4) Effect lasts up to 8-12 hours after drinking. Risk factors: (1) Fasting or missing meals; (2) Exercise before/after drinking; (3) Insulin/sulfonylureas (alcohol doesn't cause hypos in non-diabetics with normal insulin); (4) Binge drinking. Clinical features: delayed hypoglycemia (often overnight, 6-12 hours post-drinking), severe hypoglycemia without preceding symptoms (alcohol impairs awareness). Prevention: (1) Never drink on empty stomach; (2) Eat carbohydrate-containing meal before/during drinking; (3) Reduce insulin dose by 10-20% if drinking significantly; (4) Bedtime snack essential; (5) Inform companion about diabetes and hypoglycemia risk; (6) Check glucose before bed and overnight if needed. This patient: drank 6 standard drinks, likely went to bed, developed delayed hypoglycemia overnight as hepatic glucose production impaired. Moderate alcohol intake (1-2 standard drinks) with food generally safe; binge drinking high risk."
    },

    "ENDO-MCQ-0052": {
        "subtopic": "Whipple's Triad",
        "scenario": "A 48-year-old woman without diabetes presents to her GP with recurrent episodes of confusion, tremor, and sweating, relieved by eating. These occur in the morning before breakfast. Her fasting glucose during an episode is 2.4 mmol/L, which rises to 6.2 mmol/L after eating toast.",
        "stem": "Which diagnostic criteria (Whipple's triad) are met, suggesting true hypoglycemia disorder?",
        "options": {
            "A": "Low glucose only",
            "B": "Symptoms consistent with hypoglycemia; documented low glucose (<2.5-3.0 mmol/L) during symptomatic episode; relief of symptoms with glucose administration",
            "C": "Symptoms alone are sufficient",
            "D": "Random low glucose measurement"
        },
        "correct_answer": "B",
        "explanation": "Whipple's triad (diagnostic criteria for pathological hypoglycemia): (1) Symptoms consistent with hypoglycemia (neuroglycopenic: confusion, behavioral change, seizure; Autonomic: tremor, sweating, palpitations, hunger); (2) Documented low blood glucose during symptomatic episode (<2.5-3.0 mmol/L, though thresholds vary by guidelines); (3) Relief of symptoms when glucose corrected. All three criteria required to diagnose true hypoglycemia disorder. This patient meets all three: appropriate symptoms, documented low glucose (2.4 mmol/L) during symptoms, symptom relief with eating. Next steps: (1) 72-hour supervised fast (gold standard for diagnosing insulinoma/fasting hypoglycemia); (2) During fast: measure glucose, insulin, C-peptide, proinsulin, beta-hydroxybutyrate when glucose <3.0 mmol/L; (3) Plasma sulfonylurea screen to exclude factitious hypoglycemia. Interpretation: High insulin + high C-peptide = endogenous hyperinsulinism (insulinoma, nesidioblastosis); High insulin + low C-peptide = exogenous insulin; High C-peptide + insulin + sulfonylurea detected = factitious. Common causes of fasting hypoglycemia: insulinoma, drugs (insulin, sulfonylureas, alcohol), adrenal insufficiency, liver failure, sepsis, malignancy (IGF-2 producing tumors)."
    },

    "ENDO-MCQ-0053": {
        "subtopic": "Insulinoma Diagnosis",
        "scenario": "A 52-year-old man completes a supervised 72-hour fast for investigation of recurrent hypoglycemic episodes. At 42 hours, he becomes confused with capillary glucose 2.1 mmol/L. Simultaneous blood tests show: glucose 2.2 mmol/L, insulin 85 pmol/L (inappropriately elevated), C-peptide 1850 pmol/L (elevated), proinsulin elevated, negative sulfonylurea screen.",
        "stem": "What is the most likely diagnosis and next investigation?",
        "options": {
            "A": "Factitious hypoglycemia from exogenous insulin - no further testing needed",
            "B": "Insulinoma - proceed with CT pancreas or endoscopic ultrasound for localization",
            "C": "Reactive hypoglycemia - dietary modification",
            "D": "Normal finding - reassure patient"
        },
        "correct_answer": "B",
        "explanation": "Insulinoma diagnosis: Biochemical: Fasting hypoglycemia (glucose <2.5 mmol/L) with: (1) Elevated/inappropriately normal insulin (>18 pmol/L when glucose <2.5 mmol/L); (2) Elevated C-peptide (>200 pmol/L); (3) Elevated proinsulin; (4) Suppressed beta-hydroxybutyrate (<2.7 mmol/L - ketone production inhibited by insulin). This patient's results diagnostic for endogenous hyperinsulinemic hypoglycemia (insulinoma or nesidioblastosis). High C-peptide confirms endogenous (not exogenous insulin), negative sulfonylurea rules out factitious. Insulinoma: (1) Rare neuroendocrine tumor of pancreatic beta cells; (2) 90% benign, 10% malignant; (3) Usually solitary, small (1-2cm); (4) 5-10% multiple (consider MEN-1 syndrome). Localization: (1) CT pancreas (sensitivity 50-70%); (2) MRI pancreas; (3) Endoscopic ultrasound (EUS) - best (sensitivity 90%), can guide FNA; (4) Selective arterial calcium stimulation (for tumors not visualized on imaging). Treatment: Surgical resection (enucleation or partial pancreatectomy) - curative in 90%. Medical management if inoperable: frequent meals, diazoxide (inhibits insulin release), octreotide. Prognosis excellent for benign insulinomas. MEN-1 screening (calcium, PTH, prolactin) if young/multiple tumors."
    },

    "ENDO-MCQ-0054": {
        "subtopic": "Post-Prandial (Reactive) Hypoglycemia",
        "scenario": "A 38-year-old woman reports episodes of tremor, sweating, and palpitations 2-3 hours after meals, particularly after high-carbohydrate breakfasts. Fasting glucose is normal. She had gastric bypass surgery 2 years ago for obesity. Symptoms improve with eating small snack.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Insulinoma",
            "B": "Post-bariatric (post-gastric bypass) reactive hypoglycemia",
            "C": "Factitious disorder",
            "D": "Anxiety disorder"
        },
        "correct_answer": "B",
        "explanation": "Reactive (post-prandial) hypoglycemia: glucose falls 2-5 hours after eating, unlike fasting hypoglycemia. Causes: (1) Post-bariatric surgery (most common, especially Roux-en-Y gastric bypass): rapid gastric emptying → exaggerated GLP-1 response → excessive insulin secretion → hypoglycemia 1-3 hours post-meal; (2) Early dumping syndrome; (3) Idiopathic (rare); (4) Gastric surgery (gastrectomy, vagotomy); (5) Alimentary hypoglycemia. Differentiate from fasting hypoglycemia (insulinoma, adrenal insufficiency) - timing is key. Diagnosis: (1) Mixed meal tolerance test (not oral GTT - not physiological); (2) CGM to capture episodes; (3) Document Whipple's triad. Post-bariatric hypoglycemia: incidence 0.2-34% after gastric bypass, symptoms can be severe/disabling. Management: (1) Dietary modification (low glycemic index diet, small frequent meals, avoid simple sugars, protein with each meal, avoid liquids with meals); (2) Acarbose (delays carbohydrate absorption); (3) Diazoxide, octreotide if refractory; (4) Rarely, gastric bypass reversal or pancreatic resection. This patient: classic timing (2-3 hours post-meal), high-carb triggers, history of gastric bypass. Investigations: confirm hypoglycemia during symptoms, exclude insulinoma with fasting studies if uncertain."
    },

    "ENDO-MCQ-0055": {
        "subtopic": "Non-Diabetic Hypoglycemia - Causes",
        "scenario": "A 45-year-old man presents to ED with confusion and sweating. Capillary glucose 2.0 mmol/L. He has no history of diabetes. On examination, he appears chronically unwell with hyperpigmentation of palmar creases and buccal mucosa. BP 85/55 mmHg, HR 110 bpm.",
        "stem": "What is the most likely underlying diagnosis?",
        "options": {
            "A": "Insulinoma",
            "B": "Primary adrenal insufficiency (Addison's disease)",
            "C": "Growth hormone deficiency",
            "D": "Malnutrition alone"
        },
        "correct_answer": "B",
        "explanation": "Non-diabetic hypoglycemia causes: (1) Endocrine: Adrenal insufficiency (cortisol deficiency), hypopituitarism (cortisol and GH deficiency), hypothyroidism (severe); (2) Hepatic: Cirrhosis, acute liver failure, glycogen storage diseases; (3) Renal: Advanced CKD (impaired gluconeogenesis, reduced insulin clearance); (4) Sepsis; (5) Malignancy (IGF-2 secreting tumors - mesothelioma, sarcomas); (6) Drugs: Insulin, sulfonylureas, alcohol, quinine, pentamidine, beta-blockers; (7) Critical illness; (8) Insulinoma; (9) Post-bariatric surgery; (10) Factitious (deliberate insulin/sulfonylurea use). This patient: hypoglycemia + hypotension + hyperpigmentation suggests primary adrenal insufficiency (Addison's disease). Cortisol essential for gluconeogenesis and counter-regulation during hypoglycemia. Investigations: (1) Treat hypoglycemia immediately; (2) Random cortisol (may be inappropriately normal/low given stress); (3) ACTH level (elevated in primary adrenal insufficiency); (4) Short Synacthen test; (5) Electrolytes (hyponatraemia, hyperkalaemia common in Addison's). Management: (1) IV dextrose for hypoglycemia; (2) IV hydrocortisone 100mg stat; (3) IV fluids; (4) Investigate cause of adrenal insufficiency. Hypoglycemia in adrenal insufficiency typically occurs with prolonged fasting or stress."
    },

    "ENDO-MCQ-0056": {
        "subtopic": "Sulfonylurea-Induced Hypoglycemia",
        "scenario": "An 82-year-old woman with type 2 diabetes presents with recurrent hypoglycemic episodes (glucose 2.2-2.8 mmol/L) over the past week, requiring multiple ED presentations. Her medications include gliclazide 160mg twice daily, metformin 1g twice daily, perindopril, and atorvastatin. Creatinine 145 micromol/L (eGFR 32).",
        "stem": "What is the most important management step to prevent further hypoglycemia?",
        "options": {
            "A": "Continue gliclazide but reduce dose to 80mg twice daily",
            "B": "Cease gliclazide (contraindicated in CKD stage 3B-5); consider alternative agent (DPP-4 inhibitor, SGLT2 inhibitor if eGFR appropriate)",
            "C": "Add extra carbohydrate snacks between meals",
            "D": "Switch to glibenclamide which is safer in renal impairment"
        },
        "correct_answer": "B",
        "explanation": "Sulfonylurea-induced hypoglycemia: Mechanism: Sulfonylureas stimulate insulin release regardless of glucose level. Risk factors: (1) Renal impairment (sulfonylureas/active metabolites renally excreted); (2) Elderly; (3) Irregular meals; (4) Alcohol; (5) Drug interactions; (6) Frailty. Long-acting sulfonylureas (glibenclamide, gliclazide MR) highest risk. This patient: elderly, CKD 3B (eGFR 32), on high-dose gliclazide - very high hypoglycemia risk. Gliclazide contraindicated in CKD stage 3B-5 (eGFR <45). Management: (1) Cease sulfonylurea immediately; (2) If glucose-lowering still needed: consider DPP-4 inhibitors (linagliptin, saxagliptin dose-adjusted), SGLT2 inhibitors (if eGFR appropriate, cardio-renal benefits), basal insulin (carefully titrated); (3) Metformin dose may need reduction/cessation if eGFR continues declining (cease if eGFR <30). (4) Observe for 24-48 hours after stopping sulfonylurea (long half-life, may have recurrent hypos). Treatment of sulfonylurea-induced hypoglycemia: (1) Dextrose IV (may need prolonged infusion); (2) Octreotide (inhibits insulin release) if refractory; (3) Hospital admission often required (prolonged hypoglycemia risk). Prevention: avoid sulfonylureas in elderly with CKD; use agents with lower hypo risk."
    },

    "ENDO-MCQ-0057": {
        "subtopic": "Hypoglycemia in Hospital",
        "scenario": "A 70-year-old man with type 2 diabetes is admitted for pneumonia. He is usually on metformin and gliclazide. On day 3 of admission, he becomes confused with capillary glucose 2.5 mmol/L. He has been eating poorly (30% of meals). His gliclazide has been continued at usual dose.",
        "stem": "What is the most likely contributing factor and prevention strategy?",
        "options": {
            "A": "Infection-related hypoglycemia - no medication changes needed",
            "B": "Continued sulfonylurea despite poor oral intake - should have been ceased/held during acute illness with reduced eating",
            "C": "Metformin causing hypoglycemia - cease metformin",
            "D": "Laboratory error"
        },
        "correct_answer": "B",
        "explanation": "Inpatient hypoglycemia is common (5-10% of hospitalized diabetics) and preventable. Causes: (1) Continued usual diabetes medications despite reduced oral intake; (2) Inappropriate insulin doses; (3) Timing mismatch (insulin given before meal that's not eaten); (4) Failure to adjust for AKI/liver disease; (5) Nil by mouth status without medication adjustment; (6) Interruption of tube feeds/TPN without glucose source. Risk factors: elderly, CKD, sepsis, corticosteroid use (then stopped), variable nutrition. This patient: sulfonylurea continued despite poor oral intake - inappropriate. Sulfonylureas stimulate insulin regardless of glucose/food - hypoglycemia inevitable if not eating. Prevention strategies: (1) Cease sulfonylureas during acute illness (use insulin instead if needed); (2) Hold short-acting insulin if meal not eaten; (3) Adjust long-acting insulin doses during illness; (4) Bedside glucose monitoring (QID minimum if on insulin/sulfonylureas); (5) Hypoglycemia protocol (15g glucose, recheck, repeat); (6) If NBM: IV dextrose or reduce/cease insulin/sulfonylureas. Metformin does NOT cause hypoglycemia (stops hepatic glucose production but doesn't stimulate insulin). After discharge: resume usual medications with sick-day education. Inpatient diabetes management guidelines emphasize basal-bolus insulin as safer than continuing outpatient oral agents."
    },

    "ENDO-MCQ-0058": {
        "subtopic": "Driving and Hypoglycemia",
        "scenario": "A 32-year-old truck driver with type 1 diabetes has had 2 severe hypoglycemic episodes in the past 6 months, including one while driving (minor accident, no injuries). He holds a commercial driver's license. He asks about driving regulations.",
        "stem": "What are the Australian driving requirements regarding hypoglycemia and diabetes?",
        "options": {
            "A": "No restrictions - can continue driving immediately",
            "B": "Commercial drivers: conditional license - must not have had severe hypoglycemia requiring assistance in past 12 months; must check glucose before and every 2 hours during driving; private license: must report severe hypos to licensing authority",
            "C": "All diabetics are permanently banned from commercial driving",
            "D": "Only need to report if glucose <2.0 mmol/L"
        },
        "correct_answer": "B",
        "explanation": "Australian driving standards (Austroads guidelines) for diabetes: Private (Class C) license: (1) Must have awareness of hypoglycemia; (2) Must not have had severe hypoglycemia requiring assistance while driving in past 12 months; (3) Must report severe hypos to licensing authority - may need medical review; (4) Check glucose before driving if on insulin/sulfonylureas; (5) Do not drive if glucose <5.0 mmol/L. Commercial (Class HC, MC) license: More stringent: (1) No severe hypoglycemia requiring assistance in past 12 months; (2) Check glucose before driving and every 2 hours during driving; (3) Annual specialist diabetes review; (4) Documented hypoglycemia awareness; (5) Regular BGM monitoring. This patient: severe hypos in past 6 months (including while driving) - does NOT meet commercial license standards currently. Management: (1) Notify licensing authority; (2) Commercial license suspended until 12 months hypo-free; (3) Optimize diabetes management (relaxed targets, CGM, education); (4) After 12 months hypo-free + specialist clearance: may reapply. Private driving: suspension variable by state, often 3-6 months after severe hypo. Legal obligation: healthcare providers must advise patients of driving restrictions; patients must notify licensing authority."
    },

    "ENDO-MCQ-0059": {
        "subtopic": "Factitious Hypoglycemia",
        "scenario": "A 28-year-old nurse with no history of diabetes presents with recurrent severe hypoglycemic episodes requiring hospital admission. During a supervised fast, glucose falls to 2.1 mmol/L with simultaneous blood tests showing: insulin 250 pmol/L (elevated), C-peptide 110 pmol/L (low/suppressed), negative sulfonylurea screen.",
        "stem": "What is the most likely diagnosis?",
        "options": {
            "A": "Insulinoma",
            "B": "Factitious hypoglycemia from exogenous insulin administration",
            "C": "Adrenal insufficiency",
            "D": "Laboratory error"
        },
        "correct_answer": "B",
        "explanation": "Factitious hypoglycemia: Deliberate self-administration of insulin or sulfonylureas causing hypoglycemia. Risk factors: healthcare workers, access to diabetes medications, psychiatric history, attention-seeking behavior. Biochemistry patterns: Exogenous insulin: High insulin + Low C-peptide (exogenous insulin suppresses endogenous production); Insulin antibodies may be present if animal insulin used; Sulfonylurea: High insulin + High C-peptide + Positive sulfonylurea screen. Endogenous hyperinsulinism (insulinoma): High insulin + High C-peptide + High proinsulin. This patient: elevated insulin but suppressed C-peptide - diagnostic of exogenous insulin use. C-peptide suppressed because exogenous insulin inhibits endogenous insulin secretion. Management: (1) Confirm diagnosis (repeat testing, insulin antibodies, check for injection sites); (2) Psychiatric evaluation essential; (3) Address underlying psychiatric disorder; (4) Restrict access to insulin; (4) Multidisciplinary approach (endocrinology, psychiatry, ethics); (5) Document thoroughly. Prognosis: Difficult condition; high recurrence; requires long-term psychiatric follow-up. Differential: Autoimmune hypoglycemia (insulin antibodies causing glucose dysregulation, rare, more common in Asia), but typically high C-peptide. Clues to factitious: healthcare background, unexplained hypos, psychiatric history, suppressed C-peptide."
    },

    "ENDO-MCQ-0060": {
        "subtopic": "Glucagon Emergency Kit",
        "scenario": "A 16-year-old boy with type 1 diabetes is prescribed glucagon emergency kit. His parents ask when and how to use it, and about side effects.",
        "stem": "What is the correct information about glucagon use?",
        "options": {
            "A": "Use only if glucose <1.0 mmol/L",
            "B": "Use when patient unconscious or having seizure due to hypoglycemia and unable to take oral glucose safely; dose 1mg IM/SC (0.5mg if <25kg); place in recovery position; expect vomiting; give oral carbohydrate once conscious; call ambulance; recheck glucose in 10-15 minutes",
            "C": "Give orally dissolved in water",
            "D": "Glucagon has no side effects"
        },
        "correct_answer": "B",
        "explanation": "Glucagon emergency kit information: Indications: (1) Severe hypoglycemia with unconsciousness or seizure; (2) Patient unable to safely swallow oral glucose; (3) No IV access available. Mechanism: Stimulates hepatic glycogenolysis, raises glucose in 10-15 minutes. Dose: (1) Adults and children >25kg: 1mg IM or SC; (2) Children <25kg: 0.5mg. Administration: (1) Glucagon comes as powder + diluent, requires reconstitution (takes ~1 minute); (2) Inject IM into deltoid, thigh, or gluteal muscle; (3) Place patient in recovery position (risk of vomiting - aspiration prevention); (4) Call ambulance (000); (5) Recheck glucose 10-15 minutes - expect rise to >4 mmol/L; (6) Once conscious and able to swallow: give oral glucose then longer-acting carbohydrate; (7) Monitor closely - may need repeat treatment or IV dextrose. Side effects: (1) Nausea and vomiting (very common - 50%); (2) Headache; (3) Transient hyperglycemia. Limitations: (1) Ineffective if glycogen depleted (starvation, alcohol, liver disease); (2) Duration of action 60-90 minutes; (3) Requires training to use. Education: All caregivers/family should know how to use glucagon kit; practice with expired kits recommended. Storage: Room temperature, check expiry date annually. Newer options: Intranasal glucagon powder (no reconstitution needed), pre-filled pens."
    }
}


if __name__ == "__main__":
    file_path = "data/mcqs/missing_topics_comprehensive_mcqs.json"

    print("="*70)
    print("MCQ BATCH 6A UPDATE - Claude Code Generated Content")
    print("="*70)
    print(f"Batch 6A: ENDO-MCQ-0041 to 0060 (DKA continued + Hypoglycemia)")
    print(f"Sub-batch 1 of 5 in Batch 6 (100 MCQs total)")
    print("="*70 + "\n")

    updated = update_mcq_batch(file_path, batch6a_generated)

    print(f"\n✅ Batch 6A Complete: {updated}/20 MCQs updated")
    print(f"✅ Total Progress: 60/658 MCQs (9.1%)")
    print(f"\n🔄 Batch 6 Progress: 20/100 complete")
    print(f"Next: Batch 6B (MCQs 0061-0080 - Thyroid Nodules + Adrenal)")
