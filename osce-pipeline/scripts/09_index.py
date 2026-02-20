#!/usr/bin/env python3
"""
PRD_OSCE_008: Master Index Generator
Usage: $MSDEV_VENV/bin/python 09_index.py
"""
import json, datetime
from pathlib import Path

PIPELINE = Path("/home/dev/Development/irStudy/osce-pipeline")
OUTPUT = PIPELINE / "output"

BADGE_COLORS = {
    "history_taking":       ("#3498DB", "History Taking"),
    "physical_examination": ("#27AE60", "Physical Exam"),
    "communication":        ("#9B59B6", "Communication"),
    "unknown":              ("#95A5A6", "Unknown"),
}

reports = []
for slug_dir in sorted(OUTPUT.iterdir()):
    if not slug_dir.is_dir():
        continue
    status_file = slug_dir / "status.json"
    if not status_file.exists():
        continue
    try:
        status = json.loads(status_file.read_text())
    except:
        continue
    if status.get("step") != "complete":
        continue

    metadata = {}
    analysis = {}
    diagrams = []

    if (slug_dir / "metadata.json").exists():
        try:
            metadata = json.loads((slug_dir / "metadata.json").read_text())
        except:
            pass
    if (slug_dir / "analysis.json").exists():
        try:
            analysis = json.loads((slug_dir / "analysis.json").read_text())
        except:
            pass
    if (slug_dir / "diagrams_manifest.json").exists():
        try:
            diagrams = json.loads((slug_dir / "diagrams_manifest.json").read_text())
        except:
            pass

    reports.append({
        "slug": slug_dir.name,
        "title": metadata.get("title", slug_dir.name.replace("_", " ").title()),
        "station_type": analysis.get("station_type", "unknown"),
        "ddx": analysis.get("ddx_mentioned", []),
        "diagram_count": len(diagrams),
        "report_path": f"output/{slug_dir.name}/report.html"
    })

total = len(reports)
by_type = {
    "history_taking": sum(1 for r in reports if r["station_type"] == "history_taking"),
    "physical_examination": sum(1 for r in reports if r["station_type"] == "physical_examination"),
    "communication": sum(1 for r in reports if r["station_type"] == "communication"),
}

print(f"Building index for {total} completed reports...")

def make_card(r):
    color, label = BADGE_COLORS.get(r["station_type"], ("#95A5A6", "Unknown"))
    ddx_str = ", ".join(r["ddx"][:3]) if r["ddx"] else "See report"
    return f"""
    <div class="card" data-type="{r['station_type']}" data-title="{r['title'].lower()}" data-ddx="{ddx_str.lower()}">
      <div class="card-header" style="background:{color}">
        <span class="card-type">{label}</span>
        <span class="card-diagrams">{r['diagram_count']} diagrams</span>
      </div>
      <div class="card-body">
        <h3 title="{r['title']}">{r['title'][:75]}{'...' if len(r['title']) > 75 else ''}</h3>
        <p class="ddx">{ddx_str}</p>
      </div>
      <div class="card-footer">
        <a href="{r['report_path']}" target="_blank" class="btn">Open Report</a>
      </div>
    </div>"""

