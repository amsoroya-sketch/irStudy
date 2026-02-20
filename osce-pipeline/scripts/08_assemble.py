#!/usr/bin/env python3
"""
PRD_OSCE_006: Report Assembler (v3 — inline diagrams + enhanced content highlighting)
Usage: $MSDEV_VENV/bin/python 08_assemble.py <slug>

Layout:
  - Clinical notes rendered as flowing book chapter
  - Diagrams injected inline (float-right) beside the relevant section
  - Sections enriched beyond source material highlighted with subtle tint + badge
  - Key facts panel (red flags | differentials | AMC tips)
  - Dual output: self-contained HTML + book-ready Markdown
"""

import sys, json, base64, datetime, re
from pathlib import Path

try:
    import markdown as md_lib
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

SLUG = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Usage: 08_assemble.py <slug>")
BASE = Path(f"/home/dev/Development/irStudy/osce-pipeline/output/{SLUG}")

# Load all data
metadata          = json.loads((BASE / "metadata.json").read_text())          if (BASE / "metadata.json").exists()          else {"title": SLUG}
analysis          = json.loads((BASE / "analysis.json").read_text())          if (BASE / "analysis.json").exists()          else {}
key_facts         = json.loads((BASE / "key_facts.json").read_text())         if (BASE / "key_facts.json").exists()         else {}
notes_md          = (BASE / "clinical_notes.md").read_text(encoding="utf-8") if (BASE / "clinical_notes.md").exists()       else None
diagrams_manifest = json.loads((BASE / "diagrams_manifest.json").read_text()) if (BASE / "diagrams_manifest.json").exists() else []

station_type  = analysis.get("station_type", "history_taking")
station_label = station_type.replace("_", " ").title()
title         = metadata.get("title", SLUG.replace("_", " ").title())
complaint     = analysis.get("presenting_complaint", "")[:400]
word_count    = len((BASE / "transcript.txt").read_text().split()) if (BASE / "transcript.txt").exists() else 0

BADGE_COLORS = {
    "history_taking":       "#3498DB",
    "physical_examination": "#27AE60",
    "communication":        "#9B59B6",
}
badge_color = BADGE_COLORS.get(station_type, "#95A5A6")

# ============================================================
# Load and base64 encode diagrams
# ============================================================
diagram_map = {}   # name_key → {label, b64, path}
for path_str in diagrams_manifest:
    path = Path(path_str)
    if path.exists():
        b64   = base64.b64encode(path.read_bytes()).decode("utf-8")
        stem  = path.stem   # e.g. "01_socrates_flow"
        raw   = stem.lstrip("0123456789").lstrip("_")          # "socrates_flow"
        label = raw.replace("_", " ").title()                  # "Socrates Flow"
        diagram_map[raw] = {"label": label, "b64": b64, "path": str(path), "used": False}

# ============================================================
# Diagram → section heading keyword mapping
# Which diagram floats next to which section heading
# ============================================================
DIAGRAM_PLACEMENT = {
    # history_taking
    "socrates_flow":     ["socrates", "systematic approach", "opening", "history framework"],
    "differential_tree": ["differential", "diagnosis", "ddx"],
    "redflags_panel":    ["red flag", "must not miss", "alarm"],
    "management_flow":   ["management", "investigation", "safety net"],
    # physical_examination
    "exam_sequence":     ["systematic approach", "examination sequence", "station framework"],
    "findings_map":      ["regional", "findings", "abdominal region", "clinical signs"],
    "investigations_grid":["investigation", "bedside", "bloods", "imaging"],
    # communication
    "ice_framework":     ["ice", "ideas", "concerns", "expectations", "opening"],
    "counselling_pathway":["counselling", "communication", "station framework", "systematic"],
    "comm_domains":      ["amc exam", "key points", "communication domain"],
    # shared
    "04_differential_tree": ["differential", "diagnosis"],
}

