#!/usr/bin/env python3
"""
Test script for Task tool delegation integration.
Verifies that agent delegation, prompt population, and JSON parsing work correctly.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation_system.core.claude_task_delegation import (
    load_item_content,
    populate_prompt_template,
    extract_json_from_response,
    evaluate_item_with_agent_real,
    TaskDelegationError,
    JSONParseError
)


async def test_load_item_content():
    """Test loading item content from file."""
    print("=" * 80)
    print("Test 1: Load Item Content")
    print("=" * 80)

    # Test MCQ (array-based content)
    item_path = "data/mcqs/week1_all_100_unique_mcqs.json"

    try:
        content = await load_item_content(item_path)
        print(f"✅ Loaded item content: {item_path}")
        print(f"   Type: {content.get('type')}")

        if content.get('type') == 'array':
            print(f"   Array length: {len(content.get('content_array', []))}")
            if content.get('content_array'):
                print(f"   First item preview: {str(content['content_array'][0])[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error loading item content: {e}")
        return False


async def test_populate_prompt():
    """Test prompt template population."""
    print("\n" + "=" * 80)
    print("Test 2: Populate Prompt Template")
    print("=" * 80)

    base_dir = Path(__file__).parent.parent.parent
    template_path = base_dir / "evaluation-system/config/evaluation_prompts/medication-management-expert_prompt.md"

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False

    item = {
        "item_id": "test_mcq_001",
        "item_type": "mcq",
        "specialty": "cardiology",
        "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
        "array_index": 0
    }

    # Load content
    content = await load_item_content(item["file_path"])

    try:
        populated = populate_prompt_template(template_path, item, content)

        print(f"✅ Populated prompt template")
        print(f"   Template size: {len(populated)} characters")
        print(f"   Contains item_id: {'{{item_id}}' not in populated}")
        print(f"   Contains actual ID: {item['item_id'] in populated}")

        # Show sample
        print(f"\n   Preview (first 300 chars):")
        print(f"   {populated[:300]}...")

        return True

    except Exception as e:
        print(f"❌ Error populating template: {e}")
        return False


def test_json_extraction():
    """Test JSON extraction from various formats."""
    print("\n" + "=" * 80)
    print("Test 3: JSON Extraction")
    print("=" * 80)

    test_cases = [
        # Case 1: Pure JSON
        (
            '{"agent_name": "test", "score": 8.5}',
            "Pure JSON"
        ),
        # Case 2: JSON in markdown code block
        (
            '''Here is the evaluation:

```json
{
  "agent_name": "medication-management-expert",
  "overall_score": 8.5,
  "pass_fail": "PASS"
}
```

That's my evaluation.''',
            "JSON in markdown block"
        ),
        # Case 3: JSON with surrounding text
        (
            '''The evaluation results are as follows:

{"agent_name": "test", "score": 9.0, "violations": []}

Please review.''',
            "JSON with surrounding text"
        ),
    ]

    all_passed = True

    for response_text, description in test_cases:
        try:
            result = extract_json_from_response(response_text)
            print(f"✅ {description}: Extracted successfully")
            print(f"   Keys: {list(result.keys())}")

        except JSONParseError as e:
            print(f"❌ {description}: Failed to extract")
            print(f"   Error: {e}")
            all_passed = False

    return all_passed


async def test_full_delegation():
    """Test full end-to-end delegation (with simulation)."""
    print("\n" + "=" * 80)
    print("Test 4: Full Agent Delegation (Simulation Mode)")
    print("=" * 80)

    item = {
        "item_id": "test_mcq_cardiology_001",
        "item_type": "mcq",
        "specialty": "cardiology",
        "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
        "array_index": 0
    }

    agents_to_test = [
        "medication-management-expert",
        "clinical-documentation-expert",
        "radiology-interpretation-expert"
    ]

    all_passed = True

    for agent_name in agents_to_test:
        try:
            print(f"\n   Testing {agent_name}...")

            result = await evaluate_item_with_agent_real(
                item=item,
                agent_name=agent_name
            )

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
                print(f"   ❌ Missing required fields: {missing_fields}")
                all_passed = False
            else:
                print(f"   ✅ All required fields present")
                print(f"      Score: {result['overall_score']}/10.0")
                print(f"      Status: {result['pass_fail']}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False

    return all_passed


async def main():
    """Run all tests."""
    print("=" * 80)
    print("Task Delegation Integration Tests")
    print("=" * 80)
    print()

    results = {}

    # Test 1: Load item content
    results["load_content"] = await test_load_item_content()

    # Test 2: Populate prompt
    results["populate_prompt"] = await test_populate_prompt()

    # Test 3: JSON extraction
    results["json_extraction"] = test_json_extraction()

    # Test 4: Full delegation
    results["full_delegation"] = await test_full_delegation()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()

    if all(results.values()):
        print("🎉 All tests passed! Task delegation integration is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
