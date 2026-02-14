# HTML Conversion Plan: Medical Education Content

**Date Created**: 2026-01-26
**Purpose**: Convert all generated JSON content to interactive HTML format
**Total Content**: 1,898 MCQs + 210 OSCEs = 2,108 items

---

## 🎯 Overview

All generated medical content will be converted to interactive HTML format for:
- **Study mode**: Browse by specialty, topic, difficulty
- **Practice mode**: Randomized questions, timed tests
- **Review mode**: Flagged questions, missed topics
- **Print mode**: PDF export for offline study

---

## 📊 HTML Conversion Breakdown

### Phase 1: MCQ HTML Conversion (1,898 items)

**Location**: `data-jan-26/html/mcqs/`

#### Structure:
```
data-jan-26/html/mcqs/
├── index.html (Master navigation)
├── cardiology/ (290 MCQs)
│   ├── index.html
│   ├── mcq_001.html
│   ├── mcq_002.html
│   └── ... (290 files)
├── respiratory/ (270 MCQs)
├── psychiatry/ (350 MCQs)
├── emergency/ (200 MCQs)
├── general_practice/ (175 MCQs)
├── endocrinology/ (170 MCQs)
├── gastroenterology/ (135 MCQs)
├── neurology/ (128 MCQs)
├── paediatrics/ (100 MCQs)
└── obgyn/ (80 MCQs)
```

#### HTML Features per MCQ:
1. **Question Card**:
   - Clinical scenario (patient demographics highlighted)
   - Question stem
   - 4 options (A, B, C, D)
   - Interactive radio buttons

2. **Answer Section** (revealed on click):
   - Correct answer highlighted in green
   - Explanation (why_correct, why_incorrect)
   - Key points (bullet list)
   - Summary (50-200 chars, bold)

3. **References Section**:
   - 3 citations with confidence scores
   - Links to guidelines (eTG, RANZCP, AMH)
   - Australian context markers

4. **Metadata Footer**:
   - Topic tags
   - Difficulty level
   - Agent OS ID (MED-001, etc.)
   - Tools applied (ECG, spirometry, MSE)
   - Specialty
   - Date generated

5. **Navigation**:
   - Previous/Next MCQ buttons
   - Back to specialty index
   - Back to master index
   - Flag for review button
   - Print button

#### Sample HTML Template:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCQ #{id}: {topic} - {specialty}</title>
    <link rel="stylesheet" href="../../styles/mcq.css">
    <script src="../../scripts/mcq-interactive.js"></script>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>{specialty} MCQ #{id}</h1>
            <div class="meta">
                <span class="topic">{topic}</span>
                <span class="difficulty">{difficulty}</span>
                <span class="agent">{agent_id}</span>
            </div>
        </header>

        <!-- Question Card -->
        <div class="question-card">
            <div class="scenario">
                <p>{clinical_scenario}</p>
            </div>
            <div class="stem">
                <p><strong>{question_stem}</strong></p>
            </div>
            <div class="options">
                <label><input type="radio" name="answer" value="A"> {option_A}</label>
                <label><input type="radio" name="answer" value="B"> {option_B}</label>
                <label><input type="radio" name="answer" value="C"> {option_C}</label>
                <label><input type="radio" name="answer" value="D"> {option_D}</label>
            </div>
            <button id="reveal-answer">Show Answer</button>
        </div>

        <!-- Answer Section (hidden initially) -->
        <div class="answer-section" id="answer-section" style="display: none;">
            <div class="correct-answer">
                <h3>✓ Correct Answer: {correct_option}</h3>
            </div>
            <div class="explanation">
                <h4>Explanation</h4>
                <p><strong>Why correct:</strong> {why_correct}</p>
                <p><strong>Why incorrect:</strong> {why_incorrect}</p>
            </div>
            <div class="key-points">
                <h4>Key Points</h4>
                <ul>
                    {key_points as bullet list}
                </ul>
            </div>
            <div class="summary">
                <p><strong>Summary:</strong> {summary}</p>
            </div>
        </div>

        <!-- References Section -->
        <div class="references">
            <h4>References</h4>
            {for each citation}
                <div class="citation">
                    <p><strong>{citation.source}</strong> (Confidence: {citation.rag_confidence})</p>
                    <p>{citation.snippet}</p>
                </div>
            {/for}
        </div>

        <!-- Navigation -->
        <nav class="bottom-nav">
            <button onclick="location.href='mcq_{prev_id}.html'">← Previous</button>
            <button onclick="location.href='index.html'">Back to {specialty}</button>
            <button onclick="location.href='mcq_{next_id}.html'">Next →</button>
            <button onclick="flagForReview()">🚩 Flag for Review</button>
            <button onclick="window.print()">🖨️ Print</button>
        </nav>
    </div>
