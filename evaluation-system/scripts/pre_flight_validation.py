#!/usr/bin/env python3
"""
Pre-Flight Validation Script
Comprehensive system check before production evaluation run.

Validates:
- Infrastructure (agents, registry, prompts, templates)
- Services (Vault, Qdrant, Postgres, Redis)
- API key configuration
- Code integrity
- Sample evaluation test

Usage:
    python3 pre_flight_validation.py [--skip-api-test]
"""

import sys
import json
import subprocess
import asyncio
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class ValidationResult:
    def __init__(self):
        self.checks: List[Tuple[str, bool, str]] = []
        self.warnings: List[str] = []

    def add_check(self, name: str, passed: bool, details: str = ""):
        self.checks.append((name, passed, details))

    def add_warning(self, message: str):
        self.warnings.append(message)

    def print_summary(self):
        print("\n" + "=" * 80)
        print(f"{BOLD}PRE-FLIGHT VALIDATION SUMMARY{RESET}")
        print("=" * 80)

        passed = sum(1 for _, p, _ in self.checks if p)
        total = len(self.checks)

        for name, passed_check, details in self.checks:
            icon = f"{GREEN}✅{RESET}" if passed_check else f"{RED}❌{RESET}"
            print(f"{icon} {name}")
            if details:
                print(f"   {details}")

        if self.warnings:
            print(f"\n{YELLOW}WARNINGS:{RESET}")
            for warning in self.warnings:
                print(f"   ⚠️  {warning}")

        print("\n" + "=" * 80)
        if passed == total:
            print(f"{GREEN}{BOLD}✅ ALL CHECKS PASSED ({passed}/{total}){RESET}")
            print(f"{GREEN}System is READY for production evaluation!{RESET}")
            print("=" * 80)
            return True
        else:
            print(f"{RED}{BOLD}❌ {total - passed} CHECK(S) FAILED ({passed}/{total} passed){RESET}")
            print(f"{RED}Fix issues above before proceeding.{RESET}")
            print("=" * 80)
            return False


def check_file_structure(result: ValidationResult) -> None:
    """Check that all required files and directories exist."""
    print(f"\n{BLUE}[1/9] Checking File Structure...{RESET}")

    base_dir = Path(__file__).parent.parent

    required_files = [
        "core/evaluation_orchestrator.py",
        "core/agent_assignment_engine.py",
        "core/claude_task_delegation.py",
        "config/agent_assignment_rules.yaml",
        "data/knowledge_item_registry.json",
        "scripts/inventory_content.py",
        "scripts/setup_vault_api_key.sh",
    ]

    required_dirs = [
        "config/evaluation_prompts",
        "scripts",
        "data",
        "core",
    ]

    # Check files
    missing_files = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)

    if missing_files:
        result.add_check(
            "Required files present",
            False,
            f"Missing: {', '.join(missing_files)}"
        )
    else:
        result.add_check(
            f"Required files present ({len(required_files)} files)",
            True
        )

    # Check directories
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        result.add_check(
            "Required directories present",
            False,
            f"Missing: {', '.join(missing_dirs)}"
        )
    else:
        result.add_check(
            f"Required directories present ({len(required_dirs)} dirs)",
            True
        )


