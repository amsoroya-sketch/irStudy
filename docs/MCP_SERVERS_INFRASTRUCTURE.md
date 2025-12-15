# MCP Servers Infrastructure
## Model Context Protocol Servers for Medical AI System

**Last Updated:** December 14, 2025
**Purpose:** Standardized interfaces for medical knowledge access via MCP

**What is MCP?** Model Context Protocol - A standard way for AI agents to access external tools and data sources.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [MCP Server #1: Medical Knowledge Server](#1-medical-knowledge-server)
3. [MCP Server #2: PubMed Search Server](#2-pubmed-search-server)
4. [MCP Server #3: Drug Database Server](#3-drug-database-server)
5. [MCP Server #4: Clinical Guidelines Server](#4-clinical-guidelines-server)
6. [MCP Server #5: Medical Terminology Server](#5-medical-terminology-server)
7. [MCP Server #6: Clinical Calculator Server](#6-clinical-calculator-server)
8. [Setup & Configuration](#setup--configuration)
9. [Integration with Agents](#integration-with-agents)

---

## Overview

### What are MCP Servers?

MCP (Model Context Protocol) servers provide standardized interfaces for AI agents to access:
- Medical knowledge databases
- External APIs
- Clinical tools
- Real-time data sources

### Benefits

✅ **Standardized Interface:** All agents access data the same way
✅ **Modularity:** Add/remove servers independently
✅ **Testability:** Mock servers for testing
✅ **Scalability:** Servers can run on separate machines
✅ **Security:** Centralized access control

### Architecture

```
AI Agents (46 agents)
    ↓
MCP Protocol
    ↓
MCP Servers (6 servers)
    ↓
Data Sources (Qdrant, PostgreSQL, APIs, etc.)
```

---

## 1. Medical Knowledge Server

**Purpose:** Interface to vector database (Qdrant) + knowledge graph (Neo4j)
**Port:** 5001
**Protocol:** HTTP + WebSocket

### Features

- Semantic search across medical textbooks
- Knowledge graph traversal
- Multi-hop reasoning
- Citation retrieval
- Context aggregation

### API Endpoints

```python
# Search medical knowledge
POST /api/search
{
  "query": "acute coronary syndrome management",
  "limit": 10,
  "filters": {
    "specialty": "cardiology",
    "source": "therapeutic_guidelines"
  }
}

# Response
{
  "results": [
    {
      "text": "Acute coronary syndrome management includes...",
      "source": "Therapeutic Guidelines: Cardiovascular",
      "page": 342,
      "score": 0.94,
      "citations": ["eTG 2025, Section 3.2"]
    }
  ],
  "query_time_ms": 450
}

# Knowledge graph query
POST /api/graph/traverse
{
  "start_entity": "Acute Coronary Syndrome",
  "relationship": "TREATED_WITH",
  "hops": 2
}

# Response
{
  "paths": [
    ["Acute Coronary Syndrome", "TREATED_WITH", "Aspirin"],
    ["Acute Coronary Syndrome", "TREATED_WITH", "Clopidogrel"],
    ["Aspirin", "INTERACTS_WITH", "Warfarin"]
  ]
}
```

### Implementation

`src/mcp_servers/medical_knowledge_server.py`:

```python
#!/usr/bin/env python3
"""
MCP Server: Medical Knowledge
Provides access to Qdrant vector DB + Neo4j knowledge graph
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import uvicorn

app = FastAPI(title="Medical Knowledge MCP Server")

# Initialize connections
qdrant_client = QdrantClient(url="http://localhost:6333")
embedding_model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "medical_ai_password_2025"))

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    text: str
    source: str
    page: int
    score: float
    citations: List[str]

@app.post("/api/search", response_model=Dict[str, Any])
async def search_medical_knowledge(request: SearchRequest):
    """
    Semantic search across medical knowledge base.

    Example:
        POST /api/search
        {"query": "heart failure management", "limit": 5}
    """
    try:
        # Generate query embedding
        query_vector = embedding_model.encode(request.query).tolist()

        # Search Qdrant
        search_results = qdrant_client.search(
            collection_name="medical_knowledge",
            query_vector=query_vector,
            limit=request.limit,
            query_filter=request.filters
        )

        # Format results
        results = []
        for result in search_results:
            results.append({
                "text": result.payload['text'],
                "source": result.payload['source'],
                "page": result.payload['page'],
                "score": result.score,
                "citations": result.payload.get('citations', [])
            })

        return {
            "results": results,
            "query": request.query,
            "total": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GraphTraversalRequest(BaseModel):
    start_entity: str
    relationship: str
    hops: int = 1

@app.post("/api/graph/traverse")
async def traverse_knowledge_graph(request: GraphTraversalRequest):
    """
    Traverse knowledge graph for medical entity relationships.

    Example:
        POST /api/graph/traverse
        {
          "start_entity": "Diabetes Mellitus",
          "relationship": "TREATED_WITH",
          "hops": 2
        }
    """
    try:
        with neo4j_driver.session() as session:
            # Cypher query for traversal
            query = f"""
            MATCH path = (start:MedicalEntity {{name: $start_entity}})
            -[:{request.relationship}*1..{request.hops}]-(related)
            RETURN path
            LIMIT 50
            """

            result = session.run(query, start_entity=request.start_entity)

            paths = []
            for record in result:
                path = record["path"]
                path_nodes = [node["name"] for node in path.nodes]
                paths.append(path_nodes)

            return {
                "start_entity": request.start_entity,
                "relationship": request.relationship,
                "hops": request.hops,
                "paths": paths
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "qdrant": "connected",
        "neo4j": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
```

---

## 2. PubMed Search Server

**Purpose:** Real-time medical literature search via PubMed API
**Port:** 5002
**Protocol:** HTTP

### Features

- Search PubMed for latest research
- Retrieve article abstracts
- Download full-text from PMC
- Citation extraction
- Literature review automation

### API Endpoints

```python
# Search PubMed
POST /api/pubmed/search
{
  "query": "acute coronary syndrome 2024",
  "max_results": 20,
  "article_type": "Review"
}

# Response
{
  "articles": [
    {
      "pmid": "12345678",
      "title": "Management of Acute Coronary Syndrome: 2024 Update",
      "authors": ["Smith J", "Jones K"],
      "journal": "JAMA",
      "year": 2024,
      "abstract": "...",
      "doi": "10.1001/jama.2024.12345"
    }
  ]
}

# Get full text (if available in PMC)
GET /api/pubmed/fulltext/{pmid}
```

### Implementation

`src/mcp_servers/pubmed_server.py`:

```python
#!/usr/bin/env python3
"""MCP Server: PubMed Search"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from Bio import Entrez
import uvicorn

app = FastAPI(title="PubMed MCP Server")

# Configure Entrez
Entrez.email = "your_email@example.com"  # Required by NCBI

class PubMedSearchRequest(BaseModel):
    query: str
    max_results: int = 20
    article_type: Optional[str] = None  # "Review", "Clinical Trial", etc.

@app.post("/api/pubmed/search")
async def search_pubmed(request: PubMedSearchRequest):
    """Search PubMed for medical literature"""

    # Build search term
    search_term = request.query
    if request.article_type:
        search_term += f" AND {request.article_type}[ptyp]"

    # Search PubMed
    handle = Entrez.esearch(
        db="pubmed",
        term=search_term,
        retmax=request.max_results,
        sort="relevance"
    )
    search_results = Entrez.read(handle)
    handle.close()

    pmids = search_results["IdList"]

    # Fetch article details
    if pmids:
        handle = Entrez.efetch(db="pubmed", id=pmids, rettype="medline", retmode="xml")
        articles_xml = Entrez.read(handle)
        handle.close()

        articles = []
        for article in articles_xml['PubmedArticle']:
            medline = article['MedlineCitation']
            article_data = medline['Article']

            articles.append({
                "pmid": str(medline['PMID']),
                "title": str(article_data['ArticleTitle']),
                "authors": [f"{author.get('LastName', '')} {author.get('Initials', '')}"
                           for author in article_data.get('AuthorList', [])],
                "journal": str(article_data['Journal']['Title']),
                "year": int(article_data['Journal']['JournalIssue']['PubDate'].get('Year', 0)),
                "abstract": str(article_data.get('Abstract', {}).get('AbstractText', [''])[0])
            })

        return {"articles": articles, "total": len(articles)}

    return {"articles": [], "total": 0}

@app.get("/api/pubmed/fulltext/{pmid}")
async def get_fulltext(pmid: str):
    """Get full text from PubMed Central (if available)"""

    # Convert PMID to PMCID
    handle = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pmc")
    links = Entrez.read(handle)
    handle.close()

    if links[0]["LinkSetDb"]:
        pmcid = links[0]["LinkSetDb"][0]["Link"][0]["Id"]

        # Fetch full text from PMC
        handle = Entrez.efetch(db="pmc", id=pmcid, rettype="full", retmode="xml")
        fulltext_xml = handle.read()
        handle.close()

        return {"pmcid": pmcid, "fulltext_xml": fulltext_xml}

    return {"error": "Full text not available in PMC"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)
```

---

## 3. Drug Database Server

**Purpose:** Medication information from RxNorm, DrugBank, Australian Medicines Handbook
**Port:** 5003
**Protocol:** HTTP

### Features

- Drug name lookup
- Dosage information
- Drug interactions
- Contraindications
- PBS information (Australian)

### API Endpoints

```python
# Drug lookup
GET /api/drug/search?name=aspirin

# Response
{
  "drug_name": "Aspirin",
  "generic_name": "Acetylsalicylic Acid",
  "class": "Antiplatelet",
  "indications": ["Acute Coronary Syndrome", "Stroke prevention"],
  "dosage": {
    "adult": "100-300mg daily",
    "pediatric": "Not recommended <16 years"
  },
  "contraindications": ["Active bleeding", "Hemophilia"],
  "pbs_listed": true,
  "pbs_code": "1234"
}

# Drug interactions
POST /api/drug/interactions
{
  "drugs": ["aspirin", "warfarin"]
}

# Response
{
  "interactions": [
    {
      "severity": "major",
      "description": "Increased bleeding risk",
      "recommendation": "Avoid combination or monitor INR closely"
    }
  ]
}
```

### Implementation

```python
#!/usr/bin/env python3
"""MCP Server: Drug Database"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
import uvicorn

app = FastAPI(title="Drug Database MCP Server")

# RxNorm API base URL
RXNORM_API = "https://rxnav.nlm.nih.gov/REST"

@app.get("/api/drug/search")
async def search_drug(name: str):
    """Search for drug information"""

    # Search RxNorm
    response = requests.get(f"{RXNORM_API}/drugs.json?name={name}")
    data = response.json()

    if data.get('drugGroup'):
        drug_info = data['drugGroup']['conceptGroup'][0]['conceptProperties'][0]

        return {
            "drug_name": drug_info['name'],
            "rxcui": drug_info['rxcui'],
            "synonym": drug_info.get('synonym', ''),
            "tty": drug_info['tty']
        }

    return {"error": "Drug not found"}

class DrugInteractionRequest(BaseModel):
    drugs: List[str]

@app.post("/api/drug/interactions")
async def check_interactions(request: DrugInteractionRequest):
    """Check drug-drug interactions"""

    # Get RXCUIs for all drugs
    rxcuis = []
    for drug in request.drugs:
        response = requests.get(f"{RXNORM_API}/rxcui.json?name={drug}")
        data = response.json()
        if data.get('idGroup'):
            rxcui = data['idGroup']['rxnormId'][0]
            rxcuis.append(rxcui)

    # Check interactions
    if len(rxcuis) >= 2:
        rxcui_list = "+".join(rxcuis)
        response = requests.get(f"{RXNORM_API}/interaction/list.json?rxcuis={rxcui_list}")
        interactions = response.json()

        return {"interactions": interactions}

    return {"interactions": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5003)
```

---

## 4. Clinical Guidelines Server

**Purpose:** Access to clinical guidelines (eTG, NSW Health, WHO)
**Port:** 5004
**Protocol:** HTTP

### Features

- Search guidelines by condition
- Protocol lookup
- Flowchart retrieval
- Australian-specific protocols

### Implementation

```python
#!/usr/bin/env python3
"""MCP Server: Clinical Guidelines"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Clinical Guidelines MCP Server")

# In-memory guideline database (in production, use PostgreSQL)
GUIDELINES = {
    "acute_coronary_syndrome": {
        "condition": "Acute Coronary Syndrome",
        "source": "Therapeutic Guidelines: Cardiovascular",
        "updated": "2025-01-01",
        "protocol": """
        1. Initial Assessment:
           - ECG within 10 minutes
           - Troponin
           - Aspirin 300mg PO immediately

        2. Risk Stratification:
           - STEMI → Primary PCI within 90 min
           - NSTEMI → Risk assess with GRACE score

        3. Treatment:
           - Dual antiplatelet (Aspirin + Clopidogrel/Ticagrelor)
           - Anticoagulation
           - Consider PCI vs medical management
        """,
        "medications": ["Aspirin", "Clopidogrel", "Heparin", "Morphine"],
        "flowchart_url": "/static/flowcharts/acs_management.pdf"
    }
    # Add more guidelines...
}

@app.get("/api/guideline/search")
async def search_guideline(condition: str):
    """Search for clinical guideline"""

    condition_key = condition.lower().replace(" ", "_")

    if condition_key in GUIDELINES:
        return GUIDELINES[condition_key]

    return {"error": "Guideline not found"}

@app.get("/api/guideline/list")
async def list_guidelines():
    """List all available guidelines"""
    return {"guidelines": list(GUIDELINES.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5004)
```

---

## 5. Medical Terminology Server

**Purpose:** SNOMED CT, ICD-10, LOINC terminology lookups
**Port:** 5005
**Protocol:** HTTP

### Features

- Terminology code lookups
- Concept relationships
- Hierarchy traversal
- Code mapping (ICD-10 ↔ SNOMED CT)

### Implementation

```python
#!/usr/bin/env python3
"""MCP Server: Medical Terminology"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Medical Terminology MCP Server")

# SNOMED CT codes (sample - full version requires SNOMED CT license)
SNOMED_CODES = {
    "22298006": {
        "code": "22298006",
        "term": "Myocardial infarction",
        "system": "SNOMED CT",
        "parent": "414545008",  # Ischemic heart disease
        "children": ["70422006", "304914007"]  # STEMI, NSTEMI
    }
}

@app.get("/api/terminology/snomed/{code}")
async def get_snomed_concept(code: str):
    """Get SNOMED CT concept by code"""
    if code in SNOMED_CODES:
        return SNOMED_CODES[code]
    return {"error": "Code not found"}

@app.get("/api/terminology/icd10/{code}")
async def get_icd10_code(code: str):
    """Get ICD-10 code description"""
    # Implement ICD-10 lookup
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005)
```

---

## 6. Clinical Calculator Server

**Purpose:** Medical calculators (CURB-65, CHA2DS2-VASc, eGFR, etc.)
**Port:** 5006
**Protocol:** HTTP

### Features

- 50+ clinical calculators
- Risk scores
- Dosage calculators
- Unit conversions

### Implementation

```python
#!/usr/bin/env python3
"""MCP Server: Clinical Calculators"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Clinical Calculator MCP Server")

class CURB65Request(BaseModel):
    confusion: bool
    urea_gt_7: bool
    respiratory_rate_gte_30: bool
    bp_low: bool  # SBP <90 or DBP <=60
    age_gte_65: bool

@app.post("/api/calculator/curb65")
async def calculate_curb65(request: CURB65Request):
    """
    Calculate CURB-65 score for pneumonia severity.

    Score:
    0-1: Low risk (outpatient)
    2: Moderate risk (consider admission)
    3-5: High risk (hospital admission)
    """
    score = sum([
        request.confusion,
        request.urea_gt_7,
        request.respiratory_rate_gte_30,
        request.bp_low,
        request.age_gte_65
    ])

    if score <= 1:
        risk = "Low"
        recommendation = "Consider outpatient treatment"
    elif score == 2:
        risk = "Moderate"
        recommendation = "Consider hospital admission"
    else:
        risk = "High"
        recommendation = "Hospital admission recommended"

    return {
        "score": score,
        "risk": risk,
        "recommendation": recommendation
    }

class eGFRRequest(BaseModel):
    creatinine_umol_l: float
    age: int
    is_female: bool
    is_black: bool

@app.post("/api/calculator/egfr")
async def calculate_egfr(request: eGFRRequest):
    """Calculate eGFR using CKD-EPI equation"""

    # Convert creatinine to mg/dL
    creatinine_mg_dl = request.creatinine_umol_l / 88.4

    # CKD-EPI equation
    kappa = 0.7 if request.is_female else 0.9
    alpha = -0.329 if request.is_female else -0.411

    egfr = 141 * min(creatinine_mg_dl / kappa, 1) ** alpha
    egfr *= max(creatinine_mg_dl / kappa, 1) ** -1.209
    egfr *= 0.993 ** request.age

    if request.is_female:
        egfr *= 1.018

    if request.is_black:
        egfr *= 1.159

    # Classify CKD stage
    if egfr >= 90:
        stage = "G1 (Normal)"
    elif egfr >= 60:
        stage = "G2 (Mildly decreased)"
    elif egfr >= 45:
        stage = "G3a (Mild-moderately decreased)"
    elif egfr >= 30:
        stage = "G3b (Moderate-severely decreased)"
    elif egfr >= 15:
        stage = "G4 (Severely decreased)"
    else:
        stage = "G5 (Kidney failure)"

    return {
        "egfr": round(egfr, 1),
        "units": "mL/min/1.73m²",
        "ckd_stage": stage
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5006)
```

---

## Setup & Configuration

### 1. Install Dependencies

```bash
# Create MCP servers directory
mkdir -p src/mcp_servers

# Install requirements
pip install fastapi uvicorn python-multipart biopython requests
```

### 2. Start All MCP Servers

Create `scripts/start_mcp_servers.sh`:

```bash
#!/bin/bash
# Start all MCP servers

echo "🚀 Starting MCP Servers..."

# Medical Knowledge Server (port 5001)
python src/mcp_servers/medical_knowledge_server.py &
MCP1_PID=$!

# PubMed Server (port 5002)
python src/mcp_servers/pubmed_server.py &
MCP2_PID=$!

# Drug Database Server (port 5003)
python src/mcp_servers/drug_server.py &
MCP3_PID=$!

# Clinical Guidelines Server (port 5004)
python src/mcp_servers/guidelines_server.py &
MCP4_PID=$!

# Medical Terminology Server (port 5005)
python src/mcp_servers/terminology_server.py &
MCP5_PID=$!

# Clinical Calculator Server (port 5006)
python src/mcp_servers/calculator_server.py &
MCP6_PID=$!

echo "✅ All MCP Servers Started"
echo "  - Medical Knowledge: http://localhost:5001"
echo "  - PubMed Search: http://localhost:5002"
echo "  - Drug Database: http://localhost:5003"
echo "  - Clinical Guidelines: http://localhost:5004"
echo "  - Terminology: http://localhost:5005"
echo "  - Calculators: http://localhost:5006"

# Save PIDs for cleanup
echo "$MCP1_PID $MCP2_PID $MCP3_PID $MCP4_PID $MCP5_PID $MCP6_PID" > /tmp/mcp_servers.pid
```

**Run:**
```bash
chmod +x scripts/start_mcp_servers.sh
./scripts/start_mcp_servers.sh
```

### 3. Stop All MCP Servers

Create `scripts/stop_mcp_servers.sh`:

```bash
#!/bin/bash
# Stop all MCP servers

if [ -f /tmp/mcp_servers.pid ]; then
    echo "🛑 Stopping MCP Servers..."
    kill $(cat /tmp/mcp_servers.pid)
    rm /tmp/mcp_servers.pid
    echo "✅ All MCP Servers Stopped"
else
    echo "⚠️  No running MCP servers found"
fi
```

---

## Integration with Agents

### Use MCP Servers in Agents

```python
from src.agents import BaseAgent
import requests

class CardiologyAgent(BaseAgent):
    def execute_task(self, task):
        # Search medical knowledge via MCP server
        response = requests.post(
            "http://localhost:5001/api/search",
            json={
                "query": "acute coronary syndrome management",
                "limit": 5,
                "filters": {"specialty": "cardiology"}
            }
        )

        results = response.json()['results']

        # Use PubMed MCP for latest research
        pubmed_response = requests.post(
            "http://localhost:5002/api/pubmed/search",
            json={
                "query": "acute coronary syndrome 2024",
                "max_results": 10,
                "article_type": "Review"
            }
        )

        # Combine knowledge
        context = self._combine_sources(results, pubmed_response.json())

        return {"status": "success", "context": context}
```

---

## 📊 Summary

**6 MCP Servers Provide:**
- ✅ Medical knowledge access (Qdrant + Neo4j)
- ✅ Real-time literature search (PubMed)
- ✅ Drug information (RxNorm, DrugBank)
- ✅ Clinical guidelines (eTG, NSW Health)
- ✅ Medical terminology (SNOMED CT, ICD-10)
- ✅ Clinical calculators (CURB-65, eGFR, etc.)

**All agents can now:**
- Access standardized medical knowledge
- Search latest research
- Look up drug interactions
- Retrieve clinical protocols
- Use medical calculators

**Next:** See `EXPERT_AGENTS_INFRASTRUCTURE.md` for agent system setup

---

**Last Updated:** December 14, 2025
**Status:** Ready to implement MCP servers 🚀
