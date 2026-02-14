# Medical Resources RAG Pipeline - User Guide

## Overview

This guide will help you index your medical resources into a searchable vector database using the RAG (Retrieval-Augmented Generation) pipeline.

## Prerequisites

✓ Python 3.11+ installed
✓ Docker installed and running
✓ Virtual environment activated
✓ RAG system setup complete (Qdrant + PubMedBERT)

## Quick Start

### 1. Activate Virtual Environment

```bash
cd /home/dev/Development/irStudy
source venv/bin/activate
```

### 2. Verify Setup

Check that Qdrant is running:

```bash
curl http://localhost:6333/collections
```

You should see a JSON response with collections.

### 3. Run the Pipeline

#### Option A: Process Everything (Recommended for first run)

Process all PDFs from your medical resources:

```bash
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/
```

This will:
- Extract all PDFs to structured text
- Chunk texts intelligently (preserving medical context)
- Generate 768-dimensional PubMedBERT embeddings
- Index to Qdrant vector database

**Estimated time**: 2-6 hours depending on number of PDFs and CPU speed

#### Option B: Test with Small Subset (Recommended for testing)

Test with first 10 PDFs:

```bash
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/ \
  --limit 10
```

**Estimated time**: 5-15 minutes

### 4. Test Your Search

Once indexing is complete, test semantic search:

```bash
# Basic search
python3 scripts/test_rag_search.py \
  --query "acute myocardial infarction diagnosis"

# Get more results
python3 scripts/test_rag_search.py \
  --query "diabetes management" \
  --limit 10

# Filter by source
python3 scripts/test_rag_search.py \
  --query "hypertension treatment guidelines" \
  --source australian_guidelines
```

## Advanced Usage

### Run Specific Pipeline Steps

If you already have processed some steps:

```bash
# Only extract PDFs (Step 1)
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/ \
  --steps 1

# Only generate embeddings and index (Steps 3-4)
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/ \
  --steps 3,4
```

### Use Custom Collection Name

Create separate collections for different resource types:

```bash
# Cochrane-only collection
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/cochrane/ \
  --collection cochrane_reviews

# StatPearls-only collection
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/statpearls/ \
  --collection statpearls_textbooks
```

### Incremental Updates

To add new resources without reprocessing everything:

```bash
# 1. Extract new PDFs only
python3 scripts/extract_pdfs.py --input /path/to/new/pdfs --output data/processed

# 2. Re-chunk all texts (includes new ones)
python3 scripts/chunk_medical_texts.py \
  --input data/processed \
  --output data/chunks.json

# 3. Generate embeddings for all chunks
python3 scripts/generate_embeddings.py \
  --input data/chunks.json \
  --output data/embeddings/medical_embeddings.pkl

# 4. Re-index to Qdrant (will replace collection)
python3 scripts/index_qdrant.py \
  --embeddings data/embeddings/medical_embeddings.pkl \
  --collection medical_knowledge
```

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Medical Resources                           │
│  (PDFs: Cochrane, StatPearls, NSW Health, etc.)                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: PDF Extraction                                          │
│ ─────────────────────────────────────────────────────────────── │
│ • PyMuPDF for text extraction                                   │
│ • OCR for scanned pages (Tesseract)                             │
│ • Preserve tables, drug info, lists                             │
│ • Output: data/processed/*.json                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Intelligent Chunking                                    │
│ ─────────────────────────────────────────────────────────────── │
│ • Chunk size: ~1000 tokens                                      │
│ • Overlap: 150 tokens for context                               │
│ • Preserve medical context (don't split tables, drug info)      │
│ • Output: data/chunks.json                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Embedding Generation                                    │
│ ─────────────────────────────────────────────────────────────── │
│ • Model: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract  │
│ • Embedding dimension: 768                                      │
│ • Batch processing for efficiency                               │
│ • Output: data/embeddings/medical_embeddings.pkl                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Vector Database Indexing                                │
│ ─────────────────────────────────────────────────────────────── │
│ • Qdrant vector database                                        │
│ • Cosine similarity search                                      │
│ • Metadata filters (source, page, category)                     │
│ • Collection: medical_knowledge                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Output Files

```
data/
├── processed/           # Extracted PDF text (JSON format)
│   ├── document1.json
│   ├── document2.json
│   └── ...
├── chunks.json         # Chunked texts with metadata
├── embeddings/
│   ├── medical_embeddings.pkl        # Full embeddings
│   └── embeddings_sample.json        # First 10 for inspection
└── logs/
    └── rag/            # Processing logs
```

## Monitoring Progress

### View Qdrant Dashboard

Open in browser: http://localhost:6333/dashboard

### Check Collection Status

```bash
# List all collections
curl http://localhost:6333/collections | jq

# Get specific collection info
curl http://localhost:6333/collections/medical_knowledge | jq
```

### View Processing Logs

The pipeline provides real-time progress updates:

```
================================================================================
MEDICAL RESOURCES RAG PIPELINE
================================================================================
Running steps: [1, 2, 3, 4]

================================================================================
STEP 1: Extracting PDFs
================================================================================
Found 1247 PDF files
  cochrane: 892 PDFs
  statpearls: 234 PDFs
  nsw_health: 67 PDFs
  ...

Processing: CD000011_interventions_for_enhancing_medication_adherence.pdf
✓ Extracted 45 pages

...
```

## Troubleshooting

### "No PDFs found to process"

Check that your input directory exists and contains PDFs:

```bash
ls -la /mnt/data/medical_resources/
find /mnt/data/medical_resources/ -name "*.pdf" | head
```

### "Cannot import MedicalPDFExtractor"

Make sure you're running from the project root and the scripts are in the right location:

```bash
cd /home/dev/Development/irStudy
ls scripts/*.py
```

### "Qdrant connection failed"

Make sure Qdrant is running:

```bash
docker ps | grep qdrant
# If not running:
docker start qdrant
```

### "Out of memory"

Reduce batch size:

```bash
python3 scripts/generate_embeddings.py \
  --input data/chunks.json \
  --output data/embeddings/medical_embeddings.pkl \
  --batch-size 8
```

### "CUDA not available" warnings

This is normal if you don't have a GPU. The pipeline will use CPU (slower but works fine):

```
Using device: cpu
```

For GPU acceleration, install PyTorch with CUDA support.

## Performance Optimization

### Use GPU (if available)

```bash
# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Run with GPU
python3 scripts/generate_embeddings.py \
  --input data/chunks.json \
  --output data/embeddings/medical_embeddings.pkl \
  --device cuda
```

### Parallel Processing

Process different sources in parallel:

```bash
# Terminal 1: Cochrane
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/cochrane/ \
  --collection cochrane_reviews &

# Terminal 2: StatPearls
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/statpearls/ \
  --collection statpearls &

wait
```

### Batch Processing

For very large datasets, process in batches:

```bash
# First 100 PDFs
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/ \
  --limit 100

# Check results, then process more
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/ \
  --limit 500
```

## Maintenance

### Update Embeddings

When you add new medical resources:

```bash
# Full re-index (recommended if many changes)
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/

# Or incremental (see "Incremental Updates" above)
```

### Backup Collections

```bash
# Export collection
docker exec qdrant sh -c "cd /qdrant/storage && tar czf /tmp/medical_knowledge_backup.tar.gz collections/medical_knowledge"

# Copy backup out
docker cp qdrant:/tmp/medical_knowledge_backup.tar.gz ./backups/
```

### Clear and Restart

```bash
# Delete collection
curl -X DELETE http://localhost:6333/collections/medical_knowledge

# Re-index
python3 scripts/embed_medical_resources.py \
  --input /mnt/data/medical_resources/ \
  --steps 4
```

## Integration with Your Workflow

### Use in Python Scripts

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Initialize
client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")

# Search
query = "How to diagnose acute appendicitis?"
query_embedding = model.encode(query).tolist()

results = client.search(
    collection_name="medical_knowledge",
    query_vector=query_embedding,
    limit=5
)

for result in results:
    print(f"Source: {result.payload['source']}")
    print(f"Page: {result.payload['page']}")
    print(f"Text: {result.payload['text'][:200]}...")
    print(f"Score: {result.score}\n")
```

### Use with Medical Agents

The RAG system integrates with your existing medical expert agents:

```python
# In your agent code
from src.llm.rag_retrieval import retrieve_medical_context

context = retrieve_medical_context(
    query="acute myocardial infarction management",
    limit=3,
    source_filter="australian_guidelines"
)

# Use context in your prompt
prompt = f"""
Based on these medical guidelines:

{context}

Answer the following question: {user_question}
"""
```

## Next Steps

1. **Test the pipeline** with a small subset (--limit 10)
2. **Verify search results** are relevant and accurate
3. **Run full indexing** of all medical resources
4. **Integrate with your medical agents** for citation-backed responses
5. **Set up weekly updates** to keep knowledge base current

## Support

For issues or questions:
1. Check logs in `logs/rag/`
2. Review troubleshooting section above
3. Verify all prerequisites are met
4. Check Qdrant dashboard for collection status

---

**Last Updated**: 2026-01-18
**Version**: 1.0
