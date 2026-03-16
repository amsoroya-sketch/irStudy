-- Database Schema for Patient Personas and Validation Reports
-- PostgreSQL 14+

-- ========================================
-- Table: patient_personas
-- ========================================
CREATE TABLE IF NOT EXISTS patient_personas (
    -- Primary key
    id VARCHAR(100) PRIMARY KEY,

    -- Creation metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by_skill_id VARCHAR(20) NOT NULL,  -- e.g., "MED-001"

    -- Persona basic info
    name VARCHAR(200) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(50) NOT NULL,
    specialty VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),

    -- Clinical presentation
    chief_complaint TEXT NOT NULL,
    opening_statement TEXT,
    expected_diagnosis TEXT NOT NULL,

    -- Complete persona JSON (includes all fields: symptoms, history, management, etc.)
    persona_json JSONB NOT NULL,

    -- Validation status
    clinical_validation_status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    qa_validation_status VARCHAR(20) DEFAULT 'pending',
    deployment_status VARCHAR(20) DEFAULT 'draft',  -- draft, deployed, archived

    -- Cultural diversity flags
    cultural_background VARCHAR(100),
    is_aboriginal_tsi BOOLEAN DEFAULT FALSE,
    is_lgbtqia BOOLEAN DEFAULT FALSE,
    is_cald BOOLEAN DEFAULT FALSE,

    -- Search indexes
    symptoms_tsvector TSVECTOR,  -- Full-text search on symptoms

    CONSTRAINT valid_specialty CHECK (specialty IN (
        'Cardiology', 'Emergency', 'General Practice', 'Pediatrics',
        'Respiratory', 'Neurology', 'ObGyn', 'Surgery',
        'Psychiatry', 'Infectious Diseases', 'Physical Examination'
    ))
);

-- Indexes for performance
CREATE INDEX idx_personas_specialty ON patient_personas(specialty);
CREATE INDEX idx_personas_difficulty ON patient_personas(difficulty);
CREATE INDEX idx_personas_deployment_status ON patient_personas(deployment_status);
CREATE INDEX idx_personas_cultural_aboriginal ON patient_personas(is_aboriginal_tsi) WHERE is_aboriginal_tsi = TRUE;
CREATE INDEX idx_personas_cultural_lgbtqia ON patient_personas(is_lgbtqia) WHERE is_lgbtqia = TRUE;
CREATE INDEX idx_personas_symptoms_fts ON patient_personas USING GIN(symptoms_tsvector);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_personas_updated_at BEFORE UPDATE ON patient_personas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Table: clinical_validations
-- ========================================
CREATE TABLE IF NOT EXISTS clinical_validations (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Foreign key to persona
    persona_id VARCHAR(100) NOT NULL REFERENCES patient_personas(id) ON DELETE CASCADE,

    -- Validation metadata
    validated_at TIMESTAMP DEFAULT NOW(),
    validator_id VARCHAR(30) NOT NULL,  -- e.g., "FRACP-VALIDATOR-001"
    validator_specialty VARCHAR(50) NOT NULL,

    -- Validation results
    overall_approval BOOLEAN NOT NULL,
    clinical_accuracy_score DECIMAL(3,1) NOT NULL CHECK (clinical_accuracy_score >= 0 AND clinical_accuracy_score <= 10),

    -- Detailed validation results (JSON)
    validation_results JSONB NOT NULL,
    errors_found JSONB,
    feedback JSONB,

    -- Recommendation
    recommendation TEXT NOT NULL,
    requires_revision BOOLEAN DEFAULT FALSE,

    -- Full validation report JSON
    full_report JSONB NOT NULL
);

-- Indexes
CREATE INDEX idx_clinical_validations_persona ON clinical_validations(persona_id);
CREATE INDEX idx_clinical_validations_approval ON clinical_validations(overall_approval);
CREATE INDEX idx_clinical_validations_score ON clinical_validations(clinical_accuracy_score);

-- ========================================
-- Table: qa_validations
-- ========================================
CREATE TABLE IF NOT EXISTS qa_validations (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Foreign key to persona
    persona_id VARCHAR(100) NOT NULL REFERENCES patient_personas(id) ON DELETE CASCADE,

    -- Validation metadata
    validated_at TIMESTAMP DEFAULT NOW(),
    qa_validator_id VARCHAR(20) DEFAULT 'QA-001',

    -- Quality gates results
    total_quality_gates INTEGER DEFAULT 13,
    gates_passed INTEGER NOT NULL,
    gates_failed INTEGER NOT NULL,
    deployment_readiness DECIMAL(5,2) NOT NULL,  -- Percentage 0-100

    -- Detailed gate results (JSON)
    quality_gates JSONB NOT NULL,
    errors JSONB,
    warnings JSONB,

    -- Recommendation
    recommendation TEXT NOT NULL,

    -- Full QA report JSON
    full_report JSONB NOT NULL
);

