#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
source .env
set +a
cd ..
backend/venv/bin/python scripts/content_reconciliation.py --json
echo "== reconciliation.json coverage_by_blueprint =="
python3 -c "
import json
d = json.load(open('data/mcqs/_reports/reconciliation.json'))
print(list(d.keys()))
cov = d.get('coverage_by_blueprint', {})
print(json.dumps(cov, indent=2))
"
