# Planning Master Index
## Medical Education AI Platform - Complete Planning Structure

**Last Updated:** January 17, 2026
**Project Status:** 35% Complete (Infrastructure & ICRP Content)
**Timeline:** 24 weeks to production launch

---

## 📋 Quick Navigation

### 🎯 Start Here
- [Quick Start Guide](QUICK_START_GUIDE.md) - What to do first
- [Priority Matrix](PRIORITY_MATRIX.md) - P0 to P4 across all work
- [Dependency Map](DEPENDENCY_MAP.md) - What blocks what

### 📅 Phase-by-Phase Plans

#### Current Sprint (ACTIVE)
- **[Phase 1 MVP Implementation (Feb 7-27, 2026)](../phase1-mvp-implementation-feb7-2026/00_README.md)** ⭐ **CURRENT SPRINT**
  - 3 weeks, 14 tasks, Agent OS integrated
  - Backend Foundation + Frontend Core + Integration & Polish
  - Target: Production-ready platform with 1,208 MCQs, 210 OSCEs, 140 Study Cards
  - [Master Plan](../phase1-mvp-implementation-feb7-2026/02_MASTER_PLAN.md) | [Quick Start](../phase1-mvp-implementation-feb7-2026/03_QUICK_START.md) | [Task Checklist](../phase1-mvp-implementation-feb7-2026/04_TASK_CHECKLIST.md)

#### High-Level Roadmap
- [Phase 1: Foundation (Week 1-2)](../01_PHASE_EXECUTION/phase1_foundation.md) - High-level overview (complementary to detailed MVP plan above)
- [Phase 2: Backend Core (Week 3-6)](../01_PHASE_EXECUTION/phase2_backend.md)
- [Phase 3: RAG & Generation (Week 7-10)](../01_PHASE_EXECUTION/phase3_rag_generation.md)
- [Phase 4: Frontend MVP (Week 11-14)](../01_PHASE_EXECUTION/phase4_frontend.md)
- [Phase 5: Agent System (Week 15-18)](../01_PHASE_EXECUTION/phase5_agents.md)
- [Phase 6: Testing & Polish (Week 19-22)](../01_PHASE_EXECUTION/phase6_testing_polish.md)
- [Phase 7: Deployment (Week 23-24)](../01_PHASE_EXECUTION/phase7_deployment.md)

---

## 📚 Content Development Plans

### By Specialty
- [Cardiology Content Plan](../02_CONTENT_PLANS/by_specialty/cardiology_plan.md)
- [Respiratory Content Plan](../02_CONTENT_PLANS/by_specialty/respiratory_plan.md)
- [Gastroenterology Content Plan](../02_CONTENT_PLANS/by_specialty/gastroenterology_plan.md)
- [Endocrinology Content Plan](../02_CONTENT_PLANS/by_specialty/endocrinology_plan.md)
- [Neurology Content Plan](../02_CONTENT_PLANS/by_specialty/neurology_plan.md)
- [Emergency Medicine Content Plan](../02_CONTENT_PLANS/by_specialty/emergency_medicine_plan.md)
- [ObGyn Content Plan](../02_CONTENT_PLANS/by_specialty/obgyn_plan.md)
- [Paediatrics Content Plan](../02_CONTENT_PLANS/by_specialty/paediatrics_plan.md)
- [Psychiatry Content Plan](../02_CONTENT_PLANS/by_specialty/psychiatry_plan.md)
- [General Practice Content Plan](../02_CONTENT_PLANS/by_specialty/general_practice_plan.md)

### By Format
- [MCQ Generation Plan](../02_CONTENT_PLANS/by_format/mcq_generation_plan.md)
- [Clinical Cases Plan](../02_CONTENT_PLANS/by_format/clinical_cases_plan.md)
- [OSCE Stations Plan](../02_CONTENT_PLANS/by_format/osce_stations_plan.md)
- [Differentials Plan](../02_CONTENT_PLANS/by_format/differentials_plan.md)

