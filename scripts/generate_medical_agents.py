#!/usr/bin/env python3
"""
Medical Expert Agent Generator
Generates MED-003 through MED-010 using template pattern

Usage:
    python generate_medical_agents.py
"""

AGENT_SPECIFICATIONS = {
    "MED-003": {
        "specialty": "Gastroenterology",
        "name": "Gastroenterology & Hepatology Expert",
        "topics": [
            "Upper GI bleeding (UGIB)",
            "Lower GI bleeding (LGIB)",
            "Inflammatory bowel disease (IBD - Crohn's, UC)",
            "GORD and peptic ulcer disease",
            "Acute abdomen and surgical emergencies",
            "Hepatitis (A, B, C)",
            "Cirrhosis and chronic liver disease",
            "Coeliac disease",
            "Pancreatitis (acute and chronic)",
            "Colorectal cancer screening"
        ],
        "tools": [
            ("glasgow_blatchford_score", "Calculate Glasgow-Blatchford score for UGIB"),
            ("rockall_score", "Calculate Rockall score for UGIB risk"),
            ("assess_abdominal_pain", "Systematic abdominal pain assessment"),
            ("assess_gi_bleeding", "GI bleeding assessment and management")
        ],
        "etg_section": "4.x",
        "key_guidelines": [
            "Therapeutic Guidelines: Gastrointestinal",
            "Gastroenterological Society of Australia (GESA) guidelines",
            "Crohn's and Colitis Australia guidelines"
        ]
    },
    "MED-004": {
        "specialty": "Endocrinology",
        "name": "Endocrinology & Metabolism Expert",
        "topics": [
            "Type 1 diabetes",
            "Type 2 diabetes",
            "Diabetic ketoacidosis (DKA)",
            "Hyperosmolar hyperglycaemic state (HHS)",
            "Hypoglycaemia",
            "Thyroid function test interpretation",
            "Hyperthyroidism and thyrotoxicosis",
            "Hypothyroidism",
            "Osteoporosis screening and management",
            "Lipid management and familial hypercholesterolaemia"
        ],
        "tools": [
            ("interpret_hba1c", "Interpret HbA1c results"),
            ("interpret_thyroid_function", "Interpret TFTs (TSH, fT4, fT3)"),
            ("calculate_lipid_targets", "Calculate lipid targets for cardiovascular risk"),
            ("diabetes_stepwise_management", "Diabetes stepwise management per eTG")
        ],
        "etg_section": "6.x",
        "key_guidelines": [
            "Therapeutic Guidelines: Endocrinology & Diabetes",
            "Australian Diabetes Society guidelines",
            "PBS restrictions for diabetes medications (SGLT2i, GLP-1 RA)"
        ]
    },
    "MED-005": {
        "specialty": "Neurology",
        "name": "Neurology Expert",
        "topics": [
            "Stroke (ischaemic and haemorrhagic)",
            "Transient ischaemic attack (TIA)",
            "Seizure and epilepsy",
            "Headache (migraine, tension, cluster)",
            "Headache red flags (SAH, meningitis, temporal arteritis)",
            "Multiple sclerosis",
            "Parkinson's disease",
            "Peripheral neuropathy",
            "Guillain-Barré syndrome",
            "Neurological examination"
        ],
        "tools": [
            ("assess_stroke", "Acute stroke assessment and management"),
            ("calculate_nihss", "Calculate NIH Stroke Scale"),
            ("assess_headache", "Systematic headache assessment with red flags"),
            ("classify_seizure", "Seizure classification and management")
        ],
        "etg_section": "7.x",
        "key_guidelines": [
            "Therapeutic Guidelines: Neurology",
            "Australian Stroke Foundation guidelines",
            "Epilepsy Society of Australia guidelines"
        ]
    },
    "MED-006": {
        "specialty": "Emergency",
        "name": "Emergency Medicine Expert",
        "topics": [
            "Trauma assessment (ATLS primary and secondary survey)",
            "Anaphylaxis management",
            "Sepsis and septic shock",
            "DKA and HHS acute management",
            "Toxicology (paracetamol, salicylate, opioid overdose)",
            "Resuscitation (ACLS)",
            "Acute abdominal emergencies",
            "Head injury and GCS",
            "Shock (cardiogenic, hypovolaemic, distributive)",
            "Emergency procedures"
        ],
        "tools": [
            ("atls_primary_survey", "ATLS primary survey (ABCDE)"),
            ("anaphylaxis_management", "Anaphylaxis protocol with adrenaline dosing"),
            ("sepsis_screening", "Sepsis screening (qSOFA, SIRS)"),
            ("calculate_gcs", "Calculate Glasgow Coma Scale")
        ],
        "etg_section": "8.x",
        "key_guidelines": [
            "Therapeutic Guidelines: Emergency",
            "NSW Health Emergency Protocols",
            "ATLS guidelines"
        ]
    },
    "MED-007": {
        "specialty": "ObGyn",
        "name": "Obstetrics & Gynaecology Expert",
        "topics": [
            "Antenatal screening (Australian schedule)",
            "Antenatal bleeding (first, second, third trimester)",
            "Pre-eclampsia and eclampsia",
            "Gestational diabetes",
            "Labour and delivery management",
            "Postpartum haemorrhage",
            "Contraception counselling",
            "Menopause management",
            "Polycystic ovary syndrome (PCOS)",
            "Cervical cancer screening"
        ],
        "tools": [
            ("antenatal_screening_schedule", "Australian antenatal screening schedule"),
            ("assess_antenatal_bleeding", "Antenatal bleeding assessment by trimester"),
            ("contraception_counselling", "Contraception options and counselling"),
            ("assess_pv_bleeding", "PV bleeding assessment (gynaecological)")
        ],
        "etg_section": "9.x",
        "key_guidelines": [
            "Therapeutic Guidelines: Women's Health",
            "RANZCOG guidelines",
            "Australian Immunisation Handbook (pregnancy)"
        ]
    },
    "MED-008": {
        "specialty": "Paediatrics",
        "name": "Paediatrics Expert",
        "topics": [
            "Developmental milestones (0-5 years)",
            "Immunisation schedule (Australian)",
            "Paediatric drug dosing (weight-based)",
            "Fever without source",
            "Febrile seizure",
            "Bronchiolitis",
            "Croup",
            "Asthma in children",
            "Failure to thrive",
            "Child protection concerns"
        ],
        "tools": [
            ("assess_developmental_milestones", "Developmental milestone assessment"),
            ("paediatric_drug_dosing", "Weight-based drug dosing calculator"),
            ("immunisation_schedule", "Australian Immunisation Handbook schedule"),
            ("assess_fever_child", "Fever without source assessment in children")
        ],
        "etg_section": "10.x",
        "key_guidelines": [
            "Therapeutic Guidelines: Paediatric",
            "Australian Immunisation Handbook",
            "RACGP Red Book (well-child checks)"
        ]
    },
    "MED-009": {
        "specialty": "Psychiatry",
        "name": "Psychiatry & Mental Health Expert",
        "topics": [
            "Mental state examination (MSE)",
            "Depression (major depressive disorder)",
            "Anxiety disorders (GAD, panic, social anxiety)",
            "Psychosis and schizophrenia",
            "Bipolar disorder",
            "Suicide risk assessment",
            "Mental Health Act (NSW) - involuntary treatment",
            "Substance use disorders",
            "PTSD",
            "Personality disorders"
        ],
        "tools": [
            ("mental_state_examination", "Structured MSE framework"),
            ("suicide_risk_assessment", "Suicide risk assessment (SAD PERSONS)"),
            ("depression_management", "Depression stepwise management per eTG"),
            ("assess_capacity", "Mental capacity assessment")
        ],
        "etg_section": "11.x",
        "key_guidelines": [
            "Therapeutic Guidelines: Psychiatry",
            "RANZCP clinical practice guidelines",
            "Mental Health Act (NSW)"
        ]
    },
    "MED-010": {
        "specialty": "GeneralPractice",
        "name": "General Practice / Family Medicine Expert",
        "topics": [
            "Preventive health screening (RACGP Red Book)",
            "Chronic disease management (care plans, TCAs)",
            "Common presentations (URTI, UTI, back pain)",
            "Health assessment (45-49 years, 75+ years)",
            "Cardiovascular risk assessment",
            "Cancer screening (breast, cervical, colorectal)",
            "Immunisation (adult)",
            "Medicare items (GP Management Plan, Team Care Arrangement)",
            "Geriatric assessment",
            "Travel medicine"
        ],
        "tools": [
            ("preventive_health_checklist", "RACGP Red Book screening checklist"),
            ("chronic_disease_care_plan", "GP Management Plan and Team Care Arrangement"),
            ("cardiovascular_risk_assessment", "Framingham/Australian CVD risk calculator"),
            ("cancer_screening_guidelines", "Australian cancer screening recommendations")
        ],
        "etg_section": "12.x",
        "key_guidelines": [
            "RACGP Red Book (10th edition)",
            "Murtagh's General Practice (8th ed)",
            "PBS Schedule (primary care medications)"
        ]
    }
}


