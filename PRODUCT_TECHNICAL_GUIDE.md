# Technical Implementation Guide - Secure AMC Prep Platform

## 1. Project Structure

```
amc-prep-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Pydantic settings
│   │   ├── database.py             # SQLAlchemy setup
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py     # JWT validation
│   │   │   ├── router.py           # Login/register endpoints
│   │   │   └── security.py         # Password hashing, JWT
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── schemas.py          # Pydantic schemas
│   │   │   └── service.py          # Business logic
│   │   ├── mcqs/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   └── service.py
│   │   ├── subscriptions/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   └── stripe_webhooks.py
│   │   ├── ai_tutor/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── rag_service.py      # Your existing Qdrant client
│   │   └── progress/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       └── router.py
│   ├── tests/
│   ├── alembic/                    # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── web/                        # Next.js 14
│   ├── mobile/                     # React Native
│   └── shared/                     # Shared types, utils
└── infrastructure/
    ├── docker-compose.yml
    ├── kubernetes/
    └── terraform/                   # AWS/GCP infrastructure
```

---

## 2. Secure FastAPI Backend

### 2.1 Configuration (Secure by Default)

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from pydantic import SecretStr, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Secure configuration management"""
    
    # Application
    APP_NAME: str = "AMC Prep Platform"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Security
    SECRET_KEY: SecretStr  # openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_FREE: int = 100      # requests per hour
    RATE_LIMIT_PRO: int = 1000
    RATE_LIMIT_ULTIMATE: int = 5000
    
    # Database
    DATABASE_URL: SecretStr
    DATABASE_POOL_SIZE: int = 20
    
    # Redis (Caching & Rate Limiting)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: SecretStr | None = None
    
    # Stripe
    STRIPE_SECRET_KEY: SecretStr
    STRIPE_WEBHOOK_SECRET: SecretStr
    STRIPE_PRICE_PRO_MONTHLY: str
    STRIPE_PRICE_PRO_YEARLY: str
    STRIPE_PRICE_ULTIMATE_MONTHLY: str
    STRIPE_PRICE_ULTIMATE_YEARLY: str
    
    # External APIs
    ANTHROPIC_API_KEY: SecretStr | None = None  # For AI Tutor (optional)
    
    # Content Protection
    MAX_QUESTIONS_PER_MINUTE: int = 10
    ENABLE_WATERMARKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Security headers middleware
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.stripe.com;"
        )
        
        # HSTS (only in production)
        if not get_settings().DEBUG:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(self)"
        )
        
        return response
```

### 2.2 Authentication System

```python
# backend/app/auth/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # Enforce strong passwords
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    settings = get_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY.get_secret_value(), 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict):
    """Long-lived token for getting new access tokens"""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 2.3 Rate Limiting & Tier Enforcement

```python
# backend/app/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis import Redis
from functools import wraps
import time

from app.config import get_settings
from app.auth.security import decode_token

security = HTTPBearer()
redis_client = Redis.from_url(get_settings().REDIS_URL, decode_responses=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Validate JWT and return user info"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Check if token is revoked (user logged out)
    jti = payload.get("jti")
    if jti and redis_client.get(f"revoked_token:{jti}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "subscription_tier": payload.get("tier", "free"),
        "is_active": payload.get("is_active", True)
    }


async def get_current_active_user(
    user: dict = Depends(get_current_user)
) -> dict:
    """Ensure user account is active"""
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    return user


def require_subscription(tiers: list[str]):
    """Decorator to enforce subscription tiers"""
    async def checker(user: dict = Depends(get_current_active_user)):
        if user["subscription_tier"] not in tiers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires one of: {', '.join(tiers)}"
            )
        return user
    return Depends(checker)


def rate_limit_by_tier(request: Request, user: dict = Depends(get_current_user)):
    """Rate limiting based on subscription tier"""
    settings = get_settings()
    tier = user.get("subscription_tier", "free")
    user_id = user["user_id"]
    
    limits = {
        "free": settings.RATE_LIMIT_FREE,
        "pro": settings.RATE_LIMIT_PRO,
        "ultimate": settings.RATE_LIMIT_ULTIMATE
    }
    
    limit = limits.get(tier, settings.RATE_LIMIT_FREE)
    key = f"rate_limit:{user_id}:{int(time.time() // 3600)}"  # Per hour
    
    current = redis_client.get(key)
    if current and int(current) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Limit: {limit}/hour"
        )
    
    redis_client.incr(key)
    redis_client.expire(key, 3600)


# Premium feature decorator
def premium_feature(feature_name: str):
    """Track premium feature usage"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Log feature usage for analytics
            user = kwargs.get("user")
            if user:
                redis_client.lpush(
                    f"feature_usage:{feature_name}",
                    f"{user['user_id']}:{time.time()}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 2.4 MCQ Content Protection

```python
# backend/app/mcqs/service.py
import random
from typing import List, Dict
from fastapi import HTTPException

from app.config import get_settings


class MCQService:
    """Service for retrieving MCQs with content protection"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def get_questions(
        self,
        user_id: str,
        specialty: str,
        count: int = 10,
        shuffle_options: bool = True
    ) -> List[Dict]:
        """
        Get questions with:
        - Rate limiting
        - Option shuffling (prevent answer memorization by position)
        - Invisible watermarking
        """
        
        # Check rate limit
        self._check_content_rate_limit(user_id)
        
        # Fetch from database (mock - replace with actual query)
        questions = self._fetch_from_db(specialty, count)
        
        # Shuffle options and watermark
        processed = []
        for q in questions:
            q = self._shuffle_options(q) if shuffle_options else q
            q = self._add_watermark(q, user_id)
            processed.append(q)
        
        return processed
    
    def _check_content_rate_limit(self, user_id: str):
        """Prevent bulk scraping"""
        key = f"content_rate:{user_id}:{int(time.time() // 60)}"
        current = redis_client.get(key) or 0
        
        if int(current) >= self.settings.MAX_QUESTIONS_PER_MINUTE:
            raise HTTPException(
                status_code=429,
                detail="Too many questions requested. Please slow down."
            )
        
        redis_client.incr(key)
        redis_client.expire(key, 60)
    
    def _shuffle_options(self, question: Dict) -> Dict:
        """Shuffle options while tracking correct answer"""
        options = question["options"]
        correct = question["correct_answer"]
        
        # Create shuffled mapping
        keys = list(options.keys())
        shuffled_keys = keys.copy()
        random.shuffle(shuffled_keys)
        
        # Build new options dict
        new_options = {}
        correct_new = None
        for old_key, new_key in zip(keys, shuffled_keys):
            new_options[new_key] = options[old_key]
            if old_key == correct:
                correct_new = new_key
        
        question["options"] = new_options
        question["correct_answer"] = correct_new
        question["_shuffled"] = True  # Flag for frontend
        
        return question
    
    def _add_watermark(self, question: Dict, user_id: str) -> Dict:
        """
        Add invisible watermark to identify source if leaked.
        Uses steganographic technique in whitespace.
        """
        if not self.settings.ENABLE_WATERMARKING:
            return question
        
        # Embed user ID in HTML whitespace
        watermark = f"<!-- u:{user_id[:8]} -->"
        question["scenario"] = question.get("scenario", "") + watermark
        
        return question
```

### 2.5 Subscription Management with Stripe

```python
# backend/app/subscriptions/stripe_webhooks.py
from fastapi import APIRouter, Request, HTTPException
import stripe
from app.config import get_settings

router = APIRouter()
settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY.get_secret_value()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events securely"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET.get_secret_value()
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event["type"] == "checkout.session.completed":
        await handle_checkout_completed(event["data"]["object"])
    
    elif event["type"] == "invoice.payment_failed":
        await handle_payment_failed(event["data"]["object"])
    
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_cancelled(event["data"]["object"])
    
    return {"status": "success"}


async def handle_checkout_completed(session: dict):
    """Activate subscription after successful payment"""
    customer_id = session["customer"]
    subscription_id = session["subscription"]
    
    # Get user by Stripe customer ID
    user = await get_user_by_stripe_customer(customer_id)
    
    # Update subscription in database
    await update_user_subscription(
        user_id=user["id"],
        stripe_subscription_id=subscription_id,
        tier=map_price_to_tier(session["line_items"]["data"][0]["price"]["id"]),
        status="active",
        current_period_end=session["subscription_details"]["current_period_end"]
    )
    
    # Send welcome email
    await send_subscription_confirmation(user["email"])


async def handle_payment_failed(invoice: dict):
    """Gracefully handle failed payments"""
    customer_id = invoice["customer"]
    user = await get_user_by_stripe_customer(customer_id)
    
    # Send dunning email
    await send_payment_failed_email(user["email"], invoice["attempt_count"])
    
    # Downgrade if multiple failures
    if invoice["attempt_count"] >= 3:
        await downgrade_to_free(user["id"])
```

---

## 3. Database Schema (PostgreSQL)

```sql
-- Users table with subscription info
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL for OAuth users
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'ultimate')),
    subscription_status VARCHAR(20) DEFAULT 'inactive' CHECK (subscription_status IN ('active', 'inactive', 'cancelled', 'past_due')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    subscription_current_period_end TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),  -- Encrypted TOTP secret
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Progress tracking
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    specialty VARCHAR(50) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent_seconds INTEGER,
    user_answer VARCHAR(10),
    correct_answer VARCHAR(10),
    session_id UUID,  -- Group questions by study session
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, question_id, created_at)  -- Allow multiple attempts
);

-- Study sessions for analytics
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    questions_answered INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    specialty_focus VARCHAR(50),
    device_type VARCHAR(20)  -- web, ios, android
);

-- Spaced repetition tracking
CREATE TABLE srs_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    interval_days INTEGER DEFAULT 1,
    ease_factor FLOAT DEFAULT 2.5,
    repetitions INTEGER DEFAULT 0,
    next_review_date DATE NOT NULL,
    last_reviewed_at TIMESTAMP,
    
    UNIQUE(user_id, question_id)
);

-- AI Tutor conversations
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    sources JSONB,  -- RAG citations
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for security
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- login, logout, mcq_view, subscription_change
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX idx_progress_user_specialty ON user_progress(user_id, specialty);
CREATE INDEX idx_srs_next_review ON srs_cards(user_id, next_review_date);
CREATE INDEX idx_audit_user_action ON audit_log(user_id, action, created_at);
```

---

## 4. Frontend Security

### 4.1 Next.js Web App

```typescript
// frontend/web/lib/auth.ts
import { jwtVerify } from 'jose';

const JWT_SECRET = new TextEncoder().encode(process.env.JWT_SECRET);

export async function verifyToken(token: string) {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    return payload;
  } catch {
    return null;
  }
}

// middleware.ts - Protect routes
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;
  
  // Public routes
  const publicPaths = ['/login', '/register', '/forgot-password', '/'];
  if (publicPaths.includes(request.nextUrl.pathname)) {
    return NextResponse.next();
  }
  
  // Check auth
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  // Add security headers
  const response = NextResponse.next();
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  return response;
}
```

### 4.2 Mobile App Security (React Native)

```typescript
// frontend/mobile/src/utils/security.ts
import * as Keychain from 'react-native-keychain';
import { Platform } from 'react-native';

export class SecureStorage {
  static async setToken(token: string, type: 'access' | 'refresh') {
    await Keychain.setGenericPassword(
      `${type}_token`,
      token,
      {
        service: `com.amcprep.${type}`,
        accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED,
      }
    );
  }
  
  static async getToken(type: 'access' | 'refresh'): Promise<string | null> {
    const credentials = await Keychain.getGenericPassword({
      service: `com.amcprep.${type}`,
    });
    return credentials ? credentials.password : null;
  }
  
  static async clearTokens() {
    await Keychain.resetGenericPassword({ service: 'com.amcprep.access' });
    await Keychain.resetGenericPassword({ service: 'com.amcprep.refresh' });
  }
}

// Certificate pinning for API calls
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Add auth header to all requests
apiClient.interceptors.request.use(async (config) => {
  const token = await SecureStorage.getToken('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 - refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = await SecureStorage.getToken('refresh');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          await SecureStorage.setToken(response.data.access_token, 'access');
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          
          return apiClient(originalRequest);
        } catch {
          // Refresh failed, logout
          await SecureStorage.clearTokens();
          // Navigate to login
        }
      }
    }
    
    return Promise.reject(error);
  }
);
```

---

## 5. Environment Configuration

```bash
# .env.example - NEVER commit the real .env file

# Application
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=your-256-bit-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@localhost/amc_prep

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant (Vector DB)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=optional-api-key

# Stripe (Payment)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO_MONTHLY=price_...
STRIPE_PRICE_PRO_YEARLY=price_...
STRIPE_PRICE_ULTIMATE_MONTHLY=price_...
STRIPE_PRICE_ULTIMATE_YEARLY=price_...

# Email (SendGrid/AWS SES)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxx
FROM_EMAIL=noreply@amcprep.com

# Monitoring (Sentry)
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# AI (Optional - for AI Tutor)
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 6. Deployment Checklist

### Security Checklist Before Launch

- [ ] All secrets in environment variables (not in code)
- [ ] Database credentials rotated
- [ ] Stripe webhooks verified with signature
- [ ] Rate limiting enabled
- [ ] CORS configured for production domains only
- [ ] HTTPS enforced (HSTS headers)
- [ ] Security headers middleware active
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (output encoding, CSP)
- [ ] Dependency audit (`pip-audit`, `npm audit`)
- [ ] Penetration testing (OWASP ZAP)
- [ ] Log aggregation and monitoring
- [ ] Incident response plan documented
- [ ] GDPR/CCPA compliance review
- [ ] Data retention policy implemented
- [ ] Backup encryption verified

---

## 7. Monitoring & Alerting

```python
# backend/app/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Metrics
mcq_requests = Counter('mcq_requests_total', 'Total MCQ requests', ['tier', 'specialty'])
auth_failures = Counter('auth_failures_total', 'Auth failures', ['reason'])
api_latency = Histogram('api_request_duration_seconds', 'API latency', ['endpoint'])
active_subscriptions = Gauge('active_subscriptions', 'Active subs', ['tier'])


def monitor_endpoint(endpoint_name):
    """Decorator to track API metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                api_latency.labels(endpoint=endpoint_name).observe(duration)
        return wrapper
    return decorator
```

---

**Document Version:** 1.0  
**Security Review Date:** Before production deployment  
**Next Audit:** 90 days post-launch
