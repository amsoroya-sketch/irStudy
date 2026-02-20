# PRD_OSCE_005_DIAGRAM_GENERATOR

## R — Request

Generate a dynamic set of clinical diagrams for each OSCE station using the MSDev Python
visualization libraries. The number and type of diagrams adapts to station type and content
complexity — **not limited to 6**, typically 8–10 diagrams per station.

**Context**:
- MSDev venv: `/home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv`
- Libraries: matplotlib, graphviz, seaborn, plotly, networkx, Pillow, Jinja2
- Input: `key_facts.json` + `analysis.json` + `clinical_notes.md`
- Output: PNG files in `output/{slug}/diagrams/`

---

## A — Architecture

### Diagram Registry (Station-Type Aware)

Each station type has a defined registry of diagram generators.
The actual count varies by content — if a section has no data, that diagram is skipped.

#### HISTORY TAKING (8–10 diagrams)
| # | Diagram | Library | Always? |
|---|---------|---------|---------|
| 1 | Domain Score Radar | matplotlib polar | Yes |
| 2 | SOCRATES Assessment Flow | graphviz Digraph | Yes |
| 3 | Differential Diagnosis Tree | graphviz Digraph | Yes |
| 4 | Red Flags Heatmap | seaborn heatmap | Yes |
| 5 | Station Timeline (Gantt) | matplotlib FancyBboxPatch | Yes |
| 6 | Management / Safety-net Flow | graphviz Digraph | Yes |
| 7 | Risk Factor Matrix | seaborn/matplotlib table | If > 3 risk factors |
| 8 | Gastric vs Duodenal Timing Chart | matplotlib bar/line | If GI station |
| 9 | Complications Severity Table | matplotlib table | If DDx > 3 |
| 10 | Key Facts Summary Card | Pillow / matplotlib | Yes |

#### PHYSICAL EXAMINATION (8–10 diagrams)
| # | Diagram | Library | Always? |
|---|---------|---------|---------|
| 1 | Domain Score Radar | matplotlib polar | Yes |
| 2 | Examination Sequence Flow | graphviz Digraph | Yes |
| 3 | Body Findings Map | matplotlib + body outline | Yes |
| 4 | Differential Diagnosis Tree | graphviz Digraph | Yes |
| 5 | Grading/Scoring Chart | matplotlib bar | If scoring system present |
| 6 | Normal vs Abnormal Comparison | matplotlib table | Yes |
| 7 | Investigations Grid | seaborn heatmap | Yes |
| 8 | Station Timeline | matplotlib | Yes |
| 9 | Management Flow | graphviz Digraph | Yes |
| 10 | Key Facts Summary Card | Pillow / matplotlib | Yes |

#### COMMUNICATION / COUNSELLING (6–8 diagrams)
| # | Diagram | Library | Always? |
|---|---------|---------|---------|
| 1 | Domain Score Radar | matplotlib polar | Yes |
| 2 | Communication Framework Flow | graphviz Digraph | Yes |
| 3 | ICE (Ideas/Concerns/Expectations) Diagram | graphviz/matplotlib | Yes |
| 4 | Counselling Pathway | graphviz Digraph | Yes |
| 5 | Ethical Principles Map | networkx | If ethics station |
| 6 | Escalation Pathway | graphviz Digraph | Yes |
| 7 | Breaking Bad News Framework | graphviz | If BBN station |
| 8 | Key Facts Summary Card | Pillow / matplotlib | Yes |

---

## L — Loop / Phases

### Phase 1: Load Data
```python
VENV = "/home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv"
# Run with: $VENV/bin/python generate_diagrams.py {slug}

import json, os, sys
from pathlib import Path

SLUG = sys.argv[1]
BASE = Path(f"output/{SLUG}")
key_facts = json.loads((BASE / "key_facts.json").read_text())
analysis = json.loads((BASE / "analysis.json").read_text())
station_type = analysis["station_type"]
diagrams_dir = BASE / "diagrams"
diagrams_dir.mkdir(exist_ok=True)
```

