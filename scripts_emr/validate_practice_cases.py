"""Thin import shim -> re-exports the canonical EMR practice-case content gate.

The single, canonical implementation lives in
``scripts/validate_emr_practice_cases.py`` at the project root. To avoid making
the whole ``scripts/`` directory an importable package (and to keep exactly ONE
implementation), this shim loads that file by path and re-exports its public
functions.

Usage:
    from scripts_emr.validate_practice_cases import validate_case, validate_dir
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_CANONICAL = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validate_emr_practice_cases.py"
)

_spec = importlib.util.spec_from_file_location(
    "validate_emr_practice_cases", _CANONICAL
)
if _spec is None or _spec.loader is None:  # pragma: no cover - defensive
    raise ImportError(f"Cannot load canonical gate at {_CANONICAL}")

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

validate_case = _module.validate_case
validate_dir = _module.validate_dir

__all__ = ["validate_case", "validate_dir"]