### By Priority
- [P0: High-Yield Content](../02_CONTENT_PLANS/by_priority/p0_high_yield_content.md)
- [P1: Core Content](../02_CONTENT_PLANS/by_priority/p1_core_content.md)
- [P2: Comprehensive Content](../02_CONTENT_PLANS/by_priority/p2_comprehensive_content.md)

---

## 🏗️ Infrastructure & Technical Plans

### Backend Development
- [API Development Plan](../03_INFRASTRUCTURE_PLANS/backend/api_development_plan.md)
- [Database Models Plan](../03_INFRASTRUCTURE_PLANS/backend/database_models_plan.md)
- [Authentication System Plan](../03_INFRASTRUCTURE_PLANS/backend/authentication_plan.md)
- [Migrations Plan](../03_INFRASTRUCTURE_PLANS/backend/migrations_plan.md)

### Frontend Development
- [Next.js Setup Plan](../03_INFRASTRUCTURE_PLANS/frontend/nextjs_setup_plan.md)
- [Components Plan](../03_INFRASTRUCTURE_PLANS/frontend/components_plan.md)
- [State Management Plan](../03_INFRASTRUCTURE_PLANS/frontend/state_management_plan.md)
- [Routing Plan](../03_INFRASTRUCTURE_PLANS/frontend/routing_plan.md)

### RAG System
- [Vector Database Plan](../03_INFRASTRUCTURE_PLANS/rag_system/vector_database_plan.md)
- [Embedding Pipeline Plan](../03_INFRASTRUCTURE_PLANS/rag_system/embedding_pipeline_plan.md)
- [Query Engine Plan](../03_INFRASTRUCTURE_PLANS/rag_system/query_engine_plan.md)
- [Citation Extraction Plan](../03_INFRASTRUCTURE_PLANS/rag_system/citation_extraction_plan.md)

### LLM Integration
- [Ollama Setup Plan](../03_INFRASTRUCTURE_PLANS/llm_integration/ollama_setup_plan.md)
- [Model Router Plan](../03_INFRASTRUCTURE_PLANS/llm_integration/model_router_plan.md)
- [Prompt Engineering Plan](../03_INFRASTRUCTURE_PLANS/llm_integration/prompt_engineering_plan.md)

### MCP Servers
- [Medical Knowledge Server Plan](../03_INFRASTRUCTURE_PLANS/mcp_servers/medical_knowledge_server_plan.md)
- [PubMed Server Plan](../03_INFRASTRUCTURE_PLANS/mcp_servers/pubmed_server_plan.md)
- [Calculator Server Plan](../03_INFRASTRUCTURE_PLANS/mcp_servers/calculator_server_plan.md)

### DevOps
- [Docker Infrastructure Plan](../03_INFRASTRUCTURE_PLANS/devops/docker_infrastructure_plan.md)
- [Kubernetes Plan](../03_INFRASTRUCTURE_PLANS/devops/kubernetes_plan.md)
- [CI/CD Pipeline Plan](../03_INFRASTRUCTURE_PLANS/devops/cicd_pipeline_plan.md)

---

## 🤖 Agent System Plans

### Coordinator Agents
- [PM-001 Coordinator Plan](../04_AGENT_PLANS/coordinator/pm001_coordinator_plan.md)

### Development Agents
- [DEV-001 Backend Architect](../04_AGENT_PLANS/development/dev001_backend_plan.md)
- [DEV-002 Frontend Architect](../04_AGENT_PLANS/development/dev002_frontend_plan.md)
- [DEV-003 API Developer](../04_AGENT_PLANS/development/dev003_api_plan.md)
- [DEV-004 Database Engineer](../04_AGENT_PLANS/development/dev004_database_plan.md)

### AI/ML Agents
- [AI-001 RAG Architect](../04_AGENT_PLANS/ai_ml/ai001_rag_architect_plan.md)
- [AI-002 LLM Operations](../04_AGENT_PLANS/ai_ml/ai002_llm_ops_plan.md)
- [AI-003 Prompt Engineer](../04_AGENT_PLANS/ai_ml/ai003_prompt_engineer_plan.md)

