#!/usr/bin/env python3
"""
PRD_OSCE_005: Dynamic Diagram Generator (v2 — 4 diagrams per station type)
Usage: $MSDEV_VENV/bin/python 07_diagrams.py <slug>

Generates 4 clinically relevant diagrams per station type:
  history_taking:       SOCRATES flow | Differential tree | Red flags heatmap | Management pathway
  physical_examination: Exam sequence  | Findings map      | Differential tree  | Investigations grid
  communication:        ICE framework  | Counselling pathway| Key points chart   | Communication structure
"""

import sys, json, os
from pathlib import Path

SLUG = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Usage: 07_diagrams.py <slug>")
BASE = Path(f"/home/dev/Development/irStudy/osce-pipeline/output/{SLUG}")
DIAGRAMS_DIR = BASE / "diagrams"
DIAGRAMS_DIR.mkdir(exist_ok=True)

# Load data — prefer key_facts.json (post-enhancement) over analysis.json
analysis   = json.loads((BASE / "analysis.json").read_text())   if (BASE / "analysis.json").exists()   else {}
key_facts  = json.loads((BASE / "key_facts.json").read_text())  if (BASE / "key_facts.json").exists()  else {}
station_type = analysis.get("station_type", "history_taking")

# Colour palette
C = {
    "primary":   "#2C3E50",
    "secondary": "#3498DB",
    "success":   "#27AE60",
    "warning":   "#F39C12",
    "danger":    "#E74C3C",
    "info":      "#8E44AD",
    "neutral":   "#95A5A6",
    "bg":        "#F8F9FA",
}

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

generated = []


def save(fig, name):
    path = DIAGRAMS_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    generated.append(str(path))
    print(f"  Generated: {name}.png")
    return path


def graphviz_render(dot, name):
    """Render a graphviz Digraph and add to generated list."""
    path = DIAGRAMS_DIR / name
    dot.render(str(path), cleanup=True)
    generated.append(str(path) + ".png")
    print(f"  Generated: {name}.png")


# ============================================================
# SHARED: Differential Diagnosis Tree
# ============================================================
def make_diff_tree(prefix="02"):
    if not HAS_GRAPHVIZ:
        return
    ddx = key_facts.get("differential_diagnoses", []) or analysis.get("ddx_mentioned", [])
    if not ddx:
        ddx = ["Primary Diagnosis", "Alternative 1", "Alternative 2", "Must Not Miss"]

    complaint = analysis.get("presenting_complaint", "Presenting Complaint")
    if len(complaint) > 45:
        complaint = complaint[:45] + "..."

    dot = graphviz.Digraph("DDx", format="png")
    dot.attr(rankdir="LR", bgcolor="white", fontname="Helvetica", size="12,8")
    dot.attr("node", fontname="Helvetica", style="filled", shape="box",
             fontsize="11", margin="0.3,0.2")

    dot.node("root", f"Presenting Complaint\n{complaint}",
             fillcolor=C["primary"], fontcolor="white", shape="ellipse")

    groups = [
        ("Common",        C["secondary"], ddx[:2]),
        ("Important",     C["warning"],   ddx[2:4] if len(ddx) > 2 else []),
        ("Must Not Miss", C["danger"],    ddx[4:]  if len(ddx) > 4 else []),
    ]
    for group_label, color, items in groups:
        if not items:
            continue
        gid = f"g_{group_label.replace(' ','_')}"
        dot.node(gid, group_label, fillcolor=color, fontcolor="white", shape="oval")
        dot.edge("root", gid)
        for i, item in enumerate(items[:3]):
            nid = f"{gid}_{i}"
            dot.node(nid, item[:40], fillcolor=color + "88", fontcolor=C["primary"])
            dot.edge(gid, nid)

    graphviz_render(dot, f"{prefix}_differential_tree")


# ============================================================
# ============================================================
# HISTORY TAKING — 4 diagrams
# ============================================================
# ============================================================

