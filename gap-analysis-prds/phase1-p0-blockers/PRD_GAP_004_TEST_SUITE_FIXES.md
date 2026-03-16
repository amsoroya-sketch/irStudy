# PRD_GAP_004: Test Suite Fixes (100% Pass Rate)

**Priority**: P0 - CRITICAL BLOCKER
**Estimated Effort**: 8 hours
**Dependencies**: PRD_GAP_001 (Vault/Redis deployed)
**Owner**: testing-qa-expert

---

## 1. REQUEST (What & Why)

### Problem Statement
Test suite **FAILING**: 44 backend failures + 8 collection errors (83.8% pass rate vs 100% target)

### Root Causes
1. **WebSocket import error**: `src.db.database` should be `src.db.base`
2. **AI module import error**: `rag_service` not exposed in `__init__.py`
3. **Missing PyJWT dependency**
4. **Hardcoded Anthropic API keys** in 2 test files

---

## 2. IMPLEMENTATION TASKS

### Task 1: Fix WebSocket Imports (2 hours)
**Files to Update** (8 files):
```python
# BEFORE:
from src.db.database import get_db  # ❌ Module not found

# AFTER:
from src.db.base import get_db  # ✅ Correct import
```

Files:
- `backend/src/websocket/handler.py`
- `backend/src/websocket/session_manager.py`
- `backend/src/websocket/authenticator.py`
- `backend/tests/test_websocket/test_auth.py`
- `backend/tests/test_websocket/test_handler.py`
- `backend/tests/test_websocket/test_session_manager.py`
- `backend/tests/test_websocket/test_timer.py`
- `backend/tests/test_websocket/test_rate_limiter.py`

### Task 2: Expose AI Modules (2 hours)
**File**: `backend/src/ai/__init__.py`
```python
# Add missing exports
from .rag_service import RAGService
from .ai_patient import AIPatient
from .ai_examiner import AIExaminer
from .emotional_state import EmotionalStateMachine

__all__ = [
    "RAGService",
    "AIPatient",
    "AIExaminer",
    "EmotionalStateMachine"
]
```

### Task 3: Install Missing Dependency (1 hour)
```bash
cd /home/dev/Development/irStudy/backend
pip install pyjwt
pip freeze > requirements.txt  # Update requirements
```

### Task 4: Remove Hardcoded API Keys (2 hours)
**Files**:
- `backend/tests/test_ai/test_ai_patient.py`
- `backend/tests/test_ai/test_ai_examiner.py`

```python
# BEFORE:
ANTHROPIC_API_KEY = "sk-ant-api03-..." # ❌ Hardcoded

# AFTER:
from src.core.vault import get_vault_secret
api_key = get_vault_secret("secret/ai-osce/claude-api-key")  # ✅ From Vault
```

### Task 5: Run Full Test Suite (1 hour)
```bash
cd backend
pytest -v --tb=short 2>&1 | tee test_results.log
# Expected: 440+ tests PASSED
```

---

## 3. ACCEPTANCE CRITERIA
- [x] Test pass rate: 100% (440+/440+ passing)
- [x] 0 import errors
- [x] 0 hardcoded credentials
- [x] PyJWT installed
- [x] All WebSocket tests executable

---

**END OF PRD_GAP_004**
