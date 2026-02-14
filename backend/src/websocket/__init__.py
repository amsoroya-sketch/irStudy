"""
WebSocket Security Infrastructure for AMC Clinical Exam Platform

SECURITY:
- Zero-trust architecture
- JWT token validation with fingerprinting
- Session correlation with Redis
- Rate limiting and connection tracking
- Security event logging

Per PROJECT_CONSTRAINTS.md Section 3: NO hardcoded credentials
"""

from .authenticator import WebSocketAuthenticator
from .rate_limiter import RateLimiter
from .connection_tracker import ConnectionTracker

__all__ = [
    "WebSocketAuthenticator",
    "RateLimiter",
    "ConnectionTracker",
]
