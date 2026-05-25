#!/bin/bash
# MVP Content Audit Script
# Phase 1: Document baseline inventory of educational content
#
# PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
# Purpose: Count existing MCQs, OSCEs, EMR personas, and Mock Exam templates

set -e

echo "========================================="
echo "MVP Content Audit"
echo "========================================="
echo "Date: $(date +%Y-%m-%d\ %H:%M:%S)"
echo ""

cd /home/dev/Development/irStudy/backend

# Export DATABASE_PASSWORD to avoid connection errors during audit
export DATABASE_PASSWORD="dev_password_2024"

# Count MCQs in database
echo "Counting MCQs in database..."
MCQ_COUNT=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import MCQ

try:
    db = SessionLocal()
    count = db.query(MCQ).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
    sys.stderr.write(f'Error counting MCQs: {e}\n')
" 2>&1 | tail -1)

echo "MCQs in database: $MCQ_COUNT"

# Count MCQ specialty distribution
echo "Counting MCQ specialty distribution..."
MCQ_CARDIOLOGY=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import MCQ, MedicalSpecialty

try:
    db = SessionLocal()
    count = db.query(MCQ).filter(MCQ.specialty == MedicalSpecialty.CARDIOLOGY).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
" 2>&1 | tail -1)

MCQ_RESPIRATORY=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import MCQ, MedicalSpecialty

try:
    db = SessionLocal()
    count = db.query(MCQ).filter(MCQ.specialty == MedicalSpecialty.RESPIRATORY).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
" 2>&1 | tail -1)

MCQ_PSYCHIATRY=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import MCQ, MedicalSpecialty

try:
    db = SessionLocal()
    count = db.query(MCQ).filter(MCQ.specialty == MedicalSpecialty.PSYCHIATRY).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
" 2>&1 | tail -1)

echo "  - Cardiology: $MCQ_CARDIOLOGY"
echo "  - Respiratory: $MCQ_RESPIRATORY"
echo "  - Psychiatry: $MCQ_PSYCHIATRY"

# Count OSCEs in database
echo ""
echo "Counting OSCEs in database..."
OSCE_COUNT=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import OSCE

try:
    db = SessionLocal()
    count = db.query(OSCE).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
    sys.stderr.write(f'Error counting OSCEs: {e}\n')
" 2>&1 | tail -1)

echo "OSCEs in database: $OSCE_COUNT"

# Count OSCE specialty distribution
echo "Counting OSCE specialty distribution..."
OSCE_CARDIOLOGY=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import OSCE, MedicalSpecialty

try:
    db = SessionLocal()
    count = db.query(OSCE).filter(OSCE.specialty == MedicalSpecialty.CARDIOLOGY).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
" 2>&1 | tail -1)

OSCE_RESPIRATORY=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import OSCE, MedicalSpecialty

try:
    db = SessionLocal()
    count = db.query(OSCE).filter(OSCE.specialty == MedicalSpecialty.RESPIRATORY).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
" 2>&1 | tail -1)

OSCE_PSYCHIATRY=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import OSCE, MedicalSpecialty

try:
    db = SessionLocal()
    count = db.query(OSCE).filter(OSCE.specialty == MedicalSpecialty.PSYCHIATRY).count()
    print(count)
    db.close()
except Exception as e:
    print('0')
" 2>&1 | tail -1)

echo "  - Cardiology: $OSCE_CARDIOLOGY"
echo "  - Respiratory: $OSCE_RESPIRATORY"
echo "  - Psychiatry: $OSCE_PSYCHIATRY"

# Count EMR Personas (PatientPersona or MockPatient)
echo ""
echo "Counting EMR Patient Personas..."
PERSONA_COUNT=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import PatientPersona

try:
    db = SessionLocal()
    count = db.query(PatientPersona).count()
    print(count)
    db.close()
except Exception as e:
    # Try MockPatient if PatientPersona doesn't exist
    try:
        from src.db.models import MockPatient
        db = SessionLocal()
        count = db.query(MockPatient).count()
        print(count)
        db.close()
    except Exception as e2:
        print('0')
        sys.stderr.write(f'Error counting personas: {e2}\n')
" 2>&1 | tail -1)

echo "EMR Personas in database: $PERSONA_COUNT"

# Count Mock Exam Templates (if model exists)
echo ""
echo "Counting Mock Exam Templates..."
TEMPLATE_COUNT=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal

try:
    from src.db.models import MockExamTemplate
    db = SessionLocal()
    count = db.query(MockExamTemplate).count()
    print(count)
    db.close()
except ImportError:
    # Model doesn't exist yet
    print('0')
    sys.stderr.write('MockExamTemplate model not found\n')
