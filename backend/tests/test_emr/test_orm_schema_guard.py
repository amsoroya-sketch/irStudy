"""ORM <-> migration-008 schema drift guard (regression test).

The EMR ``submit`` endpoint 500-ed in production because the ORM models
``EMRValidationResult`` / ``EMRPrescription`` had silently drifted away from the
real Postgres schema defined in Alembic migration 008
(``backend/alembic/versions/20260215_1200_008_add_emr_tables.py``).

The drift was invisible to the existing suite because those tests build their
tables from the ORM metadata via SQLite ``create_all`` — so the ORM was always
"self-consistent" with the test DB, never with the real migration.

This guard closes that hole. It inspects the ORM ``__table__.columns`` directly
(no DB needed) and asserts:

* the critical NOT-NULL columns from migration 008 are PRESENT
  (``validation_type`` on emr_validation_results, ``repeats`` on
  emr_prescriptions), and
* the removed legacy column names are ABSENT
  (``rule_based_score`` / ``final_score`` / ``ai_validation_score`` /
  ``specialist_score``).

It would FAIL against the old (drifted) models — which HAD
``rule_based_score``/``final_score``/``ai_validation_score`` and LACKED
``validation_type`` — and PASSES against the fixed models.
"""

from src.db.models import EMRPrescription, EMRValidationResult


# Columns migration 008 defines for emr_validation_results (source of truth).
_MIGRATION_008_VALIDATION_COLUMNS = {
    "id",
    "session_id",
    "validation_type",
    "layer_1_zod",
    "layer_2_python",
    "layer_3_ai",
    "overall_score",
    "passed",
    "strengths",
    "improvements",
    "red_flags",
    "validated_at",
    "created_at",
}

# Columns migration 008 defines for emr_prescriptions (source of truth).
_MIGRATION_008_PRESCRIPTION_COLUMNS = {
    "id",
    "session_id",
    "medication_name",
    "dose",
    "frequency",
    "route",
    "repeats",
    "indication",
    "pbs_listed",
    "pbs_item_code",
    "authority_required",
    "validation_errors",
    "is_valid",
    "created_at",
    "updated_at",
}

# Legacy names that were removed — their presence means the ORM has drifted back.
_REMOVED_LEGACY_COLUMNS = {
    "rule_based_score",
    "final_score",
    "ai_validation_score",
    "specialist_score",
}


def _column_names(model) -> set[str]:
    return set(model.__table__.columns.keys())


# ---------------------------------------------------------------------------
# EMRValidationResult
# ---------------------------------------------------------------------------


def test_validation_result_has_migration_008_columns():
    """Every migration-008 column must exist on the ORM model."""
    cols = _column_names(EMRValidationResult)
    missing = _MIGRATION_008_VALIDATION_COLUMNS - cols
    assert not missing, (
        "EMRValidationResult is missing migration-008 columns "
        f"(ORM drifted behind the DB): {sorted(missing)}"
    )


def test_validation_result_has_not_null_validation_type():
    """``validation_type`` is NOT NULL in the DB and must be a real, non-nullable column."""
    cols = EMRValidationResult.__table__.columns
    assert "validation_type" in cols.keys(), (
        "EMRValidationResult.validation_type is absent — inserts will violate the "
        "NOT NULL constraint and 500 (the original production bug)."
    )
    assert cols["validation_type"].nullable is False, (
        "EMRValidationResult.validation_type must be NOT NULL to match migration 008."
    )


def test_validation_result_drops_legacy_columns():
    """Removed legacy score columns must NOT reappear on the ORM model."""
    cols = _column_names(EMRValidationResult)
    resurfaced = cols & _REMOVED_LEGACY_COLUMNS
    assert not resurfaced, (
        "EMRValidationResult still references removed legacy columns not present in "
        f"migration 008 (schema drift): {sorted(resurfaced)}"
    )


# ---------------------------------------------------------------------------
# EMRPrescription
# ---------------------------------------------------------------------------


def test_prescription_has_migration_008_columns():
    """Every migration-008 column must exist on the ORM model."""
    cols = _column_names(EMRPrescription)
    missing = _MIGRATION_008_PRESCRIPTION_COLUMNS - cols
    assert not missing, (
        "EMRPrescription is missing migration-008 columns "
        f"(ORM drifted behind the DB): {sorted(missing)}"
    )


def test_prescription_has_not_null_repeats_with_check():
    """``repeats`` is NOT NULL (CHECK 0..5) in the DB and must be non-nullable in the ORM."""
    cols = EMRPrescription.__table__.columns
    assert "repeats" in cols.keys(), (
        "EMRPrescription.repeats is absent — inserts will violate the NOT NULL "
        "constraint and 500 (the original production bug)."
    )
    assert cols["repeats"].nullable is False, (
        "EMRPrescription.repeats must be NOT NULL to match migration 008."
    )
    # The 0..5 CHECK constraint from migration 008 must be represented on the model.
    check_names = {
        c.name for c in EMRPrescription.__table__.constraints if getattr(c, "name", None)
    }
    assert "check_emr_prescriptions_repeats_range" in check_names, (
        "EMRPrescription is missing the repeats-range CHECK constraint "
        "(check_emr_prescriptions_repeats_range) defined in migration 008."
    )