def check_expert_agents(result: ValidationResult) -> None:
    """Check that all 13 expert agents exist."""
    print(f"\n{BLUE}[2/9] Checking Expert Agents...{RESET}")

    base_dir = Path(__file__).parent.parent.parent
    agents_dir = base_dir / ".claude" / "agents"

    expected_agents = [
        "clinical-documentation-expert.md",
        "history-taking-expert.md",
        "physical-examination-expert.md",
        "procedural-skills-expert.md",
        "radiology-interpretation-expert.md",
        "medication-management-expert.md",
        "mental-health-crisis-expert.md",
        "pediatric-emergency-expert.md",
        "palliative-care-expert.md",
        "rural-medicine-expert.md",
        "pathology-interpretation-expert.md",
        "surgical-skills-expert.md",
        "infection-control-expert.md",
    ]

    if not agents_dir.exists():
        result.add_check(
            "Expert agents directory",
            False,
            f"Directory not found: {agents_dir}"
        )
        return

    agent_files = list(agents_dir.glob("*.md"))

    if len(agent_files) < 13:
        result.add_check(
            "Expert agents (13 required)",
            False,
            f"Found only {len(agent_files)} agents"
        )
    else:
        result.add_check(
            f"Expert agents ({len(agent_files)} agents)",
            True
        )

    # Check each expected agent
    missing_agents = []
    for agent in expected_agents:
        if not (agents_dir / agent).exists():
            missing_agents.append(agent)

    if missing_agents:
        result.add_warning(f"Missing agents: {', '.join(missing_agents)}")


def check_evaluation_prompts(result: ValidationResult) -> None:
    """Check that evaluation prompt templates exist."""
    print(f"\n{BLUE}[3/9] Checking Evaluation Prompts...{RESET}")

    base_dir = Path(__file__).parent.parent
    prompts_dir = base_dir / "config" / "evaluation_prompts"

    if not prompts_dir.exists():
        result.add_check(
            "Evaluation prompts directory",
            False,
            f"Directory not found: {prompts_dir}"
        )
        return

    prompt_files = list(prompts_dir.glob("*.md"))

    if len(prompt_files) < 13:
        result.add_check(
            "Evaluation prompt templates (13 required)",
            False,
            f"Found only {len(prompt_files)} templates"
        )
    else:
        result.add_check(
            f"Evaluation prompt templates ({len(prompt_files)} templates)",
            True
        )


def check_knowledge_registry(result: ValidationResult) -> None:
    """Check knowledge item registry integrity."""
    print(f"\n{BLUE}[4/9] Checking Knowledge Registry...{RESET}")

    base_dir = Path(__file__).parent.parent
    registry_path = base_dir / "data" / "knowledge_item_registry.json"

    if not registry_path.exists():
        result.add_check(
            "Knowledge registry file",
            False,
            f"File not found: {registry_path}"
        )
        return

    try:
        with open(registry_path) as f:
            registry = json.load(f)

        total_items = registry.get("statistics", {}).get("total_items", 0)
        pending_items = registry.get("statistics", {}).get("by_status", {}).get("pending", 0)

        result.add_check(
            f"Knowledge registry loaded ({total_items} items)",
            True,
            f"Pending evaluation: {pending_items} items"
        )

        # Check that items have required fields
        items = registry.get("knowledge_items", [])
        if items:
            sample_item = items[0]
            required_fields = ["item_id", "item_type", "file_path", "evaluation_status"]
            missing_fields = [f for f in required_fields if f not in sample_item]

            if missing_fields:
                result.add_warning(f"Registry items missing fields: {', '.join(missing_fields)}")

    except json.JSONDecodeError as e:
        result.add_check(
            "Knowledge registry JSON valid",
            False,
            f"JSON parse error: {e}"
        )
    except Exception as e:
        result.add_check(
            "Knowledge registry",
            False,
            f"Error: {e}"
        )


def check_docker_services(result: ValidationResult) -> None:
    """Check that required Docker services are running."""
    print(f"\n{BLUE}[5/9] Checking Docker Services...{RESET}")

    required_services = {
        "vault": "amc-vault-dev",
        "postgres": "irstudy-postgres",
        "redis": "irstudy-redis",
        "qdrant": "irstudy-qdrant",
    }

    try:
        # Get running containers
        result_docker = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )

        running_containers = result_docker.stdout.strip().split("\n")

        for service_name, container_name in required_services.items():
            if container_name in running_containers:
                result.add_check(
                    f"Docker service: {service_name}",
                    True,
                    f"Container: {container_name}"
                )
            else:
                result.add_check(
                    f"Docker service: {service_name}",
                    False,
                    f"Container '{container_name}' not running"
                )

    except subprocess.CalledProcessError as e:
        result.add_check(
            "Docker services check",
            False,
            f"Docker command failed: {e}"
        )
    except FileNotFoundError:
        result.add_check(
            "Docker services check",
            False,
            "Docker not found in PATH"
        )


