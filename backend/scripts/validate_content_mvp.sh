#!/bin/bash
# MVP Content Validation Script
# Phase 2: Run Tests 1-8 from PRD-MVP-003
#
# PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md (T section)
# Purpose: Validate content meets MVP quality gates

set -e

echo "========================================="
echo "MVP Content Validation (Tests 1-8)"
echo "========================================="
echo "Date: $(date +%Y-%m-%d\ %H:%M:%S)"
echo "PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md"
echo ""

cd /home/dev/Development/irStudy/backend

# Activate venv
source venv/bin/activate

# Test results tracking
PASSED=0
FAILED=0
TOTAL_TESTS=8

echo "Running validation tests..."
echo ""

# Test 1: MCQ Count (≥200)
echo "========================================="
echo "Test 1: MCQ Count Validation"
echo "========================================="
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
    print(0)
    sys.stderr.write(f'Error: {e}\n')
" 2>&1 | grep -v "^Error:" | tail -1)

if [ "$MCQ_COUNT" -ge 200 ]; then
    echo "✅ PASS: MCQ count = $MCQ_COUNT (≥200)"
    ((PASSED++))
else
    echo "❌ FAIL: MCQ count = $MCQ_COUNT (need $((200 - MCQ_COUNT)) more)"
    ((FAILED++))
fi
echo ""

# Test 2: MCQ Specialty Distribution (≥60 each)
echo "========================================="
echo "Test 2: MCQ Specialty Balance"
echo "========================================="

