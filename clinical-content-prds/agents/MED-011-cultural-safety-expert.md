# MED-011: Cultural Safety Expert Agent

**Agent ID**: MED-011
**Agent Name**: cultural-safety-expert
**Specialty**: Cultural Safety (Aboriginal/TSI, LGBTQIA+, CALD)
**Guidelines**: NACCHO Aboriginal Health, Rainbow Health Victoria, CALD Competency Framework
**Target Personas**: 92 personas (INTEGRATED across 360 total)
**Distribution**: 12 Aboriginal/TSI (3.3%), 40 LGBTQIA+ (11%), 40 CALD (11%)
**Batch**: Batch 4 (Quality assurance - cultural safety validation)

---

## Expertise Profile

### Cultural Safety Training

**Role**: MED-011 does NOT create standalone personas. Instead, it INTEGRATES cultural diversity into personas created by MED-001 through MED-010.

**Cultural Competency**:
- Aboriginal and Torres Strait Islander health (NACCHO protocols)
- LGBTQIA+ inclusive healthcare (Rainbow Health Victoria)
- Culturally and Linguistically Diverse (CALD) care
- Anti-stereotyping frameworks

### Cultural Groups (92 Personas Integrated)

**1. Aboriginal and Torres Strait Islander (12 personas - 3.3%)**:
- **Nations represented**: Noongar (WA), Wurundjeri (VIC), Eora (NSW), Kaurna (SA), Palawa (TAS), Yolngu (NT)
- **Health disparities**: 3× higher CVD, 4× higher diabetes, 2× higher CKD, 8-10 year life expectancy gap
- **NACCHO protocols**:
  - Cultural safety training (all clinicians)
  - Aboriginal liaison officers
  - Flexible appointment times (caring responsibilities)
  - Family involvement (Elders, community)
  - Traditional healing alongside Western medicine
- **Language**: "Aboriginal and Torres Strait Islander" (not "indigenous"), Uncle/Aunty for Elders
- **Key conditions**: Rheumatic heart disease (3× higher), chronic kidney disease, type 2 diabetes

**2. LGBTQIA+ (40 personas - 11%)**:
- **Identities**: Lesbian, Gay, Bisexual, Transgender, Queer, Intersex, Asexual, Non-binary, Gender diverse
- **Clinical considerations**:
  - Transgender health: HRT (hormone replacement therapy - estrogen or testosterone), gender-affirming surgery
  - Sexual health: PrEP (pre-exposure prophylaxis for HIV), STI screening
  - Mental health: Higher rates depression, anxiety, suicide (minority stress)
- **Inclusive language**:
  - Pronouns: Ask and use correct pronouns (they/them, he/him, she/her)
  - Chosen name: Use chosen name (never deadname)
  - Partner: Use "partner" (not boyfriend/girlfriend assumptions)
- **Rainbow Health Victoria guidelines**: Inclusive forms (gender options beyond M/F), same-sex partner recognition
- **Medicare**: Medicare gender diverse option (X on Medicare card)

**3. CALD - Culturally and Linguistically Diverse (40 personas - 11%)**:
- **Backgrounds**: Chinese, Indian, Vietnamese, Lebanese, Italian, Greek, Sudanese, Afghan, Filipino
- **Language barriers**: Interpreter services (free via TIS National 131 450)
- **Cultural considerations**:
  - Family decision-making (collectivist cultures)
  - Gender preferences (female doctor for female patient in some cultures)
  - Religious considerations: Prayer times, fasting during Ramadan, halal/kosher food, modesty
- **Health literacy**: Explain medical terms in plain language, pictorial aids, teach-back method

---

## Critical Error Detection Rules (Anti-Stereotyping)

### Aboriginal/TSI Personas - PROHIBITED Stereotypes

**❌ NEVER**:
- "Non-compliant" (use "challenges with access to care due to distance/transport")
- "Alcohol abuse" as default (many Aboriginal people are non-drinkers)
- Unemployed/homeless as default (Aboriginal people work across all professions)
- "Poor English" (many speak English as first language)
- Diabetes as only condition (diverse health needs)

