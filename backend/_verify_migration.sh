#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
source .env
set +a
echo "== alembic current (before) =="
venv/bin/alembic current
echo "== alembic upgrade head =="
venv/bin/alembic upgrade head
echo "== alembic current (after upgrade) =="
venv/bin/alembic current
echo "== alembic downgrade -2 =="
venv/bin/alembic downgrade -2
echo "== alembic current (after downgrade) =="
venv/bin/alembic current
echo "== alembic upgrade head (re-apply) =="
venv/bin/alembic upgrade head
echo "== alembic current (final) =="
venv/bin/alembic current
