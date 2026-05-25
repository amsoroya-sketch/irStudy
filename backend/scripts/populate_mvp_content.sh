#!/bin/bash
# MVP Content Population Orchestration Script
# Phase 3: Execute all import scripts and create templates
#
# PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
# Purpose: Orchestrate Tests 9-12 (import operations)

set -e

echo "========================================="
echo "MVP Content Population (Phase 3)"
echo "========================================="
echo "Date: $(date +%Y-%m-%d\ %H:%M:%S)"
echo "PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md"
echo ""

cd /home/dev/Development/irStudy/backend

# Activate venv
source venv/bin/activate

TOTAL_OPERATIONS=4
COMPLETED=0
FAILED=0

echo "Phase 3: Importing content to database..."
echo ""

# Test 9: Import MCQs
echo "========================================="
echo "Test 9: MCQ Import"
echo "========================================="

if python3 scripts/import_mcqs.py --source /home/dev/Development/irStudy/data/mcqs/; then
    echo "✅ Test 9 PASSED: MCQs imported successfully"
    ((COMPLETED++))
else
    echo "❌ Test 9 FAILED: MCQ import failed"
    ((FAILED++))
fi
echo ""

# Test 10: Import OSCEs
echo "========================================="
echo "Test 10: OSCE Import"
echo "========================================="

if python3 scripts/import_osces.py --source /home/dev/Development/irStudy/data/osces/; then
    echo "✅ Test 10 PASSED: OSCEs imported successfully"
    ((COMPLETED++))
else
    echo "❌ Test 10 FAILED: OSCE import failed"
    ((FAILED++))
fi
echo ""

# Test 11: Import EMR Personas
echo "========================================="
echo "Test 11: EMR Persona Import"
echo "========================================="

if python3 scripts/import_patient_personas.py; then
    echo "✅ Test 11 PASSED: EMR personas imported successfully"
    ((COMPLETED++))
else
    echo "❌ Test 11 FAILED: EMR persona import failed"
    ((FAILED++))
fi
echo ""

# Test 12: Create Mock Exam Templates
echo "========================================="
echo "Test 12: Mock Exam Template Creation"
echo "========================================="

if python3 scripts/create_mock_exam_templates.py; then
    echo "✅ Test 12 PASSED: Mock exam templates created successfully"
    ((COMPLETED++))
else
    echo "❌ Test 12 FAILED: Template creation failed"
    ((FAILED++))
fi
echo ""

# Summary
echo "========================================="
echo "Phase 3 Summary"
echo "========================================="
echo ""
echo "Operations Completed: $COMPLETED / $TOTAL_OPERATIONS"
echo "Operations Failed: $FAILED / $TOTAL_OPERATIONS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL IMPORT OPERATIONS COMPLETE"
    echo ""
    echo "Next Step: Run validation to verify content"
    echo "  ./scripts/validate_content_mvp.sh"
    exit 0
else
    echo "❌ SOME OPERATIONS FAILED"
    echo ""
    echo "Review errors above and retry failed operations"
    exit 1
fi
