#!/usr/bin/env python3
"""
Claude CLI Delegation Wrapper
Alternative to API-based delegation - uses local `claude` CLI instead.

Advantages:
- No API key required
- Uses existing claude authentication
- Zero setup

Disadvantages:
- Slower than API (10-15 items/hour vs 60 items/hour)
- Requires claude CLI installed and authenticated

Usage:
    # Use this instead of claude_task_delegation.py
    from claude_cli_delegation import evaluate_item_with_agent_real
"""

import json
import re
import asyncio
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class TaskDelegationError(Exception):
    """Raised when task delegation fails."""
    pass


class JSONParseError(Exception):
    """Raised when agent returns invalid JSON."""
    pass


async def load_item_content(file_path: str, base_dir: Path = None) -> Dict[str, Any]:
    """
    Load item content from file.
    (Same as claude_task_delegation.py)
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent

    full_path = base_dir / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"Item file not found: {file_path}")

    with open(full_path, 'r', encoding='utf-8') as f:
        if full_path.suffix == '.json':
            content = json.load(f)

            if isinstance(content, list):
                return {"content_array": content, "type": "array"}
            else:
                return content
        else:
            return {"content": f.read(), "type": "text"}


def populate_prompt_template(
    template_path: Path,
    item: Dict[str, Any],
    item_content: Dict[str, Any]
) -> str:
    """
    Populate evaluation prompt template with item data.
    (Same as claude_task_delegation.py)
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Handle array-based content
    if item_content.get("type") == "array":
        array_index = item.get("array_index", 0)
        content_array = item_content.get("content_array", [])

        if 0 <= array_index < len(content_array):
            actual_content = content_array[array_index]
        else:
            actual_content = {"error": f"Array index {array_index} out of bounds"}
    else:
        actual_content = item_content

    # Replace placeholders
    replacements = {
        "{{item_id}}": item.get("item_id", ""),
        "{{item_type}}": item.get("item_type", ""),
        "{{specialty}}": item.get("specialty", ""),
        "{{file_path}}": item.get("file_path", ""),
        "{{item_content}}": json.dumps(actual_content, indent=2),
        "{{current_timestamp}}": datetime.now().isoformat(),
    }

    populated = template
    for placeholder, value in replacements.items():
        populated = populated.replace(placeholder, value)

    return populated


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Extract JSON from agent response.
    (Same as claude_task_delegation.py)
    """
    # Try direct JSON parse first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    json_patterns = [
        r'```json\s*\n(.*?)\n```',
        r'```\s*\n(.*?)\n```',
        r'\{.*\}',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            try:
                json_text = match.group(1) if match.lastindex else match.group(0)
                return json.loads(json_text)
            except json.JSONDecodeError:
                continue

    raise JSONParseError(
        f"Could not extract valid JSON from agent response. "
        f"Response preview: {response_text[:500]}"
    )


async def delegate_to_agent_cli(
    subagent_type: str,
    prompt: str,
    model: str = "sonnet",
    description: str = "Evaluate medical content",
    max_retries: int = 2,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Delegate evaluation task to expert agent using claude CLI.

    This uses subprocess to call the `claude` command with the evaluation prompt.
    The agent context is loaded from .claude/agents/{subagent_type}.md

    Args:
        subagent_type: Agent name (e.g., "medication-management-expert")
        prompt: Evaluation prompt with item content
        model: Claude model to use (sonnet/opus/haiku)
        description: Short task description
        max_retries: Number of retry attempts
        timeout: Timeout in seconds

    Returns:
        Parsed evaluation result as dictionary

    Raises:
        TaskDelegationError: If CLI call fails
        JSONParseError: If response is not valid JSON
    """

    # Verify agent exists
    agent_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / f"{subagent_type}.md"

    if not agent_path.exists():
        raise TaskDelegationError(f"Agent file not found: {agent_path}")

    # Load agent content to include in prompt
    with open(agent_path, 'r', encoding='utf-8') as f:
        agent_content = f.read()

    # Extract agent expertise (skip YAML frontmatter)
    agent_lines = agent_content.split('\n')
    in_frontmatter = False
    agent_system = []

    for line in agent_lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
            continue

        if not in_frontmatter:
            agent_system.append(line)

    agent_expertise = '\n'.join(agent_system)

    # Combine agent expertise with evaluation task
    full_prompt = f"""
{agent_expertise}

---

## EVALUATION TASK

You are performing a medical content evaluation. **Your response MUST be ONLY valid JSON** with no additional text before or after.

{prompt}

**CRITICAL**: Return ONLY the JSON evaluation result. No explanations, no commentary, just pure JSON.
"""

    for attempt in range(max_retries + 1):
        try:
            # Call claude CLI via stdin (not --file which doesn't exist)
            # Use --print for non-interactive output
            result = await asyncio.create_subprocess_exec(
                'claude',
                '--print',
                '--model', model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                # Send prompt via stdin
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(input=full_prompt.encode('utf-8')),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                result.kill()
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue
                raise TimeoutError(f"Claude CLI exceeded timeout of {timeout}s")

            # Check return code
            if result.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                if attempt < max_retries:
                    await asyncio.sleep(1)
                    continue
                raise TaskDelegationError(
                    f"Claude CLI failed with exit code {result.returncode}\n"
                    f"Error: {error_msg}"
                )

            # Parse response
            response_text = stdout.decode('utf-8')

            # Extract JSON from response
            return extract_json_from_response(response_text)

        except json.JSONDecodeError as e:
            if attempt < max_retries:
                await asyncio.sleep(1)
                continue
            raise JSONParseError(f"Agent returned invalid JSON: {e}")

        except FileNotFoundError:
            raise TaskDelegationError(
                "Claude CLI not found. Please install with: pip install claude-cli\n"
                "Or ensure 'claude' command is in your PATH"
            )

        except Exception as e:
            if attempt < max_retries:
                await asyncio.sleep(1)
                continue
            raise TaskDelegationError(f"Delegation failed: {e}")


async def evaluate_item_with_agent_real(
    item: Dict[str, Any],
    agent_name: str,
    base_dir: Path = None
) -> Dict[str, Any]:
    """
    High-level function to evaluate an item with a specific agent using Claude CLI.

    This combines all steps:
    1. Load item content
    2. Load and populate prompt template
    3. Delegate to agent via CLI
    4. Return parsed result

    Args:
        item: Item metadata from registry
        agent_name: Expert agent name
        base_dir: Base directory (defaults to irStudy root)

    Returns:
        Evaluation result dictionary
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent

    # Load item content
    item_content = await load_item_content(item["file_path"], base_dir)

    # Load and populate prompt template
    prompts_dir = base_dir / "evaluation-system" / "config" / "evaluation_prompts"

    template_candidates = [
        prompts_dir / f"{agent_name}_prompt.md",
        prompts_dir / f"{agent_name.replace('-', '_')}_prompt.md",
        prompts_dir / f"{agent_name.replace('-expert', '')}_prompt.md",
        prompts_dir / f"{agent_name.replace('-expert', '').replace('-', '_')}_prompt.md",
    ]

    template_path = None
    for candidate in template_candidates:
        if candidate.exists():
            template_path = candidate
            break

    if template_path is None:
        raise TaskDelegationError(
            f"Prompt template not found. Tried:\n" +
            "\n".join(f"  - {c}" for c in template_candidates)
        )

    evaluation_prompt = populate_prompt_template(template_path, item, item_content)

    # Delegate to agent via CLI
    result = await delegate_to_agent_cli(
        subagent_type=agent_name,
        prompt=evaluation_prompt,
        model="sonnet",
        description=f"Evaluate {item['item_id']}"
    )

    return result


# =============================================================================
# CLI-SPECIFIC NOTES
# =============================================================================
"""
This module provides Claude CLI integration as an alternative to API-based delegation.

ADVANTAGES:
- No API key required
- Uses existing claude authentication
- Zero setup overhead

DISADVANTAGES:
- Slower than API (10-15 items/hour vs 60 items/hour)
- Requires claude CLI installed
- Less robust error handling than API

USAGE:
To use this instead of the API version, update evaluation_orchestrator.py:

    # Change this line:
    from evaluation_system.core.claude_task_delegation import evaluate_item_with_agent_real

    # To this:
    from evaluation_system.core.claude_cli_delegation import evaluate_item_with_agent_real

TESTING:
    python3 -c "
    import asyncio
    from pathlib import Path
    import sys
    sys.path.insert(0, '.')
    from evaluation_system.core.claude_cli_delegation import evaluate_item_with_agent_real

    async def test():
        item = {
            'item_id': 'test_001',
            'item_type': 'mcq',
            'specialty': 'cardiology',
            'file_path': 'data/mcqs/week1_all_100_unique_mcqs.json',
            'array_index': 0
        }
        result = await evaluate_item_with_agent_real(item, 'medication-management-expert')
        print(result)

    asyncio.run(test())
    "
"""