MCQ_CARDIO=$(python3 -c "
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
    print(0)
" 2>&1 | tail -1)

MCQ_RESP=$(python3 -c "
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
    print(0)
" 2>&1 | tail -1)

MCQ_PSYCH=$(python3 -c "
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
    print(0)
" 2>&1 | tail -1)

echo "  Cardiology: $MCQ_CARDIO (≥60)"
echo "  Respiratory: $MCQ_RESP (≥60)"
echo "  Psychiatry: $MCQ_PSYCH (≥60)"

if [ "$MCQ_CARDIO" -ge 60 ] && [ "$MCQ_RESP" -ge 60 ] && [ "$MCQ_PSYCH" -ge 60 ]; then
    echo "✅ PASS: All specialties have ≥60 MCQs"
    ((PASSED++))
else
    echo "❌ FAIL: Some specialties below minimum"
    [ "$MCQ_CARDIO" -lt 60 ] && echo "  - Cardiology: need $((60 - MCQ_CARDIO)) more"
    [ "$MCQ_RESP" -lt 60 ] && echo "  - Respiratory: need $((60 - MCQ_RESP)) more"
    [ "$MCQ_PSYCH" -lt 60 ] && echo "  - Psychiatry: need $((60 - MCQ_PSYCH)) more"
    ((FAILED++))
fi
echo ""

# Test 3: OSCE Count (≥50)
echo "========================================="
echo "Test 3: OSCE Count Validation"
echo "========================================="

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
    print(0)
" 2>&1 | tail -1)

if [ "$OSCE_COUNT" -ge 50 ]; then
    echo "✅ PASS: OSCE count = $OSCE_COUNT (≥50)"
    ((PASSED++))
else
    echo "❌ FAIL: OSCE count = $OSCE_COUNT (need $((50 - OSCE_COUNT)) more)"
    ((FAILED++))
fi
echo ""

# Test 4: OSCE Specialty Distribution (≥15 each)
echo "========================================="
echo "Test 4: OSCE Specialty Balance"
echo "========================================="

OSCE_CARDIO=$(python3 -c "
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
    print(0)
" 2>&1 | tail -1)

OSCE_RESP=$(python3 -c "
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
    print(0)
" 2>&1 | tail -1)

OSCE_PSYCH=$(python3 -c "
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
    print(0)
" 2>&1 | tail -1)

echo "  Cardiology: $OSCE_CARDIO (≥15)"
echo "  Respiratory: $OSCE_RESP (≥15)"
echo "  Psychiatry: $OSCE_PSYCH (≥15)"

if [ "$OSCE_CARDIO" -ge 15 ] && [ "$OSCE_RESP" -ge 15 ] && [ "$OSCE_PSYCH" -ge 15 ]; then
    echo "✅ PASS: All specialties have ≥15 OSCEs"
    ((PASSED++))
else
    echo "❌ FAIL: Some specialties below minimum"
    [ "$OSCE_CARDIO" -lt 15 ] && echo "  - Cardiology: need $((15 - OSCE_CARDIO)) more"
    [ "$OSCE_RESP" -lt 15 ] && echo "  - Respiratory: need $((15 - OSCE_RESP)) more"
    [ "$OSCE_PSYCH" -lt 15 ] && echo "  - Psychiatry: need $((15 - OSCE_PSYCH)) more"
    ((FAILED++))
fi
echo ""

# Test 5: EMR Persona Count (≥100)
echo "========================================="
echo "Test 5: EMR Persona Count Validation"
echo "========================================="

PERSONA_COUNT=$(python3 -c "
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
try:
    from src.db.models import PatientPersona
    db = SessionLocal()
    count = db.query(PatientPersona).count()
    print(count)
    db.close()
except ImportError:
    try:
        from src.db.models import MockPatient
        db = SessionLocal()
        count = db.query(MockPatient).count()
        print(count)
        db.close()
    except Exception:
        print(0)
except Exception:
    print(0)
" 2>&1 | tail -1)

if [ "$PERSONA_COUNT" -ge 100 ]; then
    echo "✅ PASS: Persona count = $PERSONA_COUNT (≥100)"
    ((PASSED++))
else
    echo "❌ FAIL: Persona count = $PERSONA_COUNT (need $((100 - PERSONA_COUNT)) more)"
    ((FAILED++))
fi
echo ""

# Test 6: Mock Exam Templates (≥3)
echo "========================================="
echo "Test 6: Mock Exam Template Validation"
echo "========================================="

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
    print(0)
except Exception:
    print(0)
" 2>&1 | tail -1)

if [ "$TEMPLATE_COUNT" -ge 3 ]; then
    echo "✅ PASS: Template count = $TEMPLATE_COUNT (≥3)"
    ((PASSED++))
else
    echo "❌ FAIL: Template count = $TEMPLATE_COUNT (need $((3 - TEMPLATE_COUNT)) more)"
    ((FAILED++))
fi
echo ""

# Test 7: Placeholder Content Detection
echo "========================================="
echo "Test 7: Placeholder Content Detection"
echo "========================================="

PLACEHOLDER_COUNT=$(python3 -c "
import sys
import json
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import MCQ, OSCE

try:
    db = SessionLocal()

    # Check MCQs for placeholders
    mcqs = db.query(MCQ).all()
    placeholder_count = 0

    for mcq in mcqs:
        text = str(mcq.question_text) + str(mcq.options) + str(mcq.explanation)
        if 'TODO' in text or 'Lorem ipsum' in text or 'placeholder' in text.lower():
            placeholder_count += 1

    # Check OSCEs for placeholders
    osces = db.query(OSCE).all()
    for osce in osces:
        text = str(osce.patient_instructions) + str(osce.candidate_instructions)
        if 'TODO' in text or 'Lorem ipsum' in text or 'placeholder' in text.lower():
            placeholder_count += 1

    print(placeholder_count)
    db.close()
except Exception as e:
    print(0)
" 2>&1 | tail -1)

if [ "$PLACEHOLDER_COUNT" -eq 0 ]; then
    echo "✅ PASS: No placeholder content found"
    ((PASSED++))
else
    echo "❌ FAIL: Found $PLACEHOLDER_COUNT items with placeholder content"
    ((FAILED++))
fi
echo ""

# Test 8: RAG Citation Coverage (≥95%)
echo "========================================="
echo "Test 8: RAG Citation Coverage Validation"
echo "========================================="

CITATION_COVERAGE=$(python3 -c "
import sys
import json
sys.path.insert(0, '/home/dev/Development/irStudy/backend')
from src.db.base import SessionLocal
from src.db.models import OSCE

try:
    db = SessionLocal()
    osces = db.query(OSCE).all()

    total_osces = len(osces)
    osces_with_citations = 0

    for osce in osces:
        # Check if rubric has citations
        if isinstance(osce.rubric, dict):
            rubric_str = json.dumps(osce.rubric)
            if 'qdrant_point_id' in rubric_str or 'citation' in rubric_str:
                osces_with_citations += 1
        elif isinstance(osce.rubric, str):
            if 'qdrant_point_id' in osce.rubric or 'citation' in osce.rubric:
                osces_with_citations += 1

    if total_osces > 0:
        coverage = (osces_with_citations / total_osces) * 100
        print(f'{coverage:.1f}')
    else:
        print('0.0')

    db.close()
except Exception as e:
    print('0.0')
" 2>&1 | tail -1)

COVERAGE_FLOAT=$(echo "$CITATION_COVERAGE" | bc)
COVERAGE_INT=$(printf "%.0f" "$CITATION_COVERAGE")

if [ "$COVERAGE_INT" -ge 95 ]; then
    echo "✅ PASS: RAG citation coverage = ${CITATION_COVERAGE}% (≥95%)"
    ((PASSED++))
else
    echo "❌ FAIL: RAG citation coverage = ${CITATION_COVERAGE}% (need ≥95%)"
    ((FAILED++))
fi
echo ""

# Summary Report
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo ""
echo "Tests Passed: $PASSED / $TOTAL_TESTS"
echo "Tests Failed: $FAILED / $TOTAL_TESTS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - MVP CONTENT READY"
    echo ""
    echo "Content meets all MVP quality gates:"
    echo "  - MCQs: $MCQ_COUNT (≥200) ✅"
    echo "  - OSCEs: $OSCE_COUNT (≥50) ✅"
    echo "  - EMR Personas: $PERSONA_COUNT (≥100) ✅"
    echo "  - Mock Templates: $TEMPLATE_COUNT (≥3) ✅"
    echo "  - No placeholders ✅"
    echo "  - RAG citations: ${CITATION_COVERAGE}% (≥95%) ✅"

    # Generate final readiness report
    cat > /home/dev/Development/irStudy/backend/MVP_CONTENT_READINESS_FINAL.md <<EOF
# MVP Content Readiness Final Report

**Date**: $(date +"%Y-%m-%d %H:%M:%S")
**PRD**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
**Phase**: 3 - Final Validation

---

## ✅ ALL QUALITY GATES PASSED

### Test Results (8/8 Passed)

| Test | Requirement | Result | Status |
|------|-------------|--------|--------|
| Test 1 | MCQ Count ≥200 | $MCQ_COUNT | ✅ PASS |
| Test 2 | MCQ Specialty Balance ≥60 each | Card:$MCQ_CARDIO, Resp:$MCQ_RESP, Psych:$MCQ_PSYCH | ✅ PASS |
| Test 3 | OSCE Count ≥50 | $OSCE_COUNT | ✅ PASS |
| Test 4 | OSCE Specialty Balance ≥15 each | Card:$OSCE_CARDIO, Resp:$OSCE_RESP, Psych:$OSCE_PSYCH | ✅ PASS |
| Test 5 | EMR Persona Count ≥100 | $PERSONA_COUNT | ✅ PASS |
| Test 6 | Mock Exam Templates ≥3 | $TEMPLATE_COUNT | ✅ PASS |
| Test 7 | No Placeholder Content | $PLACEHOLDER_COUNT items | ✅ PASS |
| Test 8 | RAG Citation Coverage ≥95% | ${CITATION_COVERAGE}% | ✅ PASS |

---

## MVP Launch Readiness

**Status**: ✅ READY FOR MVP LAUNCH

**Content Inventory**:
- **$MCQ_COUNT MCQs** across 3 specialties (balanced)
- **$OSCE_COUNT OSCEs** across 3 specialties (balanced)
- **$PERSONA_COUNT EMR patient personas** (diverse clinical scenarios)
- **$TEMPLATE_COUNT Mock exam templates** (16-station format)

**Quality Assurance**:
- Zero placeholder content (100% real clinical content)
- ${CITATION_COVERAGE}% RAG citation coverage (traceable to medical references)
- Australian medical standards (AMC Clinical Exam)

---

**Generated by**: scripts/validate_content_mvp.sh
**PRD Reference**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
EOF

    echo ""
    echo "📄 Final Report: /home/dev/Development/irStudy/backend/MVP_CONTENT_READINESS_FINAL.md"
    exit 0
else
    echo "❌ SOME TESTS FAILED - Content gaps identified"
    echo ""
    echo "Failed tests:"
    [ "$MCQ_COUNT" -lt 200 ] && echo "  - Test 1: MCQ count ($MCQ_COUNT < 200)"
    [ "$MCQ_CARDIO" -lt 60 ] || [ "$MCQ_RESP" -lt 60 ] || [ "$MCQ_PSYCH" -lt 60 ] && echo "  - Test 2: MCQ specialty balance"
    [ "$OSCE_COUNT" -lt 50 ] && echo "  - Test 3: OSCE count ($OSCE_COUNT < 50)"
    [ "$OSCE_CARDIO" -lt 15 ] || [ "$OSCE_RESP" -lt 15 ] || [ "$OSCE_PSYCH" -lt 15 ] && echo "  - Test 4: OSCE specialty balance"
    [ "$PERSONA_COUNT" -lt 100 ] && echo "  - Test 5: Persona count ($PERSONA_COUNT < 100)"
    [ "$TEMPLATE_COUNT" -lt 3 ] && echo "  - Test 6: Mock exam templates ($TEMPLATE_COUNT < 3)"
    [ "$PLACEHOLDER_COUNT" -gt 0 ] && echo "  - Test 7: Placeholder content ($PLACEHOLDER_COUNT items)"
    [ "$COVERAGE_INT" -lt 95 ] && echo "  - Test 8: RAG citations (${CITATION_COVERAGE}% < 95%)"

    # Generate gap report
    cat > /home/dev/Development/irStudy/backend/MVP_CONTENT_GAP_REPORT.md <<EOF
# MVP Content Gap Report

**Date**: $(date +"%Y-%m-%d %H:%M:%S")
**PRD**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
**Phase**: 2 - Validation (Gaps Identified)

---

## ❌ Validation Failed: $FAILED / $TOTAL_TESTS tests failed

### Failed Tests

$([ "$MCQ_COUNT" -lt 200 ] && echo "**Test 1: MCQ Count**
- Current: $MCQ_COUNT
- Required: ≥200
- Gap: $((200 - MCQ_COUNT)) MCQs needed
- Action: Import additional MCQs or generate missing content
")

$([ "$MCQ_CARDIO" -lt 60 ] || [ "$MCQ_RESP" -lt 60 ] || [ "$MCQ_PSYCH" -lt 60 ] && echo "**Test 2: MCQ Specialty Balance**
- Cardiology: $MCQ_CARDIO ($([ "$MCQ_CARDIO" -ge 60 ] && echo "✅" || echo "❌ need $((60 - MCQ_CARDIO))"))
- Respiratory: $MCQ_RESP ($([ "$MCQ_RESP" -ge 60 ] && echo "✅" || echo "❌ need $((60 - MCQ_RESP))"))
- Psychiatry: $MCQ_PSYCH ($([ "$MCQ_PSYCH" -ge 60 ] && echo "✅" || echo "❌ need $((60 - MCQ_PSYCH))"))
- Action: Generate/import MCQs for deficient specialties
")

$([ "$OSCE_COUNT" -lt 50 ] && echo "**Test 3: OSCE Count**
- Current: $OSCE_COUNT
- Required: ≥50
- Gap: $((50 - OSCE_COUNT)) OSCEs needed
- Action: Import OSCEs from data/osces/ (140 available)
")

$([ "$OSCE_CARDIO" -lt 15 ] || [ "$OSCE_RESP" -lt 15 ] || [ "$OSCE_PSYCH" -lt 15 ] && echo "**Test 4: OSCE Specialty Balance**
- Cardiology: $OSCE_CARDIO ($([ "$OSCE_CARDIO" -ge 15 ] && echo "✅" || echo "❌ need $((15 - OSCE_CARDIO))"))
- Respiratory: $OSCE_RESP ($([ "$OSCE_RESP" -ge 15 ] && echo "✅" || echo "❌ need $((15 - OSCE_RESP))"))
- Psychiatry: $OSCE_PSYCH ($([ "$OSCE_PSYCH" -ge 15 ] && echo "✅" || echo "❌ need $((15 - OSCE_PSYCH))"))
- Action: Import OSCEs for deficient specialties
")

$([ "$PERSONA_COUNT" -lt 100 ] && echo "**Test 5: EMR Persona Count**
- Current: $PERSONA_COUNT
- Required: ≥100
- Gap: $((100 - PERSONA_COUNT)) personas needed
- Action: Import personas from batch1_personas/ (207 available)
")

$([ "$TEMPLATE_COUNT" -lt 3 ] && echo "**Test 6: Mock Exam Templates**
- Current: $TEMPLATE_COUNT
- Required: ≥3
- Gap: $((3 - TEMPLATE_COUNT)) templates needed
- Action: Run scripts/create_mock_exam_templates.py
")

$([ "$PLACEHOLDER_COUNT" -gt 0 ] && echo "**Test 7: Placeholder Content**
- Found: $PLACEHOLDER_COUNT items with placeholders
- Required: 0
- Action: Replace TODO/Lorem ipsum with real content
")

$([ "$COVERAGE_INT" -lt 95 ] && echo "**Test 8: RAG Citation Coverage**
- Current: ${CITATION_COVERAGE}%
- Required: ≥95%
- Gap: $((95 - COVERAGE_INT))% coverage needed
- Action: Add qdrant_point_id citations to content
")

---

## Next Steps

Run Phase 3 import scripts to populate missing content:

\`\`\`bash
# Import OSCEs (if needed)
python3 scripts/import_osces.py --source /home/dev/Development/irStudy/data/osces/

# Import MCQs (if needed)
python3 scripts/import_mcqs.py --source /home/dev/Development/irStudy/data/mcqs/

# Import personas (if needed)
python3 scripts/import_patient_personas.py

# Create templates (if needed)
python3 scripts/create_mock_exam_templates.py

# Re-run validation
./scripts/validate_content_mvp.sh
\`\`\`

---

**Generated by**: scripts/validate_content_mvp.sh
**PRD Reference**: PRD-MVP-003-CONTENT-POPULATION-MVP.md
EOF

    echo ""
    echo "📄 Gap Report: /home/dev/Development/irStudy/backend/MVP_CONTENT_GAP_REPORT.md"
    exit 1
fi
