-- AMC Clinical Exam Simulation - Initial Database Schema
-- v2.0 Enhanced Architecture - Task 1.3: Encrypted Schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Patient Personas Table (with encrypted history)
CREATE TABLE IF NOT EXISTS patient_personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(50) NOT NULL,
    presenting_complaint TEXT NOT NULL,
    encrypted_history BYTEA,  -- ENCRYPTED patient medical history
    emotional_baseline VARCHAR(50) DEFAULT 'neutral',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- OSCE Scenarios Table
CREATE TABLE IF NOT EXISTS osce_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50),
    duration_minutes INTEGER DEFAULT 8,
    patient_persona_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- OSCE Sessions Table (with encrypted sensitive data)
CREATE TABLE IF NOT EXISTS osce_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scenario_id UUID NOT NULL REFERENCES osce_scenarios(id),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    encrypted_transcript BYTEA,  -- ENCRYPTED conversation
    encrypted_scoring BYTEA,     -- ENCRYPTED scoring results
    duration_seconds INTEGER,
    final_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON osce_sessions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_completed ON osce_sessions(completed_at DESC);

-- Encryption helper functions
CREATE OR REPLACE FUNCTION encrypt_data(data TEXT, key TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data, key);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION decrypt_data(encrypted_data BYTEA, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_data, key);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
