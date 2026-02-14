# Phase 1: Foundation (Week 1-2)
## Content Acquisition & Infrastructure Setup

**Duration:** 2 weeks
**Priority:** P0 (Critical Path)
**Dependencies:** None (can start immediately)
**Status:** 🟡 80% Complete
**Estimated Effort:** 40-50 hours

---

## Objectives

1. Acquire and process medical content (free resources)
2. Validate PDF processing → Embeddings → Vector DB pipeline
3. Implement 2 MCP servers (Medical Knowledge + PubMed)
4. Deploy agent infrastructure (registry + message queue)
5. Test end-to-end RAG pipeline
6. Establish quality baselines

---

## Week 1: Content Acquisition & Processing

### Monday: Download Free Resources
**Time:** 2-3 hours
**Dependencies:** Internet connection, storage space (~10 GB)

**Tasks:**
- [ ] **Download StatPearls** (10,000+ medical articles)
  ```bash
  python scripts/download_statpearls.py
  # Expected time: 2-4 hours
  # Storage: ~5 GB
  # Output: data/pdfs/free/statpearls/
  ```

- [ ] **Download NCBI Bookshelf** (100 medical books)
  ```bash
  python scripts/download_ncbi_bookshelf.py
  # Expected time: 1-2 hours
  # Storage: ~2 GB
  # Output: data/pdfs/free/ncbi_bookshelf/
  ```

- [ ] **Collect Australian Guidelines** (NSW Health, Immunisation Handbook)
  ```bash
  python scripts/download_australian_guidelines.py
  # Expected time: 1 hour
  # Storage: ~200 MB
  ```

**Success Criteria:**
- ✅ 1,000+ PDF files downloaded
- ✅ ~7-10 GB of medical content
- ✅ All free resources catalogued

---

### Tuesday-Wednesday: Process Content
**Time:** 6-8 hours (mostly automated)
**Dependencies:** Monday complete, GPU recommended for embeddings

**Tasks:**
- [ ] **Extract text from PDFs**
  ```bash
  ./medical_ai.py process pdfs --input data/pdfs/free/statpearls
  # Extract text, metadata, citations
  # Output: data/processed/text/
  ```

- [ ] **Chunk documents** (optimal size for retrieval)
  ```bash
  ./medical_ai.py process chunk --chunk-size 512 --overlap 50
  # Semantic chunking with overlap
  # Output: data/processed/chunks/
  ```

- [ ] **Generate embeddings** (S-PubMedBert model)
  ```bash
  ./medical_ai.py process embed --batch-size 32 --model pritamdeka/S-PubMedBert-MS-MARCO
  # GPU: ~2 hours
  # CPU: ~6-8 hours
  # Output: data/processed/embeddings/
  ```

- [ ] **Index in Qdrant** (vector database)
  ```bash
  ./medical_ai.py process index --collection medical_knowledge
  # Upload embeddings to Qdrant
  # Output: Qdrant collection with ~40,000 points
  ```

**Success Criteria:**
- ✅ 40,000+ chunks in Qdrant
- ✅ Semantic search working
- ✅ Average search time <500ms
- ✅ Metadata preserved (title, page, source)

---

### Thursday: Validate Pipeline
**Time:** 2-3 hours
**Dependencies:** Wednesday complete

**Tasks:**
- [ ] **Test vector search**
  ```bash
  ./medical_ai.py test search "acute coronary syndrome management"
  ./medical_ai.py test search "diabetes diagnosis criteria"
  ./medical_ai.py test search "anaphylaxis emergency management"
  ```

- [ ] **Test LLM generation**
  ```bash
  ./medical_ai.py test llm --model meditron:7b --prompt "Explain ACS management"
  ```

- [ ] **Generate first test question**
  ```bash
  python src/generation/mcq_generator.py --topic "cardiology" --difficulty "medium" --count 1
  ```

- [ ] **Manual quality review**
  - Check if question is clinically accurate
  - Verify citations are correct
  - Assess difficulty level
  - Document quality issues

**Success Criteria:**
- ✅ Search returns relevant results (validated manually)
- ✅ LLM generates coherent, medically accurate content
- ✅ End-to-end pipeline validated (search → generate → validate)
- ✅ Response time acceptable (<5 seconds total)