def find_diagram_for_section(heading_lower):
    """Return diagram key that best matches this heading, or None."""
    for key, keywords in DIAGRAM_PLACEMENT.items():
        if any(kw in heading_lower for kw in keywords):
            # Check if diagram exists and not yet used
            if key in diagram_map and not diagram_map[key]["used"]:
                return key
    return None

# ============================================================
# Sections that are enhanced beyond source material
# (AI-enriched clinical knowledge, not transcribed content)
# ============================================================
ENHANCED_SECTIONS = {
    "amc exam tips",
    "high-yield",
    "safety net",
    "communication & patient education",
    "communication and patient education",
    "differential diagnosis",
    "investigations",
    "management",
    "red flags",
}

def is_enhanced_section(heading_lower):
    return any(kw in heading_lower for kw in ENHANCED_SECTIONS)

# ============================================================
# Parse markdown into sections, inject diagrams inline
# ============================================================
def build_notes_html_with_inline_diagrams(notes_md_text):
    """
    Split notes by ## headings. For each section:
    - Wrap in a div
    - If a diagram matches the heading, inject it as float-right
    - If section is enhanced, add highlight class
    Returns HTML string.
    """
    if not notes_md_text:
        return "<p><em>Enhancement pending.</em></p>"

    # Split on ## headings (keep the heading line)
    parts = re.split(r'(?=^## )', notes_md_text, flags=re.MULTILINE)

    html_sections = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Extract heading
        heading_match = re.match(r'^## (.+)$', part, re.MULTILINE)
        heading_text  = heading_match.group(1).strip() if heading_match else ""
        heading_lower = heading_text.lower()

        # Find diagram for this section
        diagram_key   = find_diagram_for_section(heading_lower)
        enhanced      = is_enhanced_section(heading_lower)

        # Convert this section's markdown to HTML
        section_md = part
        if HAS_MARKDOWN:
            section_html = md_lib.markdown(
                section_md,
                extensions=["tables", "fenced_code", "nl2br"]
            )
        else:
            section_html = "<pre>" + section_md.replace("<","&lt;").replace(">","&gt;") + "</pre>"

        # Build inline diagram HTML (float right)
        diagram_html = ""
        if diagram_key and diagram_key in diagram_map:
            d = diagram_map[diagram_key]
            diagram_map[diagram_key]["used"] = True
            diagram_html = f"""
<div class="inline-diagram">
  <img src="data:image/png;base64,{d['b64']}" alt="{d['label']}" loading="lazy">
  <div class="inline-diagram-label">{d['label']}</div>
</div>"""

        # Enhanced badge
        enhanced_badge = ""
        if enhanced and heading_text:
            enhanced_badge = '<span class="enhanced-badge">Clinically Enriched</span>'

        # Section class
        section_class = "notes-section"
        if enhanced:
            section_class += " notes-section-enhanced"
        if diagram_key:
            section_class += " has-diagram"

        html_sections.append(f"""
<div class="{section_class}">
{diagram_html}
<div class="section-body">
{f'<div class="section-heading-row">{enhanced_badge}</div>' if enhanced_badge else ''}
{section_html}
<div class="clearfix"></div>
</div>
</div>""")

    # Append any unused diagrams at the end in a small row
    unused = [d for d in diagram_map.values() if not d["used"]]
    if unused:
        extra = '<div class="unused-diagrams"><h3 class="unused-title">Additional Reference Diagrams</h3><div class="diagrams-row">'
        for d in unused:
            extra += f"""<div class="diagram-card-small">
  <img src="data:image/png;base64,{d['b64']}" alt="{d['label']}" loading="lazy">
  <div class="diagram-label-small">{d['label']}</div>
</div>"""
        extra += "</div></div>"
        html_sections.append(extra)

    return "\n".join(html_sections)


# ============================================================
# Build content
# ============================================================
has_notes = bool(notes_md)
if not notes_md:
    notes_md = "# Clinical Notes\n\nEnhancement pending."

notes_with_diagrams_html = build_notes_html_with_inline_diagrams(notes_md)

