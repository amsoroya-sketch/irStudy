-- AMC Clinical Exam Simulation - Database Initialization
-- v2.0 Enhanced Architecture - Enable Security Extensions
-- This script runs automatically when PostgreSQL container starts

-- Enable pgcrypto for field-level encryption (AES-256)
-- Required for encrypting sensitive OSCE session data (SEC-002 mitigation)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enable uuid-ossp for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_stat_statements for query performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify extensions enabled
SELECT extname, extversion FROM pg_extension WHERE extname IN ('pgcrypto', 'uuid-ossp', 'pg_stat_statements');