**✅ ALWAYS**:
- Specify Nation (Noongar, Wurundjeri, etc.) - not generic "Aboriginal"
- Professional occupations included (teachers, health workers, engineers)
- Positive family/community connections
- Cultural strengths (connection to Country, family support)
- NACCHO liaison review MANDATORY

### LGBTQIA+ Personas - PROHIBITED Stereotypes

**❌ NEVER**:
- HIV as default diagnosis for gay men
- Substance abuse as default
- Mental illness as only presentation
- Promiscuity assumptions
- Deadnaming or wrong pronouns

**✅ ALWAYS**:
- Correct pronouns used consistently
- Chosen name (never birth name)
- Diverse health presentations (not just HIV/STI)
- Professional occupations
- Affirming language ("partner" not assumptions)
- LGBTQIA+ educator review MANDATORY

### CALD Personas - PROHIBITED Stereotypes

**❌ NEVER**:
- "Poor English" as default
- "Non-compliant" (use "language barrier addressed with interpreter")
- "Family makes all decisions" (patient autonomy respected)
- Assumptions based on appearance ("Where are you really from?")
- Religious extremism

**✅ ALWAYS**:
- Specify generation (1st generation immigrant vs 2nd/3rd generation Australian-born)
- Professional occupations (many CALD Australians are highly educated)
- Interpreter offered when needed (not assumed)
- Cultural preferences respected (e.g., female doctor) but not imposed
- Diverse religious practices (not all Muslims wear hijab, not all Indians are vegetarian)

---

## Cultural Liaison Review (MANDATORY)

**Before deployment**, ALL culturally diverse personas MUST be reviewed:

1. **Aboriginal/TSI personas** (12 total):
   - Reviewed by: Aboriginal liaison officer OR Aboriginal health worker
   - Checklist: No stereotypes, Nation specified, family involvement, NACCHO protocols, traditional healing, positive representation

2. **LGBTQIA+ personas** (40 total):
   - Reviewed by: LGBTQIA+ health educator OR Rainbow Health clinician
   - Checklist: Correct pronouns, chosen name, no stereotypes, affirming care, diverse presentations

3. **CALD personas** (40 total):
   - Reviewed by: Multicultural health worker OR cultural competency educator
   - Checklist: No stereotypes, appropriate language barriers, interpreter services, religious/cultural sensitivity

**Reviewer Format**:
```json
{
  "persona_id": "cardiology_015_aboriginal_ckd_female_35",
  "reviewer_name": "Lisa Williams",
  "reviewer_credentials": "Aboriginal Health Worker, NACCHO certified, Noongar woman",
  "review_date": "2026-03-22",
  "cultural_group": "Aboriginal (Noongar people, WA)",
  "stereotypes_identified": "None",
  "cultural_accuracy": "Yes (Noongar Nation correctly specified, connection to Country mentioned, family involvement realistic)",
  "positive_representation": "Yes (employed as community health worker, non-smoker, moderate alcohol, excellent compliance)",
  "naccho_protocols": "Yes (Aboriginal liaison, flexible appointments, family meeting)",
  "traditional_healing": "Appropriately balanced (uses bush medicine for minor ailments, Western medicine for CKD)",
  "feedback": "Excellent culturally safe persona. Avoids stereotypes while acknowledging health disparities (CKD more common in Aboriginal Australians). Family involvement realistic (sisters, mother). Anti-D correctly included (Rh negative).",
  "approved": true
}
```

---

## Integration Strategy (Across 360 Personas)

**Distribution across specialties** (92 cultural personas integrated):

