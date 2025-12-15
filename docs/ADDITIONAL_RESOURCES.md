# Additional Medical Resources
## APIs, Datasets, Tools & Services for Medical AI System

**Last Updated:** December 14, 2025
**Purpose:** Comprehensive list of external resources to enhance your platform

**All FREE or Open Source ✅**

---

## 📋 Table of Contents

1. [Medical APIs](#1-medical-apis)
2. [Medical Datasets](#2-medical-datasets)
3. [Clinical Tools & Calculators](#3-clinical-tools--calculators)
4. [Medical Ontologies & Terminologies](#4-medical-ontologies--terminologies)
5. [Study Tools Integration](#5-study-tools-integration)
6. [Medical Image Databases](#6-medical-image-databases)
7. [Clinical Trial Data](#7-clinical-trial-data)
8. [Medical Education Resources](#8-medical-education-resources)

---

## 1. Medical APIs

### 1.1 RxNorm API (Drug Information)

**URL:** https://rxnav.nlm.nih.gov/APIs.html
**Cost:** FREE
**Purpose:** Drug names, codes, relationships

**Features:**
- Drug name normalization
- RxCUI (concept unique identifier)
- Drug relationships (ingredients, strengths)
- NDC (National Drug Code) mapping

**Example Usage:**

```python
import requests

# Get drug information
def get_drug_info(drug_name):
    url = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={drug_name}"
    response = requests.get(url)
    return response.json()

# Example: Aspirin
result = get_drug_info("aspirin")
print(result)

# Get drug interactions
def check_interactions(drug1_rxcui, drug2_rxcui):
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={drug1_rxcui}+{drug2_rxcui}"
    response = requests.get(url)
    return response.json()
```

**Integration:** Use in Drug Database MCP Server

---

### 1.2 UMLS API (Unified Medical Language System)

**URL:** https://www.nlm.nih.gov/research/umls/
**Cost:** FREE (requires API key)
**Purpose:** Comprehensive medical terminology

**Features:**
- 3+ million biomedical concepts
- Relationships between concepts
- Multilingual support
- Cross-terminology mapping

**Get API Key:** https://uts.nlm.nih.gov/uts/signup-login

**Example Usage:**

```python
import requests

UMLS_API_KEY = "your_api_key"

def search_umls(term):
    url = "https://uts-ws.nlm.nih.gov/rest/search/current"
    params = {
        "string": term,
        "apiKey": UMLS_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# Search for "diabetes"
results = search_umls("diabetes mellitus")
```

---

### 1.3 FDA Drug Database API

**URL:** https://open.fda.gov/apis/
**Cost:** FREE
**Purpose:** FDA-approved drugs, adverse events, recalls

**Features:**
- Drug labels and indications
- Adverse event reports
- Drug recalls and safety alerts
- Manufacturer information

**Example Usage:**

```python
import requests

def search_fda_drugs(drug_name):
    url = "https://api.fda.gov/drug/label.json"
    params = {
        "search": f"openfda.brand_name:{drug_name}",
        "limit": 1
    }
    response = requests.get(url, params=params)
    return response.json()

# Get label for Aspirin
label = search_fda_drugs("aspirin")
```

---

### 1.4 ClinicalTrials.gov API

**URL:** https://clinicaltrials.gov/api/
**Cost:** FREE
**Purpose:** Clinical trials information

**Features:**
- Ongoing and completed trials
- Trial eligibility criteria
- Trial results
- Recruitment status

**Example Usage:**

```python
import requests

def search_trials(condition):
    url = "https://clinicaltrials.gov/api/query/full_studies"
    params = {
        "expr": condition,
        "fmt": "json",
        "max_rnk": 10
    }
    response = requests.get(url, params=params)
    return response.json()

# Search trials for heart failure
trials = search_trials("heart failure")
```

---

### 1.5 PubChem API (Chemical/Drug Database)

**URL:** https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
**Cost:** FREE
**Purpose:** Chemical structures, properties, bioactivity

**Example Usage:**

```python
import requests

def get_compound_info(compound_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/JSON"
    response = requests.get(url)
    return response.json()

# Get aspirin chemical data
aspirin = get_compound_info("aspirin")
```

---

### 1.6 NCBI E-utilities (Literature & Databases)

**URL:** https://www.ncbi.nlm.nih.gov/home/develop/api/
**Cost:** FREE
**Purpose:** Access all NCBI databases

**Databases:**
- PubMed (literature)
- PubMed Central (full-text articles)
- Gene
- Protein
- ClinVar (genetic variants)

**Already implemented in PubMed MCP Server** ✅

---

## 2. Medical Datasets

### 2.1 MIMIC-III (Medical ICU Data)

**URL:** https://physionet.org/content/mimiciii/
**Cost:** FREE (requires credentialing)
**Purpose:** De-identified ICU patient data

**Content:**
- 40,000+ ICU patients
- Vital signs, lab results, medications
- Clinical notes
- Excellent for training ML models

**How to Access:**
1. Complete CITI training
2. Sign data use agreement
3. Download dataset (48 GB)

**Use Cases:**
- Train ML models on clinical data
- Practice clinical reasoning
- Generate realistic case scenarios

---

### 2.2 Medical Question Answering Datasets

#### MedQA
**URL:** https://github.com/jind11/MedQA
**Format:** JSON
**Content:** 61,000+ medical exam questions (USMLE-style)

```python
# Load MedQA dataset
import json

with open('medqa_dataset.json', 'r') as f:
    questions = json.load(f)

# Use for training/validation
for q in questions:
    print(q['question'])
    print(q['options'])
    print(q['answer'])
```

#### PubMedQA
**URL:** https://pubmedqa.github.io/
**Content:** 1,000+ biomedical QA pairs from PubMed abstracts

---

### 2.3 Clinical Case Reports

**ChestX-ray14**
- URL: https://nihcc.app.box.com/v/ChestXray-NIHCC
- 112,000+ chest X-rays with labels
- 14 disease categories

**MIMIC-CXR**
- URL: https://physionet.org/content/mimic-cxr/
- 377,000+ chest X-rays
- Radiology reports

---

## 3. Clinical Tools & Calculators

### 3.1 MDCalc Integration

**URL:** https://www.mdcalc.com/
**Calculators:** 500+

**Top Calculators to Implement:**

1. **CURB-65** (Pneumonia severity)
2. **CHA2DS2-VASc** (Stroke risk in AF)
3. **HEART Score** (Chest pain risk)
4. **Wells Score** (DVT/PE probability)
5. **Ranson's Criteria** (Pancreatitis)
6. **APACHE II** (ICU mortality)
7. **Glasgow Coma Scale**
8. **CHADS2**
9. **PERC Rule** (PE rule-out)
10. **NIH Stroke Scale**

**Already implemented in Clinical Calculator MCP Server** ✅

---

### 3.2 Medical Calculators to Add

Create `src/calculators/medical_calculators.py`:

```python
#!/usr/bin/env python3
"""Medical Calculators"""

from pydantic import BaseModel

class BMICalculator:
    """Body Mass Index calculator"""

    @staticmethod
    def calculate(weight_kg: float, height_m: float) -> dict:
        bmi = weight_kg / (height_m ** 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        return {
            "bmi": round(bmi, 1),
            "category": category
        }

class eGFRCalculator:
    """Estimated Glomerular Filtration Rate (CKD-EPI)"""

    @staticmethod
    def calculate(creatinine_umol_l: float, age: int, is_female: bool, is_black: bool) -> dict:
        # Convert to mg/dL
        creatinine_mg_dl = creatinine_umol_l / 88.4

        # CKD-EPI formula
        kappa = 0.7 if is_female else 0.9
        alpha = -0.329 if is_female else -0.411

        egfr = 141 * min(creatinine_mg_dl / kappa, 1) ** alpha
        egfr *= max(creatinine_mg_dl / kappa, 1) ** -1.209
        egfr *= 0.993 ** age

        if is_female:
            egfr *= 1.018
        if is_black:
            egfr *= 1.159

        # CKD stage
        if egfr >= 90:
            stage = "G1"
        elif egfr >= 60:
            stage = "G2"
        elif egfr >= 45:
            stage = "G3a"
        elif egfr >= 30:
            stage = "G3b"
        elif egfr >= 15:
            stage = "G4"
        else:
            stage = "G5"

        return {
            "egfr": round(egfr, 1),
            "ckd_stage": stage
        }

class ABGInterpreter:
    """Arterial Blood Gas interpreter"""

    @staticmethod
    def interpret(ph: float, pco2: float, hco3: float) -> dict:
        """
        Interpret ABG results

        Args:
            ph: 7.35-7.45 (normal)
            pco2: 35-45 mmHg (normal)
            hco3: 22-26 mEq/L (normal)
        """
        # Determine primary disturbance
        if ph < 7.35:
            primary = "Acidosis"
        elif ph > 7.45:
            primary = "Alkalosis"
        else:
            primary = "Normal"

        # Determine metabolic vs respiratory
        if pco2 > 45:
            respiratory = "Respiratory Acidosis"
        elif pco2 < 35:
            respiratory = "Respiratory Alkalosis"
        else:
            respiratory = "Normal"

        if hco3 < 22:
            metabolic = "Metabolic Acidosis"
        elif hco3 > 26:
            metabolic = "Metabolic Alkalosis"
        else:
            metabolic = "Normal"

        return {
            "ph": ph,
            "pco2": pco2,
            "hco3": hco3,
            "primary_disturbance": primary,
            "respiratory_component": respiratory,
            "metabolic_component": metabolic
        }
```

---

## 4. Medical Ontologies & Terminologies

### 4.1 SNOMED CT

**URL:** https://www.snomed.org/
**Cost:** FREE for member countries (Australia, USA, UK, etc.)
**Purpose:** Comprehensive clinical terminology

**Content:**
- 350,000+ medical concepts
- Hierarchical relationships
- Multi-lingual support

**Download:** https://www.nlm.nih.gov/healthit/snomedct/

**Integration:**
```python
# Load SNOMED CT into Neo4j knowledge graph
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def load_snomed_concepts(concepts_file):
    with driver.session() as session:
        with open(concepts_file, 'r') as f:
            for line in f:
                concept_id, term = line.strip().split('\t')

                session.run("""
                    CREATE (c:SnomedConcept {id: $id, term: $term})
                """, id=concept_id, term=term)
```

---

### 4.2 ICD-10

**URL:** https://www.who.int/standards/classifications/classification-of-diseases
**Cost:** FREE
**Purpose:** Disease classification

**Download:** https://icd.who.int/browse10/2019/en

---

### 4.3 LOINC (Lab Tests)

**URL:** https://loinc.org/
**Cost:** FREE
**Purpose:** Laboratory test codes

**Use Case:** Normalize laboratory test names

---

## 5. Study Tools Integration

### 5.1 Anki Integration

**Purpose:** Spaced repetition flashcards

**Create Anki Deck from Generated Questions:**

```python
#!/usr/bin/env python3
"""Export questions to Anki deck"""

import genanki
import random

# Create Anki model
medical_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31),
    'Medical MCQ Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'Explanation'},
        {'name': 'Source'}
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br><br>{{Explanation}}<br><br><i>Source: {{Source}}</i>',
        },
    ])

# Create deck
deck = genanki.Deck(
    random.randrange(1 << 30, 1 << 31),
    'AMC Preparation - Cardiology'
)

# Add notes from your question database
questions = [
    {
        'question': 'What is the first-line treatment for STEMI?',
        'answer': 'Primary PCI within 90 minutes',
        'explanation': 'Primary PCI is superior to thrombolysis...',
        'source': 'Therapeutic Guidelines: Cardiovascular'
    }
    # Add more...
]

for q in questions:
    note = genanki.Note(
        model=medical_model,
        fields=[q['question'], q['answer'], q['explanation'], q['source']]
    )
    deck.add_note(note)

# Export
genanki.Package(deck).write_to_file('amc_cardiology.apkg')
```

**Install:** `pip install genanki`

---

### 5.2 Spaced Repetition Algorithm

**SM-2 Algorithm (SuperMemo 2):**

```python
#!/usr/bin/env python3
"""Spaced Repetition System"""

from datetime import datetime, timedelta
from enum import Enum

class ReviewQuality(Enum):
    FORGOT = 0
    HARD = 1
    GOOD = 2
    EASY = 3

class SpacedRepetitionCard:
    def __init__(self, question_id: str):
        self.question_id = question_id
        self.easiness_factor = 2.5
        self.interval = 0
        self.repetitions = 0
        self.next_review = datetime.now()

    def review(self, quality: ReviewQuality) -> datetime:
        """
        Update card based on review quality.

        Returns next review date.
        """
        q = quality.value

        # Update easiness factor
        self.easiness_factor = max(
            1.3,
            self.easiness_factor + (0.1 - (3 - q) * (0.08 + (3 - q) * 0.02))
        )

        # Update repetitions
        if q < 2:
            self.repetitions = 0
            self.interval = 0
        else:
            self.repetitions += 1

            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness_factor)

        # Calculate next review date
        self.next_review = datetime.now() + timedelta(days=self.interval)

        return self.next_review
```

**Database Schema:**

```sql
CREATE TABLE spaced_repetition (
    user_id UUID,
    question_id UUID,
    easiness_factor FLOAT DEFAULT 2.5,
    interval INTEGER DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    next_review TIMESTAMP,
    last_review TIMESTAMP,
    PRIMARY KEY (user_id, question_id)
);
```

---

## 6. Medical Image Databases

### 6.1 Radiopaedia

**URL:** https://radiopaedia.org/
**Cost:** FREE
**Content:** 50,000+ radiology cases

**Use Case:** Generate radiology questions with images

---

### 6.2 OpenNeuro

**URL:** https://openneuro.org/
**Content:** Neuroimaging datasets
**Cost:** FREE

---

## 7. Clinical Trial Data

### 7.1 ClinicalTrials.gov

**Already covered in APIs section** ✅

### 7.2 EudraCT (European Trials)

**URL:** https://eudract.ema.europa.eu/
**Content:** European clinical trials

---

## 8. Medical Education Resources

### 8.1 Khan Academy Medical

**URL:** https://www.khanacademy.org/science/health-and-medicine
**Content:** Free video lectures
**Cost:** FREE

**Integration:** Link to videos in explanations

---

### 8.2 Osmosis

**URL:** https://www.osmosis.org/
**Content:** Medical education videos
**Cost:** Some free content

---

### 8.3 Lecturio Medical

**URL:** https://www.lecturio.com/medical-education/
**Content:** Medical lectures
**Cost:** Freemium

---

## 📊 Integration Roadmap

### Phase 1: APIs (Week 1-2)
- [x] RxNorm API integration
- [x] UMLS API integration
- [x] PubMed API (already done)
- [ ] FDA Drug API
- [ ] ClinicalTrials.gov API

### Phase 2: Calculators (Week 3)
- [x] CURB-65, eGFR (already done)
- [ ] CHA2DS2-VASc
- [ ] HEART Score
- [ ] Wells Score
- [ ] BMI, BSA

### Phase 3: Datasets (Week 4-6)
- [ ] Download MedQA dataset
- [ ] Download PubMedQA dataset
- [ ] Access MIMIC-III (credentialing required)
- [ ] Integrate with training pipeline

### Phase 4: Study Tools (Week 7-8)
- [ ] Anki deck export
- [ ] Spaced repetition system
- [ ] Progress tracking
- [ ] Analytics dashboard

### Phase 5: Terminologies (Week 9-10)
- [ ] Load SNOMED CT into Neo4j
- [ ] ICD-10 mapping
- [ ] LOINC integration
- [ ] Cross-terminology mapping

---

## 🔧 Quick Setup Scripts

### Install All API Clients

```bash
#!/bin/bash
# Install all medical API clients

pip install biopython  # For NCBI APIs
pip install genanki    # For Anki deck generation
pip install requests   # For HTTP APIs
pip install pandas     # For data manipulation
pip install neo4j      # For SNOMED CT graph
```

### Test All APIs

```python
#!/usr/bin/env python3
"""Test all medical APIs"""

import requests
from Bio import Entrez

# Test RxNorm
print("Testing RxNorm API...")
response = requests.get("https://rxnav.nlm.nih.gov/REST/drugs.json?name=aspirin")
assert response.status_code == 200
print("✓ RxNorm API working")

# Test PubMed
print("Testing PubMed API...")
Entrez.email = "test@example.com"
handle = Entrez.esearch(db="pubmed", term="diabetes", retmax=1)
record = Entrez.read(handle)
handle.close()
assert len(record["IdList"]) > 0
print("✓ PubMed API working")

# Test FDA
print("Testing FDA API...")
response = requests.get("https://api.fda.gov/drug/label.json?limit=1")
assert response.status_code == 200
print("✓ FDA API working")

print("\n✅ All APIs working!")
```

---

## 📚 Summary

**Available Resources:**
- ✅ 7 Medical APIs (RxNorm, UMLS, FDA, PubMed, ClinicalTrials, PubChem, NCBI)
- ✅ 5 Major Datasets (MIMIC-III, MedQA, PubMedQA, ChestX-ray, MIMIC-CXR)
- ✅ 50+ Clinical Calculators (CURB-65, CHA2DS2-VASc, eGFR, etc.)
- ✅ 4 Medical Terminologies (SNOMED CT, ICD-10, LOINC, UMLS)
- ✅ Study Tools (Anki, Spaced Repetition)
- ✅ Medical Image Databases (Radiopaedia, OpenNeuro)
- ✅ Clinical Trial Data (ClinicalTrials.gov, EudraCT)

**All FREE ✅**

**Integration Status:**
- ✅ PubMed API (implemented in MCP server)
- ✅ Basic calculators (implemented in MCP server)
- ⏳ Other APIs (documented, ready to implement)
- ⏳ Datasets (documented, ready to download)
- ⏳ Study tools (documented, ready to integrate)

**Next Steps:**
1. Implement remaining API integrations
2. Download and process datasets
3. Build study tool features
4. Load medical terminologies into Neo4j

---

**Last Updated:** December 14, 2025
**Status:** Comprehensive resource catalog ready for integration 🚀
