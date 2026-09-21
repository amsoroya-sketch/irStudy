"""Unit tests for the specialty-taxonomy normalizer (SPECIALTY_MAP + planner).

These are PURE tests: they exercise the module's data map and pure helpers only
(``resolve_target`` / ``plan_table``) and never touch a database. The repo-root
``scripts`` package is importable via ``backend/tests/test_scripts/conftest.py``.
"""
# pylint: disable=import-error,no-name-in-module
from scripts.normalize_specialty_taxonomy import (
    SPECIALTY_MAP,
    LEFT_AS_CATEGORY,
    VALID_ENUM_VALUES,
    resolve_target,
    plan_table,
)
# pylint: enable=import-error,no-name-in-module


# The 5 patient_personas mappings that MUST hold (the important table — feeds
# mock-exam specialty selection). Keys are the free-text labels as authored.
EXPECTED_PERSONA_MAPPINGS = {
    "Cardiology": "cardiology",
    "Emergency": "emergency_medicine",
    "General Practice": "general_practice",
    "Pediatrics": "paediatrics",
    "Respiratory": "respiratory",
}

# html_osce_notes labels that are note CATEGORIES, not clinical specialties, and
# must be left unmapped (absent from SPECIALTY_MAP).
CATEGORY_LABELS_LEFT_UNMAPPED = ["Medicine", "Ethics & Communication", "Mock OSCE Stations"]


def test_persona_mappings_present_and_case_insensitive():
    """All 5 persona labels resolve to their exact enum target (any casing)."""
    for label, expected in EXPECTED_PERSONA_MAPPINGS.items():
        assert resolve_target(label) == expected
        assert resolve_target(label.lower()) == expected
        assert resolve_target(label.upper()) == expected
        assert resolve_target(f"  {label}  ") == expected  # stripped


def test_category_labels_are_left_unmapped():
    """Medicine / Ethics & Communication / Mock OSCE Stations are NOT specialties."""
    for label in CATEGORY_LABELS_LEFT_UNMAPPED:
        assert _norm_absent(label), f"{label!r} must not be in SPECIALTY_MAP"
        assert resolve_target(label) is None
        assert label in LEFT_AS_CATEGORY


def _norm_absent(label: str) -> bool:
    return label.strip().lower() not in SPECIALTY_MAP


def test_all_map_targets_are_valid_enum_values():
    """Every SPECIALTY_MAP target is a member of the MedicalSpecialty enum."""
    assert set(SPECIALTY_MAP.values()) <= set(VALID_ENUM_VALUES)


def test_html_osce_clinical_mappings():
    """The 7 clinical html_osce_notes categories map onto the enum."""
    expected = {
        "Musculoskeletal": "musculoskeletal",
        "Ophthalmology": "ophthalmology",
        "Psychiatry": "psychiatry",
        "Surgery": "surgery",
        "Urology": "urology",
        "Paediatrics": "paediatrics",
        "Obstetrics & Gynecology": "obstetrics_gynaecology",
    }
    for label, target in expected.items():
        assert resolve_target(label) == target


def test_plan_table_personas_no_merge_keeps_count_11():
    """Format-only normalization must NOT merge distinct specialties.

    Mirrors the live patient_personas distribution: 5 Title-Case values + 6
    already-lowercase enum values. After the plan, distinct count stays 11.
    """
    counts = {
        "Cardiology": 45,
        "Emergency": 42,
        "General Practice": 40,
        "Pediatrics": 40,
        "Respiratory": 40,
        "endocrinology": 8,
        "gastroenterology": 8,
        "neurology": 8,
        "obstetrics_gynaecology": 8,
        "psychiatry": 8,
        "surgery": 8,
    }
    updates, no_ops, untouched = plan_table(counts)

    # Exactly the 5 Title-Case values are updated.
    changed = {old: new for old, new, _n in updates}
    assert changed == EXPECTED_PERSONA_MAPPINGS

    # All 6 already-lowercase values are conforming enum values -> no-ops
    # (idempotent), regardless of whether they also appear as map self-keys.
    # No persona value is a non-specialty category label, so untouched is empty.
    no_op_values = {v for v, _n in no_ops}
    assert no_op_values == {
        "psychiatry",
        "surgery",
        "endocrinology",
        "gastroenterology",
        "neurology",
        "obstetrics_gynaecology",
    }
    assert untouched == []

    # Distinct count is preserved (no merges): each new value is novel.
    projected = set(counts)
    for old, new, _n in updates:
        projected.discard(old)
        projected.add(new)
    assert len(projected) == 11
    assert all(v in VALID_ENUM_VALUES for v in projected)


def test_plan_table_html_osce_updates_7_leaves_3():
    """Mirrors live html_osce_notes: 7 clinical updates, 3 category labels left."""
    counts = {
        "Ethics & Communication": 6,
        "Medicine": 106,
        "Mock OSCE Stations": 19,
        "Musculoskeletal": 29,
        "Obstetrics & Gynecology": 75,
        "Ophthalmology": 6,
        "Paediatrics": 8,
        "Psychiatry": 5,
        "Surgery": 5,
        "Urology": 11,
    }
    updates, no_ops, untouched = plan_table(counts)
    assert len(updates) == 7
    assert no_ops == []
    untouched_values = {v for v, _n in untouched}
    assert untouched_values == set(CATEGORY_LABELS_LEFT_UNMAPPED)


def test_plan_table_is_idempotent_on_normalized_input():
    """Feeding already-normalized enum values yields zero updates."""
    counts = {
        "cardiology": 45,
        "emergency_medicine": 42,
        "general_practice": 40,
        "paediatrics": 48,
        "respiratory": 40,
    }
    updates, _no_ops, _untouched = plan_table(counts)
    assert updates == []
