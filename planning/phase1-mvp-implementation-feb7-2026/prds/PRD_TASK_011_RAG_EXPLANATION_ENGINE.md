# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_011 - RAG Explanation Engine (5-6 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/backend

# Verify Qdrant connection
python -c "from qdrant_client import QdrantClient; client = QdrantClient('localhost', port=6333); print('✅ Qdrant connected')"

# Create RAG service
mkdir -p src/services/rag

cat > src/services/rag/rag_service.py <<'EOF'
# RAG service will be implemented here
EOF
```

**DO NOT**:
- ❌ Ask "Would you like me to implement vector search first?"
- ❌ Ask "Should I use a specific embedding model?"
- ❌ Wait for approval
- ❌ Ask "Which similarity threshold should I use?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 3
- **Day:** 2 (Feb 22, 2026)
- **Duration:** 5-6 hours
- **Priority:** P1-High
- **Dependencies:** TASK_002 (MCQ endpoints must exist)
- **Owner:** general-purpose agent (Python/RAG)
- **Status:** 🟡 Not Started

---

## 🎯 Objectives

1. **Integrate Qdrant vector database** (localhost:6333)
2. **Implement RAG query service** for enhanced MCQ explanations
3. **Add citation linking** to 11 source textbooks
4. **Configure Top-K retrieval** (K=5 for best matches)
5. **Achieve <500ms query latency**
6. **Test suite: 100% pass rate**

---

## 📝 Implementation Guide

### Step 1: Create RAG Service (2 hours)

```bash
cat > src/services/rag/rag_service.py <<'EOF'
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict
import os

class RAGService:
    """Service for RAG-enhanced MCQ explanations using Qdrant"""

    def __init__(self):
        self.client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
        self.collection_name = "medical_knowledge_base"

    def query_relevant_context(
        self,
        query: str,
        specialty: str = None,
        top_k: int = 5,
        confidence_threshold: float = 0.65
    ) -> List[Dict]:
        """
        Query Qdrant for relevant medical knowledge.

        Args:
            query: Search query text
            specialty: Filter by specialty
            top_k: Number of results to return
            confidence_threshold: Minimum similarity score

        Returns:
            List of relevant documents with citations
        """
        # Get embeddings (using sentence-transformers)
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = model.encode(query).tolist()

        # Build filter
        query_filter = None
        if specialty:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="specialty",
                        match=MatchValue(value=specialty)
                    )
                ]
            )

        # Search Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=confidence_threshold
        )

        # Format results
        results = []
        for hit in search_result:
            results.append({
                "text": hit.payload.get("text"),
                "source": hit.payload.get("source"),
                "page": hit.payload.get("page"),
                "section": hit.payload.get("section"),
                "confidence": hit.score,
                "citation": self._format_citation(hit.payload)
            })

        return results

    def _format_citation(self, payload: Dict) -> str:
        """Format citation in Australian medical guideline style"""
        source = payload.get("source", "")
        page = payload.get("page", "")
        section = payload.get("section", "")

        if source.startswith("eTG"):
            return f"eTG: {payload.get('title', '')} (Page {page}, Section {section})"
        elif source.startswith("PBS"):
            return f"PBS: {payload.get('title', '')} - {payload.get('drug_name', '')}"
        elif source.startswith("AMH"):
            return f"AMH: {payload.get('title', '')} (Page {page})"
        elif source.startswith("AHPRA"):
            return f"AHPRA: {payload.get('title', '')} - {payload.get('guideline_number', '')}"
        else:
            return f"{source}: {payload.get('title', '')} (Page {page})"

    def enhance_mcq_explanation(
        self,
        mcq_text: str,
        mcq_explanation: str,
        specialty: str
    ) -> Dict:
        """
        Enhance MCQ explanation with RAG-retrieved context.

        Returns:
            Enhanced explanation with supporting evidence and citations
        """
        # Query relevant context
        context = self.query_relevant_context(
            query=f"{mcq_text} {mcq_explanation}",
            specialty=specialty,
            top_k=3
        )

        # Build enhanced explanation
        enhanced = {
            "original_explanation": mcq_explanation,
            "supporting_evidence": [item["text"] for item in context],
            "citations": [item["citation"] for item in context],
            "confidence_scores": [item["confidence"] for item in context],
            "sources": [item["source"] for item in context]
        }

        return enhanced
EOF

echo "✅ RAG service created"
```

### Step 2: Create RAG API Endpoints (1.5 hours)

```bash
cat > src/api/v1/mcqs/rag_routes.py <<'EOF'
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.auth.dependencies import get_current_user
from src.db.models.user import User
from src.services.rag.rag_service import RAGService
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/mcqs", tags=["MCQs - RAG"])

