# Image Linking Strategy - MCQ & OSCE Integration

**Date:** 2026-02-07 06:35
**Status:** Planning Phase
**Current Images:** 2,930 images across 11 specialties

---

## Overview

This document outlines the strategy for linking downloaded medical images to existing MCQs and OSCEs in the AMC exam preparation system.

---

## Current State

### Image Library
- **Total images:** 2,930 (46.5% of 6,300 target)
- **OpenI images:** 1,982 (NIH peer-reviewed)
- **HEAL images:** 948 (teaching quality)
- **Specialties covered:** 11/11

### MCQ Database
Based on existing files in `data/mcqs/`:
- **Week 1:** 100 MCQs (haematology, cardiology, dermatology)
- **Week 2:** 100 MCQs (psychiatry - 80 MCQs)
- **Week 3:** 600 MCQs (cardiology 200 + respiratory 200 + psychiatry 100 + additional 100)
- **Total:** ~800 MCQs across multiple specialties

### OSCE Database
Based on existing files in `data/osces/`:
- **Cardiology:** 50 OSCEs
- **Respiratory:** 50 OSCEs
- **Psychiatry:** 40 OSCEs (week1) + additional
- **Total:** ~140+ OSCEs

---

## Linking Strategy

### Phase 1: Automated Metadata Extraction (Immediate)

**Objective:** Extract and catalog all image metadata for matching

**Steps:**
1. **Parse OpenI metadata** (`data/medical_images/openi/openi_metadata.json`)
   - Image ID, filename, specialty, topic
   - Search terms used
   - Source URL, title, journal
   - Clinical context from caption

2. **Parse HEAL metadata** (various `*_metadata.json` files)
   - Image ID, filename, specialty
   - Collection title and description
   - Keywords and tags

3. **Create unified image catalog**
   - Combine OpenI + HEAL metadata
   - Generate searchable index
   - Extract clinical keywords from captions
   - Map images to taxonomy nodes

**Implementation:**
```python
# scripts/create_image_catalog.py
import json
from pathlib import Path
from typing import List, Dict

def create_unified_catalog():
    """Create unified catalog of all images with metadata"""

    catalog = {
        'total_images': 0,
        'by_specialty': {},
        'by_topic': {},
        'images': []
    }

    # Parse OpenI metadata
    openi_meta = json.load(open('data/medical_images/openi/openi_metadata.json'))
    for img in openi_meta['images']:
        catalog['images'].append({
            'id': f"openi_{img['id']}",
            'path': img['filename'],
            'source': 'OpenI',
            'specialty': img['specialty'],
            'topic': img['topic'],
            'search_term': img['search_term'],
            'title': img.get('title', ''),
            'journal': img.get('journal', ''),
            'url': img.get('url', ''),
            'keywords': extract_keywords(img.get('title', '')),
            'taxonomy_node': map_to_taxonomy(img['specialty'], img['topic'])
        })

    # Parse HEAL metadata
    heal_folders = Path('data/medical_images/heal').glob('*/*_metadata.json')
    for meta_file in heal_folders:
        heal_meta = json.load(open(meta_file))
        # Similar processing for HEAL images

    # Save unified catalog
    with open('data/medical_images/unified_image_catalog.json', 'w') as f:
        json.dump(catalog, f, indent=2)

    return catalog
```

**Output:** `data/medical_images/unified_image_catalog.json`

---

### Phase 2: Topic-Based Matching (Day 1)

**Objective:** Match images to MCQs/OSCEs based on topic/specialty

**Matching Criteria:**
1. **Exact specialty match** (e.g., cardiology image → cardiology MCQ)
2. **Topic keyword match** (e.g., "STEMI" image → "myocardial infarction" MCQ)
3. **Clinical scenario overlap** (e.g., "chest pain" in both)

**Implementation:**
```python
# scripts/link_images_to_mcqs.py
def match_images_to_mcqs(catalog, mcq_file):
    """Match images to MCQs based on topic and keywords"""

    mcqs = json.load(open(mcq_file))
    matches = []

    for mcq in mcqs:
        # Extract MCQ metadata
        specialty = mcq.get('specialty', '')
        topic = mcq.get('topic', '')
        question_text = mcq.get('question', '')

        # Find matching images
        candidate_images = []

        # 1. Exact specialty + topic match
        for img in catalog['images']:
            if img['specialty'] == specialty and img['topic'] == topic:
                candidate_images.append({
                    'image_id': img['id'],
                    'path': img['path'],
                    'match_score': 100,
                    'match_reason': 'exact_topic'
                })

        # 2. Keyword overlap match
        mcq_keywords = extract_keywords(question_text)
        for img in catalog['images']:
            if img['specialty'] == specialty:
                overlap = set(mcq_keywords) & set(img['keywords'])
                if len(overlap) >= 2:  # At least 2 keyword matches
                    candidate_images.append({
                        'image_id': img['id'],
                        'path': img['path'],
                        'match_score': 50 + len(overlap) * 10,
                        'match_reason': f'keyword_overlap_{len(overlap)}'
                    })

        # Sort by match score and take top 3
        candidate_images.sort(key=lambda x: x['match_score'], reverse=True)

        matches.append({
            'mcq_id': mcq.get('id'),
            'question': question_text[:100],
            'matched_images': candidate_images[:3]  # Top 3 matches
        })

    return matches
```

