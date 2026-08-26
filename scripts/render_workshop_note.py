#!/usr/bin/env python3
"""
Render assessed workshop cases (<case>.assessed.json) into house-style HTML
notes under ICRP_OSCE_Preparation/<Specialty>/.

Expert agents write the .assessed.json files (structured content + expert
review); this renderer produces uniform final HTML — including the
"Expert Review & Enhancements" section the user requested — and copies case
images into the specialty assets/ directory.

Assessed JSON schema (written by expert agents):
{
  "case_id": str, "title": str, "specialty": str, "target_dir": str,
  "sections": [{"heading": str, "html": str}],        # cleaned clinical content
  "images": [str],                                    # filenames in staging assets/
  "expert_review": {
     "reviewed_by": str,                              # agent persona
     "corrections": [{"issue": str, "correction": str}],
     "enhancements": [str],
     "metadata": {"station_type": str, "difficulty": str,
                   "amc_frequency": str, "tags": [str],
                   "related_topics": [str]},
     "citations": [{"claim": str, "source": str, "page": any,
                     "qdrant_point_id": str}]
  }
}

USAGE:
    python3 scripts/render_workshop_note.py [--only <target_dir>]
"""

import argparse
import html as html_mod
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "25-august-docs" / "staging"
NOTES_ROOT = ROOT / "ICRP_OSCE_Preparation"

EXTRA_CSS = """
        .expert-review { border: 2px solid #8e44ad; border-radius: 8px;
            margin-top: 40px; }
        .expert-review > h2 { background: #8e44ad; color: white; margin: 0;
            padding: 15px 20px; border-radius: 6px 6px 0 0; }
        .expert-review .er-body { padding: 20px; }
        .er-block { margin-bottom: 20px; }
        .er-block h3 { color: #8e44ad; margin-bottom: 10px; }
        .correction { background: #fdf2f2; border-left: 4px solid #e74c3c;
            padding: 10px 15px; margin-bottom: 8px; border-radius: 4px; }
        .enhancement { background: #f0f9f4; border-left: 4px solid #27ae60;
            padding: 10px 15px; margin-bottom: 8px; border-radius: 4px; }
        .metadata-grid { display: grid; grid-template-columns: 160px 1fr;
            gap: 6px 14px; background: #f8f9fa; padding: 15px;
            border-radius: 4px; }
        .metadata-grid dt { font-weight: 600; color: #2c3e50; }
        .citation { background: #eef4fb; border-left: 4px solid #3498db;
            padding: 10px 15px; margin-bottom: 8px; border-radius: 4px;
            font-size: 0.95em; }
        .citation .pid { color: #7f8c8d; font-size: 0.8em; font-family: monospace; }
        .case-image { max-width: 100%; border: 1px solid #ddd;
            border-radius: 6px; margin: 12px 0; }
        .source-line { color: #7f8c8d; font-size: 0.85em; margin-top: 8px; }
"""


def esc(s):
    return html_mod.escape(str(s or ""))


def fragment_to_sections(fragment: str) -> str:
    """Wrap a mammoth html_fragment in a single content section, fixing
    image srcs to the assets/ dir and dropping empty img tags."""
    fragment = re.sub(r'<img src=""[^>]*>', "", fragment)
    return f'\n<section id="content">{fragment}</section>\n'


