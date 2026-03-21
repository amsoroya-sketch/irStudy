# PRD-FOXOPEN-001: Create All 10 FOXopen Learning Projects with Complete Code

**Created**: 2026-03-17
**Priority**: P0 (Critical)
**Status**: Ready for Execution
**Estimated Duration**: 45 minutes

---

## Executive Summary

Create complete, runnable code for all 10 FOXopen learning projects (Projects 1-10) from the FOXopen 20-Project Learning Book. Each project will include valid module XML, deployment scripts, database setup, testing scripts, and comprehensive documentation.

---

## Current State

**Completed**:
- ✅ FOXopen 20-Project Learning Book (3,907 lines, 137KB)
- ✅ Project 1 (Hello World) - Complete with module.xml, deploy.sh, README.md
- ✅ Project folders created for 2-3
- ✅ Interactive HTML documentation
- ✅ 6 architecture diagrams
- ✅ 9 setup scripts + Makefile (48 targets)

**Remaining**:
- ⏳ Projects 2-10 complete module XML files
- ⏳ Deployment scripts for all projects
- ⏳ Database setup scripts (Projects 2-9)
- ⏳ Testing scripts for validation
- ⏳ Master deploy-all.sh script

**Location**: `/home/dev/Development/FoxOpen/FOXopen/projects/`

---

## Requirements

### FR-001: Project Structure (All 10 Projects)
Each project MUST contain:
- ✅ `module.xml` - Valid FOXopen module (xs:schema wrapper)
- ✅ `deploy.sh` - Deployment script (executable)
- ✅ `database-setup.sh` - Database tables/data (if applicable)
- ✅ `test.sh` - Automated testing script
- ✅ `README.md` - Complete documentation

### FR-002: Module XML Validation
All module.xml files MUST be:
- ✅ Well-formed XML (valid syntax)
- ✅ xs:schema wrapper present
- ✅ Module at path: `/xs:schema/xs:annotation/xs:appinfo/fm:module`
- ✅ All fm:do elements present in entry-themes
- ✅ All states in fm:state-list
- ✅ No placeholder/dummy code

### FR-003: Database Integration
Projects requiring databases (2-9):
- ✅ CREATE TABLE statements with proper structure
- ✅ CREATE SEQUENCE for auto-increment IDs
- ✅ INSERT sample data (realistic test data)
- ✅ GRANT permissions to foxopen user
- ✅ Validation queries to verify setup

### FR-004: Deployment Automation
All deploy.sh scripts MUST:
- ✅ Read module.xml file
- ✅ Insert/update into fox_resources table
- ✅ Set engine_mirror='Y' for cache refresh
- ✅ Restart Tomcat container
- ✅ Display access URL
- ✅ Handle errors gracefully

---

## Implementation Steps

### Step 1: Extract Module XML from Learning Book
```bash
# Read learning book
cat /home/dev/Development/FoxOpen/FOXopen/docs/FOXOPEN_20_PROJECTS_BOOK.md

# For each project (2-10), extract XML between:
# ```xml ... ```
# And create module.xml file
```

### Step 2: Create Project Folders
```bash
cd /home/dev/Development/FoxOpen/FOXopen/projects

# Create remaining project folders
mkdir -p project-{04..10}-{basic-crud,navigation,pagination,validation,dropdowns,file-upload,charts}

# Correct names:
mkdir -p project-04-basic-crud
mkdir -p project-05-navigation
mkdir -p project-06-pagination
mkdir -p project-07-validation
mkdir -p project-08-dropdowns
mkdir -p project-09-file-upload
mkdir -p project-10-charts
```

