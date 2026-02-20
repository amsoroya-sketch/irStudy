/**
 * MCQ Test Data Fixtures
 * Sample MCQs for testing across different specialties and difficulties
 */

export interface MCQTestData {
  mcq_id: string;
  question_text: string;
  specialty: string;
  difficulty: 'easy' | 'medium' | 'hard';
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
    E: string;
  };
  correct_answer: 'A' | 'B' | 'C' | 'D' | 'E';
  explanation: string;
  citations: string[];
  tags: string[];
  is_published: boolean;
}

/**
 * Sample MCQs for different specialties
 */
export const TEST_MCQS: MCQTestData[] = [
  {
    mcq_id: 'TEST-CARDIO-EASY-001',
    question_text: 'A 45-year-old man presents with central chest pain. Which of the following is the MOST important initial investigation?',
    specialty: 'cardiology',
    difficulty: 'easy',
    options: {
      A: 'Chest X-ray',
      B: '12-lead ECG',
      C: 'Echocardiogram',
      D: 'Cardiac CT',
      E: 'Exercise stress test',
    },
    correct_answer: 'B',
    explanation: '12-lead ECG is the most important initial investigation for suspected acute coronary syndrome. It must be performed within 10 minutes of presentation to identify STEMI or other ECG changes suggestive of cardiac ischemia.',
    citations: [
      'Australian Heart Foundation - Acute Coronary Syndrome Guidelines 2016',
      'National Heart Foundation of Australia - Clinical Toolkit',
    ],
    tags: ['chest_pain', 'acs', 'ecg', 'emergency'],
    is_published: true,
  },
  {
    mcq_id: 'TEST-RESP-MEDIUM-001',
    question_text: 'A 30-year-old woman presents with acute shortness of breath and pleuritic chest pain. She is 2 weeks post-partum. O2 saturation is 92% on room air. What is the MOST appropriate next step?',
    specialty: 'respiratory',
    difficulty: 'medium',
    options: {
      A: 'Reassure and discharge',
      B: 'Arrange outpatient CT chest',
      C: 'Give antibiotics for pneumonia',
      D: 'Urgent CTPA and commence anticoagulation if PE confirmed',
      E: 'Arrange V/Q scan next week',
    },
    correct_answer: 'D',
    explanation: 'Post-partum state is a high-risk period for pulmonary embolism. With clinical features suggestive of PE (pleuritic pain, shortness of breath, hypoxia) and significant risk factor, urgent CTPA is required. Anticoagulation should be commenced if PE is confirmed.',
    citations: [
      'eTG (Therapeutic Guidelines): Cardiovascular - Venous Thromboembolism',
      'RANZCOG - Thromboembolism in Pregnancy and the Puerperium',
    ],
    tags: ['pe', 'post_partum', 'emergency', 'anticoagulation'],
    is_published: true,
  },
  {
    mcq_id: 'TEST-GASTRO-HARD-001',
    question_text: 'A 55-year-old man with chronic hepatitis C presents with new onset ascites. Diagnostic paracentesis shows SAAG of 18 g/L. Which of the following is the MOST likely cause?',
    specialty: 'gastroenterology',
    difficulty: 'hard',
    options: {
      A: 'Tuberculous peritonitis',
      B: 'Peritoneal carcinomatosis',
      C: 'Portal hypertension',
      D: 'Nephrotic syndrome',
      E: 'Pancreatitis',
    },
    correct_answer: 'C',
    explanation: 'Serum-ascites albumin gradient (SAAG) ≥11 g/L indicates portal hypertension as the cause of ascites. In a patient with chronic hepatitis C, cirrhosis with portal hypertension is the most likely cause. SAAG <11 g/L suggests non-portal hypertensive causes such as infection or malignancy.',
    citations: [
      'eTG (Therapeutic Guidelines): Gastroenterology & Hepatology - Ascites',
      'Australian & New Zealand Society of Hepatology Guidelines',
    ],
    tags: ['ascites', 'portal_hypertension', 'cirrhosis', 'saag'],
    is_published: true,
  },
  {
    mcq_id: 'TEST-NEURO-EASY-001',
    question_text: 'Which of the following cranial nerves is responsible for pupillary constriction?',
    specialty: 'neurology',
    difficulty: 'easy',
    options: {
      A: 'Optic nerve (CN II)',
      B: 'Oculomotor nerve (CN III)',
      C: 'Trochlear nerve (CN IV)',
      D: 'Trigeminal nerve (CN V)',
      E: 'Abducens nerve (CN VI)',
    },
    correct_answer: 'B',
    explanation: 'The oculomotor nerve (CN III) carries parasympathetic fibers that innervate the pupillary sphincter muscle, causing pupillary constriction. CN II (optic nerve) carries the afferent limb of the pupillary light reflex.',
    citations: [
      'Talley & O\'Connor - Clinical Examination (8th Australian Edition)',
    ],
    tags: ['cranial_nerves', 'pupil', 'cn3', 'basic'],
    is_published: true,
  },
  {
    mcq_id: 'TEST-PAEDS-MEDIUM-001',
    question_text: 'A 6-month-old infant is brought to ED with fever of 39.5°C for 24 hours. The infant is alert, well-perfused, and feeding normally. Urinalysis shows WBC >10/HPF. What is the MOST appropriate management?',
    specialty: 'paediatrics',
    difficulty: 'medium',
    options: {
      A: 'Discharge with paracetamol PRN',
      B: 'Urine culture and oral antibiotics',
      C: 'Urine culture, blood culture, LP, and IV antibiotics',
      D: 'Observe for 24 hours then review',
      E: 'Chest X-ray and start oral amoxicillin',
    },
    correct_answer: 'C',
    explanation: 'Infants <3 months with fever require septic workup including urine culture, blood culture, lumbar puncture, and empirical IV antibiotics due to high risk of serious bacterial infection. For infants 3-6 months, management depends on clinical appearance. This 6-month-old with positive urinalysis should have full septic workup given young age and significant fever.',
    citations: [
      'Australian Paediatric Society - Fever in Young Infants Guidelines',
      'Royal Children\'s Hospital Melbourne - Clinical Practice Guidelines: Fever',
    ],
    tags: ['fever', 'uti', 'septic_workup', 'infant'],
    is_published: true,
  },
];

/**
 * Helper to get MCQ by ID
 */
export function getMCQById(id: string): MCQTestData | undefined {
  return TEST_MCQS.find(mcq => mcq.mcq_id === id);
}

/**
 * Helper to get MCQs by specialty
 */
export function getMCQsBySpecialty(specialty: string): MCQTestData[] {
  return TEST_MCQS.filter(mcq => mcq.specialty === specialty);
}

/**
 * Helper to get MCQs by difficulty
 */
export function getMCQsByDifficulty(difficulty: 'easy' | 'medium' | 'hard'): MCQTestData[] {
  return TEST_MCQS.filter(mcq => mcq.difficulty === difficulty);
}
