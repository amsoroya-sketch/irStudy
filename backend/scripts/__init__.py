"""backend.scripts package.

The repository also has a top-level ``scripts/`` directory (e.g.
``scripts/content_reconciliation.py``, ``scripts/seed_conditions.py``,
``scripts/backfill_condition_links.py``). When tests run with the backend
directory as CWD, this ``backend/scripts`` package would otherwise shadow the
repo-root one, breaking ``from scripts.content_reconciliation import ...``.

Extending ``__path__`` to include the repo-root ``scripts/`` folder makes BOTH
locations importable under the ``scripts.*`` namespace, so PRD-CONDITIONS-SPINE-001
scripts (which live at the repo root per spec) resolve regardless of CWD. This is
purely additive — existing ``backend/scripts`` modules are unaffected.
"""

import os as _os

_repo_root_scripts = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.dirname(__file__))), "scripts"
)
if _os.path.isdir(_repo_root_scripts) and _repo_root_scripts not in __path__:
    __path__.append(_repo_root_scripts)