### Phase 2: Diagram Registry Lookup
```python
# Registry maps station_type to list of (generator_function, condition_check)
REGISTRY = {
    "history_taking": [
        (make_radar_chart,          lambda d: True),
        (make_socrates_flow,        lambda d: True),
        (make_differential_tree,    lambda d: True),
        (make_redflags_heatmap,     lambda d: len(d.get("red_flags", [])) > 0),
        (make_timeline,             lambda d: True),
        (make_management_flow,      lambda d: len(d.get("management_steps", [])) > 0),
        (make_risk_factor_matrix,   lambda d: len(d.get("risk_factors", [])) > 3),
        (make_timing_comparison,    lambda d: "gastric" in str(d).lower() or "duodenal" in str(d).lower()),
        (make_complications_table,  lambda d: len(d.get("differential_diagnoses", [])) > 2),
        (make_key_facts_card,       lambda d: True),
    ],
    "physical_examination": [
        (make_radar_chart,          lambda d: True),
        (make_exam_sequence_flow,   lambda d: True),
        (make_body_findings_map,    lambda d: True),
        (make_differential_tree,    lambda d: True),
        (make_grading_chart,        lambda d: len(d.get("scoring_systems", [])) > 0),
        (make_normal_abnormal_table,lambda d: True),
        (make_investigations_grid,  lambda d: len(d.get("investigations", [])) > 0),
        (make_timeline,             lambda d: True),
        (make_management_flow,      lambda d: True),
        (make_key_facts_card,       lambda d: True),
    ],
    "communication": [
        (make_radar_chart,          lambda d: True),
        (make_communication_flow,   lambda d: True),
        (make_ice_diagram,          lambda d: True),
        (make_counselling_pathway,  lambda d: True),
        (make_ethical_principles,   lambda d: "ethics" in str(d).lower() or "consent" in str(d).lower()),
        (make_escalation_pathway,   lambda d: True),
        (make_bbn_framework,        lambda d: "bad news" in str(d).lower() or "cancer" in str(d).lower()),
        (make_key_facts_card,       lambda d: True),
    ]
}
```

### Phase 3: Generate Each Diagram
```python
generated = []
for generator_fn, condition in REGISTRY[station_type]:
    if condition(key_facts):
        try:
            output_path = generator_fn(key_facts, diagrams_dir)
            generated.append(str(output_path))
            print(f"  Generated: {output_path.name}")
        except Exception as e:
            print(f"  WARNING: {generator_fn.__name__} failed: {e}")
            # Non-fatal — continue with other diagrams

print(f"\nTotal diagrams generated: {len(generated)}")
# Save manifest
import json
(BASE / "diagrams_manifest.json").write_text(json.dumps(generated, indent=2))
```

### Phase 4: Graphviz Colour Convention (all diagrams)
```python
# Colour palette (consistent across all diagrams)
COLORS = {
    "primary":   "#2C3E50",    # dark blue — main boxes
    "secondary": "#3498DB",    # bright blue — subtopics
    "success":   "#27AE60",    # green — normal/present
    "warning":   "#F39C12",    # orange — partial/borderline
    "danger":    "#E74C3C",    # red — red flags / abnormal
    "info":      "#8E44AD",    # purple — investigations
    "neutral":   "#95A5A6",    # grey — optional
    "background":"#ECF0F1",    # light grey background
}
```

---

## P — Plan / Tasks

| Task | Script | Acceptance Criterion |
|------|--------|---------------------|
| Load key_facts.json | `scripts/06_diagrams.py` | No parse errors |
| Run registry for station type | included | All condition-passing generators run |
| Save PNG files | included | At least 6 PNGs per video |
| Save manifest JSON | included | `diagrams_manifest.json` lists all paths |
| Update status | bash | `status.json` shows step=diagrams |

---

## H — Handoff / Acceptance

### Done When:
- [ ] `diagrams/` directory has >= 6 PNG files
- [ ] `diagrams_manifest.json` exists and lists all generated paths
- [ ] All PNGs are valid image files (not 0 bytes)
- [ ] No fatal errors in diagram generation log (warnings acceptable)
- [ ] `status.json` shows `"step": "diagrams"`
- [ ] Consistent colour scheme across all diagrams

### Hands Off To: PRD_OSCE_006_REPORT_ASSEMBLER
