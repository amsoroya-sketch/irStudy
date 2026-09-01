"""
OSCE Analysis Script - Identify Image Opportunities

Analyzes all OSCEs in the database to identify which ones would benefit from
educational images and recommends specific image types.

ANALYSIS CRITERIA:
1. Comparison Tables: Multiple entities with distinguishing features (e.g., gastric vs duodenal)
2. Decision Trees: Red flags, diagnostic algorithms, safety-critical decisions
3. Timelines: Temporal patterns (pain timing, disease progression)
4. Flowcharts: Management pathways, procedural steps, treatment algorithms

PRIORITY LEVELS:
- HIGH: Critical diagnostic features or safety-critical content
- MEDIUM: Helpful visual aids that improve understanding
- LOW: Nice-to-have visualizations

WEEK 1-2 DELIVERABLE:
    Analysis of all 226 OSCEs to guide batch image generation (Week 5-6)

USAGE:
    export DATABASE_PASSWORD=your_password
    python scripts/image_generation/analyze_osces_for_images.py

OUTPUT:
    - JSON file: analysis_results.json (complete analysis data)
    - CSV file: osce_image_opportunities.csv (sortable spreadsheet)
    - Summary report: printed to console
"""

import os
import sys
import json
import re
from collections import defaultdict
from typing import Dict, List, Any, Tuple

# Database imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import OSCE
from db.base import get_database_url


def analyze_osce_content(osce: OSCE) -> Dict[str, Any]:
    """
    Analyze single OSCE for image opportunities.

    Args:
        osce: OSCE database model instance

    Returns:
        Analysis results with image recommendations
    """
    opportunities = []
    priority = "LOW"

    # Combine all text content for analysis
    content_parts = [
        osce.patient_instructions or "",
        osce.candidate_instructions or "",
        osce.examiner_instructions or "",
        str(osce.rubric or {}),
        str(osce.key_points or []),
        str(osce.red_flags or []),
    ]
    content = " ".join(content_parts).lower()

    # 1. Check for comparison opportunities (HIGH PRIORITY)
    comparison_patterns = [
        r'(vs\.?|versus|compared to|difference between)',
        r'(gastric.*duodenal|type 1.*type 2|acute.*chronic)',
        r'(left.*right|anterior.*posterior|systolic.*diastolic)',
    ]
    if any(re.search(pattern, content) for pattern in comparison_patterns):
        opportunities.append({
            'type': 'comparison_table',
            'reason': 'Multiple entities with distinguishing features',
            'priority': 'HIGH',
            'example': 'Compare key diagnostic or clinical features side-by-side'
        })
        priority = 'HIGH'

    # 2. Check for red flags (HIGH PRIORITY - safety critical)
    if osce.red_flags or re.search(r'(red flag|urgent|emergency|immediately|critical)', content):
        opportunities.append({
            'type': 'decision_tree',
            'reason': 'Red flags or safety-critical decision points',
            'priority': 'HIGH',
            'example': 'Decision tree for urgent referral criteria'
        })
        priority = 'HIGH'

    # 3. Check for timing/temporal patterns (HIGH PRIORITY - diagnostic)
    timing_patterns = [
        r'(hours? after|minutes? after|immediately after)',
        r'(timing|duration|onset|progression)',
        r'(\d+\s*(hour|minute|day|week|month)s?)',
    ]
    if any(re.search(pattern, content) for pattern in timing_patterns):
        opportunities.append({
            'type': 'timeline',
            'reason': 'Temporal patterns or timing-based distinctions',
            'priority': 'HIGH',
            'example': 'Timeline showing symptom timing after triggering event'
        })
        if priority != 'HIGH':
            priority = 'MEDIUM'

    # 4. Check for management pathways (MEDIUM PRIORITY)
    management_patterns = [
        r'(management|treatment plan|protocol|algorithm)',
        r'(first-line|second-line|step \d+)',
        r'(cessation|start|stop|initiate)',
    ]
    if any(re.search(pattern, content) for pattern in management_patterns):
        opportunities.append({
            'type': 'flowchart',
            'reason': 'Management pathway or treatment algorithm',
            'priority': 'MEDIUM',
            'example': 'Flowchart showing step-by-step management approach'
        })
        if priority == 'LOW':
            priority = 'MEDIUM'

    # 5. Check for procedural steps (MEDIUM PRIORITY)
    if osce.station_type.value in ['physical_examination', 'diagnosis_management']:
        procedural_patterns = [
            r'(step|procedure|technique|method)',
            r'(inspect|palpate|percuss|auscultate)',
            r'(preparation|position|permission|perform|present)',  # Dr. Amir 5 Ps
        ]
        if any(re.search(pattern, content) for pattern in procedural_patterns):
            opportunities.append({
                'type': 'flowchart',
                'reason': 'Procedural steps or systematic examination',
                'priority': 'MEDIUM',
                'example': 'Step-by-step examination or procedure flowchart'
            })

    # 6. Check for differential diagnosis (MEDIUM PRIORITY)
    if re.search(r'(differential|diagnosis|rule out|consider)', content):
        opportunities.append({
            'type': 'comparison_table',
            'reason': 'Differential diagnosis with distinguishing features',
            'priority': 'MEDIUM',
            'example': 'Comparison table of differential diagnoses'
        })

    # 7. Dr. Amir format OSCEs get HIGH priority (comprehensive content)
    if osce.dr_amir_format:
        priority = 'HIGH'
        if not any(opp['type'] == 'flowchart' for opp in opportunities):
            opportunities.append({
                'type': 'flowchart',
                'reason': 'Dr. Amir 5 Ps Framework (comprehensive format)',
                'priority': 'HIGH',
                'example': '5 Ps examination flowchart (Preparation, Position, Permission, Perform, Present)'
            })

    # Calculate estimated effort (time to create images)
    effort = 'LOW'  # Default: simple comparison table or single flowchart
    if len(opportunities) >= 3:
        effort = 'HIGH'  # Multiple complex images
    elif any(opp['type'] in ['decision_tree', 'flowchart'] for opp in opportunities):
        effort = 'MEDIUM'  # Complex visualizations

    return {
        'osce_id': osce.osce_id,
        'station_title': osce.station_title,
        'specialty': osce.specialty.value,
        'station_type': osce.station_type.value,
        'dr_amir_format': osce.dr_amir_format,
        'priority': priority,
        'effort': effort,
        'opportunities': opportunities,
        'recommended_image_count': len(set(opp['type'] for opp in opportunities))
    }