except Exception as e:
    print('0')
    sys.stderr.write(f'Error counting templates: {e}\n')
" 2>&1 | tail -1)

echo "Mock Exam Templates in database: $TEMPLATE_COUNT"

# Count files in data directories
echo ""
echo "========================================="
echo "File System Inventory"
echo "========================================="

# Count OSCE JSON files
OSCE_FILES=$(find /home/dev/Development/irStudy/data/osces -name "*_osces.json" -type f 2>/dev/null | wc -l)
echo "OSCE JSON files: $OSCE_FILES"

# List main OSCE files
echo "Main OSCE files:"
ls -lh /home/dev/Development/irStudy/data/osces/cardiology_50_osces.json 2>/dev/null || echo "  - cardiology_50_osces.json: NOT FOUND"
ls -lh /home/dev/Development/irStudy/data/osces/respiratory_50_osces.json 2>/dev/null || echo "  - respiratory_50_osces.json: NOT FOUND"
ls -lh /home/dev/Development/irStudy/data/osces/psychiatry_40_osces.json 2>/dev/null || echo "  - psychiatry_40_osces.json: NOT FOUND"

# Count MCQ JSON files
MCQ_FILES=$(find /home/dev/Development/irStudy/data/mcqs -name "*.json" -type f 2>/dev/null | wc -l)
echo ""
echo "MCQ JSON files: $MCQ_FILES"

# List main MCQ files
echo "Main MCQ files:"
ls -lh /home/dev/Development/irStudy/data/mcqs/week3_cardiology_200_mcqs.json 2>/dev/null || echo "  - cardiology MCQs: NOT FOUND"
ls -lh /home/dev/Development/irStudy/data/mcqs/week3_respiratory_200_mcqs.json 2>/dev/null || echo "  - respiratory MCQs: NOT FOUND"
ls -lh /home/dev/Development/irStudy/data/mcqs/psychiatry_final_day5.json 2>/dev/null || echo "  - psychiatry MCQs: NOT FOUND"

# Count EMR persona files
echo ""
PERSONA_FILES=$(find /home/dev/Development/irStudy/data/emr -name "*.json" -type f 2>/dev/null | wc -l)
echo "EMR persona JSON files: $PERSONA_FILES"

# Check for batch_1_207_personas.json
if [ -f "/home/dev/Development/irStudy/data/emr/patient_personas/batch_1_207_personas.json" ]; then
    BATCH1_SIZE=$(wc -c < /home/dev/Development/irStudy/data/emr/patient_personas/batch_1_207_personas.json)
    echo "  - batch_1_207_personas.json: $(numfmt --to=iec-i --suffix=B $BATCH1_SIZE)"
fi

# Generate report
echo ""
echo "========================================="
echo "Generating Audit Report"
echo "========================================="

cat > /home/dev/Development/irStudy/backend/MVP_CONTENT_AUDIT_REPORT.md <<EOF
# MVP Content Audit Report

**Date**: $(date +"%Y-%m-%d %H:%M:%S")
**PRD**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
**Phase**: 1 - Baseline Inventory

---

## Executive Summary

This audit documents the current state of educational content in the irStudy platform database and file system.

### Database Inventory