**Output:** `data/mcq_image_links.json` (MCQ → Image mappings)

---

### Phase 3: Clinical Scenario Matching (Day 2-3)

**Objective:** Match images to clinical scenarios in OSCEs

**OSCE Linking Strategy:**
1. **History-taking OSCEs:** Link to relevant pathology images
2. **Physical examination OSCEs:** Link to examination finding images
3. **Breaking bad news OSCEs:** Link to diagnostic images (e.g., CT showing cancer)
4. **Emergency OSCEs:** Link to acute imaging (e.g., pneumothorax X-ray)

**Implementation:**
```python
# scripts/link_images_to_osces.py
def match_images_to_osces(catalog, osce_file):
    """Match images to OSCE scenarios"""

    osces = json.load(open(osce_file))
    matches = []

    for osce in osces:
        scenario = osce.get('scenario', '')
        diagnosis = osce.get('diagnosis', '')
        specialty = osce.get('specialty', '')

        # Extract clinical keywords from scenario
        keywords = extract_clinical_keywords(scenario + ' ' + diagnosis)

        # Find relevant images
        candidate_images = []
        for img in catalog['images']:
            if img['specialty'] == specialty:
                # Match based on diagnosis
                if diagnosis.lower() in img['topic'].lower():
                    candidate_images.append({
                        'image_id': img['id'],
                        'path': img['path'],
                        'match_score': 100,
                        'match_reason': 'diagnosis_match',
                        'suggested_use': 'Show during diagnosis discussion'
                    })

                # Match based on keywords
                overlap = set(keywords) & set(img['keywords'])
                if len(overlap) >= 2:
                    candidate_images.append({
                        'image_id': img['id'],
                        'path': img['path'],
                        'match_score': 60 + len(overlap) * 10,
                        'match_reason': f'keyword_overlap_{len(overlap)}',
                        'suggested_use': 'Show during clinical correlation'
                    })

        # Sort and take top 5
        candidate_images.sort(key=lambda x: x['match_score'], reverse=True)

        matches.append({
            'osce_id': osce.get('id'),
            'scenario': scenario[:100],
            'diagnosis': diagnosis,
            'matched_images': candidate_images[:5]
        })

    return matches
```

**Output:** `data/osce_image_links.json` (OSCE → Image mappings)

---

### Phase 4: Manual Review & Curation (Day 4-5)

**Objective:** Human review of automated matches to ensure clinical accuracy

**Review Process:**
1. **High-priority review** (match_score >= 80):
   - Verify image accurately represents the condition
   - Check image quality and clarity
   - Confirm educational value

2. **Medium-priority review** (match_score 50-79):
   - Assess relevance to question/scenario
   - Consider alternative images if available
   - Flag for potential removal

3. **Low-priority review** (match_score < 50):
   - Review for unexpected high-value matches
   - Mostly reject unless clinically perfect

**Curation Tool:**
```python
# scripts/curate_image_links.py
def create_curation_interface(matches):
    """Create simple CLI for manual review"""

    for i, match in enumerate(matches):
        print(f"\n{'='*70}")
        print(f"MCQ {i+1}/{len(matches)}")
        print(f"Question: {match['question']}")
        print(f"\nMatched Images ({len(match['matched_images'])}):")

        for j, img in enumerate(match['matched_images']):
            print(f"\n  [{j+1}] Score: {img['match_score']}")
            print(f"      Path: {img['path']}")
            print(f"      Reason: {img['match_reason']}")

            # Display image (if GUI available) or show metadata

            # Get user input
            decision = input(f"      Keep this image? (y/n/s=skip): ")

            if decision == 'y':
                match['matched_images'][j]['approved'] = True
            elif decision == 'n':
                match['matched_images'][j]['approved'] = False
            else:
                match['matched_images'][j]['approved'] = None  # Skip for now

    return matches
```

---

### Phase 5: Database Integration (Day 6-7)

**Objective:** Update MCQ/OSCE JSON files with image references

**Database Schema Update:**

