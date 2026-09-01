"""Thin import package for EMR practice-case tooling.

Re-exports the canonical content gate implemented in
``scripts/validate_emr_practice_cases.py`` so test modules can import it via a
clean, stable path without turning the large project-level ``scripts/`` folder
into an importable package.
"""