### Medical Specialist Agents
- [MED-001 Cardiology Expert](../04_AGENT_PLANS/medical_specialists/med001_cardiology_plan.md)
- [MED-002 Respiratory Expert](../04_AGENT_PLANS/medical_specialists/med002_respiratory_plan.md)
- *(+ 8 more specialty agents)*

### QA Agents
- [QA-001 Medical Validator](../04_AGENT_PLANS/qa_agents/qa001_medical_validator_plan.md)
- [QA-002 E2E Testing](../04_AGENT_PLANS/qa_agents/qa002_e2e_testing_plan.md)
- [QA-003 Performance Testing](../04_AGENT_PLANS/qa_agents/qa003_performance_plan.md)

### DevOps Agents
- [DEVOPS-001 Infrastructure](../04_AGENT_PLANS/devops_agents/devops001_infrastructure_plan.md)
- [DEVOPS-002 CI/CD](../04_AGENT_PLANS/devops_agents/devops002_cicd_plan.md)

### Workflows
- [Content Generation Workflow](../04_AGENT_PLANS/workflows/content_generation_workflow.md)
- [QA Validation Workflow](../04_AGENT_PLANS/workflows/qa_validation_workflow.md)
- [Deployment Workflow](../04_AGENT_PLANS/workflows/deployment_workflow.md)

---

## ✅ Quality & Compliance Plans

### Testing
- [Unit Testing Plan](../05_QUALITY_COMPLIANCE_PLANS/testing/unit_testing_plan.md)
- [Integration Testing Plan](../05_QUALITY_COMPLIANCE_PLANS/testing/integration_testing_plan.md)
- [E2E Testing Plan](../05_QUALITY_COMPLIANCE_PLANS/testing/e2e_testing_plan.md)
- [Load Testing Plan](../05_QUALITY_COMPLIANCE_PLANS/testing/load_testing_plan.md)

### Security
- [OWASP Compliance Plan](../05_QUALITY_COMPLIANCE_PLANS/security/owasp_compliance_plan.md)
- [Penetration Testing Plan](../05_QUALITY_COMPLIANCE_PLANS/security/penetration_testing_plan.md)
- [HIPAA Compliance Plan](../05_QUALITY_COMPLIANCE_PLANS/security/hipaa_compliance_plan.md)

### Performance
- [Backend Optimization Plan](../05_QUALITY_COMPLIANCE_PLANS/performance/backend_optimization_plan.md)
- [Frontend Optimization Plan](../05_QUALITY_COMPLIANCE_PLANS/performance/frontend_optimization_plan.md)
- [Database Optimization Plan](../05_QUALITY_COMPLIANCE_PLANS/performance/database_optimization_plan.md)

### Accessibility
- [WCAG Compliance Plan](../05_QUALITY_COMPLIANCE_PLANS/accessibility/wcag_compliance_plan.md)

---

## 🎨 Feature Development Plans

### Core MVP
- [Quiz Interface Plan](../06_FEATURE_PLANS/core_mvp/quiz_interface_plan.md)
- [Study Dashboard Plan](../06_FEATURE_PLANS/core_mvp/study_dashboard_plan.md)
- [Progress Tracking Plan](../06_FEATURE_PLANS/core_mvp/progress_tracking_plan.md)

### Enhanced Features
- [Spaced Repetition Plan](../06_FEATURE_PLANS/enhanced/spaced_repetition_plan.md)
- [Clinical Calculators Plan](../06_FEATURE_PLANS/enhanced/clinical_calculators_plan.md)
- [Anki Integration Plan](../06_FEATURE_PLANS/enhanced/anki_integration_plan.md)

### Future Features
- [Mobile App Plan](../06_FEATURE_PLANS/future/mobile_app_plan.md)
- [Social Features Plan](../06_FEATURE_PLANS/future/social_features_plan.md)
- [Advanced Analytics Plan](../06_FEATURE_PLANS/future/advanced_analytics_plan.md)

---

## 🎫 GitHub Issue Breakdown