### Step 3: Create Module XML Files (Projects 2-10)
For each project, create valid module.xml with:
- **Project 2 (SIMPLE_FORM)**: Form inputs, validation, database INSERT
- **Project 3 (DATA_DISPLAY)**: SELECT query, foreach loops, table display
- **Project 4 (EMPLOYEE_CRUD)**: Full CRUD operations, context actions
- **Project 5 (NAVIGATION_DEMO)**: Multi-state navigation, JavaScript tabs
- **Project 6 (PAGINATED_TABLE)**: Server-side pagination, ROW_NUMBER()
- **Project 7 (VALIDATION_DEMO)**: JavaScript validation, password strength
- **Project 8 (SELECT_CONTROLS)**: Dropdowns, radios, checkboxes, cascading
- **Project 9 (FILE_UPLOAD)**: File upload, BLOB storage, downloads
- **Project 10 (SALES_DASHBOARD)**: Chart.js integration, data visualization

### Step 4: Create Database Setup Scripts
```bash
# For each project with database (2-9):
# database-setup.sh contains:
#   - DROP TABLE IF EXISTS (cleanup)
#   - CREATE TABLE statements
#   - CREATE SEQUENCE
#   - INSERT sample data
#   - GRANT permissions
#   - Verification SELECT

# Example structure:
cat > project-02-simple-form/database-setup.sh << 'EOF'
#!/bin/bash
docker exec -i foxopen-oracle sqlplus foxopen/foxopen123@//localhost:1521/XE << SQL
-- Drop existing
DROP TABLE learning_greetings CASCADE CONSTRAINTS;
DROP SEQUENCE learning_greetings_seq;

-- Create table
CREATE TABLE learning_greetings (
  id NUMBER PRIMARY KEY,
  user_name VARCHAR2(100),
  message VARCHAR2(500),
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sequence
CREATE SEQUENCE learning_greetings_seq START WITH 1;

-- Verify
SELECT 'Table created: learning_greetings' as status FROM dual;
EXIT;
SQL
EOF
chmod +x project-02-simple-form/database-setup.sh
```

### Step 5: Create Deployment Scripts
```bash
# Template for deploy.sh (adapt for each project):
cat > project-XX-name/deploy.sh << 'EOF'
#!/bin/bash
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MODULE_XML=$(cat "$SCRIPT_DIR/module.xml")

# Deploy to database
docker exec -i foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
DECLARE
  v_module_xml CLOB;
BEGIN
  v_module_xml := '${MODULE_XML//\'/\'\'}';

  MERGE INTO fox_resources r
  USING (SELECT 'MODULE_NAME' as name, 'module' as type FROM DUAL) s
  ON (r.name = s.name AND r.type = s.type)
  WHEN MATCHED THEN
    UPDATE SET r.data = v_module_xml, r.engine_mirror = 'Y', r.modified_date = SYSTIMESTAMP
  WHEN NOT MATCHED THEN
    INSERT (name, type, data, engine_mirror, created_date, modified_date)
    VALUES (s.name, s.type, v_module_xml, 'Y', SYSTIMESTAMP, SYSTIMESTAMP);
  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Module deployed');
END;
/
EXIT;
SQL

# Restart Tomcat
docker restart foxopen-tomcat
echo "Access: http://localhost:8080/FOX/fox/LEARNING/MODULE_NAME"
EOF
chmod +x project-XX-name/deploy.sh
```

### Step 6: Create Testing Scripts
```bash
# test.sh template:
cat > project-XX-name/test.sh << 'EOF'
#!/bin/bash
echo "Testing MODULE_NAME..."

# Test 1: Module deployed
RESULT=$(docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SET HEADING OFF
SELECT COUNT(*) FROM fox_resources WHERE name='MODULE_NAME';
EXIT;
SQL
)

if [ "$RESULT" -eq 1 ]; then
  echo "✅ Module deployed to database"
else
  echo "❌ Module NOT found in database"
  exit 1
fi

# Test 2: HTTP accessible
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/FOX/fox/LEARNING/MODULE_NAME | grep -q "200"; then
  echo "✅ Module accessible via HTTP"
else
  echo "❌ Module HTTP error"
  exit 1
fi

echo "✅ All tests passed"
EOF
chmod +x project-XX-name/test.sh
```

