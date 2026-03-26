#!/usr/bin/env python3
"""
Test real agent integration with a single item.
Verifies that the Anthropic API integration works correctly.
"""

import asyncio
import json
import sys
import importlib.util
from pathlib import Path

# Load delegation module dynamically
spec = importlib.util.spec_from_file_location(
    "delegation",
    str(Path(__file__).parent.parent / "core" / "claude_task_delegation.py")
)
delegation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delegation)

# Import functions
evaluate_item_with_agent_real = delegation.evaluate_item_with_agent_real
TaskDelegationError = delegation.TaskDelegationError
JSONParseError = delegation.JSONParseError


async def test_single_item_evaluation():
    """Test evaluation of a single MCQ item with medication-management-expert."""
    print("=" * 80)
    print("Real Agent Integration Test - Single Item")
    print("=" * 80)
    print()

    # Test item - first MCQ from week1
    test_item = {
        "item_id": "mcq_week1_000",
        "item_type": "mcq",
        "specialty": "cardiology",
        "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
        "array_index": 0
    }

    # Test agent - medication-management-expert (has comprehensive prompt template)
    test_agent = "medication-management-expert"

    print(f"📋 Test Configuration:")
    print(f"   Item ID: {test_item['item_id']}")
    print(f"   Item Type: {test_item['item_type']}")
    print(f"   Specialty: {test_item['specialty']}")
    print(f"   Agent: {test_agent}")
    print()

    try:
        print("🚀 Calling real expert agent via Anthropic API...")
        print()

        result = await evaluate_item_with_agent_real(
            item=test_item,
            agent_name=test_agent
        )

        print("✅ Agent evaluation completed successfully!")
        print()
        print("=" * 80)
        print("Evaluation Result")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        print()

        # Verify required fields
        required_fields = [
            "agent_name",
            "item_id",
            "evaluation_date",
            "overall_score",
            "criteria_scores",
            "violations",
            "suggestions",
            "strengths",
            "pass_fail",
        ]

        missing_fields = [f for f in required_fields if f not in result]

        if missing_fields:
            print(f"⚠️  WARNING: Missing required fields: {missing_fields}")
            return False

        print("=" * 80)
        print("Validation Results")
        print("=" * 80)
        print(f"✅ All required fields present: {len(required_fields)}/{len(required_fields)}")
        print(f"✅ Agent: {result.get('agent_name')}")
        print(f"✅ Overall Score: {result.get('overall_score')}/10.0")
        print(f"✅ Status: {result.get('pass_fail')}")
        print(f"✅ Criteria Scores: {len(result.get('criteria_scores', {}))}")
        print(f"✅ Violations: {len(result.get('violations', []))}")
        print(f"✅ Suggestions: {len(result.get('suggestions', []))}")
        print(f"✅ Strengths: {len(result.get('strengths', []))}")
        print()

        # Check score range
        score = result.get('overall_score', 0)
        if not (0 <= score <= 10):
            print(f"⚠️  WARNING: Score {score} is outside valid range [0-10]")
            return False

        # Check pass/fail consistency
        pass_fail = result.get('pass_fail', '')
        if pass_fail not in ['PASS', 'FAIL']:
            print(f"⚠️  WARNING: Invalid pass_fail value: {pass_fail}")
            return False

        print("🎉 Real agent integration test PASSED!")
        print()
        print("=" * 80)
        print("Next Steps")
        print("=" * 80)
        print("1. ✅ Single item test passed")
        print("2. ⏭️  Run 10-item test: python3 evaluation-system/scripts/test_ten_items.py")
        print("3. ⏭️  Run production evaluation: python3 evaluation-system/core/evaluation_orchestrator.py")
        print()

        return True

    except TaskDelegationError as e:
        print(f"❌ Task delegation error: {e}")
        return False

    except JSONParseError as e:
        print(f"❌ JSON parsing error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_item_evaluation())
    sys.exit(0 if success else 1)
