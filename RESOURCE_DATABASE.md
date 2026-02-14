# Medical Resources Database

**Last Updated:** 2026-01-17
**Version:** 1.0.0
**Total Resources:** 15 essential + 2 optional
**Total Size:** ~25-35 GB (essential), ~75-85 GB (with optional)

---

## Database Overview

This database tracks all medical resources downloaded for the ICRP study preparation system, including:
- Download URLs and methods
- Version tracking and release dates
- Update schedules and verification
- Integration status with RAG system

---

## Essential Resources (Priority: HIGH)

### 1. StatPearls Medical Database

| Field | Value |
|-------|-------|
| **Resource ID** | RES-001 |
| **Name** | StatPearls Publishing Database |
| **Category** | Medical Textbook / Reference |
| **Source** | NCBI Bookshelf |
| **URL** | https://www.ncbi.nlm.nih.gov/books/NBK430685/ |
| **API Endpoint** | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ |
| **Latest Version** | Continuous updates (2026-01-17) |
| **Latest Release Date** | 2026-01-17 |
| **Release Frequency** | Continuous (daily updates) |
| **Next Update Check** | Weekly |
| **Next Expected Release** | 2026-01-24 (weekly check) |
| **Size** | 15-20 GB (~10,000 articles) |
| **Format** | XML, TXT |
| **Download Method** | Automated (Python script) |
| **Script** | `scripts/download_statpearls.py` |
| **Authentication** | NCBI API Key (free) |
| **Status** | ✅ Automated download available |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | All medical specialties |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Medical experts, peer-reviewed |
| **Update Strategy** | Incremental download (fetch only new/updated articles) |

**Update Check Command:**
```bash
python3 scripts/check_statpearls_updates.py --last-check-date 2026-01-17
```

---

### 2. Cochrane Library - Systematic Reviews

| Field | Value |
|-------|-------|
| **Resource ID** | RES-002 |
| **Name** | Cochrane Systematic Reviews |
| **Category** | Evidence-Based Medicine |
| **Source** | Cochrane Library |
| **URL** | https://www.cochranelibrary.com/ |
| **Latest Version** | Monthly updates |
| **Latest Release Date** | 2026-01-01 |
| **Release Frequency** | Monthly (new reviews), Quarterly (updates) |
| **Next Update Check** | Monthly (1st of each month) |
| **Next Expected Release** | 2026-02-01 |
| **Size** | 5-10 GB (~500-1000 reviews) |
| **Format** | PDF, HTML |
| **Download Method** | Manual (account required) |
| **Script** | `scripts/download_cochrane_pdfs.py` (experimental) |
| **Authentication** | Free account registration |
| **Status** | ⚠️ Manual download required |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | All clinical specialties |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Gold standard for systematic reviews |
| **Update Strategy** | Monthly scan for new reviews by specialty |

**Specialties Covered:**
- Cardiology (~50-100 reviews, ~500 MB)
- Respiratory (~50-100 reviews, ~500 MB)
- Gastroenterology (~40-80 reviews, ~400 MB)
- Endocrinology (~30-60 reviews, ~300 MB)
- Neurology (~40-80 reviews, ~400 MB)
- Emergency Medicine (~30-60 reviews, ~300 MB)
- Obstetrics & Gynaecology (~50-100 reviews, ~500 MB)
- Paediatrics (~60-120 reviews, ~600 MB)
- Psychiatry (~40-80 reviews, ~400 MB)
- General Practice (~40-80 reviews, ~400 MB)

**Update Check Command:**
```bash
python3 scripts/check_cochrane_updates.py --specialty all --last-check-date 2026-01-01
```

---

### 3. RACGP Red Book (Australian General Practice Guidelines)

| Field | Value |
|-------|-------|
| **Resource ID** | RES-003 |
| **Name** | RACGP Red Book (Guidelines for Preventive Activities in General Practice) |
| **Category** | Clinical Practice Guidelines |
| **Source** | Royal Australian College of General Practitioners |
| **URL** | https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-racgp-guidelines/red-book |
| **Latest Version** | 10th Edition (2024) |
| **Latest Release Date** | 2024-01-01 |
| **Release Frequency** | Every 2-3 years (major), Annual (minor updates) |
| **Next Update Check** | 2026-06-01 |
| **Next Expected Release** | 2027-01-01 |
| **Next Major Release** | 2026-2027 (estimated) |
| **Size** | ~50 MB |
| **Format** | PDF |
| **Download Method** | Automated (direct download) |
| **Script** | `scripts/download_external_resources.sh` |
| **Authentication** | None (publicly available) |
| **Status** | ✅ Automated download available |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | Preventive care, screening, immunisation |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Official RACGP guideline |
| **Update Strategy** | Check website quarterly for new edition |