### Step 7: Create Master Scripts
```bash
cd /home/dev/Development/FoxOpen/FOXopen/projects

# deploy-all.sh
cat > deploy-all.sh << 'EOF'
#!/bin/bash
set -e
for project in project-*/; do
  if [ -f "$project/database-setup.sh" ]; then
    echo "Setting up database for $project..."
    cd "$project" && ./database-setup.sh && cd ..
  fi
  if [ -f "$project/deploy.sh" ]; then
    echo "Deploying $project..."
    cd "$project" && ./deploy.sh && cd ..
  fi
done
echo "All projects deployed!"
EOF
chmod +x deploy-all.sh

# test-all.sh
cat > test-all.sh << 'EOF'
#!/bin/bash
for project in project-*/; do
  if [ -f "$project/test.sh" ]; then
    echo "Testing $project..."
    cd "$project" && ./test.sh && cd ..
  fi
done
EOF
chmod +x test-all.sh
```

---

## Project Details

### Project 2: Simple Form
**Module Name**: SIMPLE_FORM
**Database Tables**: learning_greetings (id, user_name, message, created_date)
**Features**: Text input, textarea, validation, INSERT query
**URL**: http://localhost:8080/FOX/fox/LEARNING/SIMPLE_FORM

### Project 3: Display Oracle Data
**Module Name**: DATA_DISPLAY
**Database Tables**: learning_employees (emp_id, first_name, last_name, email, department, salary, hire_date)
**Features**: SELECT query, foreach loops, XPath functions
**URL**: http://localhost:8080/FOX/fox/LEARNING/DATA_DISPLAY

### Project 4: Basic CRUD
**Module Name**: EMPLOYEE_CRUD
**Database Tables**: learning_employees (same as Project 3)
**Features**: Create, Read, Update, Delete operations, context actions
**URL**: http://localhost:8080/FOX/fox/LEARNING/EMPLOYEE_CRUD

### Project 5: Navigation
**Module Name**: NAVIGATION_DEMO
**Database Tables**: None
**Features**: Multi-state navigation, JavaScript tabs, breadcrumbs
**URL**: http://localhost:8080/FOX/fox/LEARNING/NAVIGATION_DEMO

### Project 6: Pagination
**Module Name**: PAGINATED_TABLE
**Database Tables**: learning_customers (500 records generated)
**Features**: Server-side pagination, ROW_NUMBER(), page navigation
**URL**: http://localhost:8080/FOX/fox/LEARNING/PAGINATED_TABLE

### Project 7: Validation
**Module Name**: VALIDATION_DEMO
**Database Tables**: learning_users
**Features**: Client-side validation, password strength, regex patterns
**URL**: http://localhost:8080/FOX/fox/LEARNING/VALIDATION_DEMO

### Project 8: Dropdowns
**Module Name**: SELECT_CONTROLS
**Database Tables**: learning_categories, learning_products
**Features**: Cascading dropdowns, radio buttons, checkboxes
**URL**: http://localhost:8080/FOX/fox/LEARNING/SELECT_CONTROLS

### Project 9: File Upload
**Module Name**: FILE_UPLOAD
**Database Tables**: learning_documents (BLOB storage)
**Features**: File upload, BLOB storage, download links, validation
**URL**: http://localhost:8080/FOX/fox/LEARNING/FILE_UPLOAD

### Project 10: Charts
**Module Name**: SALES_DASHBOARD
**Database Tables**: learning_sales (365 records generated)
**Features**: Chart.js integration, line/bar/pie charts, data visualization
**URL**: http://localhost:8080/FOX/fox/LEARNING/SALES_DASHBOARD

---

## Acceptance Criteria

### AC-001: All Project Folders Exist
```bash
ls -1d project-*/
# Expected: 10 directories (project-01 through project-10)
```

### AC-002: All Module XML Files Valid
```bash
for module in project-*/module.xml; do
  xmllint --noout "$module" 2>&1 || echo "ERROR: $module"
done
# Expected: No errors
```

### AC-003: All Deployment Scripts Executable
```bash
ls -l project-*/deploy.sh | awk '{print $1}' | grep -c 'x'
# Expected: 10 (all executable)
```

