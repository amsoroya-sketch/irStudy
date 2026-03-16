# Testing Instructions: RAG-Integrated Persona Generator

**File**: `persona_rag_generator.py`
**Created**: 2026-03-16

---

## Quick Start Test

```bash
cd /home/dev/Development/irStudy
source venv_validation/bin/activate

# Run example generation
python clinical-content-prds/validation-system/persona_rag_generator.py
```

**Expected Output**:
```
=== Qdrant Health Check ===
{
  "healthy": true,
  "qdrant_connected": true,
  "total_chunks": 9950,
  "australian_boost_active": true,
  "collection": "medical_knowledge"
}

=== Generating Example Persona: Anaphylaxis ===
✓ symptoms: 10/10 chunks above 0.65 confidence
✓ management: 10/10 chunks above 0.75 confidence
✓ investigations: 5/5 chunks above 0.70 confidence
✓ critical_errors: 5/5 chunks above 0.80 confidence
✓ diagnosis: 5/5 chunks above 0.75 confidence
✓ Retrieved 35 RAG chunks across 5 sections
✓ Generated context bundle: 9047 chars
✓ Persona generated: emergency_001_anaphylaxis_peanut_allergy_female_28
✓ Persona saved to: example_rag_persona.json

=== Persona Summary ===
ID: emergency_001_anaphylaxis_peanut_allergy_female_28
Name: Sarah Chen
Diagnosis: Anaphylaxis (peanut allergy)
Symptoms: 5
Management steps: 10
Critical errors: 5
Total RAG citations: 5

=== Example Symptom with RAG Citation ===
Symptom: [symptom text from RAG]
Citation: John Murtagh General Practice (John Murtagh, 2020)
Page: [page number]
Confidence: [0.65-1.0]
Qdrant Point ID: [UUID]
```

---

## Verification Tests

### Test 1: Citation Traceability

```bash
# Extract a citation from generated persona
POINT_ID=$(jq -r '.symptoms[0].rag_citations[0].qdrant_point_id' example_rag_persona.json)

# Verify it exists in Qdrant
python << EOF
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
point = client.retrieve("medical_knowledge", ids=["$POINT_ID"])

if point:
    print(f"✓ Citation verified in Qdrant")
    print(f"Source: {point[0].payload.get('source')}")
    print(f"Page: {point[0].payload.get('page')}")
else:
    print(f"✗ FAILED: Citation not found (hallucination!)")
    exit(1)
