#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
source .env
set +a
venv/bin/python - <<'PYEOF'
import os
from sqlalchemy import create_engine, text

url = f"postgresql://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}@{os.environ['DATABASE_HOST']}:{os.environ['DATABASE_PORT']}/{os.environ['DATABASE_NAME']}"
engine = create_engine(url)
with engine.connect() as conn:
    n_cond = conn.execute(text("SELECT count(*) FROM conditions")).scalar()
    print("conditions rows:", n_cond)
    for tbl in ("mcqs", "osces", "patient_personas", "mock_patients"):
        total = conn.execute(text(f"SELECT count(*) FROM {tbl}")).scalar()
        linked = conn.execute(text(f"SELECT count(*) FROM {tbl} WHERE condition_id IS NOT NULL")).scalar()
        print(f"{tbl}: total={total} linked={linked}")
PYEOF