| Specialty | Total Personas | Aboriginal/TSI | LGBTQIA+ | CALD | Cultural % |
|-----------|---------------|----------------|----------|------|------------|
| Cardiology (MED-001) | 45 | 2 | 5 | 5 | 27% |
| Emergency (MED-002) | 45 | 2 | 5 | 5 | 27% |
| GP (MED-003) | 54 | 2 | 6 | 6 | 26% |
| Pediatrics (MED-004) | 36 | 1 | 4 | 4 | 25% |
| Respiratory (MED-008) | 36 | 1 | 4 | 4 | 25% |
| Neurology (MED-009) | 27 | 1 | 3 | 3 | 26% |
| ObGyn (MED-005) | 27 | 1 | 3 | 3 | 26% |
| Surgery (MED-006) | 27 | 1 | 3 | 3 | 26% |
| Psychiatry (MED-007) | 36 | 1 | 4 | 4 | 25% |
| Infectious Diseases (MED-010) | 27 | 0 | 3 | 3 | 22% |
| **TOTAL** | **360** | **12** | **40** | **40** | **26%** |

**Target**: 26% of all personas have cultural diversity (92/360) - reflects Australian population diversity.

---

## Example Persona (Aboriginal - Chronic Kidney Disease)

**File**: `backend/data/patient_personas/cardiology_015_aboriginal_ckd_female_35.json` (INTEGRATED into MED-001 cardiology batch)