**Update Check Command:**
```bash
curl -I https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-racgp-guidelines/red-book | grep "Last-Modified"
```

---

### 4. RANZCOG Guidelines (Obstetrics & Gynaecology)

| Field | Value |
|-------|-------|
| **Resource ID** | RES-004 |
| **Name** | RANZCOG Clinical Statements and Guidelines |
| **Category** | Clinical Practice Guidelines |
| **Source** | Royal Australian and New Zealand College of Obstetricians and Gynaecologists |
| **URL** | https://ranzcog.edu.au/statements-guidelines |
| **Latest Version** | Continuous updates (individual statements) |
| **Latest Release Date** | 2026-01-01 |
| **Release Frequency** | Monthly (new/updated statements) |
| **Next Update Check** | Monthly (1st of each month) |
| **Next Expected Release** | 2026-02-01 |
| **Size** | ~500 MB |
| **Format** | PDF |
| **Download Method** | Manual (account recommended) |
| **Script** | Manual checklist in download guide |
| **Authentication** | Free account (healthcare professional verification) |
| **Status** | ⚠️ Manual download required |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | Obstetrics, gynaecology, women's health |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Official Australian/NZ ObGyn college |
| **Update Strategy** | Monthly scan for new/updated statements |

**Key Statements:**
- Antenatal screening
- Pre-eclampsia management
- Gestational diabetes
- Post-partum haemorrhage
- Contraception
- Menopause management

**Update Check Command:**
```bash
python3 scripts/check_ranzcog_updates.py --last-check-date 2026-01-01
```

---

### 5. RANZCP Clinical Practice Guidelines (Psychiatry)

| Field | Value |
|-------|-------|
| **Resource ID** | RES-005 |
| **Name** | RANZCP Clinical Practice Guidelines |
| **Category** | Clinical Practice Guidelines |
| **Source** | Royal Australian and New Zealand College of Psychiatrists |
| **URL** | https://www.ranzcp.org/clinical-guidelines-publications |
| **Latest Version** | Varies by guideline (2020-2024) |
| **Latest Release Date** | 2024-01-01 |
| **Release Frequency** | Every 3-5 years per guideline |
| **Next Update Check** | Quarterly |
| **Next Expected Release** | 2027-01-01 |
| **Size** | ~200 MB |
| **Format** | PDF |
| **Download Method** | Manual (direct download) |
| **Script** | Manual checklist in download guide |
| **Authentication** | None (publicly available) |
| **Status** | ✅ Available for download |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | Mental health, psychiatry |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Official Australian/NZ psychiatry college |
| **Update Strategy** | Quarterly check for guideline updates |

**Key Guidelines:**
- Depression treatment
- Anxiety disorders
- Schizophrenia management
- Bipolar disorder
- Suicide risk assessment

**Update Check Command:**
```bash
python3 scripts/check_ranzcp_updates.py --last-check-date 2026-01-01
```

---

### 6. MeSH (Medical Subject Headings) Database

| Field | Value |
|-------|-------|
| **Resource ID** | RES-006 |
| **Name** | MeSH (Medical Subject Headings) |
| **Category** | Medical Terminology / Ontology |
| **Source** | U.S. National Library of Medicine |
| **URL** | https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/meshtrees/ |
| **Latest Version** | 2026 MeSH (released 2025-12) |
| **Latest Release Date** | 2025-12-01 |
| **Release Frequency** | Annual (December each year) |
| **Next Update Check** | 2026-12-01 |
| **Next Expected Release** | 2026-12-01 |
| **Next Major Release** | 2027-01-01 (2027 MeSH) |
| **Size** | ~500 MB |
| **Format** | XML, ASCII |
| **Download Method** | Automated (direct download) |
| **Script** | `scripts/download_external_resources.sh` |
| **Authentication** | None (publicly available) |
| **Status** | ✅ Automated download available |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | Comprehensive medical terminology |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | NLM standard medical vocabulary |
| **Update Strategy** | Annual download (December/January) |