def check_vault_status(result: ValidationResult) -> None:
    """Check Vault is unsealed and accessible."""
    print(f"\n{BLUE}[6/9] Checking Vault Status...{RESET}")

    import os
    os.environ.setdefault("VAULT_ADDR", "http://127.0.0.1:8200")

    try:
        # Check Vault status
        result_vault = subprocess.run(
            ["vault", "status"],
            capture_output=True,
            text=True,
            env=os.environ
        )

        # Vault returns exit code 0 if unsealed, 2 if sealed
        if result_vault.returncode == 0:
            # Check for "Sealed" line
            if "Sealed" in result_vault.stdout:
                lines = result_vault.stdout.split("\n")
                sealed_line = [l for l in lines if "Sealed" in l][0]

                if "false" in sealed_line:
                    result.add_check(
                        "Vault status",
                        True,
                        "Unsealed and accessible"
                    )
                else:
                    result.add_check(
                        "Vault status",
                        False,
                        "Vault is sealed"
                    )
            else:
                result.add_check(
                    "Vault status",
                    True,
                    "Running"
                )
        else:
            result.add_check(
                "Vault status",
                False,
                f"Exit code: {result_vault.returncode}"
            )

    except FileNotFoundError:
        result.add_check(
            "Vault status",
            False,
            "vault command not found"
        )
    except Exception as e:
        result.add_check(
            "Vault status",
            False,
            f"Error: {e}"
        )


def check_vault_api_key(result: ValidationResult) -> None:
    """Check that Claude API key is stored in Vault."""
    print(f"\n{BLUE}[7/9] Checking Vault API Key...{RESET}")

    import os
    os.environ.setdefault("VAULT_ADDR", "http://127.0.0.1:8200")
    os.environ.setdefault("VAULT_TOKEN", "dev-only-token-change-in-prod")

    try:
        # Try primary path
        result_primary = subprocess.run(
            ["vault", "kv", "get", "-field=value", "secret/ai-osce/claude-api-key"],
            capture_output=True,
            text=True,
            env=os.environ
        )

        if result_primary.returncode == 0:
            api_key = result_primary.stdout.strip()
            masked_key = api_key[-4:] if len(api_key) >= 4 else "****"
            result.add_check(
                "Claude API key in Vault",
                True,
                f"Key found (***{masked_key})"
            )
        else:
            # Try fallback path
            result_fallback = subprocess.run(
                ["vault", "kv", "get", "-field=api_key", "irStudy/claude"],
                capture_output=True,
                text=True,
                env=os.environ
            )

            if result_fallback.returncode == 0:
                api_key = result_fallback.stdout.strip()
                masked_key = api_key[-4:] if len(api_key) >= 4 else "****"
                result.add_check(
                    "Claude API key in Vault",
                    True,
                    f"Key found at fallback path (***{masked_key})"
                )
            else:
                result.add_check(
                    "Claude API key in Vault",
                    False,
                    "No API key found. Run: ./scripts/setup_vault_api_key.sh YOUR_KEY"
                )

    except Exception as e:
        result.add_check(
            "Claude API key in Vault",
            False,
            f"Error: {e}"
        )


def check_python_dependencies(result: ValidationResult) -> None:
    """Check required Python packages are installed."""
    print(f"\n{BLUE}[8/9] Checking Python Dependencies...{RESET}")

    required_packages = {
        "anthropic": "0.76.0",
        "pyyaml": None,
    }

    try:
        import pkg_resources

        for package, min_version in required_packages.items():
            try:
                installed_version = pkg_resources.get_distribution(package).version

                if min_version and installed_version < min_version:
                    result.add_check(
                        f"Python package: {package}",
                        False,
                        f"Version {installed_version} < {min_version} (required)"
                    )
                else:
                    result.add_check(
                        f"Python package: {package}",
                        True,
                        f"Version {installed_version}"
                    )
            except pkg_resources.DistributionNotFound:
                result.add_check(
                    f"Python package: {package}",
                    False,
                    "Not installed. Run: pip install anthropic pyyaml"
                )

    except Exception as e:
        result.add_check(
            "Python dependencies check",
            False,
            f"Error: {e}"
        )