def analyze_all_osces() -> List[Dict[str, Any]]:
    """
    Analyze all OSCEs in database for image opportunities.

    Returns:
        List of analysis results for each OSCE
    """
    # Connect to database
    try:
        engine = create_engine(get_database_url())
        Session = sessionmaker(bind=engine)
        session = Session()
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n💡 Set DATABASE_PASSWORD environment variable:")
        print("   export DATABASE_PASSWORD=your_password")
        sys.exit(1)

    print("📊 OSCE Image Opportunity Analysis")
    print("=" * 70)
    print("Analyzing all OSCEs for educational image opportunities...\n")

    # Query all OSCEs
    osces = session.query(OSCE).all()
    print(f"Found {len(osces)} OSCEs in database\n")

    # Analyze each OSCE
    results = []
    for idx, osce in enumerate(osces, 1):
        if idx % 25 == 0:
            print(f"Analyzed {idx}/{len(osces)} OSCEs...")

        analysis = analyze_osce_content(osce)
        results.append(analysis)

    session.close()

    print(f"✅ Analysis complete: {len(results)} OSCEs analyzed\n")
    return results


def generate_summary_report(results: List[Dict[str, Any]]):
    """
    Generate summary report of analysis results.

    Args:
        results: List of OSCE analysis results
    """
    print("=" * 70)
    print("📈 SUMMARY REPORT")
    print("=" * 70)

    # Priority breakdown
    priority_counts = defaultdict(int)
    for result in results:
        priority_counts[result['priority']] += 1

    print("\n1. Priority Breakdown:")
    print(f"   HIGH Priority:   {priority_counts['HIGH']:3d} OSCEs (critical diagnostic/safety content)")
    print(f"   MEDIUM Priority: {priority_counts['MEDIUM']:3d} OSCEs (helpful visualizations)")
    print(f"   LOW Priority:    {priority_counts['LOW']:3d} OSCEs (nice-to-have)")

    # Effort estimation
    effort_counts = defaultdict(int)
    for result in results:
        effort_counts[result['effort']] += 1

    print("\n2. Estimated Effort:")
    print(f"   HIGH Effort:   {effort_counts['HIGH']:3d} OSCEs (3-5 complex images each)")
    print(f"   MEDIUM Effort: {effort_counts['MEDIUM']:3d} OSCEs (2-3 images each)")
    print(f"   LOW Effort:    {effort_counts['LOW']:3d} OSCEs (1 simple image)")

    # Image type breakdown
    image_type_counts = defaultdict(int)
    for result in results:
        for opp in result['opportunities']:
            image_type_counts[opp['type']] += 1

    print("\n3. Recommended Image Types:")
    print(f"   Comparison Tables: {image_type_counts['comparison_table']:3d} opportunities")
    print(f"   Decision Trees:    {image_type_counts['decision_tree']:3d} opportunities")
    print(f"   Timelines:         {image_type_counts['timeline']:3d} opportunities")
    print(f"   Flowcharts:        {image_type_counts['flowchart']:3d} opportunities")

    # Specialty breakdown
    specialty_priority = defaultdict(lambda: {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0})
    for result in results:
        specialty_priority[result['specialty']][result['priority']] += 1

    print("\n4. Priority by Specialty (HIGH/MEDIUM/LOW):")
    for specialty, counts in sorted(specialty_priority.items()):
        print(f"   {specialty:20s}: {counts['HIGH']:2d} / {counts['MEDIUM']:2d} / {counts['LOW']:2d}")

    # Dr. Amir format OSCEs
    dr_amir_count = sum(1 for r in results if r['dr_amir_format'])
    print(f"\n5. Dr. Amir Enhanced Format:")
    print(f"   {dr_amir_count} OSCEs use Dr. Amir's 5 Ps Framework (auto-HIGH priority)")

    # Top 20 recommendations
    high_priority = [r for r in results if r['priority'] == 'HIGH']
    high_priority_sorted = sorted(high_priority, key=lambda x: (-len(x['opportunities']), x['effort']))

    print(f"\n6. Top 20 High-Priority OSCEs (for Week 5-6 batch generation):")
    for idx, result in enumerate(high_priority_sorted[:20], 1):
        print(f"   {idx:2d}. {result['osce_id']:15s} | {result['station_title'][:40]:40s} | {len(result['opportunities'])} images")

    print("\n" + "=" * 70)
    print("📁 Output Files:")
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "static", "images", "osces"
    )
    print(f"   JSON: {os.path.join(output_dir, 'analysis_results.json')}")
    print(f"   CSV:  {os.path.join(output_dir, 'osce_image_opportunities.csv')}")


