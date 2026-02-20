# EMR Practice System - PRD Refinement Fix Plan

## Phase 1: Update Existing PRD Files (HIGH PRIORITY)

### 1.1 Master PRD Update
- [x] Read `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md`
- [x] Replace ALL "ICRP" references with "AMC Clinical Examination"
- [x] Replace "Intern Clinical Readiness Program" with "Australian Medical Council Clinical Examination preparation"
- [x] Add "Australian Clinical Standards Compliance" section (AHPRA, NSW Health EMR, Australian SOAP format)
- [x] Update success metrics to world-class standards (95%+ AHPRA, 90%+ engagement, 90%+ AI accuracy)
- [x] Add "OSCE Station Integration" section with technical requirements
- [x] Write updated file back to same location

### 1.2 Cerner PowerChart UI PRD Update
- [ ] Read `/home/dev/Development/irStudy/emr-practice-system/prd/01_CERNER_POWERCHART_UI_PRD.md`
- [ ] Replace ALL "ICRP" references with "AMC Clinical Examination"
- [ ] Add "Australian Medical Terminology" validation section (paracetamol/adrenaline/anaesthesia)
- [ ] Add "Australian Hospital Context" examples (Aboriginal/Torres Strait Islander status, Medicare numbers)
- [ ] Add "OSCE Integration UI" section (EMR + OSCE timer, instructions banner)
- [ ] Update component specifications with Australian SOAP note format
- [ ] Write updated file back to same location

### 1.3 Epic EHR UI PRD Update
- [x] Read `/home/dev/Development/irStudy/emr-practice-system/prd/02_EPIC_EHR_UI_PRD.md`
- [x] Replace ALL "ICRP" references with "AMC Clinical Examination"
- [x] Add "Australian Medical Terminology" validation section
- [x] Add "Australian Hospital Context" examples
- [x] Add "OSCE Integration UI" section
- [x] Update component specifications with Australian SOAP note format
- [x] Write updated file back to same location

### 1.4 Backend API PRD Update
- [ ] Read `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md`
- [ ] Replace ALL "ICRP" references with "AMC Clinical Examination"
- [ ] Add "PBS Integration" section (Pharmaceutical Benefits Scheme - 4,000+ medications)
- [ ] Add "MBS Integration" section (Medicare Benefits Schedule - pathology tests)
- [ ] Add "Australian Drug Database" requirements
- [ ] Add "OSCE Integration API Endpoints" section (start session, submit documentation, score)
- [ ] Update validation rules for Australian clinical guidelines
- [ ] Add database schema for `osce_emr_integration` table
- [ ] Write updated file back to same location

### 1.5 Testing Strategy PRD Update
- [ ] Read `/home/dev/Development/irStudy/emr-practice-system/prd/04_TESTING_STRATEGY_PRD.md`
- [ ] Replace ALL "ICRP" references with "AMC Clinical Examination"
- [ ] Add "Australian-Specific Test Cases" section (AHPRA compliance, terminology validation)
- [ ] Add "OSCE Integration Tests" section (50+ E2E tests for EMR + OSCE workflows)
- [ ] Update test coverage requirements to 80%+ for world-class quality
- [ ] Add "Australian Clinical Guidelines Validation Tests" section
- [ ] Write updated file back to same location

## Phase 2: Create New PRD Files (HIGH PRIORITY)

### 2.1 OSCE Integration PRD
- [ ] Create `/home/dev/Development/irStudy/emr-practice-system/prd/05_OSCE_INTEGRATION_PRD.md`
- [ ] Add table of contents
- [ ] Write "User Stories" section (student taking OSCE with EMR requirement)
- [ ] Write "Technical Architecture" section (how EMR connects to existing OSCE system)
- [ ] Write "Database Schema" section (osce_emr_integration table SQL)
- [ ] Write "API Endpoints" section (start session, submit documentation, score calculation)
- [ ] Write "Frontend Components" section (OSCEStationWithEMR.tsx with code examples)
- [ ] Write "Scoring Algorithm" section (combine OSCE + EMR scores with weights)
- [ ] Write "Test Cases" section (50+ integration tests)
- [ ] Write "Success Criteria" section (metrics and KPIs)

### 2.2 AI Validation PRD
- [ ] Create `/home/dev/Development/irStudy/emr-practice-system/prd/06_AI_VALIDATION_PRD.md`
- [ ] Add table of contents
- [ ] Write "Claude API Integration" section (Anthropic API setup, prompt engineering)
- [ ] Write "SOAP Note Validation" section (structure, clinical accuracy, Australian terminology, AHPRA)
- [ ] Write "Prescription Validation" section (PBS compliance, dose checking, drug interactions)
- [ ] Write "Pathology Validation" section (MBS compliance, indication appropriateness)
- [ ] Write "RAG Integration" section (query Qdrant for Australian clinical guidelines)
- [ ] Write "Validation Response Format" section (JSON schema with scores and feedback)
- [ ] Write "Performance Requirements" section (<3s per validation, 90%+ accuracy)
- [ ] Write "Test Cases" section (30+ validation accuracy tests vs. human educators)

## Phase 3: Create Implementation Documentation (MEDIUM PRIORITY)

