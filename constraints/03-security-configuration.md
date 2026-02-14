# Security & Configuration

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Security & Configuration

### 3.1 NO Hardcoded Secrets (CRITICAL - ZERO TOLERANCE)

**NEVER EVER hardcode:**
- API keys
- Database passwords
- Encryption keys
- User IDs (even for testing)
- File paths with credentials
- Secret tokens

**This is a ZERO TOLERANCE policy. Any hardcoded secret will require immediate fix.**

**Example - CORRECT:**
```python
import os
from pathlib import Path

# ✅ Use environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# ✅ Use config files (excluded from git via .gitignore)
from config import load_config
config = load_config()
db_password = config['database']['password']

# ✅ For testing, use test fixtures
@pytest.fixture
def test_user_id():
    return "test-user-" + str(uuid.uuid4())
```

**Example - INCORRECT:**
```python
# ❌ NEVER do this
DATABASE_URL = "postgresql://user:password123@localhost:5432/db"
OPENAI_API_KEY = "sk-1234567890abcdef"
USER_ID = "mock-user-id-12345"  # Even for testing!
QDRANT_API_KEY = "abc123xyz"
SECRET_KEY = "my-super-secret-key"
```

### 3.2 Configuration Management (MANDATORY)

**Use configuration hierarchy:**

1. Environment variables (highest priority)
2. Config files (`.env`, `config.yaml` - in .gitignore)
3. Default values (lowest priority, only for non-sensitive)

**Example - CORRECT:**
```python
from pathlib import Path
import os
from typing import Optional

class Config:
    """Application configuration with environment variable override"""

    # Paths - safe to hardcode
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    PROCESSED_DIR = DATA_DIR / "processed"
    BOOKS_DIR = BASE_DIR / "Books"

    # Database - from env vars (REQUIRED)
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # Ollama - from env vars with safe default
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

    # Model selection - from env vars with defaults
    DEFAULT_MEDICAL_MODEL: str = os.getenv('MEDICAL_MODEL', 'meditron:7b')
    DEFAULT_QA_MODEL: str = os.getenv('QA_MODEL', 'llama3.1:70b')

    # Optional API keys - may be None
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    QDRANT_API_KEY: Optional[str] = os.getenv('QDRANT_API_KEY')

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration is present"""
        required = ['DATABASE_URL']
        missing = [key for key in required if not getattr(cls, key)]

        if missing:
            raise ValueError(f"Missing required configuration: {missing}")

# Validate config on import
Config.validate()
```

### 3.3 File Path Conventions (MANDATORY)

**ALWAYS use pathlib.Path, NEVER string concatenation:**

**Reference**: All scripts in `/home/dev/Development/irStudy/scripts/` use this pattern

```python
from pathlib import Path

# ✅ CORRECT
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PDF_FILE = DATA_DIR / "books" / "clinical_exam.pdf"

# Create directories
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Check existence
if PDF_FILE.exists():
    with open(PDF_FILE, 'rb') as f:
        content = f.read()

# Get all PDFs in directory
pdf_files = list(DATA_DIR.glob("*.pdf"))

# Recursive search
all_pdfs = list(DATA_DIR.rglob("*.pdf"))

# ❌ INCORRECT
DATA_DIR = "data"  # String path
PDF_FILE = DATA_DIR + "/books/" + "clinical_exam.pdf"  # String concatenation
PDF_FILE = os.path.join(DATA_DIR, "books", "clinical_exam.pdf")  # Old style
```

### 3.4 Sensitive Data Handling

**Medical data is sensitive - anonymize before logging:**

```python
# ✅ CORRECT - Anonymize before logging
patient_id = "12345678"
self.logger.info(f"Processing patient case: {patient_id[:4]}***")  # Show only first 4 digits

case_id = "CASE-2025-001234"
self.logger.info(f"Processing case: {case_id[:13]}...")  # Truncate

# ❌ INCORRECT - Logging sensitive data
self.logger.info(f"Processing patient: John Smith, DOB: 1985-03-15, MRN: 12345678")
self.logger.info(f"Patient email: john.smith@email.com")
```

---

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
