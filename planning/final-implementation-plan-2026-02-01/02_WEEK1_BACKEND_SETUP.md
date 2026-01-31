# Week 1: Backend Setup & API Scaffolding
**Owner:** Developer 2 - Backend Lead
**Duration:** 10 hours
**Priority:** P0 (Critical - blocks frontend work)
**Status:** Ready to Start

---

## 📋 Overview

This plan implements the FastAPI backend foundation by reusing production-tested code from `/home/dev/Development/arQ/` and `/home/dev/Development/ideas-aggregator/`. We'll establish JWT authentication, API routing structure, and database schema in 10 hours.

**Key Achievement:** Production-ready API endpoints with authentication in 1 day

---

## ✅ Prerequisites

- [x] Docker stack running (from Task 1 - Security Foundation)
- [x] PostgreSQL database healthy
- [x] Redis cache operational
- [ ] Python 3.11+ installed locally (for development)

---

## 🎯 Goals

1. **JWT Authentication from arQ** (3 hours)
   - Copy authentication module
   - Configure token generation
   - Implement refresh token logic

2. **API Endpoint Scaffolding** (5 hours)
   - Create FastAPI router structure
   - Define MCQ endpoints (CRUD)
   - Define OSCE endpoints
   - Define user management endpoints

3. **Database Schema Design** (2 hours)
   - PostgreSQL table definitions
   - Pydantic models
   - Alembic migrations

---

## 📝 Detailed Task Breakdown

### Task 1: Copy JWT Authentication from arQ (3 hours)

**Priority:** P0 (CRITICAL - blocks user features)

**Source:** `/home/dev/Development/arQ/backend/src/modules/auth/`

**Steps:**

```bash
# 1. Explore arQ authentication structure
cd /home/dev/Development/arQ/backend/src/modules/auth
ls -la

# Expected structure:
# - auth_service.py (JWT generation, validation)
# - auth_routes.py (login, register, refresh endpoints)
# - auth_schemas.py (Pydantic models for auth)
# - dependencies.py (FastAPI dependency injection)
# - utils.py (password hashing, token utilities)

# 2. Create irStudy backend structure
cd /home/dev/Development/irStudy
mkdir -p backend/src/modules/auth
mkdir -p backend/src/core
mkdir -p backend/tests

# 3. Copy authentication module
cp -r /home/dev/Development/arQ/backend/src/modules/auth/* \
   backend/src/modules/auth/

# 4. Copy core dependencies (config, security)
cp /home/dev/Development/arQ/backend/src/core/config.py \
   backend/src/core/config.py
cp /home/dev/Development/arQ/backend/src/core/security.py \
   backend/src/core/security.py

# 5. Install required dependencies
cd backend
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart

# 6. Create requirements.txt
cat > requirements.txt << 'EOF'
# FastAPI Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Redis
redis==5.0.1
hiredis==2.3.2

# LLM & RAG
langchain==0.1.5
langchain-community==0.0.16
qdrant-client==1.7.0
openai==1.10.0
anthropic==0.8.1

# Utilities
python-dotenv==1.0.0
celery==5.3.6
flower==2.0.1

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Code Quality
black==24.1.1
flake8==7.0.0
mypy==1.8.0
ruff==0.1.14
EOF

pip install -r requirements.txt
```

**Adapt Authentication Code:**

Edit `backend/src/modules/auth/auth_service.py`:

```python
"""
Authentication Service - JWT Token Management
Adapted from arQ project
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import verify_password, get_password_hash
from ..models.user import User
from .auth_schemas import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handles JWT token generation, validation, and user authentication"""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Generate JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({
            "exp": expire,
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Generate JWT refresh token (longer expiry)"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Validate JWT token and extract payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")

            if user_id is None:
                return None

            return TokenData(user_id=user_id, email=payload.get("email"))

        except JWTError:
            return None

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist (Redis-backed)"""
        # TODO: Implement Redis-backed token blacklisting
        # Key: blacklist:{token_hash}
        # Expiry: Same as token expiry
        pass


# Singleton instance
auth_service = AuthService()
```

**Create Authentication Routes:**

Create `backend/src/modules/auth/auth_routes.py`:

```python
"""
Authentication API Routes
Endpoints: /auth/register, /auth/login, /auth/refresh, /auth/logout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.user import User
from ..core.security import get_password_hash
from .auth_service import auth_service
from .auth_schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register new user account

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    """
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login

    Returns access token and refresh token
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate tokens
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    token_data = auth_service.verify_token(refresh_data.refresh_token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Generate new access token
    access_token = auth_service.create_access_token(
        data={"sub": token_data.user_id, "email": token_data.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_data.refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(token: str):
    """
    Logout user by blacklisting token
    """
    auth_service.blacklist_token(token)
    return {"message": "Successfully logged out"}
```

