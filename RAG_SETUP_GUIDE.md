# RAG System Setup Guide

## Quick Start (15-20 minutes)

### 1. Run the Setup Script

```bash
cd /home/dev/Development/irStudy
bash scripts/setup_rag_system.sh
```

**What it does:**
- ✅ Checks Python 3.11+ and Docker
- ✅ Creates/activates virtual environment
- ✅ Installs all Python dependencies (~10-15 min)
- ✅ Starts Qdrant vector database in Docker
- ✅ Downloads PubMedBERT embedding model (~420 MB)
- ✅ Tests everything works

---

## What Gets Installed

### Python Packages
- **qdrant-client** (1.7.3) - Vector database client
- **sentence-transformers** (2.3.1) - Text embeddings
- **torch** (2.1.2) - Deep learning framework
- **transformers** (4.37.2) - NLP models
- Plus ~40 other dependencies from requirements.txt

### Docker Services
- **Qdrant** - Vector database for semantic search
  - Web UI: http://localhost:6333/dashboard
  - API: http://localhost:6333

### AI Models
- **PubMedBERT** - Medical text embeddings (420 MB)
  - Model: `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext`
  - Creates 768-dimensional embeddings

---

## After Installation

### Activate Virtual Environment
```bash
source venv/bin/activate
```

### Check Services
```bash
# Check Qdrant is running
curl http://localhost:6333/collections

# View Qdrant dashboard
# Open browser: http://localhost:6333/dashboard

# Check Docker container
docker ps | grep qdrant
```

---

## Next Steps

### 1. Process Your Medical Resources (30-60 min)

Create embeddings from your downloaded PDFs and documents:

```bash
# This script needs to be created - it will:
# - Extract text from PDFs
# - Chunk text into manageable pieces
# - Generate embeddings using PubMedBERT
# - Save to embeddings/medical_embeddings.pkl

python3 scripts/embed_medical_resources.py \
    --input /mnt/data/medical_resources/ \
    --output embeddings/medical_embeddings.pkl
```

**Note:** You have 2.2 GB of resources (2,788+ files). Processing will take time.

---

### 2. Index to Qdrant (10-20 min)

Upload embeddings to vector database:

```bash
python3 scripts/index_qdrant.py \
    --embeddings embeddings/medical_embeddings.pkl \
    --collection medical_knowledge
```

---

### 3. Test RAG Search

```bash
python3 scripts/test_rag_search.py \
    --query "diagnostic criteria for acute myocardial infarction" \
    --top-k 5
```

**Expected output:**
```
Top 5 Results:
1. [Score: 0.89] StatPearls - Myocardial Infarction (Page 3)
2. [Score: 0.85] Cochrane - ACS Diagnosis (Page 12)
3. [Score: 0.82] RANZCOG - Cardiac Events (Page 45)
...
```

---

## Troubleshooting

### Installation Issues

**"Docker not found"**
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
# Logout and login again
```

**"Qdrant failed to start"**
```bash
# Check Docker logs
docker logs qdrant

# Restart Qdrant
docker restart qdrant

# Check port 6333 is free
sudo netstat -tlnp | grep 6333
```

**"Model download fails"**
```bash
# Manually download PubMedBERT
python3 -c "
from sentence_transformers import SentenceTransformer
import os
model = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')
cache_dir = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'hub')
print('Downloaded to:', cache_dir)
"
```

### Resource Issues

**"Not enough disk space"**
- Requirements: ~5 GB for dependencies + embeddings
- Check: `df -h`
- PubMedBERT model: 420 MB
- PyTorch: ~800 MB
- Other dependencies: ~2 GB

**"Out of memory during embedding"**
- Reduce batch size in embed_medical_resources.py
- Process in smaller chunks
- Use swap space

---

## Managing Qdrant

### Start/Stop
```bash
# Stop Qdrant
docker stop qdrant

# Start Qdrant
docker start qdrant

# Restart Qdrant
docker restart qdrant

# Remove Qdrant (preserves data)
docker stop qdrant && docker rm qdrant

# Completely remove (deletes data)
docker stop qdrant && docker rm qdrant && rm -rf qdrant_storage/
```

### Backup Data
```bash
# Qdrant stores data in ./qdrant_storage/
tar -czf qdrant_backup_$(date +%Y%m%d).tar.gz qdrant_storage/
```

### View Collections
```bash
# List collections
curl http://localhost:6333/collections

# Collection info
curl http://localhost:6333/collections/medical_knowledge

# Count vectors
curl http://localhost:6333/collections/medical_knowledge/points/count
```

---

## File Structure After Setup

```
irStudy/
├── venv/                          # Virtual environment
├── qdrant_storage/                # Qdrant database files
├── embeddings/                    # Generated embeddings
│   └── medical_embeddings.pkl
├── logs/rag/                      # RAG system logs
├── validation_reports/            # Validation results
├── scripts/
│   ├── setup_rag_system.sh       # Setup script (you just ran)
│   ├── embed_medical_resources.py # Process PDFs → embeddings
│   ├── index_qdrant.py           # Upload to Qdrant
│   └── test_rag_search.py        # Test search
└── requirements.txt               # Python dependencies
```

---

## Performance Tips

### Faster Embeddings
- Use GPU if available (install `torch` with CUDA)
- Process in parallel (set `--workers` flag)
- Use smaller batch sizes for stability

### Faster Search
- Limit search to specific collections
- Use filters (source, date, specialty)
- Adjust `top-k` results

### Resource Usage
- Qdrant: ~500 MB RAM + vector data size
- Embedding model: ~1.5 GB RAM during encoding
- Total for 2.2 GB docs: ~3-4 GB RAM

---

## What's Next?

After setup completes:

1. **Wait for StatPearls download to finish** (~12 hours remaining)
2. **Process all medical resources** into embeddings
3. **Index to Qdrant** for semantic search
4. **Integrate with medical agents** for RAG-powered MCQ generation
5. **Validate citations** are accurate with page numbers

---

## Support

**Check logs:**
```bash
# Setup log
cat logs/rag/setup_*.log

# Qdrant logs
docker logs qdrant

# Embedding logs
cat logs/rag/embedding_*.log
```

**Test individual components:**
```bash
# Test Qdrant
python3 -c "from qdrant_client import QdrantClient; c = QdrantClient('http://localhost:6333'); print(c.get_collections())"

# Test PubMedBERT
python3 -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext'); print('OK')"
```

---

**Installation Time:** 15-20 minutes
**Disk Space Required:** ~5 GB
**RAM Required:** 4-8 GB (8 GB recommended)
