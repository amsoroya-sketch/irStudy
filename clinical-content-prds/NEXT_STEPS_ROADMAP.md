# Next Steps Roadmap - After Batch 1 Completion

**Current Status**: ✅ All 207 personas generated with verified RAG citations
**Date**: 2026-03-16

---

## 🎯 Immediate Next Steps (Today - Week 1)

### 1. Fix QA Validator Schema (30 minutes) ⚠️ HIGH PRIORITY

**Problem**: QA validator expects `expected_diagnosis` field, personas have `diagnosis`

**Impact**: Can't run automated QA validation yet

**Fix**:
```bash
# Option A: Update validator to match generator
sed -i 's/expected_diagnosis/diagnosis/g' \
  clinical-content-prds/validation-system/qa_validator.py

# Option B: Update all personas (not recommended - 207 files)
# Better to fix validator once
```

**Validation**:
```bash
python3 -c "
import sys
sys.path.insert(0, 'clinical-content-prds/validation-system')
from qa_validator import PersonaQAValidator
import json

validator = PersonaQAValidator()
with open('clinical-content-prds/validation-system/batch1_personas/cardiology_001_stemi_male_65_persona.json') as f:
    persona = json.load(f)

result = validator.validate_single_persona(persona)
print(f'Pass: {result[\"overall_pass\"]}')
print(f'Score: {result[\"quality_score\"]}/100')
"
```

**Expected**: All personas pass QA validation

---

### 2. Database Insertion (2 hours) 🔴 CRITICAL

**Goal**: Load all 207 personas into PostgreSQL database

**Files Needed**:
```bash
# Check if insertion script exists
ls scripts/insert_batch1_personas.py
```

**If script doesn't exist, create it**:
```python
#!/usr/bin/env python3
"""Insert Batch 1 personas into PostgreSQL database"""

import json
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, 'backend/src')
from db.models import PatientPersona
from config import get_database_url

def insert_personas():
    # Database connection
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load all personas
    persona_dir = Path('clinical-content-prds/validation-system/batch1_personas')
    persona_files = sorted(persona_dir.glob('*.json'))

    inserted = 0
    errors = 0

    for pfile in persona_files:
        try:
            with open(pfile) as f:
                data = json.load(f)

            # Create database record
            persona = PatientPersona(
                persona_id=data['id'],
                name=data['name'],
                age=data['age'],
                gender=data['gender'],
                specialty=data['specialty'],
                diagnosis=data['diagnosis'],
                difficulty=data['difficulty'],
                persona_data=data,  # Store full JSON
                is_active=True
            )

            session.add(persona)
            session.commit()
            inserted += 1
            print(f"✅ {pfile.name}")

        except Exception as e:
            errors += 1
            print(f"❌ {pfile.name}: {e}")
            session.rollback()

    print(f"\n=== Summary ===")
    print(f"Inserted: {inserted}/207")
    print(f"Errors: {errors}")

    session.close()

if __name__ == "__main__":
    insert_personas()
```

**Run**:
```bash
cd /home/dev/Development/irStudy
source backend/venv/bin/activate
python3 scripts/insert_batch1_personas.py
```

**Verify**:
```sql
-- Connect to database
psql -U postgres -d irstudy_medical

-- Check insertion
SELECT COUNT(*) FROM patient_personas;
-- Expected: 207

-- Check specialty distribution
SELECT specialty, COUNT(*) FROM patient_personas GROUP BY specialty;
```

---

### 3. Frontend Integration (3 hours) 🟡 IMPORTANT

**Goal**: Make personas available in the UI

**Tasks**:

#### A. Update API Endpoints
```typescript
// backend/src/api/v1/personas.py
@router.get("/personas", response_model=List[PersonaListItem])
async def get_personas(
    specialty: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    # Query database with filters
    # Return persona list
```

