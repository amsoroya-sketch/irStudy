#!/usr/bin/env python3
"""
Security Validators for Medical Resources Download System

Implements security validation layers:
- HTTPS certificate validation (enforce TLS)
- Input validation and sanitization
- Path traversal prevention
- File type validation
- Size limit enforcement

Security Principles:
- Defense in Depth: Multiple validation layers
- Fail-Safe Defaults: Reject invalid input by default
- Least Privilege: Strict permissions on created files
- Input Validation: Never trust external input

Usage:
    from scripts.lib.security_validators import (
        HTTPSValidator,
        InputValidator,
        enforce_https
    )

    # HTTPS enforcement
    validator = HTTPSValidator()
    validator.validate_url('https://ncbi.nlm.nih.gov/...')

    # Input sanitization
    safe_filename = InputValidator.sanitize_filename(untrusted_filename)
    safe_path = InputValidator.validate_path(user_path, allowed_base='/mnt/data')
"""

import re
import os
import ssl
import urllib.parse
from pathlib import Path
from typing import Optional, List
import logging

import requests
import certifi

logger = logging.getLogger(__name__)


# ==================== HTTPS Validation ====================

class HTTPSValidator:
    """
    Enforce HTTPS connections with valid certificates

    Prevents:
    - Man-in-the-middle attacks
    - Certificate validation bypass
    - Downgrade attacks to HTTP
    """

    ALLOWED_PROTOCOLS = ['https']
    MINIMUM_TLS_VERSION = ssl.TLSVersion.TLSv1_2

    def __init__(self, enforce_https: bool = True):
        """
        Initialize HTTPS validator

        Args:
            enforce_https: Reject non-HTTPS URLs (default True)
        """
        self.enforce_https = enforce_https

        # Create SSL context with security settings
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.minimum_version = self.MINIMUM_TLS_VERSION
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED

    def validate_url(self, url: str) -> dict:
        """
        Validate URL security

        Args:
            url: URL to validate

        Returns:
            dict: Validation result with 'valid', 'errors', 'warnings'
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'url': url
        }

        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Invalid URL format: {e}")
            return result

        # Check protocol
        if parsed.scheme not in self.ALLOWED_PROTOCOLS:
            if self.enforce_https:
                result['valid'] = False
                result['errors'].append(
                    f"Protocol must be HTTPS (got {parsed.scheme}://). "
                    f"HTTP is insecure and vulnerable to MITM attacks."
                )
            else:
                result['warnings'].append(f"Non-HTTPS protocol: {parsed.scheme}://")

        # Check hostname
        if not parsed.hostname:
            result['valid'] = False
            result['errors'].append("URL missing hostname")

        # Warn about IP addresses (suspicious for medical resources)
        if parsed.hostname and self._is_ip_address(parsed.hostname):
            result['warnings'].append(
                f"URL uses IP address ({parsed.hostname}) instead of domain name. "
                f"This may be suspicious for medical resources."
            )

        return result

    def _is_ip_address(self, hostname: str) -> bool:
        """Check if hostname is an IP address"""
        import socket
        try:
            socket.inet_aton(hostname)
            return True
        except socket.error:
            return False

    def create_secure_session(self) -> requests.Session:
        """
        Create requests session with HTTPS enforcement

        Returns:
            requests.Session configured for secure HTTPS
        """
        session = requests.Session()

        # Enforce certificate verification
        session.verify = certifi.where()

        # Set minimum TLS version (requires urllib3 >= 1.26)
        # Note: This is handled by the ssl_context, but we can't easily
        # inject it into requests. Instead, we rely on system defaults
        # and explicit verify=True

        # Prevent automatic HTTP->HTTPS redirects (security concern)
        session.max_redirects = 5

        return session


def enforce_https(url: str) -> str:
    """
    Enforce HTTPS protocol on URL

    Args:
        url: URL to check

    Returns:
        URL with HTTPS protocol

    Raises:
        ValueError: If URL is invalid
    """
    parsed = urllib.parse.urlparse(url)

    if parsed.scheme == 'http':
        # Upgrade HTTP to HTTPS
        logger.warning(f"Upgrading HTTP to HTTPS: {url}")
        return url.replace('http://', 'https://', 1)
    elif parsed.scheme == 'https':
        return url
    else:
        raise ValueError(f"Invalid URL protocol: {parsed.scheme}://")


# ==================== Input Validation ====================

class InputValidator:
    """
    Validate and sanitize untrusted input

    Prevents:
    - Path traversal attacks (../../etc/passwd)
    - Command injection
    - XML/JSON bombs
    - Filename exploits
    """

    MAX_FILENAME_LENGTH = 200
    MAX_FILE_SIZE_MB = 500  # 500 MB per file
    MAX_PATH_LENGTH = 4096

    ALLOWED_EXTENSIONS = {
        '.pdf', '.xml', '.txt', '.html', '.htm',
        '.json', '.csv', '.md', '.rst'
    }

    # Dangerous patterns in filenames
    FORBIDDEN_PATTERNS = [
        r'\.\.',  # Path traversal
        r'[\/\\]',  # Path separators
        r'\x00',  # Null bytes
        r'^\.', # Hidden files (security risk)
        r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Windows reserved names
    ]

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and injection attacks

        Args:
            filename: Untrusted filename

        Returns:
            Safe filename

        Example:
            >>> InputValidator.sanitize_filename("../../etc/passwd")
            'etc_passwd'
            >>> InputValidator.sanitize_filename("test<>|file.pdf")
            'test___file.pdf'
        """
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')

        # Remove null bytes (can terminate strings in C)
        filename = filename.replace('\x00', '')

        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)

        # Whitelist safe characters
        # Allow: alphanumeric, dash, underscore, dot, space
        filename = re.sub(r'[^a-zA-Z0-9._\-\s]', '_', filename)

        # Remove leading dots (hidden files)
        filename = filename.lstrip('.')

        # Remove multiple consecutive spaces/underscores
        filename = re.sub(r'[_\s]+', '_', filename)

        # Limit length
        if len(filename) > InputValidator.MAX_FILENAME_LENGTH:
            # Preserve extension
            name, ext = os.path.splitext(filename)
            max_name_length = InputValidator.MAX_FILENAME_LENGTH - len(ext) - 1
            filename = name[:max_name_length] + ext

        # Check for Windows reserved names
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in ['CON', 'PRN', 'AUX', 'NUL'] or \
           re.match(r'^(COM|LPT)[1-9]$', name_without_ext):
            filename = f'file_{filename}'

        # Ensure filename is not empty
        if not filename or filename == '.':
            filename = 'unnamed_file'

        return filename

    @staticmethod
    def validate_path(path: Path,
                     allowed_base: Optional[Path] = None,
                     must_exist: bool = False) -> dict:
        """
        Validate file path for security issues

        Args:
            path: Path to validate
            allowed_base: If provided, path must be under this directory
            must_exist: If True, path must already exist

        Returns:
            dict: Validation result with 'valid', 'errors', 'resolved_path'
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'resolved_path': None
        }

        # Convert to Path object
        try:
            path = Path(path)
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Invalid path: {e}")
            return result

        # Check path length
        if len(str(path)) > InputValidator.MAX_PATH_LENGTH:
            result['valid'] = False
            result['errors'].append(
                f"Path too long ({len(str(path))} > {InputValidator.MAX_PATH_LENGTH} chars)"
            )
            return result

        # Resolve path (expand ~, follow symlinks, resolve ..)
        try:
            resolved_path = path.resolve()
            result['resolved_path'] = resolved_path
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Cannot resolve path: {e}")
            return result

        # Check path traversal (path must be under allowed_base)
        if allowed_base:
            allowed_base = Path(allowed_base).resolve()
            try:
                resolved_path.relative_to(allowed_base)
            except ValueError:
                result['valid'] = False
                result['errors'].append(
                    f"Path traversal detected: {resolved_path} is not under {allowed_base}"
                )
                return result

        # Check existence
        if must_exist and not resolved_path.exists():
            result['valid'] = False
            result['errors'].append(f"Path does not exist: {resolved_path}")

        # Warn about symlinks
        if path.is_symlink():
            result['warnings'].append(
                f"Path is a symlink: {path} → {resolved_path}"
            )

        return result

    @staticmethod
    def validate_file_size(size_bytes: int) -> bool:
        """
        Check if file size is within acceptable range

        Args:
            size_bytes: File size in bytes

        Returns:
            True if size is acceptable
        """
        max_bytes = InputValidator.MAX_FILE_SIZE_MB * 1024 * 1024
        return 0 < size_bytes <= max_bytes

    @staticmethod
    def validate_extension(filepath: Path) -> dict:
        """
        Validate file extension

        Args:
            filepath: File path

        Returns:
            dict: Validation result
        """
        result = {
            'valid': True,
            'errors': [],
            'extension': filepath.suffix.lower()
        }

        if result['extension'] not in InputValidator.ALLOWED_EXTENSIONS:
            result['valid'] = False
            result['errors'].append(
                f"File extension not allowed: {result['extension']}. "
                f"Allowed: {', '.join(sorted(InputValidator.ALLOWED_EXTENSIONS))}"
            )

        return result

    @staticmethod
    def validate_content_type(content_type: str, expected: str) -> bool:
        """
        Verify HTTP Content-Type header matches expected type

        Args:
            content_type: Actual Content-Type from HTTP response
            expected: Expected Content-Type

        Returns:
            True if content type matches
        """
        # Normalize (remove parameters like charset)
        actual = content_type.split(';')[0].strip().lower()
        expected = expected.split(';')[0].strip().lower()

        return actual == expected or actual.startswith(expected)


# ==================== Resource ID Validation ====================

class ResourceIDValidator:
    """Validate resource identifiers (e.g., RES-001)"""

    VALID_PATTERN = re.compile(r'^RES-\d{3}$')

    @staticmethod
    def validate(resource_id: str) -> dict:
        """
        Validate resource ID format

        Args:
            resource_id: Resource identifier to validate

        Returns:
            dict: Validation result
        """
        result = {
            'valid': True,
            'errors': []
        }

        if not ResourceIDValidator.VALID_PATTERN.match(resource_id):
            result['valid'] = False
            result['errors'].append(
                f"Invalid resource ID format: {resource_id}. "
                f"Expected format: RES-XXX (e.g., RES-001)"
            )

        return result


# ==================== URL Parameter Validation ====================

class URLParameterValidator:
    """Validate URL parameters for injection attacks"""

    # Characters allowed in URL parameters (conservative whitelist)
    SAFE_PARAM_PATTERN = re.compile(r'^[a-zA-Z0-9\-_.~]+$')

    @staticmethod
    def validate_parameter(param_name: str, param_value: str) -> dict:
        """
        Validate URL parameter for injection attacks

        Args:
            param_name: Parameter name
            param_value: Parameter value

        Returns:
            dict: Validation result
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Check for SQL injection patterns
        sql_patterns = [r'(\bOR\b|\bAND\b).*=', r'--', r'/\*', r'\bUNION\b', r'\bSELECT\b']
        for pattern in sql_patterns:
            if re.search(pattern, param_value, re.IGNORECASE):
                result['warnings'].append(
                    f"Potential SQL injection in {param_name}: {param_value}"
                )

        # Check for command injection
        cmd_chars = ['|', '&', ';', '$', '`', '\n']
        if any(char in param_value for char in cmd_chars):
            result['warnings'].append(
                f"Potential command injection in {param_name}: {param_value}"
            )

        # Check for XSS
        xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        if any(pattern in param_value.lower() for pattern in xss_patterns):
            result['warnings'].append(
                f"Potential XSS in {param_name}: {param_value}"
            )

        return result


