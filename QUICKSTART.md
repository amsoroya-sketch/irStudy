# Quick Start Guide
## Get the Medical Education AI System Running in 1 Hour

---

## ⚡ Super Quick Setup (If You Have PDFs Ready)

```bash
# 1. Run automated setup (10-15 minutes)
./setup.sh

# 2. Place PDFs in data/pdfs/ folder

# 3. Process everything (2-4 hours total)
python scripts/extract_pdfs.py
python scripts/chunk_medical_texts.py
python scripts/generate_embeddings.py
python scripts/index_qdrant.py

# 4. Test the system
python src/models/ollama_client.py
```

**Done!** Your medical knowledge base is now ready.

---

## 📋 Detailed Step-by-Step

### Step 1: Run Setup Script (10-15 min)

```bash
cd /home/dev/Development/irStudy
./setup.sh
```

This will:
- ✅ Check all prerequisites (Python, Docker, GPU, Ollama)
- ✅ Create virtual environment
- ✅ Install all Python packages
- ✅ Install Tesseract OCR
- ✅ Download Ollama models (meditron, biomistral, llama3.1, mixtral)
- ✅ Start Docker services (Qdrant, Neo4j, PostgreSQL, Redis, etc.)

### Step 2: Add Medical Textbooks (Manual)

Place your PDF files in the correct folders:

```
data/pdfs/
├── australian/
│   ├── therapeutic_guidelines_etg.pdf
│   ├── murtaghs_general_practice_8ed.pdf
│   ├── talley_clinical_examination_9ed.pdf
│   └── australian_medicines_handbook.pdf
├── core/
│   ├── harrisons_internal_medicine_21ed.pdf
│   ├── kumar_clark_10ed.pdf
│   └── davidsons_24ed.pdf
└── specialties/
    ├── nelson_pediatrics_21ed.pdf
    ├── williams_obstetrics_26ed.pdf
    ├── bailey_love_surgery_28ed.pdf
    └── kaplan_sadock_psychiatry_12ed.pdf
```

**Where to get PDFs:**
- 📚 Purchase from Amazon, Book Depository
- 🏛️ University/hospital library (free access)
- 📖 Library Genesis, Z-Library (gray area)

### Step 3: Extract Text from PDFs (30-60 min)

```bash
# Activate virtual environment
source venv/bin/activate

# Extract all PDFs
python scripts/extract_pdfs.py

# Expected output:
# Found 20 PDF files to process
# Processing PDFs: 100%
# ✓ Extracted 35,000+ pages, 12,000,000+ words
```

### Step 4: Chunk Medical Texts (10-20 min)

```bash
python scripts/chunk_medical_texts.py

# Expected output:
# Found 20 books to chunk
# Chunking books: 100%
# ✓ Chunking complete!
#   Total chunks: 40,000
#   Total words: 12,000,000
```

### Step 5: Generate Embeddings (2-4 hours)

```bash
# This uses your NVIDIA GPU for fast processing
python scripts/generate_embeddings.py

# Expected output:
# Using device: cuda
# Loading model: pritamdeka/S-PubMedBert-MS-MARCO
# Embedding dimension: 768
# Loaded 40,000 chunks
# Generating embeddings (batch_size=32): 100%
# ✓ Embedding generation complete!
#   File size: 485 MB
```

**💡 Tip:** This runs on your GPU. You can do other work while it processes.

### Step 6: Index in Qdrant (20-40 min)

```bash
python scripts/index_qdrant.py

# Expected output:
# Connected to Qdrant at http://localhost:6333
# ✓ Created collection 'medical_knowledge'
# Uploading 40,000 points in batches of 100
# Uploading batches: 100%
# ✓ Upload complete!
#   Collection now has 40,000 points
```

### Step 7: Test the System! 🎉

```bash
# Test local LLM
python src/models/ollama_client.py

# Test search with a real query
python scripts/index_qdrant.py --test
```

---

## ✅ Verification Checklist

Run these commands to verify everything works:

```bash
# 1. Check Ollama models
ollama list
# Should show: meditron:7b, biomistral:7b, llama3.1:70b, mixtral:8x7b

# 2. Check Docker services
docker-compose ps
# All services should be "Up"

# 3. Check Qdrant
curl http://localhost:6333/collections
# Should show "medical_knowledge" collection

# 4. Check GPU
nvidia-smi
# Should show your GPU

# 5. Test Python imports
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
# Should print: CUDA available: True
```

---

## 🌐 Access Your Services

After setup, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Qdrant Dashboard** | http://localhost:6333/dashboard | None |
| **Neo4j Browser** | http://localhost:7474 | neo4j / medical_ai_password_2025 |
| **Grafana** | http://localhost:3001 | admin / medical_admin_2025 |
| **Prometheus** | http://localhost:9090 | None |

---

## 🧪 Quick Tests

### Test 1: Search Medical Knowledge

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Connect
client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

# Search
query = "treatment of acute coronary syndrome"
query_vec = model.encode(query).tolist()

results = client.search(
    collection_name="medical_knowledge",
    query_vector=query_vec,
    limit=3
)

for r in results:
    print(f"Score: {r.score:.3f} | Source: {r.payload['source']}")
    print(f"Text: {r.payload['text'][:200]}...\n")
```

### Test 2: Generate with Local LLM

```python
from src.models.ollama_client import OllamaClient

client = OllamaClient()

response = client.generate(
    prompt="What are the key features of acute coronary syndrome?",
    model_name="meditron:7b"
)

print(response)
```

---

## 🚨 Troubleshooting

### "Ollama not found"
```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl start ollama
```

### "CUDA not available"
```bash
# Check NVIDIA drivers
nvidia-smi

# If not working, install CUDA:
# https://developer.nvidia.com/cuda-downloads
```

### "Docker service failed to start"
```bash
# Check logs
docker-compose logs qdrant

# Restart
docker-compose down
docker-compose up -d
```

### "Out of memory during embeddings"
```bash
# Reduce batch size
python scripts/generate_embeddings.py --batch-size 16
```

### "Permission denied on setup.sh"
```bash
chmod +x setup.sh
./setup.sh
```

---

## ⏱️ Time Estimates

| Task | Time | Can Skip? |
|------|------|-----------|
| Run setup.sh | 10-15 min | ❌ Required |
| Acquire PDFs | Manual | ❌ Required |
| Extract PDFs | 30-60 min | ❌ Required |
| Chunk texts | 10-20 min | ❌ Required |
| Generate embeddings | 2-4 hours | ❌ Required |
| Index Qdrant | 20-40 min | ❌ Required |
| **TOTAL** | **4-6 hours** | |

**Most time is GPU processing** - you can work on other things during embeddings!

---

## 🎯 What You Get After Setup

- ✅ **40,000+ medical knowledge chunks** indexed and searchable
- ✅ **4 local medical LLMs** ready to use (no API costs)
- ✅ **Semantic search** across 20 medical textbooks
- ✅ **Infrastructure** ready for building AI agents
- ✅ **Zero monthly costs** (all self-hosted)

---

## 📝 Next Steps

After completing this quick start:

1. **Build RAG query system** - Create intelligent medical Q&A
2. **Create first AI agent** - Medical expert agent using local LLM
3. **Generate test questions** - Auto-generate MCQs
4. **Build multi-agent system** - 28 specialized medical agents
5. **Create web interface** - FastAPI + Next.js platform

See main README.md for detailed development roadmap.

---

## 💡 Pro Tips

1. **Start small:** Process 5 textbooks first, verify quality, then do all 20
2. **Monitor GPU:** Watch `nvidia-smi` during embedding generation
3. **Backup embeddings:** Copy `data/embeddings/` - takes hours to regenerate
4. **Use screen/tmux:** For long-running processes
5. **Check logs:** `docker-compose logs -f` to watch all services

---

**Questions?** Check the main README.md or create an issue.

**Ready to start!** 🚀