</body>
</html>
```

---

### Phase 2: OSCE HTML Conversion (210 items)

**Location**: `data-jan-26/html/osces/`

#### Structure:
```
data-jan-26/html/osces/
├── index.html
├── cardiology/ (50 OSCEs)
├── respiratory/ (50 OSCEs)
├── psychiatry/ (53 OSCEs)
├── comprehensive/ (52 OSCEs)
└── general/ (5 OSCEs)
```

#### HTML Features per OSCE:
1. **Station Overview**:
   - Title
   - Time limit (8-10 minutes)
   - Specialty
   - Summary (1-2 sentences)

2. **Task Instructions**:
   - What you need to do
   - Key objectives
   - Assessment criteria

3. **Resources Provided**:
   - Patient information
   - Lab results
   - Imaging descriptions
   - Drug charts

4. **Model Answer**:
   - Suggested approach
   - Key findings to elicit
   - Management plan
   - Communication points

5. **Scoring Rubric**:
   - Categories (History, Examination, Management, Communication)
   - Points per category
   - Total score /100

---

### Phase 3: Master Index Pages

#### 3.1: Master Index (`data-jan-26/html/index.html`)

**Features**:
- Dashboard showing progress (MCQs attempted, OSCEs reviewed)
- Quick links to each specialty
- Search bar (by topic, keyword)
- Filter by difficulty, date generated
- Statistics (total items, completion rate)

#### 3.2: Specialty Index Pages

**Example**: `data-jan-26/html/mcqs/cardiology/index.html`

**Features**:
- List of all 290 cardiology MCQs
- Grouped by topic (ACS, arrhythmias, heart failure)
- Sortable by ID, difficulty, date
- Completion status (not started, in progress, completed)
- Flagged items highlighted

---

## 🔧 HTML Generation Scripts

### Script 1: `scripts-jan-26/convert_mcqs_to_html.py`

**Purpose**: Convert all MCQ JSON files to HTML

```python
#!/usr/bin/env python3
"""
Convert MCQ JSON files to interactive HTML format

Usage:
    python scripts-jan-26/convert_mcqs_to_html.py \
        --input data-jan-26/mcqs/*.json \
        --output data-jan-26/html/mcqs/ \
        --template templates/mcq_template.html
"""

import json
import os
from pathlib import Path
from jinja2 import Template