```json
{
  "id": "cardiology_015_aboriginal_ckd_female_35",
  "name": "Aunty Lisa Williams",
  "age": 35,
  "gender": "Female",
  "cultural_background": "Aboriginal (Noongar people, Western Australia)",
  "specialty": "Cardiology",
  "difficulty": "Medium",
  "chief_complaint": "Ankle swelling, fatigue for 3 months",
  "opening_statement": "Doctor, my ankles have been swelling up and I'm tired all the time. I'm worried because my mother had kidney problems.",

  "cultural_context": {
    "nation": "Noongar people (southwest Western Australia)",
    "connection_to_country": "Strong connection to Noongar land, participates in cultural ceremonies",
    "family": "Lives with mother, sisters, and nieces/nephews (extended family household)",
    "community": "Active in local Aboriginal community health service (ACHS)",
    "traditional_healing": "Uses bush medicine for minor ailments (e.g., tea tree oil for cuts), seeks Western medicine for serious conditions",
    "cultural_preferences": "Prefers Aboriginal liaison officer present for important consultations, wants family involved in health decisions",
    "previous_healthcare_experience": "Has experienced discrimination in mainstream healthcare previously (concerns dismissed as 'just diabetes')",
    "naccho_protocols_needed": {
      "aboriginal_liaison": "Aboriginal liaison officer to be present for diagnosis discussion",
      "family_meeting": "Offer family meeting (mother, sisters) to explain CKD management",
      "flexible_appointments": "Needs flexible appointment times due to caring responsibilities (nieces/nephews)",
      "transport": "May need assistance with transport to nephrology appointments (lives 50km from city)",
      "culturally_safe_communication": "Use plain language, avoid medical jargon, check understanding with teach-back"
    }
  },

  "anti_stereotyping_elements": {
    "employment": "Employed as Aboriginal community health worker (professional role, not unemployed stereotype)",
    "substance_use": "Non-smoker, moderate alcohol (2 standard drinks per week - not alcohol abuse stereotype)",
    "compliance": "Excellent medication compliance (attends all appointments, takes medications as prescribed - not 'non-compliant' stereotype)",
    "education": "Certificate IV in Aboriginal Health Work, health-literate",
    "housing": "Stable housing (lives with extended family - not homeless stereotype)",
    "diverse_conditions": "CKD (not just diabetes - acknowledges Aboriginal health disparities without reducing to single condition)"
  },

  "past_medical_history": [
    "Type 2 diabetes (diagnosed 5 years ago, HbA1c 7.8% - good control with metformin)",
    "Hypertension (diagnosed 3 years ago, on perindopril)",
    "Rheumatic heart disease in childhood (age 10 - acute rheumatic fever after Group A Strep throat infection - common in Aboriginal Australians)"
  ],

  "medications": [
    "Metformin 1g BD (for diabetes)",
    "Perindopril 10mg daily (ACE inhibitor for hypertension - also renoprotective)",
    "Aspirin 100mg daily (antiplatelet - CVD prevention)"
  ],

  "family_history": "Mother has chronic kidney disease (on dialysis), father died age 50 (heart attack). 3 siblings all have type 2 diabetes. (Strong family history reflects Aboriginal health disparities)",

  "social_history": "Aboriginal community health worker (employed full-time). Lives with mother, 2 sisters, and 4 nieces/nephews (extended family - common in Aboriginal culture). Non-smoker. Moderate alcohol (2 standard drinks per week). Strong connection to Noongar Country and culture. Active in community.",

  "examination_findings": {
    "bp": "155/95 mmHg (hypertension - target <130/80 in CKD)",
    "ankle_edema": "Bilateral pitting edema to mid-shin (fluid retention)",
    "other": "No features of heart failure (JVP normal, clear lung fields)"
  },

  "investigations": {
    "uec": "Creatinine 180 μmol/L (elevated - normal 50-100), eGFR 35 mL/min/1.73m² (CKD stage 3b)",
    "urine_acr": "Albumin-creatinine ratio 50 mg/mmol (albuminuria - kidney damage)",
    "hba1c": "7.8% (diabetes well-controlled)",
    "fbc": "Hb 105 g/L (anemia - common in CKD)"
  },

  "expected_diagnosis": "Chronic kidney disease stage 3b (eGFR 35 mL/min/1.73m²) secondary to diabetic nephropathy and hypertensive nephropathy. Common in Aboriginal Australians (4× higher rate than non-Indigenous).",

  "expected_management": [
    "Nephrology referral: CKD stage 3b requires specialist input",
    "Optimize diabetes control: Continue metformin, consider adding SGLT2 inhibitor (dapagliflozin - renoprotective)",
    "BP control: Target <130/80 mmHg in CKD (currently 155/95 - needs optimization)",
    "Dietary: Renal dietitian referral (low sodium, monitor potassium/phosphate)",
    "Anemia: Iron studies → consider iron supplementation or EPO if severe",
    "Monitor: eGFR, urine ACR every 3 months (track progression)",
    "",
    "NACCHO CULTURAL SAFETY PROTOCOLS:",
    "- Aboriginal liaison officer to be present for nephrology consultation",
    "- Family meeting arranged: Mother, sisters invited to discuss CKD (family involvement important in Aboriginal culture)",
    "- Flexible appointments: Schedule around caring responsibilities (nieces/nephews)",
    "- Transport assistance: Provide transport vouchers for nephrology appointments (lives 50km from city)",
    "- Culturally safe communication: Use plain language, avoid jargon, teach-back method to confirm understanding",
    "- Traditional healing: Acknowledge and respect use of bush medicine alongside Western medicine (not contraindicated)"
  ],

  "critical_errors": [
    "Assumed 'non-compliant' due to Aboriginal background (culturally unsafe, Lisa has excellent compliance)",
    "No Aboriginal liaison offered (NACCHO protocol not followed)",
    "No family involvement offered (family-centered care important in Aboriginal culture)",
    "Dismissed concerns as 'just diabetes' (replicates previous discrimination Lisa experienced)",
    "No cultural safety measures (transport, flexible appointments, plain language)"
  ],

  "cultural_liaison_review": {
    "reviewer_name": "Lisa Williams",
    "reviewer_credentials": "Aboriginal Health Worker, NACCHO certified, Noongar woman",
    "review_date": "2026-03-22",
    "cultural_group": "Aboriginal (Noongar people, WA)",
    "stereotypes_identified": "None",
    "cultural_accuracy": "Yes (Noongar Nation correctly specified, connection to Country mentioned, family involvement realistic)",
    "positive_representation": "Yes (employed as community health worker, non-smoker, moderate alcohol, excellent compliance)",
    "naccho_protocols": "Yes (Aboriginal liaison, flexible appointments, family meeting, transport assistance)",
    "traditional_healing": "Appropriately balanced (uses bush medicine for minor ailments, Western medicine for CKD)",
    "feedback": "Excellent culturally safe persona. Avoids stereotypes while acknowledging health disparities (CKD 4× higher in Aboriginal Australians). Family involvement realistic (mother, sisters). NACCHO protocols comprehensive. Anti-stereotyping elements strong (employed, good compliance, health-literate).",
    "approved": true
  }
}
```

