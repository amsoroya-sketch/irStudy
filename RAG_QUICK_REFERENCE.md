# RAG Quick Reference Card
**irStudy Medical RAG System**

---

## 🎯 TL;DR

**Current System:** 42,647 vectors | Status: 🟢 ACTIVE | Quality: 0.95+ scores

```bash
# Activate & Search
source venv/bin/activate
python3 -c "
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
client = QdrantClient(url='http://localhost:6333')
model = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')
query_embedding = model.encode('YOUR QUERY HERE').tolist()
results = client.search(collection_name='medical_knowledge', query_vector=query_embedding, limit=5)
for r in results: print(f'{r.score:.4f} | {r.payload[\"source\"][:40]} | p.{r.payload[\"page\"]}')
"
```

---

## 📊 System Comparison

| Version | Vectors | Status | Use Case |
|---------|---------|--------|----------|
| **Current** | **42,647** | 🟢 **ACTIVE** | **Use this for everything** |
| Original | 27,264 | 📦 Archived | Only if needed for comparison |

---

## 🗂️ File Locations

```
Current RAG (ACTIVE):
└── data/embeddings/medical_embeddings_complete.pkl  (42,647 vectors)

Original RAG (Archived):
└── data/embeddings/medical_embeddings_all.pkl       (27,264 vectors)
```

---

## ⚡ Most Common Operations

### 1. Check Status (10 seconds)

```bash
curl -s http://localhost:6333/collections/medical_knowledge | python3 -m json.tool | grep -E '(points_count|status)'
```

**Expected:**
```json
"status": "green",
"points_count": 42647,
```

### 2. Quick Search (30 seconds)

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(url='http://localhost:6333')
model = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')

# Search
query = "hypertension management"
results = client.search(
    collection_name='medical_knowledge',
    query_vector=model.encode(query).tolist(),
    limit=3
)

# Results
for r in results:
    print(f"{r.score:.4f} | {r.payload['source']} | Page {r.payload['page']}")
```

### 3. Re-index (if needed - 10 seconds)

```bash
source venv/bin/activate
python3 scripts/index_qdrant.py \
  --embeddings data/embeddings/medical_embeddings_complete.pkl \
  --collection medical_knowledge \
  --batch-size 100
```

---

## 🔍 Search Templates

### Template 1: Basic Search

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(url='http://localhost:6333')
model = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')

query = "YOUR MEDICAL QUERY"
query_embedding = model.encode(query).tolist()

results = client.search(
    collection_name='medical_knowledge',
    query_vector=query_embedding,
    limit=5
)

for i, r in enumerate(results, 1):
    print(f"\n{i}. Score: {r.score:.4f}")
    print(f"   {r.payload['source']} (Page {r.payload['page']})")
    print(f"   {r.payload['text'][:200]}...")
```

### Template 2: Filter by Source Type

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Search only Australian guidelines
results = client.search(
    collection_name='medical_knowledge',
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key='source_category',
                match=MatchValue(value='australian_guidelines')
            )
        ]
    ),
    limit=5
)
```

**Available source_category values:**
- `australian_guidelines`
- `core_medicine`
- `clinical_skills`
- `gp_primary_care`
- `pediatrics`
- `obgyn`
- `surgery`
- `psychiatry`
- `emergency`

### Template 3: Filter by Exam Type

```python
# Search only AMC Clinical content
results = client.search(
    collection_name='medical_knowledge',
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key='exam_type',
                match=MatchValue(value='AMC_Clinical')
            )
        ]
    ),
    limit=5
)
```

**Available exam_type values:**
- `AMC_MCQ` (most content)
- `AMC_Clinical` (Talley, clinical examination)
- `ICRP` (NSW Health, Australian-specific)

---

## 🆘 Troubleshooting

### Problem: Qdrant not responding

```bash
# Check if running
curl http://localhost:6333/health

# If Docker: restart
docker restart qdrant

# Check status
docker ps | grep qdrant
```

### Problem: Low search scores

```bash
# Verify model
python3 -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')
print(f'Dimension: {model.get_sentence_embedding_dimension()}')
"
# Should output: Dimension: 768
```

### Problem: Wrong collection

```bash
# List all collections
curl -s http://localhost:6333/collections | python3 -m json.tool

# Switch to current RAG if needed
python3 scripts/index_qdrant.py \
  --embeddings data/embeddings/medical_embeddings_complete.pkl \
  --collection medical_knowledge
```

---

## 📈 What's Included

### Current RAG (42,647 vectors)

- ✅ **Medical Textbooks** (14 books) - 9,950 chunks
- ✅ **StatPearls** (9,627 articles) - 17,314 chunks
- ✅ **Cochrane Reviews** (1,509 PDFs) - 15,383 chunks
  - Original: 1,431 PDFs
  - **New:** 78 PDFs (added 2026-01-24)

### Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Search Scores | 0.95+ | ✅ Excellent |
| Latency | <100ms | ✅ Fast |
| Index Size | 42,647 | ✅ Complete |
| Status | Green | ✅ Healthy |

---

## 🎓 Use Cases

### 1. Generate MCQs

```python
# Get content on a topic
topic = "diabetes mellitus type 2"
results = client.search(
    collection_name='medical_knowledge',
    query_vector=model.encode(topic).tolist(),
    limit=10
)

# Use with Claude to generate MCQs
# Include citations from result.payload['source'] and result.payload['page']
```

### 2. Create OSCE Scenarios

```python
# Get clinical examination content
query = "cardiovascular examination"
results = client.search(
    collection_name='medical_knowledge',
    query_vector=model.encode(query).tolist(),
    query_filter=Filter(
        must=[FieldCondition(key='exam_type', match=MatchValue(value='AMC_Clinical'))]
    ),
    limit=5
)
```

### 3. Answer Clinical Questions

```python
# Get evidence for clinical question
question = "What is the first-line treatment for hypertension?"
results = client.search(
    collection_name='medical_knowledge',
    query_vector=model.encode(question).tolist(),
    limit=5
)

# Format answer with citations
answer = f"Based on {results[0].payload['source']} (p.{results[0].payload['page']}): ..."
```

---

## 📞 Support

**Full Documentation:** `RAG_SYSTEM_INDEX.md`

**Session Logs:** `/mnt/data/medical_resources/logs/`

**System Status:**
```bash
curl http://localhost:6333/collections/medical_knowledge | python3 -m json.tool
```

---

**Last Updated:** 2026-01-24
**System:** 🟢 PRODUCTION-READY
**Vectors:** 42,647
**Quality:** Excellent (0.95+)