async def check_sample_evaluation(result: ValidationResult, skip_api_test: bool = False) -> None:
    """Run a sample evaluation to test integration."""
    print(f"\n{BLUE}[9/9] Testing Sample Evaluation...{RESET}")

    if skip_api_test:
        result.add_warning("API test skipped (--skip-api-test flag)")
        result.add_check(
            "Sample evaluation test",
            True,
            "Skipped by user request"
        )
        return

    # Load delegation module
    base_dir = Path(__file__).parent.parent
    delegation_path = base_dir / "core" / "claude_task_delegation.py"

    try:
        spec = importlib.util.spec_from_file_location(
            "delegation",
            str(delegation_path)
        )
        delegation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(delegation)

        # Create test item
        test_item = {
            "item_id": "test_mcq_preflight",
            "item_type": "mcq",
            "specialty": "cardiology",
            "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
            "array_index": 0
        }

        # Evaluate with medication-management-expert
        eval_result = await delegation.evaluate_item_with_agent_real(
            item=test_item,
            agent_name="medication-management-expert"
        )

        # Validate result
        required_fields = [
            "agent_name", "item_id", "evaluation_date",
            "overall_score", "criteria_scores", "violations",
            "suggestions", "strengths", "pass_fail"
        ]

        missing_fields = [f for f in required_fields if f not in eval_result]

        if missing_fields:
            result.add_check(
                "Sample evaluation test",
                False,
                f"Missing fields: {', '.join(missing_fields)}"
            )
        else:
            score = eval_result.get("overall_score", 0)
            status = eval_result.get("pass_fail", "UNKNOWN")

            result.add_check(
                "Sample evaluation test",
                True,
                f"Score: {score}/10.0, Status: {status}"
            )

    except delegation.TaskDelegationError as e:
        result.add_check(
            "Sample evaluation test",
            False,
            f"Delegation error: {e}"
        )
    except delegation.JSONParseError as e:
        result.add_check(
            "Sample evaluation test",
            False,
            f"JSON parse error: {e}"
        )
    except FileNotFoundError as e:
        result.add_check(
            "Sample evaluation test",
            False,
            f"File not found: {e}"
        )
    except Exception as e:
        result.add_check(
            "Sample evaluation test",
            False,
            f"Error: {e}"
        )


async def main():
    """Run all validation checks."""
    skip_api_test = "--skip-api-test" in sys.argv

    print(f"{BOLD}{'=' * 80}{RESET}")
    print(f"{BOLD}EVALUATION SYSTEM - PRE-FLIGHT VALIDATION{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}")

    result = ValidationResult()

    # Run all checks
    check_file_structure(result)
    check_expert_agents(result)
    check_evaluation_prompts(result)
    check_knowledge_registry(result)
    check_docker_services(result)
    check_vault_status(result)
    check_vault_api_key(result)
    check_python_dependencies(result)
    await check_sample_evaluation(result, skip_api_test)

    # Print summary
    all_passed = result.print_summary()

    if all_passed:
        print(f"\n{GREEN}{BOLD}Next steps:{RESET}")
        print(f"  1. Test with 10 items:")
        print(f"     venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py --max-items 10")
        print(f"  2. Run production evaluation:")
        print(f"     venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \\")
        print(f"       --output-dir evaluation-system/reports/production_iteration_1")
        print()
        return 0
    else:
        print(f"\n{RED}{BOLD}Action required:{RESET}")
        print(f"  Fix the failed checks above, then re-run this validation.")
        print()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