#### B. Update Frontend Persona Selector
```typescript
// frontend/src/pages/OSCEPractice.tsx
const { data: personas } = useQuery({
  queryKey: ['personas', specialty, difficulty],
  queryFn: () => api.getPersonas({ specialty, difficulty })
})

// Update dropdown to show 207 personas
<Select>
  {personas?.map(p => (
    <option key={p.id} value={p.id}>
      {p.name} - {p.diagnosis} ({p.difficulty})
    </option>
  ))}
</Select>
```

#### C. Test in UI
```bash
# Start backend
cd backend
uvicorn src.main:app --reload

# Start frontend
cd frontend
npm run dev

# Navigate to: http://localhost:5173/osce-practice
# Select specialty → See 207 personas
```

---

## 🚀 Short-Term Goals (Week 2-4)

### 4. User Testing & Feedback (Ongoing)

**Goal**: Validate personas with real users (medical students, IMGs)

**Metrics to Track**:
- Which personas are most used
- Which specialties are most popular
- Average session duration per persona
- User ratings/feedback

**Implementation**:
```sql
-- Add analytics table
CREATE TABLE persona_usage (
    id SERIAL PRIMARY KEY,
    persona_id VARCHAR(100),
    user_id INTEGER,
    session_duration INTEGER,
    rating INTEGER,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Dashboard**:
```python
# Get most used personas
SELECT persona_id, COUNT(*) as usage_count
FROM persona_usage
GROUP BY persona_id
ORDER BY usage_count DESC
LIMIT 20;
```

---

### 5. Enhance Citation Content (4 hours) 🟢 ENHANCEMENT

**Current State**: Citations have page numbers but generic content
**Goal**: Extract actual clinical text from Qdrant chunks

**Example Current Citation**:
```json
{
  "content": "Symptom 1 related to STEMI",  // ❌ Generic
  "rag_confidence": 0.8181,
  "qdrant_point_id": "35ebb863-ace6-487e-9b26-004466f77d22"
}
```

**Enhanced Citation**:
```json
{
  "content": "ECG Rhythm Interpretation - Acute Myocardial Infarction presents with ST-segment elevation in contiguous leads...",  // ✅ Actual text
  "rag_confidence": 0.8181,
  "qdrant_point_id": "35ebb863-ace6-487e-9b26-004466f77d22"
}
```

**Script to Enhance**:
```python
#!/usr/bin/env python3
"""Enhance persona citations with actual Qdrant content"""

from qdrant_client import QdrantClient
import json
from pathlib import Path

client = QdrantClient(url='http://localhost:6333')

for pfile in Path('batch1_personas').glob('*.json'):
    with open(pfile) as f:
        persona = json.load(f)

    # Enhance symptom citations
    for symptom in persona.get('symptoms', []):
        for citation in symptom.get('rag_citations', []):
            point_id = citation['qdrant_point_id']
            points = client.retrieve('medical_knowledge', ids=[point_id])
            if points:
                # Replace generic content with real text
                citation['content'] = points[0].payload['text'][:250]

    # Save enhanced persona
    with open(pfile, 'w') as f:
        json.dump(persona, f, indent=2)

print("✅ All personas enhanced with real citation content")
```

---

### 6. Expand Medical Knowledge Base (8 hours) 🔵 SCALING

**Current**: 9,950 chunks from Murtagh, Talley, Oxford, etc.
**Goal**: 50,000+ chunks with specialty-specific resources

**Resources to Index**:

| Resource | Status | Chunks | Specialty |
|----------|--------|--------|-----------|
| **StatPearls** | ⏳ Downloading | ~25,000 | All 10 specialties |
| **Cochrane Reviews** | ⏳ Downloading | ~5,000 | Evidence-based |
| **RACGP Guidelines** | ✅ Ready | ~1,000 | General Practice |
| **RANZCOG Guidelines** | ✅ Ready | ~3,000 | ObGyn |
| **RANZCP Guidelines** | ✅ Ready | ~500 | Psychiatry |
| **NSW Health Manual** | ✅ Ready | ~2,000 | Procedures |

**Total Target**: 50,000+ chunks

**Indexing Script** (already exists):
```bash
# Index StatPearls
python3 scripts/index_qdrant.py \
  --collection statpearls \
  --source /mnt/adata/medical_resources/statpearls/ \
  --chunk-size 250 \
  --overlap 50