### 3.1 Implementation Checklist
- [ ] Create `/home/dev/Development/irStudy/emr-practice-system/prd/IMPLEMENTATION_CHECKLIST.md`
- [ ] Add Week 1 checklist (Database schema - 10 tasks)
- [ ] Add Week 2 checklist (API foundation - 8 tasks)
- [ ] Add Week 3-5 checklist (Cerner UI - 25 tasks)
- [ ] Add Week 6-8 checklist (Epic UI - 25 tasks)
- [ ] Add Week 9-10 checklist (AI validation - 12 tasks)
- [ ] Add Week 11 checklist (OSCE integration - 10 tasks)
- [ ] Add Week 12 checklist (Testing & documentation - 15 tasks)
- [ ] Total: 200+ actionable tasks

### 3.2 Test Data Specifications
- [ ] Create `/home/dev/Development/irStudy/emr-practice-system/prd/TEST_DATA_SPECIFICATIONS.md`
- [ ] Write "Patient Scenarios" section (200+ scenarios: 10 specialties × 20 each, complexity levels, Australian demographics)
- [ ] Write "PBS Medication Database" section (4,000+ medications with doses, interactions, authority requirements)
- [ ] Write "MBS Pathology Tests" section (common panels: FBC, UEC, LFT, TFT + individual tests)
- [ ] Write "Australian Guidelines URLs" section (links for each specialty)
- [ ] Write "Sample Data Generation Scripts" section (Python scripts to generate test data)

### 3.3 Architecture Documentation
- [ ] Create `/home/dev/Development/irStudy/emr-practice-system/prd/ARCHITECTURE.md`
- [ ] Write "System Architecture Diagram" section (ASCII art: frontend, backend, database, AI validation)
- [ ] Write "Data Flow Diagrams" section (user action → API → database → AI → response)
- [ ] Write "Security Architecture" section (authentication, PHI encryption, HIPAA audit logs)
- [ ] Write "Integration Points" section (OSCE system, PBS, MBS, Australian guidelines, Qdrant RAG)
- [ ] Write "Technology Stack" section (React, FastAPI, PostgreSQL, Redis, Claude API)

### 3.4 API Specification
- [ ] Create `/home/dev/Development/irStudy/emr-practice-system/prd/API_SPECIFICATION.md`
- [ ] Write "Authentication Endpoints" section (login, register, refresh token)
- [ ] Write "EMR Session Endpoints" section (start, get, update, complete)
- [ ] Write "SOAP Note Endpoints" section (create, update, validate, list)
- [ ] Write "Prescription Endpoints" section (create, update, validate, list)
- [ ] Write "Pathology Endpoints" section (create, update, validate, list)
- [ ] Write "Patient Scenario Endpoints" section (list, get, search)
- [ ] Write "OSCE Integration Endpoints" section (start session, submit documentation, get score)
- [ ] Write "Validation Endpoints" section (validate SOAP, validate prescription, validate pathology)
- [ ] Add request/response examples for each endpoint (JSON)
- [ ] Add error response examples (400, 401, 403, 404, 500)

### 3.5 Deployment Guide
- [ ] Create `/home/dev/Development/irStudy/emr-practice-system/prd/DEPLOYMENT_GUIDE.md`
- [ ] Write "Infrastructure Requirements" section (AWS/Azure Australian region, PostgreSQL, Redis)
- [ ] Write "Database Setup" section (PostgreSQL 16 with encryption at rest, Alembic migrations)
- [ ] Write "Environment Variables" section (DATABASE_URL, REDIS_URL, CLAUDE_API_KEY, etc.)
- [ ] Write "Frontend Deployment" section (Vite build, static file hosting)
- [ ] Write "Backend Deployment" section (FastAPI with uvicorn, process manager)
- [ ] Write "Monitoring Setup" section (Prometheus metrics, Grafana dashboards, alerting rules)
- [ ] Write "Backup and Disaster Recovery" section (automated backups, restore procedures)
- [ ] Write "Production Checklist" section (pre-launch verification steps)

## Phase 4: Quality Assurance (LOW PRIORITY)

### 4.1 Cross-Reference Check
- [ ] Verify all PRD files reference AMC Clinical Examination (zero ICRP mentions)
- [ ] Verify all PRD files include Australian-specific requirements (AHPRA, PBS, MBS)
- [ ] Verify cross-references between PRD files are accurate
- [ ] Verify code examples are production-ready (TypeScript, Python, SQL)
- [ ] Verify consistency of terminology across all PRD files

### 4.2 Final Review
- [ ] Spell check all PRD files
- [ ] Format check (proper markdown, headers, code blocks)
- [ ] Link check (all URLs valid, all file paths correct)
- [ ] Generate table of contents for each PRD file
- [ ] Add version numbers and last updated dates

## Completed Tasks

- [x] Created Ralph project structure
- [x] Set up PROMPT.md with project context

## Notes

**CRITICAL REQUIREMENTS:**
- Replace ALL "ICRP" with "AMC Clinical Examination" (per project constraints)
- Add Australian-specific sections to EVERY PRD file
- Include code examples in all technical PRDs (database schema, API endpoints, React components)
- Cross-reference implementation plan: `/home/dev/Development/irStudy/emr-practice-system/implementation-plan-15-feb/WORLD_CLASS_EMR_IMPLEMENTATION_PLAN.md`
- Target: World-class quality, production-ready specifications

**Work Priority:**
1. Phase 1 (update existing PRDs) - HIGHEST PRIORITY
2. Phase 2 (create new PRDs) - HIGH PRIORITY
3. Phase 3 (implementation docs) - MEDIUM PRIORITY
4. Phase 4 (QA) - LOW PRIORITY

**Execution Strategy:**
- Work systematically through each PRD file
- Preserve existing valuable content - only add/update, don't delete
- Include detailed code examples for all technical specifications
- Ensure cross-references are accurate and helpful
