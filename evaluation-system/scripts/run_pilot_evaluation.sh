#!/bin/bash
#
# Pilot Evaluation Run - 10% Sample (296 items)
# Uses Claude CLI (zero setup) to demonstrate system capabilities
#
# This will:
# 1. Select representative 10% sample across all content types
# 2. Run evaluation using Claude CLI (no API key needed)
# 3. Generate comprehensive analysis report
# 4. Show cost-benefit comparison for full run
#
# Estimated time: 20-30 hours (but you can stop anytime to assess)

set -e

echo "========================================================================"
echo "PILOT EVALUATION - 10% Sample (296 items)"
echo "========================================================================"
echo ""
echo "This pilot will demonstrate:"
echo "  ✓ Automated quality evaluation"
echo "  ✓ Violation detection (drug names, red flags, cultural safety)"
echo "  ✓ Score distribution and approval rates"
echo "  ✓ Auto-fix capability assessment"
echo "  ✓ ROI calculation for full run"
echo ""
echo "Estimated time: 20-30 hours (can be interrupted)"
echo "Cost: $0 (uses Claude CLI, no API key needed)"
echo ""
read -p "Press Enter to start pilot evaluation, or Ctrl+C to cancel..."
echo ""

# Calculate 10% sample
TOTAL_ITEMS=2963
SAMPLE_SIZE=296  # 10% of 2963

echo "Step 1: Selecting representative sample ($SAMPLE_SIZE items)..."

# Create stratified sample (proportional across content types)
python3 << 'PYTHON_EOF'
import json
import random
from pathlib import Path

# Load registry
registry_path = Path("evaluation-system/data/knowledge_item_registry.json")
with open(registry_path) as f:
    registry = json.load(f)

pending_items = [
    item for item in registry["knowledge_items"]
    if item["evaluation_status"] == "pending"
]

print(f"Total pending items: {len(pending_items)}")

# Stratified sampling by content type
by_type = {}
for item in pending_items:
    item_type = item.get("item_type", "unknown")
    if item_type not in by_type:
        by_type[item_type] = []
    by_type[item_type].append(item)

print(f"\nDistribution:")
for item_type, items in by_type.items():
    print(f"  {item_type}: {len(items)} items")

# Calculate sample sizes proportionally
total_pending = len(pending_items)
target_sample = 296

sample_items = []
for item_type, items in by_type.items():
    proportion = len(items) / total_pending
    type_sample_size = int(target_sample * proportion)

    # Random sample from this type
    if type_sample_size > 0:
        sampled = random.sample(items, min(type_sample_size, len(items)))
        sample_items.extend(sampled)
        print(f"  Sampling {len(sampled)} {item_type} items")

print(f"\nTotal sample size: {len(sample_items)}")

# Save sample to file
sample_output = {
    "sample_metadata": {
        "total_pending": total_pending,
        "target_sample_size": target_sample,
        "actual_sample_size": len(sample_items),
        "sampling_method": "stratified_random",
    },
    "sample_items": sample_items
}

output_path = Path("evaluation-system/reports/pilot_sample.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(sample_output, f, indent=2)

print(f"\n✅ Sample saved to: {output_path}")
PYTHON_EOF

echo ""
echo "✅ Sample selection complete"
echo ""

# Step 2: Run evaluation with Claude CLI
echo "Step 2: Running evaluation with Claude CLI..."
echo ""
echo "NOTE: This will take 20-30 hours to complete."
echo "      You can stop at any time (Ctrl+C) and assess partial results."
echo "      Progress will be saved, and you can resume later."
echo ""

# Create pilot output directory
PILOT_DIR="evaluation-system/reports/pilot_run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$PILOT_DIR"

echo "Output directory: $PILOT_DIR"
echo ""

# Run orchestrator with CLI delegation on sample
echo "Starting evaluation..."
echo ""

# Note: We'll create a custom registry for just the sample items
python3 << PYTHON_EOF
import json
from pathlib import Path

# Load sample
with open("evaluation-system/reports/pilot_sample.json") as f:
    sample = json.load(f)

# Load full registry
with open("evaluation-system/data/knowledge_item_registry.json") as f:
    registry = json.load(f)

# Create pilot registry with just sample items
pilot_registry = {
    "registry_version": registry["registry_version"],
    "generated_at": registry.get("generated_at", "2026-03-25"),
    "statistics": {
        "total_items": len(sample["sample_items"]),
        "by_type": {},
        "by_status": {"pending": len(sample["sample_items"])}
    },
    "knowledge_items": sample["sample_items"]
}

# Update statistics
for item in sample["sample_items"]:
    item_type = item.get("item_type", "unknown")
    pilot_registry["statistics"]["by_type"][item_type] = \
        pilot_registry["statistics"]["by_type"].get(item_type, 0) + 1

# Save pilot registry
pilot_registry_path = Path("evaluation-system/reports/pilot_registry.json")
with open(pilot_registry_path, 'w') as f:
    json.dump(pilot_registry, f, indent=2)

print(f"✅ Pilot registry created: {pilot_registry_path}")
PYTHON_EOF

echo ""

# Run evaluation
venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \
  --registry-path evaluation-system/reports/pilot_registry.json \
  --output-dir "$PILOT_DIR" \
  --delegation-mode cli \
  --batch-size 3 \
  --batch-delay 1

echo ""
echo "========================================================================"
echo "✅ PILOT EVALUATION COMPLETE"
echo "========================================================================"
echo ""
echo "Results saved to: $PILOT_DIR"
echo ""
echo "Next steps:"
echo "  1. Analyze results:"
echo "     venv/bin/python3 evaluation-system/scripts/analyze_results.py \\"
echo "       --input $PILOT_DIR/summary.json \\"
echo "       --output $PILOT_DIR/analysis.html"
echo ""
echo "  2. Open report:"
echo "     xdg-open $PILOT_DIR/analysis.html"
echo ""
echo "  3. Assess outcomes and decide:"
echo "     - Continue with full run (2,667 remaining items)"
echo "     - Adjust parameters"
echo "     - Or switch to API mode for faster completion"
echo ""
echo "========================================================================"
