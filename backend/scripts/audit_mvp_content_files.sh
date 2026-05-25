#!/bin/bash
# MVP Content Audit Script (File-Based)
# Phase 1: Document baseline inventory using JSON files only
#
# PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
# Purpose: Count existing MCQs, OSCEs, EMR personas in source files

set -e

echo "========================================="
echo "MVP Content Audit (File-Based)"
echo "========================================="
echo "Date: $(date +%Y-%m-%d\ %H:%M:%S)"
echo ""

cd /home/dev/Development/irStudy

# Count OSCEs in JSON files
echo "Counting OSCEs in source files..."
CARDIO_OSCES=$(python3 -c "
import json
try:
    with open('data/osces/cardiology_50_osces.json', 'r') as f:
        data = json.load(f)
        print(len(data.get('osces', data.get('scenarios', []))))
except:
    print(0)
")

RESP_OSCES=$(python3 -c "
import json
try:
    with open('data/osces/respiratory_50_osces.json', 'r') as f:
        data = json.load(f)
        print(len(data.get('osces', data.get('scenarios', []))))
except:
    print(0)
")

PSYCH_OSCES=$(python3 -c "
import json
try:
    with open('data/osces/psychiatry_40_osces.json', 'r') as f:
        data = json.load(f)
        print(len(data.get('osces', data.get('scenarios', []))))
except:
    print(0)
")

TOTAL_OSCES=$((CARDIO_OSCES + RESP_OSCES + PSYCH_OSCES))

echo "  - Cardiology: $CARDIO_OSCES"
echo "  - Respiratory: $RESP_OSCES"
echo "  - Psychiatry: $PSYCH_OSCES"
echo "  - Total: $TOTAL_OSCES"

# Count MCQs in JSON files
echo ""
echo "Counting MCQs in source files..."

CARDIO_MCQS=$(python3 -c "
import json
try:
    with open('data/mcqs/week3_cardiology_200_mcqs.json', 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            print(len(data))
        elif isinstance(data, dict) and 'questions' in data:
            print(len(data['questions']))
        else:
            print(len(data.get('mcqs', [])))
except:
    print(0)
")

RESP_MCQS=$(python3 -c "
import json
try:
    with open('data/mcqs/week3_respiratory_200_mcqs.json', 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            print(len(data))
        elif isinstance(data, dict) and 'questions' in data:
            print(len(data['questions']))
        else:
            print(len(data.get('mcqs', [])))
except:
    print(0)
")

PSYCH_MCQS=$(python3 -c "
import json
try:
    with open('data/mcqs/psychiatry_final_day5.json', 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            print(len(data))
        elif isinstance(data, dict) and 'questions' in data:
            print(len(data['questions']))
        else:
            print(len(data.get('mcqs', [])))
except:
    print(0)
")

TOTAL_MCQS=$((CARDIO_MCQS + RESP_MCQS + PSYCH_MCQS))

echo "  - Cardiology: $CARDIO_MCQS"
echo "  - Respiratory: $RESP_MCQS"
echo "  - Psychiatry: $PSYCH_MCQS"
echo "  - Total: $TOTAL_MCQS"

# Count EMR Personas
echo ""
echo "Counting EMR Patient Personas in source files..."

PERSONA_COUNT=$(find clinical-content-prds/validation-system/batch1_personas -name "*_persona.json" -type f 2>/dev/null | grep -v "_qa_report" | wc -l)
echo "  - Individual persona files: $PERSONA_COUNT"

# Mock exam templates (not yet created)
TEMPLATE_COUNT=0
echo ""
echo "Mock Exam Templates: $TEMPLATE_COUNT (not yet created)"

# File system inventory
echo ""
echo "========================================="
echo "File System Inventory"
echo "========================================="

OSCE_FILES=$(find data/osces -name "*_osces.json" -type f 2>/dev/null | wc -l)
echo "OSCE JSON files: $OSCE_FILES"

MCQ_FILES=$(find data/mcqs -name "*.json" -type f 2>/dev/null | wc -l)
echo "MCQ JSON files: $MCQ_FILES"

# Generate detailed report
cat > /home/dev/Development/irStudy/backend/MVP_CONTENT_AUDIT_REPORT.md <<EOF
# MVP Content Audit Report (File-Based)

**Date**: $(date +"%Y-%m-%d %H:%M:%S")
**PRD**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
**Phase**: 1 - Baseline Inventory

---

## Executive Summary

This audit documents educational content available in source JSON files (database import pending).

### Content Availability (Source Files)

| Content Type | Available | MVP Target | Status |
|-------------|-----------|------------|--------|
| **MCQs (Total)** | **$TOTAL_MCQS** | 200 | $(if [ $TOTAL_MCQS -ge 200 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((200 - TOTAL_MCQS)) more)"; fi) |
| - Cardiology MCQs | $CARDIO_MCQS | 60 | $(if [ $CARDIO_MCQS -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| - Respiratory MCQs | $RESP_MCQS | 60 | $(if [ $RESP_MCQS -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| - Psychiatry MCQs | $PSYCH_MCQS | 60 | $(if [ $PSYCH_MCQS -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| **OSCEs (Total)** | **$TOTAL_OSCES** | 50 | $(if [ $TOTAL_OSCES -ge 50 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| - Cardiology OSCEs | $CARDIO_OSCES | 15 | $(if [ $CARDIO_OSCES -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| - Respiratory OSCEs | $RESP_OSCES | 15 | $(if [ $RESP_OSCES -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| - Psychiatry OSCEs | $PSYCH_OSCES | 15 | $(if [ $PSYCH_OSCES -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| **EMR Personas** | **$PERSONA_COUNT** | 100 | $(if [ $PERSONA_COUNT -ge 100 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| **Mock Exam Templates** | **$TEMPLATE_COUNT** | 3 | ❌ FAIL (need 3) |

---

## Detailed Findings

### 1. MCQs

**Source Files**: $TOTAL_MCQS MCQs available

**Files**:
- \`data/mcqs/week3_cardiology_200_mcqs.json\`: $CARDIO_MCQS MCQs
- \`data/mcqs/week3_respiratory_200_mcqs.json\`: $RESP_MCQS MCQs
- \`data/mcqs/psychiatry_final_day5.json\`: $PSYCH_MCQS MCQs

**Specialty Distribution**:
- Cardiology: $CARDIO_MCQS (target: ≥60) $(if [ $CARDIO_MCQS -ge 60 ]; then echo "✅"; else echo "❌"; fi)
- Respiratory: $RESP_MCQS (target: ≥60) $(if [ $RESP_MCQS -ge 60 ]; then echo "✅"; else echo "❌"; fi)
- Psychiatry: $PSYCH_MCQS (target: ≥60) $(if [ $PSYCH_MCQS -ge 60 ]; then echo "✅"; else echo "❌"; fi)

**Assessment**:
$(if [ $TOTAL_MCQS -ge 200 ]; then
    echo "✅ MCQ count MEETS MVP requirement (≥200)"
    echo ""
    echo "**Action Required**: Import MCQs into database using \`scripts/import_mcqs.py\`"
else
    echo "❌ MCQ count BELOW MVP requirement"
    echo ""
    echo "**Gap Analysis**:"
    echo "- Current available: $TOTAL_MCQS"
    echo "- Required: 200"
    echo "- Gap: $((200 - TOTAL_MCQS)) MCQs needed"
    echo ""
    if [ $TOTAL_MCQS -gt 0 ]; then
        echo "**Action Required**: Import existing + generate additional MCQs"
    else
        echo "**Action Required**: Generate 200 MCQs across 3 specialties"
    fi
fi)

---

### 2. OSCEs

**Source Files**: $TOTAL_OSCES OSCEs available

**Files**:
- \`data/osces/cardiology_50_osces.json\`: $CARDIO_OSCES scenarios
- \`data/osces/respiratory_50_osces.json\`: $RESP_OSCES scenarios
- \`data/osces/psychiatry_40_osces.json\`: $PSYCH_OSCES scenarios

**Specialty Distribution**:
- Cardiology: $CARDIO_OSCES (target: ≥15) $(if [ $CARDIO_OSCES -ge 15 ]; then echo "✅"; else echo "❌"; fi)
- Respiratory: $RESP_OSCES (target: ≥15) $(if [ $RESP_OSCES -ge 15 ]; then echo "✅"; else echo "❌"; fi)
- Psychiatry: $PSYCH_OSCES (target: ≥15) $(if [ $PSYCH_OSCES -ge 15 ]; then echo "✅"; else echo "❌"; fi)

**Assessment**:
$(if [ $TOTAL_OSCES -ge 50 ]; then
    echo "✅ OSCE count EXCEEDS MVP requirement (≥50)"
    echo ""
    echo "**Available**: $TOTAL_OSCES OSCEs ready for import"
    echo "**Action Required**: Import OSCEs into database using \`scripts/import_osces.py\`"
else
    echo "❌ OSCE count BELOW MVP requirement"
    echo ""
    echo "**Gap**: Need $((50 - TOTAL_OSCES)) more OSCEs"
fi)

---

### 3. EMR Patient Personas

**Source Files**: $PERSONA_COUNT persona files available

**Location**: \`clinical-content-prds/validation-system/batch1_personas/\`

**Assessment**:
$(if [ $PERSONA_COUNT -ge 100 ]; then
    echo "✅ Persona count EXCEEDS MVP requirement (≥100)"
    echo ""
    echo "**Available**: $PERSONA_COUNT personas ready for import"
    echo "**Action Required**: Import personas into database using \`scripts/import_patient_personas.py\`"
else
    echo "❌ Persona count BELOW MVP requirement"
    echo ""
    echo "**Gap**: Need $((100 - PERSONA_COUNT)) more personas"
    echo "**Action Required**: Generate additional patient personas"
fi)

---

### 4. Mock Exam Templates

**Source Files**: $TEMPLATE_COUNT templates available

**Assessment**:
❌ Mock exam templates NOT YET CREATED

**Action Required**: Create 3 mock exam templates (16-station format):
1. General Practice template (balanced specialties)
2. Specialty-focused template (cardiology/respiratory)
3. Communication-heavy template (psychiatry/ethics)

Run: \`scripts/create_mock_exam_templates.py\`

---

## Quality Gates Status

| Gate | Requirement | Files Available | Status |
|------|-------------|-----------------|--------|
| MCQ Count | ≥200 | $TOTAL_MCQS | $(if [ $TOTAL_MCQS -ge 200 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| MCQ Balance | ≥60 per specialty | Card:$CARDIO_MCQS, Resp:$RESP_MCQS, Psych:$PSYCH_MCQS | $(if [ $CARDIO_MCQS -ge 60 ] && [ $RESP_MCQS -ge 60 ] && [ $PSYCH_MCQS -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| OSCE Count | ≥50 | $TOTAL_OSCES | $(if [ $TOTAL_OSCES -ge 50 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| OSCE Balance | ≥15 per specialty | Card:$CARDIO_OSCES, Resp:$RESP_OSCES, Psych:$PSYCH_OSCES | $(if [ $CARDIO_OSCES -ge 15 ] && [ $RESP_OSCES -ge 15 ] && [ $PSYCH_OSCES -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| EMR Personas | ≥100 | $PERSONA_COUNT | $(if [ $PERSONA_COUNT -ge 100 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| Mock Templates | ≥3 | $TEMPLATE_COUNT | ❌ FAIL |

**Content Availability**: $(if [ $TOTAL_MCQS -ge 200 ] && [ $TOTAL_OSCES -ge 50 ] && [ $PERSONA_COUNT -ge 100 ]; then echo "✅ SUFFICIENT (import + create templates)"; else echo "❌ INSUFFICIENT (gaps identified)"; fi)

---

## Next Steps

### Immediate Actions Required

1. **Import OSCEs** (✅ $TOTAL_OSCES available)
   \`\`\`bash
   python3 scripts/import_osces.py --source /home/dev/Development/irStudy/data/osces/
   \`\`\`

2. **Import MCQs** ($(if [ $TOTAL_MCQS -ge 200 ]; then echo "✅ $TOTAL_MCQS available"; else echo "❌ $TOTAL_MCQS available, need $((200 - TOTAL_MCQS)) more"; fi))
   \`\`\`bash
   python3 scripts/import_mcqs.py --source /home/dev/Development/irStudy/data/mcqs/
   \`\`\`

3. **Import EMR Personas** (✅ $PERSONA_COUNT available)
   \`\`\`bash
   python3 scripts/import_patient_personas.py --source clinical-content-prds/validation-system/batch1_personas/
   \`\`\`

4. **Create Mock Exam Templates** (❌ 0 available, need 3)
   \`\`\`bash
   python3 scripts/create_mock_exam_templates.py
   \`\`\`

### Phase 2: Content Validation
After imports, run validation:
\`\`\`bash
./scripts/validate_content_mvp.sh
\`\`\`

This will execute Tests 1-8 from PRD-MVP-003:
- Test 1-2: MCQ count and specialty balance
- Test 3-4: OSCE count and specialty balance
- Test 5: EMR persona count
- Test 6: Mock exam templates
- Test 7: Placeholder content detection
- Test 8: RAG citation coverage

---

**Generated by**: scripts/audit_mvp_content_files.sh
**PRD Reference**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
EOF

echo ""
echo "========================================="
echo "Audit Complete"
echo "========================================="
echo ""
echo "📄 Report: /home/dev/Development/irStudy/backend/MVP_CONTENT_AUDIT_REPORT.md"
echo ""
echo "Summary:"
echo "  MCQs: $TOTAL_MCQS / 200 $(if [ $TOTAL_MCQS -ge 200 ]; then echo "✅"; else echo "❌"; fi)"
echo "  OSCEs: $TOTAL_OSCES / 50 $(if [ $TOTAL_OSCES -ge 50 ]; then echo "✅"; else echo "❌"; fi)"
echo "  EMR Personas: $PERSONA_COUNT / 100 $(if [ $PERSONA_COUNT -ge 100 ]; then echo "✅"; else echo "❌"; fi)"
echo "  Mock Exam Templates: $TEMPLATE_COUNT / 3 ❌"
echo ""

if [ $TOTAL_MCQS -ge 200 ] && [ $TOTAL_OSCES -ge 50 ] && [ $PERSONA_COUNT -ge 100 ]; then
    echo "✅ Sufficient content available - proceed to import (Phase 3)"
    exit 0
else
    echo "⚠️  Some content gaps - see report for details"
    exit 1
fi