def ht_socrates_flow():
    """SOCRATES framework flow diagram."""
    if not HAS_GRAPHVIZ:
        return
    components = key_facts.get("socrates", {})

    dot = graphviz.Digraph("SOCRATES", format="png")
    dot.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", size="10,14")
    dot.attr("node", fontname="Helvetica", style="filled", shape="box",
             fontsize="11", margin="0.3,0.2")

    dot.node("title", "SOCRATES Assessment Framework\n(AMC History Taking)",
             fillcolor=C["primary"], fontcolor="white", fontsize="14")

    socrates_items = [
        ("S",  "Site",          components.get("site", "Where exactly? Localised or diffuse?"),       C["secondary"]),
        ("O",  "Onset",         components.get("onset", "Sudden or gradual? What were you doing?"),    C["secondary"]),
        ("C",  "Character",     components.get("character", "Sharp / dull / burning / colicky?"),       C["secondary"]),
        ("R",  "Radiation",     components.get("radiation", "Does it spread? To shoulder/back/groin?"), C["secondary"]),
        ("A",  "Associated Sx", components.get("associated", "Nausea / vomiting / fever / jaundice?"), C["info"]),
        ("T",  "Timing",        components.get("timing", "Constant or intermittent? Relation to meals?"), C["secondary"]),
        ("E",  "Exacerbating",  components.get("exacerbating", "What makes it worse or better?"),       C["warning"]),
        ("S2", "Severity",      components.get("severity", "Pain score 0–10. Effect on daily life?"),   C["danger"]),
    ]

    dot.node("redflags", "RED FLAGS\nHaematemesis / melaena\nWeight loss / dysphagia\nFHx cancer / anaemia",
             fillcolor=C["danger"], fontcolor="white", shape="diamond")
    dot.edge("title", "redflags", label="Always screen", color=C["danger"], fontcolor=C["danger"])

    prev = "title"
    for code, name, details, color in socrates_items:
        node_id = f"s_{code}"
        label = f"{code}: {name}\n{details[:60]}"
        dot.node(node_id, label, fillcolor=color, fontcolor="white")
        dot.edge(prev, node_id)
        prev = node_id

    dot.node("ice", "ICE — Close History\nIdeas | Concerns | Expectations",
             fillcolor=C["success"], fontcolor="white", shape="ellipse")
    dot.edge(prev, "ice")

    graphviz_render(dot, "01_socrates_flow")


def ht_redflags_panel():
    """Red flags priority panel — bar chart."""
    red_flags = key_facts.get("red_flags", [])
    if not red_flags:
        red_flags = [
            "Haematemesis / melaena",
            "Unintentional weight loss >5 kg",
            "Progressive dysphagia",
            "Family history of GI cancer",
            "Iron deficiency anaemia",
            "Persistent vomiting",
            "Palpable abdominal mass",
            "Age >50 with new symptoms",
        ]

    flags = [f[:50] for f in red_flags[:8]]
    urgency = [10, 10, 9, 9, 8, 8, 8, 7][:len(flags)]
    colors_list = [C["danger"] if u >= 10 else C["warning"] if u >= 9 else C["secondary"]
                   for u in urgency]

    fig, ax = plt.subplots(figsize=(11, max(5, len(flags) * 0.7 + 2)))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bars = ax.barh(range(len(flags)), urgency, color=colors_list, alpha=0.85,
                   edgecolor="white", linewidth=1.5, height=0.6)

    for bar, flag, u in zip(bars, flags, urgency):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"  {flag}", va="center", fontsize=10, color=C["primary"])

    ax.set_xlim(0, 13)
    ax.set_yticks(range(len(flags)))
    ax.set_yticklabels([""] * len(flags))
    ax.set_xlabel("Clinical Urgency Score", fontsize=11)
    ax.set_title("Red Flags — Must Not Miss (AMC Clinical Exam)", fontsize=13,
                 fontweight="bold", color=C["primary"], pad=15)

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=C["danger"], label="Immediate action"),
                       Patch(facecolor=C["warning"], label="Urgent referral"),
                       Patch(facecolor=C["secondary"], label="Investigate")]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    save(fig, "03_redflags_panel")