cards_html = "\n".join(make_card(r) for r in reports)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OSCE Study Library — AMC Clinical Examination</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f4f8; }}
  .header {{ background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
              color: white; padding: 2.5rem; text-align: center; }}
  .header h1 {{ font-size: 2.2rem; margin-bottom: 0.5rem; }}
  .header p {{ opacity: 0.8; font-size: 1rem; }}
  .stats {{ display: flex; justify-content: center; gap: 3rem; padding: 1.5rem 2rem;
             background: #34495E; color: white; flex-wrap: wrap; }}
  .stat {{ text-align: center; }}
  .stat-num {{ font-size: 2.5rem; font-weight: 700; line-height: 1; }}
  .stat-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;
                  opacity: 0.75; margin-top: 0.25rem; }}
  .controls {{ background: white; border-bottom: 1px solid #e8ecef; padding: 1rem 2rem; }}
  .filters {{ display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap;
               margin-bottom: 1rem; }}
  .filter-btn {{ padding: 0.5rem 1.5rem; border: 2px solid #ddd; border-radius: 20px;
                  background: white; cursor: pointer; font-size: 0.9rem; transition: all 0.2s;
                  font-family: inherit; }}
  .filter-btn.active, .filter-btn:hover {{ background: #2C3E50; color: white; border-color: #2C3E50; }}
  .search-wrap {{ display: flex; justify-content: center; }}
  .search-wrap input {{ width: 100%; max-width: 550px; padding: 0.75rem 1.25rem;
                          border: 2px solid #e0e0e0; border-radius: 25px; font-size: 1rem;
                          outline: none; transition: border-color 0.2s; font-family: inherit; }}
  .search-wrap input:focus {{ border-color: #3498DB; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }}
  .card {{ background: white; border-radius: 10px; overflow: hidden; display: flex;
            flex-direction: column; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
            transition: transform 0.2s, box-shadow 0.2s; }}
  .card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }}
  .card[hidden] {{ display: none !important; }}
  .card-header {{ padding: 0.875rem 1rem; display: flex; justify-content: space-between;
                   align-items: center; color: white; flex-shrink: 0; }}
  .card-type {{ font-weight: 700; font-size: 0.8rem; text-transform: uppercase;
                 letter-spacing: 0.5px; }}
  .card-diagrams {{ font-size: 0.75rem; opacity: 0.9;
                     background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px; }}
  .card-body {{ padding: 1rem; flex: 1; }}
  .card-body h3 {{ font-size: 0.95rem; margin-bottom: 0.5rem; color: #2c3e50; line-height: 1.4; }}
  .ddx {{ color: #7f8c8d; font-size: 0.8rem; }}
  .card-footer {{ padding: 0.75rem 1rem; border-top: 1px solid #f0f0f0; }}
  .btn {{ display: inline-block; background: #3498DB; color: white; padding: 0.5rem 1.5rem;
           border-radius: 6px; text-decoration: none; font-size: 0.9rem; font-weight: 500;
           transition: background 0.2s; }}
  .btn:hover {{ background: #2980B9; }}
  .no-results {{ text-align: center; padding: 4rem; color: #95a5a6; display: none;
                  grid-column: 1/-1; }}
  .footer {{ text-align: center; padding: 2rem; color: #95a5a6; font-size: 0.8rem;
              border-top: 1px solid #e8ecef; margin-top: 1rem; }}
</style>
</head>
<body>
<div class="header">
  <h1>OSCE Study Library</h1>
  <p>AMC Clinical Examination Reference Collection</p>
</div>
<div class="stats">
  <div class="stat">
    <div class="stat-num">{total}</div>
    <div class="stat-label">Total Stations</div>
  </div>
  <div class="stat">
    <div class="stat-num" style="color:#3498DB">{by_type.get('history_taking', 0)}</div>
    <div class="stat-label">History Taking</div>
  </div>
  <div class="stat">
    <div class="stat-num" style="color:#27AE60">{by_type.get('physical_examination', 0)}</div>
    <div class="stat-label">Physical Exam</div>
  </div>
  <div class="stat">
    <div class="stat-num" style="color:#9B59B6">{by_type.get('communication', 0)}</div>
    <div class="stat-label">Communication</div>
  </div>
</div>
<div class="controls">
  <div class="filters">
    <button class="filter-btn active" onclick="filterCards('all', this)">All Stations</button>
    <button class="filter-btn" onclick="filterCards('history_taking', this)" style="border-color:#3498DB">History Taking</button>
    <button class="filter-btn" onclick="filterCards('physical_examination', this)" style="border-color:#27AE60">Physical Exam</button>
    <button class="filter-btn" onclick="filterCards('communication', this)" style="border-color:#9B59B6">Communication</button>
  </div>
  <div class="search-wrap">
    <input type="text" id="searchInput" placeholder="Search by topic, diagnosis, keyword..."
           oninput="searchCards(this.value)" autocomplete="off">
  </div>
</div>
<div class="container">
  <div class="grid" id="cardGrid">
    {cards_html}
    <div class="no-results" id="noResults">No stations match your search.</div>
  </div>
</div>
<div class="footer">
  AMC Clinical Examination Reference Material &bull; {total} stations &bull;
  Generated {datetime.datetime.now().strftime("%d %B %Y")}
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
  activeSearch = query.toLowerCase().trim();
  applyFilters();
}}

function applyFilters() {{
  const cards = document.querySelectorAll('.card:not(.no-results)');
  let visible = 0;
  cards.forEach(card => {{
    const typeMatch = activeFilter === 'all' || card.dataset.type === activeFilter;
    const searchMatch = !activeSearch ||
      (card.dataset.title || '').includes(activeSearch) ||
      (card.dataset.ddx || '').includes(activeSearch) ||
      card.textContent.toLowerCase().includes(activeSearch);
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
print(f"Master index: {PIPELINE / 'index.html'} ({len(html):,} chars)")
print(f"Total reports indexed: {total}")