red_flags     = key_facts.get("red_flags", [])
amc_criteria  = key_facts.get("amc_criteria", [])
ddx           = key_facts.get("differential_diagnoses", []) or analysis.get("ddx_mentioned", [])
investigations= key_facts.get("investigations", []) or analysis.get("investigations_mentioned", [])
management    = key_facts.get("management_steps", [])

# ============================================================
# HTML Report
# ============================================================
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — AMC Clinical Reference</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    margin: 0;
    background: #f5f5f0;
    color: #1a1a2e;
    line-height: 1.78;
    font-size: 16px;
  }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    color: white;
    padding: 3rem 2rem 2rem;
    border-bottom: 4px solid {badge_color};
  }}
  .header h1 {{
    margin: 0 0 0.75rem;
    font-size: 2rem;
    line-height: 1.3;
    font-weight: 700;
    letter-spacing: -0.02em;
  }}
  .badge {{
    display: inline-block;
    background: {badge_color};
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 0.5rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }}
  .badge-dark {{ background: rgba(255,255,255,0.15); }}
  .header-meta {{
    margin-top: 1rem;
    opacity: 0.75;
    font-size: 0.85rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }}

  /* ── Layout ── */
  .container {{ max-width: 980px; margin: 0 auto; padding: 2.5rem 2rem; }}

  .card {{
    background: white;
    border-radius: 10px;
    padding: 2.25rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border: 1px solid #e8e8e0;
  }}
  .card > h2:first-child {{
    margin-top: 0;
    margin-bottom: 1.25rem;
    color: #1a1a2e;
    font-size: 1.3rem;
    border-bottom: 2px solid {badge_color}44;
    padding-bottom: 0.6rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }}

  /* ── Overview panel ── */
  .overview-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
    gap: 1rem;
    margin-bottom: 1.25rem;
  }}
  .overview-item {{
    background: #f8f8f5;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    border-left: 4px solid {badge_color};
    font-family: 'Segoe UI', system-ui, sans-serif;
  }}
  .overview-item .label {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #6b7280;
    font-weight: 700;
  }}
  .overview-item .value {{
    font-size: 0.95rem;
    color: #1a1a2e;
    margin-top: 0.2rem;
    font-weight: 600;
  }}
  .complaint-block {{
    background: #f0f4ff;
    border-left: 4px solid {badge_color};
    padding: 0.9rem 1.25rem;
    border-radius: 0 8px 8px 0;
    color: #374151;
    font-size: 0.95rem;
    font-style: italic;
    margin-top: 1rem;
  }}

  /* ── Notes sections — inline diagram layout ── */
  .notes-section {{
    margin-bottom: 2.25rem;
    padding-bottom: 1.75rem;
    border-bottom: 1px solid #f0f0ea;
  }}
  .notes-section:last-child {{ border-bottom: none; margin-bottom: 0; }}

  /* Enhanced section highlight */
  .notes-section-enhanced {{
    background: linear-gradient(to right, #f0f7ff 0%, transparent 60px);
    border-left: 3px solid {badge_color}88;
    padding-left: 1.25rem;
    margin-left: -1.25rem;
    border-radius: 0 8px 8px 0;
  }}

  .section-heading-row {{
    margin-bottom: 0.3rem;
  }}

  /* Enhanced badge */
  .enhanced-badge {{
    display: inline-block;
    background: {badge_color}18;
    color: {badge_color};
    border: 1px solid {badge_color}44;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 700;
    font-family: 'Segoe UI', system-ui, sans-serif;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    vertical-align: middle;
    margin-bottom: 0.4rem;
  }}

  /* ── Inline diagram (floats right beside text) ── */
  .inline-diagram {{
    float: right;
    clear: right;
    width: 42%;
    max-width: 400px;
    min-width: 260px;
    margin: 0 0 1.25rem 1.75rem;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    overflow: hidden;
    background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  }}
  .inline-diagram img {{
    width: 100%;
    height: auto;
    display: block;
  }}
  .inline-diagram-label {{
    padding: 0.55rem 0.85rem;
    background: #f8f8f5;
    font-size: 0.78rem;
    font-weight: 600;
    color: #6b7280;
    border-top: 1px solid #e5e7eb;
    font-family: 'Segoe UI', system-ui, sans-serif;
    text-align: center;
    letter-spacing: 0.02em;
  }}
  .clearfix::after {{
    content: "";
    display: table;
    clear: both;
  }}

  /* ── Notes typography ── */
  .section-body {{ font-size: 16px; line-height: 1.78; color: #1f2937; }}
  .section-body h2 {{
    font-size: 1.18rem;
    color: #1a1a2e;
    margin-top: 0;
    margin-bottom: 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #e5e7eb;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-weight: 700;
  }}
  .section-body h3 {{
    font-size: 1.02rem;
    color: #374151;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-weight: 600;
  }}
  .section-body p {{ margin-bottom: 1rem; }}
  .section-body ul, .section-body ol {{
    padding-left: 1.5rem;
    margin-bottom: 1rem;
  }}
  .section-body li {{ margin-bottom: 0.35rem; }}
  .section-body strong {{ color: #111827; }}
  .section-body em {{ color: #374151; }}
  .section-body table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1.25rem 0;
    font-size: 0.88rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }}
  .section-body th, .section-body td {{
    border: 1px solid #d1d5db;
    padding: 8px 12px;
    text-align: left;
  }}
  .section-body th {{
    background: {badge_color}18;
    font-weight: 700;
    color: #1a1a2e;
  }}
  .section-body tr:nth-child(even) td {{ background: #f9fafb; }}
  .section-body blockquote {{
    border-left: 4px solid {badge_color};
    background: #f0f4ff;
    padding: 0.7rem 1.1rem;
    margin: 1rem 0;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #374151;
  }}
  .section-body hr {{
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 1.5rem 0;
  }}

  /* ── Key facts panel ── */
  .keyfacts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 1.25rem;
  }}
  .kf-panel {{
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    border: 1px solid #e5e7eb;
  }}
  .kf-panel h3 {{
    margin: 0 0 0.65rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-weight: 700;
  }}
  .kf-panel ul {{
    margin: 0;
    padding-left: 1.15rem;
    font-size: 0.88rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }}
  .kf-panel li {{ margin-bottom: 0.28rem; line-height: 1.5; }}
  .kf-red   {{ background: #fff5f5; border-left: 4px solid #ef4444; }}
  .kf-red  h3 {{ color: #dc2626; }}
  .kf-blue  {{ background: #eff6ff; border-left: 4px solid #3b82f6; }}
  .kf-blue h3 {{ color: #1d4ed8; }}
  .kf-green {{ background: #f0fdf4; border-left: 4px solid #22c55e; }}
  .kf-green h3 {{ color: #16a34a; }}

  /* ── Unused diagrams row ── */
  .unused-diagrams {{ margin-top: 1.5rem; }}
  .unused-title {{
    font-size: 0.85rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-weight: 600;
    margin-bottom: 0.75rem;
  }}
  .diagrams-row {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.25rem;
  }}
  .diagram-card-small {{
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    background: white;
  }}
  .diagram-card-small img {{ width: 100%; height: auto; display: block; }}
  .diagram-label-small {{
    padding: 0.5rem 0.75rem;
    background: #f8f8f5;
    font-size: 0.78rem;
    font-weight: 600;
    color: #6b7280;
    border-top: 1px solid #e5e7eb;
    font-family: 'Segoe UI', system-ui, sans-serif;
    text-align: center;
  }}

  /* ── Legend ── */
  .legend {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 0.75rem 1.25rem;
    background: #f8f8f5;
    border-radius: 8px;
    border: 1px solid #e8e8e0;
    margin-bottom: 1.5rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 0.82rem;
    color: #6b7280;
    flex-wrap: wrap;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 0.5rem; }}
  .legend-swatch-enhanced {{
    width: 14px; height: 14px;
    background: {badge_color}18;
    border: 1px solid {badge_color}66;
    border-left: 3px solid {badge_color};
    border-radius: 2px;
  }}
  .legend-swatch-source {{
    width: 14px; height: 14px;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 2px;
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center;
    padding: 2rem;
    color: #9ca3af;
    font-size: 0.8rem;
    border-top: 1px solid #e8e8e0;
    margin-top: 2rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }}

  /* ── Responsive ── */
  @media (max-width: 700px) {{
    .inline-diagram {{
      float: none;
      width: 100%;
      max-width: 100%;
      margin: 1rem 0;
    }}
    .overview-grid {{ grid-template-columns: 1fr 1fr; }}
    .keyfacts-grid {{ grid-template-columns: 1fr; }}
    .container {{ padding: 1.25rem; }}
    .card {{ padding: 1.5rem; }}
    .notes-section-enhanced {{ padding-left: 0.75rem; margin-left: -0.75rem; }}
  }}

  @media print {{
    body {{ background: white; font-size: 12pt; }}
    .header {{ background: #1a1a2e !important; -webkit-print-color-adjust: exact; }}
    .card {{ box-shadow: none; border: 1px solid #ddd; page-break-inside: avoid; }}
    .inline-diagram {{ max-width: 35%; }}
    .legend {{ display: none; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>{title}</h1>
  <div>
    <span class="badge">{station_label}</span>
    <span class="badge badge-dark">AMC Clinical Examination</span>
  </div>
  <div class="header-meta">Australian Medical Council Reference Material &bull; {datetime.datetime.now().strftime("%B %Y")}</div>
</div>

<div class="container">

  <!-- Station Overview -->
  <div class="card">
    <h2>Station Overview</h2>
    <div class="overview-grid">
      <div class="overview-item">
        <div class="label">Station Type</div>
        <div class="value">{station_label}</div>
      </div>
      <div class="overview-item">
        <div class="label">Time Allocation</div>
        <div class="value">8 minutes</div>
      </div>
      <div class="overview-item">
        <div class="label">Transcript Length</div>
        <div class="value">{word_count:,} words</div>
      </div>
      <div class="overview-item">
        <div class="label">Key Differentials</div>
        <div class="value">{', '.join(ddx[:2]) if ddx else '—'}</div>
      </div>
    </div>
    {f'<div class="complaint-block"><strong>Clinical context:</strong> {complaint}</div>' if complaint else ''}
  </div>

  <!-- Clinical Notes -->
  <div class="card">
    <h2>Clinical Notes {"" if has_notes else "<span style='color:#ef4444;font-size:0.8em;font-weight:normal'>(pending)</span>"}</h2>

    <!-- Legend -->
    <div class="legend">
      <span style="font-weight:600;color:#374151;">Key:</span>
      <span class="legend-item">
        <span class="legend-swatch-source"></span>
        Source-grounded content
      </span>
      <span class="legend-item">
        <span class="legend-swatch-enhanced"></span>
        <span class="enhanced-badge" style="margin:0">Clinically Enriched</span>
        &nbsp;Sections with additional clinical depth
      </span>
      <span class="legend-item" style="margin-left:auto;font-style:italic;">
        Diagrams appear inline beside the relevant section
      </span>
    </div>

    {notes_with_diagrams_html}
  </div>

"""

# Key facts panel
if red_flags or ddx or amc_criteria or investigations:
    html += '  <div class="card">\n    <h2>Key Facts &amp; Clinical Priorities</h2>\n    <div class="keyfacts-grid">\n'
    if red_flags:
        items = "".join(f"<li>{rf}</li>" for rf in red_flags[:8])
        html += f'      <div class="kf-panel kf-red"><h3>Red Flags — Must Not Miss</h3><ul>{items}</ul></div>\n'
    if ddx:
        items = "".join(f"<li>{d}</li>" for d in ddx[:8])
        html += f'      <div class="kf-panel kf-blue"><h3>Differential Diagnoses</h3><ul>{items}</ul></div>\n'
    if amc_criteria:
        items = "".join(f"<li>{kf}</li>" for kf in amc_criteria[:8])
        html += f'      <div class="kf-panel kf-green"><h3>AMC Exam Key Points</h3><ul>{items}</ul></div>\n'
    elif investigations:
        items = "".join(f"<li>{inv}</li>" for inv in investigations[:8])
        html += f'      <div class="kf-panel kf-green"><h3>Key Investigations</h3><ul>{items}</ul></div>\n'
    html += '    </div>\n  </div>\n'

html += f"""
  <div class="footer">
    AMC Clinical Examination Reference Material &bull; Australian Medical Council Standards<br>
    Generated: {datetime.datetime.now().strftime("%d %B %Y")} &bull; Transcript: {word_count:,} words
  </div>

</div>
</body>
</html>"""

(BASE / "report.html").write_text(html, encoding="utf-8")
print(f"HTML report: {len(html):,} chars → {BASE / 'report.html'}")


# ============================================================
# Markdown (book-ready source of truth)
# ============================================================
now_str = datetime.datetime.now().strftime("%d %B %Y")

md_lines = [
    f"# {title}",
    "",
    f"> **Station Type:** {station_label}  ",
    f"> **AMC Reference:** Clinical Examination Standards  ",
    f"> **Transcript:** {word_count:,} words  ",
    f"> **Generated:** {now_str}",
    "",
    "---",
    "",
    "## Station Overview",
    "",
    f"- **Station Type:** {station_label}",
    f"- **Time Allocation:** 8 minutes (standard AMC OSCE)",
]
if ddx:
    md_lines.append(f"- **Key Differentials:** {', '.join(ddx[:5])}")
if investigations:
    md_lines.append(f"- **Key Investigations:** {', '.join(investigations[:5])}")
if complaint:
    md_lines += ["", f"**Clinical Context:** {complaint}", ""]

md_lines += ["", "---", "", notes_md, ""]

if red_flags:
    md_lines += ["---", "", "## Red Flags — Must Not Miss", ""]
    for rf in red_flags:
        md_lines.append(f"- **{rf}**")
    md_lines.append("")

if amc_criteria:
    md_lines += ["---", "", "## AMC Exam Key Points", ""]
    for kf in amc_criteria:
        md_lines.append(f"- {kf}")
    md_lines.append("")

if management:
    md_lines += ["---", "", "## Management Summary", ""]
    for i, step in enumerate(management, 1):
        md_lines.append(f"{i}. {step}")
    md_lines.append("")

# Diagrams section (relative paths for portability)
all_diagrams = [d for d in diagram_map.values()]
if all_diagrams:
    md_lines += ["---", "", "## Clinical Diagrams", ""]
    for d in all_diagrams:
        rel = Path(d["path"]).relative_to(BASE)
        md_lines += [f"### {d['label']}", f"", f"![{d['label']}]({rel})", ""]

md_lines += [
    "---",
    "",
    f"*AMC Clinical Examination Reference Material — Australian Medical Council Standards*  ",
    f"*Generated: {now_str}*",
]

md_content = "\n".join(md_lines)
(BASE / "report.md").write_text(md_content, encoding="utf-8")
print(f"Markdown report: {len(md_content):,} chars → {BASE / 'report.md'}")

# Update status
diagram_count = len([d for d in diagram_map.values()])
status = {
    "step": "complete",
    "slug": SLUG,
    "station_type": station_type,
    "diagram_count": diagram_count,
    "has_clinical_notes": has_notes,
    "html_size_kb": round(len(html) / 1024, 1),
    "word_count": word_count,
    "updated_at": datetime.datetime.now().isoformat()
}
(BASE / "status.json").write_text(json.dumps(status, indent=2))
print(f"Status: complete | has_notes={has_notes} | diagrams={diagram_count} | inline placement done")
