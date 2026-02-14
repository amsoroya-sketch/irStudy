# Agent-Specific Requirements

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Agent-Specific Requirements

### 8.1 Medical Expert Agents (MED-XXX)

**Mandatory Requirements:**

1. **Citations**: MUST cite Therapeutic Guidelines or equivalent for every medical claim
2. **Terminology**: MUST use Australian spelling and drug names
3. **Validation**: MUST validate clinical accuracy in `validate_output()`
4. **Red Flags**: MUST identify and flag life-threatening conditions
5. **Dosages**: MUST specify drug dosages with units (mg, mcg, mL)
6. **SI Units**: MUST use SI units (mmol/L, not mg/dL)
7. **Emergency**: MUST use "Call 000" for emergencies (Australian number)

**Agent List:**
- MED-001: Cardiology Clinical Expert
- MED-002: Emergency Medicine Expert
- MED-003: General Practice Expert
- MED-004: Paediatrics Expert
- MED-005: Obstetrics & Gynaecology Expert
- MED-006: Surgery Expert
- MED-007: Psychiatry Expert
- MED-008: Endocrinology Expert
- MED-009: Gastroenterology Expert
- MED-010: Respiratory Medicine Expert
- MED-011: Neurology Expert
- MED-012: Rheumatology Expert
- MED-013: Infectious Diseases Expert
- MED-014: Dermatology Expert
- MED-015: Medical QA Validator (quality assurance for all medical content)

### 8.2 Development Agents (DEV-XXX)

**Mandatory Requirements:**

1. **Testing**: MUST write unit tests with 80%+ coverage
2. **Code Style**: MUST follow PEP 8 (Python) or ESLint/Prettier (TypeScript)
3. **Documentation**: MUST document APIs with OpenAPI (FastAPI) or TypeDoc (TypeScript)
4. **Error Handling**: MUST handle errors gracefully with specific exceptions
5. **Type Safety**: MUST use type hints (Python) or TypeScript types
6. **Logging**: MUST use structured logging (not print statements)
7. **Security**: MUST follow OWASP Top 10 security practices

**Agent List:**
- DEV-001: Senior Backend Architect (Python/FastAPI)
- DEV-002: Senior Frontend Architect (Next.js/React)
- DEV-003: UI/UX Specialist & Design System Engineer
- DEV-004: Database Engineer (PostgreSQL/SQLAlchemy)
- DEV-005: Authentication & Authorization Engineer (OAuth2/JWT)
- DEV-006: API Integration Engineer
- DEV-007: WebSocket & Real-time Engineer
- DEV-008: Payment Systems Engineer
- DEV-009: Email & Notifications Engineer
- DEV-010: Search Engineer (Elasticsearch)
- DEV-011: File Storage Engineer
- DEV-012: Caching Engineer (Redis)

### 8.3 AI/Data Agents (AI-XXX)

**Mandatory Requirements:**

1. **LLM Access**: MUST use OllamaClient for LLM access (never direct API calls)
2. **Token Limits**: MUST handle token limits (4K-8K tokens)
3. **Fallback**: MUST implement fallback strategies for LLM failures
4. **Performance**: MUST track and report performance metrics
5. **Quality**: MUST validate embeddings quality and search relevance
6. **Progress**: MUST use tqdm for long-running operations
7. **Memory**: MUST batch process large datasets

**Agent List:**
- AI-001: RAG System Engineer (Qdrant + PubMedBERT embeddings)
- AI-002: LLM Operations Engineer (Prompt engineering, model selection)
- AI-003: Medical NLP Engineer (Named Entity Recognition)
- AI-004: ETL Engineer (PDF → Text → Chunks → Embeddings → Qdrant)
- AI-005: Question Generator (MCQ generation with medical accuracy)
- AI-006: Answer Validator (Validate correctness and clinical accuracy)
- AI-007: Semantic Search Engineer (Vector search optimization)
- AI-008: ML Model Trainer (Train/fine-tune medical models)

### 8.4 QA Agents (QA-XXX)

**Mandatory Requirements:**

1. **Quality Gates**: MUST run all configured quality gates
2. **Coverage**: MUST achieve 80%+ test coverage
3. **Security**: MUST catch and report security vulnerabilities
4. **Medical**: MUST validate medical accuracy for medical content
5. **Accessibility**: MUST test WCAG 2.1 AA compliance
6. **Performance**: MUST validate performance targets met
7. **Reporting**: MUST generate detailed test reports

**Agent List:**
- QA-001: Medical Content QA (Clinical accuracy validator)
- QA-002: E2E Testing Engineer (Playwright, integration tests)
- QA-003: Performance Testing Engineer (Load tests, stress tests)
- QA-004: Security Testing Engineer (OWASP Top 10, vulnerability scanning)

### 8.5 DevOps & Infrastructure Agents (DEVOPS-XXX)

**Mandatory Requirements:**

1. **CI/CD**: MUST maintain CI/CD pipelines
2. **Monitoring**: MUST implement comprehensive monitoring
3. **Logging**: MUST aggregate and analyze logs
4. **Scaling**: MUST handle auto-scaling configurations
5. **Backup**: MUST implement backup and disaster recovery
6. **Security**: MUST apply security patches promptly
7. **Documentation**: MUST document infrastructure as code

**Agent List:**
- DEVOPS-001: Kubernetes Engineer (K8s, Helm charts)
- DEVOPS-002: CI/CD Engineer (GitHub Actions, deployment pipelines)
- DEVOPS-003: Monitoring & Observability Engineer (Prometheus, Grafana)
- DEVOPS-004: Database DevOps Engineer (PostgreSQL, Qdrant management)
- DEVOPS-005: Cloud Infrastructure Engineer (AWS/Azure/GCP)
- DEVOPS-006: Security & Compliance Engineer (Secrets management, compliance)

### 8.6 Inter-Agent Communication Pattern

**Standard task delegation via PM-001:**

```python
# ✅ CORRECT - PM delegates to specialist
from src.agents.pm_001_project_manager import ProjectManagerAgent
from src.agents.med_001_cardiology import CardiologyExpert

pm = ProjectManagerAgent()
cardiology_agent = CardiologyExpert()

# Register agent with PM
pm.register_agent(cardiology_agent)

# Create task
task = AgentTask(
    title="Generate Cardiology MCQ",
    description="Generate medium difficulty MCQ about acute coronary syndrome",
    metadata={
        'type': 'generate_mcq',
        'topic': 'acute_coronary_syndrome',
        'difficulty': 'medium'
    }
)

# Delegate via PM
success = pm.assign_task_to_agent(task, agent_id="MED-001")

if success:
    # Agent executes via run_task (handles validation)
    result = cardiology_agent.run_task(task)

    if result.status == TaskStatus.COMPLETED:
        print(f"MCQ generated successfully: {result.result}")
    else:
        print(f"Task failed: {result.error}")
```

---

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
