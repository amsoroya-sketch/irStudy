#!/usr/bin/env python3
"""
Test Claude CLI delegation with a single medical content item.
This will help debug any issues with the CLI integration.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.claude_cli_delegation import evaluate_item_with_agent_real


async def test_single_evaluation():
    """Test evaluating a single item with one agent."""

    print("=" * 80)
    print("TESTING CLAUDE CLI DELEGATION")
    print("=" * 80)
    print()

    # Create a test item pointing to an actual MCQ file
    test_item = {
        "item_id": "mcq_week1_test_001",
        "item_type": "mcq",
        "specialty": "cardiology",
        "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
        "array_index": 0  # First MCQ in the array
    }

    print(f"Test Item: {test_item['item_id']}")
    print(f"Type: {test_item['item_type']}")
    print(f"Specialty: {test_item['specialty']}")
    print(f"File: {test_item['file_path']}")
    print()

    # Test with medication-management-expert
    agent_name = "medication-management-expert"

    print(f"Testing delegation to: {agent_name}")
    print("This will take 30-60 seconds...")
    print()

    try:
        result = await evaluate_item_with_agent_real(
            item=test_item,
            agent_name=agent_name
        )

        print("✅ SUCCESS! Received evaluation result:")
        print()
        print(json.dumps(result, indent=2))
        print()

        # Validate result structure
        required_fields = ["overall_score", "criteria_scores", "violations", "suggestions", "strengths", "pass_fail"]
        missing = [f for f in required_fields if f not in result]

        if missing:
            print(f"⚠️  Warning: Missing fields: {missing}")
        else:
            print("✅ All required fields present")

        print()
        print(f"Overall Score: {result.get('overall_score', 'N/A')}/10")
        print(f"Pass/Fail: {result.get('pass_fail', 'N/A')}")
        print(f"Violations: {len(result.get('violations', []))}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_evaluation())
    sys.exit(0 if success else 1)