---

### Friday: Documentation & Week 1 Review
**Time:** 2-3 hours

**Tasks:**
- [ ] Document pipeline performance metrics
- [ ] Identify bottlenecks (embedding generation? search latency?)
- [ ] Document quality issues found
- [ ] Update README with setup instructions
- [ ] Week 1 retrospective: What worked? What didn't?

**Deliverables:**
- ✅ Pipeline performance report
- ✅ Quality assessment document
- ✅ Updated documentation
- ✅ Week 2 plan adjusted based on learnings

---

## Week 2: Infrastructure Setup

### Monday-Tuesday: MCP Servers
**Time:** 12-14 hours
**Dependencies:** Phase 1 Week 1 complete

**Task 1: Medical Knowledge Server** (8 hours)
```python
# File: src/mcp_servers/medical_knowledge_server.py

# Features:
- Qdrant vector search integration
- Neo4j knowledge graph queries
- Citation retrieval with page numbers
- Metadata filtering (specialty, date, source)
- Search result reranking

# API Endpoints:
- POST /search - Semantic search
- GET /concept/{id} - Get concept details
- GET /related/{concept_id} - Get related concepts
- POST /ask - Ask a medical question (RAG)

# Deploy on port 5001
```

**Testing:**
- [ ] Test search endpoint with 10 medical queries
- [ ] Validate response time (<500ms p95)
- [ ] Check citation accuracy (100% must have page numbers)
- [ ] Test Neo4j integration (concept relationships)

---

**Task 2: PubMed Server** (6 hours)
```python
# File: src/mcp_servers/pubmed_server.py

# Features:
- Biopython integration (Entrez API)
- Article search by keywords/MeSH terms
- Abstract retrieval
- Citation formatting (Vancouver style)
- Related articles

# API Endpoints:
- POST /search - Search PubMed
- GET /article/{pmid} - Get article details
- POST /batch - Batch article retrieval
- GET /related/{pmid} - Get related articles

# Deploy on port 5002
```

**Testing:**
- [ ] Search for "diabetes management" (expect 1000+ results)
- [ ] Retrieve abstract for PMID 12345678
- [ ] Test rate limiting (NCBI: 3 requests/second)
- [ ] Validate citation formatting

**Success Criteria:**
- ✅ 2 MCP servers running and responding
- ✅ API endpoints working correctly
- ✅ Integration tests passing (pytest)
- ✅ Response times within SLA

---

### Wednesday-Thursday: Agent Infrastructure
**Time:** 8-10 hours
**Dependencies:** MCP servers deployed

**Task 1: Agent Registry** (6 hours)
```python
# File: src/agents/infrastructure/agent_registry.py

# Features:
- Agent registration (name, capabilities, status)
- Health check system (heartbeat every 30s)
- Load balancing (round-robin across healthy agents)
- Agent discovery (find agents by capability)

# Database Schema:
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),
    capabilities JSONB,
    status VARCHAR(20), -- 'active', 'idle', 'failed'
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP
);

# Deploy service on port 5100
```

**Testing:**
- [ ] Register 3 test agents
- [ ] Simulate heartbeat
- [ ] Test health check (mark agent as failed if no heartbeat)
- [ ] Test load balancing (distribute tasks evenly)

---

**Task 2: Message Queue Setup** (4 hours)
```python
# File: src/agents/infrastructure/message_queue.py

# Features:
- Redis Pub/Sub for inter-agent messaging
- Message format standardization (JSON)
- Request/response pattern
- Message persistence (24-hour TTL)

# Message Format:
{
    "id": "msg_123",
    "from": "agent_id",
    "to": "agent_id",
    "type": "request|response|broadcast",
    "payload": {...},
    "timestamp": "2026-01-17T10:00:00Z"
}
```

**Testing:**
- [ ] Send message from Agent A to Agent B
- [ ] Test broadcast (Agent A → All agents)
- [ ] Test message persistence (retrieve after restart)
- [ ] Test TTL (message expires after 24 hours)