- [Issue #3: Mock OSCE Stations](../07_GITHUB_ISSUES/issue_03_mock_osce_stations.md)
- [Issue #4: Differential Diagnosis Guide](../07_GITHUB_ISSUES/issue_04_differential_diagnosis_guide.md)
- [Issue #5: Case Bank Expansion](../07_GITHUB_ISSUES/issue_05_case_bank_expansion.md)
- [Issue #6: Textbook Acquisition](../07_GITHUB_ISSUES/issue_06_textbook_acquisition.md)
- [Issue #7: Study Timeline Tracker](../07_GITHUB_ISSUES/issue_07_study_timeline_tracker.md)
- [Issue #8: LLM & MCP Guide](../07_GITHUB_ISSUES/issue_08_llm_mcp_guide.md)
- [Issue #9: Enhance CLAUDE.md](../07_GITHUB_ISSUES/issue_09_enhance_claude_md.md)
- [Issue #10: Model Routing Config](../07_GITHUB_ISSUES/issue_10_model_routing_config.md)
- [Issue #11: Verify Ollama Setup](../07_GITHUB_ISSUES/issue_11_verify_ollama_setup.md)
- [Issue #12: Medical Knowledge MCP Server](../07_GITHUB_ISSUES/issue_12_medical_knowledge_mcp.md)
- [Issue #13: Smart Model Router](../07_GITHUB_ISSUES/issue_13_smart_model_router.md)
- [Issue #14: Generate Sample MCQs](../07_GITHUB_ISSUES/issue_14_generate_sample_mcqs.md)

---

## 📊 Project Overview

### Current Status (January 2026)
- **Infrastructure:** 30% complete
- **ICRP Content:** 35% complete
- **Backend:** 0% complete
- **Frontend:** 0% complete
- **Agent System:** 10% complete (base classes only)

### Timeline
- **Phase 1:** Weeks 1-2 (80% complete)
- **Phase 2:** Weeks 3-6 (not started)
- **Phase 3:** Weeks 7-10 (not started)
- **Phase 4:** Weeks 11-14 (not started)
- **Phase 5:** Weeks 15-18 (not started)
- **Phase 6:** Weeks 19-22 (not started)
- **Phase 7:** Weeks 23-24 (not started)

### Key Metrics
- **Target Questions:** 5,000+ MCQs
- **Target OSCE Stations:** 50+
- **Target Clinical Cases:** 100+
- **Agents to Implement:** 46
- **Test Coverage Goal:** 80%+
- **Performance Target:** 3,000+ RPS

---

## 🔗 Related Documentation

### Project Documentation
- [PROJECT_ROADMAP.md](../../docs/PROJECT_ROADMAP.md) - Original 24-week timeline
- [AGENT_SPECIFICATIONS.md](../../docs/AGENT_SPECIFICATIONS.md) - Agent system design
- [REQUIRED_BOOKS.md](../../docs/REQUIRED_BOOKS.md) - Medical textbook requirements

### Technical Documentation
- [MCP_SERVERS_INFRASTRUCTURE.md](../../docs/MCP_SERVERS_INFRASTRUCTURE.md)
- [EXPERT_AGENTS_INFRASTRUCTURE.md](../../docs/EXPERT_AGENTS_INFRASTRUCTURE.md)
- [ADDITIONAL_RESOURCES.md](../../docs/ADDITIONAL_RESOURCES.md)

---

## 📝 How to Use This Planning Structure

1. **Start with [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Get oriented
2. **Check [PRIORITY_MATRIX.md](PRIORITY_MATRIX.md)** - Understand what to do first
3. **Review [DEPENDENCY_MAP.md](DEPENDENCY_MAP.md)** - See what blocks what
4. **Pick your current phase** - Go to the relevant phase execution plan
5. **Drill down to specifics** - Navigate to specialty/component-specific plans
6. **Track progress** - Update completion status in each plan file

---

**Last Updated:** January 17, 2026
**Maintained By:** Project Manager (PM-001)
**Review Frequency:** Weekly