def ht_management_flow():
    """Clinical management pathway."""
    if not HAS_GRAPHVIZ:
        return

    steps = key_facts.get("management_steps", [])
    if not steps:
        steps = [
            "History + Examination",
            "Bedside Tests (obs, BSL, urine)",
            "Bloods (FBC, UEC, LFT, CRP, lipase)",
            "Imaging (AXR / USS / CT abdomen)",
            "Specialist Referral / Surgical review",
            "Definitive Treatment",
            "Safety Net & Follow-up",
        ]

    dot = graphviz.Digraph("Mgmt", format="png")
    dot.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", size="8,12")
    dot.attr("node", fontname="Helvetica", style="filled", shape="box",
             fontsize="11", margin="0.3,0.2")

    colors_cycle = [C["secondary"], C["info"], C["warning"],
                    C["success"], C["primary"], C["danger"], C["neutral"]]

    dot.node("start", "Patient Presents", fillcolor=C["primary"],
             fontcolor="white", shape="ellipse")

    prev = "start"
    for i, step in enumerate(steps[:7]):
        nid = f"step_{i}"
        dot.node(nid, f"{i+1}. {step[:50]}", fillcolor=colors_cycle[i % len(colors_cycle)],
                 fontcolor="white")
        dot.edge(prev, nid)
        prev = nid

    dot.node("safety", "Safety Net\n• When to return to ED\n• Red flag instructions\n• Follow-up appointment",
             fillcolor=C["danger"], fontcolor="white", shape="diamond")
    dot.edge(prev, "safety")

    graphviz_render(dot, "04_management_flow")


# ============================================================
# ============================================================
# PHYSICAL EXAMINATION — 4 diagrams
# ============================================================
# ============================================================