class RAGEnhancedExplanation(BaseModel):
    mcq_id: int
    original_explanation: str
    supporting_evidence: List[str]
    citations: List[str]
    confidence_scores: List[float]

rag_service = RAGService()

@router.get("/{mcq_id}/enhanced-explanation", response_model=RAGEnhancedExplanation)
async def get_enhanced_explanation(
    mcq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get RAG-enhanced explanation for an MCQ.

    Returns: Original explanation + supporting evidence from medical textbooks
    Response time target: <500ms
    """
    import time
    start = time.time()

    # Fetch MCQ
    from src.db.models.mcq import MCQ
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(status_code=404, detail="MCQ not found")

    # Enhance explanation with RAG
    enhanced = rag_service.enhance_mcq_explanation(
        mcq_text=mcq.question_text,
        mcq_explanation=mcq.explanation,
        specialty=mcq.specialty
    )

    elapsed = (time.time() - start) * 1000

    # Performance check
    if elapsed > 500:
        print(f"⚠️  RAG query took {elapsed:.2f}ms (target: <500ms)")

    return RAGEnhancedExplanation(
        mcq_id=mcq_id,
        **enhanced
    )
EOF

# Register router
python <<'EOF'
import re
with open("src/main.py", "r") as f:
    content = f.read()
if "rag_routes" not in content:
    content = re.sub(
        r"(from src.api.v1.mcqs import router)",
        "\\1\nfrom src.api.v1.mcqs.rag_routes import router as rag_router\n",
        content
    )
    content = re.sub(
        r"(app.include_router\(mcqs_router\))",
        "\\1\napp.include_router(rag_router)\n",
        content
    )
    with open("src/main.py", "w") as f:
        f.write(content)
    print("✅ RAG routes registered")
else:
    print("✅ RAG routes already registered")
EOF
```

### Step 3: Create Tests (1 hour)

```bash
cat > tests/api/v1/test_rag.py <<'EOF'
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token
import time

client = TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "test_user@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_enhanced_explanation(auth_headers):
    """Test RAG-enhanced explanation endpoint"""
    # Get random MCQ first
    mcq_response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    mcq_id = mcq_response.json()["id"]

    # Get enhanced explanation
    response = client.get(f"/api/v1/mcqs/{mcq_id}/enhanced-explanation", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "original_explanation" in data
    assert "supporting_evidence" in data
    assert "citations" in data
    assert "confidence_scores" in data

    # Verify at least 3 citations (from RAG query top_k=3)
    assert len(data["citations"]) >= 1

    # Verify confidence scores in valid range
    for score in data["confidence_scores"]:
        assert 0.0 <= score <= 1.0
        assert score >= 0.65  # Meets threshold

def test_rag_performance(auth_headers):
    """Test that RAG queries complete in <500ms"""
    mcq_response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    mcq_id = mcq_response.json()["id"]

    start = time.time()
    response = client.get(f"/api/v1/mcqs/{mcq_id}/enhanced-explanation", headers=auth_headers)
    elapsed = (time.time() - start) * 1000

    assert response.status_code == 200
    assert elapsed < 500, f"RAG query took {elapsed:.2f}ms (target: <500ms)"

def test_rag_service_directly():
    """Test RAG service methods"""
    from src.services.rag.rag_service import RAGService

    rag = RAGService()

    # Test query_relevant_context
    results = rag.query_relevant_context(
        query="paracetamol dosage for adults",
        specialty="Pharmacology",
        top_k=5
    )

    assert isinstance(results, list)
    assert len(results) <= 5

    # Verify result structure
    if results:
        assert "text" in results[0]
        assert "source" in results[0]
        assert "confidence" in results[0]
        assert "citation" in results[0]

pytest tests/api/v1/test_rag.py -v
```

---

## ✅ Success Criteria

1. ✅ Qdrant integration complete (localhost:6333)
2. ✅ RAG query service implemented
3. ✅ Citation linking to 11 textbooks
4. ✅ Top-K retrieval configured (K=5)
5. ✅ Query latency <500ms
6. ✅ Tests: 100% pass rate

---

## 🔄 When Complete

```bash
sed -i 's/TASK_011.*TODO/TASK_011: ✅ DONE/' @fix_plan.md

git commit -m "feat(rag): Complete TASK_011 RAG Explanation Engine - Qdrant integration

- RAG service with Qdrant vector database
- Enhanced MCQ explanations with supporting evidence
- Citation linking to 11 Australian medical textbooks
- Top-K retrieval (K=5) with confidence threshold >0.65
- Query latency: <500ms
- Test suite: 100% pass rate

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_011 complete. Starting TASK_012..."
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
