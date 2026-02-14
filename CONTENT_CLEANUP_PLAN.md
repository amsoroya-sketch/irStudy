# Content Cleanup & Legal Protection Plan
## Actionable Steps to Make Your Content Legally Safe

---

## ✅ GOOD NEWS: Reduced Risk Profile

**Your statements:**
- "Remove textbook images" → You acknowledge this needs fixing ✅
- "I did not buy subscription [eTG]" → **No eTG content!** ✅

**Updated Risk Assessment:**

| Risk Factor | Status | Action |
|-------------|--------|--------|
| eTG content | ✅ **NONE** (no subscription) | None needed |
| Textbook images | ⚠️ **PRESENT** | Remove/replace |
| Verbatim text | ⚠️ **UNKNOWN** | Audit needed |
| Original expression | ✅ **LIKELY** | Verify with audit |

**Your risk level just dropped significantly.**

---

## PHASE 1: COMPLETE CONTENT AUDIT

### Step 1.1: Create Content Inventory

```bash
# Run this to catalog all your content
cd /home/dev/Development/irStudy

# Count MCQs
find data -name "*.json" -exec grep -l "question" {} \; | wc -l

# Count OSCEs
find data -name "*osce*.json" | wc -l

# Count images
find . -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | wc -l
```

**Create a spreadsheet:**

| Content ID | Type | File Path | Status | Risk Level | Action |
|------------|------|-----------|--------|------------|--------|
| mcq_001 | MCQ | data/cardio/... | To Review | Unknown | Audit |
| osce_045 | OSCE | data/osces/... | To Review | Unknown | Audit |
| img_12 | Image | assets/... | To Review | High | Remove |

### Step 1.2: Image Audit (HIGH PRIORITY)

```bash
# Find all images in your project
find /home/dev/Development/irStudy -type f \( \
    -name "*.png" -o \
    -name "*.jpg" -o \
    -name "*.jpeg" -o \
    -name "*.gif" -o \
    -name "*.svg" \
) > image_inventory.txt

# Categorize them:
# 1. Medical diagrams (HIGHEST RISK)
# 2. Photos (MEDIUM RISK)
# 3. Icons/UI elements (LOW RISK)
# 4. Your own creations (NO RISK)
```

**Image Risk Assessment:**

| Image Type | Source | Risk | Action |
|------------|--------|------|--------|
| Medical diagrams | Textbooks | 🔴 **REMOVE** | Delete |
| Anatomical illustrations | Textbooks | 🔴 **REMOVE** | Delete |
| Clinical photos | Textbooks | 🔴 **REMOVE** | Delete |
| ECG strips | Textbooks | 🔴 **REMOVE** | Delete |
| X-rays/Imaging | Textbooks | 🔴 **REMOVE** | Delete |
| Icons/UI | Free libraries | 🟢 **KEEP** | Verify license |
| Your screenshots | Original | 🟢 **KEEP** | Document |

### Step 1.3: Text Content Audit

**Manual Review Process:**

```python
# content_auditor.py
import json
import os
from difflib import SequenceMatcher

# Sample high-risk textbook passages to check against
TEXTBOOK_PATTERNS = [
    "crushing substernal chest pain",
    "radiating to the left arm",
    "associated with diaphoresis",
    # Add more patterns from your textbooks
]

def audit_mcq(mcq_file):
    """Audit single MCQ file for high-risk content"""
    with open(mcq_file, 'r') as f:
        mcqs = json.load(f)
    
    issues = []
    for mcq in mcqs:
        text = f"{mcq.get('question', '')} {mcq.get('explanation', '')}"
        
        # Check for textbook patterns
        for pattern in TEXTBOOK_PATTERNS:
            if pattern.lower() in text.lower():
                issues.append({
                    'mcq_id': mcq.get('id'),
                    'pattern_found': pattern,
                    'context': text[:200]
                })
        
        # Check for long verbatim matches
        if has_long_verbatim_match(text):
            issues.append({
                'mcq_id': mcq.get('id'),
                'issue': 'Potential verbatim match',
                'context': text[:200]
            })
    
    return issues

def has_long_verbatim_match(text, min_length=10):
    """Check if text contains long verbatim sequences"""
    # This would compare against textbook text
    # For now, placeholder
    return False

# Run audit
for root, dirs, files in os.walk('data/mcqs'):
    for file in files:
        if file.endswith('.json'):
            issues = audit_mcq(os.path.join(root, file))
            if issues:
                print(f"Issues in {file}: {len(issues)}")
```

---

## PHASE 2: CONTENT REPLACEMENT