**Success Criteria:**
- ✅ Agent registry operational (service running)
- ✅ Message queue tested (Redis Pub/Sub working)
- ✅ State management working (agents can register/deregister)
- ✅ Health checks functioning (detect failed agents)

---

### Friday: Documentation & Phase 1 Review
**Time:** 4 hours

**Tasks:**
- [ ] **Update README** with new components
  - MCP server setup instructions
  - Agent infrastructure documentation
  - Troubleshooting guide (common issues)

- [ ] **Create API documentation** (OpenAPI/Swagger)
  - Medical Knowledge Server API
  - PubMed Server API
  - Agent Registry API

- [ ] **Write troubleshooting guide**
  - Common Qdrant issues
  - LLM generation errors
  - Agent communication failures

- [ ] **Phase 1 Review Meeting**
  - Validate all success criteria met
  - Identify gaps or issues
  - Plan Phase 2 (Backend Core)
  - Update timeline if needed

---

## Phase 1 Deliverables Checklist

### Content & Data
- [ ] 10,000+ medical documents processed
- [ ] 40,000+ chunks indexed in Qdrant
- [ ] Embeddings generated (S-PubMedBert)
- [ ] Metadata preserved (citations, pages, sources)

### Infrastructure
- [ ] Medical Knowledge MCP Server (port 5001)
- [ ] PubMed MCP Server (port 5002)
- [ ] Agent Registry (port 5100)
- [ ] Redis message queue configured

### Validation
- [ ] End-to-end RAG pipeline tested
- [ ] Search quality validated (manual review)
- [ ] LLM generation tested (10 sample questions)
- [ ] Performance baselines established

### Documentation
- [ ] README updated with setup instructions
- [ ] API documentation (OpenAPI)
- [ ] Troubleshooting guide created
- [ ] Phase 1 performance report

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| PDFs processed | 1,000+ | TBD | ⏳ |
| Chunks indexed | 40,000+ | TBD | ⏳ |
| Search time (p95) | <500ms | TBD | ⏳ |
| LLM response time | <5s | TBD | ⏳ |
| MCP servers running | 2 | TBD | ⏳ |
| Agent registry uptime | 99%+ | TBD | ⏳ |
| Documentation completeness | 100% | TBD | ⏳ |

---

## Risks & Mitigation

### Risk 1: Embedding generation too slow (CPU)
**Impact:** Week 1 timeline slips by 1-2 days
**Probability:** Medium
**Mitigation:**
- Use batch processing (32-64 chunks at once)
- Run overnight if needed
- Consider cloud GPU for 4-hour job ($10)

### Risk 2: Qdrant indexing fails
**Impact:** Cannot test search pipeline
**Probability:** Low
**Mitigation:**
- Check Qdrant logs (/var/log/qdrant)
- Verify Docker container running
- Restart Qdrant service if needed

### Risk 3: LLM quality insufficient
**Impact:** Generated questions are inaccurate
**Probability:** Medium
**Mitigation:**
- Use best available model (Llama 3.1 70B)
- Add conservative system prompts
- Implement QA validation before accepting output

### Risk 4: MCP server integration issues
**Impact:** Week 2 timeline slips
**Probability:** Low-Medium
**Mitigation:**
- Start with simple endpoints
- Test incrementally
- Have fallback to direct Qdrant/PubMed access

---

## Blockers & Dependencies

### Blockers (Must resolve to proceed)
- None! Phase 1 has no dependencies

### Soft Dependencies (Helpful but not required)
- GPU for faster embedding generation
- Books acquired (for higher quality content)
- Docker running correctly (all services healthy)

---

## Next Phase: Phase 2 (Backend Core)

**Start Date:** Week 3 (after Phase 1 complete)
**Duration:** 4 weeks
**Key Deliverable:** FastAPI backend with authentication + APIs

**Prerequisites from Phase 1:**
- ✅ Qdrant populated with content
- ✅ MCP servers operational
- ✅ Agent infrastructure ready
- ✅ Pipeline validated

**See:** [phase2_backend.md](phase2_backend.md)

---

**Last Updated:** January 17, 2026
**Phase Owner:** PM-001 (Project Manager)
**Status:** 🟡 80% Complete (Infrastructure done, content acquisition pending)
**Next Review:** End of Week 2