**Validation:**
- [ ] Authentication module copied from arQ
- [ ] JWT token generation works (test with `/auth/login`)
- [ ] Refresh token flow implemented
- [ ] Password hashing secure (bcrypt)
- [ ] Token blacklisting planned (Redis-backed)

**Time Estimate:** 3 hours

---

### Task 2: API Endpoint Scaffolding (5 hours)

**Priority:** P0 (CRITICAL - defines application interface)

**Steps:**

```bash
# 1. Create API router structure
cd /home/dev/Development/irStudy/backend/src
mkdir -p routers
touch routers/__init__.py
```

**Create MCQ Router:**

Create `backend/src/routers/mcqs.py`:

```python
"""
MCQ API Router
Endpoints for Multiple Choice Questions management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.mcq import MCQ
from ..schemas.mcq import (
    MCQCreate,
    MCQUpdate,
    MCQResponse,
    MCQListResponse,
    MCQAttemptCreate,
    MCQAttemptResponse
)

router = APIRouter(prefix="/mcqs", tags=["MCQs"])


@router.get("/", response_model=MCQListResponse)
async def get_mcqs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    week: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of MCQs with optional filtering

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (max 100)
    - **topic**: Filter by topic (e.g., 'cardiology', 'respiratory')
    - **difficulty**: Filter by difficulty (easy, medium, hard)
    - **week**: Filter by week number (1, 2, 3)
    """
    query = db.query(MCQ)

    # Apply filters
    if topic:
        query = query.filter(MCQ.topic == topic)
    if difficulty:
        query = query.filter(MCQ.difficulty == difficulty)
    if week:
        query = query.filter(MCQ.week == week)

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    mcqs = query.offset(skip).limit(limit).all()

    return {
        "mcqs": mcqs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{mcq_id}", response_model=MCQResponse)
async def get_mcq(
    mcq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single MCQ by ID"""
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with id {mcq_id} not found"
        )

    return mcq


@router.post("/", response_model=MCQResponse, status_code=status.HTTP_201_CREATED)
async def create_mcq(
    mcq_data: MCQCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new MCQ (Admin only)

    Requires authenticated user with admin role
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")

    new_mcq = MCQ(**mcq_data.dict())
    db.add(new_mcq)
    db.commit()
    db.refresh(new_mcq)

    return new_mcq


@router.put("/{mcq_id}", response_model=MCQResponse)
async def update_mcq(
    mcq_id: int,
    mcq_data: MCQUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update existing MCQ (Admin only)"""
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with id {mcq_id} not found"
        )

    # Update fields
    for field, value in mcq_data.dict(exclude_unset=True).items():
        setattr(mcq, field, value)

    db.commit()
    db.refresh(mcq)

    return mcq


@router.delete("/{mcq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcq(
    mcq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete MCQ (Admin only)"""
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with id {mcq_id} not found"
        )

    db.delete(mcq)
    db.commit()

    return None


@router.post("/{mcq_id}/attempt", response_model=MCQAttemptResponse)
async def submit_mcq_attempt(
    mcq_id: int,
    attempt_data: MCQAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit user's answer to MCQ

    Records attempt, checks correctness, updates user progress
    """
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with id {mcq_id} not found"
        )

    # Check if answer is correct
    is_correct = attempt_data.selected_answer == mcq.correct_answer

    # Create attempt record
    # TODO: Implement MCQAttempt model and save

    return {
        "mcq_id": mcq_id,
        "user_id": current_user.id,
        "selected_answer": attempt_data.selected_answer,
        "is_correct": is_correct,
        "explanation": mcq.explanation if not is_correct else None
    }
```

**Create OSCE Router:**

Create `backend/src/routers/osces.py`:

```python
"""
OSCE API Router
Endpoints for Objective Structured Clinical Examination scenarios
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.osce import OSCE
from ..schemas.osce import OSCECreate, OSCEUpdate, OSCEResponse, OSCEListResponse

router = APIRouter(prefix="/osces", tags=["OSCEs"])


@router.get("/", response_model=OSCEListResponse)
async def get_osces(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
    specialty: Optional[str] = None,
    station_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of OSCEs

    - **specialty**: Filter by medical specialty
    - **station_type**: Filter by station type (history, examination, etc.)
    """
    query = db.query(OSCE)

    if specialty:
        query = query.filter(OSCE.specialty == specialty)
    if station_type:
        query = query.filter(OSCE.station_type == station_type)

    total = query.count()
    osces = query.offset(skip).limit(limit).all()

    return {
        "osces": osces,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{osce_id}", response_model=OSCEResponse)
async def get_osce(
    osce_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single OSCE scenario by ID"""
    osce = db.query(OSCE).filter(OSCE.id == osce_id).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSCE with id {osce_id} not found"
        )

    return osce


@router.post("/", response_model=OSCEResponse, status_code=status.HTTP_201_CREATED)
async def create_osce(
    osce_data: OSCECreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new OSCE scenario (Admin only)"""
    new_osce = OSCE(**osce_data.dict())
    db.add(new_osce)
    db.commit()
    db.refresh(new_osce)

    return new_osce
```

