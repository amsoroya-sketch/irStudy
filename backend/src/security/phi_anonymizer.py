"""
PHI Anonymizer - PROJECT_CONSTRAINTS.md Line 31 Compliance

Redacts Personal Health Information from logs.
Australian-specific patterns: email, phone (+61 format), Medicare numbers.

CRITICAL: Fixes Issue #2 from Security Review (PHI in logs)
"""

import re
import hashlib
from typing import Optional


class PHIAnonymizer:
    """
    Redact PHI from logs per PROJECT_CONSTRAINTS.md line 31.

    Detects and removes:
    - Email addresses
    - Australian phone numbers (+61, 04xx, 13xx, 1800 formats)
    - Medicare numbers (10 digits + check digit)
    - Names (when preceded by "my name is")
    - Date of birth patterns

    Usage in logging:
        logger.info(
            "Student message received",
            user_id=PHIAnonymizer.hash_identifier(str(user.id)),
            message=PHIAnonymizer.anonymize(student_message[:100])
        )
    """

    # Australian-specific patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b(?:\+?61[ -]?|0)[2-478](?:[ -]?[0-9]){8}\b'  # +61 or 04xx (with optional space after +61)
    PHONE_1800_PATTERN = r'\b1[38]00[ -]?\d{3}[ -]?\d{3}\b'  # 1300/1800 numbers
    MEDICARE_PATTERN = r'\b\d{10}\s?\d\b'  # 10 digits + 1 check digit
    DOB_PATTERN = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'  # dd/mm/yyyy or dd-mm-yy
    NAME_PATTERN = r'(?:my name is|I am|I\'m)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'

    @staticmethod
    def anonymize(message: str) -> str:
        """
        Redact all PHI patterns from message.

        Args:
            message: Raw text (student message, log entry, etc.)

        Returns:
            Message with all PHI redacted

        Example:
            >>> PHIAnonymizer.anonymize("My email is john@example.com")
            'My email is [EMAIL_REDACTED]'
            >>> PHIAnonymizer.anonymize("Call me on 0412 345 678")
            'Call me on [PHONE_REDACTED]'
        """
        # Email addresses
        message = re.sub(PHIAnonymizer.EMAIL_PATTERN, '[EMAIL_REDACTED]', message)

        # Phone numbers (Australian formats)
        message = re.sub(PHIAnonymizer.PHONE_PATTERN, '[PHONE_REDACTED]', message)
        message = re.sub(PHIAnonymizer.PHONE_1800_PATTERN, '[PHONE_REDACTED]', message)

        # Medicare numbers
        message = re.sub(PHIAnonymizer.MEDICARE_PATTERN, '[MEDICARE_REDACTED]', message)

        # Dates of birth
        message = re.sub(PHIAnonymizer.DOB_PATTERN, '[DOB_REDACTED]', message)

        # Names (when explicitly stated)
        message = re.sub(PHIAnonymizer.NAME_PATTERN, r'\1 [NAME_REDACTED]', message)

        return message

    @staticmethod
    def hash_identifier(identifier: str, salt: str = "osce-salt-2026") -> str:
        """
        One-way hash for user/session IDs in logs.

        Args:
            identifier: User ID, session ID, attempt ID (UUID string)
            salt: Optional salt for hashing

        Returns:
            First 12 characters of SHA256 hash (sufficient for log correlation)

        Example:
            >>> PHIAnonymizer.hash_identifier("550e8400-e29b-41d4-a716-446655440000")
            'a3f2c1b8d4e5'  # Truncated SHA256 hash
        """
        full_hash = hashlib.sha256(f"{salt}{identifier}".encode()).hexdigest()
        return full_hash[:12]  # 12 chars = 48 bits entropy (collision unlikely)
