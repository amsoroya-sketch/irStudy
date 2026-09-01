"""
Generate 5 Educational Images for GI-PUD-001 OSCE

GI-PUD-001: Peptic Ulcer Disease - Dr. Amir Enhanced OSCE
This script generates 5 educational images that enhance understanding of:
- Gastric vs Duodenal ulcer differences (critical for diagnosis)
- Red flag assessment (critical for safety)
- Pain timing patterns (key diagnostic feature)
- NSAID cessation pathway (management)
- Complete management algorithm (comprehensive care)

WEEK 1-2 DELIVERABLE:
    Gold standard example for image generation system
    Will be used as template for batch generation (Week 5-6)

USAGE:
    python scripts/image_generation/gi_pud_001_images.py
"""

import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators import OSCEImageGenerator, save_metadata_to_file


def generate_gi_pud_001_images():
    """
    Generate all 5 educational images for GI-PUD-001.

    IMAGES:
    1. Gastric vs Duodenal Ulcer: Comparison table of critical differences
    2. Red Flag Assessment: Decision tree for urgent referral
    3. Pain Timing: Timeline chart showing meal-pain relationship
    4. NSAID Cessation: Flowchart for stopping NSAIDs safely
    5. Management Pathway: Complete algorithm from diagnosis to follow-up
    """
    print("🎨 GI-PUD-001 Educational Image Generator")
    print("=" * 70)
    print("Target: Peptic Ulcer Disease OSCE (Dr. Amir Enhanced Format)")
    print("Output: 5 educational images for enhanced learning\n")

    # Initialize generator
    gen = OSCEImageGenerator("GI-PUD-001")

    # ========================================================================
    # IMAGE 1: Gastric vs Duodenal Ulcer Comparison Table
    # ========================================================================
    print("1. Generating Gastric vs Duodenal Ulcer Comparison Table...")

    comparison_data = {
        "Pain Timing After Eating": {
            "Gastric Ulcer": "IMMEDIATELY after eating (worsens with food)",
            "Duodenal Ulcer": "2-3 HOURS after eating (relieved by food)"
        },
        "Pain Relief": {
            "Gastric Ulcer": "Worsened by eating",
            "Duodenal Ulcer": "Relieved by eating or antacids"
        },
        "Night Pain": {
            "Gastric Ulcer": "Less common",
            "Duodenal Ulcer": "Common (2-3am when stomach empty)"
        },
        "Malignancy Risk": {
            "Gastric Ulcer": "CAN become malignant (biopsy required)",
            "Duodenal Ulcer": "Does NOT become malignant"
        },
        "Age Group": {
            "Gastric Ulcer": "Older patients (>50 years)",
            "Duodenal Ulcer": "Younger patients (30-50 years)"
        },
        "H. pylori Association": {
            "Gastric Ulcer": "70-80% associated",
            "Duodenal Ulcer": "90-95% associated (stronger link)"
        },
        "Location": {
            "Gastric Ulcer": "Lesser curvature of stomach",
            "Duodenal Ulcer": "First part of duodenum (D1)"
        }
    }

    gen.generate_comparison_table(
        title="Gastric vs Duodenal Ulcer: Critical Differences for Diagnosis",
        comparison_data=comparison_data,
        output_name="gastric_duodenal_comparison",
        highlight_critical=["Pain Timing After Eating", "Malignancy Risk"]
    )
    print("   ✅ Comparison table generated (highlights critical diagnostic features)\n")

    # ========================================================================
    # IMAGE 2: Red Flag Assessment Decision Tree
    # ========================================================================
    print("2. Generating Red Flag Assessment Decision Tree...")

    red_flag_nodes = [
        {"id": "start", "label": "Patient with Upper Abdominal Pain", "type": "normal"},
        {"id": "q1", "label": "Hematemesis (vomiting blood) or\nMelena (black, tarry stools)?", "type": "decision"},
        {"id": "urgent_gi_bleed", "label": "URGENT REFERRAL\nGI Bleeding", "type": "red_flag"},
        {"id": "q2", "label": "Age > 55 with new onset dyspepsia?", "type": "decision"},
        {"id": "urgent_malignancy", "label": "URGENT REFERRAL\nRule out gastric cancer", "type": "red_flag"},
        {"id": "q3", "label": "Unexplained weight loss (>5kg/3 months)\nor persistent vomiting?", "type": "decision"},
        {"id": "urgent_other", "label": "URGENT REFERRAL\nFurther investigation", "type": "red_flag"},
        {"id": "continue", "label": "Continue Standard Assessment\nH. pylori testing, PPI trial", "type": "action"}
    ]

    gen.generate_decision_tree(
        title="Red Flag Assessment in Peptic Ulcer Disease",
        nodes=red_flag_nodes,
        output_name="red_flag_decision_tree"
    )
    print("   ✅ Decision tree generated (safety-critical pathways)\n")

    # ========================================================================
    # IMAGE 3: Pain Timing Timeline
    # ========================================================================
    print("3. Generating Pain Timing Timeline...")

    timeline_events = [
        {"time": 0, "label": "MEAL", "color": "#333333"},
        {"time": 0.25, "label": "Gastric Ulcer Pain\n(IMMEDIATELY)", "color": "#d62728"},
        {"time": 2.5, "label": "Duodenal Ulcer Pain\n(2-3 HOURS)", "color": "#ff7f0e"},
        {"time": 5, "label": "Duodenal Pain Relief\n(Next meal)", "color": "#2ca02c"}
    ]

    gen.generate_timeline(
        title="Pain Timing After Meals: Key Diagnostic Distinction",
        events=timeline_events,
        output_name="pain_timing_timeline"
    )
    print("   ✅ Timeline generated (diagnostic timing patterns)\n")

    # ========================================================================
    # IMAGE 4: NSAID Cessation Flowchart
    # ========================================================================
    print("4. Generating NSAID Cessation Flowchart...")

    nsaid_steps = [
        {"id": "step1", "label": "Identify NSAID use\n(aspirin, ibuprofen, diclofenac)", "type": "process"},
        {"id": "step2", "label": "STOP NSAID immediately\n(discuss with prescribing doctor)", "type": "critical"},
        {"id": "step3", "label": "Start Proton Pump Inhibitor (PPI)\nOmeprazole 40mg once daily", "type": "action"},
        {"id": "step4", "label": "Review cardiovascular risk\nIf aspirin for cardio protection", "type": "process"},
        {"id": "step5", "label": "Consider alternative analgesia\nParacetamol (avoid NSAIDs)", "type": "action"},
        {"id": "step6", "label": "H. pylori eradication if positive\nTriple therapy for 7-14 days", "type": "action"},
        {"id": "step7", "label": "Review in 4-8 weeks\nEnsure symptom resolution", "type": "process"}
    ]

    gen.generate_flowchart(
        title="NSAID-Induced Peptic Ulcer: Cessation & Management Pathway",
        steps=nsaid_steps,
        output_name="nsaid_cessation_flowchart"
    )
    print("   ✅ Flowchart generated (management protocol)\n")

    # ========================================================================
    # IMAGE 5: Complete Management Pathway
    # ========================================================================
    print("5. Generating Complete Management Pathway...")

    management_steps = [
        {"id": "step1", "label": "Diagnosis: Upper abdominal pain\n+ characteristic timing", "type": "process"},
        {"id": "step2", "label": "RED FLAG SCREENING\n(age >55, bleeding, weight loss)", "type": "critical"},
        {"id": "step3", "label": "H. pylori testing\n(breath test, stool antigen, serology)", "type": "action"},
        {"id": "step4", "label": "Start PPI therapy\nOmeprazole 40mg once daily", "type": "action"},
        {"id": "step5", "label": "Stop NSAIDs + alcohol\nSmall, frequent meals", "type": "action"},
        {"id": "step6", "label": "H. pylori positive?\nTriple therapy x 7-14 days", "type": "action"},
        {"id": "step7", "label": "Consider endoscopy if:\n- No response to treatment\n- Recurrent symptoms\n- Age >55", "type": "process"},
        {"id": "step8", "label": "Follow-up 4-8 weeks\nConfirm H. pylori eradication", "type": "process"},
        {"id": "step9", "label": "Long-term PPI if:\n- High risk (elderly, comorbidities)\n- H. pylori negative\n- Recurrent ulcers", "type": "process"}
    ]

    gen.generate_flowchart(
        title="Peptic Ulcer Disease: Complete Management Algorithm",
        steps=management_steps,
        output_name="complete_management_pathway"
    )
    print("   ✅ Management pathway generated (comprehensive algorithm)\n")

    # ========================================================================
    # Save metadata for database insertion
    # ========================================================================
    print("=" * 70)
    print("✅ All 5 educational images generated successfully!\n")

    metadata = gen.get_metadata_json()
    metadata_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "static", "images", "osces", "GI-PUD-001_metadata.json"
    )

    save_metadata_to_file(gen, metadata_path)

    print("\n📊 Generation Summary:")
    print(f"   Total images: {sum(len(v) for v in metadata.values())}")
    print(f"   - Comparison tables: {len(metadata['comparison_charts'])}")
    print(f"   - Decision trees: {len(metadata['decision_trees'])}")
    print(f"   - Timelines: {len(metadata['timelines'])}")
    print(f"   - Flowcharts: {len(metadata['flowcharts'])}")

    print("\n📁 Output location:")
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "static", "images", "osces"
    )
    print(f"   {output_dir}")

    print("\n🔧 Next steps:")
    print("   1. Review generated images for quality")
    print("   2. Update database: Run the SQL command from metadata output")
    print("   3. Test display in OSCEDetailEnhanced React component")
    print("   4. Use as template for batch generation (Week 5-6)")

    return metadata


if __name__ == "__main__":
    try:
        metadata = generate_gi_pud_001_images()
        print("\n✅ SUCCESS: GI-PUD-001 images ready for database insertion")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
