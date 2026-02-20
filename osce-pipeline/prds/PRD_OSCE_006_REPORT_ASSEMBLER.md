# PRD_OSCE_006_REPORT_ASSEMBLER

## R — Request

Combine clinical notes, diagrams, and metadata into two output formats per OSCE station:
1. **HTML report** — self-contained (base64 embedded diagrams), professional styling
2. **Markdown study notes** — portable, renderable in any markdown viewer

**Context**: Reports are authoritative clinical references for AMC exam preparation.
No mention of source video, recording, or "missing" content anywhere in outputs.

---

## A — Architecture

### Input Files
```
output/{slug}/
├── metadata.json           ← title, duration
├── analysis.json           ← station_type, presenting_complaint, ddx
├── clinical_notes.md       ← enhanced notes from PRD_004
├── key_facts.json          ← structured data
├── screenshots/            ← PNG frames
├── diagrams/               ← PNG diagrams
└── diagrams_manifest.json  ← list of generated diagram paths
```

### Output Files
```
output/{slug}/
├── report.html             ← self-contained HTML (1-3MB)
└── report.md               ← portable Markdown study notes
```

### HTML Report Structure
```
Header: Station title + type badge + AMC reference
├── Section 1: Station Overview (presenting complaint, station type, time)
├── Section 2: All Diagrams (grid layout, labelled, base64 embedded)
├── Section 3: Clinical Notes (formatted HTML from markdown)
├── Section 4: Key Facts (AMC exam bullets)
├── Section 5: Red Flags (highlighted callout boxes)
└── Footer: AMC Clinical Examination reference
```

### Markdown Report Structure
```
# {Title}
## Station Overview
## Clinical Framework
## Key Diagrams (links to PNG files)
## Notes
## Red Flags
## Key Facts for AMC
```

---

## L — Loop / Phases

### Phase 1: Load All Data
```python
VENV = "/home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv"
# Run with: $VENV/bin/python assemble_report.py {slug}

import json, base64, markdown
from pathlib import Path

SLUG = sys.argv[1]
BASE = Path(f"output/{SLUG}")

metadata = json.loads((BASE / "metadata.json").read_text())
analysis = json.loads((BASE / "analysis.json").read_text())
key_facts = json.loads((BASE / "key_facts.json").read_text())
notes_md = (BASE / "clinical_notes.md").read_text()
diagrams = json.loads((BASE / "diagrams_manifest.json").read_text())
```

### Phase 2: Base64 Encode All Diagrams
```python
def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

diagram_data = []
for path in diagrams:
    b64 = encode_image(path)
    label = Path(path).stem.replace("_", " ").title()
    diagram_data.append({"label": label, "b64": b64, "path": path})
```

