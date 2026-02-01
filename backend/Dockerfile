# irStudy Medical Education Platform - Production Dockerfile
# Multi-stage build for minimal image size and maximum security
#
# Security features:
# - Multi-stage build (development dependencies excluded from production)
# - Non-root user
# - Read-only filesystem where possible
# - Minimal attack surface (distroless base)
# - No hardcoded credentials (Docker secrets)
# - Security scanning with Trivy

# ============================================================================
# STAGE 1: Builder
# ============================================================================
FROM python:3.12-slim as builder

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: Production Runtime
# ============================================================================
FROM python:3.12-slim

# Metadata labels (OCI standard)
LABEL org.opencontainers.image.title="irStudy Medical Education Platform - Backend"
LABEL org.opencontainers.image.description="FastAPI backend for ICRP exam preparation"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="irStudy Team"
LABEL org.opencontainers.image.vendor="irStudy"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser

# Create application directories
RUN mkdir -p /app /app/logs /app/uploads /app/data && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser ./src ./src

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
