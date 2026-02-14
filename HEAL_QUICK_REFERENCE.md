# HEAL Download - Quick Reference Card

**Status:** ✅ Production Ready | **Date:** 2026-02-03

---

## 🚀 Quick Start (Choose One)

### Test (5 min, 5 images)
```bash
./download_heal.sh --query "melanoma" --collection test --max-images 5 --show-browser
```

### Phase 1 (1-2 hrs, 300-400 images) ⭐ **RECOMMENDED**
```bash
./download_heal_comprehensive.sh --phase 1
```

### Complete (3-4 hrs, 550-800 images)
```bash
./download_heal_comprehensive.sh --phase all
```

---

## 📊 What Gets Downloaded

### Phase 1 (High-Priority)
- **Hematology:** 60 topics (blood smears, bone marrow)
- **Dermatology:** 35 topics (skin lesions, dermatitis)
- **Cardiology:** 35 topics (ECG, arrhythmias, MI)
- **Total:** 130 topics → ~300-400 images

### Phase 2 (Medium-Priority)
- **Anatomy:** 42 topics
- **Bone/Marrow:** 14 topics
- **Respiratory:** 10 topics
- **Pediatrics:** 10 topics
- **Pathology:** 20 topics
- **Total:** 96 topics → ~200-300 images

### Phase 3 (Low-Priority)
- **GI:** 8 topics
- **Infectious:** 4 topics
- **Total:** 12 topics → ~50-100 images

---

## 📁 Output Structure

```
data/medical_images/heal/
├── hematology/
│   ├── acute_myeloid_leukemia/
│   ├── sickle_cell_anemia/
│   └── ... (60 topics)
├── dermatology/
│   ├── melanoma/
│   ├── psoriasis/
│   └── ... (35 topics)
└── cardiology/
    ├── atrial_fibrillation_ECG/
    ├── ST_elevation_myocardial_infarction/
    └── ... (35 topics)
```

---

## ⚙️ Options

```bash
# Custom specialties
./download_heal_comprehensive.sh \
    --specialties hematology dermatology \
    --images-per-topic 15

# Faster (reduce delays)
./download_heal_comprehensive.sh \
    --phase 1 \
    --image-delay 0.5 \
    --topic-delay 2

# Test (no delays, show browser)
./download_heal_comprehensive.sh \
    --phase 1 \
    --images-per-topic 5 \
    --no-delay \
    --show-browser
```

---

## 📖 Documentation

| File | Purpose |
|------|---------|
| `HEAL_COMPLETE_SUMMARY.md` | Complete overview |
| `HEAL_COMPREHENSIVE_DOWNLOAD_GUIDE.md` | Full usage guide |
| `HEAL_TOPIC_ANALYSIS.md` | All 238 topics listed |
| `HEAL_PLAYWRIGHT_QUICKSTART.md` | Simple downloader guide |

---

## ⏱️ Time Estimates

| Phase | Topics | Images | Time |
|-------|--------|--------|------|
| Test | 1 | 5 | 5 min |
| Phase 1 | 130 | 300-400 | 1-2 hrs |
| Phase 2 | 96 | 200-300 | 1-1.5 hrs |
| Phase 3 | 12 | 50-100 | 30 min |
| **All** | **238** | **550-800** | **3-4 hrs** |

---

## ✅ After Download

```bash
# View structure
tree -L 3 data/medical_images/heal/

# Count images
find data/medical_images/heal/ -name "*.jpg" | wc -l

# Check metadata
cat data/medical_images/heal/heal_comprehensive_metadata.json | jq '.total_images'

# Process metadata
python3 scripts/process_image_metadata.py --source data/medical_images/heal

# Upload to CDN
python3 scripts/upload_to_cdn.py --source data/medical_images/heal ...

# Index database
python3 scripts/index_images.py --metadata data/heal_metadata.json
```

---

## 🎯 Best AMC Coverage

**HEAL Strengths:**
- ⭐⭐⭐⭐⭐ Hematology (exceptional)
- ⭐⭐⭐⭐⭐ Dermatology (exceptional)
- ⭐⭐⭐⭐⭐ Cardiology/ECG (exceptional)
- ⭐⭐⭐⭐ Anatomy (excellent)

**HEAL Gaps (use MedPix):**
- ❌ Neurology
- ❌ Surgery
- ❌ ObGyn
- ❌ Psychiatry

---

## 🆘 Troubleshooting

**No results found:**
```bash
# Try broader search
./download_heal.sh --query "dermatology" --collection test --max-images 10
```

**Too slow:**
```bash
# Reduce delays
./download_heal_comprehensive.sh --phase 1 --image-delay 0.5 --topic-delay 1
```

**Browser error:**
```bash
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0
```

---

## 📌 Recommended Action

**Start with Phase 1 (best ROI):**
```bash
./download_heal_comprehensive.sh --phase 1
```

**Downloads in 1-2 hours:**
- 300-400 high-value images
- Best coverage for AMC hematology, dermatology, ECG
- Organized in separate topic folders
- Ready for CDN upload and RAG integration

---

**Need help?** See `HEAL_COMPREHENSIVE_DOWNLOAD_GUIDE.md` for complete documentation.
