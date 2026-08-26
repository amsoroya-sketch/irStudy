#!/usr/bin/env python3
"""
Convert the RMO Case Bank PDF (25-august-docs/RMO_Case_Bank_Simple_Steps_Colour-1.pdf)
into study cards compatible with backend/scripts/import_flashcards.py.

The PDF holds ~80 cases in a fixed four-part format:
    A12. Code Stroke                     <- case title
    FIRST: ...                           <- the one thing to do first
    1. ... 2. ... 3. ...                 <- ordered steps
    TRAP: ...                            <- the mistake that loses the case
    SAY: "..."                           <- the line the panel listens for

Mapping to StudyCard:
    question    = "RMO case: <title> — what do you do?"
    answer      = FIRST + numbered THEN steps
    explanation = TRAP + SAY
    card_id     = RMO-CARD-0001...
    specialty   = emergency_medicine (Part A) / general_practice wards (Part B)
    card_type   = management

USAGE:
    python3 scripts/convert_rmo_casebank.py           # writes JSON
    python3 scripts/convert_rmo_casebank.py --print 3 # preview N cards
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "25-august-docs" / "RMO_Case_Bank_Simple_Steps_Colour-1.pdf"
OUT = ROOT / "data" / "study_cards" / "rmo_case_bank_cards.json"

CITATION = {
    "title": "RMO Case Bank — The Simple Version (80 cases)",
    "author": "Prepared for Dr Iram Asim",
    "year": "2026",
    "page": None,
    "content": "",
    "rag_confidence": None,
    "source_type": "casebank",
}

CASE_RE = re.compile(r"^([AB])(\d+)\.\s+(.+)$")
NOISE_RE = re.compile(r"^(RMO Case Bank — The Simple Version|Part [AB] —|[AB]\d+–[AB]?\d+\s)")


def get_text() -> str:
    return subprocess.run(
        ["pdftotext", str(PDF), "-"], capture_output=True, text=True, check=True
    ).stdout


def parse(text: str):
    cases, current = [], None
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or NOISE_RE.match(line):
            continue
        m = CASE_RE.match(line)
        # guard: numbered steps also match "1. ..." but not "A1. ..." pattern
        if m and len(m.group(3)) > 3:
            if current:
                cases.append(current)
            current = {"part": m.group(1), "num": int(m.group(2)),
                       "title": m.group(3).strip(), "first": "", "steps": [],
                       "trap": "", "say": "", "_last": None}
            continue
        if current is None:
            continue
        if line.startswith("FIRST:"):
            current["first"] = line[6:].strip()
            current["_last"] = "first"
        elif line.startswith("TRAP:"):
            current["trap"] = line[5:].strip()
            current["_last"] = "trap"
        elif line.startswith("SAY:"):
            current["say"] = line[4:].strip()
            current["_last"] = "say"
        elif re.match(r"^\d+\.\s", line):
            current["steps"].append(re.sub(r"^\d+\.\s*", "", line))
            current["_last"] = "step"
        else:  # continuation of the previous field
            last = current["_last"]
            if last == "first":
                current["first"] += " " + line
            elif last == "trap":
                current["trap"] += " " + line
            elif last == "say":
                current["say"] += " " + line
            elif last == "step" and current["steps"]:
                current["steps"][-1] += " " + line
    if current:
        cases.append(current)
    return cases


def to_cards(cases):
    cards = []
    for i, c in enumerate(cases, 1):
        steps = "\n".join(f"{n}. {s}" for n, s in enumerate(c["steps"], 1))
        answer = f"FIRST: {c['first']}\n\nTHEN:\n{steps}"
        explanation = f"TRAP (the mistake that loses the case): {c['trap']}\n\nSAY: {c['say']}"
        specialty = "emergency_medicine" if c["part"] == "A" else "general_practice"
        cards.append({
            "card_id": f"RMO-CARD-{i:04d}",
            "specialty": specialty,
            "topic": f"RMO Case Bank Part {c['part']}",
            "subtopic": c["title"][:250],
            "question": f"RMO case: {c['title']} — what is your immediate management approach?",
            "answer": answer.strip(),
            "explanation": explanation.strip(),
            "citations": [dict(CITATION)],
            "difficulty": "medium",
            "tags": ["rmo", "emergency-management", "interview-prep",
                     f"part-{c['part'].lower()}"],
            "card_type": "management",
        })
    return cards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", type=int, default=0, dest="preview")
    args = ap.parse_args()

    cases = parse(get_text())
    incomplete = [c for c in cases if not (c["first"] and c["steps"] and c["trap"] and c["say"])]
    cards = to_cards(cases)

    if args.preview:
        for card in cards[: args.preview]:
            print(json.dumps(card, indent=1, ensure_ascii=False)[:900], "\n---")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"version": "1.0",
                               "source": "RMO_Case_Bank_Simple_Steps_Colour-1.pdf",
                               "cards": cards}, indent=1, ensure_ascii=False))
    print(f"Parsed {len(cases)} cases → {len(cards)} cards → {OUT}")
    if incomplete:
        print(f"⚠ {len(incomplete)} cases missing a field:")
        for c in incomplete:
            missing = [k for k in ("first", "steps", "trap", "say") if not c[k]]
            print(f"   {c['part']}{c['num']} {c['title'][:50]} — missing {missing}")


if __name__ == "__main__":
    main()