| Content Type | Current Count | MVP Target | Status |
|-------------|---------------|------------|--------|
| MCQs (Total) | $MCQ_COUNT | 200 | $(if [ $MCQ_COUNT -ge 200 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((200 - MCQ_COUNT)) more)"; fi) |
| - Cardiology MCQs | $MCQ_CARDIOLOGY | 60 | $(if [ $MCQ_CARDIOLOGY -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((60 - MCQ_CARDIOLOGY)) more)"; fi) |
| - Respiratory MCQs | $MCQ_RESPIRATORY | 60 | $(if [ $MCQ_RESPIRATORY -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((60 - MCQ_RESPIRATORY)) more)"; fi) |
| - Psychiatry MCQs | $MCQ_PSYCHIATRY | 60 | $(if [ $MCQ_PSYCHIATRY -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((60 - MCQ_PSYCHIATRY)) more)"; fi) |
| OSCEs (Total) | $OSCE_COUNT | 50 | $(if [ $OSCE_COUNT -ge 50 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((50 - OSCE_COUNT)) more)"; fi) |
| - Cardiology OSCEs | $OSCE_CARDIOLOGY | 15 | $(if [ $OSCE_CARDIOLOGY -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((15 - OSCE_CARDIOLOGY)) more)"; fi) |
| - Respiratory OSCEs | $OSCE_RESPIRATORY | 15 | $(if [ $OSCE_RESPIRATORY -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((15 - OSCE_RESPIRATORY)) more)"; fi) |
| - Psychiatry OSCEs | $OSCE_PSYCHIATRY | 15 | $(if [ $OSCE_PSYCHIATRY -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((15 - OSCE_PSYCHIATRY)) more)"; fi) |
| EMR Personas | $PERSONA_COUNT | 100 | $(if [ $PERSONA_COUNT -ge 100 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((100 - PERSONA_COUNT)) more)"; fi) |
| Mock Exam Templates | $TEMPLATE_COUNT | 3 | $(if [ $TEMPLATE_COUNT -ge 3 ]; then echo "✅ PASS"; else echo "❌ FAIL (need $((3 - TEMPLATE_COUNT)) more)"; fi) |

### File System Inventory

- **OSCE Files**: $OSCE_FILES JSON files in \`data/osces/\`
- **MCQ Files**: $MCQ_FILES JSON files in \`data/mcqs/\`
- **EMR Persona Files**: $PERSONA_FILES JSON files in \`data/emr/\`

### Known Data Sources

**OSCEs** (140 total available):
- \`data/osces/cardiology_50_osces.json\` (50 OSCEs)
- \`data/osces/respiratory_50_osces.json\` (50 OSCEs)
- \`data/osces/psychiatry_40_osces.json\` (40 OSCEs)

**EMR Personas** (207 total available):
- \`data/emr/patient_personas/batch_1_207_personas.json\`

**MCQs** (location varies):
- \`data/mcqs/week3_cardiology_200_mcqs.json\`
- \`data/mcqs/week3_respiratory_200_mcqs.json\`
- \`data/mcqs/psychiatry_final_day5.json\`

---

## Detailed Findings

### 1. MCQs

**Database Status**: $MCQ_COUNT MCQs currently in database

**Specialty Distribution**:
- Cardiology: $MCQ_CARDIOLOGY (target: ≥60)
- Respiratory: $MCQ_RESPIRATORY (target: ≥60)
- Psychiatry: $MCQ_PSYCHIATRY (target: ≥60)

**Assessment**:
$(if [ $MCQ_COUNT -ge 200 ]; then
    echo "✅ MCQ count meets MVP requirement (≥200)"
else
    echo "❌ MCQ count BELOW MVP requirement"
    echo "   - Current: $MCQ_COUNT"
    echo "   - Required: 200"
    echo "   - Gap: $((200 - MCQ_COUNT)) MCQs needed"
fi)

**Specialty Balance**:
$(if [ $MCQ_CARDIOLOGY -ge 60 ] && [ $MCQ_RESPIRATORY -ge 60 ] && [ $MCQ_PSYCHIATRY -ge 60 ]; then
    echo "✅ All specialties meet minimum requirement (≥60 each)"
else
    echo "❌ Some specialties below minimum:"
    [ $MCQ_CARDIOLOGY -lt 60 ] && echo "   - Cardiology: Need $((60 - MCQ_CARDIOLOGY)) more"
    [ $MCQ_RESPIRATORY -lt 60 ] && echo "   - Respiratory: Need $((60 - MCQ_RESPIRATORY)) more"
    [ $MCQ_PSYCHIATRY -lt 60 ] && echo "   - Psychiatry: Need $((60 - MCQ_PSYCHIATRY)) more"
fi)

### 2. OSCEs

**Database Status**: $OSCE_COUNT OSCEs currently in database

**Specialty Distribution**:
- Cardiology: $OSCE_CARDIOLOGY (target: ≥15)
- Respiratory: $OSCE_RESPIRATORY (target: ≥15)
- Psychiatry: $OSCE_PSYCHIATRY (target: ≥15)

**Assessment**:
$(if [ $OSCE_COUNT -ge 50 ]; then
    echo "✅ OSCE count meets MVP requirement (≥50)"
else
    echo "❌ OSCE count BELOW MVP requirement"
    echo "   - Current: $OSCE_COUNT"
    echo "   - Required: 50"
    echo "   - Gap: $((50 - OSCE_COUNT)) OSCEs needed"
    echo ""
    echo "**Available Source Data**: 140 OSCEs in JSON files (ready to import)"
fi)

**Specialty Balance**:
$(if [ $OSCE_CARDIOLOGY -ge 15 ] && [ $OSCE_RESPIRATORY -ge 15 ] && [ $OSCE_PSYCHIATRY -ge 15 ]; then
    echo "✅ All specialties meet minimum requirement (≥15 each)"
else
    echo "❌ Some specialties below minimum:"
    [ $OSCE_CARDIOLOGY -lt 15 ] && echo "   - Cardiology: Need $((15 - OSCE_CARDIOLOGY)) more"
    [ $OSCE_RESPIRATORY -lt 15 ] && echo "   - Respiratory: Need $((15 - OSCE_RESPIRATORY)) more"
    [ $OSCE_PSYCHIATRY -lt 15 ] && echo "   - Psychiatry: Need $((15 - OSCE_PSYCHIATRY)) more"
fi)

### 3. EMR Patient Personas

**Database Status**: $PERSONA_COUNT personas currently in database

**Assessment**:
$(if [ $PERSONA_COUNT -ge 100 ]; then
    echo "✅ Persona count meets MVP requirement (≥100)"
else
    echo "❌ Persona count BELOW MVP requirement"
    echo "   - Current: $PERSONA_COUNT"
    echo "   - Required: 100"
    echo "   - Gap: $((100 - PERSONA_COUNT)) personas needed"
    echo ""
    echo "**Available Source Data**: 207 personas in batch_1_207_personas.json (ready to import)"
fi)

### 4. Mock Exam Templates

**Database Status**: $TEMPLATE_COUNT templates currently in database

**Assessment**:
$(if [ $TEMPLATE_COUNT -ge 3 ]; then
    echo "✅ Template count meets MVP requirement (≥3)"
else
    echo "❌ Template count BELOW MVP requirement"
    echo "   - Current: $TEMPLATE_COUNT"
    echo "   - Required: 3"
    echo "   - Gap: $((3 - TEMPLATE_COUNT)) templates needed"
    echo ""
    echo "**Action Required**: Create 3 mock exam templates (16-station format)"
fi)

---

## Next Steps

### Phase 2: Content Validation
Run \`scripts/validate_content_mvp.sh\` to:
- Execute Tests 1-8 (PRD section T)
- Validate RAG citations (≥95% coverage)
- Check for placeholder content (TODO, Lorem ipsum)
- Generate detailed gap report

### Phase 3: Content Population
Based on gaps identified:
1. **Import OSCEs**: Run \`scripts/import_osces.py\` (140 available)
2. **Import MCQs**: Run \`scripts/import_mcqs.py\` (verify availability)
3. **Import EMR Personas**: Run \`scripts/import_patient_personas.py\` (207 available)
4. **Create Templates**: Run \`scripts/create_mock_exam_templates.py\` (3 required)

---

## Quality Gates Status

| Gate | Requirement | Status |
|------|-------------|--------|
| MCQ Count | ≥200 | $(if [ $MCQ_COUNT -ge 200 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| MCQ Balance | ≥60 per specialty | $(if [ $MCQ_CARDIOLOGY -ge 60 ] && [ $MCQ_RESPIRATORY -ge 60 ] && [ $MCQ_PSYCHIATRY -ge 60 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| OSCE Count | ≥50 | $(if [ $OSCE_COUNT -ge 50 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| OSCE Balance | ≥15 per specialty | $(if [ $OSCE_CARDIOLOGY -ge 15 ] && [ $OSCE_RESPIRATORY -ge 15 ] && [ $OSCE_PSYCHIATRY -ge 15 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| EMR Personas | ≥100 | $(if [ $PERSONA_COUNT -ge 100 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |
| Mock Templates | ≥3 | $(if [ $TEMPLATE_COUNT -ge 3 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi) |

**Overall Readiness**: $(if [ $MCQ_COUNT -ge 200 ] && [ $OSCE_COUNT -ge 50 ] && [ $PERSONA_COUNT -ge 100 ] && [ $TEMPLATE_COUNT -ge 3 ]; then echo "✅ READY FOR MVP"; else echo "❌ NOT READY (see gaps above)"; fi)

---

**Generated by**: scripts/audit_mvp_content.sh
**PRD Reference**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
EOF

echo ""
echo "✅ Audit complete!"
echo ""
echo "Report generated: /home/dev/Development/irStudy/backend/MVP_CONTENT_AUDIT_REPORT.md"
echo ""
echo "Summary:"
echo "  - MCQs: $MCQ_COUNT / 200 (target)"
echo "  - OSCEs: $OSCE_COUNT / 50 (target)"
echo "  - EMR Personas: $PERSONA_COUNT / 100 (target)"
echo "  - Mock Exam Templates: $TEMPLATE_COUNT / 3 (target)"
echo ""

if [ $MCQ_COUNT -ge 200 ] && [ $OSCE_COUNT -ge 50 ] && [ $PERSONA_COUNT -ge 100 ] && [ $TEMPLATE_COUNT -ge 3 ]; then
    echo "✅ ALL CONTENT TARGETS MET - MVP READY"
    exit 0
else
    echo "❌ Some content gaps identified - proceed to Phase 2 validation"
    exit 1
fi