**Update Check Command:**
```bash
curl -I https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/meshtrees/mtrees2026.bin | grep "Last-Modified"
```

---

### 7. Australian Immunisation Handbook

| Field | Value |
|-------|-------|
| **Resource ID** | RES-007 |
| **Name** | The Australian Immunisation Handbook |
| **Category** | Clinical Practice Guidelines |
| **Source** | Australian Government Department of Health |
| **URL** | https://immunisationhandbook.health.gov.au/ |
| **Latest Version** | 2023 (updated regularly) |
| **Latest Release Date** | 2025-10-01 |
| **Release Frequency** | Annual updates, quarterly revisions |
| **Next Update Check** | Quarterly |
| **Next Expected Release** | 2026-04-01 |
| **Size** | ~100 MB |
| **Format** | HTML, PDF (downloadable sections) |
| **Download Method** | Automated (web scraping) |
| **Script** | `scripts/download_australian_guidelines.py` |
| **Authentication** | None (publicly available) |
| **Status** | ✅ Automated download available |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | Immunisation, vaccination schedules |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Official Australian government guideline |
| **Update Strategy** | Quarterly check for updates |

**Update Check Command:**
```bash
python3 scripts/check_immunisation_updates.py --last-check-date 2026-01-01
```

---

### 8. Australian Stroke Foundation Guidelines

| Field | Value |
|-------|-------|
| **Resource ID** | RES-008 |
| **Name** | Clinical Guidelines for Stroke Management |
| **Category** | Clinical Practice Guidelines |
| **Source** | Stroke Foundation (Australia) |
| **URL** | https://informme.org.au/guidelines/clinical-guidelines-for-stroke-management |
| **Latest Version** | 2023 (Living guidelines - continuous updates) |
| **Latest Release Date** | 2026-01-15 |
| **Release Frequency** | Continuous (living guidelines) |
| **Next Update Check** | Monthly |
| **Next Expected Release** | Continuous |
| **Size** | ~200 MB |
| **Format** | PDF, HTML |
| **Download Method** | Automated (direct download) |
| **Script** | `scripts/download_external_resources.sh` |
| **Authentication** | None (publicly available) |
| **Status** | ✅ Automated download available |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | Stroke prevention, acute management, rehabilitation |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | National Stroke Foundation Australia |
| **Update Strategy** | Monthly check (living guidelines) |

**Update Check Command:**
```bash
python3 scripts/check_stroke_updates.py --last-check-date 2026-01-01
```

---

### 9. NSW Health Clinical Protocols

| Field | Value |
|-------|-------|
| **Resource ID** | RES-009 |
| **Name** | NSW Health Policy Directives and Guidelines |
| **Category** | Clinical Protocols |
| **Source** | NSW Ministry of Health |
| **URL** | https://www.health.nsw.gov.au/policies/ |
| **Latest Version** | Continuous updates (individual policies) |
| **Latest Release Date** | 2026-01-10 |
| **Release Frequency** | Weekly (new/updated policies) |
| **Next Update Check** | Monthly |
| **Next Expected Release** | Weekly |
| **Size** | ~300 MB |
| **Format** | PDF |
| **Download Method** | Manual (search and download) |
| **Script** | Manual checklist in download guide |
| **Authentication** | None (publicly available) |
| **Status** | ⚠️ Manual download required |
| **Last Downloaded** | - |
| **Integration Status** | Pending |
| **Coverage** | Emergency, obstetric, mental health, paediatric protocols |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Official NSW Health protocols |
| **Update Strategy** | Monthly scan for new/updated policies |

**Key Protocol Categories:**
- Emergency medicine
- Resuscitation
- Sepsis management
- Mental health crisis
- Paediatric emergencies

**Update Check Command:**
```bash
python3 scripts/check_nsw_health_updates.py --last-check-date 2026-01-01
```

---

### 10. Therapeutic Guidelines (eTG) - OPTIONAL