def convert_mcq_to_html(mcq, template, output_path):
    """Convert single MCQ JSON to HTML"""
    html = template.render(
        id=mcq['id'],
        specialty=mcq['metadata']['specialty'],
        topic=mcq['metadata']['topic'],
        difficulty=mcq['metadata'].get('difficulty', 'Medium'),
        agent_id=mcq['metadata'].get('agent_id', 'Unknown'),

        # Question
        scenario=mcq['question']['scenario'],
        stem=mcq['question']['stem'],
        options=mcq['question']['options'],
        correct_option=mcq['question']['correct_option'],

        # Explanation
        why_correct=mcq['explanation']['why_correct'],
        why_incorrect=mcq['explanation']['why_incorrect'],
        key_points=mcq['explanation']['key_points'],
        summary=mcq.get('summary', 'No summary provided'),

        # References
        references=mcq.get('references', []),

        # Navigation
        prev_id=mcq['id'] - 1 if mcq['id'] > 1 else None,
        next_id=mcq['id'] + 1
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    # Load template
    with open('templates/mcq_template.html', 'r') as f:
        template = Template(f.read())

    # Process all MCQ files
    mcq_files = Path('data-jan-26/mcqs').glob('*.json')

    for mcq_file in mcq_files:
        specialty = mcq_file.stem.replace('_mcqs', '')
        output_dir = Path(f'data-jan-26/html/mcqs/{specialty}')
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(mcq_file, 'r') as f:
            data = json.load(f)

        for mcq in data:
            output_file = output_dir / f"mcq_{mcq['id']:03d}.html"
            convert_mcq_to_html(mcq, template, output_file)
            print(f"✓ Generated {output_file}")
```

---

### Script 2: `scripts-jan-26/convert_osces_to_html.py`

**Purpose**: Convert all OSCE JSON files to HTML

```python
#!/usr/bin/env python3
"""
Convert OSCE JSON files to interactive HTML format
"""

import json
from pathlib import Path
from jinja2 import Template

def convert_osce_to_html(osce, template, output_path):
    """Convert single OSCE JSON to HTML"""
    html = template.render(
        id=osce['id'],
        specialty=osce['metadata']['specialty'],
        title=osce['title'],
        summary=osce.get('summary', 'No summary provided'),
        time_limit=osce.get('time_limit', '8 minutes'),

        # Task
        task=osce['task'],
        objectives=osce.get('objectives', []),

        # Resources
        resources=osce.get('resources', {}),

        # Model answer
        approach=osce.get('approach', ''),
        key_findings=osce.get('key_findings', []),
        management=osce.get('management', ''),

        # Scoring
        scoring=osce.get('scoring', {})
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

# Similar main() function as MCQ script
```

---

### Script 3: `scripts-jan-26/generate_index_pages.py`

**Purpose**: Generate master and specialty index pages

```python
#!/usr/bin/env python3
"""
Generate index pages for HTML navigation
"""

def generate_master_index():
    """Generate data-jan-26/html/index.html"""
    specialties = [
        {'name': 'Cardiology', 'mcqs': 290, 'osces': 50},
        {'name': 'Respiratory', 'mcqs': 270, 'osces': 50},
        # ... etc
    ]

    # Render master template with specialty data

def generate_specialty_index(specialty, mcqs):
    """Generate data-jan-26/html/mcqs/{specialty}/index.html"""
    # Group MCQs by topic
    # Render specialty template with MCQ list
```

---

## 📅 HTML Conversion Timeline (Integrated into Per-Day Plan)

### Day 27: Initial HTML Conversion (Week 5+)

**Time**: 8 hours

#### Morning (4 hours): Create HTML Templates & Scripts
- [ ] **Create Jinja2 Templates**
  ```bash
  mkdir -p templates
  touch templates/mcq_template.html
  touch templates/osce_template.html
  touch templates/index_template.html
  touch templates/specialty_index_template.html
  ```

- [ ] **Create CSS Stylesheet**
  ```bash
  mkdir -p data-jan-26/html/styles
  touch data-jan-26/html/styles/mcq.css
  touch data-jan-26/html/styles/osce.css
  touch data-jan-26/html/styles/index.css
  ```

- [ ] **Create JavaScript Interactivity**
  ```bash
  mkdir -p data-jan-26/html/scripts
  touch data-jan-26/html/scripts/mcq-interactive.js
  touch data-jan-26/html/scripts/navigation.js
  ```

- [ ] **Write Conversion Scripts**
  ```bash
  touch scripts-jan-26/convert_mcqs_to_html.py
  touch scripts-jan-26/convert_osces_to_html.py
  touch scripts-jan-26/generate_index_pages.py
  ```

#### Afternoon (4 hours): Run HTML Conversion
- [ ] **Convert All MCQs to HTML (1,898 files)**
  ```bash
  python scripts-jan-26/convert_mcqs_to_html.py \
    --input data-jan-26/mcqs/*.json \
    --output data-jan-26/html/mcqs/ \
    --template templates/mcq_template.html
  ```
  **Expected Output**: 1,898 HTML files (one per MCQ)

- [ ] **Convert All OSCEs to HTML (210 files)**
  ```bash
  python scripts-jan-26/convert_osces_to_html.py \
    --input data-jan-26/osces/*.json \
    --output data-jan-26/html/osces/ \
    --template templates/osce_template.html
  ```
  **Expected Output**: 210 HTML files (one per OSCE)

- [ ] **Generate Index Pages**
  ```bash
  python scripts-jan-26/generate_index_pages.py \
    --data-dir data-jan-26/ \
    --output data-jan-26/html/
  ```
  **Expected Output**:
  - 1 master index (index.html)
  - 10 specialty indexes (cardiology, respiratory, etc.)
  - 5 OSCE specialty indexes

---

### Day 28: HTML Testing & Refinement (Week 5+)

**Time**: 4 hours

#### Morning (2 hours): HTML Validation
- [ ] **Test Master Index**
  ```bash
  # Open in browser
  google-chrome data-jan-26/html/index.html

  # Check navigation works
  # Check search functionality
  # Check filtering works
  ```

- [ ] **Test MCQ Pages**
  ```bash
  # Sample 10 MCQs from each specialty
  # Verify:
  # - Question displays correctly
  # - Answer reveal button works
  # - Navigation works
  # - References formatted properly
  ```

- [ ] **Test OSCE Pages**
  ```bash
  # Sample 5 OSCEs
  # Verify formatting and layout
  ```

#### Afternoon (2 hours): HTML Refinement
- [ ] **Fix any display issues**
- [ ] **Optimize CSS for print mode**
- [ ] **Add responsive design for mobile**
- [ ] **Test cross-browser compatibility**

---

## 🎨 HTML Features

### Interactive Features:
1. **Answer Reveal**: Click button to show explanation
2. **Flag for Review**: Mark difficult questions
3. **Progress Tracking**: Track completed MCQs
4. **Search**: Find MCQs by keyword/topic
5. **Filter**: By specialty, difficulty, date
6. **Random Mode**: Generate random test
7. **Timed Mode**: Simulate exam conditions
8. **Print Mode**: Clean layout for PDF export

### Accessibility:
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast mode
- Adjustable font sizes

### Mobile Responsive:
- Touch-friendly buttons
- Optimized layout for small screens
- Swipe navigation

---

## 📊 HTML Conversion Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **MCQ HTML files** | 1,898 | All JSON converted |
| **OSCE HTML files** | 210 | All JSON converted |
| **Index pages** | 16 | Master + specialties |
| **CSS files** | 3 | MCQ, OSCE, Index |
| **JS files** | 2 | Interactive, Navigation |
| **Total HTML pages** | 2,124 | 1,898 + 210 + 16 |
| **Validation** | 100% W3C | HTML5 compliant |
| **Load time** | <2s per page | Optimized |

---

## 🚀 Final HTML Deliverables

### Structure:
```
data-jan-26/html/
├── index.html (Master dashboard)
├── styles/
│   ├── mcq.css
│   ├── osce.css
│   └── index.css
├── scripts/
│   ├── mcq-interactive.js
│   └── navigation.js
├── mcqs/
│   ├── cardiology/ (290 HTML files + index)
│   ├── respiratory/ (270 HTML files + index)
│   ├── psychiatry/ (350 HTML files + index)
│   ├── emergency/ (200 HTML files + index)
│   ├── general_practice/ (175 HTML files + index)
│   ├── endocrinology/ (170 HTML files + index)
│   ├── gastroenterology/ (135 HTML files + index)
│   ├── neurology/ (128 HTML files + index)
│   ├── paediatrics/ (100 HTML files + index)
│   └── obgyn/ (80 HTML files + index)
└── osces/
    ├── cardiology/ (50 HTML files + index)
    ├── respiratory/ (50 HTML files + index)
    ├── psychiatry/ (53 HTML files + index)
    ├── comprehensive/ (52 HTML files + index)
    └── general/ (5 HTML files + index)
```

**Total Files**: 2,124 HTML files + 3 CSS + 2 JS = 2,129 files

---

## Git Commit for HTML Conversion

```bash
git add data-jan-26/html/
git add scripts-jan-26/convert_*
git add templates/

git commit -m "$(cat <<'EOF'
feat(html): Complete HTML conversion of all medical content (2,108 items)

HTML Conversion Complete:
- MCQs: 1,898 HTML files (all specialties)
- OSCEs: 210 HTML files (all specialties)
- Index pages: 16 (master + specialties)
- Total HTML pages: 2,124

Features:
- Interactive answer reveal
- Navigation (prev/next, back to index)
- Flag for review
- Print-friendly layout
- Responsive design (mobile-ready)
- Search and filter functionality
- Progress tracking

Technical Stack:
- HTML5 compliant
- CSS3 for styling
- Vanilla JavaScript for interactivity
- Jinja2 templating
- W3C validated

Conversion Scripts:
- convert_mcqs_to_html.py (1,898 conversions)
- convert_osces_to_html.py (210 conversions)
- generate_index_pages.py (16 indexes)

Time Spent: 12 hours (Day 27-28)

🤖 Generated with Claude Code (claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git push origin main
```

---

**Document Status**: Ready for Integration
**Created**: 2026-01-26
**Integration**: Add Days 27-28 to PER_DAY_EXECUTION_PLAN.md
**Total HTML Files**: 2,129 files (2,124 HTML + 3 CSS + 2 JS)
**Expected Completion**: Week 6 (after all content generation complete)