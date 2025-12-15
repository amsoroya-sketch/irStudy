# AI-Powered Medical Education System
## ICRP + AMC MCQ + AMC Clinical Preparation

A comprehensive, AI-powered platform for medical exam preparation using local LLMs, RAG, and multi-agent systems.

---

## 🎯 Project Overview

This system provides:
- **ICRP (Young Hospital, NSW)** preparation materials
- **AMC MCQ (CAT)** comprehensive question bank and study materials
- **AMC Clinical (OSCE)** scenario simulation and practice

### Key Features:
- ✅ **100% Self-Hosted** - No cloud costs, no API fees
- ✅ **Local LLMs** - Uses Ollama with medical-specific models
- ✅ **RAG System** - Semantic search across 20+ medical textbooks
- ✅ **Multi-Agent AI** - Specialized agents for each medical specialty
- ✅ **Unlimited Content** - AI generates questions on-demand
- ✅ **Australian-Focused** - Therapeutic Guidelines, NSW protocols, AMC format

---

## 📋 Prerequisites

### System Requirements:
- **OS:** Linux (Ubuntu 20.04+ recommended)
- **GPU:** NVIDIA GPU with CUDA support (for local LLM inference)
- **RAM:** 32GB+ recommended (16GB minimum)
- **Storage:** 100GB+ free space
- **Python:** 3.11+
- **Docker:** Latest version

### Software:
- Ollama (for local LLMs)
- Docker & Docker Compose
- NVIDIA CUDA drivers
- Tesseract OCR (for scanned PDFs)

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd irStudy
```

### 2. Install Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
sudo apt-get install tesseract-ocr
```

### 3. Download Additional Ollama Models
```bash
# Medical-specific models
ollama pull meditron:7b          # Medical expert
ollama pull biomistral:7b        # Biomedical LLM
ollama pull llama3.1:70b         # Best reasoning
ollama pull mixtral:8x7b         # Question generation

# Verify installation
ollama list
```

### 4. Start Infrastructure Services
```bash
# Start Qdrant, Neo4j, PostgreSQL, Redis, Prometheus, Grafana
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### 5. Acquire Medical Textbooks (PDF)
Place your medical textbook PDFs in the following structure:
```
data/pdfs/
├── australian/
│   ├── therapeutic_guidelines_etg.pdf
│   ├── murtaghs_general_practice_8ed.pdf
│   ├── talley_clinical_examination_9ed.pdf
│   └── amh_australian_medicines_handbook.pdf
├── core/
│   ├── harrisons_internal_medicine_21ed.pdf
│   ├── kumar_clark_clinical_medicine_10ed.pdf
│   └── davidsons_medicine_24ed.pdf
├── specialties/
│   ├── nelson_pediatrics_21ed.pdf
│   ├── williams_obstetrics_26ed.pdf
│   ├── bailey_love_surgery_28ed.pdf
│   └── kaplan_sadock_psychiatry_12ed.pdf
└── free/
    └── statpearls.pdf
```

---

## 📚 Processing Medical Textbooks

### Step 1: Extract Text from PDFs
```bash
# Extract text from all PDFs (handles OCR for scanned pages)
python scripts/extract_pdfs.py \
    --input data/pdfs \
    --output data/processed

# This will create JSON files in data/processed/
# Expected time: 1-3 hours for 20 books
```

### Step 2: Chunk Medical Texts
```bash
# Intelligently chunk texts while preserving medical context
python scripts/chunk_medical_texts.py \
    --input data/processed \
    --output data/chunks.json \
    --chunk-size 1000 \
    --overlap 150

# Expected output: 30,000-50,000 chunks
# Expected time: 10-30 minutes
```

### Step 3: Generate Embeddings
```bash
# Generate PubMedBERT embeddings (using local GPU)
python scripts/generate_embeddings.py \
    --input data/chunks.json \
    --output data/embeddings/medical_embeddings.pkl \
    --model pritamdeka/S-PubMedBert-MS-MARCO \
    --batch-size 32

# Expected time: 2-4 hours for 40,000 chunks on GPU
# File size: ~500MB
```

### Step 4: Index in Qdrant
```bash
# Upload embeddings to Qdrant vector database
python scripts/index_qdrant.py \
    --embeddings data/embeddings/medical_embeddings.pkl \
    --collection medical_knowledge \
    --qdrant-url http://localhost:6333 \
    --batch-size 100

# Verify indexing with test search
python scripts/index_qdrant.py --test

# Expected time: 20-40 minutes
```

---

## 🧪 Testing the System

### Test Local LLM Integration
```bash
python src/models/ollama_client.py
```

### Test RAG Search
```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Connect to Qdrant
client = QdrantClient(url="http://localhost:6333")

# Load embedding model
model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

# Search medical knowledge
query = "Management of acute coronary syndrome"
query_embedding = model.encode(query).tolist()

results = client.search(
    collection_name="medical_knowledge",
    query_vector=query_embedding,
    limit=5
)

