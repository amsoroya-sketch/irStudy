"""Progress tracking API endpoints."""

# Import the router from the flat progress module (PRD endpoints)
import importlib.util, sys, os

# Load the flat progress.py (not this package)
flat_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'progress.py')
spec = importlib.util.spec_from_file_location('_progress_flat', flat_path)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)
router = _mod.router

__all__ = ['router']