def render(record: dict, css: str) -> str:
    er = record.get("expert_review", {})
    meta = er.get("metadata", {})

    sections_html = ""
    if record.get("use_fragment") and record.get("html_fragment"):
        sections_html = fragment_to_sections(record["html_fragment"])
    for sec in record.get("sections", []):
        anchor = re.sub(r"[^a-z0-9]+", "-", sec["heading"].lower()).strip("-")
        sections_html += f'\n<section id="{anchor}"><h2>{esc(sec["heading"])}</h2>\n{sec["html"]}\n</section>\n'

    images_html = ""
    for img in record.get("images", []):
        images_html += f'<img class="case-image" src="assets/{esc(img)}" alt="{esc(record["title"])} figure" loading="lazy">\n'
    if images_html:
        images_html = f'<section id="figures"><h2>Case Figures</h2>\n{images_html}</section>\n'

    corrections = "".join(
        f'<div class="correction">✏️ <strong>{esc(c["issue"])}</strong><br>{esc(c["correction"])}</div>'
        for c in er.get("corrections", [])
    ) or "<p>No factual corrections required.</p>"

    enhancements = "".join(
        f'<div class="enhancement">⭐ {esc(e)}</div>' for e in er.get("enhancements", [])
    ) or "<p>No further enhancements suggested.</p>"

    meta_rows = ""
    for k in ("station_type", "difficulty", "amc_frequency"):
        if meta.get(k):
            meta_rows += f"<dt>{esc(k.replace('_', ' ').title())}</dt><dd>{esc(meta[k])}</dd>"
    if meta.get("tags"):
        meta_rows += f"<dt>Tags</dt><dd>{esc(', '.join(meta['tags']))}</dd>"
    if meta.get("related_topics"):
        meta_rows += f"<dt>Related Topics</dt><dd>{esc(', '.join(meta['related_topics']))}</dd>"

    citations = "".join(
        f'<div class="citation">📚 {esc(c["claim"])}<br>'
        f'<strong>{esc(c["source"])}</strong>'
        f'{" p." + esc(c["page"]) if c.get("page") else ""} '
        f'<span class="pid">qdrant:{esc(c.get("qdrant_point_id", ""))}</span></div>'
        for c in er.get("citations", [])
    ) or "<p>No RAG citations recorded.</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(record["title"])} - {esc(record["target_dir"])} OSCE Notes</title>
<style>{css}{EXTRA_CSS}</style>
</head>
<body>
<div class="container">
    <div class="breadcrumbs">
        <a href="../START_HERE.html">Home</a><span>›</span>
        <a href="../00_MASTER_INDEX_AMC_CLINICAL_OSCE.html">Master Index</a><span>›</span>
        {esc(record["target_dir"])}<span>›</span>{esc(record["title"])}
    </div>
    <h1>{esc(record["title"])}</h1>
    <p class="source-line">Source: Dr. Amir workshop — {esc(record.get("bundle", ""))}
       / {esc(record.get("class", ""))} (Aug 2026 drop) · Specialty: {esc(record["specialty"])}</p>
{sections_html}
{images_html}
    <div class="expert-review">
        <h2>🔬 Expert Review &amp; Enhancements</h2>
        <div class="er-body">
            <p><em>Reviewed by: {esc(er.get("reviewed_by", "expert agent"))} ·
               fact-checked against the irStudy medical textbook RAG index.</em></p>
            <div class="er-block"><h3>✏️ Corrections</h3>{corrections}</div>
            <div class="er-block"><h3>⭐ Suggested Enhancements</h3>{enhancements}</div>
            <div class="er-block"><h3>🏷️ Metadata</h3>
                <dl class="metadata-grid">{meta_rows}</dl></div>
            <div class="er-block"><h3>📚 Reference Citations (RAG)</h3>{citations}</div>
        </div>
    </div>
</div>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="restrict to one target_dir (e.g. ObGyn)")
    args = ap.parse_args()

    css_path = Path("/tmp/claude-1000/-home-dev-Development-irStudy/eb55f577-dd49-4be7-a9f1-e645efad0272/scratchpad/house_style.css")
    if css_path.exists():
        css = css_path.read_text()
    else:  # fall back to extracting from an existing note
        src = (NOTES_ROOT / "Medicine" / "01_GI_Abdominal_Pain_Differentials.html").read_text()
        css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)

    count = 0
    for path in sorted(STAGING.rglob("*.assessed.json")):
        record = json.loads(path.read_text())
        # merge in the base extraction record (html_fragment, images, bundle...)
        base_path = path.with_name(path.name.replace(".assessed", ""))
        if base_path.exists():
            base = json.loads(base_path.read_text())
            base.pop("rag_context", None)
            record = {**base, **record}
        if args.only and record["target_dir"] != args.only:
            continue
        out_dir = NOTES_ROOT / record["target_dir"]
        assets_out = out_dir / "assets"
        assets_out.mkdir(parents=True, exist_ok=True)

        for img in record.get("images", []):
            src_img = path.parent / "assets" / img
            if src_img.exists():
                shutil.copy2(src_img, assets_out / img)

        out_file = out_dir / f"WS_{record['case_id']}.html"
        out_file.write_text(render(record, css))
        count += 1

    print(f"Rendered {count} notes into {NOTES_ROOT}/<Specialty>/")


if __name__ == "__main__":
    main()
