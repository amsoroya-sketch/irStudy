"""
HTTPS Redirect Middleware
Enforces HTTPS in production and adds 9 mandatory security headers

SECURITY STANDARDS:
- HTTP → HTTPS redirect (301 permanent)
- 9 mandatory security headers (SHARED_INFRASTRUCTURE_SPEC.md Section 4.1)
- Content Security Policy (CSP) for XSS prevention
- Permissions Policy to restrict browser features

Reference: SHARED_INFRASTRUCTURE_SPEC.md Section 4 (HTTPS & Security Headers)
"""

import os
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Redirect all HTTP requests to HTTPS in production
    Add 9 mandatory security headers to all responses
    """
    
    def __init__(self, app: ASGIApp, enforce_https: bool = None):
        """
        Initialize HTTPS middleware
        
        Args:
            app: ASGI application
            enforce_https: Force HTTPS redirect (default: True in production)
        """
        super().__init__(app)
        
        # Auto-detect production environment
        env = os.getenv("ENV", "development")
        self.enforce_https = (
            enforce_https 
            if enforce_https is not None 
            else (env == "production")
        )
        
        if self.enforce_https:
            logger.info("HTTPS enforcement enabled")
        else:
            logger.info("HTTPS enforcement disabled (development mode)")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and add security headers
        
        Security: Transmission security (HIPAA § 164.312(e)(1))
        """
        # Redirect HTTP to HTTPS in production
        if self.enforce_https and request.url.scheme == "http":
            # Allow localhost and 127.0.0.1 for development
            if request.url.hostname not in ["localhost", "127.0.0.1"]:
                # Redirect to HTTPS
                https_url = request.url.replace(scheme="https")
                logger.warning(
                    f"HTTP request redirected to HTTPS: {request.url} -> {https_url}"
                )
                return RedirectResponse(url=str(https_url), status_code=301)
        
        # Process request
        response = await call_next(request)
        
        # Add 9 mandatory security headers
        self._add_security_headers(response, request)
        
        return response
    
    def _add_security_headers(self, response, request: Request):
        """
        Add 9 mandatory security headers to response
        
        Headers (SHARED_INFRASTRUCTURE_SPEC.md Section 4.1):
        1. Strict-Transport-Security (HSTS)
        2. X-Content-Type-Options
        3. X-Frame-Options
        4. X-XSS-Protection
        5. Content-Security-Policy
        6. Referrer-Policy
        7. Permissions-Policy
        8. Cache-Control
        9. Pragma
        """
        # 1. HTTP Strict Transport Security (HSTS)
        # Force HTTPS for 1 year, including subdomains
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        
        # 2. Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 3. Prevent clickjacking (deny iframe embedding)
        response.headers["X-Frame-Options"] = "DENY"
        
        # 4. Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # 5. Content Security Policy
        # - default-src 'self': Only load resources from same origin
        # - script-src 'self': Only allow scripts from same origin
        # - style-src 'self' 'unsafe-inline': Allow inline styles (for React)
        # - img-src 'self' data: https:: Allow images from same origin, data URIs, HTTPS
        # - font-src 'self': Only allow fonts from same origin
        # - connect-src 'self' wss://irstudy.com: Allow WebSocket for OSCE
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self' wss://irstudy.com"
        )
        
        # 6. Referrer Policy (don't leak URLs in referrer)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 7. Permissions Policy (restrict browser features)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        
        # 8. Cache Control (no caching of sensitive data)
        # Apply to all API endpoints
        if "/api/v1/" in request.url.path:
            response.headers["Cache-Control"] = "no-store, max-age=0"
        
        # 9. Pragma (legacy cache control)
        if "/api/v1/" in request.url.path:
            response.headers["Pragma"] = "no-cache"


# Convenience function for FastAPI app registration
def add_https_middleware(app, enforce_https: bool = None):
    """
    Add HTTPS redirect middleware to FastAPI app
    
    Usage:
        from middleware.https_redirect import add_https_middleware
        
        app = FastAPI()
        add_https_middleware(app)  # Auto-detect production
        # or
        add_https_middleware(app, enforce_https=True)  # Force HTTPS
    """
    app.add_middleware(HTTPSRedirectMiddleware, enforce_https=enforce_https)
    logger.info("HTTPS redirect middleware registered")
