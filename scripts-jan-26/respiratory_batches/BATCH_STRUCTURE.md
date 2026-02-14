# Week 3 Respiratory MCQ Regeneration - Batch Structure

**Total MCQs**: 200
**Total Batches**: 8
**Status**: Planning complete, ready for generation

---

## Batch Structure Overview

### **Batch 1: Asthma & Early COPD (MCQs 001-025)** - 25 MCQs
**Topics**:
- Asthma diagnosis, severity, control (ACT score)
- Asthma management: SABA, ICS, ICS-LABA, montelukast
- Acute asthma exacerbation
- Special cases: pregnancy, exercise-induced, occupational, AERD
- COPD introduction: diagnosis, GOLD classification

**eTG References**: Respiratory section - Asthma, COPD

---

### **Batch 2: COPD Management & Bronchiectasis (MCQs 026-050)** - 25 MCQs
**Topics**:
- COPD management: LAMA, LABA-LAMA, triple therapy, roflumilast
- Pulmonary rehabilitation, LTOT, smoking cessation
- Alpha-1 antitrypsin deficiency, bullectomy, lung volume reduction
- Bronchiectasis, cystic fibrosis
- COPD phenotypes, COPD-asthma overlap
- Inhaler devices, spirometry, FeNO, biologics (omalizumab)

**eTG References**: Respiratory - COPD management, smoking cessation

---

### **Batch 3: Pneumonia & TB (MCQs 051-075)** - 25 MCQs
**Topics**:
- CAP: CURB-65, PSI, antibiotic choice (amoxicillin, doxycycline, macrolides)
- HAP, VAP, aspiration pneumonia
- Atypical pneumonia: Mycoplasma, Legionella, Chlamydophila
- PCP, influenza, COVID-19 pneumonia
- Complications: empyema, lung abscess
- Tuberculosis: screening, latent TB, active TB treatment

**eTG References**: Respiratory - Pneumonia, Tuberculosis, Infectious diseases

---

### **Batch 4: Infections & PE Diagnosis (MCQs 076-100)** - 25 MCQs
**Topics**:
- MDR-TB, TB contact tracing
- Vaccinations: pneumococcal, influenza, COVID-19, whooping cough
- Fungal pneumonia: aspergillosis, histoplasmosis
- URTI, sinusitis, pharyngitis, acute bronchitis
- Antibiotic stewardship
- PE diagnosis: Wells score, PERC rule, D-dimer, CTPA vs V/Q
- PE classification: massive vs submassive

**eTG References**: Respiratory - Infectious diseases, VTE diagnosis

---

### **Batch 5: PE/DVT Management (MCQs 101-125)** - 25 MCQs
**Topics**:
- Anticoagulation: heparin, LMWH, UFH, DOACs (rivaroxaban, apixaban)
- Thrombolysis, embolectomy, IVC filter
- DVT diagnosis: Wells score, compression ultrasound
- Duration of anticoagulation, recurrent VTE, unprovoked VTE
- Thrombophilia: Factor V Leiden, protein C, antiphospholipid syndrome
- Special cases: cancer VTE, pregnancy VTE, travel DVT
- VTE prophylaxis
- ILD introduction: classification, IPF, HRCT patterns (UIP, NSIP)

**eTG References**: Cardiovascular - VTE management

---

### **Batch 6: Interstitial Lung Disease (MCQs 126-150)** - 25 MCQs
**Topics**:
- Hypersensitivity pneumonitis
- Sarcoidosis: diagnosis, treatment
- Drug-induced ILD: amiodarone, methotrexate, nitrofurantoin
- Connective tissue ILD: rheumatoid, scleroderma, Sjögren, dermatomyositis
- Pneumoconiosis: asbestosis, silicosis, coal worker
- Eosinophilic pneumonia, COP, LAM, PAP
- Antifibrotic therapy (IPF)
- Respiratory failure: Type 1 vs 2, ARDS
- Mechanical ventilation, NIV

**eTG References**: Respiratory - ILD, ARDS

---

### **Batch 7: Ventilation & Pleural Disease (MCQs 151-175)** - 25 MCQs
**Topics**:
- BiPAP vs CPAP, OSA management
- Obesity hypoventilation syndrome
- Ventilator settings, PEEP, lung protective ventilation
- Prone positioning, ECMO, ventilator weaning, tracheostomy
- Oxygen therapy principles
- Hypercapnic respiratory failure, neuromuscular respiratory failure
- Chest wall disorders: kyphoscoliosis, flail chest
- Pneumothorax: spontaneous, tension, chest drain
- Pleural effusion: Light's criteria, exudate vs transudate
- Thoracentesis, pleural biopsy

**eTG References**: Respiratory - Pleural disease, Critical care

---

### **Batch 8: Lung Cancer & Pulmonary Diagnostics (MCQs 176-200)** - 25 MCQs
**Topics**:
- Malignant pleural effusion, pleurodesis
- Hemothorax, chylothorax, mesothelioma
- Lung cancer screening, solitary pulmonary nodule
- Lung cancer staging, NSCLC vs SCLC, treatment
- Bronchoscopy, EBUS, mediastinoscopy
- Sleep apnea: diagnosis, polysomnography, Epworth scale
- Central sleep apnea, nocturnal hypoventilation
- Chronic cough evaluation
- Hemoptysis workup
- Pulmonary hypertension, right heart failure, cor pulmonale
- Pulmonary function tests, DLCO

**eTG References**: Respiratory - Lung cancer, Cancer

---

## Australian Guidelines References

All MCQs will reference:
- **eTG Complete (2024-2025)** - Respiratory section
- **National Asthma Council Australia** - Asthma Handbook
- **COPD-X Guidelines** - COPD management
- **Thoracic Society of Australia and New Zealand (TSANZ)** - Various respiratory guidelines
- **Australian and New Zealand Society of Blood Transfusion** - VTE management
- **Cancer Council Australia** - Lung cancer guidelines

---

## Generation Approach

Following Week 3 Cardiology success pattern:

1. **Generate each batch separately** using clinical-documentation-expert agent
2. **25 MCQs per batch** (manageable for agent output token limits)
3. **Save to individual .py files** with GENERATED_MCQS dict
4. **Create consolidation script** for each batch
5. **Execute batch scripts sequentially** to update main JSON

Each MCQ must include:
- ✓ Australian medical context (Australian hospitals, eTG references)
- ✓ Australian spelling (oedema, paracetamol, adrenaline)
- ✓ Realistic clinical scenario (50-150 words)
- ✓ 200-400 word explanation with differential diagnosis
- ✓ AMC Clinical Examination focus
- ✓ Zero placeholder content
- ✓ Citations from eTG/TSANZ/COPD-X

---

**Status**: Ready to begin Batch 1 generation
**Next Step**: Generate Batch 1 (Asthma & Early COPD, MCQs 001-025)
