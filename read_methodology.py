#!/usr/bin/env python3
import os

# Read DR AAMIR Methodology Guide
print("=== READING DR_AAMIR_METHODOLOGY_GUIDE.html ===\n")
with open('/home/dev/Development/irStudy/DR_AAMIR_METHODOLOGY_GUIDE.html', 'r', encoding='utf-8') as f:
    content = f.read()
    # Find Template 2 section
    if 'Template 2: Physical Examination Station' in content:
        start = content.find('Template 2: Physical Examination Station')
        section = content[start:start+5000]
        print(section[:2000])
    else:
        print("Template 2 not found, showing first 2000 chars:")
        print(content[:2000])

print("\n\n=== READING EXISTING EXAMINATION FILE ===\n")
with open('/home/dev/Development/irStudy/ICRP_OSCE_Preparation/Medicine/02_Physical_Examination_Cardiovascular_Respiratory.html', 'r', encoding='utf-8') as f:
    content = f.read()
    print(content[:2000])

print("\n\n=== CHECKING PDF FILES ===\n")
pdf_dir = '/home/dev/Development/irStudy/Clinical_Examination_Split/'
if os.path.exists(pdf_dir):
    files = os.listdir(pdf_dir)
    for f in sorted(files):
        print(f)
else:
    print("PDF directory not found")
