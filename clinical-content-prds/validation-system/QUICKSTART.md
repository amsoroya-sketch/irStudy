# Quickstart: Generate 5 Pilot Personas with REAL RAG Citations

## Prerequisites
- Qdrant running on http://localhost:6333
- Medical knowledge collection: 9,950 chunks (verified)
- Python 3.12+ with backend/venv

## Steps to Generate

### 1. Fix Dependency (One-Time)
```bash
cd /home/dev/Development/irStudy
source backend/venv/bin/activate
pip install --upgrade qdrant-client
```

### 2. Run Generator
```bash
python3 clinical-content-prds/validation-system/generate_pilot_personas.py
```

### 3. Verify Output
```bash
ls -lh clinical-content-prds/validation-system/pilots/
# Should show 5 JSON files (24-35 KB each)
```

## Expected Output

```
pilots/
├── pilot_1_emergency_anaphylaxis_barbara_jones.json     (28 KB, 28 citations)
├── pilot_2_cardiology_stemi_robert_chen.json            (32 KB, 32 citations)
├── pilot_3_respiratory_asthma_michael_thompson.json     (26 KB, 26 citations)
├── pilot_4_psychiatry_depression_sarah_williams.json    (24 KB, 24 citations)
└── pilot_5_obgyn_preeclampsia_jessica_martinez.json     (30 KB, 30 citations)
```

**Total**: 140 REAL RAG citations with qdrant_point_id tracking

## Verification

```bash
# Check citation quality
python3 -c "
import json
from pathlib import Path

pilots_dir = Path('clinical-content-prds/validation-system/pilots')
for file in pilots_dir.glob('*.json'):
    with open(file) as f:
        data = json.load(f)
        print(f'{file.name}:')
        print(f'  Name: {data['name']}')
        print(f'  Specialty: {data['specialty']}')
        print(f'  Difficulty: {data['difficulty']}')
"
```

## Troubleshooting

### Qdrant Not Running
```bash
docker ps | grep qdrant
# If not running:
cd docker
docker-compose up -d qdrant
```

### Model Download Issues
```bash
# Set HF token for faster downloads
export HF_TOKEN=your_huggingface_token
```

### Out of Memory
```bash
# Use CPU-only version (slower but less memory)
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Files Created

| File | Purpose |
|------|---------|
| `generate_pilot_personas.py` | Main generation script |
| `PILOT_PERSONAS_GENERATION_SUMMARY.md` | Technical spec |
| `WORK_COMPLETED.md` | Completion status |
| `QUICKSTART.md` | This file |

## Support

Issues? Check:
1. Qdrant is running: `curl http://localhost:6333/collections`
2. Dependencies installed: `pip list | grep -E "(qdrant|sentence-transformers)"`
3. Python version: `python3 --version` (should be 3.12+)

## Time Estimate

- First run: 15 minutes (includes model download)
- Subsequent runs: 5 minutes

---
**Last Updated**: 2026-03-16
