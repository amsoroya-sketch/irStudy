#!/usr/bin/env python3
"""
Task Tool Delegation Wrapper for irStudy Evaluation System
Integrates Claude Code's Task tool with evaluation orchestrator.

This module provides the bridge between the evaluation orchestrator and
real expert agents, handling:
- Item content loading
- Prompt template population
- Task tool delegation
- JSON response parsing
- Error handling and retries
"""

import json
import re
import asyncio
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add backend to path for Vault integration
backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

logger = logging.getLogger(__name__)


class TaskDelegationError(Exception):
    """Raised when task delegation fails."""
    pass


class JSONParseError(Exception):
    """Raised when agent returns invalid JSON."""
    pass


async def load_item_content(file_path: str, base_dir: Path = None) -> Dict[str, Any]:
    """
    Load item content from file.

    Args:
        file_path: Relative path to item file
        base_dir: Base directory (defaults to irStudy root)

    Returns:
        Item content as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent

    full_path = base_dir / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"Item file not found: {file_path}")

    with open(full_path, 'r', encoding='utf-8') as f:
        if full_path.suffix == '.json':
            content = json.load(f)

            # Handle array-based content (MCQs, OSCEs, study cards)
            # If item is part of an array, we need the array index
            if isinstance(content, list):
                # For array-based items, return the whole array
                # The orchestrator will need to specify which index to evaluate
                return {"content_array": content, "type": "array"}
            else:
                return content
        else:
            # Text-based content
            return {"content": f.read(), "type": "text"}


def populate_prompt_template(
    template_path: Path,
    item: Dict[str, Any],
    item_content: Dict[str, Any]
) -> str:
    """
    Populate evaluation prompt template with item data.

    Args:
        template_path: Path to prompt template markdown file
        item: Item metadata from registry
        item_content: Loaded item content

    Returns:
        Populated prompt string
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Handle array-based content
    if item_content.get("type") == "array":
        # Extract specific item from array using array_index
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

    Handles multiple formats:
    1. Pure JSON
    2. JSON in markdown code block
    3. JSON with surrounding text

    Args:
        response_text: Agent's text response

    Returns:
        Parsed JSON as dictionary

    Raises:
        JSONParseError: If JSON cannot be extracted or parsed
    """
    # Try direct JSON parse first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    json_patterns = [
        r'```json\s*\n(.*?)\n```',  # Standard markdown JSON block
        r'```\s*\n(.*?)\n```',       # Generic code block
        r'\{.*\}',                    # Any JSON object (greedy)
    ]

    for pattern in json_patterns:
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            try:
                json_text = match.group(1) if match.lastindex else match.group(0)
                return json.loads(json_text)
            except json.JSONDecodeError:
                continue

    # If all extraction attempts fail
    raise JSONParseError(
        f"Could not extract valid JSON from agent response. "
        f"Response preview: {response_text[:500]}"
    )


async def delegate_to_agent(
    subagent_type: str,
    prompt: str,
    model: str = "sonnet",
    description: str = "Evaluate medical content",
    max_retries: int = 2,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Delegate evaluation task to expert agent using Task tool.

    This is the core integration point with Claude Code's Task tool.

    IMPLEMENTATION NOTE:
    This function needs to be adapted based on how Task tool is exposed in your environment:

    Option 1: Claude Code SDK (if available)
    Option 2: Subprocess call to claude CLI
    Option 3: Direct Anthropic API call with agent context

    Current implementation: Placeholder that needs to be replaced with actual Task tool integration.

    Args:
        subagent_type: Agent name (e.g., "medication-management-expert")
        prompt: Evaluation prompt with item content and instructions
        model: Claude model to use (sonnet/opus/haiku)
        description: Short task description (for logging)
        max_retries: Number of retry attempts on failure
        timeout: Timeout in seconds

    Returns:
        Parsed evaluation result as dictionary

    Raises:
        TaskDelegationError: If delegation fails after retries
        JSONParseError: If agent returns invalid JSON
        TimeoutError: If agent exceeds timeout
    """

    # =============================================================================
    # PLACEHOLDER IMPLEMENTATION
    # =============================================================================
    # TODO: Replace with actual Task tool integration
    #
    # The implementation below is a PLACEHOLDER showing the expected interface.
    # You need to replace this with actual Task tool delegation based on your setup.
    # =============================================================================

    # Get API key from Vault (following ai_examiner.py pattern)
    try:
        from src.core.vault import get_vault_secret

        # Try primary path first
        try:
            api_key = get_vault_secret("secret/ai-osce/claude-api-key", "value")
            logger.info("✅ Claude API key retrieved from Vault (secret/ai-osce/claude-api-key)")
        except Exception:
            # Fallback to secondary path
            api_key = get_vault_secret("irStudy/claude", "api_key")
            logger.info("✅ Claude API key retrieved from Vault (irStudy/claude)")

    except Exception as e:
        raise TaskDelegationError(f"Could not retrieve Claude API key from Vault: {e}")

    for attempt in range(max_retries + 1):
        try:
            # ---------------------------------------------------------------------
            # REAL IMPLEMENTATION: Direct Anthropic API call with Vault integration
            # ---------------------------------------------------------------------
            # Following the pattern from backend/src/ai/ai_examiner.py

            from anthropic import Anthropic

            # Load agent system prompt
            agent_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / f"{subagent_type}.md"

            if not agent_path.exists():
                raise TaskDelegationError(f"Agent file not found: {agent_path}")

            with open(agent_path, 'r', encoding='utf-8') as f:
                agent_content = f.read()

            # Extract agent expertise from markdown (skip YAML frontmatter)
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

            agent_system_prompt = '\n'.join(agent_system)

            # Combine agent expertise + evaluation task instruction
            full_system_prompt = f"""{agent_system_prompt}

---

## EVALUATION TASK

You are now performing a medical content evaluation task. Your response MUST be valid JSON only, with no additional text before or after the JSON.

Follow the evaluation criteria and output format specified in the prompt below."""

            # Initialize Anthropic client
            client = Anthropic(api_key=api_key)

            # Call Claude API
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=full_system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=timeout
            )

            # Extract text response
            result_text = response.content[0].text

            # Parse JSON from response
            return extract_json_from_response(result_text)

        except json.JSONDecodeError as e:
            if attempt < max_retries:
                # Retry on JSON parse error
                await asyncio.sleep(1)
                continue
            else:
                raise JSONParseError(f"Agent {subagent_type} returned invalid JSON after {max_retries} retries: {e}")

        except asyncio.TimeoutError:
            if attempt < max_retries:
                # Retry on timeout
                await asyncio.sleep(2)
                continue
            else:
                raise TimeoutError(f"Agent {subagent_type} exceeded timeout of {timeout}s after {max_retries} retries")

        except Exception as e:
            if attempt < max_retries:
                # Retry on any other error
                await asyncio.sleep(1)
                continue
            else:
                raise TaskDelegationError(f"Agent {subagent_type} delegation failed: {e}")


