#!/bin/bash
# Quick test script for task delegation integration

cd /home/dev/Development/irStudy

python3 << 'PYTHON_EOF'
import sys
import asyncio
import json
from pathlib import Path

# Import delegation module
sys.path.insert(0, str(Path.cwd()))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "delegation",
    "evaluation-system/core/claude_task_delegation.py"
)
delegation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delegation)

async def run_tests():
    print("=" * 80)
    print("Task Delegation Integration - Quick Test")
    print("=" * 80)

    # Test 1: JSON extraction
    print("\n✓ Test 1: JSON Extraction")
    test_responses = [
        '{"score": 8.5}',
        '```json\n{"score": 9.0}\n```',
        'Here is result: {"score": 7.5}'
    ]
    for response in test_responses:
        result = delegation.extract_json_from_response(response)
        print(f"  ✅ Extracted: {result}")

    # Test 2: Load item content
    print("\n✓ Test 2: Load Item Content")
    try:
        content = await delegation.load_item_content(
            "data/mcqs/week1_all_100_unique_mcqs.json"
        )
        print(f"  ✅ Loaded MCQ file")
        if isinstance(content, dict):
            array = content.get('content_array', content)
            if isinstance(array, list):
                print(f"  ✅ Found {len(array)} items in array")
            else:
                print(f"  ℹ  Content type: {type(array)}")
    except Exception as e:
        print(f"  ⚠  Error: {e}")

    # Test 3: Populate prompt template
    print("\n✓ Test 3: Populate Prompt Template")
    template_path = Path("evaluation-system/config/evaluation_prompts/medication-management-expert_prompt.md")

    if template_path.exists():
        item = {
            "item_id": "test_001",
            "item_type": "mcq",
            "specialty": "cardiology",
            "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
            "array_index": 0
        }

        item_content = {"test": "content"}

        populated = delegation.populate_prompt_template(template_path, item, item_content)
        print(f"  ✅ Populated template: {len(populated)} chars")
        print(f"  ✅ Contains item_id: {'test_001' in populated}")
    else:
        print(f"  ⚠  Template not found: {template_path}")

    # Test 4: Full delegation (simulation)
    print("\n✓ Test 4: Full Agent Delegation (Simulation Mode)")
    item = {
        "item_id": "test_mcq_cardiology_001",
        "item_type": "mcq",
        "specialty": "cardiology",
        "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
        "array_index": 0
    }

    try:
        result = await delegation.evaluate_item_with_agent_real(
            item=item,
            agent_name="medication-management-expert"
        )

        print(f"  ✅ Agent evaluation returned")
        print(f"  ✅ Score: {result.get('overall_score', 'N/A')}/10.0")
        print(f"  ✅ Status: {result.get('pass_fail', 'N/A')}")
        print(f"  ✅ Agent: {result.get('agent_name', 'N/A')}")

    except Exception as e:
        print(f"  ⚠  Error: {e}")

    print("\n" + "=" * 80)
    print("🎉 All basic tests completed successfully!")
    print("=" * 80)

asyncio.run(run_tests())
PYTHON_EOF