### Step 2.1: Image Replacement Strategy

#### Option A: Use Open-Access Medical Images

**Best Sources:**

| Source | License | URL | Quality |
|--------|---------|-----|---------|
| **Wikimedia Commons** | CC BY-SA | commons.wikimedia.org | High |
| **Radiopaedia** | CC BY-NC-SA | radiopaedia.org | Excellent |
| **OpenStax** | CC BY | openstax.org | Good |
| **NCI Visuals Online** | Public Domain | visuals.cancer.gov | Good |
| **Smart Servier** | CC BY | smart.servier.com | High |
| **Freepik Medical** | Free with attribution | freepik.com | Medium |
| **Unsplash** | Unsplash License | unsplash.com | Medium |

**Replacement Script:**

```bash
#!/bin/bash
# replace_images.sh

# Create backup
mkdir -p backup/images
cp -r assets/images backup/

# Remove textbook images (you'll need to identify these)
# This is manual - you need to review each image

# Download open-access replacements
# Example for medical diagrams:
# - Smart Servier: https://smart.servier.com/category/medical-illustrations/
# - Wikimedia: Search for anatomy diagrams
```

#### Option B: Create Text-Based Alternatives

```python
# Instead of images, use ASCII/text descriptions

def replace_image_with_text(image_path, content_type):
    """
    Replace image with text description
    """
    replacements = {
        'ecg': generate_ecg_description(),
        'anatomy': generate_anatomy_description(),
        'xray': generate_xray_description(),
    }
    return replacements.get(content_type, "[Visual content removed]")

def generate_ecg_description():
    """
    Create text-based ECG question instead of image
    """
    return """
    [ECG tracing described in text]
    
    Rhythm: Regular, rate 72 bpm
    P waves: Present before each QRS, upright in II
    PR interval: 0.16 seconds (normal)
    QRS duration: 0.08 seconds (narrow)
    ST segment: Elevated 2mm in V1-V4
    T waves: Peaked in V2-V4
    
    What is the most likely diagnosis?
    """
```

#### Option C: Generate AI Images

```python
# Using DALL-E, Midjourney, or Stable Diffusion
# Check terms of service for commercial use

import openai

def generate_medical_illustration(description):
    """
    Generate original medical illustration
    """
    prompt = f"""
    Medical textbook style illustration of {description}.
    Clean, educational style. White background.
    Anatomically accurate but simplified for learning.
    No text or labels.
    """
    
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024"
    )
    
    return response.data[0].url
```

### Step 2.2: Text Content Verification

#### Spot-Check Process

```
SAMPLE AUDIT (Check 100 random MCQs):

For each MCQ:
1. Read the question
2. Read the explanation
3. Ask: Could this be verbatim from a textbook?
4. Check: Are there any unique phrases?
5. Decision:
   - Clearly original → KEEP ✅
   - Borderline → FLAG for review ⚠️
   - Clearly copied → REWRITE ❌
```

#### Rewrite Template for Flagged Content

```
ORIGINAL (Flagged):
"A 45-year-old male presents with crushing substernal chest pain 
radiating to the left arm, associated with diaphoresis and nausea."

REWRITE:
"Which presentation is most consistent with acute coronary syndrome?

A) Sudden onset chest pressure with arm discomfort and sweating
B) Gradual chest tightness with palpitations
C) Sharp chest pain worse with inspiration
D) Dull chest ache with shortness of breath"

Changes:
- Removed specific patient description
- Made it a general question format
- Used different words for same concepts
- Tests same knowledge, different expression
```

---

## PHASE 3: VERIFICATION & DOCUMENTATION

### Step 3.1: Clean Room Certification

Create a document that proves your process:

```markdown
# Content Creation Process Documentation

## Our Methodology

### 1. Source Research
We use the following sources for medical information:
- StatPearls (CC BY license)
- Cochrane Reviews (CC BY license)
- PubMed Central (various open licenses)
- Government health guidelines (public domain)
- Medical journals (abstracts, fair use)

We do NOT use:
- Subscription-only clinical guidelines (eTG)
- Proprietary textbook content
- Copyrighted images without license

### 2. Content Generation
- Information is processed through AI systems
- Original questions and scenarios are generated
- No verbatim copying of source material
- Facts are transformed into original educational content

### 3. Human Review
- All content is reviewed for medical accuracy
- Content is checked for originality
- No copyrighted images are used
- All content is original expression

### 4. Quality Assurance
- Medical professionals verify accuracy
- Plagiarism checks are performed
- Content is validated against multiple sources

## Certification

I certify that:
1. All MCQs are original questions written by our team/systems
2. No verbatim text from copyrighted textbooks is used
3. No copyrighted images from textbooks are used
4. No subscription-only content (eTG) is used
5. All content is based on publicly available medical knowledge

Date: _______________
Signature: _______________
```

