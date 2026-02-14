# AMC Clinical Exam Simulation - Architecture Documentation

**Version:** 1.0
**Created:** 2026-02-06
**Purpose:** Comprehensive architecture documentation with Python-generated diagrams

---

## 🎯 Quick Start

This folder contains detailed architecture documentation for the **AMC Clinical Examination Simulator** - an AI-powered clinical exam preparation system with conversational AI patients, real-time examiner scoring, and WebSocket-based interface.

### What's Inside

- **12 Architecture Diagrams** (PNG) - Generated using Python `diagrams` library
- **8 Comprehensive Markdown Documents** - Detailed technical specifications
- **Diagram Generation Script** - Python script to regenerate all diagrams

---

## 📊 Architecture Diagrams

All diagrams are auto-generated from `generate_amc_simulation_diagrams.py`:

### System & Data Flow
1. **[System Architecture (4-Layer)](images/01_system_architecture_4layer.png)** - High-level four-layer design
2. **[Data Flow - OSCE Session](images/02_data_flow_osce_session.png)** - End-to-end message flow

### Agent Architecture
3. **[Agent Architecture Overview](images/03_agent_architecture_overview.png)** - All 6 SIM-* agents
4. **[SIM-001 AI Patient Detail](images/04_sim001_ai_patient_detail.png)** - AI Patient class diagram
5. **[SIM-002 AI Examiner Detail](images/05_sim002_examiner_detail.png)** - AI Examiner class diagram
6. **[SIM-003 Orchestrator Detail](images/06_sim003_orchestrator_detail.png)** - Session orchestrator

### State Machines
7. **[Session State Machine](images/07_state_machine_session.png)** - OSCE session lifecycle
8. **[Emotional State Machine](images/08_state_machine_emotions.png)** - Patient emotional states

### Data & API
9. **[Database Schema ER Diagram](images/09_database_schema_er.png)** - PostgreSQL + Redis schema
10. **[WebSocket Protocol](images/10_websocket_protocol.png)** - Message types and flow

### Deployment & Integration
11. **[Deployment Architecture](images/11_deployment_architecture.png)** - Docker containers
12. **[Integration Architecture](images/12_integration_architecture.png)** - System integrations

---

## 📚 Documentation Files

1. **[00_INDEX.md](00_INDEX.md)** - Master index and navigation
2. **[01_SYSTEM_ARCHITECTURE.md](01_SYSTEM_ARCHITECTURE.md)** - Four-layer architecture explained
3. **02_AGENT_ARCHITECTURE.md** - Detailed agent specifications (6 agents)
4. **03_STATE_MACHINES.md** - Session and emotional state machines
5. **04_DATA_ARCHITECTURE.md** - Database schema and Redis structures
6. **05_API_SPECIFICATIONS.md** - REST + WebSocket API documentation
7. **06_DEPLOYMENT_GUIDE.md** - Docker deployment and scaling
8. **07_INTEGRATION_GUIDE.md** - Integration with existing systems

---

## 🔧 Regenerating Diagrams

### Prerequisites

```bash
pip install diagrams==0.25.1 graphviz==0.20.3
```

### Generate All Diagrams

```bash
cd planning/feb-6-ai-simulator-amc/
python3 generate_amc_simulation_diagrams.py
```

**Output:** 12 PNG files in `images/` directory (total ~2MB)

**Generation Time:** ~10 seconds

---

## 🏗️ System Overview

### Four-Layer Architecture

