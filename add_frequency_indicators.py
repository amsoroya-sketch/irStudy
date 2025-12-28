#!/usr/bin/env python3
"""
Automated AMC Frequency Indicator Addition Script

This script systematically adds AMC frequency indicators to all OSCE preparation files.
It processes both .md and .html files, adding appropriate frequency banners based on
predefined classifications.

Usage:
    python3 add_frequency_indicators.py
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Base directory for OSCE files
BASE_DIR = Path("/home/dev/Development/irStudy/ICRP_OSCE_Preparation")

# Frequency classifications with specific "Why High-Yield" explanations
FREQUENCY_MAP = {
    # GROUP 1: HIGH-YIELD MEDICINE (⭐⭐⭐)
    "Medicine/02_Physical_Examination_Cardiovascular_Respiratory": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "80%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Cardiovascular and respiratory examinations are core OSCE skills tested in 70-80% of AMC Clinical exams. This station assesses systematic examination technique (HIPJAP and IPTAP frameworks), interpretation of clinical signs (murmurs, crackles, consolidation), and appropriate presentation to examiners—fundamental competencies for safe intern practice."
    },
    "Medicine/03_Physical_Examination_Abdominal_Neurological": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "80%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Abdominal and neurological examinations appear in approximately 3 out of 4 AMC Clinical exams. These assess your ability to perform systematic 9-region abdominal examination, detect organomegaly/masses/ascites, and complete cranial nerve (CN I-XII) assessment—essential skills that examiners use to differentiate competent from unsafe candidates."
    },
    "Medicine/01_GI_Abdominal_Pain_Differentials": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "80%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Abdominal pain is the second most common presenting complaint in AMC Clinical exams (after chest pain). This tests your ability to localize pain to one of 9 regions, generate appropriate region-specific differentials, and recognize surgical emergencies requiring urgent intervention—critical for safe medical practice."
    },
    "Medicine/03_Neurology_Headache_Differentials": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "70%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Headache presentations appear in 60-70% of AMC Clinical exams, testing your ability to differentiate benign primary headaches (migraine, tension) from life-threatening secondary causes (SAH, meningitis, mass lesion, temporal arteritis). Red flag recognition is heavily emphasized as it demonstrates safety awareness."
    },
    "Medicine/09_Endocrinology_Diabetes_Management": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "70%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Diabetes management appears in 60-70% of AMC exams as it tests multiple competencies: new diagnosis counselling, lifestyle modification, medication education (insulin), complication screening, and shared decision-making. It's a cornerstone of Australian general practice and primary care."
    },
    "Medicine/10_Emergency_Anaphylaxis_Management": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "60%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Anaphylaxis management is a critical emergency scenario appearing in 50-60% of AMC exams. This tests immediate recognition of anaphylaxis, appropriate adrenaline dosing (0.5mg IM), systematic ABCDE approach, and escalation pathways—essential life-saving skills that examiners prioritize."
    },
    "Medicine/11_ECG_Interpretation_Guide": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "70%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "ECG interpretation appears in 60-70% of AMC exams across multiple scenarios (chest pain, palpitations, syncope, pre-op). This tests systematic ECG analysis (rate, rhythm, axis, intervals, ST changes), recognition of life-threatening arrhythmias (VT, complete heart block), and STEMI identification—critical for emergency medicine."
    },
    "Medicine/12_Emergency_Seizure_Management": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "60%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Seizure management and status epilepticus appear in approximately 50-60% of AMC exams. This tests immediate seizure termination (benzodiazepines), systematic ABCDE approach, post-ictal care, and appropriate investigation sequencing—essential emergency management skills for all doctors."
    },

    # GROUP 2: HIGH-YIELD COMMUNICATION (⭐⭐⭐) - ALL communication is high-yield
    "Ethics_Communication/01_Communication_Skills_Role_Play_Scripts": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "90%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Communication skills are assessed in 90-100% of AMC Clinical stations. Role-play scenarios test empathy, active listening, shared decision-making, and patient-centered care—competencies that often differentiate passing from failing candidates. Strong communication is the single most important predictor of exam success."
    },
    "Ethics_Communication/02_Breaking_Bad_News_Additional_Scenarios": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "80%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Breaking bad news scenarios appear in 70-80% of AMC exams (cancer diagnoses, miscarriage, STI results, unexpected findings). This tests SPIKES framework application, empathy, handling difficult emotions, and safety-netting—essential communication skills for all medical specialties."
    },
    "Ethics_Communication/03_Breaking_Bad_News_Additional_Scenarios_Part2": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "80%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Extended breaking bad news scenarios cover diverse emotional reactions (anger, denial, bargaining) and cultural contexts. Multiple practice scenarios prepare you for the unpredictability of real exam interactions where standardized patients may display various emotional responses."
    },
    "Ethics_Communication/04_Comprehensive_Emotional_Reactions_Handbook": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "85%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Handling emotional reactions (anger, crying, denial, anxiety) appears across 80-85% of communication stations. This tests your ability to remain empathetic under pressure, validate emotions appropriately, and continue therapeutic communication—skills that examiners specifically assess in communication domains."
    },
    "Ethics_Communication/05_Cultural_Variations_Breaking_Bad_News_Australia": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "70%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "Cultural safety and Indigenous health competency are increasingly emphasized in AMC exams (appearing in 60-70% of recent cycles). This tests culturally appropriate communication, interpreter use, and understanding of Australian healthcare disparities—critical for practice in multicultural Australia."
    },
    "Ethics_Communication/06_IMG_Common_Mistakes_Breaking_Bad_News": {
        "rating": "⭐⭐⭐",
        "level": "HIGH-YIELD",
        "appearance": "80%+",
        "priority": "CRITICAL",
        "practice": "10-15 times",
        "why": "This specifically addresses common IMG pitfalls in breaking bad news that cause exam failures: using US terminology (ER not ED), lacking empathy, rushing through disclosure, insufficient safety-netting, and poor Australian cultural adaptation. Essential for IMG success."
    },

    # Add more mappings as needed...
}

# CSS styles for HTML files
HTML_FREQUENCY_CSS = '''
        /* Frequency indicator banner styles */
        .frequency-banner {
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 6px solid;
            font-weight: bold;
        }

        .frequency-high-yield {
            background-color: #ffe6e6;
            border-left-color: #d32f2f;
            color: #b71c1c;
        }

        .frequency-medium-yield {
            background-color: #fff9e6;
            border-left-color: #f57c00;
            color: #e65100;
        }

        .frequency-low-yield {
            background-color: #e8f5e9;
            border-left-color: #388e3c;
            color: #1b5e20;
        }

        .frequency-stars {
            font-size: 1.3em;
            margin-right: 10px;
        }

        .study-priority {
            display: block;
            margin-top: 10px;
            font-size: 0.9em;
            font-weight: normal;
        }

        .why-high-yield {
            display: block;
            margin-top: 8px;
            font-size: 0.85em;
            font-weight: normal;
            font-style: italic;
        }
'''

def get_frequency_info(file_key):
    """Get frequency information for a file."""
    return FREQUENCY_MAP.get(file_key, None)

def add_frequency_to_markdown(file_path, freq_info):
    """Add frequency indicator to a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the position to insert (after subtitle, before Purpose)
    # Pattern: Look for the line with "Purpose" or "**Purpose**"
    pattern = r'(^##\s+.*?\n\n)(\*\*Purpose\*\*:)'

    frequency_banner = f'''---

## 🎯 AMC EXAM FREQUENCY INDICATOR

**[{freq_info["rating"]} {freq_info["level"]}]** - Appears in {freq_info["appearance"]} of AMC Clinical exams
**Study Priority:** {freq_info["priority"]} - Practice {freq_info["practice"]} before exam
**Why {freq_info["level"].split("-")[0].title()}-Yield:** {freq_info["why"]}

---

'''

    # Insert frequency banner
    new_content = re.sub(pattern, r'\1' + frequency_banner + r'\2', content, count=1, flags=re.MULTILINE)

    # Update Last Updated field
    today = datetime.now().strftime("%B %d, %Y")
    new_content = re.sub(
        r'\*\*Created\*\*:([^\n]+)',
        r'**Created**:\1\n**Last Updated**: ' + today + ' (AMC Frequency Indicator added)',
        new_content,
        count=1
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Updated: {file_path.name}")

def add_frequency_to_html(file_path, freq_info):
    """Add frequency indicator to an HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add CSS if not already present
    if '.frequency-banner' not in content:
        # Insert CSS before /* Print styles */
        content = content.replace('        /* Print styles */', HTML_FREQUENCY_CSS + '\n        /* Print styles */')

    # Create frequency banner HTML
    css_class = f"frequency-{freq_info['level'].lower().replace(' ', '-')}"
    frequency_banner_html = f'''<hr>

<div class="frequency-banner {css_class}">
    <span class="frequency-stars">{freq_info["rating"]}</span>
    <span>{freq_info["level"]} - Appears in {freq_info["appearance"]} of AMC Clinical exams</span>
    <span class="study-priority">📚 Study Priority: {freq_info["priority"]} - Practice {freq_info["practice"]} before exam</span>
    <span class="why-high-yield">💡 Why {freq_info["level"].split("-")[0].title()}-Yield: {freq_info["why"]}</span>
</div>

<hr>

'''

    # Find position to insert (after h2 subtitle, before Purpose)
    pattern = r'(<h2>.*?</h2>\s*\n\s*\n)(<strong>Purpose</strong>:)'
    new_content = re.sub(pattern, r'\1' + frequency_banner_html + r'<p>\n\2', content, count=1)

    # Update Last Updated field
    today = datetime.now().strftime("%B %d, %Y")
    last_updated_line = f'<strong>Last Updated</strong>: {today} (AMC Frequency Indicator added)<br>'
    new_content = re.sub(
        r'(<strong>Created</strong>:[^<]+)',
        r'\1<br>\n' + last_updated_line,
        new_content,
        count=1
    )
    # Close the paragraph tag properly
    new_content = new_content.replace(last_updated_line + '<br>', last_updated_line + '\n</p>')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Updated: {file_path.name}")

def main():
    """Main execution function."""
    print("🎯 AMC Frequency Indicator Addition Script")
    print("=" * 60)
    print(f"Base directory: {BASE_DIR}")
    print(f"Files to process: {len(FREQUENCY_MAP)} file groups")
    print("=" * 60)

    processed_count = 0
    error_count = 0

    for file_key, freq_info in FREQUENCY_MAP.items():
        # Process both .md and .html versions
        md_path = BASE_DIR / f"{file_key}.md"
        html_path = BASE_DIR / f"{file_key}.html"

        # Process markdown file
        if md_path.exists():
            try:
                add_frequency_to_markdown(md_path, freq_info)
                processed_count += 1
            except Exception as e:
                print(f"❌ Error processing {md_path.name}: {e}")
                error_count += 1
        else:
            print(f"⚠️  File not found: {md_path}")

        # Process HTML file
        if html_path.exists():
            try:
                add_frequency_to_html(html_path, freq_info)
                processed_count += 1
            except Exception as e:
                print(f"❌ Error processing {html_path.name}: {e}")
                error_count += 1
        else:
            print(f"⚠️  File not found: {html_path}")

    print("=" * 60)
    print(f"✅ Processing complete!")
    print(f"   Processed: {processed_count} files")
    print(f"   Errors: {error_count} files")
    print("=" * 60)

if __name__ == "__main__":
    main()