def generate_agent_file(agent_id: str, spec: dict) -> str:
    """Generate Python code for a medical expert agent"""

    specialty = spec["specialty"]
    name = spec["name"]
    topics = spec["topics"]
    tools = spec["tools"]
    etg_section = spec["etg_section"]
    guidelines = spec["key_guidelines"]

    # Generate tools registration
    tools_registration = "\n        ".join([
        f'self.register_tool("{tool_name}", self._{tool_name}, "{tool_desc}")'
        for tool_name, tool_desc in tools
    ])

    # Generate tool method stubs
    tool_methods = "\n\n    ".join([
        f'''def _{tool_name}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        {tool_desc}

        Implementation pending - integrate with RAG system
        """
        self.logger.info(f"Executing {tool_name}...")
        return {{"status": "success", "message": "Tool implementation pending"}}'''
        for tool_name, tool_desc in tools
    ])

    code = f'''#!/usr/bin/env python3
"""
{agent_id}: {name}
{specialty} specialist for AMC exam preparation

Generated by: scripts/generate_medical_agents.py
"""

from typing import Dict, List, Any
from src.agents.medical.base_medical_expert import BaseMedicalExpert
from src.agents.base_agent import AgentMetadata, AgentRole


class {specialty}Expert(BaseMedicalExpert):
    """
    {agent_id}: {name}

    Australian guideline compliance:
    - Therapeutic Guidelines: {specialty} (eTG Section {etg_section})
    - {guidelines[0] if guidelines else 'Specialist guidelines'}
    """

    def __init__(self, rag_system=None):
        """Initialize {specialty} Expert Agent"""
        metadata = AgentMetadata(
            agent_id="{agent_id}",
            name="{name}",
            role=AgentRole.MEDICAL_EXPERT,
            experience_years=15,
            technologies={guidelines},
            specializations={[t.split(' (')[0] for t in topics[:5]]},
            pros=[
                "Expert in Australian {specialty.lower()} guidelines",
                "15+ years clinical experience",
                "AMC Clinical Exam preparation specialist",
                "Evidence-graded recommendations (GRADE system)"
            ],
            cons=[
                "Limited to {specialty.lower()} domain",
                "Requires validation for complex cases"
            ],
            max_concurrent_tasks=5,
            quality_gate_required=True,
            version="2.0.0"
        )

        super().__init__(metadata, rag_system)
        self._register_{specialty.lower()}_tools()

    def _get_specialty_sources(self) -> List[str]:
        """Return primary sources for {specialty.lower()}"""
        return {guidelines}

    def _get_specialty_topics(self) -> List[str]:
        """Return high-yield {specialty.lower()} topics for AMC"""
        return {topics}

    def _register_{specialty.lower()}_tools(self):
        """Register {specialty.lower()}-specific tools"""
        {tools_registration}

    {tool_methods}


def main():
    """Test the {specialty} Expert Agent"""
    print("="*80)
    print("{agent_id}: {name} Test")
    print("="*80)

    agent = {specialty}Expert()
    print(f"Agent ID: {{agent.metadata.agent_id}}")
    print(f"Specializations: {{', '.join(agent.metadata.specializations)}}")
    print("✅ Agent initialized successfully")


if __name__ == "__main__":
    main()
'''

    return code


def main():
    """Generate all remaining medical expert agents"""
    import os

    output_dir = "/home/dev/Development/irStudy/src/agents/medical"

    print("="*80)
    print("Medical Expert Agent Generator")
    print("="*80)
    print()

    for agent_id, spec in AGENT_SPECIFICATIONS.items():
        specialty = spec["specialty"]
        filename = f"med_{agent_id.split('-')[1]}_{specialty.lower()}.py"
        filepath = os.path.join(output_dir, filename)

        print(f"Generating {agent_id}: {spec['name']}...")

        code = generate_agent_file(agent_id, spec)

        with open(filepath, 'w') as f:
            f.write(code)

        print(f"  ✅ Created: {filename}")
        print(f"  📝 Topics: {len(spec['topics'])}")
        print(f"  🔧 Tools: {len(spec['tools'])}")
        print()

    print("="*80)
    print("✅ All agents generated successfully!")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Review generated agents in src/agents/medical/")
    print("2. Implement tool methods (integrate with RAG system)")
    print("3. Add unit tests")
    print("4. Generate MCQs and OSCE scenarios")


if __name__ == "__main__":
    main()