```
┌─────────────────────────────────────┐
│  Layer 1: Presentation (Frontend)   │  React UI, WebSocket Client
├─────────────────────────────────────┤
│  Layer 2: Orchestration (Backend)   │  FastAPI, SIM-003, SIM-004
├─────────────────────────────────────┤
│  Layer 3: Intelligence (AI Agents)  │  SIM-001, SIM-002, Claude API
├─────────────────────────────────────┤
│  Layer 4: Data (Storage)            │  Redis, PostgreSQL
└─────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **SIM-001** | AI Patient (conversational) | Claude 3.5 + LangChain |
| **SIM-002** | AI Examiner (scoring) | Claude 3.5 + AMC Rubrics |
| **SIM-003** | Session Orchestrator | FastAPI + WebSocket |
| **SIM-004** | Context Manager | Redis + Conversation History |
| **SIM-005** | Physical Exam (future) | - |
| **SIM-006** | Performance Analytics | PostgreSQL + Analytics |

---

## 🎓 For Different Audiences

### Developers
1. Start with **[01_SYSTEM_ARCHITECTURE.md](01_SYSTEM_ARCHITECTURE.md)** for overview
2. Read **02_AGENT_ARCHITECTURE.md** for implementation details
3. Reference **05_API_SPECIFICATIONS.md** for API integration
4. Check diagrams 03-06 for agent class structures

### DevOps / SRE
1. Read **06_DEPLOYMENT_GUIDE.md** for Docker setup
2. Check diagram 11 for container architecture
3. Review scaling and monitoring sections

### Product / Business
1. Start with this README for high-level overview
2. View diagrams 01-02 for system understanding
3. Read **01_SYSTEM_ARCHITECTURE.md** sections on success metrics

### Architects
1. Review **[01_SYSTEM_ARCHITECTURE.md](01_SYSTEM_ARCHITECTURE.md)** for design principles
2. Read **07_INTEGRATION_GUIDE.md** for integration patterns
3. Check diagram 12 for system integrations

---

## 📈 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| AI Patient Realism | 90%+ | User satisfaction survey |
| Scoring Accuracy | ±2 marks | vs. human examiners |
| End-to-End Latency | <3 seconds | Candidate message → response |
| WebSocket Uptime | 99%+ | Prometheus monitoring |
| Concurrent Sessions | 100+ | Load testing |

---

## 🔗 Related Documentation

### Master Plans
- **[../AMC_CLINICAL_EXAM_SIMULATION_ULTRATHINK.md](../AMC_CLINICAL_EXAM_SIMULATION_ULTRATHINK.md)** - Complete implementation plan (28,000+ words)
- **[../feature-modules-2026-02-01/03_PHASE3_AMC_SIMULATION.md](../feature-modules-2026-02-01/03_PHASE3_AMC_SIMULATION.md)** - Original Phase 3 specifications

### Existing Architecture
- **[../../SYSTEM_ARCHITECTURE_OVERVIEW.md](../../SYSTEM_ARCHITECTURE_OVERVIEW.md)** - Overall system architecture
- **[../../ARCHITECTURE_DECISION_RECORD.md](../../ARCHITECTURE_DECISION_RECORD.md)** - Architecture decisions

### Implementation
- **[../../src/agents/](../../src/agents/)** - Existing agent implementations
- **[../../backend/](../../backend/)** - Backend codebase
- **[../../frontend/](../../frontend/)** - Frontend codebase

---

## 🚀 Quick Reference

### Technology Stack

**Backend:**
- FastAPI 0.109.0 + Uvicorn
- Python 3.12+
- LangChain 0.1.0
- Anthropic Claude 3.5 Sonnet

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS 3.4+
- Zustand + TanStack Query

**Data:**
- Redis 7.x (session state)
- PostgreSQL 15.x (persistent data)

**Infrastructure:**
- Docker + docker-compose
- Nginx (reverse proxy)
- Prometheus + Grafana

---

## 📧 Questions?

1. Check the **[00_INDEX.md](00_INDEX.md)** for navigation
2. Review relevant diagram in `images/` folder
3. Read corresponding markdown document
4. Consult master Ultrathink plan for implementation details

---

## 📝 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-06 | Initial documentation with 12 diagrams | Claude (Sonnet 4.5) |

---

**Next Steps:**
- Read [00_INDEX.md](00_INDEX.md) for complete table of contents
- View [01_SYSTEM_ARCHITECTURE.md](01_SYSTEM_ARCHITECTURE.md) for detailed architecture
- Generate diagrams: `python3 generate_amc_simulation_diagrams.py`
