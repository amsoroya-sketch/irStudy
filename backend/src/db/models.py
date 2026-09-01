"""
SQLAlchemy database models for irStudy Medical Education Platform

MODELS:
- User: User accounts with HIPAA-compliant security
- MCQ: Multiple-choice questions with Australian medical context
- OSCE: OSCE scenarios with rubrics
- UserProgress: Progress tracking with analytics
- MCQAttempt: Individual MCQ attempt records with audit trail

SECURITY:
- Passwords hashed with bcrypt (never stored plaintext)
- PHI encrypted at rest where applicable
- Audit timestamps on all records
- Soft deletes for HIPAA compliance

AUSTRALIAN MEDICAL CONTEXT:
- All drug names use Australian terminology
- All citations reference Australian guidelines (eTG, AHPRA, AMH)
- Emergency number field defaults to "000"
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    Float,
    Table,
    UniqueConstraint,
    TypeDecorator,
    CHAR,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4
import uuid as uuid_lib
import enum

from .base import Base


# ============================================================================
# CUSTOM TYPES (PostgreSQL + SQLite compatibility)
# ============================================================================


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses
    CHAR(36) to store UUID as a string in SQLite for testing.
    """
    impl = CHAR(36)
    cache_ok = True

    def __init__(self, as_uuid=True):
        """Initialize UUID type with as_uuid parameter for compatibility."""
        self.as_uuid = as_uuid
        super(UUID, self).__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID(as_uuid=self.as_uuid))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid_lib.UUID):
                return str(value)
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif not self.as_uuid:
            return value
        else:
            if isinstance(value, uuid_lib.UUID):
                return value
            else:
                return uuid_lib.UUID(value)


# ============================================================================
# ENUMS
# ============================================================================


class UserRole(str, enum.Enum):
    """User roles for access control"""

    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"


