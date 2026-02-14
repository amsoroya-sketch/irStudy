"""
Security module for AMC Clinical Exam Simulation

Exports:
- ConversationEncryptionService: GDPR Article 32 encryption for conversations
- SecurityEvent: Dataclass for security event structure
- SecurityEventLogger: Main logging class with Vault integration
"""

# Import encryption service (no external dependencies)
from .encryption import ConversationEncryptionService

# Import security events (requires redis - optional)
try:
    from .events import SecurityEvent, SecurityEventLogger
    __all__ = ["ConversationEncryptionService", "SecurityEvent", "SecurityEventLogger"]
except ImportError:
    # Redis not installed - events module unavailable
    __all__ = ["ConversationEncryptionService"]
