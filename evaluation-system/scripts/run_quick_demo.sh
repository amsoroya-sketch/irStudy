#!/bin/bash
#
# Quick Demo - 1% Sample (30 items)
# Fast demonstration of system capabilities using Claude CLI
#
# Estimated time: 2-3 hours
# Cost: $0 (uses Claude CLI)

set -e

echo "========================================================================"
echo "QUICK DEMO - 1% Sample (30 items)"
echo "========================================================================"
echo ""
echo "This demo will show you:"
echo "  ✓ How the evaluation system works"
echo "  ✓ What violations are detected"
echo "  ✓ Score distribution across items"
echo "  ✓ Auto-fix capabilities"
echo ""
echo "Estimated time: 2-3 hours"
echo "Cost: $0"
echo ""

# Select 30 representative items
echo "Selecting 30-item sample..."

python3 << 'PYTHON_EOF'
import json
import random
from pathlib import Path

# Load registry
with open("evaluation-system/data/knowledge_item_registry.json") as f:
    registry = json.load(f)

pending_items = [
    item for item in registry["knowledge_items"]
    if item["evaluation_status"] == "pending"
]

# Stratified sample - 10 MCQs, 10 OSCEs, 10 study cards
sample_items = []

# Get items by type
by_type = {}
for item in pending_items:
    item_type = item.get("item_type", "unknown")
    if item_type not in by_type:
        by_type[item_type] = []
    by_type[item_type].append(item)

# Sample 10 from each major type
for item_type in ["mcq", "osce_script", "study_card"]:
    if item_type in by_type and len(by_type[item_type]) >= 10:
        sampled = random.sample(by_type[item_type], 10)
        sample_items.extend(sampled)
        print(f"✓ Selected 10 {item_type} items")

print(f"\nTotal sample: {len(sample_items)} items")

# Create demo registry
demo_registry = {
    "registry_version": "1.0.0",
    "generated_at": registry.get("generated_at", "2026-03-25"),
    "statistics": {
        "total_items": len(sample_items),
        "by_status": {"pending": len(sample_items)}
    },
    "knowledge_items": sample_items
}

# Save
output_path = Path("evaluation-system/reports/demo_registry.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(demo_registry, f, indent=2)

print(f"✅ Demo registry saved: {output_path}")
PYTHON_EOF

echo ""
echo "========================================================================"
echo "Starting evaluation (this will take 2-3 hours)..."
echo "========================================================================"
echo ""
echo "You can monitor progress in real-time."
echo "Press Ctrl+C to stop at any time (progress will be saved)."
echo ""
sleep 2

# Create output directory
DEMO_DIR="evaluation-system/reports/demo_run_$(date +%Y%m%d_%H%M%S)"

# Run evaluation with Claude CLI
venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \
  --registry-path evaluation-system/reports/demo_registry.json \
  --output-dir "$DEMO_DIR" \
  --delegation-mode cli \
  --batch-size 2 \
  --batch-delay 2

echo ""
echo "========================================================================"
echo "✅ DEMO COMPLETE"
echo "========================================================================"
echo ""
echo "Results: $DEMO_DIR"
echo ""
echo "Analyzing results..."

# Generate analysis report
venv/bin/python3 evaluation-system/scripts/analyze_results.py \
  --input "$DEMO_DIR/summary.json" \
  --output "$DEMO_DIR/analysis.html"

echo ""
echo "✅ Analysis complete!"
echo ""
echo "Open the report:"
echo "  xdg-open $DEMO_DIR/analysis.html"
echo ""
echo "Or view summary:"
echo "  cat $DEMO_DIR/summary.json | jq '.statistics'"
echo ""
echo "========================================================================"
echo "Next Steps:"
echo "========================================================================"
echo ""
echo "Based on these 30 items, you can see:"
echo "  1. Average score achieved"
echo "  2. Types of violations detected"
echo "  3. How auto-fix would improve scores"
echo "  4. Estimated time for full 2,963 items"
echo ""
echo "To run full 10% pilot (296 items):"
echo "  ./evaluation-system/scripts/run_pilot_evaluation.sh"
echo ""
echo "To run full evaluation (2,963 items):"
echo "  venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \\"
echo "    --delegation-mode cli"
echo ""
echo "========================================================================"