def save_results(results: List[Dict[str, Any]]):
    """
    Save analysis results to JSON and CSV files.

    Args:
        results: List of OSCE analysis results
    """
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "static", "images", "osces"
    )
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON
    json_path = os.path.join(output_dir, 'analysis_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Save CSV
    csv_path = os.path.join(output_dir, 'osce_image_opportunities.csv')
    with open(csv_path, 'w', encoding='utf-8') as f:
        # Header
        f.write("OSCE_ID,Station_Title,Specialty,Station_Type,Dr_Amir_Format,Priority,Effort,Image_Count,Image_Types\n")

        # Data rows
        for result in results:
            image_types = ", ".join(sorted(set(opp['type'] for opp in result['opportunities'])))
            f.write(f'"{result["osce_id"]}","{result["station_title"]}","{result["specialty"]}","{result["station_type"]}",')
            f.write(f'"{result["dr_amir_format"]}","{result["priority"]}","{result["effort"]}",')
            f.write(f'"{result["recommended_image_count"]}","{image_types}"\n')

    print(f"\n✅ Results saved to:")
    print(f"   {json_path}")
    print(f"   {csv_path}")


if __name__ == "__main__":
    try:
        # Run analysis
        results = analyze_all_osces()

        # Generate summary report
        generate_summary_report(results)

        # Save results
        save_results(results)

        print("\n✅ SUCCESS: Analysis complete")
        print("\n🔧 Next Steps:")
        print("   1. Review top 20 high-priority OSCEs")
        print("   2. Week 3-4: Create backend API endpoints for enhanced content")
        print("   3. Week 5-6: Batch generate images for top 100 OSCEs")
        print("   4. Week 7-8: Low-effort batch generation for remaining OSCEs")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