class DifficultyLevel(str, enum.Enum):
    """Question difficulty levels"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MedicalSpecialty(str, enum.Enum):
    """Australian medical specialties"""

    CARDIOLOGY = "cardiology"
    RESPIRATORY = "respiratory"
    GASTROENTEROLOGY = "gastroenterology"
    NEUROLOGY = "neurology"
    PSYCHIATRY = "psychiatry"
    ENDOCRINOLOGY = "endocrinology"
    EMERGENCY_MEDICINE = "emergency_medicine"
    GENERAL_PRACTICE = "general_practice"
    PAEDIATRICS = "paediatrics"
    OBSTETRICS_GYNAECOLOGY = "obstetrics_gynaecology"
    SURGERY = "surgery"
    OPHTHALMOLOGY = "ophthalmology"
    UROLOGY = "urology"
    MUSCULOSKELETAL = "musculoskeletal"


class OSCEType(str, enum.Enum):
    """OSCE station types"""

    HISTORY_TAKING = "history_taking"
    PHYSICAL_EXAMINATION = "physical_examination"
    COUNSELLING = "counselling"
    COMMUNICATION = "communication"
    DIAGNOSIS_MANAGEMENT = "diagnosis_management"
    EMERGENCY_SCENARIO = "emergency_scenario"


# ============================================================================
# ASSOCIATION TABLES (Many-to-Many)
# ============================================================================

user_favorite_mcqs = Table(
    "user_favorite_mcqs",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("mcq_id", Integer, ForeignKey("mcqs.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

user_favorite_osces = Table(
    "user_favorite_osces",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("osce_id", Integer, ForeignKey("osces.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


# ============================================================================
# USER MODEL
# ============================================================================


class User(Base):
    """
    User account model with HIPAA-compliant security.

    SECURITY:
    - Passwords hashed with bcrypt (never plaintext)
    - Account lockout after failed login attempts
    - Session timeout tracking
    - Audit trail for all actions

    FIELDS:
    - email: Unique email address (PHI - encrypted at rest)
    - password_hash: Bcrypt hashed password
    - full_name: User's full name (PHI - encrypted at rest)
    - role: User role (student, educator, admin)
    - is_active: Account active status
    - is_verified: Email verification status
    - failed_login_attempts: Counter for account lockout
    - last_login_at: Last successful login timestamp
    """

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Profile (PHI - should be encrypted at application layer)
    full_name = Column(String(255), nullable=False)
    # Use values_callable to tell SQLAlchemy to use enum.value (lowercase) not enum.name (uppercase)
    role = Column(
        SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.STUDENT,
        nullable=False,
    )

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Email verification (Task 3.1)
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset (Task 3.1)
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    mcq_attempts = relationship("MCQAttempt", back_populates="user", cascade="all, delete-orphan")
    osce_attempts = relationship("OSCEAttempt", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan"
    )
    favorite_mcqs = relationship("MCQ", secondary=user_favorite_mcqs, back_populates="favorited_by")
    favorite_osces = relationship(
        "OSCE", secondary=user_favorite_osces, back_populates="favorited_by"
    )
    study_cards = relationship("StudyCard", back_populates="user", cascade="all, delete-orphan")

    # AI OSCE relationships (PRD_AI_OSCE_001)
    osce_attempts_ai = relationship("OSCEAttemptAI", back_populates="user", cascade="all, delete-orphan")
    mock_exams = relationship("MockExam", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# ============================================================================
# MCQ MODEL
# ============================================================================


class MCQ(Base):
    """
    Multiple-choice question model with Australian medical context.

    AUSTRALIAN CONTEXT:
    - Drug names: Australian (paracetamol not acetaminophen)
    - Units: SI units (mmol/L not mg/dL)
    - Guidelines: eTG, AHPRA, AMH citations required
    - Emergency number: 000 (not 911)

    FIELDS:
    - question_text: Clinical vignette with patient demographics
    - options: JSON array of answer options (A-E)
    - correct_answer: Correct option letter
    - explanation: Detailed explanation with clinical reasoning
    - citation: Australian guideline reference (eTG, AHPRA, AMH)
    - specialty: Medical specialty
    - difficulty: Question difficulty (easy, medium, hard)
    - tags: JSON array of topic tags
    - image_url: Optional clinical image (ECG, X-ray, etc.)
    """

    __tablename__ = "mcqs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Question content
    question_id = Column(
        String(50), unique=True, index=True, nullable=False
    )  # e.g., "MCQ-CARD-001"
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # {"A": "...", "B": "...", ...}
    correct_answer = Column(String(1), nullable=False)  # A, B, C, D, or E

    # Educational content
    explanation = Column(Text, nullable=False)
    citation = Column(String(500), nullable=False)  # Australian guideline reference
    learning_points = Column(JSON, nullable=True)  # ["Point 1", "Point 2", ...]

    # Metadata
    # Use values_callable to tell SQLAlchemy to use enum.value (lowercase) not enum.name (uppercase)
    specialty = Column(
        SQLEnum(MedicalSpecialty, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    difficulty = Column(
        SQLEnum(DifficultyLevel, values_callable=lambda x: [e.value for e in x]),
        default=DifficultyLevel.MEDIUM,
        nullable=False,
    )
    tags = Column(JSON, nullable=True)  # ["hypertension", "cardiovascular", "first-line"]

    # Media
    image_url = Column(String(500), nullable=True)
    image_caption = Column(String(500), nullable=True)

    # Statistics
    times_attempted = Column(Integer, default=0, nullable=False)
    times_correct = Column(Integer, default=0, nullable=False)
    average_time_seconds = Column(Float, default=0.0, nullable=False)

    # Flags
    is_published = Column(Boolean, default=True, nullable=False)
    requires_australian_context = Column(Boolean, default=True, nullable=False)

    # Email verification (Task 3.1)
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset (Task 3.1)
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    attempts = relationship("MCQAttempt", back_populates="mcq", cascade="all, delete-orphan")
    favorited_by = relationship(
        "User", secondary=user_favorite_mcqs, back_populates="favorite_mcqs"
    )

    def __repr__(self):
        return f"<MCQ(id={self.question_id}, specialty={self.specialty}, difficulty={self.difficulty})>"

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.times_attempted == 0:
            return 0.0
        return (self.times_correct / self.times_attempted) * 100


# ============================================================================
# OSCE MODEL
# ============================================================================


class OSCE(Base):
    """
    OSCE (Objective Structured Clinical Examination) scenario model.

    AMC CLINICAL EXAM FORMAT:
    - 16 stations × 8 minutes each
    - Rubric-based scoring (15 marks per station, 9/15 to pass)
    - Focus: History taking, physical examination, communication

    AUSTRALIAN CONTEXT:
    - Patient scenarios reflect Australian demographics
    - Management plans follow Australian guidelines (eTG, NSW Health)
    - Communication adjusted for Australian cultural norms

    FIELDS:
    - station_title: OSCE station title
    - station_type: Type (history, examination, counselling, etc.)
    - patient_instructions: Instructions for simulated patient/actor
    - candidate_instructions: Instructions shown to candidate
    - rubric: JSON scoring rubric (15 marks total)
    - time_limit_minutes: Time limit (default: 8 minutes)
    - learning_objectives: Educational objectives
    """

    __tablename__ = "osces"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Station identification
    osce_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "OSCE-CARD-001"
    station_title = Column(String(255), nullable=False)
    station_type = Column(
        SQLEnum(OSCEType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )

    # Instructions
    patient_instructions = Column(Text, nullable=False)  # For simulated patient/actor
    candidate_instructions = Column(Text, nullable=False)  # Shown to candidate at station
    examiner_instructions = Column(Text, nullable=True)  # For examiner (marking guide)

    # Rubric (15-mark AMC format)
    rubric = Column(JSON, nullable=False)
    """
    Example rubric JSON:
    {
        "introduction": {"max_marks": 1, "criteria": "Introduces self, confirms patient identity"},
        "history_taking": {"max_marks": 5, "criteria": "Systematic history using SOCRATES"},
        "examination": {"max_marks": 4, "criteria": "Correct technique, patient comfort"},
        "diagnosis": {"max_marks": 3, "criteria": "Appropriate differential diagnosis"},
        "management": {"max_marks": 2, "criteria": "Evidence-based management plan"}
    }
    """

    # Metadata
    specialty = Column(
        SQLEnum(MedicalSpecialty, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    difficulty = Column(
        SQLEnum(DifficultyLevel, values_callable=lambda x: [e.value for e in x]),
        default=DifficultyLevel.MEDIUM,
        nullable=False,
    )
    time_limit_minutes = Column(Integer, default=8, nullable=False)

    # Educational content
    learning_objectives = Column(JSON, nullable=True)  # ["Objective 1", "Objective 2", ...]
    key_points = Column(JSON, nullable=True)
    red_flags = Column(JSON, nullable=True)  # Red flag conditions to identify
    tags = Column(JSON, nullable=True)  # ["tag1", "tag2", ...] for filtering and categorization

    # Australian context
    australian_guidelines = Column(JSON, nullable=True)  # eTG, NSW Health protocols

    # Media
    supporting_documents = Column(JSON, nullable=True)  # URLs to test results, images
    video_resources = Column(JSON, nullable=True)  # Video demonstration links
    """
    Example video_resources JSON:
    {
        "essential_videos": [
            {
                "title": "Cardiovascular Examination - Stanford Medicine 25",
                "url": "https://stanfordmedicine25.stanford.edu/the25/cardiovascular.html",
                "source": "Stanford Medicine 25",
                "duration_minutes": 10,
                "focus": "Complete systematic cardiac examination",
                "why_recommended": "Gold standard demonstration"
            }
        ],
        "supplementary_videos": [...]
    }
    """

    # Educational Images (Week 1-2 Enhancement)
    educational_images = Column(JSON, nullable=True)  # Generated educational images metadata
    """
    Example educational_images JSON:
    {
        "comparison_charts": [{
            "title": "Gastric vs Duodenal Ulcer: Critical Differences",
            "image_url": "/static/images/osces/GI-PUD-001_gastric_duodenal_comparison.png",
            "type": "comparison_table",
            "generated_at": "2026-05-28T10:30:00Z"
        }],
        "decision_trees": [{
            "title": "Red Flag Assessment Flowchart",
            "image_url": "/static/images/osces/GI-PUD-001_red_flag_decision_tree.png",
            "type": "decision_tree"
        }],
        "timelines": [{
            "title": "Pain Timing After Meals",
            "image_url": "/static/images/osces/GI-PUD-001_pain_timing.png",
            "type": "timeline"
        }],
        "flowcharts": [{
            "title": "NSAID Cessation Pathway",
            "image_url": "/static/images/osces/GI-PUD-001_nsaid_cessation.png",
            "type": "flowchart"
        }]
    }
    """
    dr_amir_format = Column(Boolean, default=False, nullable=False)
    """
    Dr. Amir's 5 Ps Framework flag (724-line enhanced format):
    - True: Uses comprehensive Dr. Amir pattern (Preparation, Position, Permission, Perform, Present)
    - False: Standard OSCE format
    """

    # Statistics
    times_practiced = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0.0, nullable=False)

    # Flags
    is_published = Column(Boolean, default=True, nullable=False)

    # Email verification (Task 3.1)
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset (Task 3.1)
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    attempts = relationship("OSCEAttempt", back_populates="osce", cascade="all, delete-orphan")
    favorited_by = relationship(
        "User", secondary=user_favorite_osces, back_populates="favorite_osces"
    )

    def __repr__(self):
        return f"<OSCE(id={self.osce_id}, type={self.station_type}, specialty={self.specialty})>"


class OSCEStudyNote(Base):
    """
    Study notes linked to OSCE scenarios (from /ICRP_OSCE_Preparation/).

    DR. AMIR'S 5 Ps FRAMEWORK:
    - Preparation: Assess context and gather materials
    - Position: Patient positioning for examination
    - Permission: Explicit consent before touching
    - Perform: Systematic examination technique
    - Present: Summarize findings professionally

    CONTENT SOURCE:
    - 106 study note files from /ICRP_OSCE_Preparation/
    - Organized by specialty (Medicine, Psychiatry, Surgery, etc.)
    - Cross-referenced with OSCEs and MCQs

    FIELDS:
    - note_id: Unique identifier (e.g., "STUDY-CARD-001")
    - osce_id: Foreign key to linked OSCE (nullable - some notes are standalone)
    - title: Note title (e.g., "Cardiovascular Examination - Complete Guide")
    - content_markdown: Full markdown content
    - word_count: Calculated word count for reading time estimation
    - reading_time_minutes: Estimated reading time (200 words/minute)
    - topics: JSONB array of topics (e.g., ["Peptic Ulcer Disease", "Gastroenterology"])
    - tags: JSONB array of tags (e.g., ["red_flags", "management", "differential_diagnosis"])
    - amc_relevance: High/Medium/Low relevance to AMC Clinical Exam
    - specialty: Medical specialty (Medicine, Surgery, Psychiatry, etc.)
    - related_osce_ids: JSONB array of related OSCE IDs for cross-referencing
    - related_mcq_ids: JSONB array of related MCQ IDs for cross-referencing
    - is_published: Publication flag (default: True)
    """

    __tablename__ = "osce_study_notes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Identification
    note_id = Column(String(50), unique=True, index=True, nullable=False)
    osce_id = Column(Integer, ForeignKey("osces.id", ondelete="CASCADE"), nullable=True, index=True)

    # Content
    title = Column(String(500), nullable=False)
    content_markdown = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=True)
    reading_time_minutes = Column(Integer, nullable=True)

    # Classification
    topics = Column(JSON, nullable=True)  # ["Peptic Ulcer Disease", "Gastroenterology"]
    tags = Column(JSON, nullable=True)  # ["red_flags", "management", "differential_diagnosis"]
    amc_relevance = Column(String(50), nullable=True)  # "high", "medium", "low"
    specialty = Column(String(100), nullable=True, index=True)  # "Medicine", "Surgery", "Psychiatry"

    # Cross-referencing
    related_osce_ids = Column(JSON, nullable=True)  # [1, 5, 12] - related OSCE IDs
    related_mcq_ids = Column(JSON, nullable=True)  # [45, 67, 89] - related MCQ IDs

    # Flags
    is_published = Column(Boolean, default=True, nullable=False)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    osce = relationship("OSCE", backref="study_notes")

    def __repr__(self):
        return f"<OSCEStudyNote(note_id={self.note_id}, title={self.title[:50]})>"


class HTMLOSCENote(Base):
    """
    Pre-generated HTML OSCE notes (65 files from /ICRP_OSCE_Preparation/).

    CONTENT SOURCE:
    - 65 HTML files with embedded CSS and styling
    - Organized by specialty: Medicine, Surgery, Psychiatry, Paediatrics, ObGyn, Ethics_Communication, Mock_Stations
    - Uses Dr. Amir's method
    - Files served as static content, not stored in database

    FIELDS:
    - note_id: Unique identifier (e.g., "HTML-MED-001")
    - title: Extracted from HTML title tag
    - file_path: Relative path from /ICRP_OSCE_Preparation/ (e.g., "Medicine/10_Emergency_Anaphylaxis_Management.html")
    - specialty: Medical specialty
    - category: Sub-category (History, Physical Exam, Emergency, etc.)
    - topics: Extracted topics from content
    - preview_text: First 200 characters for preview
    - file_size_kb: File size in KB
    - estimated_reading_minutes: Reading time estimation
    - related_osce_ids: Link to related OSCEs in database
    """

    __tablename__ = "html_osce_notes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Identification
    note_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)  # Relative from ICRP_OSCE_Preparation/

    # Classification
    specialty = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    topics = Column(JSON, nullable=True)

    # Content metadata
    preview_text = Column(Text, nullable=True)
    file_size_kb = Column(Integer, nullable=True)
    estimated_reading_minutes = Column(Integer, nullable=True)

    # Cross-referencing
    related_osce_ids = Column(JSON, nullable=True)

    # Flags
    is_published = Column(Boolean, default=True, nullable=False)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<HTMLOSCENote(note_id={self.note_id}, specialty={self.specialty})>"


# ============================================================================
# AI OSCE MODELS (PRD_AI_OSCE_001)
# ============================================================================


class PatientPersona(Base):
    """
    AI Patient persona for OSCE simulation system.

    AMC CLINICAL EXAM CONTEXT:
    - 360 unique patient personas (specialties × difficulty levels)
    - Progressive disclosure: Information revealed based on student questions
    - Emotional intelligence: Patient state changes based on student interaction
    - RAG integration: Hints for AI Patient to query medical knowledge

    AUSTRALIAN CONTEXT:
    - Demographics reflect Australian population diversity
    - Cultural backgrounds appropriate for Australian medical practice
    - References to Australian healthcare system (Medicare, PBS, etc.)

    FIELDS:
    - persona_id: UUID primary key
    - persona_code: Unique code (e.g., "CARD-001-CHEST-PAIN")
    - name, age, gender, occupation, cultural_background, preferred_language
    - specialty: Medical specialty (cardiology, respiratory, etc.)
    - chief_complaint: Patient's main concern
    - opening_statement: First thing patient says
    - symptoms: JSONB progressive disclosure structure
    - medical_history: JSONB medical background
    - emotional_profile: JSONB emotional intelligence config
    - rag_query_hints: Array of search terms for RAG
    - key_differentials: Expected differential diagnoses
    - critical_actions: Must-do actions (e.g., "ECG within 10 minutes")
    - difficulty_level: foundation, intermediate, advanced
    - amc_blueprint_area: AMC curriculum alignment
    """

    __tablename__ = "patient_personas"

    # Primary key
    persona_id = Column(String, primary_key=True)  # UUID stored as string
    persona_code = Column(String(20), unique=True, nullable=False, index=True)

    # Demographics
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    occupation = Column(String(100), nullable=True)
    cultural_background = Column(String(100), nullable=True)
    preferred_language = Column(String(50), default="English")

    # Clinical Presentation
    specialty = Column(String(50), nullable=False, index=True)
    chief_complaint = Column(Text, nullable=False)
    opening_statement = Column(Text, nullable=False)

    # Progressive Disclosure (JSONB)
    symptoms = Column(JSON, nullable=False)
    medical_history = Column(JSON, nullable=False)
    emotional_profile = Column(JSON, nullable=False)

    # RAG Integration
    rag_query_hints = Column(JSON, nullable=True)  # TEXT[] stored as JSON
    key_differentials = Column(JSON, nullable=True)  # TEXT[] stored as JSON
    critical_actions = Column(JSON, nullable=True)  # TEXT[] stored as JSON

    # Metadata
    difficulty_level = Column(String(20), nullable=False, index=True)
    estimated_pass_rate = Column(Float, nullable=True)
    amc_blueprint_area = Column(String(100), nullable=True)
    amc_competencies = Column(JSON, nullable=True)  # TEXT[] stored as JSON

    # Audit Fields
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    validated_by = Column(String, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    # Relationships
    attempts = relationship("OSCEAttemptAI", back_populates="persona")

    def __repr__(self):
        return f"<PatientPersona(code={self.persona_code}, specialty={self.specialty}, difficulty={self.difficulty_level})>"


class MockExam(Base):
    """
    Mock OSCE exam orchestration (16 stations).

    AMC CLINICAL EXAM FORMAT:
    - 16 stations × 8 minutes each = 128 minutes
    - 2-minute breaks between stations
    - Total duration: ~150 minutes (2.5 hours)
    - Pass criteria: ≥9/15 on each station, overall competence demonstrated

    FIELDS:
    - exam_id: UUID primary key
    - user_id: Foreign key to User
    - stations_config: JSONB array of 16 persona_ids
    - exam_state: IN_PROGRESS, COMPLETED, ABANDONED
    - current_station_number: 1-16
    - started_at, completed_at, total_duration_minutes
    - total_score: Sum of all station scores (max 240)
    - stations_passed: Count of stations with ≥9/15
    - overall_pass: Boolean pass/fail
    """

    __tablename__ = "mock_exams"

    # Primary key
    exam_id = Column(String, primary_key=True)  # UUID stored as string
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Exam Configuration
    stations_config = Column(JSON, nullable=False)  # Array of 16 persona_ids
    exam_name = Column(String(200), nullable=True)

    # Progress Tracking
    exam_state = Column(String(20), default="IN_PROGRESS", nullable=False)
    current_station_number = Column(Integer, default=1, nullable=False)

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_duration_minutes = Column(Integer, nullable=True)

    # Overall Performance
    total_score = Column(Integer, default=0, nullable=False)
    stations_passed = Column(Integer, default=0, nullable=False)
    overall_pass = Column(Boolean, nullable=True)

    # Relationships
    user = relationship("User", back_populates="mock_exams")
    attempts = relationship("OSCEAttemptAI", back_populates="mock_exam")

    def __repr__(self):
        return f"<MockExam(exam_id={self.exam_id}, user_id={self.user_id}, state={self.exam_state}, station={self.current_station_number}/16)>"


class OSCEAttemptAI(Base):
    """
    Individual AI OSCE session attempt.

    SESSION TYPES:
    - individual: Practice single persona (8 minutes)
    - mock_exam: Part of 16-station exam

    STATE MACHINE:
    initialized → conversation → finalized → scoring → complete

    CONVERSATION ARCHIVE:
    - conversation_history: JSONB array of messages
    - emotional_state_transitions: JSONB tracking patient emotional state
    - student_actions: JSONB log of student actions (questions asked, exams ordered, etc.)

    FIELDS:
    - attempt_id: UUID primary key
    - user_id: Foreign key to User
    - persona_id: Foreign key to PatientPersona
    - mock_exam_id: Foreign key to MockExam (null for individual practice)
    - session_type: individual or mock_exam
    - station_number: 1-16 for mock exams, null for individual
    - started_at, ended_at, duration_seconds
    - conversation_history: JSONB conversation archive
    - emotional_state_transitions: JSONB emotional tracking
    - student_actions: JSONB action log
    - was_completed: Boolean completion status
    """

    __tablename__ = "ai_osce_attempts"

    # Primary key
    attempt_id = Column(String, primary_key=True)  # UUID stored as string

    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    persona_id = Column(String, ForeignKey("patient_personas.persona_id"), nullable=False, index=True)
    mock_exam_id = Column(String, ForeignKey("mock_exams.exam_id"), nullable=True, index=True)

    # Session Metadata
    session_type = Column(String(20), nullable=False)  # individual, mock_exam
    station_number = Column(Integer, nullable=True)  # 1-16 for mock exams

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Conversation Archive
    conversation_history = Column(JSON, default=list, nullable=False)
    emotional_state_transitions = Column(JSON, default=list, nullable=False)
    student_actions = Column(JSON, default=list, nullable=False)

    # Metadata
    was_completed = Column(Boolean, default=False, nullable=False)
    abandonment_reason = Column(Text, nullable=True)
    session_state = Column(String(20), nullable=False, default='initialized')

    # Relationships
    user = relationship("User", back_populates="osce_attempts_ai")
    persona = relationship("PatientPersona", back_populates="attempts")
    mock_exam = relationship("MockExam", back_populates="attempts")
    score = relationship("OSCEScoreAI", back_populates="attempt", uselist=False)

    def __repr__(self):
        return f"<OSCEAttemptAI(attempt_id={self.attempt_id}, user_id={self.user_id}, persona_id={self.persona_id}, type={self.session_type})>"


class OSCEScoreAI(Base):
    """
    AI Examiner scoring for OSCE attempt.

    AMC 15-MARK RUBRIC:
    - Communication: 0-3 marks
    - Clinical Reasoning: 0-4 marks
    - Information Gathering: 0-4 marks
    - Management: 0-2 marks
    - Professionalism: 0-2 marks
    - Total: 15 marks (9/15 to pass)

    GENERATED COLUMNS (PostgreSQL):
    - total_score: Computed sum of 5 domains
    - pass_fail: PASS if ≥9/15, FAIL otherwise

    FIELDS:
    - score_id: UUID primary key
    - attempt_id: Foreign key to OSCEAttemptAI (unique - one score per attempt)
    - communication_score: 0-3
    - clinical_reasoning_score: 0-4
    - information_gathering_score: 0-4
    - management_score: 0-2
    - professionalism_score: 0-2
    - total_score: GENERATED COLUMN (sum of above)
    - pass_fail: GENERATED COLUMN (PASS/FAIL)
    - ai_examiner_feedback: JSONB structured feedback
    - strengths: TEXT[] array of strengths
    - areas_for_improvement: TEXT[] array of improvement areas
    - critical_errors: TEXT[] array of critical errors
    - scored_at: Timestamp of scoring
    - scoring_model_version: AI model version used
    """

    __tablename__ = "ai_osce_scores"

    # Primary key
    score_id = Column(String, primary_key=True)  # UUID stored as string
    attempt_id = Column(String, ForeignKey("ai_osce_attempts.attempt_id"), unique=True, nullable=False, index=True)

    # AMC 15-Mark Rubric
    communication_score = Column(Integer, nullable=True)  # 0-3
    clinical_reasoning_score = Column(Integer, nullable=True)  # 0-4
    information_gathering_score = Column(Integer, nullable=True)  # 0-4
    management_score = Column(Integer, nullable=True)  # 0-2
    professionalism_score = Column(Integer, nullable=True)  # 0-2

    # Note: total_score and pass_fail are GENERATED columns in PostgreSQL
    # They are NOT defined in the SQLAlchemy model as they are computed by the database

    # Feedback
    ai_examiner_feedback = Column(JSON, nullable=True)
    strengths = Column(JSON, nullable=True)  # TEXT[] stored as JSON
    areas_for_improvement = Column(JSON, nullable=True)  # TEXT[] stored as JSON
    critical_errors = Column(JSON, nullable=True)  # TEXT[] stored as JSON

    # Audit
    scored_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    scoring_model_version = Column(String(50), nullable=True)

    # Relationships
    attempt = relationship("OSCEAttemptAI", back_populates="score")

    def __repr__(self):
        return f"<OSCEScoreAI(score_id={self.score_id}, attempt_id={self.attempt_id})>"

    @property
    def calculated_total_score(self) -> int:
        """Calculate total score from components (for use when GENERATED column not available)"""
        return (
            (self.communication_score or 0) +
            (self.clinical_reasoning_score or 0) +
            (self.information_gathering_score or 0) +
            (self.management_score or 0) +
            (self.professionalism_score or 0)
        )

    @property
    def calculated_pass_fail(self) -> str:
        """Calculate pass/fail status (for use when GENERATED column not available)"""
        return "PASS" if self.calculated_total_score >= 9 else "FAIL"


# ============================================================================
# MCQ ATTEMPT MODEL
# ============================================================================


class MCQAttempt(Base):
    """
    Individual MCQ attempt record with audit trail.

    HIPAA COMPLIANCE:
    - Tracks student performance (PHI)
    - Audit trail for learning analytics
    - Retention period: 7 years (configurable)

    FIELDS:
    - user_id: Foreign key to User
    - mcq_id: Foreign key to MCQ
    - selected_answer: Answer chosen by user
    - is_correct: Whether answer was correct
    - time_taken_seconds: Time taken to answer
    - confidence_level: User's confidence (1-5)
    """

    __tablename__ = "mcq_attempts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mcq_id = Column(Integer, ForeignKey("mcqs.id"), nullable=False, index=True)

    # Attempt details
    selected_answer = Column(String(1), nullable=False)  # A, B, C, D, or E
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=False)
    confidence_level = Column(Integer, nullable=True)  # 1-5 scale (1=guessing, 5=certain)

    # Context
    attempt_number = Column(
        Integer, default=1, nullable=False
    )  # How many times user attempted this MCQ
    was_flagged_for_review = Column(Boolean, default=False, nullable=False)

    # Audit timestamp
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="mcq_attempts")
    mcq = relationship("MCQ", back_populates="attempts")

    def __repr__(self):
        return (
            f"<MCQAttempt(user_id={self.user_id}, mcq_id={self.mcq_id}, correct={self.is_correct})>"
        )


# ============================================================================
# OSCE ATTEMPT MODEL
# ============================================================================


class OSCEAttempt(Base):
    """
    OSCE station practice attempt record with rubric scoring.

    AMC CLINICAL EXAM CONTEXT:
    - 15-mark rubric (5 categories × 3 marks each)
    - Pass mark: 9/15 (60%)
    - Tracks performance across categories for targeted improvement

    FIELDS:
    - user_id: Foreign key to User
    - osce_id: Foreign key to OSCE
    - scores: JSON dict of category scores (history_examination: 2, etc.)
    - total_score: Total score out of 15
    - time_taken_seconds: Time taken to complete station
    - self_reflection: Optional student self-assessment
    - areas_for_improvement: JSON array of weak categories
    """

    __tablename__ = "osce_attempts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    osce_id = Column(Integer, ForeignKey("osces.id"), nullable=False, index=True)

    # Scoring (AMC 15-mark format)
    scores = Column(JSON, nullable=False)  # {"history_examination": 2, "clinical_reasoning": 3, ...}
    total_score = Column(Integer, nullable=False)  # Sum of all category scores (max 15)
    passed = Column(Boolean, nullable=False)  # True if total_score >= 9

    # Time tracking
    time_taken_seconds = Column(Integer, nullable=False)

    # Reflective practice
    self_reflection = Column(Text, nullable=True)
    areas_for_improvement = Column(JSON, nullable=True)  # ["communication", "safety", ...]

    # Context
    attempt_number = Column(Integer, default=1, nullable=False)  # User's attempt count for this OSCE
    was_flagged_for_review = Column(Boolean, default=False, nullable=False)

    # Audit timestamp
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="osce_attempts")
    osce = relationship("OSCE", back_populates="attempts")

    def __repr__(self):
        return f"<OSCEAttempt(user_id={self.user_id}, osce_id={self.osce_id}, score={self.total_score}/15)>"


# ============================================================================
# USER PROGRESS MODEL
# ============================================================================


class UserProgress(Base):
    """
    User progress tracking with learning analytics.

    FEATURES:
    - Specialty-specific progress tracking
    - Spaced repetition scheduling
    - Weak areas identification
    - Study time tracking

    FIELDS:
    - user_id: Foreign key to User
    - specialty: Medical specialty
    - total_mcqs_attempted: Total MCQs attempted in specialty
    - total_mcqs_correct: Total correct answers
    - current_streak_days: Current daily study streak
    - longest_streak_days: Longest study streak
    - total_study_time_minutes: Total study time in specialty
    - weak_topics: JSON array of topics needing improvement
    """

    __tablename__ = "user_progress"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Specialty progress
    specialty = Column(
        SQLEnum(MedicalSpecialty, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )

    # MCQ statistics
    total_mcqs_attempted = Column(Integer, default=0, nullable=False)
    total_mcqs_correct = Column(Integer, default=0, nullable=False)
    unique_mcqs_attempted = Column(Integer, default=0, nullable=False)

    # OSCE statistics
    total_osces_practiced = Column(Integer, default=0, nullable=False)
    average_osce_score = Column(Float, default=0.0, nullable=False)

    # Streaks
    current_streak_days = Column(Integer, default=0, nullable=False)
    longest_streak_days = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)

    # Study time
    total_study_time_minutes = Column(Integer, default=0, nullable=False)

    # Weak areas (for targeted revision)
    weak_topics = Column(JSON, nullable=True)  # ["hypertension", "arrhythmias", ...]

    # Mastery level
    mastery_percentage = Column(Float, default=0.0, nullable=False)  # Overall mastery in specialty

    # AI OSCE progress tracking (PRD_AI_OSCE_001)
    ai_osces_attempted = Column(Integer, default=0, nullable=True)
    ai_osces_passed = Column(Integer, default=0, nullable=True)
    ai_osce_avg_score = Column(Float, default=0.0, nullable=True)  # Average total score
    mock_exams_completed = Column(Integer, default=0, nullable=True)
    last_ai_osce_at = Column(DateTime(timezone=True), nullable=True)

    # Email verification (Task 3.1)
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset (Task 3.1)
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="progress_records")

    # Unique constraint: One progress record per user per specialty
    __table_args__ = (
        UniqueConstraint("user_id", "specialty", name="unique_user_specialty_progress"),
    )

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, specialty={self.specialty}, mastery={self.mastery_percentage:.1f}%)>"

    @property
    def success_rate(self) -> float:
        """Calculate MCQ success rate percentage"""
        if self.total_mcqs_attempted == 0:
            return 0.0
        return (self.total_mcqs_correct / self.total_mcqs_attempted) * 100


# ============================================================================
# STUDY CARD MODEL
# ============================================================================


class StudyCard(Base):
    """
    Study card model for spaced repetition learning.

    SPACED REPETITION:
    - Uses SM-2 algorithm for optimal review scheduling
    - Tracks ease factor, interval, and repetition count
    - Supports quality ratings 0-5 for review

    AUSTRALIAN CONTEXT:
    - Citations reference Australian medical guidelines
    - Content aligned with AMC examination requirements
    - Drug names and units follow Australian standards

    FIELDS:
    - card_id: Unique card identifier (e.g., "CARDI-CARD-0001")
    - specialty: Medical specialty category
    - topic: Main topic (e.g., "ECG Interpretation")
    - subtopic: Specific subtopic (e.g., "STEMI patterns")
    - question: Front of flashcard
    - answer: Back of flashcard
    - explanation: Additional context/clinical pearls
    - citations: JSON array of Australian guideline references
    - difficulty: Card difficulty level
    - next_review_date: When card should be reviewed next
    - interval_days: Days until next review (SM-2)
    - ease_factor: SM-2 ease factor (default 2.5)
    - repetitions: Number of successful reviews
    """

    __tablename__ = "study_cards"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key (nullable for shared/public cards)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # OSCE session link (nullable for manually created cards)
    session_id = Column(String(255), nullable=True, index=True)  # Links to OSCEAttemptAI.attempt_id

    # Card identification
    card_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "CARDI-CARD-0001"

    # Content fields
    specialty = Column(
        SQLEnum(MedicalSpecialty, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    topic = Column(String(255), nullable=False, index=True)
    subtopic = Column(String(255), nullable=True)
    question = Column(Text, nullable=False)  # Front of card
    answer = Column(Text, nullable=False)  # Back of card
    explanation = Column(Text, nullable=True)  # Additional context

    # Citations (Australian medical guidelines)
    citations = Column(JSON, nullable=False)  # List of citation objects

    # Metadata
    difficulty = Column(
        SQLEnum(DifficultyLevel, values_callable=lambda x: [e.value for e in x]),
        default=DifficultyLevel.MEDIUM,
        nullable=False,
        index=True,
    )
    tags = Column(JSON, nullable=True)  # ["tag1", "tag2", ...]
    card_type = Column(
        String(50), default="concept", nullable=False
    )  # concept, clinical_pearl, etc.

    # Spaced Repetition (SM-2 Algorithm)
    next_review_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    interval_days = Column(Integer, default=1, nullable=False)
    ease_factor = Column(Float, default=2.5, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)

    # Flags
    is_active = Column(Boolean, default=True, nullable=False)

    # Email verification (Task 3.1)
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset (Task 3.1)
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    user = relationship("User", back_populates="study_cards")

    def __repr__(self):
        return f"<StudyCard(id={self.card_id}, specialty={self.specialty}, topic={self.topic})>"

    def update_sm2(self, quality: int) -> None:
        """
        Update spaced repetition schedule using SM-2 algorithm.

        Args:
            quality: Quality rating 0-5 (0=complete blackout, 5=perfect recall)

        SM-2 Algorithm:
        - If quality < 3: Reset to day 1
        - If quality >= 3: Increase interval based on ease factor
        - Ease factor adjusted by quality (min 1.3)
        """
        from datetime import timedelta

        if quality < 3:
            # Failed review - reset
            self.repetitions = 0
            self.interval_days = 1
        else:
            # Successful review
            if self.repetitions == 0:
                self.interval_days = 1
            elif self.repetitions == 1:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.ease_factor)

            self.repetitions += 1

        # Update ease factor
        self.ease_factor = max(
            1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )

        # Calculate next review date
        self.next_review_date = datetime.utcnow() + timedelta(days=self.interval_days)


# ============================================================================
# STUDY CARD REVIEW MODEL
# ============================================================================


class StudyCardReview(Base):
    """
    Individual study card review record with SM-2 tracking.

    FEATURES:
    - Tracks every review attempt for analytics
    - Records quality ratings (0-5) for SM-2 algorithm
    - Stores time taken for performance analysis
    - Maintains review history for learning insights

    FIELDS:
    - user_id: Foreign key to User
    - card_id: Foreign key to StudyCard
    - quality: Quality rating 0-5 (0=complete blackout, 5=perfect recall)
    - time_taken_seconds: Time taken to review card
    - ease_factor_after: Ease factor after this review
    - interval_days_after: Interval days after this review
    - repetitions_after: Repetitions count after this review
    - next_review_date_after: Next review date after this review
    """

    __tablename__ = "study_card_reviews"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("study_cards.id"), nullable=False, index=True)

    # Review details
    quality = Column(Integer, nullable=False)  # 0-5 scale (SM-2)
    time_taken_seconds = Column(Integer, nullable=False)

    # SM-2 state after this review
    ease_factor_after = Column(Float, nullable=False)
    interval_days_after = Column(Integer, nullable=False)
    repetitions_after = Column(Integer, nullable=False)
    next_review_date_after = Column(DateTime(timezone=True), nullable=False)

    # Audit timestamp
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<StudyCardReview(user_id={self.user_id}, card_id={self.card_id}, quality={self.quality})>"


# ============================================================================
# EMR (Electronic Medical Record) MODELS
# ============================================================================
# Models for Epic/Cerner EMR practice simulation
# Migrated from inline definitions in src/api/v1/emr/sessions.py
# Migration file: 20260215_1200_008_add_emr_tables.py


class MockPatient(Base):
    """
    Simulated Patient for EMR Practice

    Represents realistic patient scenarios for clinical documentation training.
    """
    __tablename__ = "mock_patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # NOT-NULL columns per Alembic migration 008 (source of truth for Postgres).
    mrn = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    presenting_complaint = Column(Text, nullable=False)
    vital_signs = Column(JSON)
    medical_history = Column(JSON)
    specialty = Column(String(50), index=True, nullable=False)
    difficulty = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Answer-key + clinical detail columns (already present in DB migration 008,
    # previously unmapped in the ORM). Mapping them lets the assessment engine
    # read the per-case expected findings. See PRD-EMR-PRACTICE-001.
    # ``demographics`` is NOT NULL in migration 008; ``default=dict`` guarantees a
    # value on INSERT even when callers don't supply one.
    demographics = Column(JSON, nullable=False, default=dict)
    medications = Column(JSON, nullable=True)
    allergies = Column(JSON, nullable=True)
    physical_exam_findings = Column(JSON, nullable=True)
    investigation_results = Column(JSON, nullable=True)
    source_osce_id = Column(Integer, ForeignKey("osces.id"), nullable=True)
    validation_criteria = Column(JSON, nullable=True)


class EMRSession(Base):
    """
    EMR Practice Session

    Tracks a single EMR documentation session (Epic or Cerner).
    """
    __tablename__ = "emr_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    # NOT-NULL columns per Alembic migration 008 — every EMR session references a
    # real mock_patients row and carries specialty/difficulty. The OSCE→EMR
    # converter materialises a MockPatient so these are always populated.
    patient_id = Column(UUID(as_uuid=True), ForeignKey("mock_patients.id"), index=True, nullable=False)
    emr_system = Column(String(20))  # "epic" or "cerner"
    specialty = Column(String(50), index=True, nullable=False)
    difficulty = Column(String(20), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    submitted_at = Column(DateTime, nullable=True)
    elapsed_time_seconds = Column(Integer, default=0)
    validation_score = Column(Float, nullable=True)
    score_breakdown = Column(JSON, nullable=True)
    status = Column(String(20), default="in_progress")
    auto_save_count = Column(Integer, default=0)
    last_auto_save_at = Column(DateTime, nullable=True)
    typing_metrics = Column(JSON, nullable=True)

    # OSCE-to-EMR conversion fields (backed by migration 008).
    # NOTE: the un-migrated ``patient_data``/``session_data`` JSON columns were
    # removed — they had no Alembic migration and 500-ed conversions on Postgres.
    # Converted sessions now reference a real MockPatient (``patient_id``) and
    # store the pre-filled SOAP note as an EMRSOAPNote draft.
    source_osce_attempt_id = Column(String(255), nullable=True, index=True)
    conversion_metadata = Column(JSON, nullable=True)


class EMRSOAPNote(Base):
    """
    SOAP Note (Subjective-Objective-Assessment-Plan)

    Clinical documentation following Australian medical standards.
    """
    __tablename__ = "emr_soap_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("emr_sessions.id"), index=True)
    subjective = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)
    typing_wpm = Column(Float, nullable=True)
    completion_time_seconds = Column(Integer, nullable=True)
    is_final_submission = Column(Boolean, default=False)


class EMRPrescription(Base):
    """
    EMR Prescription (PBS-Compliant)

    Australian PBS (Pharmaceutical Benefits Scheme) compliance enforced.
    """
    __tablename__ = "emr_prescriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("emr_sessions.id"), index=True)

    # Prescription details (Australian format) - matches migration 008
    medication_name = Column(String(200), nullable=False)
    dose = Column(String(50), nullable=False)
    frequency = Column(String(50), nullable=False)
    route = Column(String(20), nullable=False)
    repeats = Column(Integer, nullable=False)
    indication = Column(Text, nullable=True)

    # PBS (Pharmaceutical Benefits Scheme) validation
    pbs_listed = Column(Boolean, nullable=True)
    pbs_item_code = Column(String(10), nullable=True)
    authority_required = Column(Boolean, nullable=True)

    # Validation results
    validation_errors = Column(JSON, nullable=True)
    is_valid = Column(Boolean, nullable=True)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "repeats >= 0 AND repeats <= 5",
            name="check_emr_prescriptions_repeats_range",
        ),
    )


class EMRPathologyOrder(Base):
    """
    Pathology Order (MBS-Compliant)

    Australian MBS (Medicare Benefits Schedule) compliance.
    """
    __tablename__ = "emr_pathology_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("emr_sessions.id"), index=True)
    test_name = Column(String(200))
    urgency = Column(String(20))
    indication = Column(Text)


class EMRValidationResult(Base):
    """
    EMR Session Validation Result (3-Layer Validation)

    Schema matches Alembic migration 008 (the source of truth for the live DB).

    Validation Layers (stored verbatim as JSON):
    1. layer_1_zod: Zod/Pydantic field-level validation
    2. layer_2_python: Python business-logic (Australian terminology, PBS) validation
    3. layer_3_ai: Claude AI clinical assessment (retains critical_errors_committed
       and missing_elements so the learner sees WHY they passed/failed)

    ``strengths``/``improvements``/``red_flags`` are extracted for direct UI display.
    """
    __tablename__ = "emr_validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("emr_sessions.id"), unique=True, index=True, nullable=False
    )

    # Validation type discriminator (NOT NULL in the DB)
    validation_type = Column(String(50), nullable=False)

    # 3-layer validation results (stored verbatim)
    layer_1_zod = Column(JSON, nullable=True)
    layer_2_python = Column(JSON, nullable=True)
    layer_3_ai = Column(JSON, nullable=True)

    # Overall validation summary
    overall_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)

    # Extracted feedback (for UI display) - Postgres text[] arrays, JSON on SQLite
    strengths = Column(PG_ARRAY(Text).with_variant(JSON(), "sqlite"), nullable=True)
    improvements = Column(PG_ARRAY(Text).with_variant(JSON(), "sqlite"), nullable=True)
    red_flags = Column(PG_ARRAY(Text).with_variant(JSON(), "sqlite"), nullable=True)

    # Metadata
    validated_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "overall_score >= 0 AND overall_score <= 15",
            name="check_emr_validation_overall_score",
        ),
    )


# Import sqlalchemy for unique constraint
import sqlalchemy
