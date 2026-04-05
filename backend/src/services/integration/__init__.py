"""
Integration Services

Cross-system integration layer for irStudy platform:
- OSCE-to-EMR conversion
- Learning transfer analytics
- Progress synchronization
"""

from .osce_to_emr_converter import OSCEToEMRConverter

__all__ = ['OSCEToEMRConverter']
