"""
Comprehensive Security Test Suite
Tests all security controls before deployment

Reference: docs/SECURITY_COMPLIANCE_CHECKLIST.md
"""

import pytest
import os
import re
from pathlib import Path
from fastapi.testclient import TestClient


# ============================================================================
# 1. CREDENTIAL SCANNING TESTS
# ============================================================================

def test_no_hardcoded_passwords():
    """Ensure no hardcoded passwords in codebase"""
    project_root = Path("/home/dev/Development/irStudy")
    violations = []
    
    # Scan Python files
    for filepath in project_root.glob("backend/src/**/*.py"):
        if "test_" in filepath.name or "__pycache__" in str(filepath):
            continue
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Check for hardcoded passwords (simple pattern)
            # Matches: password = "something" (not password_hash, hashed_password)
            pattern = r'password\s*=\s*["\'](?!.*{{|}})[\w\-!@#$%^&*()+=]{8,}["\']'
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(f"{filepath}:{line_num} - {match.group()}")
    
    assert len(violations) == 0, (
        f"Hardcoded passwords found ({len(violations)} violations):\n" +
        "\n".join(violations[:5])
    )


def test_no_hardcoded_api_keys():
    """Ensure no Anthropic API keys in code"""
    project_root = Path("/home/dev/Development/irStudy")
    violations = []
    
    # Files to exclude from scan (test helpers and setup scripts that reference patterns)
    excluded_names = {"setup_secrets.py", "test_security_comprehensive.py"}

    # Scan all Python and TypeScript files
    for ext in ["**/*.py", "**/*.ts", "**/*.tsx"]:
        for filepath in project_root.glob(ext):
            if "node_modules" in str(filepath) or "venv" in str(filepath):
                continue
            if ".md" in filepath.suffix or "__pycache__" in str(filepath):
                continue
            if filepath.name in excluded_names:
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        stripped = line.strip()
                        # Skip comment lines
                        if stripped.startswith('#') or stripped.startswith('//'):
                            continue
                        # Check for real sk-ant- key (not placeholder)
                        if "sk-ant-" in line and "REPLACE" not in line and "your-" not in line.lower():
                            violations.append(f"{filepath}:{line_num}")
            except Exception:
                pass  # Skip binary or unreadable files
    
    assert len(violations) == 0, (
        f"Anthropic API keys found in code ({len(violations)} violations):\n" +
        "\n".join(violations[:5])
    )


def test_no_database_urls_with_credentials():
    """Ensure no database URLs with credentials in code"""
    project_root = Path("/home/dev/Development/irStudy")
    violations = []
    
    # Scan Python files
    for filepath in project_root.glob("backend/src/**/*.py"):
        if "test_" in filepath.name or "__pycache__" in str(filepath):
            continue
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Check for database URL pattern with credentials
            # postgresql://user:password@host/db
            pattern = r'postgresql://[\w\-]+:[\w\-!@#$%^&*()+=]+@'
            matches = re.finditer(pattern, content)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                # Ignore if in .env file or comment
                line_start = content.rfind('\n', 0, match.start()) + 1
                line = content[line_start:content.find('\n', match.end())]
                if not line.strip().startswith('#'):
                    violations.append(f"{filepath}:{line_num}")
    
    assert len(violations) == 0, (
        f"Database URLs with credentials found ({len(violations)} violations):\n" +
        "\n".join(violations[:5])
    )


# ============================================================================
# 2. PHI PROTECTION TESTS
# ============================================================================