| Field | Value |
|-------|-------|
| **Resource ID** | RES-010 |
| **Name** | Therapeutic Guidelines (eTG Complete) |
| **Category** | Clinical Practice Guidelines |
| **Source** | Therapeutic Guidelines Limited |
| **URL** | https://www.tg.org.au/ |
| **Latest Version** | Continuous updates (subscription-based) |
| **Latest Release Date** | 2026-01-01 |
| **Release Frequency** | Monthly updates |
| **Next Update Check** | Monthly (if subscribed) |
| **Next Expected Release** | 2026-02-01 |
| **Size** | ~1 GB |
| **Format** | PDF (via subscription portal) |
| **Download Method** | Manual (requires paid subscription) |
| **Script** | N/A (subscription required) |
| **Authentication** | Paid subscription (~$300-500/year) |
| **Status** | ⚠️ Optional - Requires subscription |
| **Last Downloaded** | - |
| **Integration Status** | Already integrated (9,672 chunks in vector DB) |
| **Coverage** | All therapeutic areas |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | Australian standard for therapeutic guidelines |
| **Update Strategy** | Monthly download if subscribed |

**Note:** We already have 9,672 eTG chunks in the existing vector database, so new downloads are optional.

---

## Optional Resources (Priority: MEDIUM-LOW)

### 11. UMLS Metathesaurus / SNOMED CT

| Field | Value |
|-------|-------|
| **Resource ID** | RES-011 |
| **Name** | UMLS Metathesaurus with SNOMED CT Australian Edition |
| **Category** | Medical Terminology / Ontology |
| **Source** | U.S. National Library of Medicine / SNOMED International |
| **URL** | https://uts.nlm.nih.gov/ |
| **Latest Version** | 2026 AA (released 2026-01) |
| **Latest Release Date** | 2026-01-01 |
| **Release Frequency** | Biannual (May, November) |
| **Next Update Check** | 2026-05-01 |
| **Next Expected Release** | 2026-05-01 |
| **Next Major Release** | 2026-05-01 (2026 AB) |
| **Size** | ~2 GB |
| **Format** | RRF, SQL |
| **Download Method** | Manual (requires UMLS license) |
| **Script** | Manual download from UTS |
| **Authentication** | UMLS License (free, 1-3 days approval) |
| **Status** | ⏳ Requires UMLS license application |
| **Last Downloaded** | - |
| **Integration Status** | Not started |
| **Coverage** | Comprehensive medical terminology mapping |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | International standard (SNOMED CT) |
| **Update Strategy** | Biannual download (May, November) |

**License Application Steps:**
1. Visit: https://uts.nlm.nih.gov/uts/signup-login
2. Create UMLS account
3. Request UMLS Metathesaurus License
4. Select "Affiliate License" (free for non-commercial use)
5. Wait for approval (1-3 business days)
6. Download SNOMED CT Australian Edition

**Update Check Command:**
```bash
# Check after logging into UTS account
# Visit: https://uts.nlm.nih.gov/uts/
```

---

### 12. MIMIC-III Clinical Database - OPTIONAL

| Field | Value |
|-------|-------|
| **Resource ID** | RES-012 |
| **Name** | MIMIC-III (Medical Information Mart for Intensive Care III) |
| **Category** | Clinical Database (De-identified Patient Data) |
| **Source** | MIT Lab for Computational Physiology |
| **URL** | https://physionet.org/content/mimiciii/1.4/ |
| **Latest Version** | v1.4 (2016, stable) |
| **Latest Release Date** | 2016-01-01 |
| **Release Frequency** | Stable (no regular updates) |
| **Next Update Check** | Annually (check for MIMIC-IV) |
| **Next Expected Release** | N/A (stable) |
| **Size** | ~50 GB (compressed) |
| **Format** | CSV, SQL |
| **Download Method** | Manual (requires PhysioNet credentialing) |
| **Script** | Manual download from PhysioNet |
| **Authentication** | PhysioNet credentialed access (requires CITI training) |
| **Status** | ⏳ Optional - Requires PhysioNet credentialing |
| **Last Downloaded** | - |
| **Integration Status** | Not started |
| **Coverage** | ICU patient data (58,000+ admissions) |
| **Quality Rating** | ⭐⭐⭐⭐⭐ (5/5) |
| **Authority** | MIT, widely used in medical AI research |
| **Update Strategy** | Consider MIMIC-IV for updates |

**Credentialing Steps:**
1. Visit: https://physionet.org/
2. Create account
3. Complete CITI training: https://physionet.org/about/citi-course/
4. Apply for MIMIC-III access
5. Wait for approval (1-2 weeks)
6. Download dataset

**Note:** MIMIC-III is optional and very large. Only download if needed for advanced clinical decision support features.

---

## Resource Summary

### By Category

