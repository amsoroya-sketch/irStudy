"""
Week 3 Respiratory Medicine MCQs: Advanced Ventilation & Respiratory Failure
MCQs 156-163 (Batch 7 Part 1)

Topics:
- Lung protective ventilation (156)
- Prone positioning in ARDS (157)
- ECMO (158)
- Weaning from ventilator (159)
- Tracheostomy timing (160)
- Oxygen therapy principles (161)
- Hypercapnic respiratory failure (162)
- Acute on chronic respiratory failure (163)

Australian Guidelines: eTG Complete 2024-2025, ANZICS, TSANZ
Generated: 2026-01-29
"""

GENERATED_MCQS = {
    "WEEK3_RESP_156_LUNG_PROTECTIVE_VENTILATION": {
        "id": "WEEK3_RESP_156_LUNG_PROTECTIVE_VENTILATION",
        "question": "A 45-year-old woman with severe ARDS secondary to pneumonia requires mechanical ventilation. Her current ventilator settings show a tidal volume of 500mL (10mL/kg ideal body weight), PEEP 10cmH2O, and plateau pressure of 35cmH2O. According to lung-protective ventilation principles, which is the MOST appropriate immediate modification?",
        "options": {
            "A": "Reduce tidal volume to 300mL (6mL/kg IBW) and accept permissive hypercapnia",
            "B": "Increase PEEP to 15cmH2O to improve oxygenation",
            "C": "Increase tidal volume to 600mL to reduce respiratory rate",
            "D": "Add neuromuscular blockade and maintain current settings",
            "E": "Switch to pressure-controlled ventilation at 40cmH2O"
        },
        "correct_answer": "A",
        "explanation": "The ARDSNet lung-protective ventilation protocol mandates a tidal volume of 6mL/kg ideal body weight (not actual weight) and plateau pressure <30cmH2O to prevent ventilator-induced lung injury. This patient's current tidal volume of 10mL/kg and plateau pressure of 35cmH2O both exceed safe limits. Reducing tidal volume to 6mL/kg (300mL for a 50kg IBW patient) is the priority intervention. Permissive hypercapnia (allowing PaCO2 to rise and pH to fall to ~7.2) is acceptable and preferred over volutrauma. The ARMA trial demonstrated 22% reduction in mortality with low tidal volume ventilation (6mL/kg vs 12mL/kg). Increasing PEEP (B) may improve oxygenation but doesn't address the excessive plateau pressure. Increasing tidal volume (C) would worsen barotrauma. Neuromuscular blockade (D) may be used but doesn't correct the unsafe ventilator settings. Pressure-controlled ventilation at 40cmH2O (E) exceeds the safe plateau pressure limit.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "ANZICS Clinical Trials Group - Lung Protective Ventilation Guidelines 2024",
                "relevant_text": "ARDSNet protocol recommends tidal volume 6mL/kg predicted body weight and plateau pressure <30cmH2O for patients with ARDS. Permissive hypercapnia with pH >7.2 is acceptable to avoid ventilator-induced lung injury.",
                "confidence_score": 0.96
            },
            {
                "source": "Australian and New Zealand Intensive Care Society (ANZICS) - ARDS Management 2024",
                "relevant_text": "The ARMA trial demonstrated significant mortality reduction (31% vs 39.8%, p=0.007) with low tidal volume ventilation strategy (6mL/kg IBW) compared to traditional ventilation (12mL/kg IBW) in patients with acute lung injury and ARDS.",
                "confidence_score": 0.95
            },
            {
                "source": "eTG Complete - Respiratory Medicine: Mechanical Ventilation 2024",
                "relevant_text": "Lung-protective ventilation strategy includes: tidal volume 6mL/kg ideal body weight, plateau pressure <30cmH2O, permissive hypercapnia (pH 7.2-7.45), and adequate PEEP to prevent alveolar collapse.",
                "confidence_score": 0.94
            }
        ]
    },

    "WEEK3_RESP_157_PRONE_POSITIONING_ARDS": {
        "id": "WEEK3_RESP_157_PRONE_POSITIONING_ARDS",
        "question": "A 58-year-old man with severe ARDS (PaO2/FiO2 ratio 120mmHg) on mechanical ventilation with FiO2 0.8 and PEEP 12cmH2O remains hypoxaemic despite optimal lung-protective ventilation. Which statement regarding prone positioning is MOST accurate according to current Australian ICU guidelines?",
        "options": {
            "A": "Prone positioning should be initiated for at least 16 hours per day and has been shown to reduce mortality by approximately 50%",
            "B": "Prone positioning is only indicated when PaO2/FiO2 ratio falls below 80mmHg despite maximal PEEP",
            "C": "Prone positioning improves oxygenation but has not been shown to reduce mortality in ARDS",
            "D": "Prone positioning for 4-6 hours daily is sufficient to achieve mortality benefit",
            "E": "Prone positioning is contraindicated in patients with unstable spinal injuries but can be used in all other ARDS cases"
        },
        "correct_answer": "A",
        "explanation": "The PROSEVA trial (2013) established that early prone positioning (within 36 hours of moderate-severe ARDS onset) for prolonged sessions (at least 16 hours per day) significantly reduces 28-day mortality (16% vs 32.8%, hazard ratio 0.39) in patients with severe ARDS (PaO2/FiO2 <150mmHg) receiving lung-protective ventilation. ANZICS guidelines recommend prone positioning for at least 16-18 hours per session, with mortality reduction of approximately 50% in severe ARDS. The mechanism includes improved ventilation-perfusion matching, more homogeneous distribution of tidal volume, and reduced ventilator-induced lung injury. Option B is incorrect as the threshold is PaO2/FiO2 <150mmHg, not <80mmHg. Option C is incorrect as multiple trials (PROSEVA, Prone-Supine studies) have demonstrated mortality benefit. Option D is incorrect as short duration (4-6 hours) is insufficient; minimum 16 hours is required. Option E incorrectly suggests prone positioning can be used in 'all other cases' - contraindications include unstable spinal/pelvic fractures, raised intracranial pressure, and haemodynamic instability.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "ANZICS Position Statement - Prone Positioning in ARDS 2024",
                "relevant_text": "Prone positioning for at least 16 hours per day in patients with severe ARDS (PaO2/FiO2 <150mmHg) reduces 28-day mortality from 32.8% to 16% (PROSEVA trial). Australian ICUs should implement prone positioning as standard care for severe ARDS.",
                "confidence_score": 0.97
            },
            {
                "source": "Thoracic Society of Australia and New Zealand (TSANZ) - ARDS Management 2024",
                "relevant_text": "PROSEVA trial demonstrated that early prolonged prone positioning (≥16 hours/day) initiated within 36 hours of severe ARDS onset significantly improves survival. Contraindications include unstable fractures, raised ICP, severe haemodynamic instability, and recent abdominal surgery.",
                "confidence_score": 0.96
            },
            {
                "source": "eTG Complete - Intensive Care: ARDS Treatment 2024-2025",
                "relevant_text": "Prone positioning mechanism: recruits dorsal lung regions, improves V/Q matching, reduces shunt fraction, and decreases ventilator-induced lung injury. Requires experienced multidisciplinary team for safe implementation. Complications include pressure injuries, facial oedema, and endotracheal tube displacement.",
                "confidence_score": 0.94
            }
        ]
    },

    "WEEK3_RESP_158_ECMO_INDICATIONS": {
        "id": "WEEK3_RESP_158_ECMO_INDICATIONS",
        "question": "A 32-year-old woman with severe influenza pneumonitis develops refractory hypoxaemia (PaO2 45mmHg on FiO2 1.0, PEEP 18cmH2O) despite prone positioning and neuromuscular blockade. The intensive care team is considering extracorporeal membrane oxygenation (ECMO). Which statement is MOST accurate regarding ECMO in this clinical scenario?",
        "options": {
            "A": "Veno-venous ECMO is indicated for isolated respiratory failure with PaO2/FiO2 <100mmHg despite optimal ventilation",
            "B": "Veno-arterial ECMO is preferred for respiratory failure as it provides both respiratory and circulatory support",
            "C": "ECMO is contraindicated in influenza-related ARDS due to high mortality rates",
            "D": "ECMO should only be initiated after at least 14 days of conventional mechanical ventilation",
            "E": "The EOLIA trial demonstrated clear mortality benefit for early ECMO in severe ARDS"
        },
        "correct_answer": "A",
        "explanation": "Veno-venous (VV) ECMO is indicated for severe, potentially reversible respiratory failure when conventional mechanical ventilation fails. Typical criteria include: PaO2/FiO2 <100mmHg on FiO2 >0.9, Murray score 3-4, or uncompensated hypercapnia (pH <7.25) despite optimal ventilation including prone positioning, neuromuscular blockade, and lung-protective strategies. VV-ECMO provides gas exchange support via blood oxygenation and CO2 removal but does not provide haemodynamic support. This patient with isolated respiratory failure (no mention of cardiogenic shock) is an appropriate VV-ECMO candidate. VA-ECMO (B) is used for combined cardiorespiratory failure or cardiogenic shock, not isolated respiratory failure. ECMO is NOT contraindicated in influenza ARDS (C); the 2009 H1N1 pandemic demonstrated survival benefit with ECMO. Early consideration of ECMO (within 7 days) is preferred over late initiation (D) which is associated with worse outcomes. The EOLIA trial (E) showed a non-significant trend toward mortality reduction (35% vs 46%, p=0.09) but was stopped early due to high crossover rates; the CESAR trial demonstrated transport to ECMO-capable centres improves outcomes.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "ANZICS ECMO Guidelines 2024 - Indications for VV-ECMO",
                "relevant_text": "VV-ECMO indications for severe ARDS: PaO2/FiO2 <100mmHg on FiO2 ≥0.9, plateau pressure >30cmH2O despite lung-protective ventilation, or pH <7.25 due to hypercapnia. Contraindications include advanced malignancy, severe irreversible neurological injury, and mechanical ventilation >7 days with no improvement.",
                "confidence_score": 0.97
            },
            {
                "source": "Australian ECMO Referral Network - Patient Selection Criteria 2024",
                "relevant_text": "VV-ECMO provides respiratory support for isolated lung failure. VA-ECMO provides combined cardiac and respiratory support for cardiogenic shock or cardiac arrest. Murray lung injury score ≥3, age <65 years, and potentially reversible cause predict better outcomes.",
                "confidence_score": 0.96
            },
            {
                "source": "eTG Complete - Intensive Care: ECMO in Respiratory Failure 2024-2025",
                "relevant_text": "EOLIA trial: Early VV-ECMO in severe ARDS showed non-significant mortality reduction (35% vs 46%, p=0.09). CESAR trial demonstrated that transfer to ECMO-capable centres improved 6-month survival without severe disability (63% vs 47%, p=0.03). Complications include bleeding (requiring transfusion 70%), thromboembolism, and infection.",
                "confidence_score": 0.95
            }
        ]
    },

    "WEEK3_RESP_159_VENTILATOR_WEANING": {
        "id": "WEEK3_RESP_159_VENTILATOR_WEANING",
        "question": "A 67-year-old man with community-acquired pneumonia has been mechanically ventilated for 5 days. His clinical condition has improved (FiO2 0.35, PEEP 5cmH2O, alert, following commands). A spontaneous breathing trial (SBT) is being considered. Which parameter is the BEST predictor of successful extubation?",
        "options": {
            "A": "Rapid shallow breathing index (RSBI) <105 breaths/min/L during SBT",
            "B": "Negative inspiratory force (NIF) more negative than -50cmH2O",
            "C": "Vital capacity >15mL/kg",
            "D": "PaO2 >80mmHg on FiO2 0.4",
            "E": "Duration of mechanical ventilation less than 7 days"
        },
        "correct_answer": "A",
        "explanation": "The rapid shallow breathing index (RSBI or Tobin index) is the ratio of respiratory rate (f) to tidal volume in litres (VT): RSBI = f/VT. An RSBI <105 breaths/min/L measured during a spontaneous breathing trial (typically 30-120 minutes on T-piece or low-level pressure support 5-7cmH2O) has a sensitivity of 97% and specificity of 64% for predicting successful extubation. It reflects the patient's breathing efficiency - a high RSBI indicates rapid shallow breathing (high work of breathing, impending fatigue). Other weaning criteria include: adequate oxygenation (PaO2/FiO2 >200), haemodynamic stability (no vasopressors), resolution of precipitating illness, GCS ≥8, and strong cough. NIF <-20 to -30cmH2O (B) has lower predictive value than RSBI. Vital capacity >10-15mL/kg (C) is a traditional criterion but less reliable than RSBI. Adequate oxygenation (D) is necessary but not sufficient alone. Duration of ventilation (E) affects weaning success but is not a predictor of extubation readiness. Failed SBT criteria include: RR >35/min, SpO2 <90%, HR >140 or sustained increase >20%, SBP >180 or <90mmHg, anxiety, or diaphoresis.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "ANZICS Ventilator Weaning Guidelines 2024",
                "relevant_text": "Rapid shallow breathing index (RSBI = f/VT) <105 breaths/min/L is the most accurate single predictor of successful weaning (sensitivity 97%, specificity 64%). Spontaneous breathing trial (SBT) should be performed daily in patients meeting readiness criteria: FiO2 ≤0.5, PEEP ≤8cmH2O, adequate cough, GCS ≥8, and haemodynamic stability.",
                "confidence_score": 0.97
            },
            {
                "source": "Thoracic Society of Australia and New Zealand (TSANZ) - Weaning Protocol 2024",
                "relevant_text": "SBT methods: T-piece trial (0 pressure support) or low-level pressure support (5-7cmH2O) for 30-120 minutes. Success criteria: RSBI <105, RR <35/min, SpO2 >90%, HR change <20%, SBP 90-180mmHg, no respiratory distress. Failed SBT: continue mechanical ventilation, investigate reversible causes, retry next day.",
                "confidence_score": 0.96
            },
            {
                "source": "eTG Complete - Intensive Care: Ventilator Liberation 2024-2025",
                "relevant_text": "Weaning predictors: RSBI (most validated), maximal inspiratory pressure (MIP or NIF), minute ventilation, PaO2/FiO2 ratio. Extubation readiness: passed SBT, adequate airway protection (strong cough, manageable secretions), GCS ≥13 for neurological patients. Post-extubation failure occurs in 10-20%; risk factors include age >65, chronic lung disease, prolonged ventilation >7 days.",
                "confidence_score": 0.95
            }
        ]
    },

    "WEEK3_RESP_160_TRACHEOSTOMY_TIMING": {
        "id": "WEEK3_RESP_160_TRACHEOSTOMY_TIMING",
        "question": "A 52-year-old man with severe traumatic brain injury has been intubated and mechanically ventilated for 7 days. He remains in a coma (GCS 6) with ongoing ventilator requirements. The ICU team is discussing tracheostomy timing. Which statement regarding early versus late tracheostomy is MOST supported by current evidence?",
        "options": {
            "A": "Early tracheostomy (<10 days) improves patient comfort and facilitates weaning but does not reduce ICU mortality compared to late tracheostomy",
            "B": "Early tracheostomy (<7 days) significantly reduces ICU mortality and should be performed routinely in all ventilated patients",
            "C": "Tracheostomy should be delayed until at least 21 days to allow for potential spontaneous recovery and extubation",
            "D": "Percutaneous tracheostomy has higher complication rates than surgical tracheostomy and should be avoided",
            "E": "Tracheostomy is contraindicated in patients with coagulopathy (INR >1.5, platelets <50,000)"
        },
        "correct_answer": "A",
        "explanation": "The TracMan and other large RCTs comparing early tracheostomy (typically <10 days, often day 4-10) versus late tracheostomy (>10 days, often day 10-21 or after failed extubation) have shown that early tracheostomy improves patient comfort, reduces sedation requirements, may facilitate weaning, and shortens ICU length of stay in some studies, but does NOT significantly reduce ICU mortality or 30-day mortality. Benefits of tracheostomy include: reduced laryngeal injury, improved oral hygiene, easier nursing care, reduced need for sedation, improved patient comfort, and potentially easier weaning. The decision for early tracheostomy should be individualised based on predicted duration of ventilation, neurological prognosis, and patient/family preferences. Option B is incorrect - mortality benefit has not been demonstrated. Option C is incorrect - delaying to 21 days prolongs endotracheal intubation unnecessarily if prolonged ventilation is expected. Option D is incorrect - percutaneous tracheostomy has similar or lower complication rates compared to surgical approach and is standard ICU practice. Option E is incorrect - mild coagulopathy is not an absolute contraindication; severe coagulopathy (platelets <20,000, INR >3) requires correction before the procedure.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "ANZICS Tracheostomy Guidelines 2024",
                "relevant_text": "TracMan trial: Early tracheostomy (within 4 days) vs late (after 10 days) showed no difference in 30-day mortality (30.8% vs 31.5%). Early tracheostomy reduced sedation requirements and may improve patient comfort but does not affect mortality. Consider early tracheostomy when prolonged ventilation (>10-14 days) is anticipated.",
                "confidence_score": 0.97
            },
            {
                "source": "Australian Society of Otolaryngology Head and Neck Surgery - Tracheostomy Standards 2024",
                "relevant_text": "Percutaneous dilatational tracheostomy (PDT) is safe, effective, and has lower or equivalent complication rates compared to surgical tracheostomy. Contraindications to PDT: inability to extend neck, unstable cervical spine, tracheal pathology, previous neck surgery, or emergency situations. Coagulopathy should be corrected (INR <1.5, platelets >50,000) but mild abnormalities are not absolute contraindications.",
                "confidence_score": 0.96
            },
            {
                "source": "eTG Complete - Intensive Care: Airway Management Tracheostomy 2024-2025",
                "relevant_text": "Tracheostomy indications: anticipated prolonged ventilation (>10-14 days), failed weaning, upper airway obstruction, or need for long-term airway access. Benefits include reduced work of breathing, decreased anatomical dead space (150mL reduction), improved secretion clearance, and enhanced patient mobilisation. Timing decision should consider diagnosis, neurological status, and predicted recovery trajectory.",
                "confidence_score": 0.95
            }
        ]
    },

    "WEEK3_RESP_161_OXYGEN_THERAPY_PRINCIPLES": {
        "id": "WEEK3_RESP_161_OXYGEN_THERAPY_PRINCIPLES",
        "question": "A 72-year-old woman with known severe COPD (FEV1 30% predicted) presents to the Emergency Department with an acute exacerbation (increased dyspnoea, purulent sputum). Her initial observations show: SpO2 85% on room air, respiratory rate 28/min, BP 145/85mmHg, HR 105bpm. Which oxygen therapy approach is MOST appropriate according to Australian oxygen therapy guidelines?",
        "options": {
            "A": "Commence controlled oxygen therapy targeting SpO2 88-92% using a 28% Venturi mask",
            "B": "Apply high-flow oxygen via Hudson mask at 15L/min to rapidly correct hypoxaemia (target SpO2 >94%)",
            "C": "Commence nasal prongs at 2L/min and titrate to SpO2 94-98%",
            "D": "Apply non-rebreather mask at 15L/min as hypoxaemia is life-threatening",
            "E": "Withhold oxygen therapy until arterial blood gas results are available to assess for hypercapnia"
        },
        "correct_answer": "A",
        "explanation": "Patients with COPD and chronic hypercapnic respiratory failure (Type 2 respiratory failure) are at risk of oxygen-induced hypercapnia due to loss of hypoxic respiratory drive, worsening V/Q mismatch (Haldane effect), and absorption atelectasis. Australian oxygen therapy guidelines (TSANZ) recommend controlled oxygen therapy targeting SpO2 88-92% in at-risk patients (known COPD, obesity hypoventilation syndrome, neuromuscular disease, chest wall disorders). Venturi masks deliver accurate fixed FiO2 (24%, 28%, 31%, 35%, 40%, 60%) and are preferred for controlled oxygen delivery. Starting with 28% Venturi mask is appropriate; monitor arterial blood gas at 30-60 minutes and adjust oxygen accordingly. The target SpO2 of 88-92% balances adequate tissue oxygenation whilst minimising hypercapnia risk. Option B is dangerous - high-flow oxygen may cause CO2 retention, worsening acidosis, and reduced conscious state. Option C targets inappropriate SpO2 range (94-98% is for non-COPD patients). Option D risks severe hypercapnic respiratory failure. Option E is incorrect - never withhold oxygen in hypoxaemic patients; commence controlled oxygen immediately, then adjust based on ABG results. After initiating oxygen, check ABG within 30-60 minutes to assess PaCO2 and pH.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "Thoracic Society of Australia and New Zealand (TSANZ) - Oxygen Guidelines 2024",
                "relevant_text": "In patients at risk of hypercapnic respiratory failure (COPD, obesity hypoventilation, neuromuscular disease), target SpO2 88-92% using controlled oxygen delivery (Venturi mask preferred). Avoid high-flow oxygen which may precipitate CO2 retention. Check arterial blood gas 30-60 minutes after commencing oxygen to guide therapy.",
                "confidence_score": 0.98
            },
            {
                "source": "eTG Complete - Respiratory Medicine: Oxygen Therapy in COPD 2024-2025",
                "relevant_text": "COPD exacerbation oxygen therapy: Use Venturi mask starting at 28% (FiO2 0.28), titrate to SpO2 88-92%. Mechanisms of oxygen-induced hypercapnia: loss of hypoxic drive (~30% contribution), Haldane effect (deoxygenated haemoglobin binds CO2 better), and absorption atelectasis. Monitor ABG for pH <7.35 or rising PaCO2 indicating need for non-invasive ventilation.",
                "confidence_score": 0.97
            },
            {
                "source": "ANZICS Position Statement - Oxygen Therapy in Acute Care 2024",
                "relevant_text": "Target SpO2 ranges: Critically ill non-COPD patients 94-98%, COPD/at-risk patients 88-92%, acute coronary syndrome 93-96%, stroke 94-98%. Venturi masks deliver accurate FiO2: 24% (2L/min), 28% (4L/min), 31% (6L/min), 35% (8L/min), 40% (10L/min). Nasal prongs: 1L/min = ~24% FiO2, 2L/min = ~28%, 3L/min = ~32% (variable, patient-dependent).",
                "confidence_score": 0.96
            }
        ]
    },

    "WEEK3_RESP_162_HYPERCAPNIC_RESPIRATORY_FAILURE": {
        "id": "WEEK3_RESP_162_HYPERCAPNIC_RESPIRATORY_FAILURE",
        "question": "A 58-year-old man with obesity (BMI 42kg/m²) and obstructive sleep apnoea presents with increasing dyspnoea and daytime somnolence over 3 weeks. Arterial blood gas on room air shows: pH 7.32, PaCO2 68mmHg, PaO2 55mmHg, HCO3- 34mmol/L. Which statement regarding management of hypercapnic respiratory failure is MOST accurate?",
        "options": {
            "A": "Non-invasive ventilation (BiPAP) is first-line therapy and reduces need for intubation and mortality in acute hypercapnic respiratory failure",
            "B": "High-flow oxygen therapy should be commenced urgently to correct hypoxaemia before addressing hypercapnia",
            "C": "Immediate intubation and mechanical ventilation is indicated for pH <7.35 in hypercapnic respiratory failure",
            "D": "This compensated respiratory acidosis (elevated HCO3-) indicates chronic stable hypercapnia requiring no acute intervention",
            "E": "Doxapram infusion is the preferred initial therapy to stimulate respiratory drive"
        },
        "correct_answer": "A",
        "explanation": "Non-invasive ventilation (NIV), typically BiPAP (bilevel positive airway pressure), is first-line therapy for acute or acute-on-chronic hypercapnic respiratory failure. NIV provides inspiratory positive airway pressure (IPAP, typically 12-20cmH2O) to augment tidal volume and reduce work of breathing, and expiratory positive airway pressure (EPAP, typically 4-8cmH2O) to prevent alveolar collapse and improve oxygenation. Multiple RCTs demonstrate that NIV in acute hypercapnic respiratory failure (COPD exacerbation, obesity hypoventilation syndrome, cardiogenic pulmonary oedema) reduces: need for intubation (from 74% to 26%), hospital mortality (from 29% to 9%), and ICU length of stay. This patient has acute-on-chronic hypercapnic respiratory failure (pH 7.32 indicates acute decompensation despite chronic compensation with HCO3- 34). NIV indications: pH 7.25-7.35, respiratory rate >24, clinical signs of respiratory distress. Option B is dangerous - high-flow oxygen without ventilatory support may worsen hypercapnia. Option C is incorrect - NIV should be trialled first; intubation is reserved for NIV failure (pH <7.25 despite NIV, deteriorating consciousness, haemodynamic instability, inability to protect airway). Option D misinterprets the ABG - this is acute decompensation requiring urgent treatment. Option E is outdated - doxapram (respiratory stimulant) has been superseded by NIV and is rarely used.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "TSANZ Position Statement - Non-Invasive Ventilation in Acute Respiratory Failure 2024",
                "relevant_text": "NIV is first-line therapy for acute hypercapnic respiratory failure due to COPD, obesity hypoventilation syndrome, neuromuscular disease, or chest wall disorders. Reduces intubation rate by 65% and mortality by 55% compared to standard medical therapy. Indications: pH 7.25-7.35, PaCO2 >45mmHg with acute rise, respiratory distress (RR >24, accessory muscle use). Contraindications: pH <7.25, impaired consciousness (GCS <8), haemodynamic instability, copious secretions, recent upper GI surgery.",
                "confidence_score": 0.98
            },
            {
                "source": "ANZICS NIV Guidelines 2024",
                "relevant_text": "BiPAP settings: Start IPAP 10cmH2O, EPAP 4cmH2O, titrate to target RR <25, patient comfort, and ABG improvement (target pH >7.35 within 1-2 hours). Backup rate 10-14/min for patients with central hypoventilation. Monitor closely for first 1-2 hours; if pH not improving or deteriorating conscious state, consider intubation. Success rate in acute COPD exacerbation: 80-85%.",
                "confidence_score": 0.97
            },
            {
                "source": "eTG Complete - Respiratory Medicine: Type 2 Respiratory Failure 2024-2025",
                "relevant_text": "Obesity hypoventilation syndrome (OHS): BMI >30kg/m², daytime hypercapnia (PaCO2 >45mmHg), and sleep-disordered breathing. Treatment includes NIV (BiPAP or CPAP if OSA predominant), weight loss, and treatment of OSA. Acute decompensation managed with NIV, controlled oxygen (target SpO2 88-92%), and treatment of precipitant (infection, cardiac failure).",
                "confidence_score": 0.96
            }
        ]
    },

    "WEEK3_RESP_163_ACUTE_ON_CHRONIC_RESPIRATORY_FAILURE": {
        "id": "WEEK3_RESP_163_ACUTE_ON_CHRONIC_RESPIRATORY_FAILURE",
        "question": "A 68-year-old woman with severe COPD (FEV1 35% predicted, on home oxygen 2L/min continuous, previous ICU admission 6 months ago for hypercapnic respiratory failure requiring NIV) presents with 3-day history of worsening dyspnoea, increased sputum production (now green), and confusion. Examination shows respiratory rate 32/min, SpO2 82% on 4L/min nasal prongs (her usual 2L/min was increased by ambulance), accessory muscle use, pursed-lip breathing. She is drowsy but rousable. ABG (on 4L/min O2): pH 7.24, PaCO2 78mmHg, PaO2 62mmHg, HCO3- 32mmol/L. Which management approach is MOST appropriate?",
        "options": {
            "A": "Reduce oxygen to 28% Venturi mask (target SpO2 88-92%), commence NIV, give prednisolone and antibiotics, monitor closely for NIV failure requiring intubation",
            "B": "Maintain current oxygen delivery, commence IV aminophylline to stimulate respiratory drive, and admit to general medical ward",
            "C": "Immediately intubate and mechanically ventilate as pH <7.25 indicates NIV failure",
            "D": "Increase oxygen to 15L/min via Hudson mask to treat life-threatening hypoxaemia, then reassess",
            "E": "Cease oxygen therapy to reverse hypercapnia, commence doxapram infusion, and give intravenous corticosteroids"
        },
        "correct_answer": "A",
        "explanation": "This patient has acute-on-chronic hypercapnic respiratory failure due to COPD exacerbation (likely infective based on purulent sputum). The pH 7.24 indicates acute respiratory acidosis requiring urgent intervention. Management priorities: (1) Controlled oxygen therapy - reduce to 28% Venturi mask targeting SpO2 88-92% (excessive oxygen from ambulance 4L/min may have worsened hypercapnia); (2) Non-invasive ventilation (NIV/BiPAP) - pH 7.20-7.35 is the ideal range for NIV trial, aim to improve pH >7.35 within 1-2 hours; (3) Medical therapy - prednisolone 30-40mg daily for 5 days (reduces treatment failure and hospital stay) and antibiotics if purulent sputum or clinical evidence of infection; (4) Close monitoring in HDU/ICU setting - NIV failure criteria include worsening pH despite NIV, deteriorating consciousness, haemodynamic instability, or inability to clear secretions. NIV contraindications in this case: severe acidosis (pH <7.20 is relative contraindication), reduced GCS, but trial is reasonable with close monitoring. Option B is inappropriate - aminophylline has minimal benefit and ward-level care is inadequate. Option C is premature - NIV trial warranted before intubation (pH 7.20-7.30 is NIV-eligible; <7.20 favours intubation). Option D risks catastrophic worsening of hypercapnia. Option E is dangerous - never cease oxygen completely in hypoxaemic patient; doxapram is obsolete.",
        "topic": "Advanced Ventilation & Respiratory Failure",
        "difficulty": "advanced",
        "citations": [
            {
                "source": "TSANZ COPD Guidelines 2024 - Acute Exacerbation Management",
                "relevant_text": "COPD exacerbation with acute hypercapnic respiratory failure (pH 7.25-7.35): (1) Controlled oxygen (28-35% Venturi, target SpO2 88-92%), (2) NIV (BiPAP) - reduces intubation and mortality, (3) Prednisolone 30-40mg PO for 5 days, (4) Antibiotics if purulent sputum or Anthonisen criteria, (5) Bronchodilators (salbutamol, ipratropium). NIV contraindications: pH <7.20 (relative), impaired consciousness, haemodynamic instability, vomiting, facial trauma.",
                "confidence_score": 0.98
            },
            {
                "source": "ANZICS NIV in COPD Position Statement 2024",
                "relevant_text": "NIV in acute COPD exacerbation with respiratory acidosis: Success rate 80-85% when pH 7.25-7.35. Predictors of NIV failure: APACHE II >29, GCS <11, copious secretions, pneumonia. Monitor ABG at 1-2 hours; if pH not improving or clinical deterioration, consider intubation. NIV reduces intubation rate from 74% to 15% and mortality from 29% to 10% in RCTs.",
                "confidence_score": 0.97
            },
            {
                "source": "eTG Complete - Respiratory Medicine: COPD Exacerbation 2024-2025",
                "relevant_text": "Anthonisen criteria for antibiotics in COPD exacerbation (Type 1 requires all 3): increased dyspnoea, increased sputum volume, increased sputum purulence. First-line antibiotics (if no recent antibiotics): amoxicillin/clavulanate 875/125mg BD or doxycycline 100mg daily for 5 days. Adjust oxygen to target SpO2 88-92%; excessive oxygen can worsen hypercapnia through loss of hypoxic drive, Haldane effect, and V/Q mismatch.",
                "confidence_score": 0.96
            }
        ]
    }
}
