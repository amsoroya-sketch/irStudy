#!/usr/bin/env bash
#
# run_mcq_reimport.sh — re-import MCQs into the database and reconcile authored vs live.
#
# WHO RUNS THIS: the developer/operator, in an environment that HAS database
# credentials. The agent session that created this script does NOT have DB access.
#
# PERMISSIONS: this file is committed without the executable bit in some setups.
# Make it runnable once with:  chmod +x scripts/run_mcq_reimport.sh
# (or simply invoke it via:    bash scripts/run_mcq_reimport.sh)
#
# REQUIRED SECRETS (provide these yourself — NEVER commit them):
#   export DATABASE_PASSWORD='...'        # DB password (or mount /run/secrets/db_password)
#   # Optional overrides (sensible defaults exist in backend/src/db/base.py):
#   export DATABASE_HOST='localhost'
#   export DATABASE_PORT='5432'
#   export DATABASE_NAME='irstudy_medical'
#   export DATABASE_USER='postgres'
#   # OR provide a full URL instead of the components:
#   export DATABASE_URL='postgresql://user:pass@host:5432/irstudy_medical'
#
set -euo pipefail

# --- Resolve repo paths (script lives in <repo>/scripts) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${REPO_ROOT}/backend"

echo "=================================================================="
echo "MCQ RE-IMPORT + RECONCILIATION"
echo "Repo: ${REPO_ROOT}"
echo "=================================================================="

# --- Activate backend virtualenv if present ---
PY="python3"
if [[ -f "${BACKEND_DIR}/venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "${BACKEND_DIR}/venv/bin/activate"
    PY="python"
    echo "[ok] Activated backend venv."
else
    echo "[warn] backend/venv not found — using system ${PY}."
fi

# --- Verify a DB secret is configured (fail fast with a clear message) ---
if [[ -z "${DATABASE_URL:-}" && -z "${DATABASE_PASSWORD:-}" && ! -f "/run/secrets/db_password" ]]; then
    echo "[ERROR] No database credentials found."
    echo "        Set DATABASE_PASSWORD (or DATABASE_URL), or mount /run/secrets/db_password."
    exit 1
fi

# --- Helper: print live respiratory MCQ count (0 if DB/table not ready) ---
resp_count() {
    ( cd "${BACKEND_DIR}" && "${PY}" - <<'PYEOF'
try:
    from sqlalchemy import create_engine, func
    from sqlalchemy.orm import sessionmaker
    from src.db.base import get_database_url
    from src.db.models import MCQ, MedicalSpecialty
    db = sessionmaker(bind=create_engine(get_database_url()))()
    try:
        print(db.query(MCQ).filter(MCQ.specialty == MedicalSpecialty.RESPIRATORY).count())
    finally:
        db.close()
except Exception as e:
    print(f"0  (count unavailable: {str(e)[:80]})")
PYEOF
)
}

echo ""
echo "------------------------------------------------------------------"
echo "PRE-IMPORT respiratory MCQ count in DB: $(resp_count)"
echo "------------------------------------------------------------------"

# --- (a) Run the resilient importer ---
echo ""
echo ">>> Running import_mcqs.py ..."
( cd "${REPO_ROOT}" && "${PY}" backend/scripts/import_mcqs.py --source data/mcqs/ )

echo ""
echo "------------------------------------------------------------------"
echo "POST-IMPORT respiratory MCQ count in DB: $(resp_count)"
echo "------------------------------------------------------------------"

# --- (b) Run the reconciliation report (writes reconciliation.json) ---
echo ""
echo ">>> Running content_reconciliation.py --json ..."
( cd "${REPO_ROOT}" && "${PY}" scripts/content_reconciliation.py --json )

echo ""
echo "=================================================================="
echo "DONE. Review:"
echo "  - data/mcqs/_reports/respiratory_unimportable.json (regenerate these)"
echo "  - data/mcqs/_reports/reconciliation.json           (authored vs live)"
echo "=================================================================="