| Category | Count | Total Size | Priority |
|----------|-------|------------|----------|
| Clinical Practice Guidelines | 7 | ~2.4 GB | HIGH |
| Evidence-Based Medicine | 1 | 5-10 GB | HIGH |
| Medical Textbooks | 1 | 15-20 GB | HIGH |
| Medical Terminology | 2 | ~2.5 GB | MEDIUM |
| Clinical Databases | 1 | ~50 GB | LOW (optional) |
| **Total** | **12** | **~75-85 GB** | - |

### By Download Method

| Method | Count | Resources |
|--------|-------|-----------|
| Automated (Python/Bash) | 5 | RES-001, RES-003, RES-006, RES-007, RES-008 |
| Manual (Browser) | 5 | RES-002, RES-004, RES-005, RES-009, RES-010 |
| Requires Approval | 2 | RES-011 (1-3 days), RES-012 (1-2 weeks) |

### By Status

| Status | Count | Resources |
|--------|-------|-----------|
| ✅ Ready for download | 5 | RES-001, RES-003, RES-006, RES-007, RES-008 |
| ⚠️ Manual required | 5 | RES-002, RES-004, RES-005, RES-009, RES-010 |
| ⏳ Approval required | 2 | RES-011, RES-012 |

---

## Update Schedule

### Weekly Updates
- **StatPearls** (RES-001): Check for new/updated articles

### Monthly Updates
- **Cochrane Library** (RES-002): 1st of each month
- **RANZCOG** (RES-004): 1st of each month
- **Stroke Foundation** (RES-008): Living guidelines check
- **NSW Health** (RES-009): Policy directive scan
- **Therapeutic Guidelines** (RES-010): If subscribed

### Quarterly Updates
- **RACGP Red Book** (RES-003): Check for new edition
- **RANZCP** (RES-005): Guideline updates
- **Immunisation Handbook** (RES-007): Quarterly revisions

### Annual Updates
- **MeSH Database** (RES-006): December/January

### Biannual Updates
- **UMLS/SNOMED CT** (RES-011): May, November

---

## Automation Status

### Fully Automated ✅
- StatPearls (RES-001)
- RACGP Red Book (RES-003)
- MeSH Database (RES-006)
- Immunisation Handbook (RES-007)
- Stroke Foundation (RES-008)

### Partially Automated ⚙️
- Cochrane Library (RES-002): Experimental scripts available

### Manual Only ⚠️
- RANZCOG (RES-004)
- RANZCP (RES-005)
- NSW Health (RES-009)
- Therapeutic Guidelines (RES-010)
- UMLS/SNOMED CT (RES-011)
- MIMIC-III (RES-012)

---

## Database Management

### Adding New Resources

When adding a new resource, include:
1. Resource ID (RES-XXX)
2. Official name and source
3. URL and access method
4. Version and release frequency
5. Size estimate
6. Download method (automated/manual)
7. Authentication requirements
8. Update strategy

### Version Tracking

Each resource should track:
- Current version downloaded
- Date of last download
- Next scheduled update check
- Version number/release date

### Integration Tracking

Monitor:
- Download completion status
- Processing status (PDF parsing, chunking, etc.)
- Vector database indexing status
- Citation validation status

---

## Commands Reference

### Check All Updates
```bash
python3 scripts/check_all_resource_updates.py --verbose
```

### Download Essential Resources
```bash
bash scripts/download_orchestrator.sh /path/to/external/disk
```

### Verify Downloads
```bash
python3 scripts/verify_downloads.py --input /path/to/medical_resources
```

### Update Database Metadata
```bash
python3 scripts/update_resource_metadata.py --resource RES-001 --version "2026-01-17" --status "downloaded"
```

---

## Maintenance Schedule

### Daily
- Monitor automated downloads (if running)

### Weekly
- Check StatPearls for updates
- Review download logs

### Monthly (1st of month)
- Run update checker for all monthly resources
- Download new Cochrane reviews
- Check RANZCOG, NSW Health for updates

### Quarterly
- Check RACGP, RANZCP, Immunisation Handbook
- Review and update this database

### Annually
- Download new MeSH release (December/January)
- Review all resources for major updates
- Archive old versions

---

**Last Updated:** 2026-01-17
**Next Review:** 2026-02-01
**Maintained By:** ICRP Study Resource Management System
**Version:** 1.0.0