**MCQ with images:**
```json
{
  "id": "MCQ_CARDIO_001",
  "question": "A 55-year-old man presents with crushing chest pain...",
  "specialty": "cardiology",
  "topic": "STEMI",
  "images": [
    {
      "id": "openi_PMC1234567",
      "path": "data/medical_images/openi/cardiology/stemi/openi_PMC1234567.png",
      "caption": "12-lead ECG showing ST elevation in leads II, III, aVF",
      "display_timing": "with_question",
      "source": "OpenI (NIH)",
      "citation": "PMC1234567"
    }
  ],
  "options": [...],
  "correct_answer": "B",
  "explanation": "The ECG shows inferior STEMI..."
}
```

**OSCE with images:**
```json
{
  "id": "OSCE_EMERG_001",
  "scenario": "A 28-year-old man presents to ED with sudden-onset right-sided chest pain...",
  "specialty": "emergency_medicine",
  "diagnosis": "Spontaneous pneumothorax",
  "images": [
    {
      "id": "openi_PMC9876543",
      "path": "data/medical_images/openi/emergency_medicine/pneumothorax/openi_PMC9876543.png",
      "caption": "Chest X-ray showing right-sided pneumothorax with visible visceral pleural line",
      "display_timing": "after_history_taking",
      "clinical_correlation": "This imaging supports the diagnosis based on clinical presentation",
      "source": "OpenI (NIH)",
      "citation": "PMC9876543"
    }
  ],
  "tasks": [...],
  "marking_criteria": [...]
}
```

**Implementation:**
```python
# scripts/integrate_images_to_database.py
def integrate_images(mcq_file, links_file, output_file):
    """Add approved image links to MCQ database"""

    mcqs = json.load(open(mcq_file))
    links = json.load(open(links_file))

    # Create lookup for quick matching
    link_map = {link['mcq_id']: link for link in links}

    for mcq in mcqs:
        mcq_id = mcq.get('id')

        if mcq_id in link_map:
            approved_images = [
                img for img in link_map[mcq_id]['matched_images']
                if img.get('approved') == True
            ]

            # Add images to MCQ
            mcq['images'] = [
                {
                    'id': img['image_id'],
                    'path': img['path'],
                    'display_timing': 'with_question',
                    'source': extract_source(img['image_id'])
                }
                for img in approved_images
            ]

    # Save updated MCQs
    with open(output_file, 'w') as f:
        json.dump(mcqs, f, indent=2)
```

---

## Implementation Timeline

### Week 1: Automated Processing
- **Day 1:** Create unified image catalog
- **Day 2:** Implement MCQ matching algorithm
- **Day 3:** Implement OSCE matching algorithm
- **Day 4:** Run automated matching on all MCQs/OSCEs
- **Day 5:** Generate match reports and statistics

**Deliverables:**
- `data/medical_images/unified_image_catalog.json`
- `data/mcq_image_links.json`
- `data/osce_image_links.json`
- `reports/image_matching_statistics.json`

### Week 2: Manual Curation
- **Day 6-7:** Review high-priority matches (score >= 80)
- **Day 8-9:** Review medium-priority matches (score 50-79)
- **Day 10:** Final quality check

**Deliverables:**
- `data/mcq_image_links_curated.json`
- `data/osce_image_links_curated.json`

### Week 3: Database Integration
- **Day 11-12:** Update MCQ JSON files with approved images
- **Day 13-14:** Update OSCE JSON files with approved images
- **Day 15:** Test frontend rendering with images
- **Day 16:** Deploy to production

**Deliverables:**
- Updated MCQ files with image references
- Updated OSCE files with image references
- Frontend image display component

---

## Matching Algorithm Details

### Keyword Extraction
```python
def extract_keywords(text: str) -> List[str]:
    """Extract clinical keywords from text"""

    # Medical keyword patterns
    patterns = [
        r'\b(pneumothorax|haemothorax|pneumonia|tuberculosis)\b',
        r'\b(STEMI|NSTEMI|myocardial infarction|angina)\b',
        r'\b(stroke|haemorrhage|infarction|ischaemia)\b',
        r'\b(fracture|dislocation|trauma)\b',
        r'\b(CT|MRI|X-ray|ultrasound|ECG|EEG)\b',
        # ... more patterns
    ]

    keywords = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend(matches)

    return list(set([k.lower() for k in keywords]))
```

### Taxonomy Mapping
```python
def map_to_taxonomy(specialty: str, topic: str) -> str:
    """Map image to taxonomy node"""

    # Load taxonomy
    taxonomy = json.load(open('data/medical_image_taxonomy_v1.json'))

    # Find matching node
    for spec_name, spec_data in taxonomy['taxonomy'].items():
        if spec_name.lower() == specialty.lower():
            for subcat in spec_data['subcategories'].values():
                for topic_name, topic_data in subcat['topics'].items():
                    for subtopic_name in topic_data['subtopics'].keys():
                        if topic.lower() in subtopic_name.lower():
                            return f"{spec_name}/{topic_name}/{subtopic_name}"

    return f"{specialty}/{topic}"
```