for result in results:
    print(f"Score: {result.score:.4f}")
    print(f"Source: {result.payload['source']}")
    print(f"Text: {result.payload['text'][:200]}...\n")
```

---

## 📂 Project Structure

```
irStudy/
├── data/
│   ├── pdfs/                    # Medical textbook PDFs (you provide)
│   │   ├── australian/
│   │   ├── core/
│   │   ├── specialties/
│   │   └── free/
│   ├── processed/               # Extracted text (JSON)
│   ├── embeddings/              # Generated embeddings
│   └── chunks.json              # All text chunks
├── scripts/
│   ├── extract_pdfs.py          # PDF text extraction
│   ├── chunk_medical_texts.py   # Text chunking
│   ├── generate_embeddings.py   # Embedding generation
│   └── index_qdrant.py          # Qdrant indexing
├── src/
│   ├── agents/                  # Multi-agent system (TBD)
│   ├── rag/                     # RAG system (TBD)
│   ├── api/                     # FastAPI backend (TBD)
│   └── models/
│       └── ollama_client.py     # Local LLM integration
├── docker/                      # Docker volumes
├── docker-compose.yml           # Infrastructure services
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🔧 Infrastructure Services

### Qdrant (Vector Database)
- **URL:** http://localhost:6333
- **Dashboard:** http://localhost:6333/dashboard
- **Purpose:** Semantic search across medical knowledge

### Neo4j (Knowledge Graph)
- **URL:** http://localhost:7474
- **Username:** neo4j
- **Password:** medical_ai_password_2025
- **Purpose:** Medical entity relationships (diseases, symptoms, treatments)

### PostgreSQL (Relational Database)
- **Host:** localhost:5432
- **Database:** medical_education
- **Username:** medical_user
- **Password:** medical_pass_2025
- **Purpose:** User data, questions, progress tracking

### Redis (Cache & Queue)
- **URL:** localhost:6379
- **Purpose:** Caching, background jobs (Celery)

### Prometheus (Metrics)
- **URL:** http://localhost:9090
- **Purpose:** System metrics collection

### Grafana (Dashboards)
- **URL:** http://localhost:3001
- **Username:** admin
- **Password:** medical_admin_2025
- **Purpose:** Monitoring dashboards

---

## 💰 Cost Analysis

### Development Costs: **$0**
- ✅ Local LLMs (Ollama)
- ✅ Self-hosted infrastructure
- ✅ Open-source software

### Operational Costs: **$0/month**
- ✅ No cloud fees
- ✅ No API costs
- ✅ Electricity only (~$50-100/month)

### Only Real Cost:
- Medical textbooks: **$800-2,000** (one-time)
- OR use free resources: **$0**

---

## 📖 Essential Medical Textbooks

### Must-Have (Top 5):
1. **Therapeutic Guidelines (eTG)** - $385/year
2. **Talley & O'Connor Clinical Examination** - $130
3. **AMC Handbook of MCQs** - $180
4. **Murtagh's General Practice** - $180
5. **Australian Medicines Handbook** - $155

### Comprehensive (20 books):
- See full list in implementation plan
- **Total:** ~$2,000-3,000 (one-time purchase)

### Free Alternatives:
- StatPearls (free comprehensive medical reference)
- NCBI Bookshelf (free medical books)
- PubMed Central (3+ million free articles)
- Australian government guidelines (all free)

---

## 🎯 Next Steps

### Immediate (This Week):
1. ✅ Install all dependencies
2. ✅ Start Docker services
3. ✅ Download Ollama models
4. ⏳ Acquire medical textbook PDFs
5. ⏳ Extract and process PDFs
6. ⏳ Generate embeddings and index in Qdrant

### Short-term (Next 2 Weeks):
- Build RAG query system
- Create first medical expert agent
- Generate test MCQ questions
- Validate with medical professional

### Medium-term (1-2 Months):
- Complete multi-agent system (28 agents)
- Generate 5,000+ MCQs
- Build FastAPI backend
- Create Next.js frontend

### Long-term (3-6 Months):
- 18,000+ MCQs across all exams
- 3,000+ clinical scenarios
- Full platform with adaptive learning
- Beta testing and launch

---

## 🤝 Contributing

This is a personal medical education project. If you're a medical professional interested in validating content or contributing, please reach out!

---

## 📄 License

Private project. All rights reserved.

---

## 🆘 Troubleshooting

### Ollama not responding
```bash
# Check Ollama status
systemctl status ollama

# Restart Ollama
systemctl restart ollama
```

### GPU not detected
```bash
# Check CUDA
nvidia-smi

# Verify PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Docker services not starting
```bash
# Check logs
docker-compose logs <service-name>

# Restart all services
docker-compose down
docker-compose up -d
```

### Out of memory during embedding generation
```bash
# Reduce batch size
python scripts/generate_embeddings.py --batch-size 16
```

---

## 📞 Support

For issues or questions about this project, please create an issue in the repository.

---

**Last Updated:** December 14, 2025
**Version:** 0.1.0-alpha
**Status:** Active Development
