# PRD_OSCE_008_MASTER_INDEX

## R — Request

Generate a master HTML index page that links to all 34 individual OSCE reports, with:
- Filtering by station type (History Taking / Physical Exam / Communication)
- Progress indicator (how many complete vs pending)
- Search by topic keyword
- Direct links to HTML reports

**Context**: The master index is the primary entry point for students studying from this
collection. It should be usable as a standalone study dashboard.

---

## A — Architecture

### Input
- All `output/{slug}/metadata.json` files
- All `output/{slug}/analysis.json` files
- All `output/{slug}/status.json` files
- `pipeline_progress.json`

### Output
```
osce-pipeline/
└── index.html              ← master index (self-contained)
```

### Layout
```
Header: "OSCE Study Library — AMC Clinical Examination"
├── Stats bar: Total | Complete | History | Exam | Communication
├── Filter buttons: All | History Taking | Physical Exam | Communication
├── Search box (JavaScript, client-side)
└── Cards grid: one card per completed video
    ├── Station type badge (colour coded)
    ├── Topic title
    ├── Key differentials (from analysis.json)
    ├── Diagram count
    └── "Open Report" button → links to report.html
```

---

## L — Loop / Phases

### Phase 1: Collect All Metadata
```python
VENV = "/home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv"
# Run with: $VENV/bin/python generate_index.py

import json
from pathlib import Path

PIPELINE = Path("/home/dev/Development/irStudy/osce-pipeline")
OUTPUT = PIPELINE / "output"

reports = []
for slug_dir in sorted(OUTPUT.iterdir()):
    if not slug_dir.is_dir():
        continue
    status_file = slug_dir / "status.json"
    if not status_file.exists():
        continue
    status = json.loads(status_file.read_text())
    if status.get("step") != "complete":
        continue  # only include completed reports

    metadata = json.loads((slug_dir / "metadata.json").read_text()) if (slug_dir / "metadata.json").exists() else {}
    analysis = json.loads((slug_dir / "analysis.json").read_text()) if (slug_dir / "analysis.json").exists() else {}
    diagrams = json.loads((slug_dir / "diagrams_manifest.json").read_text()) if (slug_dir / "diagrams_manifest.json").exists() else []

    reports.append({
        "slug": slug_dir.name,
        "title": metadata.get("title", slug_dir.name.replace("_", " ").title()),
        "station_type": analysis.get("station_type", "unknown"),
        "ddx": analysis.get("ddx_mentioned", []),
        "diagram_count": len(diagrams),
        "report_path": f"output/{slug_dir.name}/report.html"
    })

print(f"Found {len(reports)} completed reports")
```

