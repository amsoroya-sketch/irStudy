#!/usr/bin/env python3
"""
Analyze all generic citations (those without page/section numbers)
"""

import re
import os
from pathlib import Path
from collections import defaultdict
import json


def analyze_citations():
    """Analyze all citations in OSCE files"""

    print("🔍 Analyzing citations in OSCE files...")
    print("=" * 80)

    # Patterns for different citation types
    patterns = {
        "talley": r"\(Talley[^)]*?(?:8th ed|Clinical Examination)[^)]*?\)",
        "murtagh": r"\(Murtagh[^)]*?(?:8th ed|General Practice)[^)]*?\)",
        "etg": r"\(Therapeutic Guidelines:[^)]*?\)",
        "oxford": r"\(Oxford[^)]*?(?:Handbook|Emergency)[^)]*?\)",
        "amc": r"\(AMC[^)]*?\)",
        "other": r"\([^)]*?(?:Guidelines|Handbook|Manual)[^)]*?\)",
    }

    # Stats
    stats = {
        "talley_with_page": 0,
        "talley_without_page": 0,
        "murtagh_with_page": 0,
        "murtagh_without_page": 0,
        "etg_with_section": 0,
        "etg_without_section": 0,
        "oxford_with_page": 0,
        "oxford_without_page": 0,
        "amc_with_page": 0,
        "amc_without_page": 0,
        "other_citations": 0,
    }

    generic_citations = defaultdict(list)

    # Scan all .md files
    osce_dir = Path("ICRP_OSCE_Preparation")
    md_files = list(osce_dir.rglob("*.md"))

    print(f"📂 Scanning {len(md_files)} markdown files...")
    print()

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # Check Talley citations
                for match in re.finditer(patterns["talley"], line):
                    citation = match.group()
                    if re.search(r"p\.\s*\d+", citation):
                        stats["talley_with_page"] += 1
                    else:
                        stats["talley_without_page"] += 1
                        generic_citations["Talley"].append(
                            {
                                "file": str(md_file),
                                "line": line_num,
                                "citation": citation,
                                "context": line.strip()[:100],
                            }
                        )

                # Check Murtagh citations
                for match in re.finditer(patterns["murtagh"], line):
                    citation = match.group()
                    if re.search(r"p\.\s*\d+", citation):
                        stats["murtagh_with_page"] += 1
                    else:
                        stats["murtagh_without_page"] += 1
                        generic_citations["Murtagh"].append(
                            {
                                "file": str(md_file),
                                "line": line_num,
                                "citation": citation,
                                "context": line.strip()[:100],
                            }
                        )

                # Check eTG citations
                for match in re.finditer(patterns["etg"], line):
                    citation = match.group()
                    if re.search(r"Section\s+[\d.]+", citation):
                        stats["etg_with_section"] += 1
                    else:
                        stats["etg_without_section"] += 1
                        generic_citations["eTG"].append(
                            {
                                "file": str(md_file),
                                "line": line_num,
                                "citation": citation,
                                "context": line.strip()[:100],
                            }
                        )

                # Check Oxford citations
                for match in re.finditer(patterns["oxford"], line):
                    citation = match.group()
                    if re.search(r"p\.\s*\d+", citation):
                        stats["oxford_with_page"] += 1
                    else:
                        stats["oxford_without_page"] += 1
                        generic_citations["Oxford"].append(
                            {
                                "file": str(md_file),
                                "line": line_num,
                                "citation": citation,
                                "context": line.strip()[:100],
                            }
                        )

                # Check AMC citations
                for match in re.finditer(patterns["amc"], line):
                    citation = match.group()
                    # Skip AMC exam structure references (these are allowed to be generic)
                    if "stations" in line.lower() or "exam has" in line.lower():
                        continue
                    if re.search(r"p\.\s*\d+", citation):
                        stats["amc_with_page"] += 1
                    else:
                        stats["amc_without_page"] += 1
                        generic_citations["AMC"].append(
                            {
                                "file": str(md_file),
                                "line": line_num,
                                "citation": citation,
                                "context": line.strip()[:100],
                            }
                        )

        except Exception as e:
            print(f"⚠️  Error reading {md_file}: {e}")
            continue

    # Print results
    print("📊 Citation Analysis Results:")
    print("=" * 80)
    print()

    print("✅ Citations WITH exact references:")
    print(f"   Talley with pages:        {stats['talley_with_page']}")
    print(f"   Murtagh with pages:       {stats['murtagh_with_page']}")
    print(f"   eTG with sections:        {stats['etg_with_section']}")
    print(f"   Oxford with pages:        {stats['oxford_with_page']}")
    print(f"   AMC with pages:           {stats['amc_with_page']}")
    total_with_ref = (
        stats["talley_with_page"]
        + stats["murtagh_with_page"]
        + stats["etg_with_section"]
        + stats["oxford_with_page"]
        + stats["amc_with_page"]
    )
    print(f"   {'='*30}")
    print(f"   TOTAL WITH REFERENCES:    {total_with_ref}")
    print()

    print("❌ Citations WITHOUT exact references (GENERIC):")
    print(f"   Talley without pages:     {stats['talley_without_page']}")
    print(f"   Murtagh without pages:    {stats['murtagh_without_page']}")
    print(f"   eTG without sections:     {stats['etg_without_section']}")
    print(f"   Oxford without pages:     {stats['oxford_without_page']}")
    print(f"   AMC without pages:        {stats['amc_without_page']}")
    total_generic = (
        stats["talley_without_page"]
        + stats["murtagh_without_page"]
        + stats["etg_without_section"]
        + stats["oxford_without_page"]
        + stats["amc_without_page"]
    )
    print(f"   {'='*30}")
    print(f"   TOTAL GENERIC:            {total_generic}")
    print()

    print("📈 Coverage:")
    total_citations = total_with_ref + total_generic
    if total_citations > 0:
        coverage = (total_with_ref / total_citations) * 100
        print(f"   Total citations:          {total_citations}")
        print(f"   Exact reference coverage: {coverage:.1f}%")
        print(f"   Remaining work:           {total_generic} citations need exact references")
    print()

    print("🎯 Breakdown by Source:")
    print("-" * 80)
    for source, citations in sorted(generic_citations.items()):
        print(f"\n{source}: {len(citations)} generic citations")
        if citations:
            print(f"Sample:")
            for item in citations[:3]:
                file_short = Path(item["file"]).relative_to("ICRP_OSCE_Preparation")
                print(f"  - {file_short}:{item['line']}")
                print(f"    Citation: {item['citation']}")
                print(f"    Context: {item['context']}...")

    print("\n" + "=" * 80)

    # Save detailed report
    report = {
        "stats": stats,
        "total_with_ref": total_with_ref,
        "total_generic": total_generic,
        "coverage_percent": coverage if total_citations > 0 else 0,
        "generic_by_source": {
            source: [
                {
                    "file": str(Path(c["file"]).relative_to("ICRP_OSCE_Preparation")),
                    "line": c["line"],
                    "citation": c["citation"],
                    "context": c["context"],
                }
                for c in citations
            ]
            for source, citations in generic_citations.items()
        },
    }

    with open("generic_citations_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("📝 Detailed report saved to: generic_citations_report.json")

    return report


if __name__ == "__main__":
    analyze_citations()