-- Indexes
CREATE INDEX idx_qa_validations_persona ON qa_validations(persona_id);
CREATE INDEX idx_qa_validations_readiness ON qa_validations(deployment_readiness);

-- ========================================
-- View: deployment_ready_personas
-- ========================================
CREATE OR REPLACE VIEW deployment_ready_personas AS
SELECT
    p.id,
    p.name,
    p.specialty,
    p.difficulty,
    p.expected_diagnosis,
    p.deployment_status,
    cv.clinical_accuracy_score,
    cv.overall_approval AS clinical_approved,
    qa.deployment_readiness,
    qa.gates_passed,
    qa.gates_failed
FROM patient_personas p
LEFT JOIN LATERAL (
    SELECT *
    FROM clinical_validations
    WHERE persona_id = p.id
    ORDER BY validated_at DESC
    LIMIT 1
) cv ON TRUE
LEFT JOIN LATERAL (
    SELECT *
    FROM qa_validations
    WHERE persona_id = p.id
    ORDER BY validated_at DESC
    LIMIT 1
) qa ON TRUE
WHERE
    cv.overall_approval = TRUE
    AND cv.clinical_accuracy_score >= 8.0
    AND qa.deployment_readiness = 100.0
    AND p.deployment_status = 'draft';

-- ========================================
-- View: validation_summary
-- ========================================
CREATE OR REPLACE VIEW validation_summary AS
SELECT
    p.specialty,
    p.difficulty,
    COUNT(*) AS total_personas,
    SUM(CASE WHEN cv.overall_approval = TRUE THEN 1 ELSE 0 END) AS clinically_approved,
    SUM(CASE WHEN qa.deployment_readiness = 100 THEN 1 ELSE 0 END) AS qa_approved,
    SUM(CASE WHEN p.deployment_status = 'deployed' THEN 1 ELSE 0 END) AS deployed,
    ROUND(AVG(cv.clinical_accuracy_score), 2) AS avg_clinical_score,
    ROUND(AVG(qa.deployment_readiness), 2) AS avg_qa_readiness
FROM patient_personas p
LEFT JOIN LATERAL (
    SELECT *
    FROM clinical_validations
    WHERE persona_id = p.id
    ORDER BY validated_at DESC
    LIMIT 1
) cv ON TRUE
LEFT JOIN LATERAL (
    SELECT *
    FROM qa_validations
    WHERE persona_id = p.id
    ORDER BY validated_at DESC
    LIMIT 1
) qa ON TRUE
GROUP BY p.specialty, p.difficulty
ORDER BY p.specialty, p.difficulty;

-- ========================================
-- Sample Queries
-- ========================================

-- Get all deployment-ready personas
-- SELECT * FROM deployment_ready_personas ORDER BY specialty, difficulty;

-- Get validation summary by specialty
-- SELECT * FROM validation_summary;

-- Get personas needing revision (failed clinical validation)
-- SELECT p.id, p.name, p.specialty, cv.clinical_accuracy_score, cv.feedback
-- FROM patient_personas p
-- JOIN clinical_validations cv ON p.id = cv.persona_id
-- WHERE cv.overall_approval = FALSE
-- ORDER BY cv.validated_at DESC;

-- Get QA issues (failed gates)
-- SELECT p.id, p.name, p.specialty, qa.gates_failed, qa.errors
-- FROM patient_personas p
-- JOIN qa_validations qa ON p.id = qa.persona_id
-- WHERE qa.gates_failed > 0
-- ORDER BY qa.gates_failed DESC;

-- Cultural diversity distribution
-- SELECT
--     COUNT(*) FILTER (WHERE is_aboriginal_tsi) AS aboriginal_tsi_count,
--     COUNT(*) FILTER (WHERE is_lgbtqia) AS lgbtqia_count,
--     COUNT(*) FILTER (WHERE is_cald) AS cald_count,
--     COUNT(*) AS total
-- FROM patient_personas
-- WHERE deployment_status = 'deployed';
