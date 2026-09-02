#!/usr/bin/env python3
"""Re-exec the backend venv's Python with the given script + args.

Operator convenience only: lets `python3 scripts/_run_with_venv.py <script> [args...]`
run <script> under backend/venv (qdrant-client, sentence-transformers, etc.)
without needing to invoke the venv interpreter path directly.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."
_VENV_PYTHON = os.path.join(_ROOT, "backend", "venv", "bin", "python3")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/_run_with_venv.py <script.py> [args...]")
        sys.exit(2)
    # Load backend/.env into this process so the re-exec'd script inherits it
    # (DATABASE_PASSWORD, ANTHROPIC_API_KEY, QDRANT_URL, etc.) — execv passes
    # through the current os.environ.
    try:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(_ROOT, "backend", ".env"))
    except ImportError:
        pass
    os.execv(_VENV_PYTHON, [_VENV_PYTHON] + sys.argv[1:])