### Phase 2: Generate Index HTML
```python
BADGE_COLORS = {
    "history_taking":       ("#3498DB", "History Taking"),
    "physical_examination": ("#27AE60", "Physical Exam"),
    "communication":        ("#9B59B6", "Communication"),
    "unknown":              ("#95A5A6", "Unknown"),
}

def make_card(r):
    color, label = BADGE_COLORS.get(r["station_type"], ("#95A5A6", "Unknown"))
    ddx_str = ", ".join(r["ddx"][:3]) if r["ddx"] else "See report"
    return f"""
    <div class="card" data-type="{r['station_type']}">
      <div class="card-header" style="background:{color}">
        <span class="card-type">{label}</span>
        <span class="card-diagrams">{r['diagram_count']} diagrams</span>
      </div>
      <div class="card-body">
        <h3>{r['title'][:80]}</h3>
        <p class="ddx">Differentials: {ddx_str}</p>
      </div>
      <div class="card-footer">
        <a href="{r['report_path']}" target="_blank" class="btn">Open Report</a>
      </div>
    </div>"""

total = len(reports)
by_type = {t: sum(1 for r in reports if r["station_type"] == t)
           for t in ["history_taking", "physical_examination", "communication"]}

cards_html = "\n".join(make_card(r) for r in reports)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>OSCE Study Library — AMC Clinical Examination</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f4f8; }}
  .header {{ background: #2C3E50; color: white; padding: 2rem; text-align: center; }}
  .header h1 {{ font-size: 2rem; }}
  .stats {{ display: flex; justify-content: center; gap: 2rem; padding: 1.5rem;
             background: #34495E; color: white; }}
  .stat {{ text-align: center; }}
  .stat-num {{ font-size: 2rem; font-weight: bold; }}
  .stat-label {{ font-size: 0.8rem; opacity: 0.8; }}
  .filters {{ display: flex; justify-content: center; gap: 1rem; padding: 1.5rem;
              background: white; border-bottom: 1px solid #ddd; flex-wrap: wrap; }}
  .filter-btn {{ padding: 0.5rem 1.5rem; border: 2px solid #ddd; border-radius: 20px;
                 background: white; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; }}
  .filter-btn.active, .filter-btn:hover {{ background: #2C3E50; color: white; border-color: #2C3E50; }}
  .search-bar {{ padding: 1rem 2rem; background: white; border-bottom: 1px solid #eee; }}
  .search-bar input {{ width: 100%; max-width: 600px; display: block; margin: 0 auto;
                        padding: 0.75rem 1rem; border: 2px solid #ddd; border-radius: 8px;
                        font-size: 1rem; outline: none; }}
  .search-bar input:focus {{ border-color: #3498DB; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }}
  .card {{ background: white; border-radius: 10px; overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }}
  .card[hidden] {{ display: none; }}
  .card-header {{ padding: 0.75rem 1rem; display: flex; justify-content: space-between;
                   align-items: center; color: white; }}
  .card-type {{ font-weight: 600; font-size: 0.85rem; }}
  .card-diagrams {{ font-size: 0.8rem; opacity: 0.9; }}
  .card-body {{ padding: 1rem; }}
  .card-body h3 {{ font-size: 1rem; margin-bottom: 0.5rem; color: #2c3e50; line-height: 1.4; }}
  .ddx {{ color: #7f8c8d; font-size: 0.85rem; }}
  .card-footer {{ padding: 0.75rem 1rem; border-top: 1px solid #f0f0f0; }}
  .btn {{ display: inline-block; background: #3498DB; color: white; padding: 0.5rem 1.5rem;
           border-radius: 6px; text-decoration: none; font-size: 0.9rem;
           transition: background 0.2s; }}
  .btn:hover {{ background: #2980B9; }}
  .no-results {{ text-align: center; padding: 3rem; color: #95a5a6; display: none; }}
  .footer {{ text-align: center; padding: 2rem; color: #95a5a6; font-size: 0.85rem; }}
</style>
</head>
<body>
<div class="header">
  <h1>OSCE Study Library</h1>
  <p>AMC Clinical Examination Reference Collection</p>
</div>
<div class="stats">
  <div class="stat"><div class="stat-num">{total}</div><div class="stat-label">Total Stations</div></div>
  <div class="stat"><div class="stat-num">{by_type.get('history_taking', 0)}</div><div class="stat-label">History Taking</div></div>
  <div class="stat"><div class="stat-num">{by_type.get('physical_examination', 0)}</div><div class="stat-label">Physical Exam</div></div>
  <div class="stat"><div class="stat-num">{by_type.get('communication', 0)}</div><div class="stat-label">Communication</div></div>
</div>
<div class="filters">
  <button class="filter-btn active" onclick="filterCards('all', this)">All Stations</button>
  <button class="filter-btn" onclick="filterCards('history_taking', this)">History Taking</button>
  <button class="filter-btn" onclick="filterCards('physical_examination', this)">Physical Exam</button>
  <button class="filter-btn" onclick="filterCards('communication', this)">Communication</button>
</div>
<div class="search-bar">
  <input type="text" id="searchInput" placeholder="Search by topic, diagnosis, or keyword..."
         oninput="searchCards(this.value)">
</div>
<div class="container">
  <div class="grid" id="cardGrid">
    {cards_html}
  </div>
  <div class="no-results" id="noResults">No stations match your search.</div>
</div>
<div class="footer">
  AMC Clinical Examination Reference Material | {total} stations
</div>
<script>
let activeFilter = 'all';
let activeSearch = '';

function filterCards(type, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  activeFilter = type;
  applyFilters();
}}

function searchCards(query) {{
  activeSearch = query.toLowerCase();
  applyFilters();
}}

function applyFilters() {{
  const cards = document.querySelectorAll('.card');
  let visible = 0;
  cards.forEach(card => {{
    const typeMatch = activeFilter === 'all' || card.dataset.type === activeFilter;
    const text = card.textContent.toLowerCase();
    const searchMatch = !activeSearch || text.includes(activeSearch);
    const show = typeMatch && searchMatch;
    card.hidden = !show;
    if (show) visible++;
  }});
  document.getElementById('noResults').style.display = visible === 0 ? 'block' : 'none';
}}
</script>
</body>
</html>"""

(PIPELINE / "index.html").write_text(html, encoding="utf-8")
print(f"Master index: osce-pipeline/index.html ({len(html):,} chars)")
```

---

## P — Plan / Tasks

| Task | Script | Acceptance Criterion |
|------|--------|---------------------|
| Collect all metadata | `scripts/09_index.py` | Reads all complete slug dirs |
| Generate index HTML | included | `index.html` > 10KB |
| Validate filter JS | manual | Filter buttons hide/show cards |
| Validate search | manual | Typing filters cards in real-time |

---

## H — Handoff / Acceptance

### Done When:
- [ ] `osce-pipeline/index.html` exists and opens in browser
- [ ] All completed reports appear as cards
- [ ] Filter buttons work (All / History / Exam / Communication)
- [ ] Search box filters cards in real-time
- [ ] "Open Report" links open individual HTML reports
- [ ] Stats bar shows correct counts

### Pipeline Complete: All 34 OSCE videos processed and accessible via master index.