### Phase 3: Generate HTML
```python
# Convert markdown notes to HTML
notes_html = markdown.markdown(notes_md, extensions=["tables", "fenced_code", "toc"])

station_badge_color = {
    "history_taking": "#3498DB",
    "physical_examination": "#27AE60",
    "communication": "#9B59B6"
}[analysis["station_type"]]

station_label = analysis["station_type"].replace("_", " ").title()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{metadata.get('title', SLUG)} — OSCE Reference</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background: #f5f7fa; color: #2c3e50; }}
  .header {{ background: #2C3E50; color: white; padding: 2rem; }}
  .badge {{ display: inline-block; background: {station_badge_color}; color: white;
            padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-left: 1rem; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
  .section {{ background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem;
              box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .diagrams-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
                    gap: 1.5rem; }}
  .diagram-card {{ border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }}
  .diagram-card img {{ width: 100%; height: auto; display: block; }}
  .diagram-label {{ padding: 0.75rem 1rem; background: #f8f9fa; font-weight: 600;
                    font-size: 0.9rem; color: #2c3e50; border-top: 1px solid #e0e0e0; }}
  .red-flag {{ background: #FFF3F3; border-left: 4px solid #E74C3C; padding: 0.75rem 1rem;
               margin: 0.5rem 0; border-radius: 0 4px 4px 0; }}
  .key-fact {{ background: #F0FFF4; border-left: 4px solid #27AE60; padding: 0.75rem 1rem;
               margin: 0.5rem 0; border-radius: 0 4px 4px 0; }}
  .footer {{ text-align: center; padding: 2rem; color: #95a5a6; font-size: 0.85rem; }}
  h1,h2,h3 {{ color: #2c3e50; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th,td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
  th {{ background: #f2f2f2; }}
</style>
</head>
<body>
<div class="header">
  <h1>{metadata.get('title', SLUG).title()}
  <span class="badge">{station_label}</span></h1>
  <p>AMC Clinical Examination Reference Material</p>
</div>
<div class="container">

  <div class="section">
    <h2>Station Overview</h2>
    <p><strong>Station Type:</strong> {station_label}</p>
    <p><strong>Presenting Complaint:</strong> {analysis.get('presenting_complaint', 'N/A')[:300]}</p>
    <p><strong>Key Differentials:</strong> {', '.join(analysis.get('ddx_mentioned', [])) or 'See clinical notes'}</p>
  </div>

  <div class="section">
    <h2>Clinical Diagrams ({len(diagram_data)} diagrams)</h2>
    <div class="diagrams-grid">
"""
for d in diagram_data:
    html += f"""
      <div class="diagram-card">
        <img src="data:image/png;base64,{d['b64']}" alt="{d['label']}">
        <div class="diagram-label">{d['label']}</div>
      </div>"""

red_flags = key_facts.get("red_flags", [])
key_facts_list = key_facts.get("amc_criteria", [])

html += f"""
    </div>
  </div>

  <div class="section">
    <h2>Clinical Notes</h2>
    {notes_html}
  </div>
"""

if red_flags:
    html += '<div class="section"><h2>Red Flags</h2>'
    for rf in red_flags:
        html += f'<div class="red-flag"><strong>Red Flag:</strong> {rf}</div>'
    html += '</div>'

if key_facts_list:
    html += '<div class="section"><h2>AMC Key Facts</h2>'
    for kf in key_facts_list:
        html += f'<div class="key-fact">{kf}</div>'
    html += '</div>'

html += f"""
  <div class="footer">
    AMC Clinical Examination Reference | Australian Medical Council Standards
  </div>
</div>
</body>
</html>"""

(BASE / "report.html").write_text(html, encoding="utf-8")
print(f"HTML report: output/{SLUG}/report.html ({len(html):,} chars)")
```

### Phase 4: Generate Markdown
```python
md = f"""# {metadata.get('title', SLUG).title()}

**Station Type:** {station_label}
**AMC Reference:** Clinical Examination Standards

## Station Overview

- **Presenting Complaint:** {analysis.get('presenting_complaint', '')[:200]}
- **Key Differentials:** {', '.join(analysis.get('ddx_mentioned', []))}
- **Investigations:** {', '.join(analysis.get('investigations_mentioned', []))}

## Diagrams

"""
for d in diagram_data:
    rel_path = Path(d['path']).relative_to(BASE)
    md += f"### {d['label']}\n![{d['label']}]({rel_path})\n\n"

md += "\n## Clinical Notes\n\n" + notes_md

if red_flags:
    md += "\n## Red Flags\n\n"
    for rf in red_flags:
        md += f"- **{rf}**\n"

if key_facts_list:
    md += "\n## AMC Key Facts\n\n"
    for kf in key_facts_list:
        md += f"- {kf}\n"

(BASE / "report.md").write_text(md, encoding="utf-8")
print(f"Markdown: output/{SLUG}/report.md")
```

---

## P — Plan / Tasks

| Task | Script | Acceptance Criterion |
|------|--------|---------------------|
| Load all data | `scripts/07_assemble.py` | No JSON parse errors |
| Generate HTML | included | `report.html` > 100KB |
| Generate Markdown | included | `report.md` > 5KB |
| Update status | bash | `status.json` shows step=complete |

---

## H — Handoff / Acceptance

### Done When:
- [ ] `report.html` exists and is valid HTML (> 100KB)
- [ ] `report.html` opens in browser showing diagrams inline
- [ ] `report.md` exists (> 5KB)
- [ ] No references to "video", "recording", "missing" in either file
- [ ] `status.json` shows `"step": "complete"`

### Hands Off To: PRD_OSCE_007_BATCH_ORCHESTRATOR (for next video)
