#!/bin/bash
# Python + LLM Integration Setup Validation

set -e

echo "🐍 Python + LLM Integration Validation"
echo "======================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$PROJECT_ROOT"

# Check 1: Python venv exists
echo -n "1. Python venv exists... "
if [ -d "venv" ]; then
    echo "✅ Found"
else
    echo "❌ NOT FOUND"
    echo "   Create with: python3 -m venv venv"
    exit 1
fi

# Check 2: venv activated
echo -n "2. venv activated... "
if python --version 2>&1 | grep -q "Python 3" && which python | grep -q "venv"; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo "✅ Active ($PYTHON_VERSION)"
else
    echo "❌ NOT ACTIVATED"
    echo "   Run: source venv/bin/activate"
    exit 1
fi

# Check 3: Claude API key
echo -n "3. ANTHROPIC_API_KEY... "
if python -c "import os; exit(0 if os.getenv('ANTHROPIC_API_KEY') else 1)" 2>/dev/null; then
    echo "✅ Configured"
else
    echo "❌ NOT SET"
    echo "   Set in .env or: export ANTHROPIC_API_KEY=your_key"
    exit 1
fi

# Check 4: Required Python packages
echo -n "4. Required packages... "
MISSING_PACKAGES=()

if ! python -c "import anthropic" 2>/dev/null; then
    MISSING_PACKAGES+=("anthropic")
fi

if ! python -c "import qdrant_client" 2>/dev/null; then
    MISSING_PACKAGES+=("qdrant-client")
fi

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo "✅ All installed"
else
    echo "❌ Missing: ${MISSING_PACKAGES[*]}"
    echo "   Install with: pip install ${MISSING_PACKAGES[*]}"
    exit 1
fi

# Check 5: Ollama availability (optional)
echo -n "5. Ollama (optional)... "
if command -v ollama &> /dev/null; then
    OLLAMA_MODELS=$(ollama list 2>/dev/null | grep -c "llama3" || echo 0)
    if [ "$OLLAMA_MODELS" -gt 0 ]; then
        echo "✅ Available with llama3 models"
    else
        echo "⚠️  Installed but no llama3 models"
    fi
else
    echo "⚠️  Not installed (OK - Claude API primary)"
fi

# Check 6: UTF-8 encoding in Python scripts
echo -n "6. UTF-8 encoding usage... "
SCRIPTS_WITHOUT_UTF8=$(grep -r "open(" scripts/ backend/ --include="*.py" 2>/dev/null | grep -v "encoding=\"utf-8\"" | wc -l || echo 0)
if [ "$SCRIPTS_WITHOUT_UTF8" -eq 0 ]; then
    echo "✅ All scripts use UTF-8"
else
    echo "⚠️  Found $SCRIPTS_WITHOUT_UTF8 files without explicit UTF-8"
    echo "   Review scripts for: open(..., encoding='utf-8')"
fi

echo ""
echo "✅ Python + LLM Integration Setup Valid"
echo ""
echo "Quick Reference:"
echo "  - Activate venv: source venv/bin/activate"
echo "  - Check API key: echo \$ANTHROPIC_API_KEY"
echo "  - Run validation: python scripts/validate_rag_citations.py"
