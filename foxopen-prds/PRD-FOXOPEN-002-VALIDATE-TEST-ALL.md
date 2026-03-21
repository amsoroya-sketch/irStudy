# PRD-FOXOPEN-002: Validate and Test All FOXopen Projects

**Created**: 2026-03-17
**Priority**: P1 (High)
**Status**: Ready for Execution
**Estimated Duration**: 30 minutes
**Dependencies**: PRD-FOXOPEN-001 (Complete)

---

## Executive Summary

Comprehensive validation and testing of all 10 FOXopen learning projects. Verify module XML syntax, database connectivity, deployment success, and HTTP accessibility. Generate test reports and quality metrics.

---

## Current State

**Assumed Completed** (from PRD-FOXOPEN-001):
- ✅ 10 project folders created
- ✅ All module.xml files generated
- ✅ Deployment scripts created
- ✅ Database setup scripts created
- ✅ Test scripts created

**To Be Validated**:
- ⏳ XML syntax correctness
- ⏳ Database tables exist
- ⏳ Modules deployed to fox_resources
- ⏳ HTTP endpoints accessible
- ⏳ No runtime errors

**Location**: `/home/dev/Development/FoxOpen/FOXopen/projects/`

---

## Requirements

### FR-001: XML Validation
All module.xml files MUST pass:
- ✅ xmllint --noout validation (well-formed XML)
- ✅ xs:schema wrapper verification
- ✅ fm:module element at correct XPath
- ✅ No missing required elements
- ✅ No syntax errors

### FR-002: Database Validation
All database tables MUST:
- ✅ Exist in Oracle database
- ✅ Have correct structure (columns, types)
- ✅ Contain sample data
- ✅ Have sequences created (where applicable)
- ✅ Grant permissions to foxopen user

### FR-003: Deployment Validation
All modules MUST:
- ✅ Deploy to fox_resources table
- ✅ Have engine_mirror='Y' set
- ✅ Have data column populated (not NULL)
- ✅ Have created_date and modified_date set

### FR-004: HTTP Validation
All module URLs MUST:
- ✅ Return HTTP 200 status code
- ✅ Render without Tomcat errors
- ✅ Display expected content
- ✅ Load within 3 seconds

---

## Implementation Steps

### Step 1: XML Validation Suite
```bash
#!/bin/bash
# validate-xml.sh

echo "==================================================================="
echo "  FOXopen Module XML Validation"
echo "==================================================================="
echo ""

TOTAL=0
PASSED=0
FAILED=0

for project in project-*/; do
  MODULE_FILE="$project/module.xml"

  if [ -f "$MODULE_FILE" ]; then
    TOTAL=$((TOTAL + 1))
    echo -n "Validating $MODULE_FILE... "

    # Test 1: Well-formed XML
    if xmllint --noout "$MODULE_FILE" 2>/dev/null; then
      # Test 2: xs:schema wrapper exists
      if grep -q '<xs:schema' "$MODULE_FILE"; then
        # Test 3: fm:module element exists
        if grep -q '<fm:module>' "$MODULE_FILE"; then
          echo "✅ PASS"
          PASSED=$((PASSED + 1))
        else
          echo "❌ FAIL: Missing fm:module element"
          FAILED=$((FAILED + 1))
        fi
      else
        echo "❌ FAIL: Missing xs:schema wrapper"
        FAILED=$((FAILED + 1))
      fi
    else
      echo "❌ FAIL: Invalid XML syntax"
      FAILED=$((FAILED + 1))
    fi
  fi
done

echo ""
echo "Results: $PASSED passed, $FAILED failed (Total: $TOTAL)"
echo ""
```

### Step 2: Database Validation
```bash
#!/bin/bash
# validate-database.sh

echo "==================================================================="
echo "  Database Tables Validation"
echo "==================================================================="
echo ""

# Expected tables
EXPECTED_TABLES=(
  "LEARNING_GREETINGS"
  "LEARNING_EMPLOYEES"
  "LEARNING_CUSTOMERS"
  "LEARNING_USERS"
  "LEARNING_CATEGORIES"
  "LEARNING_PRODUCTS"
  "LEARNING_DOCUMENTS"
  "LEARNING_SALES"
)

# Query Oracle for existing tables
EXISTING=$(docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SET HEADING OFF
SET FEEDBACK OFF
SELECT table_name FROM user_tables WHERE table_name LIKE 'LEARNING_%' ORDER BY table_name;
EXIT;
SQL
)

# Check each expected table
TOTAL=${#EXPECTED_TABLES[@]}
FOUND=0

for table in "${EXPECTED_TABLES[@]}"; do
  if echo "$EXISTING" | grep -q "$table"; then
    echo "✅ $table - EXISTS"
    FOUND=$((FOUND + 1))
  else
    echo "❌ $table - MISSING"
  fi
done

echo ""
echo "Results: $FOUND/$TOTAL tables found"
echo ""

# Verify sample data exists
echo "Checking sample data..."
docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SET HEADING OFF
SELECT 'learning_greetings: ' || COUNT(*) || ' records' FROM learning_greetings;
SELECT 'learning_employees: ' || COUNT(*) || ' records' FROM learning_employees;
SELECT 'learning_customers: ' || COUNT(*) || ' records' FROM learning_customers;
EXIT;
SQL
```

