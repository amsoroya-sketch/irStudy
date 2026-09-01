-- Import Physical Examination OSCEs
-- Creates physical examination OSCE entries in the database

-- Cardiovascular Physical Examination
INSERT INTO osces (
    osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes,
    patient_instructions, candidate_instructions, examiner_instructions,
    rubric, learning_objectives, key_points, is_published, created_at, updated_at
) VALUES (
    'OSCE-MED-CARDIO-001',
    'Cardiovascular Physical Examination',
    'physical_examination',
    'cardiology',
    'medium',
    8,
    'You are a patient attending for a cardiovascular examination.

**Your Symptoms:**
- You have been experiencing occasional chest discomfort on exertion
- You sometimes feel short of breath when climbing stairs
- You have no pain at rest

**During the examination:**
- Allow the doctor to examine your hands, neck, and chest
- Inform them if you feel uncomfortable',
    'Perform a systematic cardiovascular examination on this patient.

**Task:**
- Perform a complete cardiovascular examination
- Use the systematic approach (inspection, palpation, auscultation)
- Present your findings to the examiner

**Time:** 8 minutes',
    'Observe the candidate performing a cardiovascular examination.

**Assessment Criteria:**
1. Preparation (Wash hands, introduce, gain consent)
2. Systematic approach (Hands → Neck → Precordium)
3. Correct technique (Proper auscultation sites, positioning)
4. Communication (Clear, professional, patient comfort)
5. Presentation (Concise summary of findings)',
    '{"criteria": [{"item": "Hand hygiene and introduction", "points": 2}, {"item": "Appropriate patient positioning (45 degrees)", "points": 2}, {"item": "Auscultation at all 4 areas (APTM)", "points": 4}, {"item": "Clear presentation of findings", "points": 4}], "total_points": 40, "pass_mark": 28}'::jsonb,
    '["Perform a systematic cardiovascular examination", "Identify normal and abnormal cardiovascular signs", "Demonstrate appropriate communication with patients", "Present findings concisely to examiners"]'::jsonb,
    '["Always position patient at 45 degrees for JVP assessment", "Auscultate at 4 key areas: Aortic, Pulmonary, Tricuspid, Mitral (APTM)", "Use dynamic maneuvers to accentuate murmurs", "Check for peripheral signs (clubbing, cyanosis, edema)"]'::jsonb,
    true,
    NOW(),
    NOW()
) ON CONFLICT (osce_id) DO NOTHING;

-- Respiratory Physical Examination
INSERT INTO osces (
    osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes,
    patient_instructions, candidate_instructions, examiner_instructions,
    rubric, learning_objectives, key_points, is_published, created_at, updated_at
) VALUES (
    'OSCE-MED-RESP-001',
    'Respiratory Physical Examination',
    'physical_examination',
    'respiratory',
    'medium',
    8,
    'You are a patient attending for a respiratory examination.

**Your Symptoms:**
- You have been experiencing a persistent cough for 3 weeks
- You sometimes feel short of breath
- You have no chest pain

**During the examination:**
- Allow the doctor to examine your hands, neck, and chest
- Breathe normally unless asked to breathe deeply',
    'Perform a systematic respiratory examination on this patient.

**Task:**
- Perform a complete respiratory examination
- Use the systematic approach (inspection, palpation, percussion, auscultation)
- Present your findings to the examiner

**Time:** 8 minutes',
    'Observe the candidate performing a respiratory examination.

**Assessment Criteria:**
1. Preparation (Wash hands, introduce, gain consent)
2. Systematic approach (Hands → Neck → Chest)
3. Correct technique (Proper percussion, auscultation)
4. Communication (Clear, professional)',
    '{"criteria": [{"item": "Hand hygiene and introduction", "points": 2}, {"item": "Percussion technique and comparison", "points": 4}, {"item": "Auscultation (all zones, breath sounds)", "points": 5}, {"item": "Clear presentation", "points": 4}], "total_points": 42, "pass_mark": 29}'::jsonb,
    '["Perform systematic respiratory examination", "Identify normal and abnormal respiratory signs", "Demonstrate proper percussion and auscultation technique", "Present findings clearly and concisely"]'::jsonb,
    '["Always check tracheal position first", "Compare left and right sides systematically", "Proper percussion technique is crucial", "Examine both anterior and posterior chest"]'::jsonb,
    true,
    NOW(),
    NOW()
) ON CONFLICT (osce_id) DO NOTHING;

