#!/usr/bin/env python3
"""
Generate remaining evaluation prompt templates for all expert agents.
Uses medication_management_prompt.md as base template, customizes per agent.
"""

from pathlib import Path

# Agent configurations
AGENT_CONFIGS = {
    "history-taking-expert": {
        "title": "History Taking Expert",
        "role": "history-taking-expert",
        "experience": "10+ years Australian teaching hospital (Royal North Shore, Alfred)",
        "qualifications": "MBBS, FRACP, Clinical Educator",
        "criteria": {
            "9_step_history": {
                "weight": 40,
                "description": "Complete 9-step systematic history (CC, HPI, PMHx, Meds, Allergies, FHx, SHx, ROS, Functional)"
            },
            "socrates_oldcarts": {
                "weight": 30,
                "description": "SOCRATES for pain / OLDCARTS for general symptoms"
            },
            "australian_terminology": {
                "weight": 20,
                "description": "GP (not PCP), ED (not ER), Australian context"
            },
            "red_flags_identified": {
                "weight": 10,
                "description": "Red flags documented and addressed"
            }
        },
        "critical_checklist": [
            "9-step history complete (all elements present)",
            "SOCRATES/OLDCARTS used appropriately",
            "Red flags identified (chest pain → cardiac red flags)",
            "Australian terminology throughout"
        ]
    },

    "physical-examination-expert": {
        "title": "Physical Examination Expert",
        "role": "physical-examination-expert",
        "experience": "10+ years Australian teaching hospital clinical educator",
        "qualifications": "MBBS, FRACP, Advanced Clinical Examination Certificate",
        "criteria": {
            "systematic_approach": {
                "weight": 40,
                "description": "Systematic examination (e.g., CVS: inspection, palpation, percussion, auscultation)"
            },
            "appropriate_systems": {
                "weight": 30,
                "description": "Relevant systems examined based on presenting complaint"
            },
            "examination_findings": {
                "weight": 20,
                "description": "Findings documented clearly (positive and pertinent negatives)"
            },
            "australian_standards": {
                "weight": 10,
                "description": "AMC Clinical Exam standards followed"
            }
        },
        "critical_checklist": [
            "Systematic approach used (not random examination)",
            "All relevant systems examined",
            "Positive findings AND pertinent negatives documented",
            "AMC Clinical Exam format followed"
        ]
    },

    "pediatric-emergency-expert": {
        "title": "Pediatric Emergency Expert",
        "role": "pediatric-emergency-expert",
        "experience": "10+ years paediatric emergency (Royal Children's Hospital Melbourne, Sydney Children's)",
        "qualifications": "MBBS, FRACP (Paediatrics), APLS Instructor",
        "criteria": {
            "weight_based_dosing": {
                "weight": 40,
                "description": "Weight-based medication dosing (mg/kg) correct"
            },
            "apls_protocols": {
                "weight": 30,
                "description": "APLS resuscitation protocols followed"
            },
            "age_appropriate_assessment": {
                "weight": 20,
                "description": "Assessment appropriate for child's age"
            },
            "australian_standards": {
                "weight": 10,
                "description": "Australian paediatric guidelines (RCH, CHW)"
            }
        },
        "critical_checklist": [
            "Weight-based dosing correct (mg/kg verified)",
            "APLS protocols followed (if resuscitation)",
            "Age-appropriate assessment (infant vs toddler vs child)",
            "Australian guidelines (RCH Clinical Practice Guidelines)"
        ]
    },

    "palliative-care-expert": {
        "title": "Palliative Care Expert",
        "role": "palliative-care-expert",
        "experience": "10+ years palliative medicine (Peter MacCallum, Sacred Heart Hospice)",
        "qualifications": "MBBS, FAChPM (Fellowship Australasian Chapter Palliative Medicine)",
        "criteria": {
            "who_analgesic_ladder": {
                "weight": 35,
                "description": "WHO analgesic ladder followed correctly"
            },
            "opioid_conversions": {
                "weight": 25,
                "description": "Opioid dose conversions accurate (morphine equivalents)"
            },
            "end_of_life_symptoms": {
                "weight": 25,
                "description": "Terminal symptoms managed (dyspnoea, death rattle, agitation)"
            },
            "advance_care_planning": {
                "weight": 15,
                "description": "Goals of care, NFR orders documented appropriately"
            }
        },
        "critical_checklist": [
            "WHO analgesic ladder appropriate for pain severity",
            "Opioid conversions correct (morphine equivalents)",
            "Breakthrough dosing = 1/6 of 24-hour total",
            "NFR order documented (if applicable)"
        ]
    },

    "rural-medicine-expert": {
        "title": "Rural Medicine Expert",
        "role": "rural-medicine-expert",
        "experience": "10+ years rural/remote medicine (NSW Rural Health, RFDS)",
        "qualifications": "MBBS, FACRRM (Fellowship Australian College Rural & Remote Medicine)",
        "criteria": {
            "emergency_stabilization": {
                "weight": 40,
                "description": "ABC stabilization appropriate for rural setting"
            },
            "rfds_activation": {
                "weight": 30,
                "description": "RFDS retrieval criteria applied correctly"
            },
            "telehealth_appropriate": {
                "weight": 20,
                "description": "Telehealth consultation documented if applicable"
            },
            "limited_resources": {
                "weight": 10,
                "description": "Management appropriate for limited resources"
            }
        },
        "critical_checklist": [
            "ABC stabilization prioritized (before retrieval)",
            "RFDS activated appropriately (criteria met)",
            "Telehealth used if available",
            "Management realistic for rural setting (limited imaging/specialists)"
        ]
    },

    "pathology-interpretation-expert": {
        "title": "Pathology Interpretation Expert",
        "role": "pathology-interpretation-expert",
        "experience": "10+ years clinical pathology (ICPMR Westmead, PathWest WA)",
        "qualifications": "MBBS, FRCPA (Fellowship Royal College Pathologists Australasia)",
        "criteria": {
            "australian_reference_ranges": {
                "weight": 40,
                "description": "Australian reference ranges used (g/L for Hb, mmol/L for glucose)"
            },
            "fbc_uec_lft_interpretation": {
                "weight": 30,
                "description": "FBC/UEC/LFT interpreted correctly"
            },
            "pattern_recognition": {
                "weight": 20,
                "description": "Patterns recognized (microcytic anaemia, hepatocellular vs cholestatic)"
            },
            "clinical_correlation": {
                "weight": 10,
                "description": "Results correlated with clinical context"
            }
        },
        "critical_checklist": [
            "Australian units used (g/L, mmol/L, micromol/L)",
            "Reference ranges correct for Australian labs",
            "Patterns recognized (anaemia classified by MCV)",
            "Clinical correlation appropriate"
        ]
    },

    "surgical-skills-expert": {
        "title": "Surgical Skills Expert",
        "role": "surgical-skills-expert",
        "experience": "10+ years general surgery (Royal Prince Alfred, Royal Adelaide)",
        "qualifications": "MBBS, FRACS (Fellowship Royal Australasian College Surgeons)",
        "criteria": {
            "asa_classification": {
                "weight": 30,
                "description": "ASA physical status classified correctly"
            },
            "preop_assessment": {
                "weight": 30,
                "description": "Pre-operative investigations appropriate"
            },
            "postop_complications": {
                "weight": 30,
                "description": "Post-op complications recognized (5 W's: wind, water, wound, walking, wonder drugs)"
            },
            "australian_surgical_standards": {
                "weight": 10,
                "description": "RACS surgical competencies met"
            }
        },
        "critical_checklist": [
            "ASA classification accurate (1-6 scale)",
            "Pre-op investigations justified",
            "Post-op complications identified early (5 W's)",
            "RACS standards followed"
        ]
    },

    "infection-control-expert": {
        "title": "Infection Control Expert",
        "role": "infection-control-expert",
        "experience": "10+ years infectious diseases (Alfred Hospital, Royal North Shore)",
        "qualifications": "MBBS, FRACP (Infectious Diseases), Diploma Hospital Infection Control",
        "criteria": {
            "hand_hygiene_who_5_moments": {
                "weight": 30,
                "description": "WHO 5 Moments for hand hygiene documented"
            },
            "transmission_precautions": {
                "weight": 30,
                "description": "Contact/Droplet/Airborne precautions appropriate"
            },
            "antimicrobial_stewardship": {
                "weight": 30,
                "description": "Antibiotic choice appropriate (narrow-spectrum, de-escalate)"
            },
            "australian_guidelines": {
                "weight": 10,
                "description": "ACSQHC infection control standards met"
            }
        },
        "critical_checklist": [
            "Hand hygiene WHO 5 Moments documented",
            "Transmission precautions correct (MRSA → contact, TB → airborne)",
            "Antimicrobial stewardship followed (narrow-spectrum first)",
            "Australian guidelines (eTG Antibiotic, ACSQHC)"
        ]
    },

    "procedural-skills-expert": {
        "title": "Procedural Skills Expert",
        "role": "procedural-skills-expert",
        "experience": "10+ years anaesthetics/intensive care (Austin Health, Royal Melbourne)",
        "qualifications": "MBBS, FANZCA, CICM",
        "criteria": {
            "procedural_indication": {
                "weight": 30,
                "description": "Indication for procedure appropriate"
            },
            "contraindications_checked": {
                "weight": 25,
                "description": "Contraindications assessed (bleeding, infection, anatomy)"
            },
            "procedural_technique": {
                "weight": 25,
                "description": "Technique described systematically (ANZCA/CICM standards)"
            },
            "complications_recognized": {
                "weight": 20,
                "description": "Complications anticipated and managed"
            }
        },
        "critical_checklist": [
            "Indication documented and appropriate",
            "Contraindications checked (bleeding risk, local infection)",
            "Technique systematic (ANZCA standards)",
            "Complications anticipated (pneumothorax post-CVL)"
        ]
    }
}