def pe_exam_sequence():
    """Systematic examination sequence — step diagram."""
    steps = key_facts.get("exam_sequence", [])
    if not steps:
        steps = [
            ("Approach & Consent",     "Introduce, wash hands, position patient, consent", C["secondary"]),
            ("General Inspection",     "From end of bed: JACCOL, body habitus, distress", C["secondary"]),
            ("Inspect",                "Hands → face → abdomen: scars, distension, pulsation", C["info"]),
            ("Palpate — Superficial",  "All 9 regions, watch patient's face for pain", C["warning"]),
            ("Palpate — Deep",         "Organomegaly: liver, spleen, kidneys (ballottement)", C["warning"]),
            ("Percuss",                "Liver span, splenic dullness, shifting dullness (ascites)", C["info"]),
            ("Auscultate",             "Bowel sounds, bruits; renal/hepatic", C["success"]),
            ("Special Tests",          "Murphy's, Rovsing's, Psoas, Obturator signs", C["danger"]),
            ("Digital Rectal (if ind.)", "PR exam, stool, prostate assessment", C["neutral"]),
            ("Summarise Findings",     "Present to examiner, differential, investigations", C["primary"]),
        ]
        data = [(s[0], s[1], s[2]) for s in steps]
    else:
        data = [(s, "", C["secondary"]) for s in steps[:10]]

    fig, ax = plt.subplots(figsize=(13, len(data) * 0.9 + 2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.axis("off")
    ax.set_title("Systematic Abdominal / Physical Examination Sequence\n(AMC Clinical Examination)",
                 fontsize=13, fontweight="bold", color=C["primary"], pad=15)

    for i, (step, detail, color) in enumerate(data):
        y = 1 - (i + 0.5) / len(data)
        # Step number circle
        circle = plt.Circle((0.04, y), 0.025, color=color, zorder=3, transform=ax.transAxes)
        ax.add_patch(circle)
        ax.text(0.04, y, str(i + 1), ha="center", va="center", fontsize=9,
                fontweight="bold", color="white", transform=ax.transAxes, zorder=4)
        # Connector line
        if i < len(data) - 1:
            ax.plot([0.04, 0.04], [y - 0.025, y - (1 / len(data)) + 0.025],
                    color=color, linewidth=2, alpha=0.4, transform=ax.transAxes)
        # Step name
        ax.text(0.10, y + 0.01, step, ha="left", va="center", fontsize=11,
                fontweight="bold", color=C["primary"], transform=ax.transAxes)
        if detail:
            ax.text(0.10, y - 0.015, detail[:80], ha="left", va="center", fontsize=8.5,
                    color="#5d6d7e", transform=ax.transAxes)

    plt.tight_layout()
    save(fig, "01_exam_sequence")


def pe_findings_map():
    """Abdominal region findings map — 9-region grid."""
    findings = key_facts.get("regional_findings", {})

    regions = [
        ("RUQ",    findings.get("ruq",    "Liver / gallbladder\nMurphy's sign")),
        ("Epigastric", findings.get("epigastric", "Stomach / aorta\nPeptic ulcer")),
        ("LUQ",    findings.get("luq",    "Spleen / stomach\nKidney")),
        ("Right Flank", findings.get("right_flank", "Ascending colon\nRight kidney")),
        ("Umbilical",   findings.get("umbilical",   "Small bowel\nAorta / uterus")),
        ("Left Flank",  findings.get("left_flank",  "Descending colon\nLeft kidney")),
        ("RIF",    findings.get("rif",    "Appendix / caecum\nRovsing's sign")),
        ("Suprapubic", findings.get("suprapubic", "Bladder / uterus\nProstate")),
        ("LIF",    findings.get("lif",    "Sigmoid colon\nLeft ovary")),
    ]

    region_colors = [
        C["warning"], C["secondary"], C["info"],
        C["success"],  C["primary"],   C["neutral"],
        C["danger"],   C["info"],      C["success"],
    ]

    fig, axes = plt.subplots(3, 3, figsize=(13, 9))
    fig.patch.set_facecolor("white")
    fig.suptitle("Abdominal Examination — Regional Findings Map\n(AMC Clinical Examination)",
                 fontsize=13, fontweight="bold", color=C["primary"], y=1.01)

    for idx, (ax, (region, detail), color) in enumerate(zip(axes.flat, regions, region_colors)):
        ax.set_facecolor(color + "22")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor(color)
            spine.set_linewidth(2)
        ax.text(0.5, 0.72, region, ha="center", va="center", fontsize=12,
                fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.5, 0.35, detail, ha="center", va="center", fontsize=8.5,
                color=C["primary"], transform=ax.transAxes, multialignment="center")

    plt.tight_layout()
    save(fig, "03_findings_map")


def pe_investigations_grid():
    """Investigations priority grid — 4 columns."""
    investigations = key_facts.get("investigations", []) or analysis.get("investigations_mentioned", [])
    if not investigations:
        investigations = [
            "Urine MCS", "BSL", "ECG", "O2 sats",
            "FBC", "UEC", "LFT", "CRP", "Lipase", "Blood cultures",
            "AXR", "USS abdomen", "CT abdomen/pelvis", "CXR erect",
            "OGD / Endoscopy", "Colonoscopy", "ERCP",
        ]

    categories = ["Bedside", "Bloods", "Imaging", "Endoscopy/Specialist"]
    bedside = [i for i in investigations if any(w in i.lower()
               for w in ["urine", "ecg", "bsl", "sats", "temp", "obs", "usg"])]
    bloods  = [i for i in investigations if any(w in i.lower()
               for w in ["fbc", "uec", "lft", "crp", "troponin", "lipase", "blood", "esr", "tft"])]
    imaging = [i for i in investigations if any(w in i.lower()
               for w in ["xr", "ct", "mri", "ultra", "axr", "cxr", "uss"])]
    endo    = [i for i in investigations if any(w in i.lower()
               for w in ["endoscopy", "colonoscopy", "ercp", "ogd", "scope", "biopsy"])]

    all_groups = [bedside or ["Urine MCS", "BSL", "ECG"],
                  bloods  or ["FBC", "UEC", "LFT", "CRP"],
                  imaging or ["AXR", "USS", "CT abdomen"],
                  endo    or ["OGD", "Colonoscopy"]]

    group_colors = [C["success"], C["secondary"], C["warning"], C["info"]]
    max_len = max(len(g) for g in all_groups)

    fig, axes = plt.subplots(1, 4, figsize=(15, max(4.5, max_len * 0.75 + 2.5)))
    fig.patch.set_facecolor("white")
    fig.suptitle("Investigation Priority Grid — AMC Clinical Examination",
                 fontsize=13, fontweight="bold", color=C["primary"], y=1.02)

    for ax, cat, items, color in zip(axes, categories, all_groups, group_colors):
        ax.set_facecolor(color + "18")
        ax.axis("off")
        # Category header strip
        ax.text(0.5, 0.97, cat, ha="center", va="top", fontsize=11, fontweight="bold",
                color="white", transform=ax.transAxes,
                bbox=dict(facecolor=color, pad=5, boxstyle="round"))
        for i, item in enumerate(items[:8]):
            ax.text(0.1, 0.86 - i * 0.11, f"▸ {item[:30]}", fontsize=9.5,
                    color=C["primary"], transform=ax.transAxes, va="top")
        for spine in ax.spines.values():
            spine.set_edgecolor(color)
            spine.set_linewidth(1.5)

    plt.tight_layout()
    save(fig, "04_investigations_grid")


# ============================================================
# ============================================================
# COMMUNICATION — 4 diagrams
# ============================================================
# ============================================================

def comm_ice_framework():
    """ICE framework + communication structure."""
    if not HAS_GRAPHVIZ:
        return

    ideas       = key_facts.get("patient_ideas",    "What the patient thinks is wrong")
    concerns    = key_facts.get("patient_concerns",  "What worries them most")
    expectations = key_facts.get("patient_expectations", "What they hope for from the consultation")

    dot = graphviz.Digraph("ICE", format="png")
    dot.attr(bgcolor="white", fontname="Helvetica", size="10,10")
    dot.attr("node", fontname="Helvetica", style="filled", shape="box",
             fontsize="11", margin="0.3,0.2")

    dot.node("start", "Opening the Consultation\n• Introduce & establish rapport\n• Open question: 'Tell me about...'",
             fillcolor=C["primary"], fontcolor="white", shape="ellipse")

    dot.node("ice_title", "ICE Framework", fillcolor=C["secondary"],
             fontcolor="white", fontsize="13")
    dot.edge("start", "ice_title")

    dot.node("ideas", f"I — Ideas\n{str(ideas)[:60]}",
             fillcolor=C["info"], fontcolor="white")
    dot.node("concerns", f"C — Concerns\n{str(concerns)[:60]}",
             fillcolor=C["warning"], fontcolor="white")
    dot.node("expectations", f"E — Expectations\n{str(expectations)[:60]}",
             fillcolor=C["success"], fontcolor="white")

    dot.edge("ice_title", "ideas")
    dot.edge("ice_title", "concerns")
    dot.edge("ice_title", "expectations")

    dot.node("explain", "Explanation\n• Simple language\n• Chunk and check\n• Avoid jargon",
             fillcolor=C["secondary"], fontcolor="white")
    dot.node("summarise", "Summarise & Safety Net\n• Repeat key points\n• Written info\n• Follow-up plan",
             fillcolor=C["success"], fontcolor="white", shape="diamond")

    dot.edge("ideas",       "explain")
    dot.edge("concerns",    "explain")
    dot.edge("expectations","explain")
    dot.edge("explain",     "summarise")

    graphviz_render(dot, "01_ice_framework")


def comm_counselling_pathway():
    """Counselling / communication station pathway."""
    steps = key_facts.get("counselling_steps", [])
    if not steps:
        steps = [
            ("Opening",            "Introduce, confirm identity, check comfort, set agenda"),
            ("Explore Ideas",      "What does the patient already know / believe?"),
            ("Explore Concerns",   "What are they most worried about?"),
            ("Explore Expectations","What do they hope to get from today?"),
            ("Provide Information","Chunk & check; simple language; no jargon"),
            ("Address Concerns",   "Empathy, validate, acknowledge uncertainty"),
            ("Shared Decision",    "Involve patient in management decisions"),
            ("Safety Net",         "When to seek urgent help, follow-up plan"),
            ("Close",              "Summarise, check understanding, written info"),
        ]
        data = [(s[0], s[1]) for s in steps]
    else:
        data = [(s, "") for s in steps[:9]]

    fig, ax = plt.subplots(figsize=(13, len(data) * 0.9 + 2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.axis("off")
    ax.set_title("Counselling / Communication Station — Step-by-Step Framework\n(AMC Clinical Examination)",
                 fontsize=13, fontweight="bold", color=C["primary"], pad=15)

    step_colors = [C["secondary"], C["info"], C["info"], C["info"],
                   C["warning"], C["warning"], C["success"], C["danger"], C["primary"]]

    for i, (step, detail) in enumerate(data):
        y = 1 - (i + 0.5) / len(data)
        color = step_colors[i % len(step_colors)]
        circle = plt.Circle((0.04, y), 0.025, color=color, zorder=3, transform=ax.transAxes)
        ax.add_patch(circle)
        ax.text(0.04, y, str(i + 1), ha="center", va="center", fontsize=9,
                fontweight="bold", color="white", transform=ax.transAxes, zorder=4)
        if i < len(data) - 1:
            ax.plot([0.04, 0.04], [y - 0.025, y - (1 / len(data)) + 0.025],
                    color=color, linewidth=2, alpha=0.4, transform=ax.transAxes)
        ax.text(0.10, y + 0.01, step, ha="left", va="center", fontsize=11,
                fontweight="bold", color=C["primary"], transform=ax.transAxes)
        if detail:
            ax.text(0.10, y - 0.015, detail[:85], ha="left", va="center", fontsize=8.5,
                    color="#5d6d7e", transform=ax.transAxes)

    plt.tight_layout()
    save(fig, "02_counselling_pathway")


def comm_key_points_chart():
    """Key communication points — horizontal bar chart showing domain coverage."""
    domains = key_facts.get("comm_domains", {})
    if not domains:
        domains = {
            "Information Giving":    9,
            "Empathy & Rapport":     8,
            "Listening Skills":      8,
            "ICE Elicitation":       9,
            "Safety Netting":        8,
            "Shared Decision Making":7,
            "Health Literacy":       7,
            "Cultural Sensitivity":  6,
        }

    labels = list(domains.keys())[:8]
    values = [domains[k] for k in labels]
    colors_list = [C["danger"] if v >= 9 else C["warning"] if v >= 8 else C["secondary"]
                   for v in values]

    fig, ax = plt.subplots(figsize=(11, max(5, len(labels) * 0.8 + 2)))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bars = ax.barh(labels, values, color=colors_list, alpha=0.85,
                   edgecolor="white", linewidth=1.5, height=0.55)
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{val}/10", va="center", fontsize=10, color=C["primary"], fontweight="bold")

    ax.set_xlim(0, 12)
    ax.set_xlabel("AMC Competency Score", fontsize=11)
    ax.set_title("Communication Domain Competency — AMC Clinical Examination",
                 fontsize=13, fontweight="bold", color=C["primary"], pad=15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.invert_yaxis()
    plt.tight_layout()
    save(fig, "03_comm_domains")


# ============================================================
# DISPATCHER — run 4 diagrams based on station_type
# ============================================================

print(f"\n[07_diagrams] Slug: {SLUG} | Station type: {station_type}")

if station_type == "history_taking":
    ht_socrates_flow()
    make_diff_tree(prefix="02")
    ht_redflags_panel()
    ht_management_flow()

elif station_type == "physical_examination":
    pe_exam_sequence()
    make_diff_tree(prefix="02")
    pe_findings_map()
    pe_investigations_grid()

else:  # communication / meta / other
    comm_ice_framework()
    comm_counselling_pathway()
    comm_key_points_chart()
    make_diff_tree(prefix="04")


# ============================================================
# Save manifest
# ============================================================
(BASE / "diagrams_manifest.json").write_text(json.dumps(generated, indent=2))
print(f"\nTotal diagrams generated: {len(generated)}")
print(f"Manifest: {BASE / 'diagrams_manifest.json'}")

# Update status
import datetime
status = {
    "step": "diagrams",
    "slug": SLUG,
    "station_type": station_type,
    "diagram_count": len(generated),
    "updated_at": datetime.datetime.now().isoformat()
}
(BASE / "status.json").write_text(json.dumps(status, indent=2))
