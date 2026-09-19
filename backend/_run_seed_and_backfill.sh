#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
source .env
set +a
cd ..
echo "== seed_conditions.py =="
backend/venv/bin/python scripts/seed_conditions.py
echo "== backfill_condition_links.py =="
backend/venv/bin/python scripts/backfill_condition_links.py
echo "== content_reconciliation.py --json (tail) =="
backend/venv/bin/python scripts/content_reconciliation.py --json > /tmp/reconciliation.json
python3 -c "
import json
d = json.load(open('/tmp/reconciliation.json'))
print(list(d.keys()))
if 'coverage_by_blueprint' in d:
    print(json.dumps(d['coverage_by_blueprint'], indent=2)[:3000])
"
