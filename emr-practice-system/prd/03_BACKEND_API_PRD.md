# Backend API Product Requirements Document

**Version**: 1.0
**Date**: 2026-02-02
**Product**: EMR Practice System - Backend API
**Technology**: FastAPI 0.109.0 + Python 3.11

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Architecture](#architecture)
3. [Authentication & Authorization](#authentication--authorization)
4. [API Endpoints](#api-endpoints)
5. [Database Schema](#database-schema)
6. [Validation Services](#validation-services)
7. [Error Handling](#error-handling)
8. [Performance Requirements](#performance-requirements)

---

## API Overview

### Technology Stack

```python
# Core Framework
FastAPI==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
SQLAlchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9  # PostgreSQL (production)
aiosqlite==0.19.0       # SQLite (development)

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Validation & AI
anthropic==0.18.1
pydantic==2.5.3
pydantic-settings==2.1.0

# PBS/MBS Integration
httpx==0.25.2
requests==2.31.0

# Utilities
python-dotenv==1.0.0
pytz==2023.3
```

### API Base URL

```
Development: http://localhost:8001/api/v1
Production:  https://api.irstudy.com/emr/v1
```

### API Documentation

- **OpenAPI/Swagger**: `/docs`
- **ReDoc**: `/redoc`
- **Health Check**: `/health`

---

## Architecture

### Project Structure

```
backend/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── sessions.py       # EMR session management
│   │       ├── soap_notes.py     # SOAP note CRUD
│   │       ├── prescriptions.py  # Prescription management
│   │       ├── pathology.py      # Pathology orders
│   │       ├── validation.py     # Validation endpoints
│   │       └── progress.py       # Progress tracking
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   ├── session.py            # EMR session model
│   │   ├── soap_note.py          # SOAP note model
│   │   ├── prescription.py       # Prescription model
│   │   ├── pathology_order.py    # Pathology order model
│   │   └── validation_result.py  # Validation result model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py               # Auth schemas
│   │   ├── session.py            # Session schemas
│   │   ├── soap_note.py          # SOAP note schemas
│   │   ├── prescription.py       # Prescription schemas
│   │   ├── pathology.py          # Pathology schemas
│   │   └── validation.py         # Validation schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Authentication logic
│   │   ├── session_service.py    # Session management
│   │   ├── pbs_service.py        # PBS medication service
│   │   ├── mbs_service.py        # MBS pathology service
│   │   └── ai_validation_service.py  # Claude AI validation
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── pbs_validator.py      # PBS validation logic
│   │   ├── mbs_validator.py      # MBS validation logic
│   │   └── clinical_safety_validator.py  # Safety checks
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py               # Database base classes
│   │   └── session.py            # Database session management
│   └── utils/
│       ├── __init__.py
│       ├── security.py           # Security utilities
│       └── dependencies.py       # FastAPI dependencies
├── alembic/
│   ├── versions/                 # Database migrations
│   └── env.py
├── tests/
│   ├── test_api/
│   ├── test_services/
│   └── test_validation/
├── requirements.txt
├── .env.example
└── README.md
```

### FastAPI Application Setup

```python
# src/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from src.api.v1 import (
    auth, sessions, soap_notes, prescriptions,
    pathology, validation, progress
)
from src.db.session import engine, Base
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: Close database connections
    await engine.dispose()

# Create FastAPI app
app = FastAPI(
    title="EMR Practice System API",
    description="Backend API for EMR practice system with PBS/MBS compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(soap_notes.router, prefix="/api/v1/soap-notes", tags=["SOAP Notes"])
app.include_router(prescriptions.router, prefix="/api/v1/prescriptions", tags=["Prescriptions"])
app.include_router(pathology.router, prefix="/api/v1/pathology", tags=["Pathology"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["Progress"])

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "EMR Practice System API",
        "docs": "/docs",
        "health": "/health"
    }
```

### Configuration Management

```python
# src/config.py

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "EMR Practice System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./emr_practice.db"
    DB_ECHO: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React dev
        "https://irstudy.com"     # Production frontend
    ]

    # Anthropic AI
    ANTHROPIC_API_KEY: str
    AI_MODEL: str = "claude-3-5-sonnet-20241022"
    AI_MAX_TOKENS: int = 4000
    AI_TEMPERATURE: float = 0.3

    # PBS/MBS Integration
    PBS_API_URL: str = "https://api.pbs.gov.au/v1"
    MBS_API_URL: str = "https://api.mbsonline.gov.au/v1"

    # Validation Settings
    VALIDATION_TIMEOUT: int = 10  # seconds
    ENABLE_AI_VALIDATION: bool = True

    # Session Settings
    SESSION_TIMEOUT_MINUTES: int = 15
    AUTO_SAVE_INTERVAL_SECONDS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## Authentication & Authorization

### JWT Token Authentication

```python
# src/services/auth_service.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.config import settings
from src.models.user import User
from src.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()

class AuthService:
    """Authentication service"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Get current user from JWT token"""

        token = credentials.credentials

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        return user
```

### Authentication Endpoints

```python
# src/api/v1/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from src.schemas.auth import Token, UserLogin, UserCreate
from src.models.user import User
from src.services.auth_service import AuthService
from src.db.session import get_db
from src.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint

    Returns JWT access token for authentication
    """

    # Get user from database
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    # Verify user and password
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    User registration endpoint

    Creates new user account and returns JWT token
    """

    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_create.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = AuthService.get_password_hash(user_create.password)
    new_user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_current_user(
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get current user profile"""

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat()
    }
```

---

## API Endpoints

### 1. Session Management

**Create EMR Session**

```http
POST /api/v1/sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "emr_type": "cerner",  // or "epic"
  "scenario_id": "uuid",
  "patient_id": "uuid"
}

Response 201:
{
  "session_id": "uuid",
  "emr_type": "cerner",
  "patient": {
    "id": "uuid",
    "name": "Sarah Johnson",
    "age": 45,
    "sex": "F",
    "mrn": "12345678"
  },
  "started_at": "2026-02-02T14:30:00Z",
  "expires_at": "2026-02-02T14:45:00Z"
}
```

**Get Session Details**

```http
GET /api/v1/sessions/{session_id}
Authorization: Bearer <token>

Response 200:
{
  "session_id": "uuid",
  "status": "active",  // "active", "completed", "expired"
  "emr_type": "cerner",
  "patient": {...},
  "soap_note_id": "uuid",
  "prescriptions": [],
  "pathology_orders": [],
  "validation_results": [],
  "metrics": {
    "time_elapsed": 420,  // seconds
    "words_typed": 523,
    "wpm": 45,
    "auto_saves": 14
  }
}
```

**Complete Session**

```http
POST /api/v1/sessions/{session_id}/complete
Authorization: Bearer <token>

Response 200:
{
  "session_id": "uuid",
  "status": "completed",
  "completed_at": "2026-02-02T14:42:15Z",
  "final_scores": {
    "overall_score": 82,
    "clinical_reasoning": 25,
    "documentation_completeness": 21,
    "australian_compliance": 18,
    "patient_safety": 13,
    "professional_communication": 5
  }
}
```

### 2. SOAP Note Management

**Create SOAP Note**

```http
POST /api/v1/soap-notes
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "uuid",
  "patient_id": "uuid",
  "subjective": {
    "chief_complaint": "Chest pain",
    "hpi": "45F presents with...",
    "past_medical_history": ["Type 2 Diabetes", "Hypertension"],
    "medications": [{
      "name": "Metformin",
      "dose": "500mg",
      "frequency": "BD",
      "route": "PO"
    }],
    "allergies": [{
      "allergen": "Penicillin",
      "reaction": "Anaphylaxis",
      "severity": "severe"
    }],
    "social_history": {
      "smoking": "ex-smoker",
      "alcohol": "social"
    },
    "family_history": ["CAD in father"]
  },
  "objective": {
    "vital_signs": {
      "temperature": 37.2,
      "heart_rate": 88,
      "blood_pressure": {
        "systolic": 142,
        "diastolic": 86
      },
      "respiratory_rate": 16,
      "oxygen_saturation": 98
    },
    "general_appearance": "Alert and oriented...",
    "systems_examination": {
      "cardiovascular": "Regular rhythm...",
      "respiratory": "Clear to auscultation..."
    }
  },
  "assessment": {
    "working_diagnosis": "Unstable angina",
    "differential_diagnoses": [
      "Acute coronary syndrome",
      "GERD",
      "Musculoskeletal pain"
    ],
    "clinical_reasoning": "Patient presents with..."
  },
  "plan": {
    "investigations": [{
      "type": "pathology",
      "test": "Troponin",
      "mbs_item_number": "66800",
      "indication": "Rule out ACS",
      "urgency": "urgent"
    }],
    "management": [{
      "category": "medication",
      "description": "Aspirin 300mg stat",
      "timeframe": "immediate"
    }],
    "follow_up": {
      "timing": "24 hours",
      "review_items": ["Troponin result", "Chest pain resolved"]
    },
    "safety_netting": "Return immediately if chest pain worsens..."
  }
}

Response 201:
{
  "soap_note_id": "uuid",
  "session_id": "uuid",
  "created_at": "2026-02-02T14:32:00Z",
  "auto_save_enabled": true
}
```

**Update SOAP Note (Auto-save)**

```http
PATCH /api/v1/soap-notes/{soap_note_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "subjective": {
    "hpi": "Updated HPI content..."
  }
}

Response 200:
{
  "soap_note_id": "uuid",
  "last_updated": "2026-02-02T14:32:45Z",
  "auto_saved": true
}
```

**Get SOAP Note**

```http
GET /api/v1/soap-notes/{soap_note_id}
Authorization: Bearer <token>

Response 200:
{
  "soap_note_id": "uuid",
  "session_id": "uuid",
  "patient_id": "uuid",
  "subjective": {...},
  "objective": {...},
  "assessment": {...},
  "plan": {...},
  "created_at": "2026-02-02T14:32:00Z",
  "last_updated": "2026-02-02T14:32:45Z"
}
```

### 3. Prescription Management

**Create Prescription**

```http
POST /api/v1/prescriptions
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "uuid",
  "patient_id": "uuid",
  "medications": [{
    "pbs_code": "1234A",
    "medication_name": "Paracetamol",
    "strength": "500mg",
    "form": "tablet",
    "quantity": 100,
    "repeats": 5,
    "dosage": {
      "amount": "1-2",
      "frequency": "QID",
      "route": "PO"
    },
    "indication": "Chronic pain management",
    "authority_required": false
  }],
  "prescriber_number": "1234567"
}

Response 201:
{
  "prescription_id": "uuid",
  "session_id": "uuid",
  "medications": [{
    "medication_id": "uuid",
    "pbs_code": "1234A",
    "medication_name": "Paracetamol",
    "status": "pending_validation"
  }],
  "created_at": "2026-02-02T14:35:00Z"
}
```

**Get Prescription**

```http
GET /api/v1/prescriptions/{prescription_id}
Authorization: Bearer <token>

Response 200:
{
  "prescription_id": "uuid",
  "session_id": "uuid",
  "patient_id": "uuid",
  "medications": [{...}],
  "validation_result": {
    "passed": true,
    "errors": [],
    "warnings": [
      {
        "severity": "warning",
        "category": "pbs_compliance",
        "message": "Quantity (100) at PBS maximum",
        "suggestion": "Consider if full quantity needed"
      }
    ]
  },
  "created_at": "2026-02-02T14:35:00Z"
}
```

### 4. Pathology Orders

**Create Pathology Order**

```http
POST /api/v1/pathology
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "uuid",
  "patient_id": "uuid",
  "tests": [{
    "test_name": "Full Blood Count",
    "mbs_item_number": "65070",
    "category": "haematology",
    "specimen_type": "blood",
    "urgency": "routine",
    "indication": "Investigate fatigue and pallor",
    "fasting_required": false
  }],
  "provider_number": "1234567AB",
  "clinical_notes": "Patient presents with 3-month history of fatigue..."
}

Response 201:
{
  "pathology_order_id": "uuid",
  "session_id": "uuid",
  "tests": [{
    "test_id": "uuid",
    "test_name": "Full Blood Count",
    "mbs_item_number": "65070",
    "status": "pending"
  }],
  "created_at": "2026-02-02T14:36:00Z"
}
```

### 5. Validation Endpoints

**Validate SOAP Note**

```http
POST /api/v1/validation/soap-note
Authorization: Bearer <token>
Content-Type: application/json

{
  "soap_note_id": "uuid",
  "validation_level": "full"  // "basic", "standard", "full"
}

Response 200:
{
  "validation_id": "uuid",
  "soap_note_id": "uuid",
  "passed": true,
  "layers": {
    "layer1": {
      "status": "passed",
      "duration_ms": 15,
      "errors": []
    },
    "layer2": {
      "status": "passed",
      "duration_ms": 845,
      "warnings": [...]
    },
    "layer3": {
      "status": "passed",
      "duration_ms": 4250,
      "ai_result": {
        "overall_score": 82,
        "category_scores": {...},
        "strengths": [...],
        "improvements": [...],
        "educational_feedback": "..."
      }
    }
  },
  "overall_score": 82,
  "total_duration_ms": 5110,
  "validated_at": "2026-02-02T14:40:00Z"
}
```

**Validate Prescription**

```http
POST /api/v1/validation/prescription
Authorization: Bearer <token>
Content-Type: application/json

{
  "prescription_id": "uuid"
}

Response 200:
{
  "validation_id": "uuid",
  "prescription_id": "uuid",
  "passed": false,
  "errors": [{
    "severity": "error",
    "category": "pbs_compliance",
    "message": "Repeats (6) exceed PBS maximum (5)",
    "field": "medications[0].repeats",
    "suggestion": "Reduce to 5 repeats"
  }],
  "warnings": [],
  "validated_at": "2026-02-02T14:37:00Z"
}
```

### 6. Progress Tracking

**Get User Progress**

```http
GET /api/v1/progress/user
Authorization: Bearer <token>

Response 200:
{
  "user_id": "uuid",
  "total_sessions": 24,
  "completed_sessions": 18,
  "average_score": 78.5,
  "soap_notes_written": 18,
  "prescriptions_written": 22,
  "pathology_orders": 16,
  "time_spent_minutes": 1240,
  "improvement_areas": [
    {
      "category": "clinical_reasoning",
      "current_score": 22,
      "target_score": 28,
      "trend": "improving"
    }
  ],
  "recent_sessions": [...]
}
```

---

## Database Schema

### User Model

```python
# src/models/user.py

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from src.db.base import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
```

### EMR Session Model

```python
# src/models/session.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from src.db.base import Base

class EMRType(str, enum.Enum):
    CERNER = "cerner"
    EPIC = "epic"

class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

class EMRSession(Base):
    __tablename__ = "emr_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("mock_patients.id"), nullable=False)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=True)

    emr_type = Column(SQLEnum(EMRType), nullable=False)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)

    # Metrics
    time_elapsed_seconds = Column(Integer, default=0)
    words_typed = Column(Integer, default=0)
    wpm = Column(Integer, default=0)
    auto_saves_count = Column(Integer, default=0)

    # Final scores
    overall_score = Column(Integer, nullable=True)
    scores_breakdown = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", backref="emr_sessions")
    patient = relationship("MockPatient", backref="emr_sessions")
    soap_notes = relationship("SOAPNote", back_populates="session")
    prescriptions = relationship("Prescription", back_populates="session")
    pathology_orders = relationship("PathologyOrder", back_populates="session")
```

### SOAP Note Model

```python
# src/models/soap_note.py

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from src.db.base import Base

class SOAPNote(Base):
    __tablename__ = "soap_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("emr_sessions.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("mock_patients.id"), nullable=False)

    # SOAP sections stored as JSON
    subjective = Column(JSON, nullable=False)
    objective = Column(JSON, nullable=False)
    assessment = Column(JSON, nullable=False)
    plan = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    auto_save_enabled = Column(Boolean, default=True)

    # Validation
    validation_result_id = Column(UUID(as_uuid=True), ForeignKey("validation_results.id"), nullable=True)

    # Relationships
    session = relationship("EMRSession", back_populates="soap_notes")
    patient = relationship("MockPatient")
    validation_result = relationship("ValidationResult", backref="soap_note")
```

---

## Validation Services

### PBS Validator Service

```python
# src/services/pbs_service.py

from typing import List, Dict, Optional
from src.validation.pbs_validator import PBSValidator, ValidationError

class PBSService:
    """PBS medication validation service"""

    def __init__(self):
        self.validator = PBSValidator()

    async def validate_prescription(
        self,
        medications: List[Dict],
        patient_allergies: List[Dict],
        patient_conditions: List[str],
        patient_medications: List[Dict],
        patient_age: int,
        patient_pregnant: bool = False,
        patient_breastfeeding: bool = False
    ) -> List[ValidationError]:
        """
        Validate prescription against PBS rules

        Returns list of validation errors/warnings
        """

        return self.validator.validate_prescription(
            medications=medications,
            patient_allergies=patient_allergies,
            patient_conditions=patient_conditions,
            patient_medications=patient_medications,
            patient_age=patient_age,
            patient_pregnant=patient_pregnant,
            patient_breastfeeding=patient_breastfeeding
        )

    async def search_pbs_medications(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search PBS database for medications

        In production, this would call actual PBS API
        """

        # Mock implementation
        # In production: make HTTP request to PBS API
        pass
```

### AI Validation Service

```python
# src/services/ai_validation_service.py

from anthropic import Anthropic
from typing import Dict
import json

from src.config import settings
from src.validation.ai_validator import AIValidator

class AIValidationService:
    """AI-powered clinical validation service"""

    def __init__(self):
        self.validator = AIValidator(api_key=settings.ANTHROPIC_API_KEY)

    async def validate_soap_note(
        self,
        soap_note: Dict,
        patient_context: Dict
    ) -> Dict:
        """
        Deep clinical validation of SOAP note using Claude AI

        Returns:
        {
            "overall_score": 0-100,
            "category_scores": {...},
            "strengths": [...],
            "improvements": [...],
            "educational_feedback": "...",
            "clinical_reasoning_quality": "excellent|good|adequate|needs_improvement"
        }
        """

        return await self.validator.validate_soap_note(
            soap_note=soap_note,
            patient_context=patient_context
        )

    async def validate_prescription(
        self,
        prescription: Dict,
        patient_context: Dict
    ) -> Dict:
        """
        Deep validation of prescription using Claude AI

        Returns safety and appropriateness assessment
        """

        return await self.validator.validate_prescription_ai(
            prescription=prescription,
            patient_context=patient_context
        )
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "SOAP note validation failed",
    "details": [
      {
        "field": "subjective.chief_complaint",
        "message": "Chief complaint must be at least 5 characters"
      }
    ],
    "timestamp": "2026-02-02T14:40:00Z",
    "request_id": "uuid"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_FAILED` | 422 | Data validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid token |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `PBS_VALIDATION_ERROR` | 422 | PBS compliance validation failed |
| `MBS_VALIDATION_ERROR` | 422 | MBS compliance validation failed |
| `AI_SERVICE_ERROR` | 503 | AI validation service unavailable |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

## Performance Requirements

### Response Time SLAs

| Endpoint Category | Target Response Time | Max Response Time |
|-------------------|---------------------|-------------------|
| Authentication | <200ms | 500ms |
| Session Management | <300ms | 1s |
| SOAP Note CRUD | <400ms | 1s |
| Layer 1 Validation | <50ms | 100ms |
| Layer 2 Validation | <1s | 3s |
| Layer 3 AI Validation | 3-5s | 10s |
| Progress Queries | <500ms | 2s |

### Concurrency

- **Target**: Support 100 concurrent users
- **Database Connection Pool**: 20 connections
- **API Rate Limiting**: 100 requests/minute per user

### Caching Strategy

```python
# Redis caching for frequently accessed data
- PBS medication database: 24 hour TTL
- MBS item numbers: 24 hour TTL
- Patient mock data: 1 hour TTL
- Validation results: 30 minute TTL
```

---

## Implementation Checklist

### Core API
- [ ] FastAPI application setup
- [ ] Database models and migrations
- [ ] Authentication & JWT tokens
- [ ] CORS middleware configuration
- [ ] Error handling middleware
- [ ] Request logging

### Endpoints
- [ ] Authentication endpoints (login, register, me)
- [ ] Session management (create, get, complete)
- [ ] SOAP note CRUD
- [ ] Prescription management
- [ ] Pathology order management
- [ ] Validation endpoints
- [ ] Progress tracking

### Services
- [ ] Auth service with JWT
- [ ] PBS validation service
- [ ] MBS validation service
- [ ] AI validation service (Claude)
- [ ] Session service

### Database
- [ ] User model and table
- [ ] EMR session model
- [ ] SOAP note model
- [ ] Prescription model
- [ ] Pathology order model
- [ ] Validation result model
- [ ] Alembic migrations

### Testing
- [ ] Unit tests for validators
- [ ] Integration tests for API endpoints
- [ ] Authentication tests
- [ ] Validation service tests
- [ ] Performance tests

### Documentation
- [ ] OpenAPI/Swagger docs
- [ ] API endpoint documentation
- [ ] Database schema documentation
- [ ] Deployment guide

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Status**: ✅ Ready for Implementation
**Estimated Implementation Time**: 20-25 hours