### AC-004: Database Tables Created
```bash
docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SELECT table_name FROM user_tables WHERE table_name LIKE 'LEARNING_%' ORDER BY table_name;
EXIT;
SQL
# Expected: 8 tables (greetings, employees, customers, users, categories, products, documents, sales)
```

### AC-005: All Modules Deployed
```bash
docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SELECT name FROM fox_resources WHERE type='module' AND name IN (
  'HELLO_WORLD','SIMPLE_FORM','DATA_DISPLAY','EMPLOYEE_CRUD','NAVIGATION_DEMO',
  'PAGINATED_TABLE','VALIDATION_DEMO','SELECT_CONTROLS','FILE_UPLOAD','SALES_DASHBOARD'
) ORDER BY name;
EXIT;
SQL
# Expected: 10 modules
```

### AC-006: All Modules Accessible
```bash
for project in HELLO_WORLD SIMPLE_FORM DATA_DISPLAY EMPLOYEE_CRUD NAVIGATION_DEMO PAGINATED_TABLE VALIDATION_DEMO SELECT_CONTROLS FILE_UPLOAD SALES_DASHBOARD; do
  curl -s -o /dev/null -w "%{http_code} $project\n" "http://localhost:8080/FOX/fox/LEARNING/$project"
done
# Expected: All 200 responses
```

---

## Risk Mitigation

### Risk 1: XML Parsing Errors
**Probability**: Medium
**Impact**: High (module won't deploy)
**Mitigation**: Validate all XML with xmllint before deployment

### Risk 2: Database Connection Issues
**Probability**: Low
**Impact**: Medium
**Mitigation**: Verify Docker containers running before deployment

### Risk 3: Tomcat Restart Timeout
**Probability**: Low
**Impact**: Low
**Mitigation**: Wait 15 seconds after restart, check logs if issues

---

## Dependencies

- ✅ FOXopen Docker containers running
- ✅ Oracle database accessible (XE)
- ✅ Tomcat on port 8080
- ✅ Database credentials: foxopen/foxopen123
- ✅ FOXopen 20-Project Learning Book (source material)

---

## Deliverables

### D-001: Complete Project Folders (10)
**Location**: `/home/dev/Development/FoxOpen/FOXopen/projects/`
**Structure**:
```
project-01-hello-world/
├── module.xml
├── deploy.sh
├── test.sh
└── README.md

project-02-simple-form/
├── module.xml
├── database-setup.sh
├── deploy.sh
├── test.sh
└── README.md

... (8 more projects)
```

### D-002: Master Scripts
- `deploy-all.sh` - Deploy all projects sequentially
- `test-all.sh` - Test all deployed modules
- `README.md` - Project index and instructions

### D-003: Database Tables (8)
- learning_greetings
- learning_employees
- learning_customers
- learning_users
- learning_categories
- learning_products
- learning_documents
- learning_sales

---

## Timeline

**Total Estimated Duration**: 45 minutes

| Task | Duration | Dependencies |
|------|----------|--------------|
| Extract module XML from learning book | 10 min | Learning book |
| Create project folders & structure | 5 min | None |
| Create database setup scripts | 10 min | Table definitions |
| Create deployment scripts | 10 min | Module XML |
| Create testing scripts | 5 min | Deployment scripts |
| Validate all files | 5 min | All files created |

---

## Success Metrics

- ✅ **Completion Rate**: 100% (10/10 projects)
- ✅ **XML Validation**: 100% (all valid)
- ✅ **Deployment Success**: 100% (all modules deployed)
- ✅ **HTTP Accessibility**: 100% (all return 200)
- ✅ **Database Tables**: 8/8 created successfully

---

## Post-Completion Actions

1. **Test All Projects**: Run ./test-all.sh
2. **Create Usage Guide**: Document deployment workflow
3. **Archive Project Scaffolds**: Backup complete project set
4. **Update Main README**: Add projects section

---

**Status**: ✅ READY FOR EXECUTION
**Next PRD**: PRD-FOXOPEN-002 (Validate and Test All Projects)
**Owner**: FOXopen Learning System
**Approver**: Development Team