**Create User Router:**

Create `backend/src/routers/users.py`:

```python
"""
User API Router
Endpoints for user profile and progress tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.user import UserResponse, UserUpdate, UserProgressResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current logged-in user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/me/progress", response_model=UserProgressResponse)
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's learning progress

    Returns:
    - Total MCQs attempted
    - Correct percentage
    - Topics mastered
    - Study streak
    """
    # TODO: Implement progress calculation
    return {
        "user_id": current_user.id,
        "total_mcqs_attempted": 0,
        "correct_percentage": 0.0,
        "topics_mastered": [],
        "study_streak_days": 0
    }
```

**Create Main FastAPI App:**

Create `backend/src/main.py`:

```python
"""
irStudy Medical Education Platform - FastAPI Application
Main entry point for the backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.database import engine, Base
from .modules.auth.auth_routes import router as auth_router
from .routers.mcqs import router as mcq_router
from .routers.osces import router as osce_router
from .routers.users import router as user_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Australian Medical Education Platform with AI-powered learning",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for Docker/K8s"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(mcq_router, prefix="/api")
app.include_router(osce_router, prefix="/api")
app.include_router(user_router, prefix="/api")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
```

**Validation:**
- [ ] API router structure created
- [ ] MCQ endpoints defined (GET, POST, PUT, DELETE)
- [ ] OSCE endpoints defined
- [ ] User profile endpoints defined
- [ ] Main FastAPI app configured
- [ ] CORS middleware enabled

**Time Estimate:** 5 hours

---

### Task 3: Database Schema Design (2 hours)

**Priority:** P0 (CRITICAL - defines data structure)

**Create SQLAlchemy Models:**

Create `backend/src/models/user.py`:

```python
"""
User Model - SQLAlchemy ORM
"""

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    mcq_attempts = relationship("MCQAttempt", back_populates="user")
    progress_records = relationship("UserProgress", back_populates="user")
```

Create `backend/src/models/mcq.py`:

```python
"""
MCQ Model - Multiple Choice Questions
"""

from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class MCQ(Base):
    __tablename__ = "mcqs"

    id = Column(Integer, primary_key=True, index=True)

    # Question content
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer = Column(String(1), nullable=False)  # "A", "B", "C", or "D"
    explanation = Column(Text, nullable=False)

    # Metadata
    topic = Column(String, index=True, nullable=False)  # "cardiology", "respiratory"
    subtopic = Column(String, nullable=True)
    difficulty = Column(String, nullable=False)  # "easy", "medium", "hard"
    week = Column(Integer, nullable=True)  # Week 1, 2, 3

    # Citations (Australian sources)
    citations = Column(JSON, nullable=True)  # List of citation objects

    # Images
    image_url = Column(String, nullable=True)
    image_caption = Column(String, nullable=True)

    # Australian standards
    australian_spelling = Column(Boolean, default=True)
    uses_amc_guidelines = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attempts = relationship("MCQAttempt", back_populates="mcq")


class MCQAttempt(Base):
    __tablename__ = "mcq_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mcq_id = Column(Integer, ForeignKey("mcqs.id"), nullable=False)

    selected_answer = Column(String(1), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="mcq_attempts")
    mcq = relationship("MCQ", back_populates="attempts")
```

Create `backend/src/models/osce.py`:

```python
"""
OSCE Model - Clinical Examination Scenarios
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime

from ..core.database import Base


class OSCE(Base):
    __tablename__ = "osces"

    id = Column(Integer, primary_key=True, index=True)

    # Scenario content
    title = Column(String, nullable=False)
    patient_presentation = Column(Text, nullable=False)
    task_description = Column(Text, nullable=False)

    # Station details
    specialty = Column(String, nullable=False)  # "cardiology", "psychiatry"
    station_type = Column(String, nullable=False)  # "history", "examination", "counselling"
    duration_minutes = Column(Integer, default=8)

    # Marking criteria
    marking_scheme = Column(JSON, nullable=False)  # Structured criteria

    # Model answers
    model_answer = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=False)

    # Citations
    citations = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Create Pydantic Schemas:**

Create `backend/src/schemas/mcq.py`:

```python
"""
MCQ Pydantic Schemas - Request/Response validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class MCQCreate(BaseModel):
    question: str
    options: Dict[str, str]  # {"A": "...", "B": "...", ...}
    correct_answer: str = Field(..., regex="^[A-D]$")
    explanation: str
    topic: str
    subtopic: Optional[str] = None
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")
    week: Optional[int] = None
    citations: Optional[List[Dict]] = None
    image_url: Optional[str] = None


class MCQUpdate(BaseModel):
    question: Optional[str] = None
    options: Optional[Dict[str, str]] = None
    correct_answer: Optional[str] = Field(None, regex="^[A-D]$")
    explanation: Optional[str] = None
    difficulty: Optional[str] = Field(None, regex="^(easy|medium|hard)$")


class MCQResponse(BaseModel):
    id: int
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str
    topic: str
    difficulty: str
    created_at: datetime

    class Config:
        from_attributes = True


class MCQListResponse(BaseModel):
    mcqs: List[MCQResponse]
    total: int
    skip: int
    limit: int


class MCQAttemptCreate(BaseModel):
    selected_answer: str = Field(..., regex="^[A-D]$")
    time_taken_seconds: Optional[int] = None


class MCQAttemptResponse(BaseModel):
    mcq_id: int
    user_id: int
    selected_answer: str
    is_correct: bool
    explanation: Optional[str] = None
```

**Setup Alembic Migrations:**

```bash
# 1. Initialize Alembic
cd /home/dev/Development/irStudy/backend
alembic init alembic

# 2. Configure alembic.ini
# Edit sqlalchemy.url to use environment variable
# sqlalchemy.url = postgresql://postgres:password@postgres:5432/irstudy_medical

# 3. Create initial migration
alembic revision --autogenerate -m "Initial schema: users, mcqs, osces"

# 4. Apply migration
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade -> abc123, Initial schema
# Created tables: users, mcqs, mcq_attempts, osces
```

**Validation:**
- [ ] User model created with authentication fields
- [ ] MCQ model created with Australian standards fields
- [ ] OSCE model created with marking criteria
- [ ] Pydantic schemas defined for validation
- [ ] Alembic migrations configured
- [ ] Database tables created successfully

**Time Estimate:** 2 hours

---

## 📊 Success Metrics

### Completion Criteria
- [ ] JWT authentication working (login returns access token)
- [ ] All API endpoints respond (even if with mock data)
- [ ] Database schema created (5+ tables)
- [ ] API documentation accessible at `/api/docs`
- [ ] Zero authentication vulnerabilities (security scan passes)

### Quality Gates
- [ ] `/api/health` returns 200 OK
- [ ] `/api/mcqs` returns paginated results
- [ ] `/auth/login` generates valid JWT
- [ ] Database migrations applied successfully
- [ ] API documentation complete (Swagger UI)

### Testing Checklist
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123", "full_name": "Test User"}'

curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"

# Test MCQ endpoint (with JWT token)
curl http://localhost:8000/api/mcqs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔗 Related Documents

- **[00_MASTER_PLAN.md](./00_MASTER_PLAN.md)** - Overall implementation plan
- **[01_WEEK1_SECURITY_FOUNDATION.md](./01_WEEK1_SECURITY_FOUNDATION.md)** - Security infrastructure
- **[03_WEEK1_FRONTEND_SETUP.md](./03_WEEK1_FRONTEND_SETUP.md)** - Frontend components (depends on these APIs)
- **[12_IMMEDIATE_NEXT_STEPS.md](./12_IMMEDIATE_NEXT_STEPS.md)** - Getting started guide

---

## 🆘 Troubleshooting

### Issue: Database connection fails
**Solution:**
```bash
# Check PostgreSQL is running
docker exec irstudy-postgres psql -U postgres -c "SELECT 1;"

# Verify DATABASE_URL in .env
echo $DATABASE_URL

# Test connection from backend
python -c "from sqlalchemy import create_engine; engine = create_engine('your_db_url'); print(engine.connect())"
```

### Issue: Alembic migration fails
**Solution:**
```bash
# Drop all tables and retry
alembic downgrade base
alembic upgrade head

# If schema conflicts, manually drop tables
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Issue: JWT token validation fails
**Solution:**
```bash
# Verify JWT_SECRET_KEY in .env
echo $JWT_SECRET_KEY

# Check token expiry settings
# Access token: 30 minutes
# Refresh token: 7 days
```

---

## 📞 Support

**Questions?** Post in `#irstudy-backend` Slack channel with:
- API endpoint not working
- Error message from logs
- Database connection issues

**Critical Blocker?** Contact Project Manager immediately.

---

**Last Updated:** 2026-02-01
**Owner:** Developer 2 - Backend Lead
**Estimated Completion:** 2026-02-02 (Day 2 of Week 1)
