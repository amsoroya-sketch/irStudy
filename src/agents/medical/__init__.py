"""
Medical Expert Agents (MED-001 to MED-010)
Specialized Australian clinical knowledge experts for AMC exam preparation

All agents comply with:
- Australian medical guidelines (eTG, Australian handbooks)
- 100% citation accuracy (RAG-verified page/section numbers)
- Australian terminology (paediatric, salbutamol, adrenaline)
- SI units (mmol/L not mg/dL)
- Emergency number 000 (not 911)
- PBS medication restrictions
"""

from .base_medical_expert import BaseMedicalExpert
from .med_001_cardiology import CardiologyExpert
from .med_002_respiratory import RespiratoryExpert
from .med_003_gastroenterology import GastroenterologyExpert
from .med_004_endocrinology import EndocrinologyExpert
from .med_005_neurology import NeurologyExpert
from .med_006_emergency import EmergencyExpert
from .med_007_obgyn import ObGynExpert
from .med_008_paediatrics import PaediatricsExpert
from .med_009_psychiatry import PsychiatryExpert
from .med_010_generalpractice import GeneralPracticeExpert

__all__ = [
    'BaseMedicalExpert',
    'CardiologyExpert',
    'RespiratoryExpert',
    'GastroenterologyExpert',
    'EndocrinologyExpert',
    'NeurologyExpert',
    'EmergencyExpert',
    'ObGynExpert',
    'PaediatricsExpert',
    'PsychiatryExpert',
    'GeneralPracticeExpert',
]

# Medical Expert Agent Registry
MEDICAL_AGENTS = {
    'MED-001': CardiologyExpert,
    'MED-002': RespiratoryExpert,
    'MED-003': GastroenterologyExpert,
    'MED-004': EndocrinologyExpert,
    'MED-005': NeurologyExpert,
    'MED-006': EmergencyExpert,
    'MED-007': ObGynExpert,
    'MED-008': PaediatricsExpert,
    'MED-009': PsychiatryExpert,
    'MED-010': GeneralPracticeExpert,
}


def get_medical_agent(agent_id: str, rag_system=None):
    """
    Get medical expert agent by ID.

    Args:
        agent_id: Agent ID (e.g., 'MED-001')
        rag_system: Optional RAG system instance

    Returns:
        Initialized medical expert agent

    Example:
        >>> cardiology = get_medical_agent('MED-001')
        >>> cardiology.metadata.name
        'Cardiology Clinical Expert'
    """
    if agent_id not in MEDICAL_AGENTS:
        raise ValueError(f"Unknown agent ID: {agent_id}. Available: {list(MEDICAL_AGENTS.keys())}")

    agent_class = MEDICAL_AGENTS[agent_id]
    return agent_class(rag_system=rag_system)


def list_medical_agents():
    """
    List all available medical expert agents.

    Returns:
        Dictionary of agent IDs to agent information
    """
    agents_info = {}
    for agent_id, agent_class in MEDICAL_AGENTS.items():
        # Instantiate temporarily to get metadata
        agent = agent_class()
        agents_info[agent_id] = {
            'name': agent.metadata.name,
            'specialty': agent.metadata.specializations[0] if agent.metadata.specializations else 'General',
            'experience_years': agent.metadata.experience_years,
            'version': agent.metadata.version
        }

    return agents_info
