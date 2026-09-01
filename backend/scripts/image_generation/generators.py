"""
OSCE Educational Image Generator

Generates educational images for OSCE scenarios using Python visualization libraries.

SUPPORTED IMAGE TYPES:
1. Comparison Tables: Side-by-side feature comparison (e.g., gastric vs duodenal ulcer)
2. Decision Trees: Flowchart-style decision making (e.g., red flag assessment)
3. Timeline Charts: Temporal relationships (e.g., pain timing after meals)
4. Flowcharts: Process flows (e.g., management pathways)
5. Management Pathways: Complete clinical algorithms

LIBRARIES USED:
- matplotlib: Basic charts, graphs, comparison tables
- seaborn: Statistical visualizations
- graphviz: Flowcharts, decision trees
- Pillow: Image composition, annotations

USAGE:
    from generators import OSCEImageGenerator

    gen = OSCEImageGenerator("GI-PUD-001")

    # Generate comparison table
    img_path = gen.generate_comparison_table(
        title="Gastric vs Duodenal Ulcer",
        comparison_data={
            "Pain Timing": {
                "Gastric Ulcer": "IMMEDIATELY after eating",
                "Duodenal Ulcer": "2-3 HOURS after eating"
            }
        },
        output_name="gastric_duodenal_comparison"
    )

WEEK 1-2 IMPLEMENTATION:
    Phase 1 of 8-week UI enhancement plan
    Part of database foundation for Dr. Amir OSCE content
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import numpy as np
from graphviz import Digraph
from PIL import Image, ImageDraw, ImageFont

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "images", "osces")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Style configuration
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 11

# Color palette (colorblind-friendly)
COLORS = {
    'primary': '#1f77b4',      # Blue
    'secondary': '#ff7f0e',    # Orange
    'success': '#2ca02c',      # Green
    'danger': '#d62728',       # Red
    'warning': '#ff9896',      # Light Red
    'info': '#9467bd',         # Purple
    'light': '#f0f0f0',        # Light Gray
    'dark': '#333333',         # Dark Gray
}


class OSCEImageGenerator:
    """
    Generate educational images for OSCE scenarios.

    DESIGN PRINCIPLES:
    - High contrast for readability
    - Colorblind-friendly palette
    - Professional medical education style
    - 300 DPI for print quality
    - Consistent sizing (14" x 8" for tables, 12" x 10" for flowcharts)
    """

    def __init__(self, osce_id: str):
        """
        Initialize image generator for specific OSCE.

        Args:
            osce_id: Unique OSCE identifier (e.g., "GI-PUD-001")
        """
        self.osce_id = osce_id
        self.output_prefix = os.path.join(OUTPUT_DIR, osce_id)
        self.metadata = []  # Track generated images for database insertion

    def generate_comparison_table(
        self,
        title: str,
        comparison_data: Dict[str, Dict[str, str]],
        output_name: str,
        highlight_critical: Optional[List[str]] = None
    ) -> str:
        """
        Generate comparison table image (e.g., gastric vs duodenal ulcer).

        Args:
            title: Table title
            comparison_data: Nested dict {feature: {column1: value1, column2: value2}}
                Example:
                {
                    "Pain Timing": {
                        "Gastric Ulcer": "IMMEDIATELY after eating",
                        "Duodenal Ulcer": "2-3 HOURS after eating"
                    }
                }
            output_name: Output filename (without extension)
            highlight_critical: List of rows to highlight in red (critical differences)

        Returns:
            Relative path to generated image
        """
        highlight_critical = highlight_critical or []

        # Extract column headers (ulcer types)
        columns = list(next(iter(comparison_data.values())).keys())
        rows = list(comparison_data.keys())

        # Create figure
        fig, ax = plt.subplots(figsize=(14, len(rows) * 0.8 + 2))
        ax.axis('off')

        # Create table data
        table_data = []
        for row_name in rows:
            row_values = [comparison_data[row_name][col] for col in columns]
            table_data.append([row_name] + row_values)

        # Create table
        table = ax.table(
            cellText=table_data,
            colLabels=["Feature"] + columns,
            cellLoc='left',
            loc='center',
            colWidths=[0.3] + [0.35] * len(columns)
        )

        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.5)

        # Color header row
        for i in range(len(columns) + 1):
            cell = table[(0, i)]
            cell.set_facecolor(COLORS['primary'])
            cell.set_text_props(weight='bold', color='white')

        # Highlight critical rows
        for row_idx, row_name in enumerate(rows):
            if row_name in highlight_critical:
                for col_idx in range(len(columns) + 1):
                    cell = table[(row_idx + 1, col_idx)]
                    cell.set_facecolor(COLORS['warning'])
                    if col_idx > 0:  # Make values bold
                        cell.set_text_props(weight='bold')

        # Add title
        plt.title(title, fontsize=16, fontweight='bold', pad=20)

        # Save image
        output_path = f"{self.output_prefix}_{output_name}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        # Track metadata
        rel_path = os.path.relpath(output_path, os.path.join(BASE_DIR, "static"))
        self.metadata.append({
            "title": title,
            "image_url": f"/static/{rel_path}",
            "type": "comparison_table",
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z"
        })

        return rel_path

    def generate_decision_tree(
        self,
        title: str,
        nodes: List[Dict[str, Any]],
        output_name: str
    ) -> str:
        """
        Generate decision tree flowchart (e.g., red flag assessment).

        Args:
            title: Tree title
            nodes: List of node definitions
                Example:
                [
                    {"id": "start", "label": "Patient with Upper Abdominal Pain"},
                    {"id": "q1", "label": "Hematemesis or Melena?", "type": "decision"},
                    {"id": "urgent", "label": "URGENT REFERRAL", "type": "red_flag"},
                    {"id": "continue", "label": "Continue Assessment", "type": "normal"}
                ]
            output_name: Output filename (without extension)

        Returns:
            Relative path to generated image
        """
        # Create directed graph
        dot = Digraph(comment=title)
        dot.attr(rankdir='TB', size='12,10')
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')

        # Add nodes
        for node in nodes:
            node_id = node['id']
            label = node['label']
            node_type = node.get('type', 'normal')

            if node_type == 'red_flag':
                dot.node(node_id, label, fillcolor='#ffcccc', color='#d62728', penwidth='3')
            elif node_type == 'decision':
                dot.node(node_id, label, shape='diamond', fillcolor='#cce5ff', color='#1f77b4')
            elif node_type == 'action':
                dot.node(node_id, label, fillcolor='#ccffcc', color='#2ca02c')
            else:
                dot.node(node_id, label, fillcolor='#f0f0f0', color='#333333')

        # Add edges (inferred from node order with yes/no logic)
        for i in range(len(nodes) - 1):
            if nodes[i].get('type') == 'decision':
                # Decision node - add yes/no branches
                if i + 1 < len(nodes):
                    dot.edge(nodes[i]['id'], nodes[i + 1]['id'], label='Yes', color='red', fontcolor='red')
                if i + 2 < len(nodes):
                    dot.edge(nodes[i]['id'], nodes[i + 2]['id'], label='No', color='green', fontcolor='green')
            else:
                dot.edge(nodes[i]['id'], nodes[i + 1]['id'])

        # Render to file
        output_path = f"{self.output_prefix}_{output_name}"
        dot.render(output_path, format='png', cleanup=True)

        # Track metadata
        final_path = output_path + '.png'
        rel_path = os.path.relpath(final_path, os.path.join(BASE_DIR, "static"))
        self.metadata.append({
            "title": title,
            "image_url": f"/static/{rel_path}",
            "type": "decision_tree",
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z"
        })

        return rel_path

    def generate_timeline(
        self,
        title: str,
        events: List[Dict[str, Any]],
        output_name: str
    ) -> str:
        """
        Generate timeline chart (e.g., pain timing after meals).

        Args:
            title: Timeline title
            events: List of timed events
                Example:
                [
                    {"time": 0, "label": "Meal", "color": "blue"},
                    {"time": 0.5, "label": "Gastric Ulcer Pain", "color": "red"},
                    {"time": 2.5, "label": "Duodenal Ulcer Pain", "color": "orange"}
                ]
            output_name: Output filename (without extension)

        Returns:
            Relative path to generated image
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # Draw timeline axis
        ax.axhline(y=0, color='black', linewidth=2)

        # Plot events
        for event in events:
            time = event['time']
            label = event['label']
            color = event.get('color', 'blue')

            # Draw vertical line
            ax.plot([time, time], [0, 1], color=color, linewidth=2, marker='o', markersize=10)

            # Add label
            ax.text(time, 1.2, label, ha='center', va='bottom', fontsize=11,
                   fontweight='bold', color=color)

        # Configure axes
        ax.set_xlim(-0.5, max([e['time'] for e in events]) + 0.5)
        ax.set_ylim(-0.5, 2)
        ax.set_xlabel('Time After Meal (hours)', fontsize=12, fontweight='bold')
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Add title
        plt.title(title, fontsize=16, fontweight='bold', pad=20)

        # Save image
        output_path = f"{self.output_prefix}_{output_name}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        # Track metadata
        rel_path = os.path.relpath(output_path, os.path.join(BASE_DIR, "static"))
        self.metadata.append({
            "title": title,
            "image_url": f"/static/{rel_path}",
            "type": "timeline",
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z"
        })

        return rel_path

    def generate_flowchart(
        self,
        title: str,
        steps: List[Dict[str, Any]],
        output_name: str
    ) -> str:
        """
        Generate process flowchart (e.g., NSAID cessation pathway).

        Args:
            title: Flowchart title
            steps: List of process steps
                Example:
                [
                    {"id": "step1", "label": "Confirm NSAID use", "type": "process"},
                    {"id": "step2", "label": "Stop NSAID immediately", "type": "action"},
                    {"id": "step3", "label": "Start PPI", "type": "action"}
                ]
            output_name: Output filename (without extension)

        Returns:
            Relative path to generated image
        """
        # Create directed graph
        dot = Digraph(comment=title)
        dot.attr(rankdir='TB', size='10,12')
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='11')

        # Add nodes
        for step in steps:
            step_id = step['id']
            label = step['label']
            step_type = step.get('type', 'process')

            if step_type == 'action':
                dot.node(step_id, label, fillcolor='#ccffcc', color='#2ca02c', penwidth='2')
            elif step_type == 'critical':
                dot.node(step_id, label, fillcolor='#ffcccc', color='#d62728', penwidth='3')
            else:
                dot.node(step_id, label, fillcolor='#cce5ff', color='#1f77b4', penwidth='2')

        # Add edges
        for i in range(len(steps) - 1):
            dot.edge(steps[i]['id'], steps[i + 1]['id'], penwidth='2')

        # Render to file
        output_path = f"{self.output_prefix}_{output_name}"
        dot.render(output_path, format='png', cleanup=True)

        # Track metadata
        final_path = output_path + '.png'
        rel_path = os.path.relpath(final_path, os.path.join(BASE_DIR, "static"))
        self.metadata.append({
            "title": title,
            "image_url": f"/static/{rel_path}",
            "type": "flowchart",
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z"
        })

        return rel_path

    def get_metadata_json(self) -> Dict[str, List[Dict]]:
        """
        Get metadata JSON for database insertion.

        Returns organized metadata by image type for educational_images JSONB column.

        Example return:
        {
            "comparison_charts": [{...}],
            "decision_trees": [{...}],
            "timelines": [{...}],
            "flowcharts": [{...}]
        }
        """
        organized = {
            "comparison_charts": [],
            "decision_trees": [],
            "timelines": [],
            "flowcharts": []
        }

        for img in self.metadata:
            img_type = img['type']
            if img_type == 'comparison_table':
                organized['comparison_charts'].append(img)
            elif img_type == 'decision_tree':
                organized['decision_trees'].append(img)
            elif img_type == 'timeline':
                organized['timelines'].append(img)
            elif img_type == 'flowchart':
                organized['flowcharts'].append(img)

        return organized