---

## Quality Metrics

### Success Criteria
1. **Coverage:** ≥70% of MCQs have at least 1 relevant image
2. **Quality:** ≥90% of matched images are clinically accurate (manual review)
3. **Relevance:** Average match score ≥75 for approved images
4. **Diversity:** Each specialty has images linked to MCQs/OSCEs

### Validation
- **Clinical accuracy review:** Medical professional review of top 100 matches
- **Educational value assessment:** Verify images enhance learning
- **Technical quality check:** Ensure images are high resolution and clear

---

## Example Linkings

### MCQ Example: STEMI ECG
**MCQ:**
```json
{
  "id": "CARDIO_MCQ_045",
  "question": "A 60-year-old man presents with crushing central chest pain radiating to left arm. Which ECG finding confirms STEMI?",
  "options": [
    "A) T-wave inversion in V1-V3",
    "B) ST elevation ≥2mm in leads II, III, aVF",
    "C) Prolonged PR interval",
    "D) Right bundle branch block"
  ],
  "correct_answer": "B"
}
```

**Matched Images:**
1. `openi_PMC_STEMI_001.png` - ECG showing inferior STEMI (score: 100, exact match)
2. `heal_cardiology_ecg_045.jpg` - Teaching ECG with ST elevation marked (score: 95, excellent teaching image)

**Integration:**
```json
{
  "id": "CARDIO_MCQ_045",
  "images": [
    {
      "id": "openi_PMC_STEMI_001",
      "path": "data/medical_images/openi/cardiology/stemi/openi_PMC_STEMI_001.png",
      "caption": "12-lead ECG showing ST elevation in inferior leads (II, III, aVF)",
      "display_timing": "with_question",
      "source": "OpenI"
    }
  ]
}
```

### OSCE Example: Pneumothorax
**OSCE:**
```json
{
  "id": "EMERG_OSCE_012",
  "scenario": "28-year-old male presents with sudden-onset right-sided pleuritic chest pain and dyspnoea",
  "diagnosis": "Spontaneous pneumothorax"
}
```

**Matched Images:**
1. `openi_PMC_PTX_078.png` - Chest X-ray showing large right pneumothorax (score: 100)
2. `openi_PMC_PTX_123.png` - CT chest showing pneumothorax with measurements (score: 90)

**Integration:**
```json
{
  "id": "EMERG_OSCE_012",
  "images": [
    {
      "id": "openi_PMC_PTX_078",
      "path": "data/medical_images/openi/emergency_medicine/pneumothorax/openi_PMC_PTX_078.png",
      "caption": "Chest X-ray: Right-sided pneumothorax with visible visceral pleural line and absence of lung markings laterally",
      "display_timing": "after_examination",
      "clinical_correlation": "Imaging confirms clinical suspicion based on reduced breath sounds and hyperresonance on right side",
      "source": "OpenI"
    }
  ]
}
```

---

## Tools and Scripts

### Required Scripts
1. `scripts/create_image_catalog.py` - Create unified catalog
2. `scripts/link_images_to_mcqs.py` - Automated MCQ matching
3. `scripts/link_images_to_osces.py` - Automated OSCE matching
4. `scripts/curate_image_links.py` - Manual review interface
5. `scripts/integrate_images_to_database.py` - Update JSON files
6. `scripts/validate_image_links.py` - Quality checks

### Support Tools
- `scripts/extract_keywords.py` - Clinical keyword extraction
- `scripts/map_to_taxonomy.py` - Taxonomy node mapping
- `scripts/generate_match_report.py` - Statistics and reports

---

## Next Steps

### Immediate Actions
1. ✅ Complete ongoing OpenI downloads (neurology, gastroenterology)
2. 🔄 Create unified image catalog script
3. 🔄 Implement MCQ matching algorithm
4. 🔄 Run initial automated matching on Week 3 cardiology/respiratory MCQs

### This Week
5. Implement OSCE matching algorithm
6. Generate comprehensive match report
7. Begin manual curation of high-priority matches
8. Integrate first batch of images into MCQ database

### Next Week
9. Complete manual curation
10. Integrate all approved images
11. Test frontend rendering
12. Create image-enhanced MCQ study sets

---

**Generated:** 2026-02-07 06:35
**Status:** Planning Complete - Ready for Implementation
**Current Images:** 2,930 (46.5% of target)
**Estimated MCQs with Images After Linking:** 560+ (70% of 800 MCQs)
**Estimated OSCEs with Images After Linking:** 100+ (71% of 140 OSCEs)