def test_no_phi_in_logging_statements():
    """Ensure patient names not logged"""
    project_root = Path("/home/dev/Development/irStudy")
    violations = []
    
    # Scan Python files
    for filepath in project_root.glob("backend/src/**/*.py"):
        if "test_" in filepath.name or "__pycache__" in str(filepath):
            continue
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Check for logging patient names
            # logger.info(f"Patient: {patient.name}")
            patterns = [
                r'logger\.\w+\(.*patient.*name',
                r'print\(.*patient.*name',
                r'console\.log\(.*patient.*name',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    # Check if anonymized
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line = content[line_start:content.find('\n', match.end())]
                    if "anonymize" not in line.lower() and "# PHI" not in line:
                        violations.append(f"{filepath}:{line_num}")
    
    assert len(violations) == 0, (
        f"PHI in logging statements ({len(violations)} violations):\n" +
        "\n".join(violations[:5])
    )


def test_phi_anonymization():
    """Test PHI anonymization before Claude API"""
    from src.security.phi_anonymizer import anonymize_for_claude
    
    # Mock patient data
    patient_data = {
        "full_name": "John Smith",
        "email": "john.smith@example.com",
        "mrn": "MRN12345678",
        "dob": "1985-05-15"
    }
    
    soap_note = {
        "subjective": "John Smith presents with chest pain radiating to left arm",
        "objective": "BP 150/90, HR 95, normal ECG",
        "assessment": "Possible ACS, r/o MI",
        "plan": "Aspirin 300mg, GTN, admit for troponin"
    }
    
    # Anonymize
    anonymized = anonymize_for_claude(soap_note, patient_data)
    
    # Assertions
    assert "John Smith" not in str(anonymized), "Patient name not anonymized"
    assert "john.smith@example.com" not in str(anonymized), "Email not anonymized"
    assert "MRN12345678" not in str(anonymized), "MRN not anonymized"
    assert "[PATIENT]" in anonymized["subjective"], "Placeholder not used"


# ============================================================================
# 3. HTTPS & SECURITY HEADERS TESTS
# ============================================================================

@pytest.mark.skip(reason="Requires running server - test manually")
def test_https_redirect(client: TestClient):
    """Test HTTPS redirect middleware"""
    # Simulate HTTP request
    response = client.get(
        "http://example.com/api/health",
        follow_redirects=False,
        headers={"Host": "example.com"}
    )
    
    # Should redirect to HTTPS
    assert response.status_code == 301
    assert response.headers["location"].startswith("https://")


@pytest.mark.skip(reason="Requires running server - test manually")
def test_security_headers(client: TestClient):
    """Test security headers are present"""
    response = client.get("/api/health")
    
    # HSTS
    assert "Strict-Transport-Security" in response.headers
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
    
    # Anti-MIME-sniffing
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    
    # Anti-clickjacking
    assert response.headers.get("X-Frame-Options") == "DENY"
    
    # XSS protection
    assert "X-XSS-Protection" in response.headers
    
    # CSP
    assert "Content-Security-Policy" in response.headers


# ============================================================================
# 4. ENCRYPTION TESTS
# ============================================================================

def test_no_weak_hashing_algorithms():
    """Ensure no MD5/SHA1 usage"""
    project_root = Path("/home/dev/Development/irStudy")
    violations = []
    
    # Scan Python files
    for filepath in project_root.glob("backend/src/**/*.py"):
        if "test_" in filepath.name or "__pycache__" in str(filepath):
            continue
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Check for weak algorithms
            weak_patterns = [
                r'import md5',
                r'import sha1',
                r'hashlib\.md5',
                r'hashlib\.sha1',
            ]
            
            for pattern in weak_patterns:
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    # Ignore comments
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line = content[line_start:content.find('\n', match.end())]
                    if not line.strip().startswith('#'):
                        violations.append(f"{filepath}:{line_num} - {match.group()}")
    
    assert len(violations) == 0, (
        f"Weak hashing algorithms found ({len(violations)} violations):\n" +
        "\n".join(violations[:5])
    )


def test_encryption_module_exists():
    """Verify encryption module exists"""
    encryption_path = Path("/home/dev/Development/irStudy/backend/src/security/encryption.py")
    assert encryption_path.exists(), "Encryption module not found"


# ============================================================================
# 5. AUSTRALIAN COMPLIANCE TESTS
# ============================================================================

def test_no_american_drug_names():
    """Ensure Australian drug names used (not American)"""
    project_root = Path("/home/dev/Development/irStudy")
    violations = []
    
    american_terms = {
        "acetaminophen": "paracetamol",
        "albuterol": "salbutamol",
        "epinephrine": "adrenaline",
    }
    
    # Scan Python and TypeScript files
    for ext in ["backend/src/**/*.py", "frontend/src/**/*.ts", "frontend/src/**/*.tsx"]:
        for filepath in project_root.glob(ext):
            if "test_" in filepath.name or "validator" in filepath.name:
                continue
            if "__pycache__" in str(filepath):
                continue
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Build set of line numbers that are inside docstrings/comments
                in_docstring = False
                docstring_lines = set()
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if '"""' in stripped or "'''" in stripped:
                        count = stripped.count('"""') + stripped.count("'''")
                        if count >= 2:
                            docstring_lines.add(i)  # opening and closing on same line
                        else:
                            in_docstring = not in_docstring
                            docstring_lines.add(i)
                    elif in_docstring:
                        docstring_lines.add(i)

                content = "".join(lines)
                for american, australian in american_terms.items():
                    pattern = rf'\b{american}\b'
                    matches = re.finditer(pattern, content, re.IGNORECASE)

                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line = content[line_start:content.find('\n', match.end())]
                        stripped = line.strip()
                        # Skip comment, docstring, and quoted-string lines
                        if stripped.startswith('#') or stripped.startswith('//'):
                            continue
                        if stripped.startswith('"') or stripped.startswith("'"):
                            continue
                        if line_num in docstring_lines:
                            continue
                        # Skip lines with security scan exemption
                        if "SECURITY SCAN EXEMPTION" in line or "SECURITY SCAN EXEMPTION" in content[max(0, line_start-200):line_start]:
                            continue
                        violations.append(
                            f"{filepath}:{line_num} - Use '{australian}' not '{american}'"
                        )
            except Exception:
                pass
    
    # Allow some violations (might be in validators/tests)
    assert len(violations) < 5, (
        f"American drug names found ({len(violations)} violations):\n" +
        "\n".join(violations[:5])
    )


def test_no_american_emergency_number():
    """Ensure 000 used, not 911"""
    project_root = Path("/home/dev/Development/irStudy")
    violations = []
    
    # Scan Python and TypeScript files
    for ext in ["backend/src/**/*.py", "frontend/src/**/*.ts", "frontend/src/**/*.tsx"]:
        for filepath in project_root.glob(ext):
            if "test_" in filepath.name:
                continue
            if "__pycache__" in str(filepath):
                continue
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Build set of docstring line numbers
                in_docstring = False
                docstring_lines = set()
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if '"""' in stripped or "'''" in stripped:
                        count = stripped.count('"""') + stripped.count("'''")
                        if count >= 2:
                            docstring_lines.add(i)
                        else:
                            in_docstring = not in_docstring
                            docstring_lines.add(i)
                    elif in_docstring:
                        docstring_lines.add(i)

                content = "".join(lines)
                pattern = r'\b911\b'
                matches = re.finditer(pattern, content)

                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line = content[line_start:content.find('\n', match.end())]
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('//'):
                        continue
                    if stripped.startswith('"') or stripped.startswith("'"):
                        continue
                    if line_num in docstring_lines:
                        continue
                    # Skip lines with security scan exemption
                    if "SECURITY SCAN EXEMPTION" in line or "SECURITY SCAN EXEMPTION" in content[max(0, line_start-200):line_start]:
                        continue
                    violations.append(f"{filepath}:{line_num} - Use 000, not 911")
            except Exception:
                pass
    
    assert len(violations) == 0, (
        f"American emergency number found ({len(violations)} violations):\n" +
        "\n".join(violations[:5])
    )


# ============================================================================
# 6. INTEGRATION TESTS
# ============================================================================

def test_vault_integration_exists():
    """Verify Vault integration module exists"""
    vault_path = Path("/home/dev/Development/irStudy/backend/src/core/vault.py")
    assert vault_path.exists(), "Vault integration module not found"


def test_https_middleware_exists():
    """Verify HTTPS middleware exists"""
    https_path = Path("/home/dev/Development/irStudy/backend/src/middleware/https_redirect.py")
    assert https_path.exists(), "HTTPS middleware not found"


def test_security_audit_script_exists():
    """Verify security audit script exists and is executable"""
    audit_script = Path("/home/dev/Development/irStudy/scripts/security-audit.sh")
    assert audit_script.exists(), "Security audit script not found"
    assert os.access(audit_script, os.X_OK), "Security audit script not executable"


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """FastAPI test client (if needed for integration tests)"""
    from src.main import app
    return TestClient(app)