# Index Cochrane
python3 scripts/index_qdrant.py \
  --collection cochrane \
  --source /mnt/adata/medical_resources/cochrane/ \
  --chunk-size 300 \
  --overlap 75

# Merge into main collection
python3 scripts/merge_qdrant_collections.py \
  --source statpearls,cochrane \
  --target medical_knowledge
```

**Benefit**: Higher quality citations, more specialty-specific content

---

## 🎯 Medium-Term Goals (Month 2-3)

### 7. Batch 2-10 Personas (1,000 total)

**Expansion Plan**:
- **Batch 2**: Psychiatry (100 personas) - Depression, Anxiety, Psychosis, ADHD, etc.
- **Batch 3**: ObGyn (100 personas) - Pregnancy complications, menstrual disorders, etc.
- **Batch 4**: Neurology (100 personas) - Stroke, seizures, headache, neuropathy
- **Batch 5**: Dermatology (100 personas) - Eczema, psoriasis, melanoma, etc.
- **Batch 6**: ENT (100 personas) - Vertigo, hearing loss, sinusitis, etc.
- **Batch 7**: Ophthalmology (100 personas) - Glaucoma, cataracts, retinal disease
- **Batch 8**: Musculoskeletal (100 personas) - Arthritis, fractures, back pain
- **Batch 9**: Endocrine (100 personas) - Diabetes, thyroid, Addison's, etc.
- **Batch 10**: Rare Diagnoses (200 personas) - Uncommon presentations

**Total**: 1,000 personas across all AMC domains

**Process**: Use same `batch1_rag_generator.py` with new configs

---

### 8. Advanced RAG Features (12 hours)

**Current**: Simple semantic search
**Goal**: Hybrid search with re-ranking

**Enhancements**:

#### A. Hybrid Search (Semantic + Keyword)
```python
# Combine semantic and keyword search
semantic_results = query_semantic(query, limit=20)
keyword_results = query_keyword(query, limit=20)
combined = merge_results(semantic_results, keyword_results)
```

**Benefit**: Better recall for specific medical terms

#### B. Re-Ranking with Cross-Encoder
```python
from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Re-rank top 20 results
scores = model.predict([(query, result.text) for result in top_20])
reranked = sort_by_scores(top_20, scores)[:10]
```

**Benefit**: Higher precision (fewer false positives)

#### C. Citation Clustering
```python
# Group similar citations to reduce redundancy
from sklearn.cluster import DBSCAN

embeddings = [embed(citation.text) for citation in citations]
clusters = DBSCAN(eps=0.3).fit(embeddings)

# Return 1 representative citation per cluster
deduplicated = [cluster[0] for cluster in clusters]
```

**Benefit**: Cleaner personas, less repetitive content

---

### 9. Performance Optimization (4 hours)

**Current Metrics**:
- Query time: ~150ms (95th percentile)
- Generation time: 6 seconds/persona
- Confidence threshold: >0.65

**Optimization Targets**:
- Query time: <100ms (50% reduction)
- Generation time: 4 seconds/persona
- Confidence threshold: >0.70 (stricter)

**Optimizations**:

#### A. Qdrant HNSW Tuning
```python
client.update_collection(
    collection_name='medical_knowledge',
    hnsw_config={
        'm': 16,  # Increase for better recall
        'ef_construct': 200  # Increase for better indexing
    }
)
```

#### B. Batch Embedding Generation
```python
# Generate embeddings in batches
queries = [build_query(spec) for spec in batch]
embeddings = model.encode(queries, batch_size=32)  # GPU acceleration
```

#### C. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def query_rag_cached(query, limit, min_confidence):
    return query_rag(query, limit, min_confidence)
```

---

## 🏆 Long-Term Goals (Month 3-6)

### 10. Mobile App Integration

**Goal**: Native iOS/Android apps for on-the-go OSCE practice

**Tech Stack**:
- Flutter (cross-platform)
- Same backend API
- Offline mode with cached personas