### Step 3: Deployment Validation
```bash
#!/bin/bash
# validate-deployment.sh

echo "==================================================================="
echo "  Module Deployment Validation"
echo "==================================================================="
echo ""

# Expected modules
MODULES=(
  "HELLO_WORLD"
  "SIMPLE_FORM"
  "DATA_DISPLAY"
  "EMPLOYEE_CRUD"
  "NAVIGATION_DEMO"
  "PAGINATED_TABLE"
  "VALIDATION_DEMO"
  "SELECT_CONTROLS"
  "FILE_UPLOAD"
  "SALES_DASHBOARD"
)

TOTAL=${#MODULES[@]}
DEPLOYED=0

for module in "${MODULES[@]}"; do
  echo -n "Checking $module... "

  RESULT=$(docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SET HEADING OFF
SET FEEDBACK OFF
SELECT COUNT(*) FROM fox_resources WHERE name='$module' AND type='module';
EXIT;
SQL
  )

  if [ "$RESULT" -eq 1 ]; then
    echo "✅ DEPLOYED"
    DEPLOYED=$((DEPLOYED + 1))
  else
    echo "❌ NOT DEPLOYED"
  fi
done

echo ""
echo "Results: $DEPLOYED/$TOTAL modules deployed"
echo ""
```

### Step 4: HTTP Validation
```bash
#!/bin/bash
# validate-http.sh

echo "==================================================================="
echo "  HTTP Endpoint Validation"
echo "==================================================================="
echo ""

# Wait for Tomcat to be ready
echo "Checking Tomcat status..."
until curl -s http://localhost:8080 > /dev/null; do
  echo "Waiting for Tomcat..."
  sleep 2
done
echo "✅ Tomcat is responding"
echo ""

# Test each module URL
MODULES=(
  "HELLO_WORLD"
  "SIMPLE_FORM"
  "DATA_DISPLAY"
  "EMPLOYEE_CRUD"
  "NAVIGATION_DEMO"
  "PAGINATED_TABLE"
  "VALIDATION_DEMO"
  "SELECT_CONTROLS"
  "FILE_UPLOAD"
  "SALES_DASHBOARD"
)

TOTAL=${#MODULES[@]}
ACCESSIBLE=0

for module in "${MODULES[@]}"; do
  echo -n "Testing $module... "
  URL="http://localhost:8080/FOX/fox/LEARNING/$module"

  # Get HTTP status code
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")

  if [ "$STATUS" -eq 200 ]; then
    echo "✅ HTTP $STATUS"
    ACCESSIBLE=$((ACCESSIBLE + 1))
  else
    echo "❌ HTTP $STATUS (Expected 200)"
  fi
done

echo ""
echo "Results: $ACCESSIBLE/$TOTAL endpoints accessible"
echo ""
```

### Step 5: Comprehensive Test Report
```bash
#!/bin/bash
# generate-test-report.sh

REPORT_FILE="test-report-$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << 'EOF'
# FOXopen Projects Test Report

**Generated**: $(date)
**Location**: /home/dev/Development/FoxOpen/FOXopen/projects/

---

## Test Summary

| Category | Passed | Failed | Total |
|----------|--------|--------|-------|
| XML Validation | X/10 | X/10 | 10 |
| Database Tables | X/8 | X/8 | 8 |
| Module Deployment | X/10 | X/10 | 10 |
| HTTP Endpoints | X/10 | X/10 | 10 |

**Overall Success Rate**: XX%

---

## Detailed Results

### XML Validation
- [ ] project-01-hello-world/module.xml
- [ ] project-02-simple-form/module.xml
... (all 10)

### Database Tables
- [ ] learning_greetings (X records)
- [ ] learning_employees (X records)
... (all 8)

### Module Deployment
- [ ] HELLO_WORLD
- [ ] SIMPLE_FORM
... (all 10)

### HTTP Endpoints
- [ ] http://localhost:8080/FOX/fox/LEARNING/HELLO_WORLD (HTTP XXX)
... (all 10)

---

## Issues Found

(List any failures or errors)

---

## Recommendations

(Next steps or fixes needed)
EOF

echo "Test report generated: $REPORT_FILE"
```