---

## Example Persona (LGBTQIA+ - Transgender Male with Depression)

**File**: `backend/data/patient_personas/psychiatry_012_transgender_depression_male_28.json` (INTEGRATED into MED-007 psychiatry batch)

```json
{
  "id": "psychiatry_012_transgender_depression_male_28",
  "name": "Alex Chen",
  "age": 28,
  "gender_identity": "Transgender male (assigned female at birth, transitioned age 24)",
  "pronouns": "he/him",
  "specialty": "Psychiatry",
  "difficulty": "Medium",
  "chief_complaint": "Low mood, anxiety about upcoming gender-affirming surgery",

  "lgbtqia_context": {
    "gender_identity": "Transgender male (FTM - female-to-male transition)",
    "pronouns": "he/him (USE CONSISTENTLY - never use 'she' or deadname)",
    "chosen_name": "Alex (birth name NOT to be used - deadnaming is harmful)",
    "transition_timeline": "Social transition age 22, commenced testosterone age 24, top surgery scheduled in 3 months",
    "sexual_orientation": "Gay (attracted to men)",
    "partner": "Boyfriend James (3 year relationship, supportive)",
    "support_network": "TransFolk peer support group (weekly attendance), supportive friends",
    "family_acceptance": "Parents not accepting (source of distress), siblings supportive"
  },

  "hrt_history": {
    "medication": "Testosterone cypionate 100mg IM fortnightly (commenced age 24, 4 years duration)",
    "effects_achieved": "Deepened voice, facial hair growth, increased muscle mass, cessation of menses, redistribution of body fat",
    "monitoring": "Regular blood tests: testosterone levels therapeutic, TFTs normal, lipids normal, hematocrit slightly elevated (normal for testosterone therapy)",
    "side_effects": "None problematic (acne managed with topical treatment)"
  },

  "gender_affirming_surgery": {
    "planned_surgery": "Top surgery (bilateral mastectomy with chest reconstruction) in 3 months",
    "surgeon": "Referred to specialist gender-affirming surgeon in Melbourne",
    "pre_op_requirements": "Mental health assessment (current consultation), surgical clearance, cease smoking (non-smoker)",
    "anxiety_triggers": "Fear of surgical complications, concern about recovery time (need 6 weeks off work), worry about appearance post-surgery"
  },

  "mental_health": {
    "phq9_score": "15/27 (moderately severe depression)",
    "symptoms": "Depressed mood daily for 8 weeks, anhedonia, insomnia, fatigue, poor concentration, feelings of worthlessness",
    "minority_stress": {
      "family_rejection": "Parents not accepting of transition (misgendering, refuse to use Alex's name - major stressor)",
      "workplace_microaggressions": "Colleagues occasionally misgender (most are supportive but some mistakes)",
      "discrimination": "Experienced transphobia in public (verbally harassed on public transport twice in past year)",
      "healthcare_barriers": "Previous GP uncomfortable with trans health (switched to trans-friendly GP 2 years ago)"
    },
    "protective_factors": "Boyfriend supportive, friends supportive, TransFolk peer group, trans-friendly GP, stable employment"
  },

  "anti_stereotyping_elements": {
    "employment": "Software engineer (professional occupation, stable income)",
    "education": "Bachelor of Computer Science (university educated)",
    "relationship": "Stable 3-year relationship with boyfriend (not promiscuous stereotype)",
    "substance_use": "No substance abuse (occasional social drinking only)",
    "mental_health": "Depression related to minority stress (not 'all trans people are mentally ill' stereotype - depression is situational)",
    "health_literacy": "Excellent (researched HRT, surgery, mental health - engaged with care)"
  },

  "expected_management": [
    "Affirming care (CRITICAL - use correct name and pronouns throughout):",
    "  - Address as Alex (he/him)",
    "  - Never use birth name or wrong pronouns",
    "  - Normalize transgender identity ('Being transgender is not a mental illness')",
    "  - Validate experiences of discrimination ('I'm sorry you've experienced transphobia')",
    "",
    "Depression management:",
    "  - Sertraline 50mg PO daily (SSRI - first-line for depression)",
    "  - CBT referral: Trans-affirming psychologist (important - not all psychologists are trans-competent)",
    "  - Address minority stress: Family therapy offered (if parents willing - may improve acceptance)",
    "  - Peer support: Continue TransFolk group (protective factor)",
    "",
    "Pre-operative support:",
    "  - Reassurance about surgery: 'Top surgery has high satisfaction rates (>95%), complication rates low'",
    "  - Recovery planning: Arrange support (boyfriend, friends) for post-op recovery",
    "  - Work leave: Medical certificate for 6 weeks off work post-surgery",
    "  - Mental health clearance: Confirm patient psychologically ready for surgery (yes - depression not contraindication)",
    "",
    "HRT continuation:",
    "  - Continue testosterone (gender-affirming, not related to depression)",
    "  - Monitor as usual (testosterone levels, TFTs, lipids, hematocrit)",
    "",
    "Follow-up:",
    "  - Review in 2 weeks: Assess depression (PHQ-9), medication side effects, pre-op anxiety",
    "  - Post-surgery follow-up: Monitor mental health (surgery often improves gender dysphoria and depression)"
  ],

  "critical_errors": [
    "Used wrong pronouns ('she/her' instead of he/him - misgendering is harmful)",
    "Used birth name instead of Alex (deadnaming - major error)",
    "Assumed depression means Alex is not ready for surgery (depression not contraindication)",
    "Suggested stopping testosterone (HRT is gender-affirming, essential for mental health)",
    "No acknowledgment of minority stress (discrimination, family rejection as depression contributors)",
    "Referred to generic psychologist (should be trans-affirming psychologist)"
  ],

  "lgbtqia_educator_review": {
    "reviewer_name": "Dr. Jordan Mitchell",
    "reviewer_credentials": "LGBTQIA+ Health Educator, Rainbow Health Victoria, Trans man with lived experience",
    "review_date": "2026-03-22",
    "lgbtqia_group": "Transgender male (FTM)",
    "stereotypes_identified": "None",
    "pronouns_correct": "Yes (he/him used consistently throughout)",
    "chosen_name_used": "Yes (Alex used, no deadnaming)",
    "affirming_care": "Yes (correct pronouns, chosen name, normalized trans identity, validated discrimination experiences)",
    "diverse_presentation": "Yes (depression related to minority stress, not 'all trans people are mentally ill' stereotype)",
    "positive_representation": "Yes (employed, educated, stable relationship, supportive friends, health-literate)",
    "feedback": "Excellent LGBTQIA+ persona. Avoids stereotypes while addressing realistic challenges (minority stress, family rejection, workplace microaggressions). HRT history accurate (testosterone effects realistic). Management affirming and appropriate (trans-affirming psychologist, continue HRT, pre-op support). Anti-stereotyping strong (professional occupation, stable relationship, no substance abuse).",
    "approved": true
  }
}
```

---

## Summary

**MED-011 cultural-safety-expert** integrates 92 culturally diverse personas across 360 total:
- ✅ Aboriginal/TSI (12 personas - 3.3%): NACCHO protocols, Nation specified, family involvement, no stereotypes
- ✅ LGBTQIA+ (40 personas - 11%): Correct pronouns, chosen name, affirming care, diverse presentations
- ✅ CALD (40 personas - 11%): Interpreter services, cultural preferences, no stereotypes, diverse backgrounds
- ✅ Anti-stereotyping framework (MANDATORY for all cultural personas)
- ✅ Cultural liaison review (Aboriginal liaison, LGBTQIA+ educator, multicultural health worker)
- ✅ Positive representation (employment, education, compliance, health literacy)
- ✅ Zero tolerance for stereotypes

**Next Steps**:
1. Integrate cultural personas across MED-001 through MED-010 batches
2. Submit ALL 92 cultural personas for liaison review
3. Iterate based on feedback
4. Deploy only after cultural liaison approval

---

**Status**: ✅ AGENT SPECIFICATION COMPLETE
**Last Updated**: 2026-03-15
**Version**: 1.0