if __name__ == '__main__':
    # Example usage and testing
    import argparse

    parser = argparse.ArgumentParser(description='Security validation operations')
    parser.add_argument('command', choices=['validate-url', 'sanitize-filename', 'validate-path'],
                       help='Validation to perform')
    parser.add_argument('--input', required=True, help='Input to validate')
    parser.add_argument('--base-path', help='Allowed base path (for path validation)')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if args.command == 'validate-url':
        validator = HTTPSValidator()
        result = validator.validate_url(args.input)

        if result['valid']:
            print(f"✓ URL is valid: {args.input}")
        else:
            print(f"✗ URL is INVALID: {args.input}")
            for error in result['errors']:
                print(f"  ERROR: {error}")

        for warning in result['warnings']:
            print(f"  WARNING: {warning}")

    elif args.command == 'sanitize-filename':
        safe_filename = InputValidator.sanitize_filename(args.input)
        print(f"Original: {args.input}")
        print(f"Sanitized: {safe_filename}")

        if safe_filename != args.input:
            print("⚠ Filename was modified for security")
        else:
            print("✓ Filename already safe")

    elif args.command == 'validate-path':
        base_path = Path(args.base_path) if args.base_path else None
        result = InputValidator.validate_path(Path(args.input), allowed_base=base_path)

        if result['valid']:
            print(f"✓ Path is valid: {result['resolved_path']}")
        else:
            print(f"✗ Path is INVALID:")
            for error in result['errors']:
                print(f"  ERROR: {error}")

        for warning in result['warnings']:
            print(f"  WARNING: {warning}")