-- Abdominal Physical Examination
INSERT INTO osces (
    osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes,
    patient_instructions, candidate_instructions, examiner_instructions,
    rubric, learning_objectives, key_points, is_published, created_at, updated_at
) VALUES (
    'OSCE-MED-ABDO-001',
    'Abdominal Physical Examination',
    'physical_examination',
    'gastroenterology',
    'medium',
    8,
    'You are a patient attending for an abdominal examination.

**Your Symptoms:**
- You have been experiencing some abdominal discomfort
- The discomfort is mainly in the upper abdomen
- You have no nausea or vomiting

**During the examination:**
- Lie flat with arms by your side
- Allow the doctor to examine your abdomen
- Tell them if anything hurts',
    'Perform a systematic abdominal examination on this patient.

**Task:**
- Perform a complete abdominal examination
- Use the systematic IPPA approach
- Present your findings to the examiner

**Time:** 8 minutes',
    'Observe the candidate performing an abdominal examination.

**Assessment Criteria:**
1. Preparation (Wash hands, introduce, position patient)
2. Systematic approach (Inspection, Palpation, Percussion, Auscultation)
3. Correct technique (Light then deep palpation)
4. Communication (Checking for pain)',
    '{"criteria": [{"item": "Hand hygiene and introduction", "points": 2}, {"item": "Auscultation (bowel sounds)", "points": 3}, {"item": "Light and deep palpation", "points": 3}, {"item": "Clear presentation", "points": 4}], "total_points": 44, "pass_mark": 31}'::jsonb,
    '["Perform systematic abdominal examination", "Identify organomegaly and masses", "Demonstrate proper palpation technique", "Present findings systematically"]'::jsonb,
    '["Always auscultate BEFORE palpation", "Start liver palpation in RIF (may be massively enlarged)", "Always examine for hernias", "Check for shifting dullness if ascites suspected"]'::jsonb,
    true,
    NOW(),
    NOW()
) ON CONFLICT (osce_id) DO NOTHING;

-- Mental State Examination
INSERT INTO osces (
    osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes,
    patient_instructions, candidate_instructions, examiner_instructions,
    rubric, learning_objectives, key_points, is_published, created_at, updated_at
) VALUES (
    'OSCE-PSYCH-MSE-001',
    'Mental State Examination',
    'physical_examination',
    'psychiatry',
    'medium',
    8,
    'You are playing the role of a patient attending a psychiatric assessment.

**Your presentation:**
- You have been feeling low in mood for the past few weeks
- You are sleeping poorly and have reduced appetite
- You are able to engage in conversation
- You do not have suicidal thoughts

**During the examination:**
- Answer questions honestly
- Engage appropriately with the doctor',
    'Perform a Mental State Examination on this patient.

**Task:**
- Assess all components of MSE
- Demonstrate appropriate communication
- Present findings systematically

**Time:** 8 minutes',
    'Observe the candidate performing an MSE.

**Assessment Criteria:**
1. Systematic approach (ASEPTIC framework)
2. Appropriate questioning
3. Professional communication
4. Risk assessment
5. Clear presentation',
    '{"criteria": [{"item": "Introduction and rapport building", "points": 2}, {"item": "Mood evaluation", "points": 4}, {"item": "Cognition screening", "points": 4}, {"item": "Risk assessment", "points": 5}, {"item": "Systematic presentation", "points": 4}], "total_points": 42, "pass_mark": 29}'::jsonb,
    '["Perform comprehensive Mental State Examination", "Assess psychiatric symptoms systematically", "Evaluate risk appropriately", "Present MSE findings clearly"]'::jsonb,
    '["Use ASEPTIC mnemonic: Appearance, Speech, Emotion, Perception, Thought, Insight, Cognition", "Always assess risk (suicide, self-harm, harm to others)", "Distinguish subjective mood from objective mood", "Screen cognition systematically"]'::jsonb,
    true,
    NOW(),
    NOW()
) ON CONFLICT (osce_id) DO NOTHING;

-- Verify insertions
SELECT
    id,
    osce_id,
    station_title,
    station_type,
    specialty
FROM osces
WHERE station_type = 'physical_examination'
ORDER BY osce_id;