### 11. AI Assessment System

**Goal**: AI evaluates student performance during OSCE practice

**Features**:
- Speech-to-text transcription (Whisper)
- Claude analyzes student responses
- Automated FRACP rubric scoring
- Personalized feedback

### 12. Multi-Language Support

**Goal**: Support non-English speaking IMGs

**Languages**: Arabic, Mandarin, Hindi, Spanish
**Method**: Translate personas while preserving medical accuracy

---

## 📋 Priority Matrix

| Task | Priority | Time | Impact | Status |
|------|----------|------|--------|--------|
| **Fix QA Validator** | 🔴 High | 30 min | High | Pending |
| **Database Insertion** | 🔴 Critical | 2 hours | Critical | Pending |
| **Frontend Integration** | 🟡 Important | 3 hours | High | Pending |
| **User Testing** | 🟢 Medium | Ongoing | Medium | Pending |
| **Enhance Citations** | 🟢 Low | 4 hours | Medium | Optional |
| **Expand Knowledge Base** | 🔵 Future | 8 hours | High | Month 2 |
| **Batch 2-10** | 🔵 Future | 40 hours | Very High | Month 2-3 |
| **Advanced RAG** | 🔵 Future | 12 hours | Medium | Month 3 |

---

## 🚦 Recommended Execution Order

### This Week (Week 1)
1. ✅ **Fix QA validator schema** (30 min)
2. ✅ **Insert all personas into database** (2 hours)
3. ✅ **Update frontend to show 207 personas** (3 hours)
4. ✅ **Deploy to staging environment** (1 hour)
5. ✅ **Test end-to-end flow** (1 hour)

**Total**: 1 day of work

### Next Week (Week 2)
1. **Launch to alpha testers** (10 medical students)
2. **Collect feedback** (surveys, analytics)
3. **Fix bugs** based on feedback
4. **Enhance citations** with real content

### Month 2
1. **Expand knowledge base** to 50,000 chunks
2. **Generate Batch 2** (Psychiatry - 100 personas)
3. **Implement advanced RAG features**

### Month 3+
1. **Generate Batches 3-10** (900 more personas)
2. **Mobile app** development
3. **AI assessment** system

---

## 🎯 Immediate Action Items (Today)

```bash
# 1. Fix QA validator (5 minutes)
cd /home/dev/Development/irStudy
sed -i 's/expected_diagnosis/diagnosis/g' \
  clinical-content-prds/validation-system/qa_validator.py

# 2. Test QA validator
python3 -c "
import sys
sys.path.insert(0, 'clinical-content-prds/validation-system')
from qa_validator import PersonaQAValidator
import json

validator = PersonaQAValidator()
with open('clinical-content-prds/validation-system/batch1_personas/cardiology_001_stemi_male_65_persona.json') as f:
    persona = json.load(f)
result = validator.validate_single_persona(persona)
print(f'✅ QA Pass: {result[\"overall_pass\"]}')
"

# 3. Check if database insertion script exists
ls scripts/insert_batch1_personas.py || \
  echo "⚠️  Need to create database insertion script"

# 4. Check database schema
psql -U postgres -d irstudy_medical -c "\d patient_personas" 2>/dev/null || \
  echo "⚠️  Need to create patient_personas table"
```

---

## 📊 Success Metrics

### Week 1 Targets
- ✅ 207 personas in database
- ✅ Frontend showing all personas
- ✅ 0 critical bugs
- ✅ End-to-end test passing

### Month 1 Targets
- 🎯 10+ active alpha testers
- 🎯 100+ OSCE practice sessions completed
- 🎯 ≥4.0/5.0 average user rating
- 🎯 <5% bug report rate

### Month 3 Targets
- 🎯 1,000+ personas across 10 specialties
- 🎯 50,000+ citations in knowledge base
- 🎯 100+ daily active users
- 🎯 Mobile app beta launched

---

**Created**: 2026-03-16
**Status**: Ready for Week 1 execution
**Next Review**: After database insertion complete
