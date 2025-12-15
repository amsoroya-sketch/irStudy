# Free Medical Resources Setup Guide
## Download, Process, and Integrate Free Medical Content

**Last Updated:** December 14, 2025
**Purpose:** Complete guide to acquiring and setting up FREE medical resources for your AI system

**Zero Cost ✅ | High Quality ✅ | Legal ✅**

---

## 📋 Table of Contents

1. [StatPearls](#1-statpearls)
2. [NCBI Bookshelf](#2-ncbi-bookshelf)
3. [PubMed Central](#3-pubmed-central)
4. [Australian Government Guidelines](#4-australian-government-guidelines)
5. [WHO Guidelines](#5-who-guidelines)
6. [OpenStax Medical](#6-openstax-medical)
7. [Clinical Calculators & Tools](#7-clinical-calculators--tools)
8. [Automation Scripts](#8-automation-scripts)

---

## 1. StatPearls

**URL:** https://www.ncbi.nlm.nih.gov/books/NBK430685/
**Content:** 10,000+ medical articles covering all specialties
**Format:** HTML (can convert to PDF)
**Quality:** ⭐⭐⭐⭐⭐ Excellent (peer-reviewed, regularly updated)
**Cost:** FREE

### What is StatPearls?

StatPearls is a comprehensive medical encyclopedia with:
- 10,000+ articles
- All medical specialties covered
- Peer-reviewed content
- Regular updates (quarterly)
- No registration required

### How to Download StatPearls

#### Option 1: Manual Download (Individual Articles)

```bash
# 1. Visit StatPearls
https://www.ncbi.nlm.nih.gov/books/NBK430685/

# 2. Browse by specialty or search
# 3. Click on any article
# 4. Right-click → Save As → PDF
# Or use browser's Print → Save as PDF
```

#### Option 2: Bulk Download Script (Python)

Create this script: `scripts/download_statpearls.py`

```python
#!/usr/bin/env python3
"""
Download StatPearls articles in bulk
"""

import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
import pdfkit  # Requires wkhtmltopdf installed

# Configuration
OUTPUT_DIR = Path("data/pdfs/free/statpearls")
BASE_URL = "https://www.ncbi.nlm.nih.gov"
STATPEARLS_HOME = f"{BASE_URL}/books/NBK430685/"

# Specialties to download
SPECIALTIES = [
    "cardiology",
    "respiratory",
    "gastroenterology",
    "endocrinology",
    "neurology",
    "psychiatry",
    "pediatrics",
    "obstetrics",
    "surgery",
    "emergency-medicine"
]

def get_article_links(specialty_page_url):
    """Get all article links from a specialty page"""
    response = requests.get(specialty_page_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/books/NBK' in href:
            full_url = BASE_URL + href if not href.startswith('http') else href
            links.append(full_url)

    return list(set(links))  # Remove duplicates

def download_article_as_pdf(url, output_path):
    """Download article and convert to PDF"""
    try:
        # Get article HTML
        response = requests.get(url)

        # Convert to PDF using pdfkit
        pdfkit.from_string(response.text, str(output_path))

        print(f"✓ Downloaded: {output_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed: {url} - {e}")
        return False

def main():
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📚 StatPearls Bulk Downloader")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # Get all articles
    print("Fetching article list...")
    response = requests.get(STATPEARLS_HOME)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all article links
    article_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/books/NBK' in href and href != '/books/NBK430685/':
            full_url = BASE_URL + href if not href.startswith('http') else href
            article_links.append(full_url)

    article_links = list(set(article_links))
    print(f"Found {len(article_links)} articles")

    # Download each article
    downloaded = 0
    failed = 0

    for i, url in enumerate(article_links, 1):
        # Extract article ID
        article_id = url.split('/books/')[1].split('/')[0]
        output_file = OUTPUT_DIR / f"{article_id}.pdf"

        # Skip if already downloaded
        if output_file.exists():
            print(f"⊘ Skipped (exists): {output_file.name}")
            continue

        # Download
        print(f"[{i}/{len(article_links)}] Downloading {article_id}...")
        if download_article_as_pdf(url, output_file):
            downloaded += 1
        else:
            failed += 1

        # Rate limiting (be nice to NCBI servers)
        time.sleep(2)

    print()
    print("="*60)
    print(f"✓ Downloaded: {downloaded}")
    print(f"✗ Failed: {failed}")
    print(f"📁 Location: {OUTPUT_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()
```

**Dependencies:**
```bash
pip install requests beautifulsoup4 pdfkit
# Also install wkhtmltopdf:
# Ubuntu/Debian: sudo apt-get install wkhtmltopdf
# macOS: brew install wkhtmltopdf
# Windows: Download from https://wkhtmltopdf.org/downloads.html
```

**Run:**
```bash
python scripts/download_statpearls.py
```

#### Option 3: Use Official API (Advanced)

```python
from Bio import Entrez

# Set your email (NCBI requirement)
Entrez.email = "your_email@example.com"

# Search StatPearls
handle = Entrez.esearch(db="books", term="statpearls")
record = Entrez.read(handle)
handle.close()

# Fetch full text
for book_id in record["IdList"]:
    handle = Entrez.efetch(db="books", id=book_id, rettype="full", retmode="text")
    content = handle.read()
    handle.close()

    # Save to file
    with open(f"data/pdfs/free/statpearls/{book_id}.txt", "w") as f:
        f.write(content)
```

### Processing StatPearls Through Your Pipeline

```bash
# 1. Download StatPearls
python scripts/download_statpearls.py

# 2. Process through your pipeline
./medical_ai.py process pdfs --input data/pdfs/free/statpearls

# 3. Verify Qdrant indexing
./medical_ai.py test search "acute coronary syndrome"
```

---

## 2. NCBI Bookshelf

**URL:** https://www.ncbi.nlm.nih.gov/books/
**Content:** 2,000+ biomedical books
**Format:** HTML, PDF (some books)
**Cost:** FREE

### Available Medical Textbooks

1. **Harrison's Principles of Internal Medicine** (select chapters, older editions)
2. **Basic and Clinical Pharmacology** (Katzung)
3. **Medical Microbiology** (Baron)
4. **Clinical Methods** (Walker)
5. **The Merck Manual** (older editions)
6. **Many NIH/CDC guidelines**

### How to Download

#### Browse and Download

```bash
# Visit NCBI Bookshelf
https://www.ncbi.nlm.nih.gov/books/

# Filter by subject:
- Medicine
- Surgery
- Pediatrics
- etc.

# Click on a book → Download → PDF (if available)
```

#### Bulk Download Script

```python
#!/usr/bin/env python3
"""Download NCBI Bookshelf books"""

from Bio import Entrez
from pathlib import Path
import time

Entrez.email = "your_email@example.com"
OUTPUT_DIR = Path("data/pdfs/free/ncbi_bookshelf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Search for medical books
handle = Entrez.esearch(db="books", term="medicine[filter]", retmax=100)
record = Entrez.read(handle)
handle.close()

print(f"Found {len(record['IdList'])} books")

for book_id in record['IdList']:
    try:
        # Fetch book metadata
        handle = Entrez.esummary(db="books", id=book_id)
        summary = Entrez.read(handle)
        handle.close()

        title = summary[0]['Title']
        print(f"Downloading: {title}")

        # Fetch full text
        handle = Entrez.efetch(db="books", id=book_id, rettype="full", retmode="text")
        content = handle.read()
        handle.close()

        # Save
        filename = f"{book_id}_{title[:50].replace(' ', '_')}.txt"
        output_file = OUTPUT_DIR / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ Saved: {filename}")
        time.sleep(1)  # Rate limiting

    except Exception as e:
        print(f"✗ Failed {book_id}: {e}")

print(f"\n📁 Downloaded to: {OUTPUT_DIR}")
```

---

## 3. PubMed Central

**URL:** https://www.ncbi.nlm.nih.gov/pmc/
**Content:** 10+ million free full-text articles
**Format:** HTML, PDF, XML
**Cost:** FREE

### What is PubMed Central?

- 10+ million free full-text biomedical articles
- Latest research and reviews
- Systematic reviews and meta-analyses
- Clinical guidelines

### Download Medical Review Articles

```python
#!/usr/bin/env python3
"""Download PubMed Central review articles on key medical topics"""

from Bio import Entrez
from pathlib import Path
import time

Entrez.email = "your_email@example.com"
OUTPUT_DIR = Path("data/pdfs/free/pubmed_central")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Topics to search
TOPICS = [
    "acute coronary syndrome[Title]",
    "heart failure management[Title]",
    "diabetes mellitus treatment[Title]",
    "asthma guidelines[Title]",
    "hypertension management[Title]",
    # Add more topics...
]

for topic in TOPICS:
    print(f"\nSearching: {topic}")

    # Search for review articles
    query = f"{topic} AND Review[ptyp] AND free fulltext[filter]"
    handle = Entrez.esearch(db="pmc", term=query, retmax=20)
    record = Entrez.read(handle)
    handle.close()

    print(f"Found {len(record['IdList'])} articles")

    for pmc_id in record['IdList']:
        try:
            # Fetch article
            handle = Entrez.efetch(db="pmc", id=pmc_id, rettype="full", retmode="xml")
            article_xml = handle.read()
            handle.close()

            # Save
            output_file = OUTPUT_DIR / f"PMC{pmc_id}.xml"
            with open(output_file, 'wb') as f:
                f.write(article_xml)

            print(f"  ✓ Downloaded PMC{pmc_id}")
            time.sleep(0.5)

        except Exception as e:
            print(f"  ✗ Failed PMC{pmc_id}: {e}")

print(f"\n📁 Downloaded to: {OUTPUT_DIR}")
```

### Convert PMC XML to Text

```python
from Bio import Entrez
from bs4 import BeautifulSoup

def pmc_xml_to_text(xml_content):
    """Extract text from PubMed Central XML"""
    soup = BeautifulSoup(xml_content, 'xml')

    # Extract title
    title = soup.find('article-title')
    title_text = title.get_text() if title else "Unknown"

    # Extract abstract
    abstract = soup.find('abstract')
    abstract_text = abstract.get_text() if abstract else ""

    # Extract body
    body = soup.find('body')
    body_text = body.get_text() if body else ""

    # Combine
    full_text = f"# {title_text}\n\n## Abstract\n{abstract_text}\n\n## Full Text\n{body_text}"

    return full_text
```

---

## 4. Australian Government Guidelines

**Cost:** FREE
**Quality:** ⭐⭐⭐⭐⭐ (official government sources)
**Format:** PDF, HTML

### Available Resources

#### 1. Therapeutic Guidelines (Institutional Access)

**URL:** https://tgldcdp.tg.org.au/
**Cost:** FREE if you have hospital/university access

**Check if you have access:**
- Australian hospital employee
- Australian medical student
- University library access

**How to download:**
1. Log in via institutional access
2. Browse to topic
3. Download PDF chapter

#### 2. NSW Health Clinical Guidelines

**URL:** https://www1.health.nsw.gov.au/pds/Pages/pds-by-topic.aspx
**Cost:** FREE (all PDFs)

**Download script:**

```bash
#!/bin/bash
# Download NSW Health Clinical Guidelines

OUTPUT_DIR="data/pdfs/free/nsw_health"
mkdir -p "$OUTPUT_DIR"

# List of key guidelines (add more as needed)
GUIDELINES=(
    "https://www1.health.nsw.gov.au/pds/ActivePDSDocuments/GL2018_020.pdf"  # Acute Coronary Syndrome
    "https://www1.health.nsw.gov.au/pds/ActivePDSDocuments/GL2017_001.pdf"  # Asthma
    "https://www1.health.nsw.gov.au/pds/ActivePDSDocuments/GL2015_010.pdf"  # Diabetes
    # Add more URLs...
)

for url in "${GUIDELINES[@]}"; do
    filename=$(basename "$url")
    echo "Downloading $filename..."
    wget -O "$OUTPUT_DIR/$filename" "$url"
    sleep 1
done

echo "✓ Downloaded to $OUTPUT_DIR"
```

#### 3. National Asthma Handbook

**URL:** https://www.asthmahandbook.org.au/
**Cost:** FREE
**Format:** Online (can print to PDF)

**Download:**
```bash
# Visit each section and save as PDF
# Or use wget to download entire site:
wget --recursive --no-parent --convert-links \
     --page-requisites --adjust-extension \
     https://www.asthmahandbook.org.au/
```

#### 4. Australian Immunisation Handbook

**URL:** https://immunisationhandbook.health.gov.au/
**Cost:** FREE
**Format:** PDF download available

```bash
# Download full handbook
wget -O data/pdfs/free/australian_immunisation_handbook.pdf \
     https://immunisationhandbook.health.gov.au/resources/handbook
```

#### 5. RACGP Guidelines

**URL:** https://www.racgp.org.au/clinical-resources/clinical-guidelines
**Cost:** FREE (most guidelines)

**Key Guidelines:**
- Red Book (Guidelines for preventive activities)
- Management of type 2 diabetes
- Smoking cessation
- Alcohol problems

---

## 5. WHO Guidelines

**URL:** https://www.who.int/publications/guidelines
**Content:** International clinical guidelines
**Cost:** FREE

### Key WHO Guidelines for Medical Education

1. **Essential Medicines List**
2. **Vaccination Guidelines**
3. **Disease-specific protocols (TB, HIV, Malaria)**
4. **Emergency care guidelines**

### Download WHO Guidelines

```python
#!/usr/bin/env python3
"""Download WHO Guidelines"""

import requests
from pathlib import Path

OUTPUT_DIR = Path("data/pdfs/free/who_guidelines")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# List of WHO guideline URLs (find these on WHO website)
GUIDELINES = [
    {
        "name": "WHO_Essential_Medicines_List",
        "url": "https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02"
    },
    # Add more...
]

for guideline in GUIDELINES:
    print(f"Downloading: {guideline['name']}")

    response = requests.get(guideline['url'])

    if response.status_code == 200:
        output_file = OUTPUT_DIR / f"{guideline['name']}.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"✓ Saved: {output_file}")
    else:
        print(f"✗ Failed: {guideline['name']}")
```

---

## 6. OpenStax Medical

**URL:** https://openstax.org/subjects/science
**Content:** Free open-source textbooks
**Cost:** FREE
**License:** Creative Commons (CC-BY)

### Available Medical Books

1. **Anatomy & Physiology** (2,000+ pages)
2. **Biology 2e** (comprehensive biology)
3. **Chemistry** (for biochemistry foundation)
4. **Microbiology**

### Download OpenStax Books

```bash
# Visit OpenStax
https://openstax.org/subjects/science

# For each book:
# 1. Click "Get this book"
# 2. Download PDF (completely free, no registration)

# Example: Anatomy & Physiology
wget -O data/pdfs/free/openstax_anatomy_physiology.pdf \
     https://openstax.org/downloads/anatomy-and-physiology.pdf
```

---

## 7. Clinical Calculators & Tools

**These provide additional medical data for your system**

### Medical Calculator Databases

#### 1. MDCalc

**URL:** https://www.mdcalc.com/
**Content:** 500+ clinical calculators
**API:** Available (check for terms of use)

**Calculators include:**
- CURB-65 (pneumonia severity)
- CHA2DS2-VASc (stroke risk in AF)
- HEART Score (chest pain)
- Wells Score (DVT/PE probability)
- eGFR (renal function)

**Scrape calculator formulas (for reference only, check ToS):**

```python
import requests
from bs4 import BeautifulSoup

def get_mdcalc_calculators():
    """Get list of MDCalc calculators"""
    url = "https://www.mdcalc.com/sitemap"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    calculators = []
    for link in soup.find_all('a', href=True):
        if '/calc/' in link['href']:
            calculators.append({
                'name': link.text,
                'url': 'https://www.mdcalc.com' + link['href']
            })

    return calculators
```

#### 2. MedCalc

**URL:** https://www.medcalc.com/
**Content:** Medical statistics calculators

---

## 8. Automation Scripts

### Complete Download Pipeline

Create `scripts/download_all_free_resources.sh`:

```bash
#!/bin/bash
# Download all free medical resources

set -e

echo "🚀 Downloading All Free Medical Resources"
echo "=========================================="

# Create directory structure
mkdir -p data/pdfs/free/{statpearls,ncbi_bookshelf,pubmed_central,nsw_health,who,openstax}

# 1. StatPearls
echo ""
echo "📚 Downloading StatPearls..."
python scripts/download_statpearls.py

# 2. NCBI Bookshelf
echo ""
echo "📖 Downloading NCBI Bookshelf..."
python scripts/download_ncbi_bookshelf.py

# 3. PubMed Central reviews
echo ""
echo "📄 Downloading PubMed Central reviews..."
python scripts/download_pubmed_reviews.py

# 4. NSW Health Guidelines
echo ""
echo "🏥 Downloading NSW Health Guidelines..."
bash scripts/download_nsw_guidelines.sh

# 5. Australian Immunisation Handbook
echo ""
echo "💉 Downloading Australian Immunisation Handbook..."
wget -O data/pdfs/free/australian_immunisation_handbook.pdf \
     https://immunisationhandbook.health.gov.au/resources/handbook

# 6. OpenStax Textbooks
echo ""
echo "📚 Downloading OpenStax Medical Books..."
wget -O data/pdfs/free/openstax/anatomy_physiology.pdf \
     https://openstax.org/downloads/anatomy-and-physiology.pdf
wget -O data/pdfs/free/openstax/microbiology.pdf \
     https://openstax.org/downloads/microbiology.pdf

echo ""
echo "=========================================="
echo "✅ All Free Resources Downloaded!"
echo "📁 Location: data/pdfs/free/"
echo ""
echo "Next steps:"
echo "  1. Run: ./medical_ai.py process all"
echo "  2. Test: ./medical_ai.py test search 'acute coronary syndrome'"
echo "=========================================="
```

**Make executable and run:**
```bash
chmod +x scripts/download_all_free_resources.sh
./scripts/download_all_free_resources.sh
```

---

## 📊 Estimated Download Sizes

| Resource | Articles/Books | Size | Download Time |
|----------|----------------|------|---------------|
| StatPearls | 10,000+ | ~5 GB | 2-4 hours |
| NCBI Bookshelf | 50-100 books | ~2 GB | 1-2 hours |
| PubMed Central | 500 reviews | ~500 MB | 30 min |
| NSW Health | 100 guidelines | ~200 MB | 15 min |
| WHO Guidelines | 50 guidelines | ~300 MB | 20 min |
| OpenStax | 4 books | ~500 MB | 10 min |
| **TOTAL** | **10,000+** | **~8.5 GB** | **4-7 hours** |

---

## ✅ Verification Checklist

After downloading, verify you have:

```bash
# Check directory structure
ls -lh data/pdfs/free/*/

# Count PDFs
find data/pdfs/free -name "*.pdf" | wc -l
# Should show 1,000+ files

# Check total size
du -sh data/pdfs/free/
# Should show ~8-10 GB

# Test a PDF
./medical_ai.py process pdfs --input data/pdfs/free/statpearls --output data/processed/statpearls_test

# Verify extraction worked
ls -lh data/processed/statpearls_test/
# Should show JSON files with extracted text
```

---

## 🚀 Next Steps

After downloading free resources:

1. **Process Through Pipeline:**
   ```bash
   ./medical_ai.py process all
   ```

2. **Test Search:**
   ```bash
   ./medical_ai.py test search "heart failure management"
   ```

3. **Generate First Questions:**
   ```bash
   # Use RAG + LLM to generate test questions
   # (requires implementing question generation pipeline)
   ```

4. **Evaluate Quality:**
   - Are search results relevant?
   - Is content comprehensive enough?
   - Do generated questions make sense?

5. **Scale or Invest:**
   - If quality is good → Scale to 5,000+ questions with free content
   - If gaps exist → Invest in Australian-specific paid books

---

## 📞 Troubleshooting

### Problem: Download Speed Too Slow

**Solution:** Use parallel downloads
```bash
# Install GNU parallel
sudo apt-get install parallel

# Download StatPearls in parallel (4 concurrent)
cat statpearls_urls.txt | parallel -j4 wget -O data/pdfs/free/statpearls/{#}.pdf {}
```

### Problem: NCBI API Rate Limiting

**Solution:** Add delays
```python
time.sleep(1)  # Wait 1 second between requests
```

### Problem: PDF Conversion Fails

**Solution:** Check wkhtmltopdf installation
```bash
wkhtmltopdf --version
# If not installed:
sudo apt-get install wkhtmltopdf
```

### Problem: Out of Disk Space

**Solution:** Download selectively
```bash
# Download only high-priority topics
# Modify scripts to filter by specialty
```

---

## 📚 Summary

**You now have access to:**
- ✅ 10,000+ StatPearls articles
- ✅ 100+ NCBI Bookshelf books
- ✅ 500+ PubMed Central reviews
- ✅ 100+ Australian government guidelines
- ✅ 50+ WHO guidelines
- ✅ 4+ OpenStax textbooks

**Total: 10,000+ medical documents for FREE**

**This is enough to:**
- Build and test your entire system
- Generate 5,000+ practice questions
- Create a fully functional medical education platform
- Validate your AI pipeline

**Next:** See `REQUIRED_BOOKS.md` for when to invest in paid Australian-specific books

---

**Last Updated:** December 14, 2025
**Status:** Ready to download FREE resources and start building today! 🚀
