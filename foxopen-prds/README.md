# FOXopen Ralph PRDs

Ralph-based Product Requirement Documents (PRDs) for automating FOXopen learning projects creation, validation, and deployment.

---

## Overview

This directory contains Ralph PRD files for the FOXopen learning platform. Ralph is an automated implementation framework that executes PRDs using Claude Code in tmux sessions with progress tracking.

---

## PRD Files

### PRD-FOXOPEN-001: Create All 10 Projects
**Status**: Ready for Execution
**Duration**: 45 minutes
**Priority**: P0 (Critical)

**Deliverables**:
- 10 complete project folders
- Valid module XML files for all projects
- Deployment scripts for each project
- Database setup scripts (8 projects)
- Testing scripts for validation
- Master deploy-all.sh and test-all.sh

**Acceptance Criteria**:
- [x] All 10 project folders exist
- [ ] All module.xml files valid (xmllint)
- [ ] All deploy.sh scripts executable
- [ ] 8 database tables created
- [ ] All modules deployed to fox_resources
- [ ] All HTTP endpoints accessible

---

### PRD-FOXOPEN-002: Validate and Test All
**Status**: Ready for Execution
**Duration**: 30 minutes
**Priority**: P1 (High)
**Dependencies**: PRD-FOXOPEN-001

**Deliverables**:
- XML validation script (validate-xml.sh)
- Database validation script (validate-database.sh)
- Deployment validation script (validate-deployment.sh)
- HTTP validation script (validate-http.sh)
- Test report generator (generate-test-report.sh)
- Master test-all.sh script
- Comprehensive test report (Markdown)

**Quality Gates**:
- [ ] 100% XML validation pass rate
- [ ] 100% database tables exist
- [ ] 100% modules deployed
- [ ] 100% HTTP endpoints accessible

---

## Ralph Executor

### Usage

```bash
# Execute all FOXopen PRDs automatically
./ralph-foxopen-executor.sh

# Attach to tmux session to monitor
tmux attach -t ralph-foxopen

# Check status
cat .ralph-foxopen-status.json | jq '.'
```

### Execution Flow

```
1. Initialize status tracking (.ralph-foxopen-status.json)
   ↓
2. Create tmux session (2 panes for 2 PRDs)
   ↓
3. Execute PRD-FOXOPEN-001 (Create all projects)
   ├── Create project folders
   ├── Generate module XML files
   ├── Create deployment scripts
   ├── Create database setup scripts
   └── Create testing scripts
   ↓
4. Execute PRD-FOXOPEN-002 (Validate and test)
   ├── XML validation (xmllint)
   ├── Database validation (Oracle queries)
   ├── Deployment validation (fox_resources check)
   ├── HTTP validation (curl tests)
   └── Generate test report
   ↓
5. Display final status and completion report
```

---

## Status Tracking

Ralph maintains real-time status in `.ralph-foxopen-status.json`:

```json
{
  "start_time": "2026-03-17T03:30:00Z",
  "current_phase": "FOXopen Projects Creation",
  "prds": {
    "PRD-FOXOPEN-001": {
      "name": "Create All 10 Projects",
      "status": "in_progress",
      "start": "2026-03-17T03:30:00Z",
      "end": null,
      "deliverables": {
        "project_folders": 10,
        "module_xml_files": 10,
        "deploy_scripts": 10,
        "database_scripts": 8
      }
    },
    "PRD-FOXOPEN-002": {
      "name": "Validate and Test All",
      "status": "pending",
      ...
    }
  },
  "overall_progress": {
    "total_prds": 2,
    "completed_prds": 0,
    "failed_prds": 0
  }
}
```

---

## Logs

Execution logs are stored in `logs/` directory:

```
logs/
├── executor.log                          # Main executor log
├── PRD-FOXOPEN-001_20260317_033000.log   # PRD-001 execution log
└── PRD-FOXOPEN-002_20260317_034500.log   # PRD-002 execution log
```

---

## Project Structure

```
foxopen-prds/
├── README.md                               # This file
├── PRD-FOXOPEN-001-CREATE-ALL-PROJECTS.md  # PRD for project creation
├── PRD-FOXOPEN-002-VALIDATE-TEST-ALL.md    # PRD for validation
├── ralph-foxopen-executor.sh               # Ralph executor script
├── .ralph-foxopen-status.json              # Runtime status tracking
└── logs/                                    # Execution logs
    ├── executor.log
    ├── PRD-FOXOPEN-001_*.log
    └── PRD-FOXOPEN-002_*.log
```

---

## Integration with irStudy Ralph System

This FOXopen Ralph PRD system follows the same patterns as the irStudy clinical content PRDs:

### Shared Patterns
1. **Tmux Sessions**: Multi-pane tmux for parallel execution
2. **Status Tracking**: JSON files for progress monitoring
3. **Logging**: Timestamped logs for each PRD
4. **Quality Gates**: Automated validation before completion
5. **Phase-based Execution**: Sequential PRD execution with dependencies

