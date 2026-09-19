#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
source .env
set +a
venv/bin/python - <<'PYEOF'
import sys
sys.path.insert(0, ".")
from sqlalchemy import create_engine, text
from src.db.base import get_database_url
engine = create_engine(get_database_url())
with engine.connect() as conn:
    rows = conn.execute(text("SELECT question_id, specialty, tags FROM mcqs LIMIT 5")).fetchall()
    for r in rows:
        print(r)
PYEOF
