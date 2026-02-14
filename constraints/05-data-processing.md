# Data Processing Standards

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Data Processing Standards

### 5.1 JSON File Handling (MANDATORY)

**Reference Files**:
- `/home/dev/Development/irStudy/scripts/extract_pdfs.py`
- `/home/dev/Development/irStudy/scripts/chunk_medical_texts.py`

**ALWAYS specify encoding='utf-8':**

```python
import json
from pathlib import Path
from typing import Dict, Any

# ✅ CORRECT - Load JSON with proper encoding and error handling
def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON file with proper encoding and error handling.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.logger.info(f"Loaded JSON from {file_path} ({file_path.stat().st_size} bytes)")
        return data

    except json.JSONDecodeError as e:
        self.logger.error(f"Invalid JSON in {file_path}: {e}")
        raise
    except Exception as e:
        self.logger.error(f"Failed to load {file_path}: {e}")
        raise

# ✅ CORRECT - Save JSON with proper encoding and formatting
def save_json(data: Dict[str, Any], file_path: Path, indent: int = 2) -> None:
    """
    Save data to JSON file with proper encoding.

    Args:
        data: Data to save
        file_path: Output file path
        indent: JSON indentation (default: 2 spaces)
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,  # Preserve Unicode characters
                indent=indent
            )

        file_size = file_path.stat().st_size
        self.logger.info(f"Saved JSON to {file_path} ({file_size:,} bytes)")

    except Exception as e:
        self.logger.error(f"Failed to save {file_path}: {e}")
        raise

# ❌ INCORRECT - Missing encoding
with open('file.json', 'r') as f:  # ❌ Missing encoding='utf-8'
    data = json.load(f)

# ❌ INCORRECT - No error handling
data = json.load(open('file.json'))  # ❌ No try-except, no encoding
```

### 5.2 Large File Processing (MANDATORY)

**ALWAYS use progress bars (tqdm) for long operations:**

**Reference File**: `/home/dev/Development/irStudy/scripts/chunk_medical_texts.py`

```python
from tqdm import tqdm
from typing import List, Any

# ✅ CORRECT - Process with progress bar
def process_large_dataset(self, items: List[Any], description: str = "Processing") -> List[Any]:
    """
    Process large dataset with progress tracking and error handling.

    Args:
        items: List of items to process
        description: Progress bar description

    Returns:
        List of successfully processed results
    """
    results = []
    errors = []

    for item in tqdm(items, desc=description, unit="item"):
        try:
            result = self._process_item(item)
            results.append(result)
        except Exception as e:
            self.logger.warning(f"Failed to process item {item}: {e}")
            errors.append({'item': item, 'error': str(e)})
            continue

    self.logger.info(f"Processed {len(results)}/{len(items)} items ({len(errors)} errors)")

    if errors:
        self.logger.warning(f"Errors occurred: {errors}")

    return results

# ✅ CORRECT - Batch processing for memory efficiency
def process_in_batches(
    self,
    items: List[Any],
    batch_size: int = 100,
    description: str = "Processing batches"
) -> List[Any]:
    """
    Process items in batches to manage memory usage.

    Args:
        items: List of items to process
        batch_size: Number of items per batch
        description: Progress bar description

    Returns:
        List of all processed results
    """
    results = []
    num_batches = (len(items) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(items), batch_size), desc=description, total=num_batches, unit="batch"):
        batch = items[i:i+batch_size]

        try:
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
        except Exception as e:
            self.logger.error(f"Batch {i//batch_size + 1} failed: {e}")
            continue

    return results

# ❌ INCORRECT - No progress indicator
for item in large_list:  # ❌ No tqdm, user has no idea of progress
    process(item)

# ❌ INCORRECT - Loading entire large file into memory
with open('huge_file.json', 'r') as f:
    data = json.load(f)  # ❌ Could be GBs, may crash
```

### 5.3 Pickle vs JSON Usage Guidelines

**Guidelines:**

**Use JSON when:**
- Data needs to be human-readable
- Data will be shared between systems or languages
- Data needs to be version-controlled (git-friendly)
- Data structure is simple (dicts, lists, strings, numbers, booleans)
- Security is a concern (JSON is safer than pickle)

**Use Pickle when:**
- Storing complex Python objects (numpy arrays, models, embeddings)
- Performance is critical (pickle is faster for large data)
- Data stays within Python ecosystem
- Object structure preservation is important

**Examples:**

```python
import pickle
import json
import numpy as np

# ✅ JSON for MCQ questions (human-readable, shareable)
questions = [
    {'id': 'MCQ-001', 'stem': '...', 'answer': 'B'},
    {'id': 'MCQ-002', 'stem': '...', 'answer': 'A'}
]
with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2)

# ✅ Pickle for embeddings (binary, fast, numpy arrays)
embeddings = np.array([[0.1, 0.2, ...], [0.3, 0.4, ...]])  # 768-dim vectors
with open('embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# ✅ JSON for configuration (human-editable)
config = {
    'model': 'meditron:7b',
    'temperature': 0.3,
    'max_tokens': 4096
}
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

# ✅ Pickle for trained model (complex object)
trained_model = some_ml_model.fit(X, y)
with open('model.pkl', 'wb') as f:
    pickle.dump(trained_model, f)
```

### 5.4 Path Management Best Practices

**Define all paths upfront in a configuration class:**

```python
from pathlib import Path

class DataPaths:
    """Centralized path management for data processing"""

    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    BOOKS_DIR = BASE_DIR / "Books"
    SCRIPTS_DIR = BASE_DIR / "scripts"

    # Output directories
    CHUNKS_DIR = PROCESSED_DIR / "chunks"
    EMBEDDINGS_DIR = PROCESSED_DIR / "embeddings"
    QUESTIONS_DIR = PROCESSED_DIR / "questions"

    # Specific files
    CHUNKS_JSON = DATA_DIR / "chunks.json"
    FLASHCARDS_JSON = BASE_DIR / "ICRP_Program_Resources" / "Flashcards" / "flashcard_data.json"

    @classmethod
    def initialize(cls) -> None:
        """Create all necessary directories"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DIR,
            cls.PROCESSED_DIR,
            cls.CHUNKS_DIR,
            cls.EMBEDDINGS_DIR,
            cls.QUESTIONS_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_processed_file(cls, book_name: str) -> Path:
        """Get path for processed book JSON"""
        safe_name = book_name.replace(' ', '_').replace('/', '_')
        return cls.PROCESSED_DIR / f"{safe_name}.json"

    @classmethod
    def get_book_chunks(cls, book_name: str) -> Path:
        """Get path for book chunks"""
        safe_name = book_name.replace(' ', '_').replace('/', '_')
        return cls.CHUNKS_DIR / f"{safe_name}_chunks.json"

# Initialize paths on import
DataPaths.initialize()

# Usage in scripts
pdf_file = DataPaths.BOOKS_DIR / "clinical_exam.pdf"
output_file = DataPaths.get_processed_file("Clinical Examination")
```

---

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