### Step 3.2: Create Content Manifest

```json
{
  "content_audit": {
    "audit_date": "2026-02-04",
    "auditor": "Internal",
    
    "totals": {
      "mcqs_audited": 18000,
      "osces_audited": 3000,
      "images_reviewed": 500
    },
    
    "findings": {
      "images_removed": 120,
      "images_replaced_open_access": 80,
      "text_rewrites": 45,
      "clean_content": 45755
    },
    
    "verification": {
      "etg_content": "NONE - no subscription",
      "textbook_images": "REMOVED",
      "verbatim_text": "REWRITTEN",
      "original_expression": "VERIFIED"
    },
    
    "attestation": "All content is original expression based on public medical knowledge"
  }
}
```

---

## PHASE 4: ONGOING PROTECTION

### Step 4.1: Content Pipeline Rules

```python
# content_rules.py

CONTENT_GUIDELINES = {
    "allowed_sources": [
        "statpearls",
        "cochrane", 
        "pubmed_central",
        "government_guidelines",
        "open_access_journals"
    ],
    
    "forbidden_sources": [
        "therapeutic_guidelines",
        "subscription_textbooks",
        "copyrighted_images"
    ],
    
    "image_rules": {
        "allowed_licenses": ["CC BY", "CC BY-SA", "Public Domain", "CC0"],
        "forbidden": ["Copyright", "All Rights Reserved", "Unknown"],
        "preferred_sources": [
            "Wikimedia Commons",
            "Radiopaedia",
            "Smart Servier",
            "AI-generated"
        ]
    },
    
    "text_rules": {
        "max_verbatim_match": 5,  # words
        "require_original_scenarios": True,
        "citation_required": True
    }
}

def validate_content(content, content_type):
    """
    Validate content before publication
    """
    if content_type == "image":
        return validate_image_license(content)
    elif content_type == "mcq":
        return validate_text_originality(content)
    else:
        return False
```

### Step 4.2: Monthly Audits

```
MONTHLY CONTENT REVIEW CHECKLIST:

□ Review any new images added
□ Check image licenses
□ Spot-check 50 MCQs for originality
□ Verify no new textbook content
□ Update content manifest
□ Document any changes
```

---

## TIMELINE

### Week 1: Image Cleanup (PRIORITY)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Inventory all images | Image list |
| 3-4 | Identify textbook images | Flagged list |
| 5-7 | Remove & replace images | Clean image library |

### Week 2: Text Audit

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Sample 500 MCQs for review | Audit report |
| 3-4 | Rewrite flagged content | Updated MCQs |
| 5-7 | Spot-check OSCEs | OSCE audit |

### Week 3: Documentation

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Create process documentation | PDF document |
| 3-4 | Create content manifest | JSON file |
| 5-7 | Legal review (if budget) | Legal opinion |

### Week 4: Final Verification

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Final audit | Clean bill |
| 3-4 | Insurance setup | Policy document |
| 5-7 | Launch preparation | Ready to launch |

---

## COST ESTIMATE

| Item | Cost | Notes |
|------|------|-------|
| Manual review time | $2,000-4,000 | Your time or VA |
| Image replacements | $500-1,000 | Free sources mostly |
| AI image generation | $200-500 | If needed |
| Legal review | $1,000-2,000 | Optional but recommended |
| Insurance | $3,000-4,000/year | Professional indemnity |
| **Total** | **$6,700-12,000** | One-time + annual |

---

## VERIFICATION CHECKLIST

Before launch, confirm:

- [ ] All textbook images removed
- [ ] All images have proper licenses (CC BY, public domain)
- [ ] No eTG content present (you confirmed this ✅)
- [ ] No verbatim text from textbooks
- [ ] All MCQs are original questions
- [ ] Content manifest created
- [ ] Process documented
- [ ] Insurance obtained
- [ ] Legal review completed (optional)

---

## FINAL STATEMENT

**After completing this plan, you can confidently state:**

> "Our platform contains original educational content created through 
> analysis of publicly available medical literature. No subscription-only 
> content is used. No copyrighted images are reproduced. All MCQs and 
> OSCEs are original questions written by our team and AI systems based 
> on medical facts, which are not subject to copyright protection."

**This is legally defensible and ethically sound.**

---

**Document Version**: 1.0  
**Status**: Actionable Plan  
**Estimated Completion**: 4 weeks