def save_metadata_to_file(generator: OSCEImageGenerator, output_path: str):
    """
    Save image metadata to JSON file for database insertion.

    Args:
        generator: OSCEImageGenerator instance with generated images
        output_path: Path to save JSON metadata file
    """
    metadata = generator.get_metadata_json()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Metadata saved to {output_path}")
    print(f"   Images generated: {sum(len(v) for v in metadata.values())}")
    print(f"   Ready for database insertion: UPDATE osces SET educational_images = '{json.dumps(metadata)}'::jsonb WHERE osce_id = '{generator.osce_id}';")


if __name__ == "__main__":
    # Test the generator
    print("🎨 OSCE Image Generator - Test Mode")
    print("=" * 60)

    gen = OSCEImageGenerator("TEST-001")

    # Test comparison table
    print("\n1. Testing comparison table generation...")
    gen.generate_comparison_table(
        title="Test Comparison: Feature A vs Feature B",
        comparison_data={
            "Characteristic 1": {"Feature A": "Value A1", "Feature B": "Value B1"},
            "Characteristic 2": {"Feature A": "Value A2", "Feature B": "Value B2"}
        },
        output_name="test_comparison"
    )
    print("   ✅ Comparison table generated")

    # Test decision tree
    print("\n2. Testing decision tree generation...")
    gen.generate_decision_tree(
        title="Test Decision Tree",
        nodes=[
            {"id": "start", "label": "Start"},
            {"id": "q1", "label": "Question?", "type": "decision"},
            {"id": "yes", "label": "Yes Path", "type": "action"},
            {"id": "no", "label": "No Path", "type": "normal"}
        ],
        output_name="test_decision_tree"
    )
    print("   ✅ Decision tree generated")

    # Test timeline
    print("\n3. Testing timeline generation...")
    gen.generate_timeline(
        title="Test Timeline",
        events=[
            {"time": 0, "label": "Event 1", "color": "blue"},
            {"time": 1, "label": "Event 2", "color": "green"},
            {"time": 2, "label": "Event 3", "color": "red"}
        ],
        output_name="test_timeline"
    )
    print("   ✅ Timeline generated")

    # Test flowchart
    print("\n4. Testing flowchart generation...")
    gen.generate_flowchart(
        title="Test Flowchart",
        steps=[
            {"id": "step1", "label": "Step 1", "type": "process"},
            {"id": "step2", "label": "Step 2", "type": "action"},
            {"id": "step3", "label": "Step 3", "type": "critical"}
        ],
        output_name="test_flowchart"
    )
    print("   ✅ Flowchart generated")

    # Save metadata
    print("\n5. Saving metadata...")
    save_metadata_to_file(gen, os.path.join(OUTPUT_DIR, "TEST-001_metadata.json"))

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print(f"   Output directory: {OUTPUT_DIR}")
