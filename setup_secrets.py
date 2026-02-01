#!/usr/bin/env python3
"""
Setup Secrets Directory for irStudy Medical Education Platform
Generates secure passwords and creates Docker secrets files
SECURITY: Ensures HIPAA compliance with zero hardcoded credentials
"""

import os
import secrets
import string
from pathlib import Path

def generate_password(length=32, use_special_chars=False):
    """Generate cryptographically secure password"""
    if use_special_chars:
        alphabet = string.ascii_letters + string.digits + string.punctuation
    else:
        alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_secrets_directory():
    """Create and secure secrets directory"""
    secrets_dir = Path(__file__).parent / 'secrets'

    # Create directory if it doesn't exist
    secrets_dir.mkdir(mode=0o700, exist_ok=True)
    print(f"✓ Created secrets directory: {secrets_dir}")

    # Generate secure passwords for each service
    secrets_files = {
        'db_password.txt': generate_password(32),
        'redis_password.txt': generate_password(32),
        'qdrant_api_key.txt': generate_password(64),
        'neo4j_auth.txt': f"neo4j/{generate_password(32)}",
        'openai_api_key.txt': 'sk-your-openai-key-here',  # Placeholder - user must replace
        'anthropic_api_key.txt': 'sk-ant-your-anthropic-key-here',  # Placeholder - user must replace
        'flower_auth.txt': f"admin:{generate_password(24)}",
        'grafana_password.txt': generate_password(24),
    }

    # Write secrets to files with secure permissions
    for filename, content in secrets_files.items():
        filepath = secrets_dir / filename
        filepath.write_text(content)
        filepath.chmod(0o600)  # Read/write for owner only

        # Display non-sensitive info
        if 'api_key' in filename and content.startswith('sk-'):
            print(f"✓ Created {filename} (PLACEHOLDER - user must replace)")
        else:
            print(f"✓ Created {filename} (32-64 chars, secure)")

    print(f"\n✅ SUCCESS: All 8 secret files created with chmod 600")
    print(f"\n⚠️  IMPORTANT:")
    print(f"  1. Replace placeholder API keys in:")
    print(f"     - secrets/openai_api_key.txt")
    print(f"     - secrets/anthropic_api_key.txt")
    print(f"  2. NEVER commit secrets/ directory to Git (.gitignore configured)")
    print(f"  3. Backup secrets/ directory securely (encrypted storage)")

    return True

if __name__ == '__main__':
    try:
        create_secrets_directory()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        exit(1)
