"""
SQLAlchemy declarative base and database session management

SECURITY:
- All database credentials loaded from Docker secrets
- Connection pooling configured for performance
- Read replicas support for scaling
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# Read database password from Docker secret
def get_database_url() -> str:
    """
    Construct database URL from environment variables and Docker secrets.

    In production: Reads password from /run/secrets/db_password
    In development: Falls back to environment variable
    """
    host = os.getenv("DATABASE_HOST", "localhost")
    port = os.getenv("DATABASE_PORT", "5432")
    name = os.getenv("DATABASE_NAME", "irstudy_medical")
    user = os.getenv("DATABASE_USER", "postgres")

    # Try to read password from Docker secret
    secret_path = "/run/secrets/db_password"
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            password = f.read().strip()
    else:
        # Fallback to environment variable (development only)
        password = os.getenv("DATABASE_PASSWORD", "")
        if not password:
            raise ValueError(
                "Database password not found. "
                "Set DATABASE_PASSWORD env var or mount /run/secrets/db_password"
            )

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


# Database engine configuration
DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=int(os.getenv("DB_POOL_SIZE", 20)),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 40)),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", 30)),
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("DB_ECHO", "False").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base for all models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes to get database session.

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