def generate_prompt_template(agent_name: str, config: dict) -> str:
    """Generate evaluation prompt template for an agent."""

    criteria_section = ""
    for criterion_name, criterion_config in config["criteria"].items():
        criteria_section += f"""
### {criterion_config["weight"]}% - {criterion_name.replace('_', ' ').title()}
{criterion_config["description"]}

"""

    checklist_section = "\n".join([f"- [ ] {item}" for item in config["critical_checklist"]])

    template = f"""# Evaluation Task: {config["title"]}

## Your Role
You are: **{config["role"]}**
Experience: {config["experience"]}
Qualifications: {config["qualifications"]}

## Item to Evaluate
- **Item ID:** {{{{item_id}}}}
- **Type:** {{{{item_type}}}}
- **Specialty:** {{{{specialty}}}}
- **File Path:** {{{{file_path}}}}

## Content to Review
```json
{{{{item_content}}}}
```

## Evaluation Criteria (Your Domain)

{criteria_section}

## Scoring Rubric

### 10.0 - Perfect
All criteria met excellently, Australian standards throughout, zero issues.

### 9.0-9.9 - Excellent
All criteria met well, minor non-critical omissions only.

### 8.0-8.9 - Good
Criteria mostly met, 1-2 minor issues that don't affect safety.

### 7.0-7.9 - Acceptable (Needs Revision)
Criteria partially met, several minor issues or 1 moderate issue.

### 6.0-6.9 - Poor (Major Revisions Needed)
Criteria inadequately met, multiple moderate issues or 1 major issue.

### 0.0-5.9 - FAIL (AUTO-REJECT)
Critical safety issues, major violations, or non-compliance with Australian standards.

## Required Output Format

```json
{{
  "agent_name": "{config["role"]}",
  "item_id": "{{{{item_id}}}}",
  "evaluation_date": "{{{{current_timestamp}}}}",
  "overall_score": 8.5,
  "criteria_scores": {{
    {', '.join([f'"{k}": 8.5' for k in config["criteria"].keys()])}
  }},
  "violations": [
    {{
      "severity": "warning",
      "category": "category_name",
      "issue": "Description of issue",
      "location": "path.to.issue",
      "suggested_fix": "Specific fix recommendation"
    }}
  ],
  "suggestions": [
    "Optional improvement suggestion 1",
    "Optional improvement suggestion 2"
  ],
  "strengths": [
    "Positive aspect 1",
    "Positive aspect 2"
  ],
  "pass_fail": "PASS",
  "requires_manual_review": false,
  "australian_compliance_verified": true
}}
```

## Critical Checklist (Complete Before Returning)

{checklist_section}
- [ ] Output JSON valid (all required fields present)
- [ ] Violations categorized correctly (critical/warning/suggestion)
- [ ] Suggested fixes are specific and actionable
- [ ] Australian standards verified

---

**Your Mission:** Ensure Australian medical standards compliance in your domain of expertise.
**Time to Evaluate:** ~2-3 minutes per item
"""

    return template


def main():
    """Generate all remaining prompt templates."""
    output_dir = Path(__file__).parent.parent / "config" / "evaluation_prompts"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Generating Evaluation Prompt Templates")
    print("=" * 80)

    for agent_name, config in AGENT_CONFIGS.items():
        output_file = output_dir / f"{agent_name}_prompt.md"

        if output_file.exists():
            print(f"⏭️  Skipping {agent_name} (already exists)")
            continue

        template = generate_prompt_template(agent_name, config)

        with open(output_file, 'w') as f:
            f.write(template)

        print(f"✅ Created {agent_name}_prompt.md ({len(template)} bytes)")

    print()
    print(f"✅ All prompt templates generated in: {output_dir}")
    print(f"📊 Total templates: {len(list(output_dir.glob('*_prompt.md')))}")


if __name__ == "__main__":
    main()