### Step 6: Automated Full Test Suite
```bash
#!/bin/bash
# test-all.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "==================================================================="
echo "  FOXopen Projects - Complete Test Suite"
echo "==================================================================="
echo ""

# Run all validation scripts
"$SCRIPT_DIR/validate-xml.sh"
"$SCRIPT_DIR/validate-database.sh"
"$SCRIPT_DIR/validate-deployment.sh"
"$SCRIPT_DIR/validate-http.sh"

# Generate report
"$SCRIPT_DIR/generate-test-report.sh"

echo ""
echo "==================================================================="
echo "  All tests complete! Check test-report-*.md for details"
echo "==================================================================="
```

---

## Acceptance Criteria

### AC-001: All XML Files Valid
```bash
./validate-xml.sh
# Expected: 10/10 passed
```

### AC-002: All Database Tables Exist
```bash
./validate-database.sh
# Expected: 8/8 tables found
```

### AC-003: All Modules Deployed
```bash
./validate-deployment.sh
# Expected: 10/10 modules deployed
```

### AC-004: All HTTP Endpoints Accessible
```bash
./validate-http.sh
# Expected: 10/10 endpoints return HTTP 200
```

### AC-005: Test Report Generated
```bash
ls -1 test-report-*.md
# Expected: 1 file with current timestamp
```

---

## Quality Gates

All quality gates MUST pass before marking PRD complete:

- [ ] **Zero XML syntax errors** (xmllint validation)
- [ ] **100% database tables created** (8/8)
- [ ] **100% modules deployed** (10/10)
- [ ] **100% HTTP endpoints accessible** (10/10)
- [ ] **All sample data loaded** (verify counts)
- [ ] **No Tomcat errors in logs**

---

## Risk Mitigation

### Risk 1: Tomcat Container Not Running
**Probability**: Low
**Impact**: High
**Mitigation**: Check Docker containers first, restart if needed

### Risk 2: Database Connection Timeout
**Probability**: Low
**Impact**: Medium
**Mitigation**: Verify Oracle container healthy, check connection pool

### Risk 3: Module Cache Not Cleared
**Probability**: Medium
**Impact**: Low
**Mitigation**: Set engine_mirror='Y' and restart Tomcat

---

## Dependencies

- ✅ PRD-FOXOPEN-001 completed (all projects created)
- ✅ Docker containers running
- ✅ xmllint installed (for XML validation)
- ✅ curl installed (for HTTP testing)
- ✅ jq installed (for JSON parsing)

---

## Deliverables

### D-001: Validation Scripts (5)
- `validate-xml.sh` - XML syntax validation
- `validate-database.sh` - Database table verification
- `validate-deployment.sh` - Module deployment check
- `validate-http.sh` - HTTP endpoint testing
- `generate-test-report.sh` - Comprehensive report generation

### D-002: Master Test Script
- `test-all.sh` - Runs all validation scripts in sequence

### D-003: Test Report
- `test-report-YYYYMMDD_HHMMSS.md` - Markdown test report with results

---

## Timeline

**Total Estimated Duration**: 30 minutes

| Task | Duration | Dependencies |
|------|----------|--------------|
| Create validation scripts | 10 min | None |
| Run XML validation | 2 min | xmllint |
| Run database validation | 5 min | Oracle running |
| Run deployment validation | 3 min | Modules deployed |
| Run HTTP validation | 5 min | Tomcat running |
| Generate test report | 5 min | All validations complete |

---

## Success Metrics

- ✅ **XML Validation**: 100% (10/10 valid)
- ✅ **Database Tables**: 100% (8/8 exist)
- ✅ **Module Deployment**: 100% (10/10 deployed)
- ✅ **HTTP Accessibility**: 100% (10/10 return 200)
- ✅ **Overall Success Rate**: 100%

---

## Post-Completion Actions

1. **Archive Test Report**: Save to docs/test-reports/
2. **Fix Any Issues**: Address failures found in testing
3. **Update Documentation**: Add test results to README
4. **Create CI/CD Pipeline**: Automate testing for future changes

---

**Status**: ✅ READY FOR EXECUTION
**Next PRD**: PRD-FOXOPEN-003 (Generate Deployment Documentation)
**Owner**: FOXopen Quality Assurance
**Approver**: Development Team
