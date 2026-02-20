/**
 * Database Test Data Seeder
 * Seeds fresh test data before each Playwright test run
 *
 * Usage: npm run test:seed
 */

import { execSync } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

// Colors for console output
const colors = {
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m',
};

function log(message: string, color: string = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logSection(title: string) {
  console.log('\n' + colors.bold + colors.cyan + '='.repeat(60) + colors.reset);
  console.log(colors.bold + colors.cyan + title + colors.reset);
  console.log(colors.bold + colors.cyan + '='.repeat(60) + colors.reset + '\n');
}

/**
 * Execute SQL command via Docker
 */
function executeSql(sqlCommand: string): void {
  try {
    const command = `docker exec -i irstudy-postgres psql -U postgres -d irstudy_medical -c "${sqlCommand.replace(/"/g, '\\"')}"`;
    execSync(command, { stdio: 'pipe' });
  } catch (error) {
    throw new Error(`SQL execution failed: ${error}`);
  }
}

/**
 * Execute SQL file via Docker
 */
function executeSqlFile(filePath: string): void {
  try {
    const absolutePath = path.resolve(filePath);
    const command = `cat ${absolutePath} | docker exec -i irstudy-postgres psql -U postgres -d irstudy_medical`;
    execSync(command, { stdio: 'pipe' });
  } catch (error) {
    throw new Error(`SQL file execution failed: ${error}`);
  }
}

/**
 * Main seeding process
 */
async function seedTestData() {
  logSection('Database Test Data Seeder');
  log('Starting fresh database seed for Playwright tests...', colors.blue);

  try {
    // Step 1: Clear existing test data
    logSection('Step 1: Clearing Existing Test Data');
    log('Deleting test users, MCQs, OSCEs, and related data...', colors.yellow);

    // Delete in correct order to respect foreign key constraints
    executeSql("DELETE FROM mcq_attempts WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@test.com')");
    executeSql("DELETE FROM user_progress WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@test.com')");
    executeSql("DELETE FROM user_favorite_mcqs WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@test.com')");
    executeSql("DELETE FROM user_favorite_osces WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@test.com')");
    executeSql("DELETE FROM study_cards WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@test.com')");
    executeSql("DELETE FROM mcqs WHERE question_id LIKE 'TEST-%'");
    executeSql("DELETE FROM osces WHERE osce_id LIKE 'TEST-%'");
    executeSql("DELETE FROM users WHERE email LIKE '%@test.com'");

    log('✓ Existing test data cleared', colors.green);

    // Step 2: Create test users
    logSection('Step 2: Creating Test Users');
    log('Creating 5 test users (student, educator, admin, inactive, unverified)...', colors.yellow);

    const createUsersSQL = `
-- Test Student (password: Student123!@#)
INSERT INTO users (email, password_hash, full_name, role, is_active, is_verified, created_at, updated_at)
VALUES (
  'student@test.com',
  '$2b$12$UVlDPjyNCLcqXmlyvXIGQe.XdU.S.qmnp50CrM4K5RjpMkvz.cywG',
  'John Student',
  'student',
  true,
  true,
  NOW(),
  NOW()
);

-- Test Educator (password: Student123!@#)
INSERT INTO users (email, password_hash, full_name, role, is_active, is_verified, created_at, updated_at)
VALUES (
  'educator@test.com',
  '$2b$12$UVlDPjyNCLcqXmlyvXIGQe.XdU.S.qmnp50CrM4K5RjpMkvz.cywG',
  'Jane Educator',
  'educator',
  true,
  true,
  NOW(),
  NOW()
);

-- Test Admin (password: Student123!@#)
INSERT INTO users (email, password_hash, full_name, role, is_active, is_verified, created_at, updated_at)
VALUES (
  'admin@test.com',
  '$2b$12$UVlDPjyNCLcqXmlyvXIGQe.XdU.S.qmnp50CrM4K5RjpMkvz.cywG',
  'Alice Admin',
  'admin',
  true,
  true,
  NOW(),
  NOW()
);

-- Test Inactive User (password: Student123!@#)
INSERT INTO users (email, password_hash, full_name, role, is_active, is_verified, created_at, updated_at)
VALUES (
  'inactive@test.com',
  '$2b$12$UVlDPjyNCLcqXmlyvXIGQe.XdU.S.qmnp50CrM4K5RjpMkvz.cywG',
  'Bob Inactive',
  'student',
  false,
  true,
  NOW(),
  NOW()
);

-- Test Unverified User (password: Student123!@#)
INSERT INTO users (email, password_hash, full_name, role, is_active, is_verified, created_at, updated_at)
VALUES (
  'unverified@test.com',
  '$2b$12$UVlDPjyNCLcqXmlyvXIGQe.XdU.S.qmnp50CrM4K5RjpMkvz.cywG',
  'Charlie Unverified',
  'student',
  true,
  false,
  NOW(),
  NOW()
);
    `;

    const usersSqlPath = '/tmp/create_test_users.sql';
    fs.writeFileSync(usersSqlPath, createUsersSQL);
    executeSqlFile(usersSqlPath);
    fs.unlinkSync(usersSqlPath);

    log('✓ Created 5 test users', colors.green);

    // Step 3: Create test MCQs
    logSection('Step 3: Creating Test MCQs');
    log('Creating 5 sample MCQs across specialties...', colors.yellow);

    const createMCQsSQL = `
-- Cardiology MCQ (Easy)
INSERT INTO mcqs (question_id, question_text, specialty, difficulty, options, correct_answer, explanation, citation, tags, is_published, created_at, updated_at)
VALUES (
  'TEST-CARDIO-EASY-001',
  'A 45-year-old man presents with central chest pain. Which of the following is the MOST important initial investigation?',
  'cardiology',
  'easy',
  '{"A": "Chest X-ray", "B": "12-lead ECG", "C": "Echocardiogram", "D": "Cardiac CT", "E": "Exercise stress test"}',
  'B',
  '12-lead ECG is the most important initial investigation for suspected acute coronary syndrome. It must be performed within 10 minutes of presentation.',
  'Australian Heart Foundation - Acute Coronary Syndrome Guidelines 2016',
  '["chest_pain", "acs", "ecg", "emergency"]',
  true,
  NOW(),
  NOW()
);

-- Respiratory MCQ (Medium)
INSERT INTO mcqs (question_id, question_text, specialty, difficulty, options, correct_answer, explanation, citation, tags, is_published, created_at, updated_at)
VALUES (
  'TEST-RESP-MEDIUM-001',
  'A 30-year-old woman 2 weeks post-partum presents with acute shortness of breath and pleuritic chest pain. O2 saturation is 92% on room air. What is the MOST appropriate next step?',
  'respiratory',
  'medium',
  '{"A": "Reassure and discharge", "B": "Arrange outpatient CT chest", "C": "Give antibiotics for pneumonia", "D": "Urgent CTPA and commence anticoagulation if PE confirmed", "E": "Arrange V/Q scan next week"}',
  'D',
  'Post-partum state is a high-risk period for pulmonary embolism. With clinical features suggestive of PE and significant risk factor, urgent CTPA is required.',
  'eTG (Therapeutic Guidelines): Cardiovascular - Venous Thromboembolism',
  '["pe", "post_partum", "emergency", "anticoagulation"]',
  true,
  NOW(),
  NOW()
);

-- Gastroenterology MCQ (Hard)
INSERT INTO mcqs (question_id, question_text, specialty, difficulty, options, correct_answer, explanation, citation, tags, is_published, created_at, updated_at)
VALUES (
  'TEST-GASTRO-HARD-001',
  'A 55-year-old man with chronic hepatitis C presents with new onset ascites. Diagnostic paracentesis shows SAAG of 18 g/L. Which of the following is the MOST likely cause?',
  'gastroenterology',
  'hard',
  '{"A": "Tuberculous peritonitis", "B": "Peritoneal carcinomatosis", "C": "Portal hypertension", "D": "Nephrotic syndrome", "E": "Pancreatitis"}',
  'C',
  'Serum-ascites albumin gradient (SAAG) ≥11 g/L indicates portal hypertension as the cause of ascites. In a patient with chronic hepatitis C, cirrhosis with portal hypertension is the most likely cause.',
  'eTG (Therapeutic Guidelines): Gastroenterology & Hepatology - Ascites',
  '["ascites", "portal_hypertension", "cirrhosis", "saag"]',
  true,
  NOW(),
  NOW()
);

-- Neurology MCQ (Easy)
INSERT INTO mcqs (question_id, question_text, specialty, difficulty, options, correct_answer, explanation, citation, tags, is_published, created_at, updated_at)
VALUES (
  'TEST-NEURO-EASY-001',
  'Which of the following cranial nerves is responsible for pupillary constriction?',
  'neurology',
  'easy',
  '{"A": "Optic nerve (CN II)", "B": "Oculomotor nerve (CN III)", "C": "Trochlear nerve (CN IV)", "D": "Trigeminal nerve (CN V)", "E": "Abducens nerve (CN VI)"}',
  'B',
  'The oculomotor nerve (CN III) carries parasympathetic fibers that innervate the pupillary sphincter muscle, causing pupillary constriction. CN II (optic nerve) carries the afferent limb of the pupillary light reflex.',
  'Talley & O''Connor - Clinical Examination (8th Australian Edition)',
  '["cranial_nerves", "pupil", "cn3", "basic"]',
  true,
  NOW(),
  NOW()
);

-- Paediatrics MCQ (Medium)
INSERT INTO mcqs (question_id, question_text, specialty, difficulty, options, correct_answer, explanation, citation, tags, is_published, created_at, updated_at)
VALUES (
  'TEST-PAEDS-MEDIUM-001',
  'A 6-month-old infant is brought to ED with fever of 39.5°C for 24 hours. The infant is alert, well-perfused, and feeding normally. Urinalysis shows WBC >10/HPF. What is the MOST appropriate management?',
  'paediatrics',
  'medium',
  '{"A": "Discharge with paracetamol PRN", "B": "Urine culture and oral antibiotics", "C": "Urine culture, blood culture, LP, and IV antibiotics", "D": "Observe for 24 hours then review", "E": "Chest X-ray and start oral amoxicillin"}',
  'C',
  'Infants 3-6 months with fever require septic workup including urine culture, blood culture, lumbar puncture, and empirical IV antibiotics due to risk of serious bacterial infection.',
  'Royal Children''s Hospital Melbourne - Clinical Practice Guidelines: Fever',
  '["fever", "uti", "septic_workup", "infant"]',
  true,
  NOW(),
  NOW()
);
    `;

    const mcqsSqlPath = '/tmp/create_test_mcqs.sql';
    fs.writeFileSync(mcqsSqlPath, createMCQsSQL);
    executeSqlFile(mcqsSqlPath);
    fs.unlinkSync(mcqsSqlPath);

    log('✓ Created 5 test MCQs', colors.green);

    // Step 4: Create test OSCEs with video resources
    logSection('Step 4: Creating Test OSCEs with Video Resources');
    log('Creating 4 test OSCEs (with and without videos)...', colors.yellow);

    const createOSCEsSQL = `
-- OSCE with full video resources (essential + supplementary)
INSERT INTO osces (osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes, patient_instructions, candidate_instructions, examiner_instructions, rubric, learning_objectives, key_points, video_resources, is_published, created_at, updated_at)
VALUES (
  'TEST-CARDIO-VIDEO-001',
  'Cardiovascular Physical Examination with Video Demonstrations',
  'physical_examination',
  'cardiology',
  'medium',
  8,
  'You are a patient attending cardiology clinic for examination. Remain relaxed and follow the doctor''s instructions.',
  'Perform a systematic cardiovascular examination. You have 8 minutes.',
  'Observe the candidate''s technique and mark using the rubric.',
  '{"criteria": [{"item": "Introduction and consent", "points": 10}, {"item": "Systematic examination approach", "points": 40}, {"item": "Correct technique", "points": 30}, {"item": "Professionalism", "points": 20}], "total_points": 100, "pass_mark": 60}',
  '["Perform systematic cardiovascular examination", "Identify normal and abnormal cardiovascular signs", "Demonstrate appropriate auscultation technique"]',
  '["Always position patient at 45 degrees for JVP assessment", "Auscultate at 4 key areas: Aortic, Pulmonary, Tricuspid, Mitral (APTM)", "Check for peripheral signs (clubbing, cyanosis, edema)"]',
  '{"essential_videos": [{"title": "Cardiovascular Examination - Stanford Medicine 25", "url": "https://stanfordmedicine25.stanford.edu/the25/cardiovascular.html", "source": "Stanford Medicine 25", "duration_minutes": 10, "focus": "Complete systematic cardiac examination with emphasis on auscultation techniques", "why_recommended": "Gold standard demonstration from Stanford, excellent for murmur identification and dynamic maneuvers", "australian_relevance": "Technique fully compatible with AMC Clinical exam requirements"}, {"title": "Heart Examination - Geeky Medics", "url": "https://geekymedics.com/cardiovascular-examination/", "source": "Geeky Medics", "duration_minutes": 8, "focus": "Step-by-step cardiovascular examination", "why_recommended": "Clear, concise demonstration with OSCE-specific tips", "australian_relevance": "Widely used in Australian medical schools"}], "supplementary_videos": [{"title": "Advanced Auscultation Techniques - Oxford Medical Education", "url": "https://www.oxfordmedicaleducation.com/clinical-examination/cardiovascular-examination/", "source": "Oxford Medical Education", "duration_minutes": 12, "focus": "Advanced heart sound identification", "why_recommended": "Detailed coverage of complex murmurs"}]}',
  true,
  NOW(),
  NOW()
);

-- OSCE with only essential videos
INSERT INTO osces (osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes, patient_instructions, candidate_instructions, examiner_instructions, rubric, learning_objectives, key_points, video_resources, is_published, created_at, updated_at)
VALUES (
  'TEST-RESP-VIDEO-001',
  'Respiratory Physical Examination',
  'physical_examination',
  'respiratory',
  'medium',
  8,
  'You are a patient with a respiratory complaint.',
  'Perform a respiratory examination.',
  'Mark systematic approach and technique.',
  '{"criteria": [{"item": "Examination technique", "points": 100}], "total_points": 100, "pass_mark": 60}',
  '["Perform respiratory examination"]',
  '["Inspect, palpate, percuss, auscultate"]',
  '{"essential_videos": [{"title": "Respiratory Examination - Geeky Medics", "url": "https://geekymedics.com/respiratory-examination/", "source": "Geeky Medics", "duration_minutes": 9, "focus": "Complete respiratory examination technique", "why_recommended": "Clear demonstration suitable for AMC Clinical exam"}], "supplementary_videos": []}',
  true,
  NOW(),
  NOW()
);

-- OSCE without videos
INSERT INTO osces (osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes, patient_instructions, candidate_instructions, examiner_instructions, rubric, learning_objectives, key_points, is_published, created_at, updated_at)
VALUES (
  'TEST-NEURO-HISTORY-001',
  'Neurological History Taking',
  'history_taking',
  'neurology',
  'medium',
  8,
  'You are presenting with headaches.',
  'Take a focused neurological history.',
  'Assess systematic history-taking.',
  '{"criteria": [{"item": "History taking", "points": 100}], "total_points": 100, "pass_mark": 60}',
  '["Take systematic neurological history"]',
  '["Use SOCRATES framework for pain history"]',
  true,
  NOW(),
  NOW()
);

-- OSCE with maximum videos (4 essential + 3 supplementary)
INSERT INTO osces (osce_id, station_title, station_type, specialty, difficulty, time_limit_minutes, patient_instructions, candidate_instructions, examiner_instructions, rubric, learning_objectives, key_points, video_resources, is_published, created_at, updated_at)
VALUES (
  'TEST-ABDO-VIDEO-001',
  'Abdominal Examination - Comprehensive',
  'physical_examination',
  'gastroenterology',
  'hard',
  8,
  'You have abdominal discomfort.',
  'Perform complete abdominal examination.',
  'Assess systematic approach and technique.',
  '{"criteria": [{"item": "Examination", "points": 100}], "total_points": 100, "pass_mark": 60}',
  '["Complete abdominal examination"]',
  '["Inspection, auscultation, percussion, palpation (correct order)"]',
  '{"essential_videos": [{"title": "Abdominal Examination Part 1 - Stanford", "url": "https://stanfordmedicine25.stanford.edu/the25/abdominal.html", "source": "Stanford Medicine 25", "duration_minutes": 8, "focus": "Inspection and auscultation", "why_recommended": "Gold standard technique demonstration"}, {"title": "Abdominal Examination Part 2 - Geeky Medics", "url": "https://geekymedics.com/abdominal-examination/", "source": "Geeky Medics", "duration_minutes": 10, "focus": "Palpation and percussion techniques", "why_recommended": "OSCE-focused demonstration"}, {"title": "Acute Abdomen Assessment - Oxford", "url": "https://www.oxfordmedicaleducation.com/clinical-examination/abdominal-examination/", "source": "Oxford Medical Education", "duration_minutes": 7, "focus": "Identifying acute surgical abdomen", "why_recommended": "Emergency presentations focus"}, {"title": "Liver Palpation Technique", "url": "https://geekymedics.com/liver-palpation/", "source": "Geeky Medics", "duration_minutes": 5, "focus": "Specific liver examination technique", "why_recommended": "Detailed hepatomegaly assessment"}], "supplementary_videos": [{"title": "Abdominal Auscultation", "url": "https://geekymedics.com/bowel-sounds/", "source": "Geeky Medics", "duration_minutes": 4, "focus": "Interpreting bowel sounds", "why_recommended": "Helps differentiate normal vs abnormal sounds"}, {"title": "Ascites Assessment", "url": "https://stanfordmedicine25.stanford.edu/the25/ascites.html", "source": "Stanford Medicine 25", "duration_minutes": 6, "focus": "Detecting and quantifying ascites", "why_recommended": "Shifting dullness and fluid thrill techniques"}, {"title": "Hernias and Masses", "url": "https://geekymedics.com/hernia-examination/", "source": "Geeky Medics", "duration_minutes": 8, "focus": "Identifying abdominal hernias", "why_recommended": "Common OSCE scenario"}]}',
  true,
  NOW(),
  NOW()
);
    `;

    const oscesSqlPath = '/tmp/create_test_osces.sql';
    fs.writeFileSync(oscesSqlPath, createOSCEsSQL);
    executeSqlFile(oscesSqlPath);
    fs.unlinkSync(oscesSqlPath);

    log('✓ Created 4 test OSCEs (3 with videos, 1 without)', colors.green);

    // Summary
    logSection('Seed Complete');
    log('✓ Database seeded successfully!', colors.green + colors.bold);
    console.log('\nTest Data Summary:');
    console.log(`  ${colors.cyan}Users:${colors.reset} 5 (student, educator, admin, inactive, unverified)`);
    console.log(`  ${colors.cyan}MCQs:${colors.reset} 5 across specialties`);
    console.log(`  ${colors.cyan}OSCEs:${colors.reset} 4 (3 with video resources)`);
    console.log(`  ${colors.cyan}Video Resources:${colors.reset} 6 videos total\n`);
    console.log(`${colors.green}Ready to run Playwright tests!${colors.reset}\n`);

  } catch (error) {
    log(`\n✗ Seeding failed: ${error}`, colors.red + colors.bold);
    process.exit(1);
  }
}

// Run the seeder
seedTestData();
