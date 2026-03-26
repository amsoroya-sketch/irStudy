#!/usr/bin/env python3
"""
Agent Assignment Engine for irStudy Medical Content Evaluation System
Automatically assigns expert agents to knowledge items based on content type and specialty.

Usage:
    python3 agent_assignment_engine.py --registry-path data/knowledge_item_registry.json
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any
from datetime import datetime


class AgentAssignmentEngine:
    """
    Assigns expert agents to knowledge items based on:
    - Content type (patient_persona, mcq, osce_script, study_card, clinical_image)
    - Specialty (cardiology, respiratory, psychiatry, etc.)
    - Assignment rules configuration
    """

    def __init__(self, rules_path: Path):
        """Load assignment rules configuration."""
        self.rules_path = rules_path

        with open(rules_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.expert_agents = self.config.get("expert_agents", {})
        self.assignment_rules = self.config.get("assignment_rules", {})
        self.specialty_mapping = self.config.get("specialty_mapping", {})
        self.evaluation_criteria = self.config.get("evaluation_criteria", {})

        print(f"✅ Loaded {len(self.expert_agents)} expert agents")
        print(f"✅ Loaded assignment rules for {len(self.assignment_rules)} content types")

    def normalize_specialty(self, specialty: str) -> str:
        """Normalize specialty name using mapping."""
        specialty_lower = specialty.lower().strip()
        return self.specialty_mapping.get(specialty_lower, specialty_lower)

    def get_primary_agents(self, content_type: str) -> List[str]:
        """Get primary agents for content type."""
        rules = self.assignment_rules.get(content_type, {})
        return rules.get("primary_agents", [])

    def get_secondary_agents(self, content_type: str, specialty: str) -> List[str]:
        """Get secondary agents based on specialty."""
        rules = self.assignment_rules.get(content_type, {})
        secondary_by_specialty = rules.get("secondary_agents_by_specialty", {})

        normalized_specialty = self.normalize_specialty(specialty)
        return secondary_by_specialty.get(normalized_specialty, [])

    def get_minimum_agents(self, content_type: str) -> int:
        """Get minimum number of agents required for content type."""
        rules = self.assignment_rules.get(content_type, {})
        return rules.get("minimum_agents", 1)

    def assign_agents_to_item(self, item: Dict) -> List[str]:
        """
        Assign agents to a single knowledge item.

        Returns:
            List of agent names to assign
        """
        content_type = item.get("item_type")
        specialty = item.get("specialty", "general")

        # Get primary agents (always assigned)
        assigned_agents = self.get_primary_agents(content_type)

        # Get secondary agents based on specialty
        secondary_agents = self.get_secondary_agents(content_type, specialty)
        assigned_agents.extend(secondary_agents)

        # Remove duplicates while preserving order
        seen = set()
        unique_agents = []
        for agent in assigned_agents:
            if agent not in seen:
                seen.add(agent)
                unique_agents.append(agent)

        # Ensure minimum number of agents
        minimum = self.get_minimum_agents(content_type)
        if len(unique_agents) < minimum:
            # Add fallback agents if needed
            fallback_agents = [
                "clinical-documentation-expert",
                "medication-management-expert",
                "physical-examination-expert",
            ]
            for fallback in fallback_agents:
                if fallback not in seen:
                    unique_agents.append(fallback)
                    seen.add(fallback)
                    if len(unique_agents) >= minimum:
                        break

        return unique_agents

    def assign_agents_bulk(self, registry: Dict) -> Dict:
        """
        Bulk assign agents to all knowledge items in registry.

        Args:
            registry: Knowledge item registry dictionary

        Returns:
            Updated registry with agent assignments
        """
        items = registry.get("knowledge_items", [])
        total_items = len(items)

        print(f"\n🔄 Assigning agents to {total_items} knowledge items...")

        # Track statistics
        stats = {
            "total_items": total_items,
            "items_assigned": 0,
            "items_already_evaluated": 0,
            "items_skipped": 0,
            "agents_assigned": {},
            "by_content_type": {},
            "by_specialty": {},
        }

        for idx, item in enumerate(items):
            # Skip already evaluated items
            if item.get("evaluation_status") == "completed":
                stats["items_already_evaluated"] += 1
                continue

            # Assign agents
            try:
                assigned_agents = self.assign_agents_to_item(item)
                item["assigned_agents"] = assigned_agents
                stats["items_assigned"] += 1

                # Update statistics
                content_type = item.get("item_type", "unknown")
                specialty = item.get("specialty", "unknown")

                stats["by_content_type"][content_type] = stats["by_content_type"].get(content_type, 0) + 1
                stats["by_specialty"][specialty] = stats["by_specialty"].get(specialty, 0) + 1

                for agent in assigned_agents:
                    stats["agents_assigned"][agent] = stats["agents_assigned"].get(agent, 0) + 1

            except Exception as e:
                print(f"❌ Error assigning agents to item {item.get('item_id')}: {e}")
                stats["items_skipped"] += 1

            # Progress indicator
            if (idx + 1) % 500 == 0:
                print(f"   Processed {idx + 1}/{total_items} items...")

        # Update registry metadata
        registry["assignment_metadata"] = {
            "assigned_at": datetime.now().isoformat(),
            "rules_version": self.config.get("version", "unknown"),
            "statistics": stats,
        }

        return registry

    def print_assignment_summary(self, registry: Dict):
        """Print summary of agent assignments."""
        metadata = registry.get("assignment_metadata", {})
        stats = metadata.get("statistics", {})

        print("\n" + "=" * 80)
        print("📊 AGENT ASSIGNMENT SUMMARY")
        print("=" * 80)

        print(f"\nTotal Items: {stats.get('total_items', 0)}")
        print(f"  Assigned: {stats.get('items_assigned', 0)}")
        print(f"  Already Evaluated: {stats.get('items_already_evaluated', 0)}")
        print(f"  Skipped (errors): {stats.get('items_skipped', 0)}")

        print(f"\nAgents Assigned:")
        agents_sorted = sorted(
            stats.get("agents_assigned", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )
        for agent, count in agents_sorted:
            print(f"  {agent}: {count} items")

        print(f"\nBy Content Type:")
        for content_type, count in sorted(stats.get("by_content_type", {}).items()):
            print(f"  {content_type}: {count}")

        print(f"\nTop 10 Specialties:")
        specialties_sorted = sorted(
            stats.get("by_specialty", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )
        for specialty, count in specialties_sorted[:10]:
            print(f"  {specialty}: {count}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Assign expert agents to knowledge items")
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path("evaluation-system/data/knowledge_item_registry.json"),
        help="Path to knowledge item registry JSON"
    )
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=Path("evaluation-system/config/agent_assignment_rules.yaml"),
        help="Path to agent assignment rules YAML"
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="Output path (defaults to overwriting registry-path)"
    )
    args = parser.parse_args()

    # Resolve paths
    base_dir = Path(__file__).parent.parent.parent
    registry_path = base_dir / args.registry_path
    rules_path = base_dir / args.rules_path
    output_path = args.output_path if args.output_path else registry_path

    print("=" * 80)
    print("irStudy Agent Assignment Engine")
    print("=" * 80)
    print(f"Registry: {registry_path}")
    print(f"Rules: {rules_path}")
    print(f"Output: {output_path}")

    # Load registry
    print(f"\n📂 Loading registry from: {registry_path}")
    with open(registry_path, 'r') as f:
        registry = json.load(f)

    print(f"✅ Loaded {len(registry.get('knowledge_items', []))} items")

    # Initialize assignment engine
    engine = AgentAssignmentEngine(rules_path)

    # Assign agents
    updated_registry = engine.assign_agents_bulk(registry)

    # Print summary
    engine.print_assignment_summary(updated_registry)

    # Save updated registry
    print(f"\n💾 Saving updated registry to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(updated_registry, f, indent=2)

    print(f"✅ Registry saved ({output_path.stat().st_size / 1024:.2f} KB)")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