### Differences
- **Domain**: FOXopen (learning platform) vs. irStudy (clinical content)
- **Deliverables**: Module XML files vs. Clinical personas
- **Validation**: XML/HTTP validation vs. QA scoring
- **Target**: Oracle/Tomcat deployment vs. Database insertion

---

## Dependencies

### Required Tools
- ✅ Docker (Oracle + Tomcat containers)
- ✅ tmux (session management)
- ✅ jq (JSON processing)
- ✅ xmllint (XML validation)
- ✅ curl (HTTP testing)
- ✅ bash 4.0+ (script execution)

### Required Services
- ✅ Oracle XE database (port 1521)
- ✅ Apache Tomcat (port 8080)
- ✅ FOXopen WAR deployed
- ✅ Database credentials: foxopen/foxopen123

### Check Prerequisites
```bash
# Check Docker containers
docker ps | grep -E "foxopen-(oracle|tomcat)"

# Check database connection
docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SELECT 'Connected' as status FROM dual;
EXIT;
SQL

# Check Tomcat
curl -s http://localhost:8080 | head -1

# Check tools
which tmux jq xmllint curl
```

---

## Execution Examples

### Example 1: Execute All PRDs
```bash
cd /home/dev/Development/irStudy/foxopen-prds
./ralph-foxopen-executor.sh
```

### Example 2: Execute Single PRD
```bash
# Manual execution of PRD-FOXOPEN-001
cd /home/dev/Development/FoxOpen/FOXopen/projects

# Follow steps in PRD-FOXOPEN-001-CREATE-ALL-PROJECTS.md
# Step 1: Create project folders
# Step 2: Generate module XML files
# Step 3: Create deployment scripts
# ...
```

### Example 3: Monitor Execution
```bash
# Attach to tmux session
tmux attach -t ralph-foxopen

# Detach without killing: Ctrl+b, d

# Watch status file
watch -n 5 'cat .ralph-foxopen-status.json | jq ".overall_progress"'

# Tail logs
tail -f logs/executor.log
```

---

## Troubleshooting

### Issue 1: Tmux session not found
```bash
# List active sessions
tmux ls

# Create new session manually
tmux new-session -s ralph-foxopen
```

### Issue 2: Database connection failed
```bash
# Check Oracle container
docker ps | grep foxopen-oracle

# Restart Oracle
docker restart foxopen-oracle
docker logs foxopen-oracle --tail 50
```

### Issue 3: Module deployment failed
```bash
# Check fox_resources table
docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
SELECT name, type, LENGTH(data) FROM fox_resources WHERE type='module';
EXIT;
SQL

# Clear cache
docker exec foxopen-oracle sqlplus -s foxopen/foxopen123@//localhost:1521/XE << SQL
UPDATE fox_resources SET engine_mirror='Y' WHERE type='module';
COMMIT;
EXIT;
SQL

# Restart Tomcat
docker restart foxopen-tomcat
```

---

## Success Metrics

### PRD-FOXOPEN-001
- ✅ **Project Creation**: 10/10 folders created
- ✅ **Module XML**: 10/10 valid files
- ✅ **Scripts**: 10/10 deploy.sh + 8/8 database-setup.sh
- ✅ **Completion Time**: ≤45 minutes

### PRD-FOXOPEN-002
- ✅ **XML Validation**: 100% pass rate
- ✅ **Database Validation**: 100% tables exist
- ✅ **Deployment Validation**: 100% modules deployed
- ✅ **HTTP Validation**: 100% endpoints accessible

### Overall
- ✅ **PRD Completion Rate**: 100% (2/2)
- ✅ **Quality Gates**: 100% passed
- ✅ **Zero Errors**: No failed PRDs
- ✅ **Total Duration**: ≤75 minutes

---

## Next Steps

After completing both PRDs:

1. **Test All Projects**: Visit each URL and verify functionality
2. **Create Additional PRDs**: PRD-FOXOPEN-003 (Deployment Documentation)
3. **Integrate with CI/CD**: Automate testing pipeline
4. **Archive Deliverables**: Backup complete project set
5. **Update Main Documentation**: Link to projects from main README

---

## Related Files

- **FOXopen Learning Book**: `/home/dev/Development/FoxOpen/FOXopen/docs/FOXOPEN_20_PROJECTS_BOOK.md`
- **Project Folders**: `/home/dev/Development/FoxOpen/FOXopen/projects/`
- **Interactive Docs**: `/home/dev/Development/FoxOpen/FOXopen/docs/index.html`
- **Setup Scripts**: `/home/dev/Development/FoxOpen/FOXopen/setup/`
- **Makefile**: `/home/dev/Development/FoxOpen/FOXopen/Makefile`

---

**Created**: 2026-03-17
**Version**: 1.0
**Owner**: FOXopen Learning System + Ralph Automation
**Status**: Ready for Execution