async def evaluate_item_with_agent_real(
    item: Dict[str, Any],
    agent_name: str,
    base_dir: Path = None
) -> Dict[str, Any]:
    """
    High-level function to evaluate an item with a specific agent.

    This combines all steps:
    1. Load item content
    2. Load and populate prompt template
    3. Delegate to agent
    4. Return parsed result

    Args:
        item: Item metadata from registry
        agent_name: Expert agent name
        base_dir: Base directory (defaults to irStudy root)

    Returns:
        Evaluation result dictionary

    Raises:
        TaskDelegationError: If evaluation fails
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent

    # Load item content
    item_content = await load_item_content(item["file_path"], base_dir)

    # Load and populate prompt template
    # Try multiple naming conventions
    prompts_dir = base_dir / "evaluation-system" / "config" / "evaluation_prompts"

    # Possible template naming patterns:
    # 1. agent-name_prompt.md (e.g., medication-management-expert_prompt.md)
    # 2. agent_name_prompt.md (e.g., medication_management_expert_prompt.md)
    # 3. agent-name-without-expert_prompt.md (e.g., medication-management_prompt.md)
    # 4. agent_name_without_expert_prompt.md (e.g., medication_management_prompt.md)

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

    # Delegate to agent
    result = await delegate_to_agent(
        subagent_type=agent_name,
        prompt=evaluation_prompt,
        model="sonnet",
        description=f"Evaluate {item['item_id']}"
    )

    return result


# =============================================================================
# INTEGRATION INSTRUCTIONS
# =============================================================================
"""
To integrate with real Task tool delegation:

1. Identify how Task tool is exposed in your environment:
   - Claude Code SDK/API?
   - CLI command?
   - Anthropic API directly?

2. Update the `delegate_to_agent()` function:
   - Replace OPTION 3 (current placeholder) with actual implementation
   - Test with one agent first
   - Verify JSON parsing works

3. Test integration:
   ```python
   # Test script
   import asyncio

   async def test_delegation():
       item = {
           "item_id": "test_mcq_001",
           "item_type": "mcq",
           "specialty": "cardiology",
           "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
           "array_index": 0
       }

       result = await evaluate_item_with_agent_real(
           item=item,
           agent_name="medication-management-expert"
       )

       print(json.dumps(result, indent=2))

   asyncio.run(test_delegation())
   ```

4. Verify output format:
   - Should return dictionary with required fields:
     - agent_name, item_id, evaluation_date
     - overall_score, criteria_scores
     - violations, suggestions, strengths
     - pass_fail, requires_manual_review

5. Update orchestrator:
   - Replace `_simulate_agent_evaluation()` call
   - Use `evaluate_item_with_agent_real()` instead
"""
